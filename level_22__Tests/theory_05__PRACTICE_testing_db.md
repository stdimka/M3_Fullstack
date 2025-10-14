# Тестируем БД с помощью pytest-django

## 1. Установка pytest и pytest-django

1. Установливем `pytest` и `pytest-django`:

```bash
pip install pytest pytest-django
```

2. И проверяем установку:

```bash
pytest --version
```

---

## 2. Настройка pytest-django

1. Создаём файл `pytest.ini` в корне проекта Django:

```ini
[pytest]
DJANGO_SETTINGS_MODULE = main.settings
python_files = tests.py test_*.py *_tests.py
```

* `DJANGO_SETTINGS_MODULE` — укажите путь к настройкам Django в проекте.
* `python_files` — паттерны, по которым pytest будет искать тесты.

2. На всякий случай, ещё раз убеждаемся, что в `settings.py` включены все 
   необходимые приложения (`INSTALLED_APPS`) для тестов.

---

## 3. Размещение тестов

Рекомендуемая структура:

```
your_project/
├── app/
│   ├── models.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_models.py
│   │   └── test_views.py
```

* Внутри `tests/` создаём отдельные файлы для моделей, вью и других частей приложения.
* Для небольших проектов допустим один общий файл `tests.py`

---
## 4. План тестов и их целей

| Тест                                            | Цель проверки                                                    |
| ----------------------------------------------- | ---------------------------------------------------------------- |
| `test_create_author`                            | Проверка, что объект `Author` создаётся и корректно отображается |
| `test_unique_author_name`                       | Проверка уникального ограничения для `Author.name`               |
| `test_create_book_with_author`                  | Проверка создания книги с автором                                |
| `test_book_deletion_with_author`                | Проверка каскадного удаления книг при удалении автора            |
| `test_book_is_deleted_flag`                     | Проверка работы логического флага `is_deleted`                   |
| `test_book_detail_one_to_one`                   | Проверка связи один-к-одному `Book ↔ BookDetail`                 |
| `test_bookdetail_unique_constraint`             | Проверка уникальности `BookDetail` для каждой книги              |
| `test_genre_many_to_many_relationship`          | Проверка связи `Book ↔ Genre`                                    |
| `test_unique_genre_name`                        | Проверка уникальности имени жанра                                |
| `test_create_full_book_with_details_and_genres` | Полная проверка работы всех связей вместе                        |



---

## 5. Реализация тестов для моделей

Создаём файл `myapp/tests/test_models.py`:

```python
import pytest
from django.db import IntegrityError
from myapp.models import Author, Book, BookDetail, Genre

pytestmark = pytest.mark.django_db  # все тесты используют тестовую БД


# ---------- Тесты модели Author ----------

def test_create_author():
    """ Проверка создания автора"""
    author = Author.objects.create(name="Leo Tolstoy")
    assert author.name == "Leo Tolstoy"
    assert str(author) == "Leo Tolstoy"


def test_unique_author_name():
    """ Проверка уникальности имени автора"""
    Author.objects.create(name="Leo Tolstoy")
    with pytest.raises(IntegrityError):
        Author.objects.create(name="Leo Tolstoy")  # должно вызвать ошибку уникальности


# ---------- Тесты модели Book ----------

def test_create_book_with_author():
    """ Проверка создания книги и связи с автором"""
    author = Author.objects.create(name="Leo Tolstoy")
    book = Book.objects.create(author=author, title="War and Peace", year_published=1869)
    assert book.author == author
    assert book.year_published == 1869
    assert str(book) == "War and Peace (Leo Tolstoy)"


def test_book_deletion_with_author():
    """ Проверка каскадного удаления книги при удалении автора"""
    author = Author.objects.create(name="Leo Tolstoy")
    book = Book.objects.create(author=author, title="Anna Karenina", year_published=1877)
    author.delete()
    assert Book.objects.count() == 0  # книга должна удалиться каскадно


def test_book_is_deleted_flag():
    """ Проверка логического удаления (is_deleted)"""
    author = Author.objects.create(name="Leo Tolstoy")
    book = Book.objects.create(author=author, title="Resurrection", year_published=1899, is_deleted=True)
    assert book.is_deleted
    active_books = Book.objects.filter(is_deleted=False)
    assert not active_books.exists()  # таких книг нет


# ---------- Тесты модели BookDetail ----------

def test_book_detail_one_to_one():
    """ Проверка OneToOne связи между Book и BookDetail"""
    author = Author.objects.create(name="Leo Tolstoy")
    book = Book.objects.create(author=author, title="Childhood", year_published=1852)
    detail = BookDetail.objects.create(book=book, summary="Autobiographical novel", page_count=200)
    assert detail.book == book
    assert book.detail == detail
    assert str(detail) == "Details for Childhood"


def test_bookdetail_unique_constraint():
    """ Проверка, что у одной книги не может быть два BookDetail"""
    author = Author.objects.create(name="Leo Tolstoy")
    book = Book.objects.create(author=author, title="Youth", year_published=1856)
    BookDetail.objects.create(book=book, summary="First", page_count=150)
    with pytest.raises(IntegrityError):
        BookDetail.objects.create(book=book, summary="Duplicate", page_count=200)


# ---------- Тесты модели Genre ----------

def test_genre_many_to_many_relationship():
    """ Проверка связи ManyToMany (Book ↔ Genre)"""
    author = Author.objects.create(name="Leo Tolstoy")
    book = Book.objects.create(author=author, title="War and Peace", year_published=1869)
    genre1 = Genre.objects.create(name="Historical")
    genre2 = Genre.objects.create(name="Classic")
    book.genres.add(genre1, genre2)
    assert book.genres.count() == 2
    assert genre1.books.first() == book


def test_unique_genre_name():
    """ Проверка уникальности имени жанра"""
    Genre.objects.create(name="Historical")
    with pytest.raises(IntegrityError):
        Genre.objects.create(name="Historical")


# ---------- Комплексный тест ----------

def test_create_full_book_with_details_and_genres():
    """
    Комплексный тест:
    - создаём автора
    - создаём книгу
    - добавляем детали (BookDetail)
    - добавляем жанры (Genre)
    - проверяем все связи
    """
    author = Author.objects.create(name="Leo Tolstoy")
    book = Book.objects.create(author=author, title="War and Peace", year_published=1869)
    detail = BookDetail.objects.create(book=book, summary="Epic novel", page_count=1225)
    genre1 = Genre.objects.create(name="Historical")
    genre2 = Genre.objects.create(name="Epic")
    book.genres.add(genre1, genre2)

    book.refresh_from_db()

    # Проверяем связи
    assert book.author.name == "Leo Tolstoy"
    assert book.detail.page_count == 1225
    assert set(book.genres.values_list("name", flat=True)) == {"Historical", "Epic"}
    assert str(book) == "War and Peace (Leo Tolstoy)"

```

