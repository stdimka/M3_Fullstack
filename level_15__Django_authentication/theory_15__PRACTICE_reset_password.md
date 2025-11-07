# Сброс и восстановление пароля

Django уже имеет встроенный механизм сброса и восстановления пароля

## Связать готовые вью и шаблоны

```python
# Встроенные Django views (django.contrib.auth.views)

from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)


class MyPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset_form.html"

class MyPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"

class MyPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"

class MyPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"

```


## Добавить ссылки маршрутизации


```python

from . import views
from django.urls import path

urlpatterns = [
    path('password_reset/', views.MyPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.MyPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.MyPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.MyPasswordResetCompleteView.as_view(), name='password_reset_complete'),
]

```

## Изменить шаблон авторизации

`accounts/login.html`

```html
{% extends 'base.html' %}
{% block title %}Login{% endblock %}
{% block content %}
<h2>Login</h2>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <input type="hidden" name="next" value="{{ next }}">
    <button type="submit" class="btn btn-primary">Login</button>
</form>
<p>No account? <a href="{% url 'register' %}?next={{ request.GET.next }}">Register</a></p>

<p>Forger Password? <a href="{% url 'password_reset' %}">Forger Password?</a></p>

{% endblock %}
```


## Добавить шаблоны сброса и замены пароля

`accounts/password_reset_form.html`

```html
{% extends 'base.html' %}
{% block title %}Register{% endblock %}
{% block content %}

<h2>Сброс пароля</h2>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Отправить письмо</button>
</form>
<p>Шаг 1 выполнен!</p>
{% endblock %}
```

`accounts/password_reset_done.html`

```html
{% extends 'base.html' %}
{% block title %}Register{% endblock %}
{% block content %}

<h2>Сброс пароля</h2>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Отправить письмо</button>
</form>
<p>Шаг 2 выполнен!</p>
{% endblock %}
```

`accounts/password_reset_confirm.html`

```html
{% extends 'base.html' %}
{% block title %}Register{% endblock %}
{% block content %}

<h2>Сброс пароля</h2>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Отправить письмо</button>
</form>
<p>Шаг 3 выполнен!</p>
{% endblock %}
```

`accounts/password_reset_complete.html`

```html
{% extends 'base.html' %}
{% block title %}Register{% endblock %}
{% block content %}

<h2>Сброс пароля</h2>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Отправить письмо</button>
</form>
<p>Шаг 4 выполнен!</p>
{% endblock %}
```