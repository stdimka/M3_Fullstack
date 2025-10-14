## Инлайн-модели (Inlines)

**Смысл:** позволяют редактировать связанные объекты прямо **в форме родительской модели**. В вашем случае:

* `Book` — родительская модель.
* `BookDetail` — связанная модель через `OneToOneField`.

Т.е. при редактировании книги мы можем сразу же редактировать её детали.

---

### `TabularInline`

* Отображает связанные объекты в **компактной таблице**.
* Удобно, когда полей немного и хочется экономить место.

```python
class BookGenreInline(admin.TabularInline):
    model = BookGenre
    extra = 1
```

Пользователь увидит список связей и сможет добавлять/удалять строки прямо в таблице.

---

### `StackedInline`

* Отображает связанные объекты в **развернутом блоке**.
* Подходит, если у модели много полей или нужно больше пространства для редактирования.

```python
class BookDetailInline(admin.StackedInline):
    model = BookDetail
    extra = 0
```

Каждый объект показывается как отдельный блок с полями, удобно для детальной информации.

---

### `model`

* Указывает **модель**, которая будет редактироваться через инлайн.
* Обязательное поле при создании инлайна.

```python
model = BookGenre
```

---

### `extra`

* Количество **пустых форм** для добавления новых объектов.
* По умолчанию 3.

```python
extra = 1
```
Примечание:
- для модели `one-to-one` возможны только 2 значения параметра `extra`:
  - extra = 0 → показывать только существующий объект, пустой формы нет.
  - extra = 1 → если объекта ещё нет, показать одну пустую форму для создания.
  
---

### `can_delete`

* Разрешает или запрещает **удаление объектов** через инлайн.

```python
can_delete = True
```

---

### `min_num` / `max_num`

* Минимальное и максимальное количество форм, которые можно добавить.
* Контролирует ограничения на стороне админки.

```python
min_num = 1
max_num = 5
```

Иными словами, это ограничение - сколько "дочерних.2 объектов может быть связано с "родителем".
НО важно понимать:
 - это ограничение ТОЛЬКО на стороне админки и НИКАК не касается ограничения БД!

---

### `readonly_fields`

* Делает поля **только для чтения** внутри инлайна.
* Пользователь увидит данные, но не сможет их менять.

```python
readonly_fields = ('genre',)
```

---

### Пример для нашей модели:

```python
from django.contrib import admin
from .models import Book, BookDetail

class BookDetailInline(admin.StackedInline):
# class BookDetailInline(admin.TabularInline):
    model = BookDetail        # Связанная модель
    extra = 0                 # Не показывать пустых форм
    can_delete = False        # Нельзя удалять детали
    readonly_fields = ('page_count',)  # Только для чтения

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'year_published', 'is_deleted')
    inlines = [BookDetailInline]  # Подключаем инлайн
```

✅ Теперь при редактировании книги в админке появится блок с полями `BookDetail`,  
и мы сможем сразу редактировать `summary` и `page_count` (если не readonly).

---

## Инлайн для ManyToMany через промежуточную модель

⚠️ **ВАЖНО!** 
В Django `ManyToManyField` напрямую НЕ ПОДДЕРЖИВАЕТСЯ инлайн!
Поэтому для инлайн-редактирования нам придётся создать промежуточную модель (`through`). 

В нашем случае модель `Genre` связана с `Book` через `books = ManyToManyField(Book, related_name='genres')`.

По умолчанию админка создаёт виджет выбора (`<select multiple>`), но если мы хотим инлайн-редактирование:

1. Создаём промежуточную модель (если её ещё нет):

```python
class BookGenre(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('book', 'genre')
```

2. Меняем `Book.genres` на использование `through=BookGenre`:

```python
class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    books = models.ManyToManyField(Book, related_name='genres', through='BookGenre')
```

3. Создаём инлайн для промежуточной модели:

```python
from django.contrib import admin
from .models import Book, BookGenre, Genre

class BookGenreInline(admin.TabularInline):  # компактная таблица
    model = BookGenre
    extra = 1  # одна пустая форма для добавления нового жанра
    can_delete = True
```

4. Подключаем инлайн к `BookAdmin`:

```python
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'year_published', 'is_deleted')
    inlines = [BookDetailInline, BookGenreInline]  # оба инлайна одновременно
```

✅ Теперь при редактировании книги в админке появятся:

* Блок `BookDetail` (StackedInline) — развернутый блок с полями `summary` и `page_count`.
* Таблица `BookGenre` (TabularInline) — компактная таблица для добавления/удаления жанров.


