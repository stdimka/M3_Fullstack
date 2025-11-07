# Форматирование результата
---

| **Метод**       | **Описание**                           | **Возвращает**      | **Пример**                                                               |
| --------------- | -------------------------------------- | ------------------- | ------------------------------------------------------------------------ |
| `values()`      | Возвращает словари с указанными полями | `QuerySet` словарей | `Book.objects.values('author', 'title')`                                 |
| `values_list()` | Возвращает кортежи с указанными полями | `QuerySet` кортежей | `Book.objects.values_list('author', flat=True)`                          |
| `raw()`         | Выполняет сырой SQL-запрос             | `RawQuerySet`       | `Book.objects.raw('SELECT * FROM app_book WHERE year_published > 2000')` |

---

* **`values()`**
  Возвращает выборку в виде QuerySet словарей, где: 
* ключи — имена полей, 
* значения — их значения. 

Удобно, если нужны только отдельные поля.

⚠️ ВАЖНОЕ УТОЧНЕНИЕ:  
`values()` и `values_list()` возвращают НЕ словари и тюплы соответственно,  
а QuerySet, который ведёт себя КАК БУДТО словарь или тюпл!

```python
books_data = Book.objects.values('author', 'title')
for book in books_data:
    print(book['author'], book['title'])
```

---

* **`values_list()`**
  Возвращает выборку в виде кортежей, содержащих указанные поля.   
  Если используется `flat=True` и выбрано одно поле,  
  то возвращается плоский список значений (почти обычный список).

  ```python
  authors = Book.objects.values_list('author', flat=True)
  for author in authors:
      print(author)
  ```


---
 
* **`raw()`**
  Позволяет выполнить произвольный SQL-запрос и получить объекты модели.

```python
recent_books = Book.objects.raw('SELECT * FROM myapp_book WHERE year_published > 1900')

```
Результатом будет просто объект запроса, что-от вроде этого:

```python
<RawQuerySet: SELECT * FROM "myapp_book" WHERE "myapp_book"."year_published" > 1900>
```

Что ещё не говорит, что запрос верный.  
Для проверки нужно применить `list(recent_books)` или цикл

```python
  for book in recent_books:
      print(book.title, book.year_published)
```