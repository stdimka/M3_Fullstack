## Ввод данных сложной вложенной структуры

Теперь мы достаточно подготовлены, чтобы попробовать ввести сразу несколько книг  
одного автора, со всеми их связями (OneToOne, OneToMany и ManyToMane):

```json
{
  "author": {
    "name": "Дж. Р. Р. Толкин",
    "books": [
      {
        "title": "Хоббит",
        "year_published": 1937,
        "detail": {
          "summary": "Фэнтезийное приключение.",
          "page_count": 310
        },
        "genres": ["Фэнтези", "Приключение"]
      },
      {
        "title": "Властелин колец",
        "year_published": 1954,
        "detail": {
          "summary": "Эпическое фэнтези.",
          "page_count": 1178
        },
        "genres": ["Фэнтези", "Эпическое"]
      }
    ]
  }
}
```

Здесь будет особенно полезно сравнить возможности DRF и обычного Django.

### 1. Использование Django

#### Обработка csrf токена

В Django есть защита от CSRF (Cross-Site Request Forgery),   
которая предотвращает выполнение POST/PUT/DELETE-запросов на ваш сайт со сторонних сайтов.  

По умолчанию Django требует, чтобы каждый такой запрос имел CSRF-токен, который обычно  
вставляется в формы HTML или передаётся в заголовке X-CSRFToken при AJAX-запросах.

В нашем коде AuthorBooksCreateView мы получаем POST-запрос с JSON в теле запроса,  
а не через форму HTML.

Следовательно, мы не передаём CSRF-токен.

В этом случае Django будет блокировать запросы и возвращать 403 Forbidden,  
потому что не видит CSRF-токена.

Вариантов выхода, как минимум, два:
 - либо отключить проверку CSRF (небезопасно, но допустимо в учебном примере), 
 - либо передавать с POST-запросом заголовок `X-CSRFToken`, созданные с помощью JavaScript.

Отключим с помощью декоратора `@method_decorator(csrf_exempt, name='dispatch')`.

Здесь, благодаря `name='dispatch` отключение происходит для всех методов класса.  
(либо `name='post'`, что отключит проверку ТОЛЬКО для `post`)

#### Создание вью для обработки запроса

```python
import json
from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import Author, Book, BookDetail, Genre


@method_decorator(csrf_exempt, name='dispatch')  
class AuthorBooksCreateView(View):

    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        author_data = data.get("author")
        if not author_data:
            return JsonResponse({"error": "Missing author"}, status=400)

        # автор
        author, _ = Author.objects.get_or_create(name=author_data["name"])

        books_response = []
        for book_data in author_data.get("books", []):
            detail_data = book_data.pop("detail", {})
            genres_data = book_data.pop("genres", [])

            # книга
            book, created = Book.objects.get_or_create(
                author=author,
                title=book_data["title"],
                defaults={"year_published": book_data["year_published"]}
            )

            if not created:  # обновим год
                book.year_published = book_data["year_published"]
                book.save()

            # detail (OneToOne)
            if detail_data:
                BookDetail.objects.update_or_create(
                    book=book,
                    defaults=detail_data
                )

            # жанры
            for genre_name in genres_data:
                genre, _ = Genre.objects.get_or_create(name=genre_name)
                book.genres.add(genre)

            books_response.append({
                "title": book.title,
                "year_published": book.year_published,
                "genres": [g.name for g in book.genres.all()],
                "detail": {
                    "summary": book.detail.summary if hasattr(book, "detail") else None,
                    "page_count": book.detail.page_count if hasattr(book, "detail") else None
                }
            })

        return JsonResponse({
            "author": author.name,
            "books": books_response
        }, status=201)
```

#### Добавление маршрута в `myapp/urls.py`

```python
from django.urls import path
from .views import create_author_books

urlpatterns = [
    path("add-author-books/", views.AuthorBooksCreateView.as_view(), name="add-author-books"),
]
```

### 2. Универсальная проверка для двух вариантов

```bash
#url="http://127.0.0.1:8000/myapp/add-author-books/"
#url="http://127.0.0.1:8000/api/add-author-books/"

curl -X POST $url \
  -H "Content-Type: application/json" \
  -d '{
    "author": {
      "name": "Дж. Р. Р. Толкин",
      "books": [
        {
          "title": "Хоббит",
          "year_published": 1937,
          "detail": {
            "summary": "Фэнтезийное приключение.",
            "page_count": 310
          },
          "genres": ["Фэнтези", "Приключения"]
        },
        {
          "title": "Властелин колец",
          "year_published": 1954,
          "detail": {
            "summary": "Эпическое высокое фэнтези.",
            "page_count": 1178
          },
          "genres": ["Фэнтези", "Эпос"]
        }
      ]
    }
  }'
```

### 3. Использование DRF

#### 3.1. Сериализаторы

```python
from rest_framework import serializers
from .models import Author, Book, BookDetail, Genre


class BookDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookDetail
        fields = ['summary', 'page_count']

        
class BookSerializer(serializers.ModelSerializer):
    detail = BookDetailSerializer()
    genres = serializers.ListField(child=serializers.CharField())

    class Meta:
        model = Book
        fields = ['title', 'year_published', 'detail', 'genres']

        
class AuthorBooksCreateSerializer(serializers.ModelSerializer):
    books = BookSerializer(many=True)

    class Meta:
        model = Author
        fields = ['name', 'books']

    def create(self, validated_data):
        books_data = validated_data.pop('books', [])
        author, _ = Author.objects.get_or_create(name=validated_data['name'])

        for book_data in books_data:
            detail_data = book_data.pop('detail')
            genres_data = book_data.pop('genres')

            book, created = Book.objects.get_or_create(
                author=author,
                title=book_data['title'],
                defaults={
                    'year_published': book_data['year_published'],
                }
            )

            # если книга существовала, можно обновить год издания
            if not created:
                book.year_published = book_data['year_published']
                book.save()

            # detail (OneToOne)
            BookDetail.objects.update_or_create(
                book=book,
                defaults=detail_data
            )

            # жанры
            for genre_name in genres_data:
                genre, _ = Genre.objects.get_or_create(name=genre_name)
                book.genres.add(genre)

        return author
```

#### 3.2. Вью

Наш сериализотор работает только "на приём".  

Поэтому есть POST-метод и нет GET-метода.

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Author
from .serializers import AuthorBooksCreateSerializer


class AuthorBooksCreateView(APIView):
    def post(self, request):
        serializer = AuthorBooksCreateSerializer(data=request.data.get('author'))
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Автор и книги успешно добавлены"},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

#### 3.3. `api_urls.py`

```python
from django.urls import path, include
from .views import AuthorBooksCreateView


urlpatterns = [
    path('add-author-books/', AuthorBooksCreateView.as_view()),
]
```