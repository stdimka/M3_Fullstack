####

### 2.1. Базовый сериализатор без вложенности

Просто меняем сериализаторы и всё должно работать по ссылке: [http://127.0.0.1:8000/api/books/](http://127.0.0.1:8000/api/books/)

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

---

### 2.2. Вложенный сериализатор (только чтение)

Чтобы при выводе автора сразу показать список его книг, используем **вложенный сериализатор**,  
придётся выполнить несколька изменений

1. Меняем сериализаторы:

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

2. Добавляем новое вью:

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

3. Добавляем роутер:

```python

```


Теперь при запросе авторов [127.0.0.1:8000/api/authors/](127.0.0.1:8000/api/authors/):

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

При запросе автора:  [127.0.0.1:8000/api/authors/1/](127.0.0.1:8000/api/authors/1/)

```json
{
    "id": 1,
    "name": "Лев Толстой"
}
```

При запросе книг автора:  [127.0.0.1:8000/api/authors/1/books/](127.0.0.1:8000/api/authors/1/books/)


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

Больше ничего менять не нужно (уже только что изменили).

Но результат будут совсем другим - теперь автор показан как вложенный json внутри книги:

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

### 🔹 Когда нужно `read_only=False`

Если мы хотим **создавать книги вместе с автором через один сериализатор**, придётся переопределять `create()`:

```python
class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()

    class Meta:
        model = Book
        fields = ["id", "title", "year_published", "author"]

    def create(self, validated_data):
        author_data = validated_data.pop("author")
        author, created = Author.objects.get_or_create(**author_data)
        book = Book.objects.create(author=author, **validated_data)
        return book
```

Тогда можно создать книгу так:

```json
{
  "title": "Идиот",
  "year_published": 1869,
  "author": {
    "name": "Фёдор Достоевский"
  }
}
```

