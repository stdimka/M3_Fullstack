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

    def clean_name(self):
        name = self.cleaned_data.get("name")
        if re.search(r'\d', name):
            raise ValidationError("Имя не должно содержать цифры.")
        return name

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get("name")
        email = cleaned_data.get("email")

        if name == 'root' and email != "root@root.com":
            raise ValidationError("Суперпользователь не тот)")
        return cleaned_data