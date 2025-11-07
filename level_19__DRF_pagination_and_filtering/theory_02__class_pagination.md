## Встроенные классы пагинации DRF

### PageNumberPagination (постраничная пагинация)

* Использует **номер страницы** и **размер страницы**.
* Самый понятный и часто используемый вариант.

**Пример настроек:**

```python
from rest_framework.pagination import PageNumberPagination

class MyPageNumberPagination(PageNumberPagination):
    page_size = 5  # количество объектов на странице по умолчанию
    page_size_query_param = 'page_size'  # параметр в URL для изменения размера
    max_page_size = 100  # максимальное количество объектов на страницу
```

**Основные параметры:**

* `page` — номер страницы.
* `page_size` — сколько объектов показывать на странице (если указано в классе).
* `page_size_query_param` — имя query-параметра, которым клиент может менять `page_size`.
* `max_page_size` — ограничение сверху для `page_size`.


**Пример запроса:**

```
GET /api/books/?page=2&page_size=10
```

**Пример ответа:**

```json
{
    "count": 12,
    "next": "http://example.com/api/books/?page=3&page_size=3",
    "previous": "http://example.com/api/books/?page=1&page_size=3",
    "results": [
        {"id": 4, "title": "Book 4", "author": "Author A"},
        {"id": 5, "title": "Book 5", "author": "Author B"},
        {"id": 6, "title": "Book 6", "author": "Author C"}
    ]
}
```

**Пояснения:**

* `count` — общее количество объектов.
* `next` / `previous` — ссылки на соседние страницы.
* `results` — список объектов текущей страницы.


---

### LimitOffsetPagination (сдвиг + лимит)

* Работает через **смещение (offset)** и **лимит (limit)**.
* Подходит для API, где нужен произвольный доступ к данным (например, загрузка с середины списка).

**Пример настроек:**

```python
from rest_framework.pagination import LimitOffsetPagination

class MyLimitOffsetPagination(LimitOffsetPagination):
    default_limit = 5  # количество объектов по умолчанию
    limit_query_param = 'limit'  # параметр лимита
    offset_query_param = 'offset'  # параметр смещения
    max_limit = 100  # максимальный лимит
```

**Основные параметры:**

* `limit` — сколько объектов вернуть.
* `offset` — с какого объекта начинать.
* `max_limit` — максимальное значение `limit`.

**Пример запроса:**

```
GET /api/books/?limit=10&offset=20
```

**Пример ответа:**

```json
{
    "count": 12,
    "next": "http://example.com/api/books/?limit=3&offset=6",
    "previous": "http://example.com/api/books/?limit=3&offset=0",
    "results": [
        {"id": 4, "title": "Book 4", "author": "Author A"},
        {"id": 5, "title": "Book 5", "author": "Author B"},
        {"id": 6, "title": "Book 6", "author": "Author C"}
    ]
}
```

**Пояснения:**

* `limit` — сколько объектов вернуть.
* `offset` — с какого объекта начинать.
* Формат ответа похож на `PageNumberPagination`.


---

### CursorPagination (курсорная пагинация)

* Вместо страниц или offset используется **курсор** — зашифрованный указатель.
* Хорошо подходит для больших и динамичных наборов данных (например, соцсети, ленты).

**Пример настроек:**

```python
from rest_framework.pagination import CursorPagination

class MyCursorPagination(CursorPagination):
    page_size = 5  # количество объектов на страницу
    ordering = '-created_at'  # сортировка (например, по дате)
    cursor_query_param = 'cursor'  # название параметра курсора в URL
```

**Основные параметры:**

* `cursor` — строка, сгенерированная сервером, указывающая, откуда продолжать.
* `page_size` — размер страницы.
* `ordering` — поле, по которому сортируются данные (обычно `created_at` или `id`).
* `cursor_query_param` — имя query-параметра для курсора (по умолчанию `cursor`).

**Пример запроса:**

```
GET /api/books/?cursor=cD0yMDI1LTA5LTAxVDA5OjAwOjAwWg==
```

**Пример ответа:**

```json
{
    "next": "http://example.com/api/books/?cursor=cD0yMDI1LTA5LTAxVDA5OjEwOjAwWg==",
    "previous": "http://example.com/api/books/?cursor=cD0yMDI1LTA5LTAxVDA4OjUwOjAwWg==",
    "results": [
        {"id": 4, "title": "Book 4", "author": "Author A"},
        {"id": 5, "title": "Book 5", "author": "Author B"},
        {"id": 6, "title": "Book 6", "author": "Author C"}
    ]
}
```

**Пояснения:**

* `next` / `previous` — курсоры для следующей и предыдущей порции данных.
* `results` — текущая порция объектов.
* `count` обычно не используется (или требует дополнительной нагрузки на базу).
* Работает быстро и стабильно на больших и динамических таблицах.



**Преимущества CursorPagination:**

* Быстрая работа на больших таблицах.
* Не "съезжают" данные при добавлении/удалении записей (в отличие от offset).

**Недостатки:**

* Нельзя "перейти к n-й странице".
* Сложнее дебажить (курсоры выглядят как длинные токены).


---

### Выводы

* **PageNumberPagination** — удобна для классических сайтов и простых API.
* **LimitOffsetPagination** — гибкая, но может тормозить на больших offset.
* **CursorPagination** — самая надёжная для больших и изменяющихся данных.



| Класс                     | Как работает                       | Основные параметры                                            | Плюсы                                                            | Минусы                                                                 |
| ------------------------- | ---------------------------------- | ------------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------- |
| **PageNumberPagination**  | Разделение на страницы (по номеру) | `page`, `page_size`, `page_size_query_param`, `max_page_size` | ✔ Понятна пользователям<br>✔ Простая реализация                  | ✖ При изменении данных страницы могут «съезжать»                       |
| **LimitOffsetPagination** | Смещение + лимит                   | `limit`, `offset`, `max_limit`                                | ✔ Гибкость (можно начать с любого места)<br>✔ Подходит для API   | ✖ Медленно при больших offset<br>✖ Данные могут «съезжать»             |
| **CursorPagination**      | Курсор (указатель на позицию)      | `cursor`, `page_size`, `ordering`, `cursor_query_param`       | ✔ Стабильна при изменении данных<br>✔ Высокая производительность | ✖ Нельзя перейти к «странице 5»<br>✖ Сложнее дебажить (длинные токены) |

