# Пагинация

### 8.1 Зачем нужна пагинация

* Если в базе много книг, возвращать их все сразу неэффективно.
* Пагинация позволяет отдавать данные **частями**, например по 10 записей на страницу.
* GraphQL не навязывает способ пагинации, но есть два популярных подхода:

  1. **Limit / Offset** — простая реализация “страницы N по M элементов”.
  2. **Cursor-based** — более гибкая для больших или постоянно изменяющихся списков.

---

## 2 Простая пагинация через аргументы limit и offset

В `schema.py` для списка книг добавим аргументы:

```python
class Query(graphene.ObjectType):
    all_books = graphene.List(
        BookType,
        limit=graphene.Int(),
        offset=graphene.Int()
    )

    def resolve_all_books(root, info, limit=None, offset=None):
        qs = Book.objects.filter(is_deleted=False).order_by("id")
        if offset:
            qs = qs[offset:]
        if limit:
            qs = qs[:limit]
        return qs
```

* `limit` — сколько записей вернуть.
* `offset` — сколько пропустить с начала.
* Пример запроса:

```graphql
query {
  allBooks(limit: 5, offset: 10) {
    id
    title
  }
}
```

* Этот запрос вернёт **5 книг, начиная с 11-й** (смещение 10).

---

## 3 Cursor-based пагинация

```python
import base64
from graphene import ObjectType, String, Int, Field, List
import graphene
from .models import Book


# Вспомогательные функции для кодирования/декодирования курсоров
def encode_cursor(book_id: int) -> str:
    return base64.b64encode(f"{book_id}".encode()).decode()


def decode_cursor(cursor: str) -> int:
    return int(base64.b64decode(cursor.encode()).decode())


# Тип книги
class BookType(graphene.ObjectType):
    id = graphene.Int()
    title = graphene.String()
    author = graphene.String()


# Тип для информации о странице
class PageInfoType(graphene.ObjectType):
    has_next_page = graphene.Boolean()
    end_cursor = graphene.String()


# Тип результата пагинации
class BookConnection(graphene.ObjectType):
    edges = graphene.List(BookType)
    page_info = Field(PageInfoType)


# Основной запрос
class Query(ObjectType):
    all_books = Field(
        BookConnection,
        first=Int(default_value=5),
        after=String()
    )

    def resolve_all_books(root, info, first, after=None):
        qs = Book.objects.filter(is_deleted=False).order_by("id")

        # Если передан курсор — начинаем после него
        if after:
            try:
                last_id = decode_cursor(after)
                qs = qs.filter(id__gt=last_id)
            except Exception:
                pass

        # Берём `first + 1`, чтобы понять, есть ли следующая страница
        books = list(qs[: first + 1])

        has_next_page = len(books) > first
        books = books[:first]

        end_cursor = encode_cursor(books[-1].id) if books else None

        return BookConnection(
            edges=books,
            page_info=PageInfoType(
                has_next_page=has_next_page,
                end_cursor=end_cursor,
            ),
        )
```

---

### Пример GraphQL-запроса

```graphql
query {
  allBooks(first: 5) {
    edges {
      id
      title
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

---

### Пример ответа

```json
{
  "data": {
    "allBooks": {
      "edges": [
        { "id": 2, "title": "Book B" },
        { "id": 3, "title": "Book C" },
        { "id": 4, "title": "Book D" },
        { "id": 5, "title": "Book E" },
        { "id": 6, "title": "Book F" }
      ],
      "pageInfo": {
        "hasNextPage": true,
        "endCursor": "Ng=="
      }
    }
  }
}
```

В ответе содержится значение следующего курсора `"Ng=="`.  
Его указываем в следующем запросе:

```graphql
query {
  allBooks(first: 5, after: "Ng==") {
    edges {
      id
      title
    }
    pageInfo {
      hasNextPage
      endCursor
    }
  }
}
```

---

### Итого:

* **Гибкость** — можно менять формат курсора, фильтры и сортировку.
* **Контроль** — полная прозрачность в том, как данные извлекаются и кодируются.

---

## 4 Итог

* Для небольших проектов можно использовать **limit/offset**.
* Для больших и динамических данных лучше использовать **cursor-based пагинацию**.
* Пагинация в GraphQL позволяет клиенту управлять, **сколько и какие записи** получать.

