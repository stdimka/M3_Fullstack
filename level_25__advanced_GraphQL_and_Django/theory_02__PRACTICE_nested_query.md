## 1. Что такое вложенные запросы

**Вложенный запрос** в GraphQL — это запрос, в котором мы получаем сам объект плюс связанные с ним объекты.

Это одна из ключевых возможностей GraphQL:
* вы можете **запрашивать данные на разных уровнях связей в одной операции**, 
* без дополнительных запросов к API.

### Ключевая идея

> Клиент сам управляет тем, насколько глубоко он хочет "спуститься" по связям между моделями.

---

## 2. Связи в нашей БД 

Напомним, у нас есть связи:

```python
class Author(models.Model):
    name = models.CharField(max_length=255)

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, related_name="books", on_delete=models.CASCADE)
    year_published = models.IntegerField()

class BookDetail(models.Model):
    book = models.OneToOneField(Book, related_name="detail", on_delete=models.CASCADE)
    summary = models.TextField()
    page_count = models.IntegerField()
```

---

## 3. Пример вложенного запроса (Author → Book → BookDetail)

Запросим всех авторов, их книги и подробности по каждой книге:

```graphql
query {
  allAuthors {
    id
    name
    books {
      id
      title
      yearPublished
      detail {
        summary
        pageCount
      }
    }
  }
}
```

### Что делает этот запрос:

* `allAuthors` — обращается к резолверу, возвращающему всех авторов.
* Для каждого автора:

  * Получаем его `books` (через `related_name="books"`).
  * Для каждой книги — детальную информацию (`detail`).

---

### Пример ответа

```json
{
  "data": {
    "allAuthors": [
      {
        "id": "1",
        "name": "Лев Толстой",
        "books": [
          {
            "id": "1",
            "title": "Война и мир",
            "yearPublished": 1869,
            "detail": {
              "summary": "Новое описание",
              "pageCount": 200
            }
          },
          {
            "id": "20",
            "title": "Война и мир +++",
            "yearPublished": 1869,
            "detail": null
          },
          {
            "id": "57",
            "title": "Новая книга",
            "yearPublished": 2025,
            "detail": {
              "summary": "Краткое описание",
              "pageCount": 120
            }
          }
        ]
      },
      ...
      
  }
```

---

## 4. Обратный пример (Book → Author)

Можно пойти в другую сторону — запросить книги и “подняться вверх” к автору:

```graphql
query {
  allBooks {
    id
    title
    yearPublished
    author {
      id
      name
    }
  }
}
```

---

## 5. Как это работает “под капотом”

Каждый уровень в GraphQL резолвится отдельным **резолвером**:

* `resolve_all_authors` возвращает список авторов.
* Для каждого автора Graphene автоматически вызывает подрезолвер для `books` (если `related_name="books"`).
* Для каждой книги — ещё один для `detail`.

Таким образом, GraphQL “шагает” по ORM-связям, следуя структуре нашего запроса.

---

## 6. Преимущества

| Преимущество                  | Описание                                                             |
|-------------------------------| -------------------------------------------------------------------- |
| Один запрос вместо нескольких | Получаете данные сразу со всех уровней                               |
| Гибкость                      | Клиент выбирает, какие поля нужны                                    |
| Оптимизация                   | Можно использовать `select_related` и `prefetch_related` в резолверах |