⚠️ Внимание!!!
Не может одновременно в одном проекте находится папка `tests` и файл `tests.py`.
---

## 6. Запуск тестов

1. В корне проекта выполняем:

```bash
pytest -v
```

* `-v` — подробный вывод.
* Pytest автоматически создаёт временную тестовую базу данных (обычно SQLite),  
  чтобы не трогать вашу основную.


Возможен также запуск конкретного файла тестов:

```bash
pytest -v app/tests/test_models.py
```

Иногда дополнительно полезно использовать:

```bash
pytest --maxfail=3 --tb=short
```

* `--maxfail=3` — остановка после 3-х ошибок.
* `--tb=short` — краткий формат трассировки ошибок.
---


## 7. Анализ результатов

Пример вывода:

```
 pytest -v
============================================================ test session starts ============================================================
platform linux -- Python 3.12.10, pytest-8.4.2, pluggy-1.6.0 -- /home/su/DjangoProjects/tdd_2/.venv/bin/python3.12
cachedir: .pytest_cache
django: version: 5.2.5, settings: main.settings (from ini)
rootdir: /home/su/DjangoProjects/tdd_2
configfile: pytest.ini
plugins: django-4.11.1
collected 10 items                                                                                                                          

myapp/tests/test_models.py::test_create_author PASSED                                                                                 [ 10%]
myapp/tests/test_models.py::test_unique_author_name PASSED                                                                            [ 20%]
myapp/tests/test_models.py::test_create_book_with_author PASSED                                                                       [ 30%]
myapp/tests/test_models.py::test_book_deletion_with_author PASSED                                                                     [ 40%]
myapp/tests/test_models.py::test_book_is_deleted_flag PASSED                                                                          [ 50%]
myapp/tests/test_models.py::test_book_detail_one_to_one PASSED                                                                        [ 60%]
myapp/tests/test_models.py::test_bookdetail_unique_constraint PASSED                                                                  [ 70%]
myapp/tests/test_models.py::test_genre_many_to_many_relationship PASSED                                                               [ 80%]
myapp/tests/test_models.py::test_unique_genre_name PASSED                                                                             [ 90%]
myapp/tests/test_models.py::test_create_full_book_with_details_and_genres PASSED                                                      [100%]

============================================================ 10 passed in 0.32s =============================================================
```

* `PASSED` — тест прошёл успешно.
* Если тест не прошёл, pytest покажет точку ошибки, трассировку и значения, 
   которые не совпали с ожиданиями.

  
