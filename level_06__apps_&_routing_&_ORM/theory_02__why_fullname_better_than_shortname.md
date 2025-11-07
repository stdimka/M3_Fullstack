Чтобы убедиться в этом создадим новый проект `full_vs_short`.

1. Создаём папку `full_vs_short`
   1. В ней создаём (и ЗАПУСКАЕМ!) виртуальное окружение
1. Импортируем Django
1. Запускаем проект `django-admin startproject main .`  
1. Создаём приложение `myapp`: `./manage.py startapp myapp`
1. Добавляем папки `templates`, `static`
1. Переносим в `static` файлы bootstrap из прошлого проекта
1. Вносим изменения в `settings.py`
```django
TEMPLATES_DIRS = BASE_DIR / 'templates'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATES_DIRS],
        ...
    }
]
...

STATIC_ROOT = BASE_DIR / 'staticfiles'
STATIC_URL = 'static/'
STATICFILES_DIRS = (
    BASE_DIR / 'static',
)
```


9. Добавляем `base.html`
```html
{% load static %}
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>{% block title %}Base Page{% endblock %}</title>
    <link href="{% static 'bootstrap/css/bootstrap.min.css' %}" rel="stylesheet">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="{% url 'home' %}">MySite</a>
            <div class="collapse navbar-collapse">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <li class="nav-item">
                        <a class="nav-link {% if active_page == 'home' %}active{% endif %}" href="{% url 'home' %}">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if active_page == 'about' %}active{% endif %}" href="/">About</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if active_page == 'contacts' %}active{% endif %}" href="/">Contacts</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if active_page == 'myapp' %}active{% endif %}" href="{% url 'myapp' %}">MyApp</a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>
    <div class="container mt-4">
        <h1>{{ active_page|title }}</h1>
        <p>Контент страницы "{{ active_page }}"</p>
        {% block content %}

        {% endblock %}
    </div>
</body>
</html>
```


10. Добавляем `index.html`
```html
{% extends "base.html" %}
{% load static %}

{% block title %}Home page{% endblock %}

{% block content %}
<h2>This is home page</h2>
{% endblock %}
```

11. Добавляем маршрут домашней страницы в `main/urls.py`
```django
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', TemplateView.as_view(
        template_name='index.html',
        extra_context={'active_page': 'home'}
    ), name='home'),
   # path('myapp/', include('myapp.urls')),
]
```

12. Запускаем проект и проверяем настройки

На [следующей странице](theory_03__why_fullname_better_than_shortname2.md) мы добавим изменения в `myapp`.