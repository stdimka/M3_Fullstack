## Основные типы полей:

| Поле              | Назначение                           | Подробное описание                                                         | Пример использования                                             |
| ----------------- | ------------------------------------ | -------------------------------------------------------------------------- | ---------------------------------------------------------------- |
| `CharField`       | Строка фиксированной длины           | Требует указания `max_length`. Для коротких текстов, названий, заголовков. | `name = models.CharField(max_length=100)`                        |
| `TextField`       | Длинный текст                        | Без ограничения длины. Для описаний, комментариев и т.п.                   | `description = models.TextField()`                               |
| `IntegerField`    | Целое число                          | Подходит для целых значений: возраст, количество, рейтинг и т.п.           | `age = models.IntegerField()`                                    |
| `FloatField`      | Число с плавающей точкой             | Для чисел с дробной частью (менее точное, чем Decimal).                    | `price = models.FloatField()`                                    |
| `BooleanField`    | Истина/Ложь                          | Хранит только `True` или `False`. Требует `default`.                       | `is_active = models.BooleanField(default=True)`                  |
| `DateField`       | Дата                                 | Хранит только дату (без времени).                                          | `birth_date = models.DateField()`                                |
| `DateTimeField`   | Дата и время                         | Для отметок времени: создания, обновления и т.п.                           | `created_at = models.DateTimeField(auto_now_add=True)`           |
| `TimeField`       | Время                                | Только время без даты.                                                     | `start_time = models.TimeField()`                                |
| `EmailField`      | Email с валидацией                   | Как `CharField`, но с проверкой формата email.                             | `email = models.EmailField()`                                    |
| `URLField`        | Ссылка                               | Хранит URL-адрес с валидацией формата.                                     | `website = models.URLField()`                                    |
| `SlugField`       | Упрощённый URL                       | Для коротких уникальных идентификаторов в URL. Только буквы, цифры, дефис. | `slug = models.SlugField(unique=True)`                           |
| `DecimalField`    | Десятичное число с высокой точностью | Лучше для денежных значений. Требует `max_digits` и `decimal_places`.      | `amount = models.DecimalField(max_digits=10, decimal_places=2)`  |
| `FileField`       | Файл                                 | Для загрузки и хранения файлов.                                            | `document = models.FileField(upload_to='docs/')`                 |
| `ImageField`      | Изображение                          | Как `FileField`, но проверяет, что файл — изображение. Требует Pillow.     | `photo = models.ImageField(upload_to='images/')`                 |
| `ForeignKey`      | Связь "многие к одному"              | Создаёт внешний ключ к другой модели.                                      | `author = models.ForeignKey(User, on_delete=models.CASCADE)`     |
| `OneToOneField`   | Связь "один к одному"                | Как `ForeignKey`, но уникальна: одна запись на одну.                       | `profile = models.OneToOneField(User, on_delete=models.CASCADE)` |
| `ManyToManyField` | Связь "многие ко многим"             | Позволяет множеству объектов быть связаны с множеством других.             | `tags = models.ManyToManyField(Tag)`                             |
| `UUIDField`       | Уникальный идентификатор             | Хранит UUID. Удобен для публичных ссылок или скрытых идентификаторов.      | `uuid = models.UUIDField(default=uuid.uuid4, editable=False)`    |

