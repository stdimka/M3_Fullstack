В DRF `TokenAuthentication` позволяет получать токен один раз и  
использовать его для всех запросов, без сессий и CSRF.

Специально инсталировать не нужно - входит в DRF.

## 1 Установка токенов

В `settings.py` убеждаемся, что `rest_framework.authtoken` подключен:

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework.authtoken',
]
```

Затем выполним миграции:

```bash
python manage.py migrate
```

---

## 2 Генерация токена для пользователя

Можно сделать через Python Console:

```bash
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()
```

```python
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

user = User.objects.get(username="root")
token, created = Token.objects.get_or_create(user=user)
print(token.key)

# f00094e3db1f60b74bed71b9b662b2d8459411ac
```

* `token.key` — это строка, которую будем использовать для аутентификации.

---

## 3 Настройка DRF для TokenAuthentication

В `settings.py`:

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.TokenAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```
---

## 4 Не забудьте убрать из views.py упоминание о `SessionAuthentication`

```python
class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]


class AuthorViewSet(viewsets.ModelViewSet):
    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
    permission_classes = [IsAuthenticated]
```


* Теперь все ViewSet по умолчанию требуют токен.

---

## 5 Использование токена через curl

### GET-запрос к API `/api/books/`:

```bash
curl -H "Authorization: Token f00094e3db1f60b74bed71b9b662b2d8459411ac" http://127.0.0.1:8000/api/books/
```

### POST-запрос для создания книги:

```bash
curl -X POST http://127.0.0.1:8000/api/books/ \
  -H "Authorization: Token f00094e3db1f60b74bed71b9b662b2d8459411ac" \
  -H "Content-Type: application/json" \
  -d '{"title":"Новая книга Льва Толстого","year_published":2025,"author":1}'
```

* Токен передаётся в заголовке `Authorization`.
* CSRF не нужен, в отличие от SessionAuthentication.
* Подходит для API-запросов из **curl, Postman, мобильных приложений**.

---

**Итог сравнения с SessionAuthentication**:

| Характеристика        | SessionAuthentication  | TokenAuthentication      |
| --------------------- | ---------------------- | ------------------------ |
| Логин через браузер   | Да, автоматом          | Нет, только токен        |
| CSRF нужен            | Да для POST/PUT/DELETE | Нет                      |
| Удобство для скриптов | Сложнее (cookie)       | Очень удобно (заголовок) |
| Срок действия         | До истечения сессии    | Пока токен действителен  |




