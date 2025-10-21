## 1 Наследование от встроенных классов

Мы уже убедились, что DRF позволяет создавать свои классы пагинации, наследуясь от встроенных:

* `PageNumberPagination`
* `LimitOffsetPagination`
* `CursorPagination`

Благодаря этому мы может добавить дополнительные поля в JSON-ответ.

---

## 2 Пример: добавление `total_pages` и `current_page`

`myapp/pagination.py`:

```python
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
import math

class CustomPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

    def get_paginated_response(self, data):
        total_pages = math.ceil(self.page.paginator.count / self.page.paginator.per_page)
        current_page = self.page.number
        return Response({
            'count': self.page.paginator.count,
            'total_pages': total_pages,
            'current_page': current_page,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
```

* `self.page.paginator.count` — общее количество объектов.
* `self.page.paginator.per_page` — размер страницы.
* `self.page.number` — текущая страница.
* JSON теперь содержит **удобные поля для фронтэнда**: `total_pages` и `current_page`.

