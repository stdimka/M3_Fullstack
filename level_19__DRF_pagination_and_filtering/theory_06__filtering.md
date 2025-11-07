## 1. Фильтрация в API

Хорошо получить ВСЕ данные БД через API.   
Но ГОРАЗДО удобнее получить ТОЛЬКО результаты, подходящие под КОНКРЕТНЫЕ условия, например:

* выбрать только активных пользователей;
* найти книги определённого автора;
* показать заказы за последний месяц;
* ограничить список объектов для текущего пользователя;
* и т.д. и т.п.

Выполнить эти задачи можно с помощью **Фильтрации**.   


## 2. Базовые средства фильтрации DRF

Django REST Framework предоставляет несколько готовых инструментов для фильтрации. 
А также для поиска и сортировки запрашиваемых данных.  
Все они подключаются через свойство `filter_backends` в классе представления (или глобально в настройках проекта).

### 2.1. `filter_backends`

Это список классов, которые будут обрабатывать входящие параметры фильтрации.
Например, в `settings.py` можно подключить фильтры глобально:

```python
REST_FRAMEWORK = {
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ]
}
```

Или в конкретном view:

```python
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book
from .serializers import BookSerializer

class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
```

---

### 2.2. `DjangoFilterBackend`

Это бэкенд для работы с библиотекой **django-filter**, позволяющий легко фильтровать по полям модели.
Простейший вариант — указать список полей:

```python
class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["author", "year"]
```

Теперь можно отправлять запросы вида:

```
GET /books/?author=Толстой&year=1877
```

---

### 2.3. `SearchFilter`

Предназначен для простого текстового поиска.
Используется параметр `search_fields`, в котором задаются поля:

```python
class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ["title", "author__name"]
```

Пример запроса:

```
GET /books/?search=django
```

Поиск будет выполнен по заголовку книги и имени автора.

---

### 2.4. `OrderingFilter`

Отвечает за сортировку результатов.
Указывается список полей, по которым разрешена сортировка:

```python
class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ["title", "year"]
    ordering = ["title"]  # сортировка по умолчанию
```

Примеры запросов:

```
GET /books/?ordering=year
GET /books/?ordering=-title
```

---

Таким образом, даже без дополнительной логики DRF позволяет:

* ограничить выборку (`DjangoFilterBackend`),
* выполнять поиск (`SearchFilter`),
* менять порядок результатов (`OrderingFilter`).

