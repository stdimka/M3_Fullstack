## Сложные фильтры и вложенные данные

В реальных проектах данные часто связаны между собой.  
Например, как в нашем случае, у книги может быть автор, жанры, издательство.   
DRF и `django-filter` позволяют работать и с такими случаями.

---

### 1. Фильтрация по связанным моделям

Через двойное подчёркивание (`__`) можно фильтровать по полям связанных объектов:

```python
class BookFilter(django_filters.FilterSet):
    author_name = django_filters.CharFilter(field_name="author__name", lookup_expr="icontains")

    class Meta:
        model = Book
        fields = ["author_name"]
```

Пример запроса:

```
GET /books/?author_name=Александр+Пушкин
```

---

### 2. Фильтрация по ManyToMany

Если у книги несколько жанров, можно фильтровать по жанру:

```python
class BookFilter(django_filters.FilterSet):
    genre = django_filters.CharFilter(field_name="genres__name", lookup_expr="iexact")

    class Meta:
        model = Book
        fields = ["genre"]
```

Запрос:

```
GET /books/?genre=фантастика
```

---

### 3. Фильтрация по диапазонам

Для чисел и дат удобно использовать `gte` (больше или равно) и `lte` (меньше или равно):

```python
class BookFilter(django_filters.FilterSet):
    min_year = django_filters.NumberFilter(field_name="year", lookup_expr="gte")
    max_year = django_filters.NumberFilter(field_name="year", lookup_expr="lte")

    class Meta:
        model = Book
        fields = ["min_year", "max_year"]
```

Запрос:

```
GET /books/?min_year=1990&max_year=2000
```

---

### 4. Фильтрация по датам

Аналогично можно отбирать записи по дате:

```python
class BookFilter(django_filters.FilterSet):
    published_after = django_filters.DateFilter(field_name="published_at", lookup_expr="gte")
    published_before = django_filters.DateFilter(field_name="published_at", lookup_expr="lte")
```

Запрос:

```
GET /books/?published_after=2020-01-01&published_before=2022-01-01
```

---

### 5. Фильтрация по булевым полям

Для логических полей (например, `is_published`) можно использовать `BooleanFilter`:

```python
class BookFilter(django_filters.FilterSet):
    is_published = django_filters.BooleanFilter(field_name="is_published")
```

Запрос:

```
GET /books/?is_published=true
```

---

### Резюме

* Для связанных моделей используем двойное подчёркивание (`author__name`).
* Для диапазонов чисел и дат — фильтры `gte` / `lte`.
* Для булевых значений — `BooleanFilter`.
* Для ManyToMany фильтрация работает так же, как для ForeignKey.


