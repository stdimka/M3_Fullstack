## Подготовка к практической работе с проектом

### Создание (перенос) проекта

1. Создаём папку проекта
1. Копируем файлы из [example_from_lecture](./example_from_lecture) 
1. Переименовываем `db.sqlite3--` в `db.sqlite3`
1. Создаём виртуальное окружение `pyton3 -m venv .venv`
1. Активируем его `source .venv/bin/activate`
1. Устанавливаем пакеты `pip install -r requirements.txt`

### БД 

1. Заполненные модели авторов, книг, детализации и жангов
1. Зарегистрирован суперадминистратор `root` с паролем `123`


### Данные DRF уже имеются:

`myapp/serializers.py`

```python
from rest_framework import serializers
from .models import Author, Book


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ["id", "name"]


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ["id", "title", "year_published", "author"]
```

`myapp/api_urls.py`

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'books', views.BookViewSet)
router.register(r'authors', views.AuthorViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
```

`myapp/views.py`

```python
from rest_framework import viewsets
from .models import Book, Author
from .serializers import BookSerializer, AuthorSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
```
