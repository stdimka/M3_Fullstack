### Модель

```python
class Book(models.Model):
    author = models.CharField(max_length=100)
    title = models.CharField(max_length=200)
    year_published = models.IntegerField()

    def __str__(self):
        return f"{self.author}-{self.title}, {self.year_published}"
    
    @classmethod
    def fill_if_empty(cls):
        if cls.objects.exists():
            return

        books_data = [
            {"author": "Лев Толстой", "title": "Война и мир", "year_published": 1869},
            {"author": "Фёдор Достоевский", "title": "Преступление и наказание", "year_published": 1866},
            {"author": "Александр Пушкин", "title": "Станционный смотритель", "year_published": 1831},
            {"author": "Александр Пушкин", "title": "Евгений Онегин", "year_published": 1833},
            {"author": "Николай Гоголь", "title": "Мёртвые души", "year_published": 1842},
            {"author": "Антон Чехов", "title": "Вишнёвый сад", "year_published": 1904},
            {"author": "Уильям Шекспир", "title": "Гамлет", "year_published": 1603},
            {"author": "Мигель де Сервантес", "title": "Дон Кихот", "year_published": 1605},
            {"author": "Габриэль Гарсиа Маркес", "title": "Сто лет одиночества", "year_published": 1967},
            {"author": "Франц Кафка", "title": "Процесс", "year_published": 1925},
            {"author": "Джордж Оруэлл", "title": "1984", "year_published": 1949},
        ]
        cls.objects.bulk_create([cls(**data) for data in books_data])
```

### Добавить метод в `apps.py` в `MyappConfig`

```python
class MyappAutofillConfig(MyappConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'
    verbose_name = 'My App with Auto Init'

    def ready(self):
        from .models import Book
        try:
            Book.fill_if_empty()
        except Exception as e:
            print(e)
```

### Создать и применить миграции

### Изменить `settings.INSTALLED_APPS`

```python

...
myapp.apps.MyappAutofillConfig
...
```