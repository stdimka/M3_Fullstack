# Django views VS DRF views

## 1. Django views (краткое напоминание)

### 1.1. Вью на основе функций (FBV)

  ```python
  def book_list(request):
      books = Book.objects.all()
      return render(request, "books/list.html", {"books": books})
  ```

### 1.2. Вью на основе классов (CBV)

Наследуются от `django.views.generic` (`ListView`, `DetailView` и т.д.):

  ```python
  class BookListView(ListView):
      model = Book
      template_name = "books/list.html"
  ```

В DRF структура похожая: можно писать **функции**, **классы** или использовать **generic**.

---

## 2. Типы вью в DRF

### 2.1. Вью на основе функций (FBV)

Используются редко, но возможны через декоратор `@api_view`.
Это самый простой способ быстро написать API.

```python
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Book
from .serializers import BookSerializer

@api_view(['GET'])
def book_list(request):
    books = Book.objects.all()
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)
```

---

### 2.2. APIView (базовый класс CBV)

Аналог `View` в Django, но с поддержкой DRF: сериализация, парсеры, аутентификация, разрешения и т.п.

```python
from rest_framework.views import APIView

class BookListAPIView(APIView):
    def get(self, request):
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)
```

**Это гибко, но больше писанины.**

---

### 2.3. GenericAPIView

Основа для дженериков. Дает:

* `queryset`, `serializer_class` как атрибуты,
* методы `get_queryset()`, `get_serializer_class()` для кастомизации.

Чаще всего **смешивается с "mixins"**, чтобы добавить CRUD-операции.

---

### 2.4. Mixins + GenericAPIView

Mixins реализуют куски CRUD (`ListModelMixin`, `CreateModelMixin`, и т.д.).
Обычно комбинируются:

```python
from rest_framework.generics import GenericAPIView
from rest_framework import mixins

class BookListCreateView(mixins.ListModelMixin,
                         mixins.CreateModelMixin,
                         GenericAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
```

**Даёт контроль + сокращает код, но пока ещё выглядит громоздко.**

---

### 2.5. Готовые generics вью

Наиболее популярный вариант, готовые классы под CRUD:

* `ListAPIView` — список
* `CreateAPIView` — создание
* `RetrieveAPIView` — получение
* `UpdateAPIView` — обновление
* `DestroyAPIView` — удаление
* Комбинированные: `ListCreateAPIView`, `RetrieveUpdateDestroyAPIView`

Пример:

```python
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView

class BookListCreateAPIView(ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class BookDetailAPIView(RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
```

**Это аналог Django generics (`ListView`, `DetailView`) и чаще всего применяется в реальных проектах.**

---

### 2.6. ViewSet / ModelViewSet

Специальный тип вью в DRF, который сразу группирует все CRUD-операции.
Работает в паре с `Router`.

```python
from rest_framework.viewsets import ModelViewSet

class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
```

**Подключается через роутер, и сразу доступны все действия (`list`, `retrieve`, `create`, `update`, `destroy`)**

---

## 3. Где размещать вью?

Точно так же, как в Django:

* В каждом приложении — в `views.py` (или, если много кода, делят на `views/` с отдельными файлами).
* Обычно:

  * `models.py` → только модели
  * `serializers.py` → сериализаторы
  * `views.py` → все вью (APIView, generics, viewsets)
  * `urls.py` → маршруты или роутер

---

## 4. Сравнение подходов

| Django View                           | DRF View                                                      | HTTP метод                        | URL                        | Что делает                                        |
|---------------------------------------| ------------------------------------------------------------- | --------------------------------- | -------------------------- | ------------------------------------------------- |
| `ListView`                            | `ListAPIView` / `GenericAPIView + ListModelMixin`             | GET                               | `/books/`                  | Возвращает список объектов                        |
| `CreateView`                          | `CreateAPIView` / `GenericAPIView + CreateModelMixin`         | POST                              | `/books/`                  | Создаёт объект                                    |
| `ListView + CreateView`               | `ListCreateAPIView` / `GenericAPIView + List + Create mixins` | GET / POST                        | `/books/`                  | Список + создание                                 |
| `DetailView`                          | `RetrieveAPIView` / `GenericAPIView + RetrieveModelMixin`     | GET                               | `/books/<id>/`             | Получение объекта по id                           |
| `UpdateView`                          | `UpdateAPIView` / `GenericAPIView + UpdateModelMixin`         | PUT / PATCH                       | `/books/<id>/`             | Полное / частичное обновление                     |
| `DeleteView`                          | `DestroyAPIView` / `GenericAPIView + DestroyModelMixin`       | DELETE                            | `/books/<id>/`             | Удаление объекта                                  |
| `DetailView + UpdateView + DeleteView` | `RetrieveUpdateDestroyAPIView`                                | GET / PUT / PATCH / DELETE        | `/books/<id>/`             | Получение + обновление + удаление                 |
| —                                     | `ModelViewSet`                                                | GET / POST / PUT / PATCH / DELETE | `/books/` и `/books/<id>/` | Все CRUD действия сразу, маршруты создаёт Router  |
| FBV (`def view`)                      | `@api_view`                                                   | GET / POST / PUT / PATCH / DELETE | любой путь                 | Можно явно указать, что делать для каждого метода |


