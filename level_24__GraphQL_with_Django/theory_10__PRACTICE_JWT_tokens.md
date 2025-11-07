## Шаг 1. Установка необходимых пакетов

Для работы с JWT в GraphQL удобно использовать пакет [`graphql-jwt`](https://github.com/flavors/django-graphql-jwt). Он интегрируется с `graphene-django`.

```bash
pip install django-graphql-jwt
```

Если нужен токен обновления, устанавливает пакет с опцией `[refresh_token]`
(Но тогда понадобятся и дополнительные настройки)

```bash
pip install django-graphql-jwt[refresh_token]
```

---

## Шаг 2. Настройка Django settings

В `settings.py` нужно добавить JWT аутентификацию в GraphQL.

```python
GRAPHENE = {
    "SCHEMA": "myapp.schema.schema",
    "MIDDLEWARE": [
        "graphql_jwt.middleware.JSONWebTokenMiddleware",
    ],
}

AUTHENTICATION_BACKENDS = [
    "graphql_jwt.backends.JSONWebTokenBackend",
    "django.contrib.auth.backends.ModelBackend",
]

from datetime import timedelta

GRAPHQL_JWT = {
    "JWT_ALLOW_REFRESH": True,   #  JWT ключ "освежатся" при каждом новом использовании
    "JWT_EXPIRATION_DELTA": timedelta(hours=1),  # здесь токен живёт 1 час
}

```

---

## Шаг 3. Добавление мутаций для работы с JWT

Создадим отдельный файл для мутаций JWT, например `your_app/schema/mutations.py`:

```python
import graphene
import graphql_jwt

class AuthMutations(graphene.ObjectType):
    # Существующие мутации
    ...
    # добавляем JWT-мутации
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()

```

* `token_auth` — получение токена по логину и паролю
* `verify_token` — проверка действительности токена
* `refresh_token` — обновление токена

---

## Шаг 4. Требуем, чтобы все API запросы были только авторизованными


```python
from django.contrib.auth.decorators import login_required
from django.urls import path
from graphene_django.views import GraphQLView

urlpatterns = [
    path("graphql/", login_required(GraphQLView.as_view(graphiql=False))),
]

```

---

## Шаг 5. Получение токена для пользователя `root`

### Запрос (mutation):

```graphql
mutation {
  tokenAuth(username: "root", password: "123") {
    token
    payload
  }
}
```

### Ответ (пример):

```json
{
  "data": {
    "tokenAuth": {
      "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InJvb3QiLCJleHAiOjE3NjIwMzM4MzksIm9yaWdJYXQiOjE3NjIwMzAyMzl9.fn2oHLWMTXUxAbl6b8g0FW3LOvoz9zQfY_FrqBZvAc0",
      "payload": {
        "username": "root",
        "exp": 1762033839,
        "origIat": 1762030239
      }
    }
  }
}
```

---

## Шаг 6. Тестируем JWT

Для чистоты эксперимента прежде надо разлогиниться на сайте!

В заголовок добавляем:

```json
{
  "Authorization": "JWT eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VybmFtZSI6InJvb3QiLCJleHAiOjE3NjIwMzM4MzksIm9yaWdJYXQiOjE3NjIwMzAyMzl9.fn2oHLWMTXUxAbl6b8g0FW3LOvoz9zQfY_FrqBZvAc0"
}
```

### Пример защищённого запроса:

```graphql
query {
  allBooks {
    id
    title
  }
}
```

В противном случае (без токена) получим ответ:

```json
{
  "errors": [
    {
      "message": "Неавторизованный пользователь",
      "locations": [
        {
          "line": 2,
          "column": 3
        }
      ],
      "path": [
        "allBooks"
      ]
    }
  ],
  "data": {
    "allBooks": null
  }
}
```

