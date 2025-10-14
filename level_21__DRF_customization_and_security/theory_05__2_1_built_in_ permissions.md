# Встроенные разрешения DRF

DRF включает **7 основных встроенных разрешений**.
Они находятся в модуле `rest_framework.permissions`.

---

## 1 `AllowAny`

**Назначение:**
Разрешает доступ всем — и анонимным, и авторизованным пользователям.

**Используется, когда:**

* endpoint должен быть полностью публичным (например, регистрация, список открытых данных).

**Пример:**

```python
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

class PublicView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"message": "Доступ открыт всем!"})
```

**Особенности:**

* Полное отсутствие ограничений.
* Часто переопределяет глобальное правило (если по умолчанию стоит `IsAuthenticated`).

---

## 2 `IsAuthenticated`

**Назначение:**
Разрешает доступ **только авторизованным пользователям** (`request.user.is_authenticated == True`).

**Используется, когда:**

* нужно, чтобы доступ к API имели только вошедшие пользователи.

**Пример:**

```python
from rest_framework.permissions import IsAuthenticated

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"user": request.user.username})
```

**Особенности:**

* Проверяет, что пользователь прошёл аутентификацию (например, через JWT, сессию и т.п.).
* Анонимные пользователи получат ответ **HTTP 401 Unauthorized**.

---

## 3 `IsAdminUser`

**Назначение:**
Доступ разрешён только пользователям с `is_staff=True`.

**Используется, когда:**

* endpoint должен быть доступен только администраторам (например, управление пользователями или настройками).

**Пример:**

```python
from rest_framework.permissions import IsAdminUser

class AdminDashboard(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        return Response({"message": "Добро пожаловать, админ!"})
```

**Особенности:**

* Проверяет флаг `user.is_staff`.
* Остальные пользователи получат **HTTP 403 Forbidden**.

---

## 4 `IsAuthenticatedOrReadOnly`

**Назначение:**
Неавторизованные пользователи могут **только читать** (`GET`, `HEAD`, `OPTIONS`),
а авторизованные — выполнять любые действия.

**Используется, когда:**

* нужно сделать API общедоступным для чтения, но защищённым для изменения.

**Пример:**

```python
from rest_framework.permissions import IsAuthenticatedOrReadOnly

class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
```

**Особенности:**

* Учитывает безопасные методы: `SAFE_METHODS = ['GET', 'HEAD', 'OPTIONS']`.
* Отличный выбор для публичных блогов, форумов и т.д.

---

## 5 `DjangoModelPermissions`

**Назначение:**
Проверяет стандартные Django-права на модель (`add`, `change`, `delete`, `view`).

**Используется, когда:**

* вы хотите использовать встроенную систему прав Django.

**Пример:**

```python
from rest_framework.permissions import DjangoModelPermissions

class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [DjangoModelPermissions]
```

**Особенности:**

* Проверяет наличие у пользователя прав:

  * `view_<model>`
  * `add_<model>`
  * `change_<model>`
  * `delete_<model>`
* Права можно задать через Django Admin или `user.user_permissions.add()`.

**⚠️ Требование:**
Пользователь должен быть **аутентифицирован**.

---

## 6 `DjangoModelPermissionsOrAnonReadOnly`

**Назначение:**
Как `DjangoModelPermissions`, но анонимные пользователи могут **только читать**.

**Используется, когда:**

* часть данных должна быть публичной для чтения, но только авторизованные могут изменять по своим правам.

**Пример:**

```python
from rest_framework.permissions import DjangoModelPermissionsOrAnonReadOnly

class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
```

**Особенности:**

* Неавторизованные могут читать (`GET`).
* Авторизованные должны иметь соответствующие Django-права для действий.

---

## 7 `DjangoObjectPermissions`

**Назначение:**
Проверяет **object-level permissions** — права на *конкретный объект*, а не просто модель.

**Используется, когда:**

* доступ к объекту зависит от индивидуальных прав (например, “только автор статьи может её редактировать”).

**Пример:**

```python
from rest_framework.permissions import DjangoObjectPermissions

class ArticleDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [DjangoObjectPermissions]
```

**Особенности:**

* Проверяет права вроде `change_article` **для конкретного объекта**.
* Требует стороннюю библиотеку, например [`django-guardian`](https://django-guardian.readthedocs.io/),  
  для хранения объектных прав.
* Проверяются методы `has_permission()` и `has_object_permission()`.

---

# Сводная таблица встроенных permissions

| Разрешение                             | Уровень проверки | Для кого доступ                                     | Комментарий                                |
| -------------------------------------- | ---------------- | --------------------------------------------------- | ------------------------------------------ |
| `AllowAny`                             | request          | Всем                                                | Без ограничений                            |
| `IsAuthenticated`                      | request          | Только авторизованным                               | Проверяет `user.is_authenticated`          |
| `IsAdminUser`                          | request          | Только `is_staff`                                   | Администраторы                             |
| `IsAuthenticatedOrReadOnly`            | request          | Чтение — всем, запись — авторизованным              | Безопасные методы разрешены всем           |
| `DjangoModelPermissions`               | request          | Авторизованным с Django-правами                     | Проверка `add`, `change`, `delete`, `view` |
| `DjangoModelPermissionsOrAnonReadOnly` | request          | Анонимы — только чтение, авторизованные — по правам | Комбинированный вариант                    |
| `DjangoObjectPermissions`              | object           | Авторизованным с правами на объект                  | Используется с `django-guardian`           |

