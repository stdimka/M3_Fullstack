Вот пример полного **кастомного Swagger UI** для Django REST Framework через `drf-yasg`, где 

* добавлен логотип, 
* изменены цвета 
* и стиль интерфейса

---

## 1. Базовая настройка (`urls.py`)

```python
from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="My Custom API",
        default_version='v1',
        description="Красиво оформленная документация для REST API",
        contact=openapi.Contact(email="support@example.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
]
```

---

## 2. Создайте папку шаблонов

В корне проекта (где `settings.py`) создайте структуру:

```
templates/
└── drf_yasg/
    └── swagger-ui.html
```

---

## 3. Добавьте кастомный шаблон (`templates/drf_yasg/swagger-ui.html`)

Пример — с логотипом и кастомными цветами:

```html
{% load static %}
<!DOCTYPE html>
<html>
  <head>
    <meta charset="UTF-8">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="{% static 'drf-yasg/style.css' %}">
    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist/swagger-ui.css">
    <style>
      body {
        background: #f9fafb;
      }
      .topbar {
        background-color: #2b6cb0 !important; /* синий фон */
      }
      .topbar-wrapper img {
        content: url('https://upload.wikimedia.org/wikipedia/commons/a/a7/React-icon.svg'); /* пример логотипа */
        height: 40px;
      }
      .swagger-ui .topbar .download-url-wrapper {
        display: none; /* убираем поле ввода URL */
      }
      .swagger-ui .info hgroup.main a {
        color: #2b6cb0;
      }
      .swagger-ui .scheme-container {
        background-color: #edf2f7;
      }
    </style>
  </head>
  <body>
    <div id="swagger-ui"></div>
    <script src="https://unpkg.com/swagger-ui-dist/swagger-ui-bundle.js"></script>
    <script>
      const ui = SwaggerUIBundle({
        url: "{{ schema_url }}",
        dom_id: '#swagger-ui',
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIBundle.SwaggerUIStandalonePreset
        ],
        layout: "BaseLayout",
        docExpansion: "none",
        defaultModelsExpandDepth: 0
      });
    </script>
  </body>
</html>
```

---

## 4. Укажите путь к шаблонам в `settings.py`

(Уже выполнено)

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        ...
    },
]
```

---

## Результат

После запуска сервера и открытия
[`http://127.0.0.1:8000/swagger/`](http://127.0.0.1:8000/swagger/)
мы получаем Swagger-документацию:

* с вашим логотипом,
* в фирменных цветах,
* без лишнего поля ввода URL.

