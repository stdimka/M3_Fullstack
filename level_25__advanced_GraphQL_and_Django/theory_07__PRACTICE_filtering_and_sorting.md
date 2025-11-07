## 1. Что даёт Graphene в плане фильтрации и сортировки?

**Graphene** позволяет добавлять фильтрацию и сортировку прямо в GraphQL-запрос,  
чтобы клиент мог сам решать, **какие данные получать и в каком порядке**.  
Но **возможности зависят от того, используем ли мы Relay**.

---

### Вариант 1 — без Relay (стандартный Graphene)

Фильтрация и сортировка задаются **вручную**, через аргументы запроса.  
Graphene просто передаёт аргументы в резолвер, а мы применяем их в ORM-запросе.

```python
class Query(graphene.ObjectType):
    all_books = graphene.List(
        BookType,
        author_name=graphene.String(),
        order_by=graphene.List(graphene.String)
    )

    def resolve_all_books(root, info, author_name=None, order_by=None):
        qs = Book.objects.all()
        if author_name:
            qs = qs.filter(author__name__icontains=author_name)
        if order_by:
            qs = qs.order_by(*order_by)
        return qs
```

**Пример запроса:**

```graphql
query {
  allBooks(authorName: "Толстой", orderBy: ["-year_published"]) {
    title
    yearPublished
  }
}
```

✅ **Плюсы:**

* не требует дополнительных пакетов;
* полностью под вашим контролем (всё делается в Python-коде);
* можно использовать любые аргументы и сложную логику.

⚠️ **Минусы:**

* нельзя использовать удобные стандартные фильтры вроде `title_Icontains`, `year_Gt` и т.п.;
* приходится вручную описывать аргументы и применять фильтры в каждом резолвере.

---

### Вариант 2 — с Relay (`DjangoFilterConnectionField`)

Relay — это надстройка над Graphene, которая добавляет:

* **автоматическую фильтрацию** через `django-filter`,
* **пагинацию и структуру данных** (`edges`, `node`),
* **единый стандарт аргументов**, например:

  ```graphql
  allBooks(title_Icontains: "анна") {
    edges {
      node {
        title
        author {
          name
        }
      }
    }
  }
  ```

Пример настройки:

```python
from graphene_django.filter import DjangoFilterConnectionField
from graphene import relay

class BookType(DjangoObjectType):
    class Meta:
        model = Book
        interfaces = (relay.Node,)
        filter_fields = ['title', 'author__name']

class Query(graphene.ObjectType):
    all_books = DjangoFilterConnectionField(BookType)
```

✅ **Плюсы:**

* автоматическая фильтрация по всем полям, заданным в `filter_fields`;
* поддержка пагинации и стандартизированных аргументов;
* не нужно вручную описывать логику фильтрации и сортировки.

⚠️ **Минусы:**

* требует установки пакета `pip install django-filter` и его добавления в `INSTALLED_APPS`;
* меняет структуру схемы (появляются `edges` и `node`);
* сложнее запросы (особенно если API не ориентировано на Relay).

---

## 2. Альтернатива — жёстко заданные (hardcoded) резолверы

Иногда нужно ограничить пользователя или упростить логику —  
тогда создаются отдельные поля в `Query`, например:

```python
class Query(graphene.ObjectType):
    recent_books = graphene.List(BookType)
    russian_classics = graphene.List(BookType)

    def resolve_recent_books(root, info):
        return Book.objects.filter(year_published__gte=2000).order_by('-year_published')

    def resolve_russian_classics(root, info):
        return Book.objects.filter(author__country="Russia", year_published__lt=1920)
```

Такой подход:

* проще,
* безопаснее,
* но не гибкий (новый фильтр → нужно менять код и схему).

---

## 3. Пример фильтрации и сортировки вместе


`myapp/schema/filters.py`


```python
import django_filters
from ..models import Book

class BookFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    author_name = django_filters.CharFilter(field_name='author__name', lookup_expr='icontains')
    genre_name = django_filters.CharFilter(field_name='genres__name', lookup_expr='icontains')
    year_published = django_filters.NumberFilter()

    class Meta:
        model = Book
        fields = ['title', 'author_name', 'genre_name', 'year_published']
```

Этот фильтр необходимо будет подключить к типу `BookType`:

`myapp/schema/queries.py`

```python
class Query(graphene.ObjectType):
    ...
    all_books = graphene.List(
        BookType,
        title=graphene.String(),
        author_name=graphene.String(),
        genre_name=graphene.String(),
        year_published=graphene.Int(),
        year_published_range=graphene.List(graphene.Int),
        order_by=graphene.List(graphene.String)
    )
    ...
    
    @staticmethod
    def resolve_all_books(root, info, title=None, author_name=None,
                          genre_name=None, year_published=None, 
                          year_published_range=None, order_by=None):
        qs = Book.objects.all()

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
        return qs.distinct()  # Убираем дубликаты, если есть ManyToMany (genres)
```

Добавляем в резолвер 
* параметры фильтрации и сортировки
* и изменение QuerySet, в зависимости 
  * от наличия в запросе этих параметров
  * и значения этих параметров

---

## 4. Примеры запросов в GraphQL

### ✅ 1. Фильтр по подстроке в названии

```graphql
query {
  allBooks(title: "мир") {
    title
    author {
      name
    }
  }
}

```

---

### ✅ 2. Фильтр по автору

```graphql
query {
  allBooks(authorName: "Лев") {
    title
    yearPublished
  }
}
```

---

### ✅ 3. Фильтр по жанру и году

```graphql
query {
  allBooks(yearPublished: 1605, genreName: "Роман") {
    title
    genres {
      name
    }
  }
}
```

---

### ✅ 4. Сортировка по году издания (по убыванию)

```graphql
query {
  allBooks(orderBy: ["-year_published"]) {
    title
    yearPublished
  }
}
```

---

### ✅ 5. Одновременная фильтрация и сортировка

```graphql
query {
  allBooks(authorName: "Пушкин", orderBy: ["-year_published"]) {
    title
    yearPublished
  }
}
```


### ✅ 6. Диапазон + фильтрация по автору

```graphql
query {
  allBooks(authorName: "Пушкин", yearPublishedRange: [1831, 1833], orderBy: ["-year_published"]) {
    title
    yearPublished
  }
}

```
