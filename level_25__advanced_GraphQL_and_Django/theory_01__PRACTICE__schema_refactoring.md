# Рефакторинг файла `schema.py`

Наш файл `schema.py` разросся и уже стал мало удобен для работы.  
Поэтому, пришло время изменить его структуру на более удобную.

## Обновлённая структура

```
myapp/
│
├── schema/
│   ├── __init__.py
│   ├── types.py
│   ├── queries.py
│   ├── mutations/
│   │   ├── __init__.py
│   │   ├── create_book.py
│   │   ├── update_book.py
│   │   └── delete_book.py
│   └── schema.py
│
└── models.py
```

---

## 1 `types.py`

Типы (обертки над Django-моделями):

```python
import graphene
from graphene_django import DjangoObjectType
from ..models import Author, Book, BookDetail, Genre


class AuthorType(DjangoObjectType):
    class Meta:
        model = Author
        fields = '__all__'


class BookDetailType(DjangoObjectType):
    class Meta:
        model = BookDetail
        fields = '__all__'


class BookType(DjangoObjectType):
    class Meta:
        model = Book
        fields = '__all__'


class GenreType(DjangoObjectType):
    class Meta:
        model = Genre
        fields = ('name',)
```

---

## 2 `queries.py`

Запросы (Query):

```python
import graphene
from graphql import GraphQLError
from ..models import Author, Book
from .types import BookType, AuthorType


class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Привет, GraphQL!")
    all_books = graphene.List(BookType)
    all_authors = graphene.List(AuthorType)
    book_by_id = graphene.Field(BookType, id=graphene.Int(required=True))

    @staticmethod
    def resolve_all_books(root, info):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Неавторизованный пользователь")
        return Book.objects.filter(is_deleted=False)

    @staticmethod
    def resolve_all_authors(root, info):
        return Author.objects.all()

    @staticmethod
    def resolve_book_by_id(root, info, id):
        return Book.objects.get(pk=id)
```

---

## 3 `mutations/create_book.py`

```python
import graphene
from graphql import GraphQLError
from ...models import Author, Book, BookDetail
from ..types import BookType


class CreateBook(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        author_id = graphene.Int(required=True)
        year_published = graphene.Int(required=True)
        summary = graphene.String()
        page_count = graphene.Int()

    book = graphene.Field(BookType)

    def mutate(root, info, title, author_id, year_published, summary="", page_count=0):
        user = info.context.user
        if not user.is_authenticated:
            raise GraphQLError("Вы должны войти в систему, чтобы создать книгу")

        author = Author.objects.get(pk=author_id)
        book = Book.objects.create(
            title=title,
            author=author,
            year_published=year_published,
        )
        BookDetail.objects.create(book=book, summary=summary, page_count=page_count)
        return CreateBook(book=book)
```

---

## 4 `mutations/update_book.py`

```python
import graphene
from graphql import GraphQLError
from ...models import Book
from ..types import BookType


class UpdateBook(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        title = graphene.String()
        year_published = graphene.Int()
        is_deleted = graphene.Boolean()
        summary = graphene.String()
        page_count = graphene.Int()

    book = graphene.Field(BookType)

    def mutate(root, info, id, **kwargs):
        try:
            book = Book.objects.get(pk=id)
        except Book.DoesNotExist:
            raise GraphQLError("Книга с таким ID не найдена")

        detail = getattr(book, 'detail', None)

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

## 5 `mutations/delete_book.py`

```python
import graphene
from graphql import GraphQLError
from ...models import Book


class DeleteBook(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    ok = graphene.Boolean()

    def mutate(root, info, id):
        try:
            book = Book.objects.get(pk=id)
        except Book.DoesNotExist:
            raise GraphQLError("Книга с таким ID не существует.")

        book.delete()
        return DeleteBook(ok=True)
```

---

## 6 `mutations/__init__.py`

Объединяет все мутации в одном месте:

```python
import graphene
import graphql_jwt
from .create_book import CreateBook
from .update_book import UpdateBook
from .delete_book import DeleteBook


class Mutation(graphene.ObjectType):
    create_book = CreateBook.Field()
    update_book = UpdateBook.Field()
    delete_book = DeleteBook.Field()

    # JWT-мутации
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
```

---

## 7 `schema.py`

Главный файл, который объединяет всё:

```python
import graphene
from .queries import Query
from .mutations import Mutation

schema = graphene.Schema(query=Query, mutation=Mutation)
```

---

## 8 `schema/__init__.py`

```python
from .schema import schema
```

Файл `schema/__init__.py` как раз и позволяет сохранить тот же путь импорта,   
что был до того как файл `schema.py` превратился в папку `schema/`.

---

## 9. В этом месте логично прогнать наши тесты

Успешные тесты - это лучшая гарантия того, что рефакторинг выполнен без ошибок.

---

**Итог:**
Теперь код логично разделён:

* `types.py` — модели GraphQL.
* `queries.py` — запросы.
* `mutations/` — отдельные мутации.
* `schema.py` — только объединение.
