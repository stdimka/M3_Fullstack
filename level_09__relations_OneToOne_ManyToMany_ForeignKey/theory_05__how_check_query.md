С помощью метода `query` мы можем проверить запросы в QuerySet.  
Это не всегда удобно - если QuerySet возвращает одиночный объект,то мы получим ошибку:

```text
>>> BookDetail.objects.select_related('book').get(id=1).query.__str__()
Traceback (most recent call last):
  File "<input>", line 1, in <module>
AttributeError: 'BookDetail' object has no attribute 'query'
```

Тем более, это не подойдёт для случая нескольких запросов.  
(неэффективный аналог предыдущего запроса):

```python
detail = BookDetail.objects.get(id=1)
title = detail.book.title  # здесь будет второй запрос
```

Решить задачу можно с помощью известного нам объекта `connection`,
и нового полезного объекта `reset_queries` (обнуление списка прежних запросов):

```python
from django.db import connection, reset_queries
from myapp.models import BookDetail

reset_queries()  # очищаем предыдущие запросы

detail = BookDetail.objects.get(id=1)
title = detail.book.title  # здесь будет второй запрос

for query in connection.queries:
    print(query['sql'])

```