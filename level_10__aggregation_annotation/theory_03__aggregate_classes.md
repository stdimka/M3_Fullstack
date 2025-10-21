## Агрегирующие Классы

### Агрегирующей классы или всё же Агрегирующие Функции?

В контексте **Django ORM** правильнее всего называть их **агрегирующими классами** (или *классами-агрегатами*), потому что:

* В Python это именно **классы**, а не функции.
* Django реализует их как подклассы `django.db.models.Aggregate` или `Func`.
* Но по назначению они выполняют **агрегирующие операции** — т.е. группируют и сводят значения.

Поэтому в документации и в разговорах встречаются оба варианта:

* «Агрегирующие функции» — если говорить в терминах **SQL** (COUNT, SUM, AVG — это функции SQL).
* «Агрегирующие классы Django» — если точнее описывать **Python-реализацию**.

### Сводная таблица Агрегирующих Классов Django



| Агрегат ( модуль ) | Назначение                                    | Что возвращает            | Частые аргументы                  | Короткий пример                                                        |
|--------------------|-----------------------------------------------|---------------------------|-----------------------------------|------------------------------------------------------------------------|
| Count (core)       | Подсчёт строк/значений                        | int                       | field, distinct, filter           | Book.objects.aggregate(n=Count("id"))                                  |
| Sum (core)         | Сумма значений                                | число / Decimal           | field, filter, output_field       | Book.objects.aggregate(total=Sum("price"))                             |
| Avg (core)         | Среднее                                       | число / Decimal           | field, filter, output_field       | Book.objects.aggregate(avg=Avg("rating"))                              |
| Min (core)         | Минимум                                       | то же, что и тип поля     | field, filter, output_field       | Book.objects.aggregate(first=Min("published_at"))                      |
| Max (core)         | Максимум                                      | то же, что и тип поля     | field, filter, output_field       | Book.objects.aggregate(last=Max("published_at"))                       |
| StdDev (core)      | Стандартное отклонение                        | float                     | field, sample/population*, filter | Book.objects.aggregate(sd=StdDev("price"))                             |
| Variance (core)    | Дисперсия                                     | float                     | field, sample/population*, filter | Book.objects.aggregate(var=Variance("price"))                          |
| StringAgg (pg)     | Склеивание строк через разделитель            | str                       | expression, delimiter, filter     | Author.objects.annotate(books=StringAgg("books__title", ", "))         |
| ArrayAgg (pg)      | Сбор значений в массив                        | list/array                | expression, distinct, filter      | Author.objects.annotate(book_ids=ArrayAgg("books__id", distinct=True)) |
| JSONBAgg (pg)      | Сбор значений в JSON-массив                   | JSON                      | expression, filter                | Author.objects.annotate(titles=JSONBAgg("books__title"))               |
| BoolAnd/BoolOr (pg)| Все/хотя бы одно значение True                | bool                      | expression, filter                | Author.objects.annotate(all_in_stock=BoolAnd("books__in_stock"))       |
| BitAnd/BitOr (pg)  | Побитовые агрегаты по целым                   | int                       | expression, filter                | SomeModel.objects.aggregate(mask=BitAnd("flags"))                      |


\* Для `StdDev/Variance` можно указать вариант выборочной/генеральной статистики через `sample=True` (в некоторых версиях — `sample=False` по умолчанию). Уточняйте для вашей версии Django/БД.

---

## Базовая схема использования

* `aggregate()` — сводит **всю** выборку к одному словарю значений.
* `annotate()` + `values()` — делает группировку и добавляет вычисленное поле для **каждой** группы/строки.
* Группировка задаётся `values("поле", ...)`.
* `filter=Q(...)` внутри агрегата — условная агрегация без `Case/When`.
* Для `NULL` часто применяют `Coalesce(...)`, чтобы получить, например, `0` вместо `None`.

---

## Подробно по каждому агрегату

### `Count` — количество

```python
from django.db.models import Count, Q

# Сколько книг у каждого автора
Author.objects.annotate(
    total_books=Count("books")
).values("name", "total_books")
# [{'name': 'Лев Толстой', 'total_books': 1}, ...]

# Сколько жанров у каждой книги
Book.objects.annotate(
    genre_count=Count("genres")
).values("title", "genre_count")

# Условный подсчёт — сколько книг после 1900 года у каждого автора
Author.objects.annotate(
    modern_books=Count("books", filter=Q(books__year_published__gte=1900))
).values("name", "modern_books")
```

---

### `Sum` — сумма

