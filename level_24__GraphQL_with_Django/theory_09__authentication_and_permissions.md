## 7. Аутентификация и разрешения в GraphQL

### 7.1 Доступ к пользователю через резолверы

В любом резолвере или мутации можно проверить текущего пользователя:

```python
class Query(graphene.ObjectType):
    all_books = graphene.List(BookType)

    def resolve_all_books(root, info):
        user = info.context.user  # текущий пользователь
        if not user.is_authenticated:
            raise Exception("Неавторизованный пользователь")
        return Book.objects.filter(is_deleted=False)
```

* `resolve_all_books` — резолвер для поля `all_books`.
* Здесь мы проверяем аутентификацию и фильтруем книги.

---

### 7.2 Ограничение доступа к мутациям

Пример мутации, доступной только авторизованным:

```python
class CreateBook(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        author_id = graphene.Int(required=True)
        summary = graphene.String()
        page_count = graphene.Int()

    book = graphene.Field(BookType)

    def mutate(root, info, title, author_id, summary="", page_count=0):
        user = info.context.user  # доступ к текущему пользователю
        if not user.is_authenticated:
            raise Exception("Вы должны войти в систему, чтобы создать книгу")

        author = Author.objects.get(pk=author_id)
        book = Book.objects.create(title=title, author=author)
        BookDetail.objects.create(book=book, summary=summary, page_count=page_count)
        return CreateBook(book=book)
```

* Мутации тоже используют **резолвер (`mutate`)**, который получает `info.context.user`.

---

### 7.3 Ограничение доступа на уровне полей через резолверы

Можно скрывать отдельные поля от неавторизованных пользователей:

```python
class BookType(DjangoObjectType):
    class Meta:
        model = Book
        fields = ("id", "title", "author", "detail")

    def resolve_detail(self, info):
        user = info.context.user
        if not user.is_authenticated:
            return None  # или raise Exception
        return self.detail
```

* `resolve_detail` — резолвер поля `detail`.
* Позволяет управлять доступом **на уровне отдельного поля**, а не всей модели.

---

### 7.4 Защита всего GraphQL endpoint

```python
from django.contrib.auth.decorators import login_required
from graphene_django.views import GraphQLView

urlpatterns += [
    path("graphql/", login_required(GraphQLView.as_view(graphiql=True))),
]
```

* Можно защитить весь endpoint через Django-декоратор.
* Более гибкий вариант — проверка внутри резолверов и мутаций (как выше).
