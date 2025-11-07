# 1 Оптимизация текущего запроса

Запрос:

```graphql
{
  allBooks {
    title
    yearPublished
    author { name }
    genres { name }
    detail { pageCount summary }
  }
}
```

У нас есть модельные связи:

| Поле     | Связь                           |
| -------- | ------------------------------- |
| `author` | ForeignKey (OneToOne/ManyToOne) |
| `genres` | ManyToMany                      |
| `detail` | OneToOne                        |

**Проблема N+1:**

* `author` → для каждой книги отдельный SELECT, если не использовать `select_related`.
* `genres` → для каждой книги отдельный SELECT через промежуточную таблицу, если не использовать `prefetch_related`.
* `detail` → для каждой книги отдельный SELECT, если не использовать `select_related`.

Если у вас 10 книг, без оптимизации может быть **10 + 10 + 10 = 30 SQL-запросов**, плюс основной SELECT → 31 запрос.

Для нашей БД из примерно 20 книг выходит 63 запроса

---

# 2  Оптимизация через ORM

В Django ORM используем **select_related** для ForeignKey и OneToOne и **prefetch_related** для ManyToMany.

```python
# models.py пример
# Book -> author (FK)
# Book -> genres (M2M)
# Book -> detail (OneToOne)

from .models import Book

books = Book.objects.all() \
    .select_related('author', 'detail') \
    .prefetch_related('genres')
```

Точные изменения в `myapp/schema/queries.py`:

```python
    def resolve_all_books(self, info, title=None, author_name=None,
                          genre_name=None, year_published=None,
                          year_published_range=None, order_by=None):
        # qs = Book.objects.all()
        qs = Book.objects.all().select_related('author', 'detail').prefetch_related('genres')

        if title:
            qs = qs.filter(title__icontains=title)
        if author_name:
            qs = qs.filter(author__name__icontains=author_name)
        if genre_name:
            qs = qs.filter(genres__name__icontains=genre_name)
        if year_published:
            qs = qs.filter(year_published=year_published)
        if year_published_range and len(year_published_range) == 2:
            start, end = year_published_range
            qs = qs.filter(year_published__gte=start, year_published__lte=end)
        if order_by:
            qs = qs.order_by(*order_by)
        return qs.distinct()
```

### Что делает каждая часть:

* `select_related('author', 'detail')`
  → объединяет таблицы `Book`, `Author` и `BookDetail` в один SQL JOIN.
* `prefetch_related('genres')`
  → делает **2 запроса**: один для книг, один для всех связанных жанров.
  → ORM соединяет данные в Python, **не создавая N+1**.

### Пример SQL после оптимизации

```sql
SELECT "book"."id", "book"."title", "book"."year_published",
       "author"."id", "author"."name",
       "bookdetail"."id", "bookdetail"."page_count", "bookdetail"."summary"
FROM "book"
LEFT JOIN "author" ON "book"."author_id" = "author"."id"
LEFT JOIN "bookdetail" ON "book"."id" = "bookdetail"."book_id";

SELECT "genres"."id", "genres"."name", "book_genres"."book_id"
FROM "genres"
INNER JOIN "book_genres" ON "genres"."id" = "book_genres"."genres_id"
WHERE "book_genres"."book_id" IN (1,2,3,...);
```

Результат: **количество SQL-запросов резко уменьшается** до 4-х

