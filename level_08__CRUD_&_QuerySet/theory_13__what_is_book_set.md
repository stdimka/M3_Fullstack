## Что такое  book_set?

`book_set` — это обратная связь в Django ORM, 
автоматически созданная для `ForeignKey`, 
если в параметрах ForeignKey не было указано значение `related_name`.

📘 Пример:
```python
class Publisher(models.Model):
    name = models.CharField(max_length=100)

class Book(models.Model):
    title = models.CharField(max_length=200)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE)
```

Теперь, для издательства `Vagrius`:
```python
publisher = Publisher.objects.get(name="Vagrius")
books = publisher.book_set.all()
```
🔹 Здесь book_set — это все книги, связанные с данным издательством.
(т.е. Book объекты, у которых publisher = this Publisher)

### Почему book_set?

Django берёт имя связанной модели (`Book`) и добавляет `_set`.

### Как задать своё имя?

Проще простого! Достаточно добавить `related_name`:
```python
class Book(models.Model):
    title = models.CharField(max_length=200)
    publisher = models.ForeignKey(
        Publisher,
        on_delete=models.CASCADE,
        related_name='books'
    )
```
Теперь можно так: `publisher.books.all()`

Это то же самое, что и `publisher.book_set.all(), но имя понятнее: books, а не book_set.