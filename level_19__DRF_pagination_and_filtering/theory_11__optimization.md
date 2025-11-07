## Оптимизация

Фильтрация может серьёзно нагружать базу данных, особенно если есть связи между моделями или большие таблицы.  

Чтобы избежать проблем с производительностью, нужно учитывать несколько моментов.

---

### 1. Избегаем проблемы N+1

Если в фильтрации или сериализации используются связанные модели, запросы могут выполняться неэффективно  
(каждый объект будет делать отдельный запрос к БД).

Решение:

* использовать `select_related` для ForeignKey;
* использовать `prefetch_related` для ManyToMany.

Пример:

```python
class BookListView(generics.ListAPIView):
    serializer_class = BookSerializer

    def get_queryset(self):
        return (
            Book.objects
            .select_related("author", "publisher")
            .prefetch_related("genres")
        )
```

---

### 2. Индексы на полях

Если поле часто используется в фильтрации (`WHERE`), имеет смысл добавить индекс:

```python
class Book(models.Model):
    title = models.CharField(max_length=255, db_index=True)   # индекс
    year = models.IntegerField(db_index=True)                 # индекс
```

Индексы ускоряют фильтрацию, но занимают дополнительное место в БД. Обычно индексируют:

* поля, по которым часто делают поиск;
* поля, участвующие в сортировке;
* поля, которые часто используются в фильтрах диапазонов (`gte`, `lte`).

---

### 3. Оптимизация фильтрации по связанным моделям

Для фильтров вида `author__name` или `genres__name` индексы особенно важны.
Лучше индексировать именно те поля, по которым идёт фильтрация (`author.name`, `genre.name`).

---

### 4. Кэширование

Если одни и те же запросы выполняются часто:

* можно использовать кэширование на уровне представлений (`@cache_page`),
* или кэшировать результаты сложных запросов (например, Redis).


---

### 5. Фильтрация по множеству значений

Можно искать по списку параметров с помощью `__in`:

```python
class BookFilter(django_filters.FilterSet):
    years = django_filters.BaseInFilter(field_name="year", lookup_expr="in")

    class Meta:
        model = Book
        fields = ["years"]
```

Запрос:

```
GET /books/?years=1990,2000,2010
```

Вернёт книги, у которых `year` равен 1990, 2000 или 2010.

---

### 6. Несколько значений через query-параметры


DRF позволяет указывать несколько значений в параметрах:

```
GET /books/?genre=фантастика&genre=детектив
```

Если использовать `MultipleChoiceFilter` или `ModelMultipleChoiceFilter`,  
`django-filter`  автоматически воспримет это как список.

```python
class BookFilter(django_filters.FilterSet):
    genre = django_filters.MultipleChoiceFilter(
        field_name="genre",
        choices=Book.GENRE_CHOICES  # [('sci-fi', 'Фантастика'), ('detective', 'Детектив'), ...]
    )

    class Meta:
        model = Book
        fields = ["genre"]
```
---

### 7. Фильтрация с `Q` (логическое ИЛИ)

Иногда нужно отобрать объекты, удовлетворяющие **любому из условий**.
Для этого используют `Q`-объекты:

```python
from django.db.models import Q

class BookListView(generics.ListAPIView):
    serializer_class = BookSerializer

    def get_queryset(self):
        queryset = Book.objects.all()
        q = self.request.query_params.get("q")
        if q:
            queryset = queryset.filter(
                Q(title__icontains=q) | Q(author__name__icontains=q)
            )
        return queryset
```

Запрос:

```
GET /books/?q=пушкин
```

Вернёт книги, где `q` встречается либо в названии, либо в имени автора.

---

### 8. Комбинация условий (AND + OR)

Можно комбинировать условия:

```python
queryset = Book.objects.filter(
    Q(year__gte=2000) & (Q(genre__name="фантастика") | Q(genre__name="детектив"))
)
```

Здесь фильтрация выберет книги **после 2000 года** и с жанром **фантастика или детектив**.

---

### 9. Кастомные фильтры с OR-логикой

В `FilterSet` можно описывать методы, которые реализуют сложные фильтры:

```python
class BookFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method="filter_search")

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            Q(title__icontains=value) | Q(author__name__icontains=value)
        )

    class Meta:
        model = Book
        fields = ["search"]
```

Запрос:

```
GET /books/?search=python
```

---
---

### Резюме

Чтобы фильтрация работала быстро:

* используем `select_related` и `prefetch_related`;
* индексируем поля, которые часто участвуют в фильтрации и сортировке;
* применяем кэширование для часто повторяющихся запросов.
* `__in` и `BaseInFilter` — для фильтрации по списку значений.
* `Q`-объекты — для логики И/ИЛИ.
* Кастомные методы в `FilterSet` — для сложных случаев.
* Можно комбинировать несколько параметров в одном запросе для гибкой фильтрации.

