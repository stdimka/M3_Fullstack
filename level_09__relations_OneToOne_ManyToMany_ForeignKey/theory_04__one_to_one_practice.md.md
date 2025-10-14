## Модели:

Ещё раз (для памяти) дублируем связанные модели

```python
class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    title = models.CharField(max_length=200)
    year_published = models.IntegerField()

class BookDetail(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name='detail')
    summary = models.TextField()
    page_count = models.IntegerField()
```

---

## Доступ из одной модели к другой

### Из `Book` к `BookDetail`

```python
book = Book.objects.get(id=1)
summary = book.detail.summary
pages = book.detail.page_count
```

Здесь используется `related_name='detail'`, поэтому нужно писать `book.detail`.  
(иначе - ошибка AttributeError)

> ⚠️ Без `related_name`, Django создаст имя по умолчанию: `bookdetail`.

---

### Из `BookDetail` к `Book`

```python
detail = BookDetail.objects.get(id=1)
title = detail.book.title
author = detail.book.author.name  # немного забегая вперёд
```

---

## 🔍 Примеры запросов

### Найти все книги, у которых больше 300 страниц

```python
from django.db.models import F

books = Book.objects.filter(detail__page_count__gt=300)
```

### Найти аннотацию (`summary`) книги с названием (`title`) "1984"

```python
summary = BookDetail.objects.get(book__title="1984").summary
```

### Получить год издания (`year_published`) через `BookDetail`

```python
detail = BookDetail.objects.select_related('book').get(id=1)
print(detail.book.year_published)
```

> `select_related` — оптимизация: сразу делает JOIN, чтобы не было лишнего запроса.
> ⚠️ Как проверить? - см. в следующем файле [theory_05__how_check_query.md](./theory_05__how_check_query.md)
---

## 🛠 Создание объектов

```python
# Создать книгу
author = Author.objects.create(name="Orwell")  # снова забегаем вперёд - связь по FK будет дальше

book = Book.objects.create(author=author, title="1984", year_published=1949)

# Привязать BookDetail
BookDetail.objects.create(book=book, summary="Anti-utopia", page_count=328)
```

