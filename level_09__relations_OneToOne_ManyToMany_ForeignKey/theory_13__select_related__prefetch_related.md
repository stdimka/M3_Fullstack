И ещё раз "на зачёт")

## **Что такое "оптимизация выборки"?**

Когда вы делаете запросы к базе данных, Django может выполнять **много мелких SQL-запросов**,   
особенно если вы обращаетесь к связанным моделям (`ForeignKey`, `ManyToMany` и т.д.).

Это замедляет работу.  
Чтобы **снизить количество SQL-запросов**, Django предоставляет инструменты:

* `select_related()` — для **ForeignKey / OneToOne** (т.е. "один к одному" или "многие к одному");
* `prefetch_related()` — для **ManyToMany и reverse ForeignKey** (т.е. "многие ко многим" и "один ко многим").

---

## 🔹 Пример без оптимизации

Модели:

```python
class Author(models.Model):
    name = models.CharField(max_length=100, unique=True)

class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')    
    title = models.CharField(max_length=200)
    year_published = models.IntegerField()

```

Код:

```python
from django.db import connection, reset_queries

reset_queries()  # очищаем предыдущие запросы
books = Book.objects.all()
for book in books:
    print(book.title, book.author.name)

print("Итого запросов:", len(connection.queries))
```

**Что произойдёт:**

* 1 запрос на выборку всех книг;
* по 1 запросу на каждого автора (если 10 книг — до 11 SQL-запросов!).

---

## ✅ Оптимизация с `select_related()`

```python
reset_queries()  # очищаем предыдущие запросы

books = Book.objects.select_related("author")
for book in books:
    print(book.title, book.author.name)

print("Итого запросов:", len(connection.queries))
```

**Что делает `select_related()`**:

* Выполняет **JOIN**: одна SQL-команда достаёт и `Book`, и `Author`;
* Количество запросов: **всего 1**;
* Работает только для `ForeignKey` и `OneToOne`.

---

## ✅ Оптимизация с `prefetch_related()`

Пример для `ManyToMany`:

```python
class BookDetail(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name='detail')
    summary = models.TextField()
    page_count = models.IntegerField()

# many-to-many — жанры книг
class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    books = models.ManyToManyField(Book, related_name='genres')

```

Без оптимизации:

```python
reset_queries()  # очищаем предыдущие запросы

for book in Book.objects.all():
    print(book.title, [genre.name for genre in book.genres.all()])
    
print("Итого запросов:", len(connection.queries))
```

**Результат:**

* 1 запрос на книги
* 1 запрос на жанры **на каждую книгу** → много запросов

**С оптимизацией:**

```python
reset_queries()  # очищаем предыдущие запросы

books = Book.objects.prefetch_related("genres")
for book in books:
    print(book.title, [genre.name for genre in book.genres.all()])
    
print("Итого запросов:", len(connection.queries))
```

Теперь:

* 1 запрос на книги
* 1 запрос на все нужные жанры
  → всего 2 запроса, Django сам всё связывает в Python-объектах.

---

## 🧠 Итого

| Метод                | Подходит для связи       | Что делает                               | Кол-во SQL |
| -------------------- | ------------------------ | ---------------------------------------- | ---------- |
| `select_related()`   | `ForeignKey`, `OneToOne` | Использует JOIN                          | 1          |
| `prefetch_related()` | `ManyToMany`, reverse FK | Выполняет 2 запроса и связывает в Python | 2          |

