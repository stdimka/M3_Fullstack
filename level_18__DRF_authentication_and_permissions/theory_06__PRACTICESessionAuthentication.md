В `settings.py` должен быть блок `REST_FRAMEWORK` (уже есть):

```python
REST_FRAMEWORK = {
    # Глобально включаем аутентификацию через сессии Django
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
    ],
    # Глобально требуем авторизацию для всех API
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

### Что это даёт:

1. **SessionAuthentication** применяется ко всем ViewSet и APIView автоматически.
2. **IsAuthenticated** запрещает доступ анонимным пользователям по умолчанию.
3. Всё ещё можно переопределять аутентификацию или права для конкретного ViewSet через `authentication_classes` и `permission_classes`.

---
## Как отправлять запросы? 

### 1. Работа через браузер

**SessionAuthentication** использует стандартные **сессии Django**, к
оторые создаются при логине пользователя (через `/admin/login/` или кастомный логин).

* Когда вы залогинены в браузере, Django хранит вашу сессию в cookie (обычно `sessionid`).
* DRF считывает эту сессию из cookie и понимает, что вы уже авторизованы.
* **То есть для браузера, где вы уже залогинены, дополнительные логины для API не нужны.**

Примеры:

1. Вы зашли на сайт `/admin/` и вошли.
2. Теперь открываете API `/api/books/` в том же браузере — DRF видит вашу сессию и позволяет делать запросы без повторного ввода логина.

### 2. Работа вне браузера (Postman или curl)

⚠️ Если вы делаете запросы через **Postman или curl**, cookie сессии нужно передавать вручную, иначе доступ будет запрещён.

---

### 2.1. Получаем страницу логина и сохраняем cookie + CSRF

```bash
curl -c cookies.txt -s http://127.0.0.1:8000/accounts/login/ > login.html
```

* `-c cookies.txt` — сохраняем cookie, включая `csrftoken`.
* Сохраняем HTML в `login.html`, чтобы вытащить CSRF-токен.

---

### 2.2. Извлекаем CSRF-токен

В `login.html` есть строка типа:

```html
    <input type="hidden" name="csrfmiddlewaretoken" value="jJsIX0xixFMn1q5HoCw2iK6f9uQnWuTBOxOYpcezdAjhp4HQjtndWizpKOZZTBne">
```

Токен `"jJsIX0xixFMn1q5HoCw2iK6f9uQnWuTBOxOYpcezdAjhp4HQjtndWizpKOZZTBne"` нужно использовать в следующем запросе.

---

### 2.3. Отправляем POST-запрос с логином и CSRF

```bash
curl -b cookies.txt -c cookies.txt -X POST http://127.0.0.1:8000/accounts/login/ \
  -d "username=root&password=123&csrfmiddlewaretoken=jJsIX0xixFMn1q5HoCw2iK6f9uQnWuTBOxOYpcezdAjhp4HQjtndWizpKOZZTBne" \
  -H "Referer: http://127.0.0.1:8000/accounts/login/"
```

* `-b cookies.txt` — используем ранее сохранённые cookie.
* `-c cookies.txt` — обновляем cookie сессии (`sessionid`).
* `-H "Referer: ..."` — Django проверяет Referer для CSRF.

После этого в `cookies.txt` появится ваш `sessionid`, который можно использовать для **SessionAuthentication** на API:

```bash
curl -b cookies.txt http://127.0.0.1:8000/api/books/
```

---

## 3. Логин через DRF API

Есть более простой способ тестировать **SessionAuthentication** в DRF через curl, **без возни с CSRF**:  
сделать **логин через DRF API** (например, используя `rest_framework` `LoginView`), а не через стандартный `/accounts/login/`.

---

### 3.1. Настроим DRF login view

В `myapp/api_urls.py` добавим:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import authenticate, login

from . import views

router = DefaultRouter()
router.register(r'books', views.BookViewSet)
router.register(r'authors', views.AuthorViewSet)

# Простейший DRF login для SessionAuthentication
@api_view(['POST'])
def drf_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)  # создаётся сессия
        return Response({"detail": "Logged in successfully"})
    return Response({"detail": "Invalid credentials"}, status=400)

urlpatterns = [
    path('', include(router.urls)),
    path('api-login/', drf_login),  # наш DRF login
]
```

---

### 3.2. Логин через curl

```bash
# Сохраняем cookie
curl -c cookies.txt -X POST http://127.0.0.1:8000/api-login/ \
  -d "username=root&password=123"
```

* В ответ получите JSON `{"detail":"Logged in successfully"}`.
* В `cookies.txt` появится `sessionid`.

---

### 3.3. Доступ к API через curl с SessionAuthentication

```bash
curl -b cookies.txt http://127.0.0.1:8000/books/
```

* Теперь сервер видит сессию и считает вас авторизованным.
* **CSRF проверка не требуется**, потому что это API-запрос, а не форма Django.

---

💡 **Плюсы такого подхода:**

1. Не нужно парсить CSRF из HTML.
2. Можно тестировать API через curl/Postman легко.
3. Сохраняется логика SessionAuthentication — в браузере тоже будет работать.

