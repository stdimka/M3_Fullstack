# Фильтрация и выборка


| **Метод**    | **Описание**                              | **Возвращает**     | **Пример**                                               |
|--------------|-------------------------------------------|--------------------|----------------------------------------------------------|
| `all()`      | Получить все записи                       | `QuerySet`         | `Book.objects.all()`                                     |
| `filter()`   | Фильтрация по условию                     | `QuerySet`         | `Book.objects.filter(year_published__gt=1900)`           |
| `exclude()`  | Противоположное `filter()`                | `QuerySet`         | `Book.objects.exclude(author='Лев Толстой')`             |
| `get()`      | Один объект по условию (или исключение)   | `Model instance`   | `Book.objects.get(title='Война и мир')`                  |
| `first()`    | Первый объект (или `None`)                | `Model` или `None` | `Book.objects.filter(author='Александр Пушкин').first()` |
| `last()`     | Последний объект (или `None`)             | `Model` или `None` | `Book.objects.order_by('year_published').last()`         |
| `exists()`   | Проверка наличия хотя бы одного объекта   | `bool`             | `Book.objects.filter(...).exists()`                      |
| `order_by()` | Сортировка по одному или нескольким полям | `QuerySet`         | `Book.objects.order_by('-year_published')`               |
| `distinct()` | Уникальные записи                         | `QuerySet`         | `User.objects.values('author').distinct()`               |


---

* **`all()`**
  Возвращает все книги.

  ```python
  books = Book.objects.all()
  ```
⚠️ ВНИМЕНИЕ!!!  
Для большой ДБ запрос может существенно замедлить работу сервера.  
Поэтому, по возможности, следует его избегать.  
И пользоваться более точными фильтрами.

---

* **`filter()`**
  Возвращает книги, опубликованные после 2000 года.

  ```python
  recent_books = Book.objects.filter(year_published__gt=1900)
  ```

---

* **`exclude()`**
  Возвращает книги, автор которых не «Толстой».

  ```python
  not_tolstoy = Book.objects.exclude(author='Лев Толстой')
  ```

---

* **`get()`**
  Возвращает книгу с точным названием «Война и мир» (если такая одна).

  ```python
  war_and_peace = Book.objects.get(title='Война и мир')
  ```

---

* **`first()`**
  Возвращает первую книгу из выборки авторов «Пушкин».

  ```python
  first_pushkin = Book.objects.filter(author='Александр Пушкин').first()
  ```

---

* **`last()`**
  Возвращает последнюю книгу, отсортированную по году публикации.

  ```python
  last_published = Book.objects.order_by('year_published').last()
  ```

---

* **`exists()`**
  Проверяет, есть ли книги автора «Достоевский».

  ```python
  has_dostoevsky = Book.objects.filter(author='Достоевский').exists()
  ```

---

* **`order_by()`**
  Сортирует книги по году публикации в обратном порядке (сначала новые).

  ```python
  books_sorted = Book.objects.order_by('-year_published')
  ```

---

* **`distinct()`**
  Возвращает уникальные имена авторов (без повторов).

  ```python
  unique_authors = Book.objects.values('author').distinct()
  ```

