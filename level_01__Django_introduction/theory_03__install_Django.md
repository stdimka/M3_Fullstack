# Установка  Django

[https://docs.djangoproject.com/en/dev/intro/install/](https://docs.djangoproject.com/en/dev/intro/install/)

## 1. Создаём виртуальное окружение

В выбранной директории создаём каталог `my_website`  
Далее, в нём же создаём виртуальное окружение:

```bash
mkdir my_website
cd my_website
python3.12 -m venv .venv
source .venv/bin/activate
```

Результат - появление (.venv) в начале приглашения командной строки.

## 2. Устанавливаем Django

```bash
pip install Django
```

## 3. Создаём `requirements.txt`

Хорошая практика - сразу же добавлять свеже-установленный пакет в `requirements.txt`:  
```bash
pip freeze > requirements.txt
```

## 4. Создаём Django проект

#### Стандартный подход:
```bash
django-admin startproject mysite
```

#### Мой вариант

```bash
django-admin startproject main .
```

Если установлена утилита `tree`, можно посмотреть результат:
```
tree
.
└── my_website
    ├── main
    │   ├── asgi.py
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── manage.py
    └── requirements.txt
```
(если не установлена, то запускаем `sudo apt install tree`)


## Запуск проекта

Проверяем список доступных команд:
```
./manage.py
```
Результат:
```bash

Type 'manage.py help <subcommand>' for help on a specific subcommand.

Available subcommands:

[auth]
    changepassword
    createsuperuser

[contenttypes]
    remove_stale_contenttypes

[django]
    check
    compilemessages
    createcachetable
    dbshell
    diffsettings
    dumpdata
    flush
    inspectdb
    loaddata
    makemessages
    makemigrations
    migrate
    optimizemigration
    sendtestemail
    shell
    showmigrations
    sqlflush
    sqlmigrate
    sqlsequencereset
    squashmigrations
    startapp
    startproject
    test
    testserver

[sessions]
    clearsessions

[staticfiles]
    collectstatic
    findstatic
    runserver
```

Сразу запускаем сервер:

```bash
./manage.py runserver
```
и далее по подсказкам выполняем то, что советуют