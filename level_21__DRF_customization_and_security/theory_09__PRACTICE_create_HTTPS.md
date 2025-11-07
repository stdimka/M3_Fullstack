## Цель

* Django + DRF контейнер (`web`)
* Nginx контейнер (`nginx`) с SSL
* Самоподписанный сертификат (`localhost`)
* Всё работает через `https://127.0.0.1`

---

## Структура проекта

```
project/
│
├── docker-compose.yml
├── .env
│
├── nginx/
│   ├── nginx.conf
│   └── certs/
│       ├── localhost.pem
│       └── localhost-key.pem
│
└── web/
    ├── Dockerfile
    ├── requirements.txt
    ├── manage.py
    ├── db.sqlite3
    │
    ├── accounts/
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py
    │   ├── tests.py
    │   └── views.py
    │
    ├── myapp/
    │   ├── __init__.py
    │   ├── admin.py
    │   ├── apps.py
    │   ├── models.py
    │   ├── tests.py
    │   └── views.py
    │
    └── main/
        ├── __init__.py
        ├── asgi.py
        ├── settings.py
        ├── urls.py
        └── wsgi.py

```

---

## 1 Создание самоподписанного сертификата

В терминале корня выполняем скрипт:

```bash
cd nginx
mkdir certs
cd certs

openssl req -x509 -nodes -days 365 \
  -newkey rsa:2048 \
  -keyout localhost.key \
  -out localhost.crt \
  -subj "/C=RU/ST=Local/L=Local/O=Local/OU=Dev/CN=localhost"
```

После этого появятся два файла:

```
localhost.crt
localhost.key
```

---

## 2 Dockerfile для Django (`web/Dockerfile`)

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "main.wsgi:application", "--bind", "0.0.0.0:8000"]
```


---

## 3 Настройка Nginx (`nginx/nginx.conf`)

```nginx
events {}

http {
    # --- upstream для Django ---
    upstream django {
        server web:8000;  # Django-контейнер
    }

    # --- HTTP: редиректим на HTTPS ---
    server {
        listen 80;
        server_name localhost;

        # Всегда редирект на HTTPS с фиксированным host
        return 301 https://localhost$request_uri;
    }

    # --- HTTPS основной сервер для localhost ---
    server {
        listen 443 ssl;
        server_name localhost;

        ssl_certificate     /etc/nginx/certs/localhost.crt;
        ssl_certificate_key /etc/nginx/certs/localhost.key;

        # Проксирование всех запросов к Django
        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
        }

    }

    # --- Fallback HTTPS сервер для любых других host ---
    server {
        listen 443 ssl default_server;
        server_name _;

        ssl_certificate     /etc/nginx/certs/localhost.crt;
        ssl_certificate_key /etc/nginx/certs/localhost.key;

        location / {
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto https;
        }

        location /static/ {
            alias /app/staticfiles/;  # Исправьте здесь на staticfiles
        }
    }
}
```

---

## 4 docker-compose.yml

```yaml
services:
  web:
    build: ./web
    container_name: django_web
    command: >
      sh -c "python manage.py collectstatic --noinput &&
             python manage.py runserver 0.0.0.0:8000"
    volumes:
      - ./web:/app
    expose:
      - "8000"
    env_file:
      - .env

  nginx:
    image: nginx:latest
    container_name: nginx_ssl
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/certs:/etc/nginx/certs:ro
      - ./web/staticfiles:/app/staticfiles:ro
    depends_on:
      - web
```

---

## 5 Django настройки

В `settings.py`:

```python
SECURE_SSL_REDIRECT = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# при разработке:
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```
В `requirements.txt` добавляем

```txt
gunicorn>=21.2
```
---

## 6 Запуск

```bash
docker compose up --build
```

В браузере:

* `https://localhost` — работает Django (через DRF или admin)
* `http://localhost` — автоматически перенаправляет на HTTPS


Браузер покажет предупреждение «Ненадёжный сертификат» — это нормально (так как он самоподписанный).

