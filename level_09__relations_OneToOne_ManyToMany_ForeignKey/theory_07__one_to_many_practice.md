## Модели:

Ещё раз (для памяти) дублируем связанные модели

```python
class Author(models.Model):
    name = models.CharField(max_length=100, unique=True)

class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')    
    title = models.CharField(max_length=200)
    year_published = models.IntegerField()
```

---

## ✅ Django: Связь **один ко многим** (One-to-Many)

---

## Доступ из одной модели к другой

### Из `Author` к связанным `Book` ("обратная связь")

```python
author = Author.objects.get(name="Джордж Оруэлл")
books = author.books.all()  # thanks to related_name='books'
```

⚠️ Если бы `related_name` не было, нужно было бы писать `author.book_set.all()`.

---

### Из `Book` к `Author`  ("прямая связь")

```python
book = Book.objects.get(title="1984")
author_name = book.author.name
```

---

## 🔍 Примеры запросов

### 📘 Найти все книги, опубликованные после 1900 года

```python
recent_books = Book.objects.filter(year_published__gt=1900)
```

---

### 🖊 Найти всех авторов, у которых есть хотя бы одна книга

```python
from django.db.models import Count

authors_with_books = Author.objects.annotate(book_count=Count('books')).filter(book_count__gte=1)
```

---

### 📚 Найти всех авторов, у которых есть книга с названием "1984"

```python
authors = Author.objects.filter(books__title="1984")
```

---

### 📅 Получить список книг определённого автора

```python
author = Author.objects.get(name="Джордж Оруэлл")
titles = author.books.values_list('title', flat=True)
```

---

## 🛠 Создание объектов

```python
# Создать автора
orwell, _ = Author.objects.get_or_create(name="Джордж Оруэлл")
# помним, что get_or_create возвращает тюпл (object, created)
# Создать книги
Book.objects.create(author=orwell, title="Скотный двор", year_published=1945)

# Или так (с сохранением)
book = Book(title="Глотнуть воздуха", year_published=1939)
book.author = orwell
book.save()
```

---

## ⚡ Оптимизация запросов

Если заранее известно, что вам понадобятся книги вместе с авторами — используйте `select_related` (при доступе к FK):

```python
books = Book.objects.select_related('author').all()

for book in books:
    print(f"{book.title} — {book.author.name}")  # не будет дополнительных SQL-запросов
```

Если идёи от автора к книгам — используем `prefetch_related`:

```python
authors = Author.objects.prefetch_related('books').all()

for author in authors:
    for book in author.books.all():
        print(f"{author.name} — {book.title}")
```

