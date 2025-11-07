***Unless you’re planning to build websites and applications that  
do nothing but publish content, and don’t accept input from your visitors,  
you’re going to need to understand and use forms.***

*(Если вы не планируете создавать веб-сайты и приложения, которые  
только публикуют контент и не принимают данные от посетителей,  
вам нужно будет понимать и использовать формы.)*

Цитата из [раздела Form официального руководства Django.](https://docs.djangoproject.com/en/5.2/topics/forms/#working-with-forms)

# Зачем нужны формы?

Итак. формы решают три основные задачи:
- Безопасное получение данных от пользователя (регистрация, обратная связь, заполнение корзины заказа и т.д.);
- Валидация данных — проверка корректности (обязательность, длина, формат и т.д.);
- Удобная обработка полученных и проверенных (валидированных) данных на сервере.

Если писать всё вручную, придётся самому:
- создавать HTML-формы,
- писать проверки для каждого поля,
- обрабатывать ошибки ввода и показывать их пользователю.

Django Forms позволяет сделать это удобнее, быстрее и, главное, безопаснее.

# Простейшая реализация формы на Django

## 1. Копируем файлы из `example_from_lecture` (как в предыдущей теме Django Admin)

- копируем папку со всем содержимым на локальный компьютер
- переименовываем файл `db.sqlite3--` (удаляем 2 дефиса в конце)
- создаём виртуальное окружение
- запускаем виртуальное окружение
- устанавливаем необходимые пакеты: `pip install -r requirements.txt` 
- супер пользователь уже добавлен в БД (login: `root`, password `123`)

Создадим новое приложение, для получения и обработки обратной связи:
- `./manage.py startapp feedback`
- добавим его в `INSTALLED_APPS` `setiings.pe`

---

## 2. Простейший вариант реализации формы (Python)

В приложении `feedback` добавляем модуль `forms.py`, где cоздаём форму, наследуемую от `forms.Form`.

```python
# forms.py
from django import forms

class FeedbackForm(forms.Form):
    name = forms.CharField(label="Ваше имя", max_length=50)
    email = forms.EmailField(label="Email")
    message = forms.CharField(label="Сообщение", widget=forms.Textarea)
```

В Django `forms.CharField` и `models.CharField` выглядят похоже,  
но они используются в разных слоях фреймворка и выполняют разные задачи:
- `models.CharField` — определяет структуру и ограничения для хранения текста в БД.
- `forms.CharField` — определяет валидацию и отображение данных на уровне формы, ПРЕЖДЕ ЧЕМ они попадут в БД.

`widget=forms.Textarea` — это параметр для поля формы, который определяет тип HTML-элемента для отображения этого поля.  
По умолчанию для текстового поля (`CharField`) Django использует `<input type="text">`.

---

## 3) Простейший вариант реализации формы (HTML)

В `views.py` передаём форму в шаблон:

```python
from django.shortcuts import render
from .forms import FeedbackForm

def feedback_view(request):
    form = FeedbackForm()
    return render(
        request, 
        "feedback/feedback.html", 
        {
            "form": form, 
            'active_page': 'feedback'
        }
    )
```

В шаблоне `feedback/feedback.html`:

```html
{% extends "base.html" %}
{% load static %}

{% block title %}Feedback page{% endblock %}

{% block content %}

<div class="w-50 mx-auto">
    <h2>This is Feedback page</h2>

    <hr>
    <h3>Feedback Form</h3>
    <form method="post">
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" class="btn btn-primary">Отправить</button>
    </form>
</div>

{% endblock %}
```

`{{ form.as_p }}` — быстрый способ отобразить все поля как параграфы.

В главном маршрутизаторе `main/urls.py` добавляем новый маршрут:
```python
    path('feedback/', include('feedback.urls')),
```

А также создаём новый маршрутизатор в приложении `feedback`:

`feedback/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.feedback_view, name='feedback'),
]
```


Для дополнительного удобство можно добавить эту ссылку в главное меню `href="{% url 'feedback' %}"`

---

## 4. Лёгкая стилизация (CSS) полей формы

Можно добавить CSS-классы прямо в `forms.py` (у нас `Bootstrap 5.3.7`):

```python
from django import forms

class FeedbackForm(forms.Form):
    name = forms.CharField(
        label="Ваше имя",
        max_length=50,
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
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "Ваше сообщение",
            "rows": 4
        })
    )
```
---

## 5. Варианты форм HTML

В Django вы можете выводить поля по-разному:
- `{{ form.as_p }}` — каждое поле в `<p>`.
- `{{ form.as_table }}` — поля внутри `<table>`.
- `{{ form.as_ul }}` — список `<ul><li>`.
- Ручной рендеринг  — полный контроль:

```html
{% for field in form %}
    <div class="fieldWrapper">
        {{ field.errors }}
        {{ field.label_tag }} {{ field }}
        {% if field.help_text %}
          <p class="help" id="{{ field.auto_id }}_helptext">
            {{ field.help_text|safe }}
          </p>
        {% endif %}
    </div>
{% endfor %}
```
(По умолчанию Django экранирует HTML. Фильтр `safe` отменяет это экранирование.)

## Выводы:

Как видим, с помощью Django можно до минимума (5 строк!) сократить HTML-код.  
А весь необходимый функционал формы описать непосредственно в Python-коде.  
Причём, и это можно сделать невероятно компактно и лаконично!