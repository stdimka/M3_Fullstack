## Шаг 1. Настройка `settings.py`

`main/settings.py

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

**Что это даёт:**

* `BasicAuthentication` → позволяет использовать заголовок `Authorization: Basic ...`.
* `SessionAuthentication` → для браузерного входа через сессию (необязательно для API).
* `IsAuthenticated` → по умолчанию все API требуют аутентификации.

---

## Шаг 2. Создание защищённого view

`myapp/views.py`:


```python
from rest_framework.authentication import BasicAuthentication, SessionAuthentication
from rest_framework.permissions import IsAuthenticated
```

В каждый `ViewSet` необходимо добавить:

```python
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
```

То есть:

```python
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    authentication_classes = [BasicAuthentication, SessionAuthentication]
    permission_classes = [IsAuthenticated]
```

✅ **Что это даёт:**

* Любой запрос к `/books/` или `/authors/` требует аутентификации.
* `BasicAuthentication` будет проверять заголовок `Authorization: Basic ...`.
* `SessionAuthentication` можно использовать для браузера.



Здесь `permission_classes = [IsAuthenticated]` не имеет смысла для разрешений   
(и так есть в settings.py), но полезно для улучшения читабельности

---

## Шаг 3. Проверка через curl

В терминале:

```bash
curl -u root:123 http://127.0.0.1:8000/api/authors/
```
,где 

login - `root`
password = `123`

* `-u root:123` автоматически создаёт Base64 кодировку для заголовка `Authorization: Basic ...`.
* Если логин и пароль верные → ответ:

```json
[{"id":1,"name":"Лев Толстой"},{"id":2,"name":"Фёдор Достоевский"}, 
  ... 
]
```

* Если неверные → 
`{"detail":"Invalid username/password."}`


* Попытка отправить запрос без логина и пароля: `curl http://127.0.0.1:8000/api/authors/`

`{"detail":"Authentication credentials were not provided."}`

---

## Шаг 4. Проверка Base64 вручную (по желанию)

Можно проверить, что делает `curl`:

```python
import base64

credentials = "root:123"
encoded = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")
print(encoded)
# Выведет что-то вроде: YWRtaW46MTIzNA==
```

* В заголовке запроса это будет:
  `Authorization: Basic cm9vdDoxMjM=`




