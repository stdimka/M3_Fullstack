# Создание проекта

Итак, мы 

* подробно разобрали ТЗ, 
* рассмотрели возможные сценарии (варианты) реализации проекта
* и определили базовую архитектуру нашего проекта (список приложений и маршрутов)

Мы также решили, что На этапе разработки удобнее все всего будет  
переместить в контейнеры только один элемент проекта - Базу данных.

### 1. Создаём виртуальное окружение

```bash
python3 -m venv .vevn
source .venv/bin/activate
```

### 2. Устанавливаем Django и DRF

```bash
pip install django djangorestframework
```


### 3. Создаём новый проект Django

```bash
django-admin startproject main .
```

### 4. Добавляем файлы `.env` и `docker-compose.yml`

`.env`:

```dotenv
# settings for Django and PostgreSQL
DJANGO_DB_NAME=jr_project_db
DJANGO_DB_USER=user
DJANGO_DB_PASSWORD=password
DJANGO_DB_HOST=localhost
DJANGO_DB_PORT=5435

# variables for PostgreSQL docker
POSTGRES_DB=jr_project_db
POSTGRES_USER=user
POSTGRES_PASSWORD=password
```


`docker-compose.yml`:

```yaml
services:
  db:
    image: postgres:17
    env_file:
      - .env
    ports:
      - "5435:5432"
    volumes:
      - jr_project_postgres_db_data:/var/lib/postgresql/data

volumes:
  jr_project_postgres_db_data:
```

Если всё выполнено правильно, проект должен выглядеть примерно так:

```
jr_project_db/
├── docker-compose.yml
├── .env
├── manage.py
├── requirements.txt
└── main/
    └── settings.py
```