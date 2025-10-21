# Встроенная валидация (built-in validation)

   * Поля форм (`CharField`, `EmailField`, `IntegerField`, ...) имеют базовую проверку, по типу поля.
     (например, `max_lentgh` (длина строки) и т. д.
   * Дополнительно имеются встроенные валидаторы (`EmailValidator`, `URLValidator` и т. д.)  
   * Модельные поля тоже содержат встроенные ограничения (`max_length`, `unique`, `blank=False`, `choices` и пр.).

## 1. Типы полей формы

| Поле формы            | Тип Python     | Встроенные проверки / валидаторы                       | Параметры ограничения                                                           |
| --------------------- | -------------- | ------------------------------------------------------ | ------------------------------------------------------------------------------- |
| `CharField`           | `str`          | Проверяет, что значение строковое                      | `max_length`, `min_length`, `required=True/False`                               |
| `EmailField`          | `str`          | Проверяет формат email через `EmailValidator`          | `max_length`, `min_length`, `required=True/False`                               |
| `IntegerField`        | `int`          | Проверяет, что значение целое                          | `min_value`, `max_value`, `required=True/False`                                 |
| `FloatField`          | `float`        | Проверяет, что значение можно преобразовать в float    | `min_value`, `max_value`, `required=True/False`                                 |
| `DecimalField`        | `Decimal`      | Проверяет, что значение можно преобразовать в Decimal  | `max_digits`, `decimal_places`, `min_value`, `max_value`, `required=True/False` |
| `BooleanField`        | `bool`         | Проверяет, что значение логическое                     | `required=True/False` (True = поле обязательно)                                 |
| `DateField`           | `date`         | Проверяет формат даты                                  | `input_formats`, `required=True/False`                                          |
| `DateTimeField`       | `datetime`     | Проверяет формат даты и времени                        | `input_formats`, `required=True/False`                                          |
| `TimeField`           | `time`         | Проверяет формат времени                               | `input_formats`, `required=True/False`                                          |
| `ChoiceField`         | любой          | Проверяет, что значение входит в список choices        | `choices`, `required=True/False`                                                |
| `MultipleChoiceField` | список         | Проверяет, что все выбранные значения входят в choices | `choices`, `required=True/False`                                                |
| `FileField`           | `UploadedFile` | Проверяет, что файл загружен                           | `required=True/False`, можно добавить кастомные валидаторы                      |
| `ImageField`          | `ImageFile`    | Проверяет, что загружен изображение                    | `required=True/False`, можно добавить кастомные валидаторы                      |

---

## 2. Параметры (ограничения) для полей формы

### Общие параметры (поддерживаются почти всеми полями)

Почти у всех классов полей (`CharField`, `IntegerField`, `EmailField` и т. д.) можно задавать такие аргументы:

| Параметр              | Тип            | Назначение                                                     |
| --------------------- | -------------- | -------------------------------------------------------------- |
| `required`            | `bool`         | Обязательное поле (по умолчанию `True`)                        |
| `label`               | `str`          | Текст метки для поля                                           |
| `label_suffix`        | `str`          | Суффикс после метки (`:` по умолчанию)                         |
| `help_text`           | `str`          | Подсказка пользователю                                         |
| `initial`             | любое значение | Значение по умолчанию                                          |
| `show_hidden_initial` | `bool`         | Показывать скрытое поле для отслеживания изменений             |
| `validators`          | `list`         | Список валидаторов                                             |
| `error_messages`      | `dict`         | Сообщения об ошибках (`{'required': '...', 'invalid': '...'}`) |
| `widget`              | `Widget`       | Виджет для отображения в HTML                                  |
| `localize`            | `bool`         | Использовать локализацию                                       |
| `disabled`            | `bool`         | Сделать поле недоступным для изменения                         |

---

### Специфические параметры для разных типов полей

#### `CharField`

```python
forms.CharField(
    max_length=None,
    min_length=None,
    strip=True  # обрезает пробелы по краям
)
```

#### `IntegerField`

```python
forms.IntegerField(
    min_value=None,
    max_value=None
)
```

#### `DecimalField`

```python
forms.DecimalField(
    max_value=None,
    min_value=None,
    max_digits=None,
    decimal_places=None
)
```

#### `FloatField`

```python
forms.FloatField(
    min_value=None,
    max_value=None
)
```

#### `BooleanField`

```python
forms.BooleanField(
    required=True  # Если False — галочка может быть пустой
)
```

#### `ChoiceField`

```python
forms.ChoiceField(
    choices=[('1', 'Да'), ('0', 'Нет')],
    initial='1'
)
```

#### `MultipleChoiceField`

```python
forms.MultipleChoiceField(
    choices=[('a', 'A'), ('b', 'B')],
)
```

#### `TypedChoiceField`

```python
forms.TypedChoiceField(
    choices=[('1', 'Один'), ('2', 'Два')],
    coerce=int,          # преобразование к типу
    empty_value=None
)
```

#### `DateField`

```python
forms.DateField(
    input_formats=['%d.%m.%Y', '%Y-%m-%d']
)
```

#### `DateTimeField`

```python
forms.DateTimeField(
    input_formats=['%d.%m.%Y %H:%M']
)
```

#### `EmailField`

```python
forms.EmailField(
    max_length=None,
    min_length=None
)
```

#### `URLField`

```python
forms.URLField(
    max_length=None,
    min_length=None
)
```

#### `FileField`

```python
forms.FileField(
    max_length=None,
    allow_empty_file=False
)
```

#### `ImageField`

```python
forms.ImageField(
    max_length=None
)
```

---

##### Мини-пример

```python
from django import forms

class RegisterForm(forms.Form):
    username = forms.CharField(
        label="Логин",
        max_length=30,
        min_length=3,
        required=True,
        help_text="Введите имя от 3 до 30 символов",
        error_messages={
            "required": "Поле обязательно!",
            "max_length": "Слишком длинное имя",
            "min_length": "Слишком короткое имя",
        }
    )
    age = forms.IntegerField(
        min_value=18,
        max_value=120,
        initial=18,
        label="Возраст"
    )
```

---


## 3. Таблица встроенных валидаторов (built-in validation) Django

Модуль `django.core.validators` содержит набор валидаторов для работы с полями моделей и форм.    
[https://docs.djangoproject.com/en/dev/ref/validators/#built-in-validators](https://docs.djangoproject.com/en/dev/ref/validators/#built-in-validators)

| Валидатор                          | Описание                                                                | Пример использования                                        | Как работает / проверка                                      |
| ---------------------------------- | ----------------------------------------------------------------------- | ----------------------------------------------------------- | ------------------------------------------------------------ |
| **EmailValidator**                 | Проверяет, что строка является корректным email-адресом.                | `EmailValidator(message="Неверный email")`                  | Использует регулярное выражение для формата `name@domain`.   |
| **URLValidator**                   | Проверяет корректность URL.                                             | `URLValidator(message="Введите правильный URL")`            | Допускает схемы `http`, `https`, `ftp`, `ftps` по умолчанию. |
| **RegexValidator**                 | Проверка строки по регулярному выражению.                               | `RegexValidator(r'^[0-9]+$', "Только цифры")`               | Сравнивает ввод с заданным паттерном.                        |
| **MaxLengthValidator**             | Ограничивает максимальную длину строки.                                 | `MaxLengthValidator(50)`                                    | Ошибка, если длина `len(value) > max_length`.                |
| **MinLengthValidator**             | Ограничивает минимальную длину строки.                                  | `MinLengthValidator(5)`                                     | Ошибка, если длина `len(value) < min_length`.                |
| **MaxValueValidator**              | Ограничивает максимальное значение числа.                               | `MaxValueValidator(100)`                                    | Ошибка, если `value > max_value`.                            |
| **MinValueValidator**              | Ограничивает минимальное значение числа.                                | `MinValueValidator(10)`                                     | Ошибка, если `value < min_value`.                            |
| **DecimalValidator**               | Проверка количества цифр и знаков после запятой для Decimal.            | `DecimalValidator(max_digits=5, decimal_places=2)`          | Ошибка, если число не соответствует ограничениям.            |
| **FileExtensionValidator**         | Проверка расширения загружаемого файла.                                 | `FileExtensionValidator(allowed_extensions=['jpg', 'png'])` | Ошибка, если расширение файла не в списке разрешённых.       |
| **validate_email** (функция)       | Упрощённая проверка email (обёртка над EmailValidator).                 | `from django.core.validators import validate_email`         | Вызывает `EmailValidator` внутри себя.                       |
---

### Как применять валидаторы

1. **В полях формы**

```python
from django import forms
from django.core.validators import MinLengthValidator, MaxLengthValidator

class MyForm(forms.Form):
    username = forms.CharField(
        validators=[
            MinLengthValidator(3),
            MaxLengthValidator(20)
        ]
    )
```

2. **В моделях**

```python
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Product(models.Model):
    price = models.DecimalField(
        max_digits=6, decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(10000)]
    )
```

3. **Ручная проверка**

```python
from django.core.validators import validate_email
from django.core.exceptions import ValidationError

try:
    validate_email("test@example.com")
    print("OK")
except ValidationError as e:
    print("Ошибка:", e)
```
