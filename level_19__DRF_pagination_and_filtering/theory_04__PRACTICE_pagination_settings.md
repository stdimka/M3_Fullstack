## 1 Создаём кастомные классы пагинации

Создаём файл `myapp/pagination.py`:

```python
from rest_framework.pagination import (PageNumberPagination, 
                                       LimitOffsetPagination, 
                                       CursorPagination)


# 1. PageNumberPagination (по номеру страницы)
class MyappPageNumberPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 10

# 2. LimitOffsetPagination (через limit и offset)
class MyappLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 3
    max_limit = 10
    limit_query_param = 'limit'
    offset_query_param = 'offset'

# 3. CursorPagination (курсором, сортировка по полю year_published)
class MyappCursorPagination(CursorPagination):
    page_size = 3
    ordering = 'id'  # сортировка по id
    cursor_query_param = 'cursor'

```

---

## 2 Подключаем пагинацию 

### 2.1. Во вью:

В `myapp/views.py`:

```python
from rest_framework import viewsets
from .models import Book, Author
from .serializers import BookSerializer, AuthorSerializer
from .pagination import (MyappPageNumberPagination,
                         MyappLimitOffsetPagination,
                         MyappCursorPagination)

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    # pagination_class = MyappPageNumberPagination   # Пагинация по умолчанию
    # pagination_class = MyappLimitOffsetPagination  # Для теста LimitOffset
    # pagination_class = MyappCursorPagination       # Для теста CursorPagination

class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    # pagination_class = MyappPageNumberPagination   # Пагинация по умолчанию
    # pagination_class = MyappLimitOffsetPagination  # Для теста LimitOffset
    # pagination_class = MyappCursorPagination       # Для теста CursorPagination

```

### 2.2. И глобально:

В `main/settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 3,
}
```

---

## 3 Примеры запросов

* Локальные настройки (во вью) имеют приоритет по сравнению с глобальной.
* Чтобы протестировать разные типы пагинации, достаточно раскомментировать нужный `pagination_class`.
* Если не раскомментировать ни одну, сработает глобальная настройка, указанная в `settings.py`. 

### PageNumberPagination

```http
127.0.0.1:8000/api/books/?page=2&page_size=3
```

* `page` — номер страницы
* `page_size` — сколько объектов на странице (до 50)

Обратите внимание: устанавливать параметр `page_size=10` в запросе можно только  
подключив локальную пагинацию непосредственно во вью.

```http request
127.0.0.1:8000/api/books/?page=2&page_size=10
```
Если оставить глобальную, то при любом `page_size=x` параметр будет определён  
в `'PAGE_SIZE': 3,`, указанный в  `settings.py`.


### LimitOffsetPagination

```http
127.0.0.1:8000/api/books/?limit=3&offset=3
```

* `limit` — сколько объектов вернуть
* `offset` — сколько пропустить

### CursorPagination

Ссылка указана для примера!!! (реальные значения курсора задаёт сам DRF)

```http
127.0.0.1:8000/api/books/?cursor=cD0yMDI1LTA5LTA5
```
* 
* `cursor` генерируется DRF автоматически
* Переход на следующую страницу через поле `next` в JSON-ответе
* Сортировка идёт по `year_published`

