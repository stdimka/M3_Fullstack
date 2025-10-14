Мы очень легко можем добавить свой валидатор.  

От нас требуется только импортировать исключение `ValidationError` из  
`django.core.exceptions`:


```python
from django.core.exceptions import ValidationError
import re


# Пользовательский валидатор
def validate_no_digits(value):
    if re.search(r'\d', value):
        raise ValidationError("Имя не должно содержать цифры.")
```

Если мы добавим этот валидатор, то цифра в имени даст ошибку валидации:  
```python
from django import forms
from django.core.validators import (
    EmailValidator, MinLengthValidator, MaxLengthValidator,
)
from django.core.exceptions import ValidationError
import re


# Пользовательский валидатор
def validate_no_digits(value):
    if re.search(r'\d', value):
        raise ValidationError("Имя не должно содержать цифры.")


class FeedbackForm(forms.Form):
    name = forms.CharField(
        label="Ваше имя",
        max_length=50,
        validators=[
            MinLengthValidator(3), MaxLengthValidator(10), validate_no_digits
        ],
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Введите имя"
        })
    )
    email = forms.EmailField(
        label="Email",
        validators=[
            EmailValidator
        ],
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Введите email"
        })
    )
    message = forms.CharField(
        label="Сообщение",
        validators=[
            MinLengthValidator(5), MaxLengthValidator(15)
        ],
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "Ваше сообщение",
            "rows": 4
        })
    )
```


Можно также добавить пользовательский метод в метод `clean()` или `clean_name()`:


И пример "глобальной ошибки" формы - ошибки, которая затрагивает несколько полей.

```python
    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        email = cleaned_data.get("email")

        # Проверка зависимости полей
        if not name == "root" and email == 'root@root.com':
            raise forms.ValidationError(
                'У суперпользователь должен быть только один email: "root@root.com"!'  
            )

```
## Добавление метода `clean_name()`:
```python
from django import forms
from django.core.validators import MinLengthValidator, MaxLengthValidator
from django.core.exceptions import ValidationError
import re


class FeedbackForm(forms.Form):
    name = forms.CharField(
        label="Ваше имя",
        max_length=50,
        validators=[
            MinLengthValidator(3),
            MaxLengthValidator(10),
        ],
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Введите имя"
        })
    )

    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "Введите email"
        })
    )

    message = forms.CharField(
        label="Сообщение",
        validators=[
            MinLengthValidator(5),
            MaxLengthValidator(15)
        ],
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "Введите сообщение"
        })
    )

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if re.search(r'\d', name):
            raise ValidationError("Имя не должно содержать цифры.")
        return name

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        email = cleaned_data.get("email")

        # Проверка зависимости полей
        if name != "root" and email == 'root@root.com':
            raise forms.ValidationError(
                'У суперпользователь должен быть только один email: "root@root.com"!'  
            )


```

## Что лучше и правильнее: добавить валидатор или изменить метод `clean()`?

Оба варианта рабочие, но есть важные нюансы.

| Подход                      | Когда использовать                                                                                              |
| --------------------------- | --------------------------------------------------------------------------------------------------------------- |
| **`validators`**            | Если проверка простая, не зависит от других полей и должна быть переиспользуемой (например, в модели и формах). |
| **`clean_<fieldname>`**     | Если нужна кастомная логика именно для формы, и она может использовать контекст формы (`cleaned_data`).         |
| **`clean()`** (общий метод) | Если нужно проверить зависимость между несколькими полями сразу.                                                |

---

### Практические рекомендации:

* Для переиспользуемых правил (одно правило для разных полей) лучше писать валидаторы  
  — их проще переиспользовать в других формах и ДАЖЕ моделях.
* Для логики, специфичной для конкретной формы, удобнее использовать `clean_<fieldname>`.
* Если проверка затрагивает несколько полей — однозначно `clean()`.

