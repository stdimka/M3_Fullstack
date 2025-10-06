## 1 Создание кастомного класса пагинации в конкретном приложении

```python
# myapp/pagination.py
from rest_framework.pagination import PageNumberPagination

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10                     # размер страницы по умолчанию
    page_size_query_param = 'page_size'  # имя query-параметра для изменения размера страницы
    max_page_size = 50                 # максимальный размер страницы
```

* **`page_size`** — сколько объектов показывать по умолчанию.
* **`page_size_query_param`** — позволяет клиенту менять размер страницы через `?page_size=...`.
* **`max_page_size`** — предотвращает запрос слишком большого количества объектов.

---

## 2 Используем пагинацию в вью

Для этого надо явно указать класс пагинации `pagination_class`

```python
# myapp/views.py
from rest_framework.generics import ListAPIView
from .models import Book
from .serializers import BookSerializer
from .pagination import CustomPageNumberPagination

class BookListView(ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    pagination_class = CustomPageNumberPagination
```

Теперь клиент может сделать запрос:

```http
GET /books/?page=2&page_size=20
```

* Если `page_size` больше 50, DRF вернёт максимум 50 объектов.
* Если `page_size` не указан, вернётся 10 объектов (по умолчанию).

---

## 3 Глобальная настройка пагинации

При желании, класс приложения можно сделать классом по умолчанию для всего проекта:

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'myapp.pagination.CustomPageNumberPagination',
    'PAGE_SIZE': 10,
}
```

Что избавляет от необходимости явно указывать `pagination_class` в каждой вью.

