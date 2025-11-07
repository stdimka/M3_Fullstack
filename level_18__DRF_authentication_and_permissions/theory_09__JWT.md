## 1 Установка библиотеки

Для JWT в DRF используется пакет `djangorestframework-simplejwt`:

```bash
pip install djangorestframework-simplejwt
```

---

## 2 Настройка DRF

В `settings.py` добавьте:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}
```

---

## 3 Настройка URL для получения и обновления токена

В `myapp/api_urls.py`:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views

router = DefaultRouter()
router.register(r'books', views.BookViewSet)
router.register(r'authors', views.AuthorViewSet)

urlpatterns = [
    path('', include(router.urls)),
    # Получение токена
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Обновление токена
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

---

## 4 Настройка токенов
```python

from datetime import timedelta

SIMPLE_JWT = {
    # Срок жизни access-токена
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),

    # Срок жизни refresh-токена
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),

    # Можно настроить алгоритм, rotation, blacklist и др.
    'ALGORITHM': 'HS256',
    'AUTH_HEADER_TYPES': ('Bearer',),
    'ROTATE_REFRESH_TOKENS': False,  # если True — refresh меняется каждый раз
    'BLACKLIST_AFTER_ROTATION': True,
}

```

## 5 Получение токена через curl

```bash
curl -X POST http://127.0.0.1:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "root", "password": "123"}'
```

Ответ будет примерно такой:

```json
{
  "refresh":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoicmVmcmVzaCIsImV4cCI6MTc1ODk4NTkyMCwiaWF0IjoxNzU4ODk5NTIwLCJqdGkiOiJlZjMwMzljMDllNjQ0NmQwODRmZjgxZDkyMDRiYjBkMCIsInVzZXJfaWQiOiIxIn0.BIEagMKtxmiO3l7IlejfK6w-MXDCpwgBqLHgKD87z9w",
  "access":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU4ODk5ODIwLCJpYXQiOjE3NTg4OTk1MjAsImp0aSI6IjZmMDVkMGRkZDVkYTQyNTViZjNlMDJjZTMzZjIyYWM3IiwidXNlcl9pZCI6IjEifQ.M2zCWl9LkuQ5V0jEfA9izj7AEuoVI73u59dRAV3W8B8"
}
```

* `access` — основной токен для запросов к API (короткий срок жизни).
* `refresh` — для получения нового access-токена, когда старый истёк.

---

## 6 Доступ к API с JWT

Для доступа к API через JWT нужно использовать access-токен

```bash
curl -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzU4ODk5ODIwLCJpYXQiOjE3NTg4OTk1MjAsImp0aSI6IjZmMDVkMGRkZDVkYTQyNTViZjNlMDJjZTMzZjIyYWM3IiwidXNlcl9pZCI6IjEifQ.M2zCWl9LkuQ5V0jEfA9izj7AEuoVI73u59dRAV3W8B8" \
     http://127.0.0.1:8000/api/books/
```
curl -H "Authorization: Bearer 'наш_access_токен'" \
     http://127.0.0.1:8000/api/books/

* Токен передаётся в заголовке `Authorization: Bearer <токен>`.
* CSRF не нужен, всё работает из любого клиента (curl, Postman, мобильные приложения).

---

## 7 Обновление токена

Если access-токен истёк, можно получить новый через refresh:

```bash
curl -X POST http://127.0.0.1:8000/api/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh": "ваш_refresh_токен"}'
```

Ответ вернёт новый access-токен.

---

**Плюсы JWT по сравнению с Session и TokenAuthentication:**

* Полностью stateless — сервер не хранит сессию.
* Можно использовать в мобильных приложениях и SPA без cookies.
* Безопасно, если использовать HTTPS.
* Поддержка автоматического обновления токена через refresh.

