## Что такое CORS?

**CORS (Cross-Origin Resource Sharing)** — это механизм безопасности браузера, который контролирует,  
может ли веб-страница, загруженная с одного домена (например, `frontend.com`), делать запросы к API,  
расположенному на другом домене (например, `api.backend.com`).

Браузер по умолчанию **блокирует** такие запросы, если сервер не сообщает, что разрешает доступ извне.

---

### Например

Если отдельно запустить фронтенд (`http://localhost:3000`) и бекенд DRF (`http://localhost:8000`),   
то при попытке сделать запрос:

```js
fetch("http://localhost:8000/api/books/")
```

браузер выдаст ошибку вроде этой:

```
Access to fetch at 'http://localhost:8000/api/books/' from origin 'http://localhost:3000' has been blocked by CORS policy
```

---

## Как разрешить CORS в DRF?

Django сам по себе CORS не поддерживает, поэтому нужно установить сторонний пакет.

### 1. Установка

```bash
pip install django-cors-headers
```

---

### 2. Подключение в `settings.py`

Добавьте приложение в `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'corsheaders',
    ...
]
```

---

### 3. Добавьте middleware

`corsheaders.middleware.CorsMiddleware` должен идти **перед** `CommonMiddleware`:

```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    ...
]
```

---

### 4. Разрешение доменов

Теперь нужно указать, кому разрешено обращаться к API:

#### Вариант 1: Разрешить конкретные домены

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://myfrontend.com",
]
```

#### Вариант 2: Разрешить все домены (только для разработки!)

```python
CORS_ALLOW_ALL_ORIGINS = True
```

---

### 5. (Опционально) Разрешить передачу cookie и авторизацию

Если используется **JWT, SessionAuth или CSRF**, нужно явно разрешить передачу cookie:

```python
CORS_ALLOW_CREDENTIALS = True
```

И тогда указываем конкретные домены:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```

---

## Предзапрос (Preflight request)

Браузер иногда делает **OPTIONS-запрос** до основного запроса — чтобы проверить, разрешён ли доступ.  
`django-cors-headers` автоматически обрабатывает такие запросы.

---

## Дополнительные настройки

| Настройка                     | Описание                                               |
| ----------------------------- | ------------------------------------------------------ |
| `CORS_ALLOW_HEADERS`          | Разрешённые заголовки (по умолчанию достаточно)        |
| `CORS_EXPOSE_HEADERS`         | Какие заголовки браузер может видеть в ответе          |
| `CORS_URLS_REGEX`             | На какие URL применять CORS (например, только `/api/`) |
| `CORS_ALLOWED_ORIGIN_REGEXES` | Разрешение по шаблону (например, для поддоменов)       |

Пример:

```python
CORS_URLS_REGEX = r"^/api/.*$"
```

---

## В связке с DRF

DRF не требует отдельной настройки для CORS — всё делается на уровне Django.
Главное — middleware и настройки в `settings.py`.

---

## Минимальная рабочая настройка (для разработки)

```python
INSTALLED_APPS = [
    ...,
    'corsheaders',
    'rest_framework',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    ...
]

CORS_ALLOW_ALL_ORIGINS = True
```

