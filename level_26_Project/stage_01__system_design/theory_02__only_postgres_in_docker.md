При старте проекта удобнее всего запускать Django в IDE, на локальной машине (через `python manage.py runserver`),   
а в контейнере запускать только PostgreSQL c БД.


## Схема работы локального проекта

* Postgres работает в Docker.
* Django-код работает локально на локальной машине, как обычно.
* Django подключается к БД внутри контейнера через `localhost` (`127.0.0.1`).

```
jr_project_db/
├── docker-compose.yml
├── .env
├── manage.py
├── requirements.txt
└── main/
    └── settings.py
```

---

## 1. Минимальный `docker-compose.yml`

Чтобы не хранить пароли в `docker-compose.yml` и `settings.py`, есть смысл создать `.env`:

```env
# Настройки базы данных для Django и PostgreSQL
DJANGO_DB_NAME=jr_project_db
DJANGO_DB_USER=user
DJANGO_DB_PASSWORD=password
DJANGO_DB_HOST=localhost
DJANGO_DB_PORT=5432

# Переменные для PostgreSQL контейнера
POSTGRES_DB=jr_project_db
POSTGRES_USER=user
POSTGRES_PASSWORD=password
```

Тогда `docker-compose.yml` будет выглядеть так:

```yaml
services:
  db:
    image: postgres:17
    env_file:
      - .env
    ports:
      - "5432:5432"
    volumes:
      - jr_project_postgres_db_data:/var/lib/postgresql/data

volumes:
  jr_project_postgres_db_data:
```

---

## 2. Запуск БД

```bash
docker compose up -d
```

Проверить, что БД работает:

```bash
docker ps
```

Должен быть контейнер `my_project_db`, и порт `5432` будет проброшен наружу.

---

## 3. Настрой `settings.py` для подключения к контейнеру

В `myproject/settings.py` пропиши:

```python
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DJANGO_DB_NAME", "jr_project_db"),
        "USER": os.getenv("DJANGO_DB_USER", "user"),
        "PASSWORD": os.getenv("DJANGO_DB_PASSWORD", "password"),
        "HOST": os.getenv("DJANGO_DB_HOST", "localhost"),
        "PORT": os.getenv("DJANGO_DB_PORT", "5432"),
    }
}
```

---

## 4. Проверка подключения

Выполняем миграции:

```bash
python manage.py migrate
```

Если всё настроено верно, Django подключится к контейнерной базе и выполнит миграции.

---

## 5. Работа как обычно

Теперь, после привычного запуска:

```bash
python manage.py runserver
```

Django будет:

* запущен локально (быстро, удобно, IDE-friendly);
* хранить данные в PostgreSQL контейнера;
* автоматически подключаться через `localhost:5432`.

