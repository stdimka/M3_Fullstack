## Кастомные фильтры

Иногда стандартных инструментов (`django-filter`, `SearchFilter`, `OrderingFilter`) недостаточно.   

В таких случаях DRF позволяет реализовать собственную логику фильтрации.

---

### 1. Переопределение `get_queryset`

Простейший способ — отфильтровать данные напрямую в методе `get_queryset`:

```python
class BookListView(generics.ListAPIView):
    serializer_class = BookSerializer

    def get_queryset(self):
        queryset = Book.objects.all()
        year = self.request.query_params.get("year")
        if year is not None:
            queryset = queryset.filter(year=year)
        return queryset
```

Теперь можно делать запрос:

```
GET /books/?year=2020
```

---

### 2. Использование `filter_queryset`

Метод `filter_queryset` применяется, когда нужно добавить собственный фильтр **вместе с другими backends**:

```python
class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        only_my = self.request.query_params.get("only_my")
        if only_my == "true":
            queryset = queryset.filter(owner=self.request.user)
        return queryset
```

Теперь запрос:

```
GET /books/?only_my=true
```

вернёт только книги, добавленные текущим пользователем.

---

### 3. Пользовательские фильтры через классы

Можно создать отдельный фильтр-бэкенд, реализовав метод `filter_queryset`:

```python
from rest_framework.filters import BaseFilterBackend

class IsPublicFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        only_public = request.query_params.get("only_public")
        if only_public == "true":
            return queryset.filter(is_public=True)
        return queryset
```

Подключаем его в `filter_backends`:

```python
class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [IsPublicFilterBackend, DjangoFilterBackend]
```

---

### 4. Когда нужны кастомные фильтры

Кастомные фильтры полезны, если:

* нужно фильтровать данные по сложным условиям (например, "показать только непросмотренные уведомления за последние 7 дней");
* требуется ограничение выборки для конкретного пользователя;
* бизнес-логика не укладывается в стандартные фильтры `django-filter`.

---

### Резюме

* `get_queryset` — простой способ встроить фильтрацию.
* `filter_queryset` — позволяет добавить кастомную логику поверх стандартных фильтров.
* собственные классы фильтров — для переиспользования и чистоты кода.

