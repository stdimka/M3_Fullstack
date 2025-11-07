## 1. Базовая кастомизация (в `get_schema_view`)

Настраивается всё прямо в `urls.py`, в объекте `openapi.Info`:

```python
schema_view = get_schema_view(
    openapi.Info(
        title="My API",
        default_version='v2',
        description="Подробное описание API для моего проекта",
        terms_of_service="https://example.com/terms/",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
)
```

*Что изменяется:*

* заголовок, версия, описание
* контактные данные
* лицензия
* ссылка на условия использования

---

## 2. Настройки интерфейса Swagger UI

Можно добавить параметры `swagger_settings` в `settings.py`:

```python
from drf_yasg import openapi

SWAGGER_SETTINGS = {
    'DEFAULT_INFO': openapi.Info(
        title="My Project API",
        default_version='v1',
        description="Документация для REST API",
    ),
    'USE_SESSION_AUTH': False,  # убрать кнопку "Authorize"
    'VALIDATOR_URL': None,      # выключить внешнюю валидацию схемы
    'DOC_EXPANSION': 'none',    # свернуть все секции
    'OPERATIONS_SORTER': 'alpha',  # сортировка эндпоинтов по алфавиту
    'TAGS_SORTER': 'alpha',
}
```

---

## 3. Кастомные теги и порядок разделов

Можно группировать эндпоинты в разделы:

```python
@swagger_auto_schema(tags=["Пользователи"])
class UserView(APIView):
    ...
```


