## 2. Настройка GraphQL в Django

### 2.1 Установка необходимых пакетов

Для Django существует готовый пакет **graphene-django**, который интегрирует GraphQL с моделями.

```bash
pip install graphene-django
```

> Этот пакет позволяет:
>
> * Автоматически генерировать типы GraphQL из моделей Django (`DjangoObjectType`)
> * Настроить единую точку входа `/graphql/`
> * Использовать встроенный интерактивный интерфейс GraphiQL для тестирования запросов

---

### 2.2 Создаём файл `myapp/schema.py`

В корне приложения `myapp` создайте файл:

```
myapp/schema.py
```

Там будет описываться вся схема GraphQL (типы, запросы, мутации).

---

### 2.3 Подключение в `settings.py`

Добавьте `graphene_django` в список приложений:

```python
INSTALLED_APPS = [
    ...,
    'graphene_django',
]
```

Затем указываем путь к файлу схема, где будет ваша схема:

```python
GRAPHENE = {
    'SCHEMA': 'myapp.schema.schema'  # путь к файлу schema.py, который создадим
}
```

---

### 2.4 Подключение GraphQL к URL

В `myapp/urls.py` добавьте маршрут:

```python
from graphene_django.views import GraphQLView

urlpatterns += [
    path("graphql/", GraphQLView.as_view(graphiql=True)),  # graphiql=True включит интерактивный интерфейс
]
```

* `/graphql/` — единая точка входа для всех запросов и мутаций.
* `graphiql=True` — позволяет открывать браузерную консоль GraphiQL, где можно писать запросы, видеть подсказки и получать ответ JSON.

---

### 2.5 Заполняем файл `myapp/schema.py`


```python
import graphene

# Минимальный Query для проверки
class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Привет, GraphQL!")

# Создаём объект схемы
schema = graphene.Schema(query=Query)
```

#### Что здесь происходит?

1. Мы создаём **корневой объект Query** с одним полем `hello`.
2. `default_value="Привет, GraphQL!"` — GraphQL будет возвращать эту строку, когда мы её запрашиваем.
3. Схема создаётся через `graphene.Schema(query=Query)`.

---


### 2.6 Проверка работы

1. Запускаем сервер Django:

```bash
python manage.py runserver
```

2. Переходим в браузере на:

```
http://127.0.0.1:8000/graphql/
```

3. В консоли GraphiQL выполните запрос:

```graphql
query {
  hello
}
```

4. Ожидаемый ответ:

```json
{
  "data": {
    "hello": "Привет, GraphQL!"
  }
}
```
---

### 2.7 Итог

После выполнения пункта #2:

* GraphQL подключён к проекту.
* Есть точка входа `/graphql/` с интерфейсом GraphiQL.
* Куда отправлен первы запрос и получен первый ответ


