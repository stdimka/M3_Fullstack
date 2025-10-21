## Inline ModelForm (`InlineFormset`)

###  1. Основная идея

Inline Formset позволяет редактировать родителя и связанные объекты в одной группе форм:

- `InlineFormset` всегда строится вокруг родителя (первый аргумент).
- Он редактирует родителя + все дочерние объекты, связанные через ForeignKey или OneToOneField.
- Нельзя использовать `InlineFormset`, чтобы в форме «ребёнка» и одновременно менять родителя через ту же форму.

Другими словами: родитель → дети, а не наоборот.

Типичные связи:

* `ForeignKey` — много к одному (например, `Book.author → Author`)
* `OneToOneField` — один к одному (например, `Profile.user → User`)

В теории может работать и для `ManyToManyField`, но требует явного (ручного) создания промежуточной модели.

---

### 2. Пример: Author + книги

```python
# models.py
from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=100)

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, related_name='books', on_delete=models.CASCADE)
```

```python
# forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Author, Book

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name']

# InlineFormset для Book в контексте Author
BookFormSet = inlineformset_factory(
    Author,  # родительская модель
    Book,    # дочерняя модель
    fields=['title'],
    extra=1,  # количество пустых форм для добавления
    can_delete=True  # возможность удалять связанные объекты
)
```

```python
# views.py
from django.shortcuts import render, get_object_or_404, redirect
from .forms import AuthorForm, BookFormSet
from .models import Author

def author_edit(request, pk):
    author = get_object_or_404(Author, pk=pk)
    if request.method == 'POST':
        form = AuthorForm(request.POST, instance=author)
        formset = BookFormSet(request.POST, instance=author)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()  # сохраняются все книги вместе
            return redirect('author_list')
    else:
        form = AuthorForm(instance=author)
        formset = BookFormSet(instance=author)
    return render(request, 'author_edit.html', {'form': form, 'formset': formset})
```
Здесь `formset.save()` создаёт/обновляет все связанные `Book` для выбранного автора.


```html
<!-- author_edit.html -->
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    {{ formset.management_form }}
    {% for f in formset %}
        {{ f.as_p }}
    {% endfor %}
    <button type="submit">Сохранить</button>
</form>
```

---

### 3. Сходства и различия с другими вариантами ModelForm

| Вариант            | Суть                                           | Сохраняются объекты                   | Классический пример                                            |
| ------------------ | ---------------------------------------------- | ------------------------------------- | -------------------------------------------------------------- |
| **ModelForm**      | Одиночная форма одной модели                   | `form.save()`                         | Создать/изменить одного автора                                 |
| **Formset**        | Несколько форм одной модели без родителя       | `formset.save()`                      | Добавление нескольких книг одновременно, без привязки к автору |
| **InlineFormset**  | Несколько связанных объектов через FK/OneToOne | `formset.save()`                      | Редактирование автора + всех его книг                          |
| **Админка Django** | InlineFormset уже встроен                      | Сохраняется автоматически через admin | `TabularInline` или `StackedInline` для Book внутри Author     |

---

### 4. Применение в админке

В админке Django inline выглядит так:

```python
# admin.py
from django.contrib import admin
from .models import Author, Book

class BookInline(admin.TabularInline):
    model = Book
    extra = 1

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    inlines = [BookInline]
```

* `TabularInline` — компактная таблица с книгами.
* `StackedInline` — вертикальное расположение форм.
* Основное отличие: админка берёт на себя генерацию формы и сохранение `formset`.

---

### 5. Отличия кастомного InlineFormset от админки

| Фактор     | InlineFormset в кастомной форме           | Inline в админке                |
| ---------- | ----------------------------------------- | ------------------------------- |
| Контроль   | Полный контроль над шаблоном и обработкой | Ограничен встроенными шаблонами |
| Валидация  | Можно кастомизировать                     | Стандартная                     |
| JS/UX      | Нужно добавить самому                     | Частично готово                 |
| Сохранение | `form.save()` + `formset.save()`          | Автоматическое через admin      |


### 6. Можно ли продолжить связи и добавить ещё и форму для BookDetail?

В Django admin inline-формы строятся по принципу **ForeignKey → родитель**.

Поэтому для моделей **Автор → Книга (родитель → ребёнок)** и потом **Книга → КнигаДетейл (родитель → ребёнок)**:

  * В админке автора вы можете добавить inline для книг.
  * В админке книги вы можете добавить inline для деталей.
  * То есть всё работает, потому что направление отношений правильное: *родитель → дети*.

Однако, если же поменять местами и сделать так, чтобы **Книга была ребёнком для КнигаДетейл**,  
то есть КнигаДетейл → Книга, то inline для Книги внутри КнигаДетейл не появится автоматически.   
В Django inline работает только с **child**-моделями — теми, у кого есть ForeignKey на родителя.

Иными словами:
**Inline показываются только "снизу вверх": родитель → дети**, а не наоборот.

#### Пример такой конструкции:

```python
# forms.py
from django import forms
from django.forms import inlineformset_factory
from .models import Author, Book, DetailBook

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name']

BookFormSet = inlineformset_factory(
    Author,
    Book,
    fields=['title', 'year_published', 'is_deleted'],
    extra=1,
    can_delete=True
)

DetailBookFormSet = inlineformset_factory(
    Book,
    DetailBook,
    fields=['summary', 'page_count'],
    extra=1,     # но реально будет только одна форма
    can_delete=False
)


```
