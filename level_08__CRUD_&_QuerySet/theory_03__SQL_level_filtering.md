# Фильтрация (и прочие запросы) на уровне SQL

Мы уже убедились, что Django сначала создаёт QuerySet, и только потом,  
когда это будет действительно нужно, обратится к БД.

Кроме того, Django очень экономично расходует ресурсы сервера, поскольку
все необходимые условия (`filter()`, `exclude()` и т. д.) формирует на уровне SQL-запроса,  
а не на уровне Python-кода.  

Что даёт лучшую производительность и снижает нагрузку на сервер приложений.

## Как это проверить?

Достаточно применить к QuerySet атрибут `.query`.

### Например:

Запрос `MyModel.objects.filter(is_active=True)` будет выглядеть так:

```sql
SELECT * FROM myapp_mymodel WHERE is_active = true;
```
а не так:
```python
qs = MyModel.objects.all()  # загружаются ВСЕ строки
filtered = [obj for obj in qs if obj.is_active]
```

## Почему это так важно?

СУБД лучше оптимизировано для работы с большим объёмом данных.  
Поэтому запросы на "чистом SQL":
- Экономит ресурсы: меньше данных передаётся от базы к Python.
- Быстрее: фильтрация в СУБД обычно быстрее, чем в Python.
- Масштабируемо: можно работать с таблицами в миллионы строк.


# Композиция - 
логически следует из всего вышесказанного:
быстрее, проще и экономичней создать один SQL запрос,  
чем загрузить в Python таблицу (таблицы) полностью и потом обрабатывать.

### Пример сложного композиционного запроса:
*Найти всех авторов, у которых есть опубликованные книги,*   
*и посчитать их средний рейтинг по этим книгам.*

Python:
```python
qs = (
    Author.objects
    .filter(book__is_published=True)
    .annotate(avg_rating=Avg('book__rating', filter=Q(book__is_published=True)))
)
```

#### SQL:
```sql
SELECT
  "app_author"."id",
  "app_author"."name",
  AVG("app_book"."rating") FILTER (WHERE "app_book"."is_published" = true) AS "avg_rating"
FROM "app_author"
INNER JOIN "app_book" ON ("app_book"."author_id" = "app_author"."id")
WHERE "app_book"."is_published" = true
GROUP BY "app_author"."id", "app_author"."name"
```