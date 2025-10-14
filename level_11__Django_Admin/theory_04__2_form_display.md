## 2️ Формы редактирования объектов (Form Display)

Эти параметры управляют тем, как именно выглядит и работает форма создания/редактирования объекта в админке Django.

Иными словами:
1. В предыдущем пункте `List Display` мы настраивали Таблицу Объектов.
2. В этой таблице есть поля со ссылкой, по которой можно перейти к редактированию (`list_display_links`).
3. После клика на эту ссылку, Django открывает форму редактирования объекта `Form Display`.

---

### `fields`

* Явно указывает список полей, которые должны быть показаны в форме.
* Полезно, когда нужно контролировать порядок отображения или исключить ненужные поля.

```python
fields = ('title', 'author', 'year_published')
```

В форме будут только эти три поля, остальные показаны не будут.

---

### `exclude`

* Противоположность `fields`.
* Позволяет скрыть отдельные поля, но все остальные будут показаны.

```python
exclude = ('is_deleted',)
```

Поле `is_deleted` не будет отображаться в форме, все остальные поля - будут.

---

### `fieldsets`

* Позволяет группировать поля в блоки с заголовками и описаниями.
* Удобно для сложных моделей с большим количеством полей.

```python
fieldsets = (
    ('Основная информация', {
        'fields': ('title', 'author')
    }),
    ('Дополнительно', {
        'fields': ('year_published', 'is_deleted'),
        'description': 'Служебные поля, не изменяйте без необходимости.'
    }),
)
```

 Форма разделится на два блока с заголовками `Основная информация` и `Дополнительно`.

---

### `readonly_fields`

* Делаем некоторые поля только для чтения.
* Они будут отображаться, но без возможности редактирования.

```python
readonly_fields = ('year_published',)
```

Пользователь увидит год издания, но не сможет его менять.

---

### `form`

* Позволяет использовать **свою собственную `ModelForm`** вместо стандартной.
* Удобно для валидации, кастомных полей или нестандартных виджетов.

```python
from django import forms

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'

    def clean_title(self):
        title = self.cleaned_data['title']
        if "!" in title:
            raise forms.ValidationError("Название книги не должно содержать '!'")
        return title

class BookAdmin(admin.ModelAdmin):
    form = BookForm
```

В админке появится дополнительная валидация.

---

### `formfield_overrides`

* Позволяет **заменить стандартные виджеты** для определённых типов полей.
* Работает глобально для этого `ModelAdmin`.

```python
from django.forms import Textarea
from django.db import models

formfield_overrides = {
    models.TextField: {'widget': Textarea(attrs={'rows': 3, 'cols': 40})},
}
```

Все `TextField` в текущей модели будут отображаться компактнее, чем по умолчанию.

---

**В итоге**:

* `fields` / `exclude` → контроль состава формы.
* `fieldsets` → группировка и описание.
* `readonly_fields` → запрет на редактирование.
* `form` → подключение своей логики.
* `formfield_overrides` → кастомные виджеты.

Таким образом, итоговый код будет:

#### module `myapp/forms.py`
```python
from django import forms
from .models import Book


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = '__all__'
        widgets = {
            'title': forms.TextInput(attrs={'size': 80}),            # вариант 1
            # 'title': forms.Textarea(attrs={'rows': 3, 'cols': 40}),  # вариант 2
        }

    def clean_title(self):
        title = self.cleaned_data['title']
        if "!" in title:
            raise forms.ValidationError("Название книги не должно содержать '!'")
        return title
```

#### module `myapp/admin.py`
```python
from django import forms
from django.contrib import admin
from django.db import models
from .models import Book
from .forms import BookForm

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # ======= Настройка List Display =======
    list_display = ('id', 'title', 'author', 'year_published', 'is_deleted', 'genre_list')
    list_display_links = ('title',)
    list_editable = ('is_deleted',)
    list_filter = ('year_published', 'is_deleted', 'author', 'genres')
    search_fields = ('title', 'author__name')
    ordering = ('-year_published',)
    list_select_related = ('author',)  # оптимизация для ForeignKey
    list_prefetch_related = ('genres',)  # оптимизация для ManyToMany

    list_per_page = 4
    list_max_show_all = 15
    
    def genre_list(self, obj):
        return ", ".join([genre.name for genre in obj.genres.all()])
    genre_list.short_description = 'Жанры'

    # ======= Настройка Form Display =======
    form = BookForm
    # Группировка через fieldsets
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'author', 'year_published')
        }),
        ('Служебные данные', {
            'fields': ('is_deleted',),
            'description': 'Эти поля используются для логики приложения',
        }),
    )

    # Поля только для чтения
    readonly_fields = ('year_published',)  
```
