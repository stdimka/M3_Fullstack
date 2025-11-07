# Django `.aggregate()` 

## **1. Когда применяется `.aggregate()`**

* Когда нужен **один или несколько итогов** по всему набору данных.
* Применяется к:

  * всей таблице
  * отфильтрованным данным (`.filter()`)
  * аннотированным данным (`.annotate()`)
* Срабатывает **в конце цепочки**, результат **не QuerySet**, а словарь.


### Что делать, если дополнительно нужно группировка по определённому полю?

* Если нужна **группировка** надо 
  * Забыть метод `.aggregate()` 
  * и использовать `.annotate()`.
  * 

### SQL-аналог агрегации:

```sql
SELECT SUM(price), AVG(price) FROM book;
```

---

## **2. Что принимает `.aggregate()`**

* **Агрегирующие функции**:

  * `Sum`, `Avg`, `Count`, `Max`, `Min`, `StdDev`, `Variance`
* **Имя поля** (строкой) или выражение (`F`, `Case/When`).
* **Аргументы**:

  * `distinct=True` — учитывать только уникальные значения.
  * `filter=Q(...)` — условие внутри агрегата (Django 2.0+).

Пример:

```python
Book.objects.aggregate(
    avg_price=Avg("price"),
    unique_authors=Count("author", distinct=True),
    expensive_count=Count("id", filter=Q(price__gt=100))
)
```

SQL-вариант этого же запроса:

```sql
SELECT 
    AVG(price) AS avg_price,
    COUNT(DISTINCT author) AS unique_authors,
    COUNT(CASE WHEN price > 100 THEN id END) AS expensive_count
FROM book;

```
---

## **3. Что возвращает `.aggregate()`**

* Словарь: ключи = заданные имена, значения = результаты.

```python
{'avg_price': 125.5, 'unique_authors': 8, 'expensive_count': 3}
```
---

## **4. Что может `.aggregate()`**

* Вычислять агрегаты по полю или выражению (`F`, арифметика, условия).
* Комбинировать несколько агрегатов за раз.
* Применять фильтры внутри агрегатов.
* Работать поверх аннотированных данных.

---

## **5. Что `.aggregate()` НЕ может**

* Не группирует (`GROUP BY`) — для этого `.annotate()`.
* Не возвращает QuerySet — после вызова работать с ним нельзя.
* Не даёт построчных результатов — только итоговые значения.

---

## **6. Примеры — Python + SQL**

### **По имени поля**

```python
Book.objects.aggregate(total_price=Sum("price"))
```

```sql
SELECT SUM(price) AS total_price FROM book;
```

---

### **С `F`-объектом (вычисление в SQL)**

```python
from django.db.models import F, Avg
Book.objects.aggregate(
    avg_final_price=Avg(F("price") * (1 - F("discount") / 100))
)
```

```sql
SELECT AVG(price * (1 - discount / 100.0)) AS avg_final_price
FROM book;
```

---

### **Через аннотацию**

```python
from django.db.models import Sum
books = Book.objects.annotate(
    final_price=F("price") * (1 - F("discount") / 100)
)
books.aggregate(total_final_price=Sum("final_price"))
```

```sql
WITH annotated AS (
    SELECT price * (1 - discount / 100.0) AS final_price
    FROM book
)
SELECT SUM(final_price) AS total_final_price
FROM annotated;
```

---

💡 **Краткая формула `.aggregate()`:**

> `.aggregate()` = `SELECT ... AGG_FUNC(...) FROM ...` без `GROUP BY`

---
