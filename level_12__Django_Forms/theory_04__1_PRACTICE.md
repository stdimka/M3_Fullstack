## Тестирование стандартных валидаторов

Для проверки можно вставить эту форму в наш тестовый проект.

```python
from django import forms
from django.core.validators import (
    EmailValidator, MinLengthValidator, MaxLengthValidator,
)


class FeedbackForm(forms.Form):
    name = forms.CharField(
        label="Ваше имя",
        max_length=50,
        validators=[
            MinLengthValidator(3), MaxLengthValidator(10)
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

С помощью `MinLengthValidator(5)`, `MaxLengthValidator(15)` валидируется длина вводимой в поле строки.

### Пример ошибок, которые пропустит браузер, но заметит Django

Современные браузеры прекрасно умеют валидировать тип поля `email`.

Однако, валидатор Django может гораздо бОльше.

Можно закомментить `EmailValidator` и попробовать ввести эти емейлы.  
Браузерный валидатор их пропустит, а Django заблокирует.

| Пример                 | Почему заблокирует Django |
|------------------------|---------------------------|
| `user@localhost`       | Домен без точки           |
| `user#name@domain.com` | Не допустимый символ      |

