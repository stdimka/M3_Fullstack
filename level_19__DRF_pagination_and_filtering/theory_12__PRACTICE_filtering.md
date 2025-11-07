### 1. Установка и подключение `django-filter`

```bash
pip install django-filter
```

В `settings.py`:

```python
INSTALLED_APPS = [
    ...,
    "django_filters",
]

REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
}
```

---

### 2. Простая фильтрация по полям модели

В `myapp/views.py`:

```python
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # Фильтрация по конкретным полям
    filterset_fields = ["year_published", "author"]

    # Поиск по названию книги и имени автора
    search_fields = ["title", "author__name"]

    # Сортировка по году и названию
    ordering_fields = ["year_published", "title"]
    ordering = ["year_published"]
```

Теперь можно делать запросы типа:

```
http://127.0.0.1:8000/api/books/?year_published=1833
http://127.0.0.1:8000/api/books/?author=1
http://127.0.0.1:8000/api/books/?search=Лев+Толстой
http://127.0.0.1:8000/api/books/?ordering=-title
```

---

### 3. Кастомный FilterSet для сложных фильтров

Создаём `myapp/filters.py`

```python
import django_filters
from .models import Book

class BookFilter(django_filters.FilterSet):
    min_year = django_filters.NumberFilter(field_name="year_published", lookup_expr="gte")
    max_year = django_filters.NumberFilter(field_name="year_published", lookup_expr="lte")
    author_name = django_filters.CharFilter(field_name="author__name", lookup_expr="icontains")

    class Meta:
        model = Book
        fields = ["min_year", "max_year", "author_name"]
```

Подключаем к ViewSet:

```python
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from .filters import BookFilter

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = BookFilter
    search_fields = ["title", "author__name"]
    ordering_fields = ["year_published", "title"]
```

Примеры запросов:

```
http://127.0.0.1:8000/api/books/?min_year=1900&max_year=2000
http://127.0.0.1:8000/api/books/?author_name=Александр+Пушкин
http://127.0.0.1:8000/api/books/?search=Война+и+мир
http://127.0.0.1:8000/api/books/?ordering=-year_published
```

---

### 4. Фильтрация по множеству значений

Если нужно фильтровать книги сразу по нескольким годам:

```python
class BookFilter(django_filters.FilterSet):
    years = django_filters.BaseInFilter(field_name="year_published", lookup_expr="in")

    class Meta:
        model = Book
        fields = ["years"]
```

Запрос:

```
http://127.0.0.1:8000/api/books/?years=1831,1833,1869
```

