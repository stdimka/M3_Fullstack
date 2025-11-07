Для иллюстрации примеров по теме связей давайте добавим три модели (и изменим Book):

```python
# Выносим автора по 1-to-many в отдельную модель
class Author(models.Model):
    name = models.CharField(max_length=100, unique=True)

# В изменённой модели Книга автор связан по ForeignKey с моделью Author
class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')    
    title = models.CharField(max_length=200)
    year_published = models.IntegerField()
     
# 1-to-1 связь — подробное описание книги
class BookDetail(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name='detail')
    summary = models.TextField()
    page_count = models.IntegerField()

# many-to-many — жанры книг
class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    books = models.ManyToManyField(Book, related_name='genres')
```

Таким образом, с учётом методом добавления тестовых данных мы имеем:
```python
from django.db import models


class MyappModel(models.Model):
    code = models.CharField(max_length=50, unique=True)
    value = models.TextField()


class Author(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    @classmethod
    def fill_if_empty(cls, books_data):
        if cls.objects.exists():
            return

        unique_authors = {data["author"] for data in books_data}
        for name in unique_authors:
            cls.objects.create(name=name)


class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    title = models.CharField(max_length=200)
    year_published = models.IntegerField()

    def __str__(self):
        return f"{self.title} ({self.author})"

    @classmethod
    def fill_if_empty(cls, books_data):
        if cls.objects.exists():
            return

        for data in books_data:
            try:
                author = Author.objects.get(name=data["author"])
                cls.objects.create(
                    author=author,
                    title=data["title"],
                    year_published=data["year_published"],
                )
            except Author.DoesNotExist:
                continue


class BookDetail(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name='detail')
    summary = models.TextField()
    page_count = models.IntegerField()

    def __str__(self):
        return f"Details for {self.book.title}"

    @classmethod
    def fill_if_empty(cls, books_data):
        if cls.objects.exists():
            return

        for data in books_data:
            try:
                book = Book.objects.get(title=data["title"])
                cls.objects.create(
                    book=book,
                    summary=data["summary"],
                    page_count=data["page_count"]
                )
            except Book.DoesNotExist:
                continue


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    books = models.ManyToManyField(Book, related_name='genres')

    def __str__(self):
        return self.name

    @classmethod
    def fill_if_empty(cls, books_data):
        if cls.objects.exists():
            return

        # собрать все уникальные жанры
        unique_genres = set()
        for data in books_data:
            unique_genres.update(data["genres"])
        for genre_name in unique_genres:
            cls.objects.create(name=genre_name)

    @classmethod
    def assign_books(cls, books_data):
        for data in books_data:
            try:
                book = Book.objects.get(title=data["title"])
                for genre_name in data["genres"]:
                    genre = Genre.objects.get(name=genre_name)
                    book.genres.add(genre)
            except (Book.DoesNotExist, Genre.DoesNotExist):
                continue
```

Для заполнения всех трёх моделей так же надо изменить `MyappAutofillConfig` в `apps.py`:
```python
from django.apps import AppConfig

class MyappAutofillConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'

    def ready(self):
        from .models import Author, Book, BookDetail, Genre
        from .book_data import BOOKS_DATA

        Author.fill_if_empty(BOOKS_DATA)
        Book.fill_if_empty(BOOKS_DATA)
        BookDetail.fill_if_empty(BOOKS_DATA)
        Genre.fill_if_empty(BOOKS_DATA)
        Genre.assign_books(BOOKS_DATA)
```

Как видим, менять нужно многое и во многих местах.  
Поэтому самое простое и логичное в нашей ситуации сделать следующее:
1. Удалить все миграции в `myapp`
1. Удалить файл БД `db.sqlite3`
1. Полностью заменить содержимое `models.py`
1. Закоментировать метод `ready` в классе `MyappAutofillConfig` модуля `apps.py` (иначе Django попытается заполнить только таблицу Books)
1. Заново создать (`./manage.py makemigrations`) и применить (`./manage.py migrate`) миграции
1. Добавить файл `book_data.py` в папку приложения
1. Изменить класс `MyappAutofillConfig` в `apps.py`
1. Запустить Django, чтобы заполнить таблицы


Обратите внимание: раньше (с одной моделью Book) мы могли проводить миграции с уже подключенной проверкой в `ready()`.  
Сейчас (с тремя связанными между собой моделями) мы этого не можем.  
Почему?  

### Почему для связанных таблицы надо СНАЧАЛА создать таблицы и только ПОТОМ подключать `ready()` в `MyappAutofillConfig`?

Прежний запрос на наличие записей в таблице (пустая/не пустая) был "ленивым":
```python
@classmethod
def fill_if_empty(cls):
    if cls.objects.exists():  # <- Это вызов к БД, но он обрабатывался "мягко"
        return
```
 
Теперь же, для проверки связанных таблиц (пустая/не пустая) необходимо явное прохождения по каждой связи.  
Что невозможно, когда таблицы ещё не созданы.