```python
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.db.models import Value

# Общая сумма страниц всех книг
Book.objects.aggregate(
    total_pages=Sum("detail__page_count")
)
# {'total_pages': 6226}

# Сумма страниц по каждому автору (если у автора нет страниц → 0)
Author.objects.annotate(
    total_pages=Coalesce(Sum("books__detail__page_count"), Value(0))
).values("name", "total_pages")

# Сумма страниц в книгах до 1900 года
Book.objects.aggregate(
    old_pages=Sum("detail__page_count", filter=Q(year_published__lt=1900))
)
```

---

### `Avg` — среднее

```python
from django.db.models import Avg

# Среднее количество страниц по всем книгам
Book.objects.aggregate(avg_pages=Avg("detail__page_count"))

# Среднее количество страниц по каждому автору
Author.objects.annotate(
    avg_pages=Avg("books__detail__page_count")
).values("name", "avg_pages")
```

---

### `Min` / `Max` — минимум и максимум

```python
from django.db.models import Min, Max

# Самый ранний и самый поздний год публикации
Book.objects.aggregate(
    earliest=Min("year_published"),
    latest=Max("year_published")
)

# У каждого автора — самая длинная книга
Author.objects.annotate(
    max_pages=Max("books__detail__page_count")
).values("name", "max_pages")
```

---

### `StdDev` / `Variance` — разброс значений

```python
from django.db.models import StdDev, Variance

# Разброс страниц по всем книгам
Book.objects.aggregate(
    sd_pages=StdDev("detail__page_count"),
    var_pages=Variance("detail__page_count")
)

# По авторам
Author.objects.annotate(
    sd_pages=StdDev("books__detail__page_count"),
    var_pages=Variance("books__detail__page_count")
).values("name", "sd_pages", "var_pages")
```

---

### PostgreSQL-агрегаты


### 1. **StringAgg** — Склеивание строк через разделитель

```python
from django.contrib.postgres.aggregates import StringAgg, ArrayAgg

# Список книг автора одной строкой
Author.objects.annotate(
    titles=StringAgg("books__title", delimiter=", ", ordering="books__year_published")
).values("name", "titles")
# {'name': 'Александр Пушкин', 'titles': 'Станционный смотритель, Евгений Онегин'}
```

### 2. **ArrayAgg** — Сбор значений в массив

```python
from django.contrib.postgres.aggregates import StringAgg, ArrayAgg

# Массив жанров по книге (уникальные)
Book.objects.annotate(
    genres_list=ArrayAgg("genres__name", distinct=True)
).values("title", "genres_list")
```


---

### 3. **JSONBAgg** — сбор значений в JSON-массив

```python
from django.contrib.postgres.aggregates import JSONBAgg

# JSON-массив с информацией о книгах каждого автора
Author.objects.annotate(
    books_json=JSONBAgg(
        # можно передать не просто поле, а выражение dict-like
        {
            "title": "books__title",
            "year": "books__year_published",
            "pages": "books__detail__page_count"
        },
        ordering="books__year_published"
    )
).values("name", "books_json")
```

**Что вернёт для Пушкина** (пример):

```json
{
  "name": "Александр Пушкин",
  "books_json": [
    {"title": "Станционный смотритель", "year": 1831, "pages": 45},
    {"title": "Евгений Онегин", "year": 1833, "pages": 320}
  ]
}
```

---

### 4. **BoolAnd / BoolOr** — логическая агрегация

> Предположим, мы добавили в `BookDetail` поле `in_stock = models.BooleanField(default=True)`
> (наличие книги в продаже/наличие в библиотеке).

```python
from django.contrib.postgres.aggregates import BoolAnd, BoolOr

# Все ли книги автора есть в наличии, и есть ли хотя бы одна в наличии
Author.objects.annotate(
    all_in_stock=BoolAnd("books__detail__in_stock"),
    any_in_stock=BoolOr("books__detail__in_stock")
).values("name", "all_in_stock", "any_in_stock")
```

**Пример:**

```
Лев Толстой — all_in_stock=True, any_in_stock=True
Пушкин — all_in_stock=False, any_in_stock=True
```

---

### 5. **BitAnd / BitOr** — побитовая агрегация

> Полезно, если у вас есть битовые флаги.
> Например, добавим в `Book` поле `flags = models.IntegerField(default=0)`
> (каждый бит обозначает особенность: `0b001` — иллюстрации, `0b010` — твёрдая обложка, `0b100` — редкий экземпляр).

```python
from django.contrib.postgres.aggregates import BitAnd, BitOr

# Побитовая агрегация флагов по автору
Author.objects.annotate(
    flags_all=BitAnd("books__flags"),
    flags_any=BitOr("books__flags")
).values("name", "flags_all", "flags_any")
```

**Как читать:**

* `flags_all` — биты, которые выставлены у **всех** книг автора.
* `flags_any` — биты, которые есть хотя бы у одной книги автора.

---

