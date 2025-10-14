## Примеры запросов к ManyToMany

### ✅ Получить все жанры книги "1984"

```python
book = Book.objects.get(title="1984")
genres = book.genres.all()

for genre in genres:
    print(genre.name)
```

---

### ✅ Получить все книги жанра "Роман"

```python
genre = Genre.objects.get(name="Роман")
books = genre.books.all()

for book in books:
    print(f"{book.title} ({book.author.name})")
```

Для одной позиции этот неэффективны запрос (по сути - 2 запроса) допустим.

Но для нескольких объектов лучше применить оптимизацию (`prefetch_related()`)

### ✅ Получить все книги и их жанры (все связи)

#### variant 1 (с оптимизацией)
```python
from django.db import connection, reset_queries

reset_queries()
books = Book.objects.prefetch_related('genres', 'author')

for book in books:
    genre_names = ", ".join([g.name for g in book.genres.all()])
    print(f"{book.title} — {book.author.name} — жанры: {genre_names}")

print("Всего запросов:", len(connection.queries))
```

#### variant 2 (без оптимизации)
```python
reset_queries()
books = Book.objects.all()  # без prefetch_related

for book in books:
    genre_names = ", ".join([g.name for g in book.genres.all()])
    print(f"{book.title} — {book.author.name} — жанры: {genre_names}")
    
print("Всего запросов:", len(connection.queries))
```
---

### ✅ Найти все книги, которые относятся к жанру "Классика" и "Роман"

```python
books = Book.objects.filter(
    genres__name="Классика"
).filter(
    genres__name="Роман"
).distinct()

for book in books:
    print(book.title)
```

> 🔍 Почему `distinct()`?
> Потому что `JOIN` удваивает записи, если совпало по двум жанрам.

---

### ✅ Получить все жанры, к которым принадлежит "Пушкин"

```python
author = Author.objects.get(name="Александр Пушкин")

# Сначала получим все жанры всех его книг
genres = Genre.objects.filter(books__author=author).distinct()

for genre in genres:
    print(genre.name)
```

---

### ✅ Получить всех авторов, у которых есть хотя бы одна книга в жанре "Фантастика"

```python
authors = Author.objects.filter(books__genres__name="Фантастика").distinct()

for author in authors:
    print(author.name)
```
`.distinct()`, чтобы исключить дублирование авторов - один автор может написать несколько фантастических книг

---

### ✅ Получить жанры с количеством книг в каждом

```python
from django.db.models import Count

genres = Genre.objects.annotate(book_count=Count('books'))

for genre in genres:
    print(f"{genre.name}: {genre.book_count} книг")
```

---

### ✅ Получить все книги без жанров

```python
books_without_genres = Book.objects.filter(genres=None)

for book in books_without_genres:
    print(book.title)
```

Если не лезть по связи ManyToMany дальше, то этот запрос вполне оптимален:

```sql
SELECT * FROM book
WHERE id NOT IN (
    SELECT book_id FROM book_genres
)
```

А вот если потребуется у найденных книг определить ещё и автора,  
то новый запрос лучше оптимизировать:

```python
books_without_genres = Book.objects.filter(genres=None).select_related('author')

for book in books_without_genres:
    print(f"{book.title} — {book.author.name}")
```

Его SQL-код:
```sql
SELECT 
    "book"."id",
    "book"."title",
    "book"."author_id",
    "author"."id",
    "author"."name"
FROM 
    "book"
INNER JOIN 
    "author" ON "book"."author_id" = "author"."id"
WHERE 
    "book"."id" NOT IN (
        SELECT "book_id" FROM "book_genres"
    );
```