Django-фильтры ведут себя по-разному в разных СУБД.

## SQlite не чувствителен к регистру символов кириллицы

### На всякий случай: мы до сих пор работаем в SQLite

Добавим ещё одну книгу:

```Python
Book.objects.create(**{
    "author": "Jane Austen",  
    "title": "Pride and Prejudice",
    "year_published": 1813
})
```

Теперь оба запроса автора по части имени 
```python
Book.objects.filter(author__icontains="Jane")
Book.objects.filter(author__icontains="jane")
```
дадут один и тот же результат:

```txt
<QuerySet [<Book: Jane Austen-Pride and Prejudice, 1813>]>
<QuerySet [<Book: Jane Austen-Pride and Prejudice, 1813>]>
```

Это на латинице.  
Но на кириллице вариант будет различаться:

```python
Book.objects.filter(author__icontains="Толстой")
Book.objects.filter(author__icontains="толстой")
```
```txt
<QuerySet [<Book: Лев Толстой-Война и мир, 1869>]>
<QuerySet []>
```
Как видим, SQLite не различает регистр кириллических букв.


### Перейдём на PostgreSQL

Дабы не усложнять жизнь тем, кто до сих пор не установил Postgres локально,  
подключим БД в контейнере:

#### 1. Добавим `docker-compose.yml`

```yaml
services:
  postgres:
    image: postgres:17
    container_name: myapp_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: myapp_db
      POSTGRES_USER: myapp_user
      POSTGRES_PASSWORD: myapp_password
    ports:
      - "5435:5432"
    volumes:
      - pg_data:/var/lib/postgresql/data

volumes:
  pg_data:
```

#### 2. Добавляем Postgres в наше виртуальное окружение:
```bash
pip install psycopg2-binary
```

#### 3. Меняем БД в `settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'myapp_db',
        'USER': 'myapp_user',
        'PASSWORD': 'myapp_password',
        'HOST': 'localhost', 
        'PORT': '5435',
    }
}
```

#### 4. Запускаем контейнер:
```bash
docker compose up --build
```

#### 5. Применяем миграции к только что созданной БД:
```bash
python manage.py migrate
```

#### 6. Запускаем Django 

#### 7. Убеждаемся, что новая БД уже содержит 11 книг:

(потому что конфигуратор настроен заполнять пустые базы книгами)
```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from myapp.models import Book
print(Book.objects.count())
```

Если всё сделано правильно, БД будет содержать 11 книг.

#### 12. Добавляем 12-ю и проделываем то же, что делали с SQLite

```Python
Book.objects.create(**{
    "author": "Jane Austen",  
    "title": "Pride and Prejudice",
    "year_published": 1813
})

print(Book.objects.filter(author__icontains="Jane"))
print(Book.objects.filter(author__icontains="jane"))
```
Латиница ожидаемо не должно принести никаких сюрпризов:

```txt
<QuerySet [<Book: Jane Austen-Pride and Prejudice, 1813>]>
<QuerySet [<Book: Jane Austen-Pride and Prejudice, 1813>]>
```

Но, и кириллица ТОЖЕ сработает правильно:

```python
print(Book.objects.filter(author__icontains="Толстой"))
print(Book.objects.filter(author__icontains="толстой"))
```

```txt
<QuerySet [<Book: Лев Толстой-Война и мир, 1869>]>
<QuerySet [<Book: Лев Толстой-Война и мир, 1869>]>
```

Как видим, PostgreSQL (в отличии от SQLite) адекватно обрабатывает кириллицу)

⚠️ ## Не забудьте вернуть всё обратно!

- Остановить Django
- Вернуть настройки БД в `settings.py`
- Удалить `pip uninstall psycopg2-binary`
- Остановить контейнер `docker compose down`
- Удалить `docker-compose.yml`
- Удалить образ и том 
```bash
docker rmi postgres:17 
docker volume rm pg_data
``` 
