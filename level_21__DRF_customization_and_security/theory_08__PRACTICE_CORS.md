# Шаг 1 — Установить пакет

В терминале проекта:

```bash
pip install django-cors-headers
```

# Шаг 2 — Подключить в `settings.py`

Откройте `settings.py` и внесите изменения.

1. В `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'corsheaders',
    'rest_framework',
    'myapp',  # ваш апп
    # ...
]
```

2. В `MIDDLEWARE` — **cors middleware должен идти как можно выше**,  
3. как минимум перед `CommonMiddleware`:

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',  # <- сюда
    'django.middleware.common.CommonMiddleware',
    # остальные middleware...
]
```

# Шаг 3 — Базовая конфигурация CORS (dev / prod)

### Вариант для разработки (быстро проверить — разрешить всё):

```python
CORS_ALLOW_ALL_ORIGINS = True
# Применять только к /api/ (необязательно, но удобно)
CORS_URLS_REGEX = r"^/api/.*$"
```

> ВНИМАНИЕ: `CORS_ALLOW_ALL_ORIGINS = True` — только для разработки. 
> Не использовать в продакшене!!!

### Вариант для продакшена (безопасно — явный список доменов):

```python
CORS_ALLOW_ALL_ORIGINS = False

CORS_ALLOWED_ORIGINS = [
    "https://your-frontend.com",
    "https://www.your-frontend.com",
    "http://localhost:3000",  # если локально тестируем фронтенд
]

# Применять только к API-путям (рекомендуется)
CORS_URLS_REGEX = r"^/api/.*$"
```

# Шаг 4 — Если используются cookie / session auth (например, session auth или cookie-JWT)

В простейшем случае (наш вариант) этот шаг можно вообще пропустить.

Если фронтенд должен отправлять cookie (авторизация основана на cookie), то нужно:

1. Включить передачу credentials:

```python
CORS_ALLOW_CREDENTIALS = True
```

2. В фронтенде — отправлять запросы с `credentials: 'include'`

```js
fetch("http://localhost:8000/api/...", {
  credentials: "include",
});
```

3. Настройки cookie для безопасности (особенно в продакшн — HTTPS):

```python
SESSION_COOKIE_SAMESITE = None   # чтобы браузер мог отправлять cookie cross-site
CSRF_COOKIE_SAMESITE = None

SESSION_COOKIE_SECURE = True     # в проде (требует HTTPS)
CSRF_COOKIE_SECURE = True        # в проде
```

> Примечание: по спецификации, `SameSite=None` требует установку 
> `SESSION_COOKIE_SECURE = True` (что означает: отправка возможно ТОЛЬКО по HTTPS)
> Если не указывать ничего (т.е. фактически оставить `SESSION_COOKIE_SECURE = False`)
> браузеры могут игнорировать cookie.

4. Для Django+CSRF при работе с HTTPS укажите доверенные origin:

```python
CSRF_TRUSTED_ORIGINS = ["https://your-frontend.com"]
```

# Шаг 5 — Примеры запросов и тесты

### Пример запроса из браузера (fetch)

1. Создадим стартовую страницу сервера `index.html`

```html
<!DOCTYPE html>
<html lang="ru">
    <head>
        <meta charset="UTF-8">
        <title>Тест CORS</title>
    </head>
    <body>
    <h1>Обновите браузер и проверьте консоль: </h1>
    <h2>там должен быть JSON-список с книгами</h2>
        <script>
            fetch("http://localhost:8000/api/books/")
                .then(r => r.json())
                .then(data => console.log(data))
                .catch(err => console.error("Ошибка:", err));
        </script>
    </body>
</html>
```

2. В той же папке, где будет создана эта страница выполним команду:

```bash
python -m http.server 3000
```

3. Поздравления! Мы только что запустили локальный сервер по адресу `http://localhost:3000/`.


Если мы не используем cookie (а отправляете токен в заголовке `Authorization`), достаточно:

```js
fetch("http://localhost:8000/api/books/")
  .then(r => r.json())
  .then(data => console.log(data))
  .catch(err => console.error(err));
```

Если используем cookie/session auth:

```js
fetch("http://localhost:8000/api/books/", {
  method: 'GET',
  credentials: 'include', // важно
  headers: {
    'Content-Type': 'application/json'
  }
})
.then(r => r.json())
.then(console.log)
.catch(console.error);
```

### Тест CORS с curl (проверка заголовков ответа):

Preflight (OPTIONS):

```bash
curl -i -X OPTIONS "http://localhost:8000/api/books/" \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET"
```

Обычный GET:

```bash
curl -i "http://localhost:8000/api/books/" -H "Origin: http://localhost:3000"
```

В ответе будет заголовок `access-control-allow-origin: http://localhost:3000`  
(или `*` при `CORS_ALLOW_ALL_ORIGINS=True`)   
и, если включены credentials — `Access-Control-Allow-Credentials: true`.


Примерно, вот так:
```bash
HTTP/1.1 200 OK
Date: Tue, 07 Oct 2025 13:30:49 GMT
Server: WSGIServer/0.2 CPython/3.12.10
content-length: 0
Content-Type: text/html; charset=utf-8
Vary: origin
access-control-allow-origin: *
access-control-allow-headers: accept, authorization, content-type, user-agent, x-csrftoken, x-requested-with
access-control-allow-methods: DELETE, GET, OPTIONS, PATCH, POST, PUT
access-control-max-age: 86400
X-Content-Type-Options: nosniff
Referrer-Policy: same-origin
Cross-Origin-Opener-Policy: same-origin
```

