## 1. Основные принципы работы BasicAuthentication

### 1.1. Идея:
Логин и пароль пользователя** передаются в HTTP-заголовке при КАЖДОМ запросе.

### 1.2. Как работает?:

1. Клиент хочет обратиться к API.
2. Он передаёт заголовок:

```
Authorization: Basic <base64(username:password)>
```

3. Сервер получает этот заголовок, декодирует Base64 → получает `username:password`.
4. Проверяет логин и пароль через стандартную аутентификацию Django (`User.check_password`).
5. Если всё верно → `request.user` содержит пользователя. Если нет → 401 Unauthorized.

**Особенности:**

* Простой метод, не требует токенов.
* Статический: каждый запрос содержит логин и пароль.
* Требует **HTTPS**, иначе пароль передаётся в открытом виде (base64 — не шифрование!).
* Обычно используется для тестирования или внутренних API, но не для публичных сервисов.

### 1.3. Пример реализации в Python библиотеке `base64`

Base64 — это способ кодирования данных в текстовый формат. 
Он не шифрует, а просто преобразует данные в последовательность символов из набора:

```
A–Z, a–z, 0–9, +, / 
```

и знак `=` используется для выравнивания длины.

В контексте **Basic Authentication** в DRF:

```
Authorization: Basic <base64(username:password)>
```

* Берётся строка вида `username:password`
* Кодируется в Base64
* Получается что-то вроде: `dXNlcm5hbWU6cGFzc3dvcmQ=`
* Этот результат вставляется в заголовок `Authorization`

Пример:

```python
import base64

credentials = "admin:1234"
encoded = base64.b64encode(credentials.encode("utf-8"))
print(encoded.decode("utf-8"))  # dGVzdDoxMjM0
```

ВАЖНО! **Base64 не защищает пароль**, он просто делает его безопасным для передачи как текст.  
Поэтому для реальной безопасности нужен HTTPS.


---

## 2. Пример реализации BasicAuthentication в DRF

### 2.1. Настройка в `settings.py`

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.BasicAuthentication',
        'rest_framework.authentication.SessionAuthentication',  # опционально
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

### 2.2. Создание защищённого view

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class HelloView(APIView):
    permission_classes = [IsAuthenticated]  # Только аутентифицированные пользователи

    def get(self, request):
        username = request.user.username
        return Response({"message": f"Hello, {username}!"})
```

### 2.3. Пример запроса с Basic Auth

Используя **curl**:

```bash
curl -u username:password http://127.0.0.1:8000/api/hello/
```

* `-u username:password` автоматически формирует заголовок `Authorization: Basic ...`.
* Если логин и пароль правильные → вернётся JSON `{"message": "Hello, username!"}`.
* Если неверные → 401 Unauthorized.


