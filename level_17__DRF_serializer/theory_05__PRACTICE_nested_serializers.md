####

### 2.1. Базовый сериализатор без вложенности

Просто меняем сериализаторы и всё должно работать по ссылке: [http://127.0.0.1:8000/api/books/](http://127.0.0.1:8000/api/books/)

`myapp/serializers.py`

```python
from rest_framework import serializers
from .models import Author, Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'
```

`myapp/views.py`

```python
from rest_framework import viewsets, generics
from .models import Book, Author
from .serializers import BookSerializer, AuthorSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
```

`myapp/api_urls.py`

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, AuthorViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'authors', AuthorViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
```

Результат по ссылке: [http://127.0.0.1:8000/api/books/](http://127.0.0.1:8000/api/books/)

([http://127.0.0.1:8000/api/books/1/](http://127.0.0.1:8000/api/books/1/)
```json
[
    {
        "id": 1,
        "title": "Война и мир",
        "year_published": 1869,
        "is_deleted": false,
        "author": 1
    },
    ...
]
```

Результат по ссылке: [http://127.0.0.1:8000/api/authors/](http://127.0.0.1:8000/api/authors/)

[http://127.0.0.1:8000/api/authors/1/](http://127.0.0.1:8000/api/authors/1/)
```json
[
    {
        "id": 1,
        "name": "Лев Толстой"
    },
    {
        "id": 2,
        "name": "Фёдор Достоевский"
    },
    ...
]
```

---

### 2.2. Вложенный сериализатор (только чтение)

Чтобы при выводе автора сразу показать список его книг, используем **вложенный сериализатор**,  
придётся выполнить некоторые изменения.

#### 2.2.1. Меняем сериализаторы:

```python
class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "title", "year_published"]


class AuthorSerializer(serializers.ModelSerializer):
    # Вложенный сериализатор
    books = BookSerializer(many=True, read_only=True)

    class Meta:
        model = Author
        fields = ["id", "name", "books"]
```

* `read_only=True` означает, что поле только для чтения.
* DRF не будет принимать данные для этого поля при создании или обновлении (POST/PUT/PATCH).

То есть, через этот сериализатор нельзя создать или добавить книги вместе с автором.
    * создать/обновить автора можно (т.к. поле name по умолчанию read/write).
    * а вот книги добавить уже нельзя

#### 2.2.2. Добавляем новое вью:

```python
from .serializers import AuthorSerializer
from rest_framework.decorators import action
from rest_framework.response import Response

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer

    # кастомный action для получения книг автора
    @action(detail=True, methods=["get"])
    def books(self, request, pk=None):
        author = self.get_object()
        books = author.books.all()  # related_name="books" в модели Book (ForeignKey)
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)
```

#### Зачем нужен декоратор `@action` ?

Используется для создания кастомных действий (actions) в ViewSet, которые не входят  
в стандартный набор CRUD (`list`, `retrieve`, `create`, `update`, `destroy`).

Здесь `@action`:

1. **Создаёт дополнительный endpoint для конкретного объекта** (`detail=True`):

   * `detail=True` означает, что этот action работает с **одним объектом**, а не со списком.
   * В результате DRF сгенерирует URL примерно такого вида: `/authors/<pk>/books/`, где `<pk>` — ID автора.

2. **Определяет HTTP-методы, которые поддерживаются** (`methods=["get"]`):

3. **Позволяет использовать ViewSet вместо отдельного APIView**:

   * Без `@action` пришлось бы писать отдельный метод в APIView и настраивать URL вручную.
   * С `@action` DRF автоматически добавляет маршрут в роутер.

---

#### 2.2.3. Роутер остаётся без изменений:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet, AuthorViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'authors', AuthorViewSet)


urlpatterns = [
    path('', include(router.urls)),
]

```


Теперь при запросе авторов [http://127.0.0.1:8000/api/authors/](http://127.0.0.1:8000/api/authors/):

```json
[
    {
        "id": 1,
        "name": "Лев Толстой",
        "books": [
            {
                "id": 1,
                "title": "Война и мир",
                "year_published": 1869
            },
            {
                "id": 20,
                "title": "Война и мир +++",
                "year_published": 1869
            }
        ]
    },
    {
        "id": 2,
        "name": "Фёдор Достоевский",
        "books": [
  ...
]
```

При запросе автора:  [http://127.0.0.1:8000/api/authors/1/](http://127.0.0.1:8000/api/authors/1/)

```json
{
    "id": 1,
    "name": "Лев Толстой",
    "books": [
        {
            "id": 1,
            "title": "Война и мир",
            "year_published": 1869
        },
        {
            "id": 21,
            "title": "Война и мир +++",
            "year_published": 1869
        }
    ]
}
```

При запросе книг автора:  [http://127.0.0.1:8000/api/authors/1/books/](http://127.0.0.1:8000/api/authors/1/books/)


```json
[
    {
        "id": 1,
        "title": "Война и мир",
        "year_published": 1869,
        "is_deleted": false,
        "author": 1
    },
    {
        "id": 20,
        "title": "Война и мир +++",
        "year_published": 1869,
        "is_deleted": false,
        "author": 1
    }
]
```
---

### 2.3. Вложенный сериализатор (обратная ситуация)

Если мы хотим при выводе книги показывать информацию об авторе:

```python
class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "name"]


class BookSerializer(serializers.ModelSerializer):
    # Вложенный сериализатор
    author = AuthorSerializer(read_only=True)

    class Meta:
        model = Book
        fields = ["id", "title", "year_published", "author"]
```

Больше ничего менять не нужно - меняем только сериалайзеры.

Но результат будут совсем другим - теперь автор показан как вложенный json внутри книги:
[http://127.0.0.1:8000/api/books/](http://127.0.0.1:8000/api/books/)
```json
[
    {
        "id": 1,
        "title": "Война и мир",
        "year_published": 1869,
        "author": {
            "id": 1,
            "name": "Лев Толстой"
        }
    },
    {
        "id": 20,
        "title": "Война и мир +++",
        "year_published": 1869,
        "author": {
            "id": 1,
            "name": "Лев Толстой"
        }
    }
]
```

---

#### Когда нужно `read_only=False`?

Если мы хотим **создавать книги вместе с автором через один сериализатор**, придётся переопределять `create()`:

```python
class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = Book
        fields = ["id", "title", "year_published", "author"]

    def create(self, validated_data):
        author_data = validated_data.pop("author")
        author, _ = Author.objects.get_or_create(**author_data)
        book = Book.objects.create(author=author, **validated_data)
        return book
```

Тогда можно создать книгу так:
[http://127.0.0.1:8000/api/books/](http://127.0.0.1:8000/api/books/)

```json
{
  "title": "Белый Клык",
  "year_published": 1906,
  "author": {
    "name": "Джек Лондон"
  }
}
```

