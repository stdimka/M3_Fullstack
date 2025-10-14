
### 1. Form

`Form` — это обычная форма Django.

**Пример:**

```python
from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    message = forms.CharField(widget=forms.Textarea)
```

**Особенности `Form`:**

* Поля задаются вручную.
* Нет привязки к базе данных.
* Нужно самостоятельно писать логику сохранения данных 
  (например, в нашем случае - добавление данных во временный список).
  * Вариант для представления-функции:
  ```python
  form = FeedbackForm(request.POST)
  if form.is_valid():
      name = form.cleaned_data['name']
      ...
  ```
  * Вариант для представления-класса:
  ```python
  def form_valid(self, form):
      # Добавляем новые данные в глобальный список results_list
      results_list.append(form.cleaned_data)
      return super().form_valid(form)
  ```


* Подходит для форм, которые не связаны с моделью, например, контактная форма, поиск, фильтры.

---

### 2. ModelForm

`ModelForm` — это форма, которая автоматически создаётся на основе модели.

**Пример:**

```python
from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'published_date']
```

**Особенности `ModelForm`:**

* Поля создаются автоматически по полям модели (`CharField`, `DateField` и т.д.).
* Позволяет сразу сохранять данные в модель через `form.save()`.
* Поддерживает валидацию на уровне модели (например, `unique=True`, `max_length`).
* Можно переопределять поля и добавлять свои виджеты так же, как в обычной форме.
* Легко создавать формы для CRUD (Create, Update, Delete).

```python
class BookUpdateView(UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'books/edit_book.html'

    def get_success_url(self):
        return reverse_lazy('book_detail', kwargs={'pk': self.object.pk})
```

Как видим, здесь валидация и сохранение (добавление изменений в ДБ) делается "под капотом"

---

### 3. Основные отличия Form и ModelForm

| Характеристика    | Form                   | ModelForm                                                |
| ----------------- | ---------------------- | -------------------------------------------------------- |
| Привязка к модели | Нет                    | Да, через `Meta.model`                                   |
| Определение полей | Вручную                | Автоматически + можно менять                             |
| Сохранение в БД   | Нужно вручную          | Через `form.save()`                                      |
| Валидация         | Только на уровне формы | На уровне формы + модели                                 |
| CRUD              | Нужно вручную писать   | Очень удобно для создания/редактирования объектов модели |

---

### 4.️ Преимущества ModelForm

1. **Меньше кода** – не нужно повторять поля модели.
2. **Меньше ошибок** – автоматически учитываются ограничения модели.
3. **Интеграция с БД** – можно сразу сохранять или обновлять объект через `save()`.
4. **Гибкость** – можно переопределять поля и виджеты, добавлять кастомные методы валидации (`clean_<field>`).
5. **Удобно для админок и CRUD-интерфейсов** – Django использует `ModelForm` в админке.


