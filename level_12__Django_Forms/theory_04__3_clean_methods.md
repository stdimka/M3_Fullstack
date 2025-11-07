## Ещё раз про переопределение методов `clean_<field>()`, `clean()` и кастомные валидаторы

### 1. Валидация отдельного поля (`clean_<field>`)

```python
from django import forms
from django.core.exceptions import ValidationError

class RegisterForm(forms.Form):
    username = forms.CharField(max_length=20)
    age = forms.IntegerField()

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if " " in username:
            raise ValidationError("Имя пользователя не должно содержать пробелов.")
        return username
```

---

### 2. Сквозная проверка формы (нескольких полей одновременно) (`clean()`)

```python
class RegisterForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        pwd = cleaned_data.get("password")
        confirm_pwd = cleaned_data.get("confirm_password")

        if pwd != confirm_pwd:
            raise ValidationError("Пароли не совпадают.")
        return cleaned_data
```

---

### 3. Валидация на уровне модели (если форма с ней связана)

```python
from django.db import models
from django.core.exceptions import ValidationError

class Product(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def clean(self):
        if self.price <= 0:
            raise ValidationError("Цена должна быть положительной.")
```

Использование:

```python
product = Product(name="Товар", price=-10)
product.full_clean()  # вызовет ValidationError
```

---

### 4. Пользовательский валидатор (функция)

```python
from django.core.exceptions import ValidationError

def validate_even(value):
    if value % 2 != 0:
        raise ValidationError("Значение должно быть чётным числом.")
```

Применение:

```python
class NumberForm(forms.Form):
    number = forms.IntegerField(validators=[validate_even])
```

---

## И, ещё раз, "на зачёт"!

* `is_valid()` → запускает валидацию формы.
* `clean_<field>()` → валидация конкретного поля.
* `clean()` → валидация зависимостей полей.
* `model.clean()` и `full_clean()` → бизнес-валидация в моделях.
* `ValidationError` — способ сообщить об ошибке.
