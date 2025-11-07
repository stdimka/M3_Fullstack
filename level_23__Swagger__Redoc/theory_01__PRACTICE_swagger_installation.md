### Что такое Swagger

**Swagger** — это интерактивная документация для REST API.
В Django REST Framework (DRF) она позволяет:

* видеть все эндпоинты API,
* тестировать запросы прямо в браузере,
* автоматически обновляться при изменении сериализаторов или вьюх.

---

### Установка в существующий проект с DRF

1. **Установите библиотеку:**

```bash
pip install drf-yasg
```

2. **Добавьте в `INSTALLED_APPS` (в `settings.py`):**

```python
INSTALLED_APPS = [
   ...
   'rest_framework',
   'drf_yasg',
]
```

3. Настройте маршруты (обычно в `urls.py` проекта):

```python
from django.urls import path, re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
   openapi.Info(
       title="My API",
       default_version='v1',
       description="Документация API",
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
```



4. Два формата отображение документации

Библиотека `drf-yasg` автоматически поддерживает **два формата отображения документации**:

| Интерфейс      | Описание                                                                     | URL по умолчанию |
| -------------- | ---------------------------------------------------------------------------- | ---------------- |
| **Swagger UI** | Интерактивная документация: можно тестировать API прямо из браузера.         | `/swagger/`      |
| **ReDoc**      | Более «читабельный» формат: удобен для просмотра описания, но не для тестов. | `/redoc/`        |


Чтоб оставить только одни вариант (например, Swagger), достаточно  
просто убрать лишнюю строку из `urls.py`:

```python
path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
```

Таким образом:

* **Swagger** — для тестирования API (обычно разработчикам).
* **ReDoc** — для документации (обычно клиентам или аналитикам).

---

### Проверка

После запуска сервера откройте:

* Swagger UI: [`http://127.0.0.1:8000/swagger/`](http://127.0.0.1:8000/swagger/)
* Redoc UI: [`http://127.0.0.1:8000/redoc/`](http://127.0.0.1:8000/redoc/)

