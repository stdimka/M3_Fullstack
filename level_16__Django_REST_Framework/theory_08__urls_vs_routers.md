# Что такое роутеры в DRF

В Django мы обычно явно прописываем URL-шаблоны в `urls.py`:

```python
from django.urls import path
from .views import BookListView, BookDetailView

urlpatterns = [
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
]
```

В **Django REST Framework (DRF)** есть удобный инструмент — **роутеры** (`routers`).  
Они автоматически создают стандартные маршруты (`list`, `retrieve`, `create`, `update`, `delete`) для `ViewSet` или `ModelViewSet`.

Это избавляет от рутины и делает API более единообразным.

---

# Типы роутеров в DRF

В DRF есть два встроенных роутера (и можно писать свои):

### 1. `SimpleRouter`

* Генерирует **только API-эндпоинты** без "root" (списка всех эндпоинтов).
* Самый лёгкий и часто используемый вариант.

Пример:

```python
from rest_framework.routers import SimpleRouter
from .views import BookViewSet

router = SimpleRouter()
router.register(r'books', BookViewSet, basename='book')

urlpatterns = router.urls
```

Создаст такие маршруты:

```
GET     /books/         -> list
POST    /books/         -> create
GET     /books/{id}/    -> retrieve
PUT     /books/{id}/    -> update
PATCH   /books/{id}/    -> partial_update
DELETE  /books/{id}/    -> destroy
```

---

### 2. `DefaultRouter`

* То же, что `SimpleRouter`, **но дополнительно создаёт корневой маршрут** (`/`), где показаны все зарегистрированные ViewSet'ы.
* Удобно для разработки и документации.

```python
from rest_framework.routers import DefaultRouter
from .views import BookViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')

urlpatterns = router.urls
```

Теперь доступно:

```
/          -> список всех ресурсов (root API)
/books/    -> list, create
/books/1/  -> retrieve, update, delete
```

---

# Способы объявление маршрутов

## 1. Ручное объявление маршрутов (как в Django)

В DRF можно вообще **не использовать роутеры**, а прописывать `urls` вручную, как в чистом Django.

Пример:

```python
from django.urls import path
from .views import BookListView, BookDetailView

urlpatterns = [
    path('books/', BookListView.as_view(), name='book-list'),
    path('books/<int:pk>/', BookDetailView.as_view(), name='book-detail'),
]
```

А `views.py` может выглядеть так:

```python
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from .models import Book
from .serializers import BookSerializer

class BookListView(ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class BookDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
```

**Здесь мы полностью контролируем маршруты и в точности задаём, какой `View` отвечает за какой `url`.**

---

## 2. Использование ViewSet без роутера

`ViewSet` — это класс, который **собирает CRUD-логику в одном месте**.
Но сам по себе он ещё **не привязан к URL**, пока вы не подключите его через `as_view()`.

Пример:

```python
from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from .models import Book
from .serializers import BookSerializer

class BookViewSet(ViewSet):
    def list(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        book = Book.objects.get(pk=pk)
        serializer = BookSerializer(book)
        return Response(serializer.data)

    def create(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
```

Чтобы связать `ViewSet` с маршрутами **вручную**, используем `.as_view()`:

```python
from django.urls import path
from .views import BookViewSet

book_list = BookViewSet.as_view({
    'get': 'list',
    'post': 'create',
})
book_detail = BookViewSet.as_view({
    'get': 'retrieve',
})

urlpatterns = [
    path('books/', book_list, name='book-list'),
    path('books/<int:pk>/', book_detail, name='book-detail'),
]
```

**Здесь мы сами сопоставляем методы (`get`, `post`) с действиями (`list`, `create`, `retrieve`).  
То есть используем ViewSet, но **без автоматической генерации маршрутов**.**

---

## 3. Использование ViewSet с роутером

Теперь — самое удобное: `ViewSet` + `Router`.

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet, basename='book')

urlpatterns = [
    path('', include(router.urls)),
]
```

**Здесь DRF сам создаёт все стандартные маршруты: `list`, `retrieve`, `create`, `update`, `destroy`.**

---

## Сравнение подходов

| Подход                                 | Когда использовать                                                          | Плюсы                                                                | Минусы                                 |
| -------------------------------------- | --------------------------------------------------------------------------- | -------------------------------------------------------------------- | -------------------------------------- |
| **Ручное объявление (GenericAPIView)** | Когда API нестандартное (например, нет `delete` или сложные кастомные пути) | Полный контроль                                                      | Много кода                             |
| **ViewSet + as\_view() (без Router)**  | Когда нужна часть CRUD, но хотите оставить гибкость                         | Баланс: ViewSet = вся логика в одном классе, urls = настраиваем сами | Нужно вручную связывать методы         |
| **ViewSet + Router**                   | Когда нужен полный CRUD (типовой REST API)                                  | Минимум кода, единообразие                                           | Меньше гибкости — за вас решает Router |

---

### Простой итоговый пример

**Ручное (как в Django):**

```python
urlpatterns = [
    path('books/', BookListView.as_view()),
    path('books/<int:pk>/', BookDetailView.as_view()),
]
```

**ViewSet без Router:**

```python
book_list = BookViewSet.as_view({'get': 'list', 'post': 'create'})
book_detail = BookViewSet.as_view({'get': 'retrieve'})
urlpatterns = [
    path('books/', book_list), 
    path('books/<int:pk>/', book_detail),
]
```

**ViewSet с Router:**

```python
router = DefaultRouter()
router.register('books', BookViewSet)
urlpatterns = [
    path('', include(router.urls)),
]
```

