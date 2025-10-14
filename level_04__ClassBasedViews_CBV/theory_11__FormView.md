## ✉️ Django `FormView` — краткий обзор и пример

`FormView` — универсальное представление для работы с **формами, не связанными с моделью**.  

Вы указываете:  
* класс формы (`form_class`)
* шаблон (`template_name`)
* URL для редиректа после успешной отправки (`success_url`)
* и можете обработать данные в `form_valid()`

---

## ✅ Цель: форма обратной связи

Поля:

* имя
* email
* сообщение

После отправки — можно, например, вывести сообщение об успешной отправке   
(или в реальном проекте — отправить email).

---

## Шаг 1: Создаём форму

**forms.py**

```python
from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(label="Ваше имя", max_length=100)
    email = forms.EmailField(label="Ваш email")
    message = forms.CharField(label="Сообщение", widget=forms.Textarea)
```

---

## Шаг 2: Создаём представление

**views.py**

```python
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from .forms import ContactForm

class ContactFormView(FormView):
    template_name = "library/contact_form.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact-success")

     
    def form_valid(self, form):
        # здесь можно отправить email, записать в лог, сохранить в БД и т.д.
        print("Сообщение отправлено:")
        print("Имя:", form.cleaned_data["name"])
        print("Email:", form.cleaned_data["email"])
        print("Сообщение:", form.cleaned_data["message"])
        
        # Только здесь и только для примера сохраним в лог-файле
        with open("contact_messages.log", "a", encoding="utf-8") as f:
            f.write(f"{form.cleaned_data['name']} — {form.cleaned_data['email']}\n")
            f.write(f"{form.cleaned_data['message']}\n\n")
     
        return super().form_valid(form)
```

---

## Шаг 3: URL-ы

**urls.py**

```python
from .views import ContactFormView
from django.views.generic import TemplateView

urlpatterns += [
    path("contact/", ContactFormView.as_view(), name="contact"),
    path("contact/success/", TemplateView.as_view(
        template_name="library/contact_success.html"
    ), name="contact-success"),
]
```

---

## Шаг 4: Шаблоны

### 📄 `templates/library/contact_form.html`

```html
{% extends "library/base.html" %}

{% block title %}Обратная связь{% endblock %}

{% block content %}
<h1>Форма обратной связи</h1>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Отправить</button>
</form>
{% endblock %}
```

---

### 📄 `templates/library/contact_success.html`

```html
{% extends "library/base.html" %}

{% block title %}Сообщение отправлено{% endblock %}

{% block content %}
<h1>Спасибо!</h1>
<p>Ваше сообщение успешно отправлено. Мы свяжемся с вами при первой возможности.</p>
{% endblock %}
```

---

## ✅ Результат

* Перейдите на `/contact/`
* Заполните форму и отправьте
* Вы попадёте на `/contact/success/`
* Данные формы обрабатываются в `form_valid()` — можно подключить отправку email, логирование и т.д.

