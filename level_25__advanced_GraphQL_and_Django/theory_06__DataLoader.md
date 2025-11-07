Задача прежняя:

```qraphql
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

Теперь попробуем решить её через DataLoader.

# 3. Оптимизация через DataLoader

**Когда использовать:**

* Если сложный GraphQL с большим количеством связанных объектов, иногда **select_related/prefetch_related** не хватает, особенно при **динамических резолверах**.
* DataLoader решает проблему **отложенных N+1 вызовов внутри GraphQL резолверов**.

---

### 1. Установка DataLoader (проверка установки)

Библиотека `DataLoader` входит в экосистему Graphene и использует пакет [`promise`](https://pypi.org/project/promise/).

Поэтому, если мы уже установили `graphene-django`, то `promise` обычно уже идёт в зависимостях.

Проверить можно так:

```bash
pip show promise
```
Если покажет версию (например, `2.3`), значит всё готово.

Если нет, то можно установить отдельно:

```bash
pip install promise
```
---
### 2. Интеграция DataLoader в Graphene-Django

Чтобы DataLoader эффективно группировал запросы, нужно передать его через контекст GraphQL.
Это контекст создаётся при инициализации GraphQL view (обычно `GraphQLView`).

---

### Структура проекта

Создаём новый файл `dataloaders.py` в нашем проекте

```
myapp/
│
├── schema/
│   ├── __init__.py
│   ├── types.py
│   ├── queries.py
│   ├── dataloaders.py      ← добавить 
│   ├── views.py            ← добавить 
│   ├── urls.py             ← добавить 
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

#### Создаём DataLoader классы

`schema/dataloaders.py`:

```python
from promise import Promise
from promise.dataloader import DataLoader
from ..models import Author, BookDetail, Genre

class AuthorLoader(DataLoader):
    def batch_load_fn(self, keys):
        authors = Author.objects.filter(id__in=keys)
        author_map = {a.id: a for a in authors}
        return Promise.resolve([author_map.get(k) for k in keys])

class DetailLoader(DataLoader):
    def batch_load_fn(self, keys):
        details = BookDetail.objects.filter(book_id__in=keys)
        detail_map = {d.book_id: d for d in details}
        return Promise.resolve([detail_map.get(k) for k in keys])

class GenreLoader(DataLoader):
    def batch_load_fn(self, keys):
        genres = Genre.objects.filter(books__id__in=keys).distinct()
        genre_map = {}
        for genre in genres:
            for book in genre.books.all():
                genre_map.setdefault(book.id, []).append(genre)
        return Promise.resolve([genre_map.get(k, []) for k in keys])
```

Каждый DataLoader объединяет запросы:

* `AuthorLoader` загрузит всех авторов одним запросом;
* `DetailLoader` загрузит все детали книг одним запросом;
* `GenreLoader` — все жанры одним запросом, сгруппировав по книгам.


---

#### Добавляем DataLoader вызовы в `schema/types.py`

```python
class BookType(DjangoObjectType):
    class Meta:
        model = Book
        fields = '__all__'

    # Здесь используем DataLoader
    def resolve_author(self, info):
        return info.context.author_loader.load(self.author_id).get()

    def resolve_detail(self, info):
        return info.context.detail_loader.load(self.id).get()

    def resolve_genres(self, info):
        return info.context.genre_loader.load(self.id).get()
```

---

#### Создаём `schema/urls.py`

```python
from django.urls import path
from .views import GraphQLViewWithDataLoader
from .schema import schema

urlpatterns = [
    path(
        "graphql/",
        GraphQLViewWithDataLoader.as_view(
            graphiql=True,
            schema=schema,
        ),
    ),
]

```

---

#### Создаём `schema/views.py`

```python
from graphene_django.views import GraphQLView
from .dataloaders import AuthorLoader, DetailLoader, GenreLoader

class GraphQLViewWithDataLoader(GraphQLView):
    def get_context(self, request):
        context = super().get_context(request)
        context.author_loader = AuthorLoader()
        context.detail_loader = DetailLoader()
        context.genre_loader = GenreLoader()
        return context
```

#### Изменяем `main/urls.py`

Убираем

```python
    # path("graphql/", GraphQLView.as_view(graphiql = True)),
```

И вместо этого добавляем

```python
    path("", include("myapp.schema.urls")),  # ← подключаем GraphQL с DataLoader
```

### Результат

Число запросов только увеличилось.

Причина не асинхронная (точнее, не awaitable) архитектура Django ORM.

Чтобы получить выигрыш, необходимо установить `aiodataloader`