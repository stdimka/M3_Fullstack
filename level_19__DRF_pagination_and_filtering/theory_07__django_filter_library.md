## Библиотека `django-filter`

Для расширенной фильтрации в DRF чаще всего применяют библиотеку **django-filter**.  
Она позволяет определять фильтры не только по простым полям модели, но и задавать собственные правила.

---

### 3.1. Установка и подключение

Установка через pip:

```bash
pip install django-filter
```

Добавляем в `settings.py`:

```python
INSTALLED_APPS = [
    ...
    "django_filters",
]
```

В DRF настраиваем глобально:

```python
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend"
    ]
}
```

---

### 3.2. Простая фильтрация с `filterset_fields`

Минимальный вариант использования — указать список разрешённых полей:

```python
class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filterset_fields = ["title", "year"]
```

Либо, не указывать в `settings.py`, а сразу же указать во вью:

```python
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics

class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["title", "year_published"]
```

Теперь можно делать запросы:

```
http://127.0.0.1:8000/api/books/?title=Война+и+мир&year_published=1869
```

---

### 3.3. Кастомные классы `FilterSet`

Если фильтрация сложнее, чем проверка на равенство, создаём модуль

`myapp/filters.py`

И в нём создаём класс `FilterSet`:

```python
import django_filters
from .models import Book

class BookFilter(django_filters.FilterSet):
    min_year = django_filters.NumberFilter(field_name="year_published", lookup_expr="gte")
    max_year = django_filters.NumberFilter(field_name="year_published", lookup_expr="lte")
    author = django_filters.CharFilter(field_name="author__name", lookup_expr="icontains")

    class Meta:
        model = Book
        fields = ["min_year", "max_year", "author"]
```

View подключается так:

```python
from .filters import BookFilter

class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filterset_class = BookFilter

```

Примеры запросов:

```
http://127.0.0.1:8000/api/books/?min_year=1800&max_year=1900
http://127.0.0.1:8000/api/books/?author=Толстой
```

---

### 3.4. Типы фильтров

`django-filter` предоставляет разные фильтры, соответствующие типам данных:

* **CharFilter** — строковые поля (с `lookup_expr="icontains"`, `"exact"`, и т. д.).
* **NumberFilter** — числовые поля (`gte`, `lte`, `exact`).
* **DateFilter** — фильтрация по датам.
* **BooleanFilter** — фильтрация по логическим полям.
* **MultipleChoiceFilter** и **ModelChoiceFilter** — выбор из набора значений.

Пример: фильтрация по диапазону дат публикации книги:

(ПРИМЕЧАНИЕ: это абстрактный пример - в нашем проекте нет поля даты `published_at`)

```python
class BookFilter(django_filters.FilterSet):
    published_after = django_filters.DateFilter(field_name="published_at", lookup_expr="gte")
    published_before = django_filters.DateFilter(field_name="published_at", lookup_expr="lte")

    class Meta:
        model = Book
        fields = ["published_after", "published_before"]
```

---

### 3.5. Итог

С помощью `django-filter` можно:

* быстро создавать простые фильтры (`filterset_fields`),
* описывать гибкие правила (`FilterSet`),
* работать с разными типами данных (строки, числа, даты, булевы значения),
* создавать виртуальные фильтры (виртуальные поля), которые внутри себя мапятся на реальные поля модели.


