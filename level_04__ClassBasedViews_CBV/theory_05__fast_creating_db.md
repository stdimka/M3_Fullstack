Для быстрого тестирования следующих view есть смысл создать тестовую БД.

Для этого прежде создадим приложение `library`

---

## 🗄️ Шаг 1: Модель `Book`

**models.py:**

```python
from django.db import models

class Book(models.Model):
    title = models.CharField("Название", max_length=200)
    author = models.CharField("Автор", max_length=100)
    year = models.PositiveIntegerField("Год издания")
    description = models.TextField("Описание", blank=True)

    def __str__(self):
        return f"{self.title} ({self.author})"
```

---

## ⚙️ Шаг 2: Миграции

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🧪 Шаг 3: Заполнение БД (фейковые книги)

Один из способов — через `shell`:

```bash
python manage.py shell
```

В интерактивной консоли:

```python
from library.models import Book

Book.objects.create(title="Война и мир", author="Лев Толстой", year=1869, description="Эпический роман.")
Book.objects.create(title="Преступление и наказание", author="Фёдор Достоевский", year=1866, description="Психологический роман.")
Book.objects.create(title="Мастер и Маргарита", author="Михаил Булгаков", year=1967, description="Мистический роман.")
Book.objects.create(title="Отцы и дети", author="Иван Тургенев", year=1862, description="Классический роман о нигилизме.")
Book.objects.create(title="Евгений Онегин", author="Александр Пушкин", year=1833, description="Роман в стихах.")
```

✅ Теперь у нас есть таблица `Book` с несколькими записями.

