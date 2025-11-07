## 6. Пример применения мутаций

### 6.1 Создание книги с деталями (CreateBook)

В `myapp/schema.py` добавим класс мутации:

```python
class CreateBook(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        author_id = graphene.Int(required=True)
        year_published = graphene.Int(required=True)  # ← добавляем
        summary = graphene.String()
        page_count = graphene.Int()

    book = graphene.Field(BookType)

    def mutate(root, info, title, author_id, year_published, summary="", page_count=0):
        user = info.context.user
        if not user.is_authenticated:
            raise Exception("Вы должны войти в систему, чтобы создать книгу")

        author = Author.objects.get(pk=author_id)
        book = Book.objects.create(
            title=title,
            author=author,
            year_published=year_published,  # ← передаём
        )
        BookDetail.objects.create(book=book, summary=summary, page_count=page_count)
        return CreateBook(book=book)

```

* `Arguments` — это поля, которые клиент передаёт в мутацию.
* Возвращаем `book`, чтобы клиент видел результат.

---

### 6.2 Обновление книги (UpdateBook)

```python
class UpdateBook(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        year_published = graphene.Int()
        is_deleted = graphene.Boolean()
        summary = graphene.String()
        page_count = graphene.Int()

    book = graphene.Field(BookType)  
    #  т.е. Field указывает, что book - это составной объект BookType

    def mutate(root, info, id, **kwargs):
        book = Book.objects.get(pk=id)
        detail = getattr(book, 'detail', None)
        
        # ---- Пояснение: -----
        # detail = getattr(book, 'detail', None) 
        #    - это эквивалент кода
        # if hasattr(book, 'detail'):
        #     detail = book.detail
        # else:
        #     detail = None

        if 'title' in kwargs and kwargs['title'] is not None:
            book.title = kwargs['title']
        if 'year_published' in kwargs and kwargs['year_published'] is not None:
            book.year_published = kwargs['year_published']
        if 'is_deleted' in kwargs and kwargs['is_deleted'] is not None:
            book.is_deleted = kwargs['is_deleted']
        book.save()

        if detail:
            if 'summary' in kwargs and kwargs['summary'] is not None:
                detail.summary = kwargs['summary']
            if 'page_count' in kwargs and kwargs['page_count'] is not None:
                detail.page_count = kwargs['page_count']
            detail.save()

        return UpdateBook(book=book)
```

---

### 6.3 Удаление книги (DeleteBook)

```python
from graphql import GraphQLError


class DeleteBook(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    def mutate(root, info, id):
        try:
            book = Book.objects.get(pk=id)
        except Book.DoesNotExist:
            raise GraphQLError("A book with this ID does not exist.")

        book.delete()
        return DeleteBook(ok=True)
```

---

### 6.4 Добавление мутаций в схему

В конце `schema.py`:

```python
class Mutation(graphene.ObjectType):
    create_book = CreateBook.Field()
    update_book = UpdateBook.Field()
    delete_book = DeleteBook.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
```

---

### 6.5 Примеры GraphQL-запросов

#### Создание книги

```graphql
mutation {
  createBook(
    title: "Новая книга",
    authorId: 1,
    yearPublished: 2025,
    summary: "Краткое описание",
    pageCount: 120
  ) {
    book {
      id
      title
      author {
        name
      }
      detail {
        summary
        pageCount
      }
    }
  }
}
```

Запрос вернёт книгу с её id (примерно так):

```graphql
{
  "data": {
    "createBook": {
      "book": {
        "id": "54",
        "title": "Новая книга",
        "author": {
          "name": "Лев Толстой"
        },
        "detail": {
          "summary": "Краткое описание",
          "pageCount": 120
        }
      }
    }
  }
}
```

⚠️ Необходимо подставить этот id книги в следующие запросы!

#### Обновление книги

⚠️ Исправьте id 1 на РЕАЛЬНЫЙ id свеже-добавленной книги!

```graphql
mutation {
  updateBook(
    id: 1,
    title: "Обновлённая книга",
    summary: "Новое описание",
    pageCount: 200
  ) {
    book {
      id
      title
      detail {
        summary
        pageCount
      }
    }
  }
}
```

#### Удаление книги

⚠️ Исправьте id 1 на РЕАЛЬНЫЙ id свеже-добавленной книги!

```graphql
mutation {
  deleteBook(id: 1) {
    ok
  }
}
```

---

### 6.6 Итог

После этого пункта:

* Мы можем создавать, обновлять и удалять книги через GraphQL.
* Клиент получает обратно данные, которые изменились.
* Мутации полностью заменяют формы и CBV на стороне API.

