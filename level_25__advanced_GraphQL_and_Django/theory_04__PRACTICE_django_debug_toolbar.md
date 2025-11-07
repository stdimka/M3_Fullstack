## Django Debug Toolbar

Самый популярный инструмент исследования всего и вся в Django.  
Но, к сожалению, но "не дружит" с GraphiQL, так как встроен в HTML,
и "не видит" POST-запросы по AJAX.


Поэтому, устанавливаем другой, чуть менее популярный инструмент Django Silk.

Он встроен непосредственно в middleware, поэтому "видит" все запросы.

Правда с ним есть маленькая проблема: при его установке нужно выполнить миграции,  
чтобы подключить его таблицу для хранения статистических данных о запросах.

## Django Silk

Популярный и простой вариант исследования проблемы N+1 запросов

### 1. Установка:

```bash
pip install django-silk
```

### 2. Настройка:

```python
INSTALLED_APPS = [
    # ...
    "silk",
]

MIDDLEWARE = [
    "silk.middleware.SilkyMiddleware",  # <- в начале
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
```

В `urls.py`:

```python
from django.conf import settings

if settings.DEBUG:
    import silk
    urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]
```


### 3. Выполняем миграции:

```bash
python manage.py migrate silk
```


### Использование:

* Перезапускаем сервер после миграций.
* Переходим на [http://127.0.0.1:8000/silk/](http://127.0.0.1:8000/silk/)
* В разделе **SQL queries** можно увидеть все запросы, их количество и повторения.

**Преимущество:** можно включать/выключать профилирование и сохранять отчёты.

