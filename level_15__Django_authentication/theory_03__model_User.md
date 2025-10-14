# User - стандартная модель пользователей в Django.

## 1 Модель `User` и её таблица `auth_user`

* В Django по умолчанию есть встроенная модель пользователя — `django.contrib.auth.models.User`.
* Модель `User` — это **Python-класс**, который описывает ORM-модель.
* Соответственно, её таблица в базе данных называется `auth_user`.
* Структура таблицы `auth_user`:

| Поле           | Тип        | Примечание                |
|----------------| ---------- |---------------------------|
| `id`           | integer PK | Автоинкремент             |
| `password`     | varchar    | Хеш пароля                |
| `last_login`   | datetime   | Последний вход            |
| `is_superuser` | boolean    | Суперпользователь         |
| `username`     | varchar    | Логин (обязательное поле) |
| `first_name`   | varchar    | Имя                       |
| `last_name`    | varchar    | Фамилия                   |
| `email`        | varchar    | Email                     |
| `is_staff`     | boolean    | Для админки               |
| `is_active`    | boolean    | Активен ли                |
| `date_joined`  | datetime   | Дата создания             |

---

## 2 Как добавить поля в модель User?

### 2.1. UserProfile (OneToOne)

Создаём отдельную модель профиля, которая связана с `User` через `OneToOneField`.

```python
from django.contrib.auth.models import User
from django.db import models

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
```

* **Плюсы:**

  * Не ломает стандартную модель User.
  * Легко добавить новые поля без переписывания авторизации.
* **Минусы:**

  * Нужно обращаться через `user.profile`.
  * Немного больше кода при доступе к полям.

---

### 2.2. CustomUser (на основе AbstractUser)

Наследуем `AbstractUser` и добавляем свои поля напрямую.

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
```

* **Плюсы:**

  * Можно использовать все стандартные возможности `User`.
  * Поля доступны напрямую (`user.bio`).

* **Минусы:**

  * Нужно создавать до первой миграции базы, нельзя просто "подключить" к существующей модели.

* **Важно:** В `settings.py` добавить:

```python
AUTH_USER_MODEL = 'myapp.CustomUser'
```

---

### 2.3. CustomUser (на основе AbstractBaseUser)

Наследуем `AbstractBaseUser` и создаём модель пользователя с нуля.

```python
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser):
    email = models.EmailField(unique=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
```

* **Плюсы:**

  * Полный контроль над моделью пользователя.
  * Можно изменить поле логина (например, email вместо username).
* **Минусы:**

  * Сложнее в настройке.
  * Нужно реализовать менеджеры, методы и права вручную.

---

### 2.4. Вывод

* Если нужно **добавить пару полей к стандартному User** → лучше **UserProfile (OneToOne)**.
* Если нужно **модифицировать User с сохранением стандартного поведения** → лучше **AbstractUser**.
* Если нужен **полностью кастомный пользователь (с email вместо username, кастомные методы)** → тогда **AbstractBaseUser**.

| Вариант                         | Как реализуется                                          | Доступ к новым полям            | Сложность настройки                                  | Сохранение стандартного поведения User                   | Плюсы                                                                           | Минусы                                                                  | Когда использовать                                                                                       |
|---------------------------------| -------------------------------------------------------- | ------------------------------- | ---------------------------------------------------- | -------------------------------------------------------- | ------------------------------------------------------------------------------- | ----------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `UserProfile (OneToOne)`        | Отдельная модель с `OneToOneField` на стандартный `User` | Через `user.profile.field_name` | Очень просто                                         | Полностью сохраняется                                    | Легко подключить к существующей базе, не трогая стандартный `User`              | Нужно обращаться через `profile`, больше кода при доступе к полям       | Добавить пару полей к существующему User без изменения модели                                            |
| `CustomUser (AbstractUser)`     | Наследуем `AbstractUser` и добавляем поля                | Прямо: `user.field_name`        | Средняя, нужно указать `AUTH_USER_MODEL` до миграций | Сохраняется стандартная логика (пароли, группы, админка) | Поля в основной модели, прямой доступ, сохраняется стандартная функциональность | Нельзя подключать к уже существующей базе без миграций                  | Добавить новые поля и использовать стандартный User с минимальными изменениями                           |
| `CustomUser (AbstractBaseUser)` | Наследуем `AbstractBaseUser`, создаём модель с нуля      | Прямо: `user.field_name`        | Сложно, нужно реализовать менеджер, методы, права    | Частично, нужно реализовать вручную                      | Полный контроль над моделью, можно менять поле логина, уникальные требования    | Сложная настройка, больше кода, ручная реализация аутентификации и прав | Полностью кастомный пользователь, когда нужны специфические требования (например, email вместо username) |


#### Уточнение по изменению админки для `UserProfile (OneToOne)`  


##### 1. User уже имеет админку "из коробки"

* Все стандартные поля (`username`, `email`, `is_staff`, `is_superuser`, группы и права) уже доступны.
* Ничего настраивать не нужно. 

---

##### 2. UserProfile (OneToOne)

* Поскольку `UserProfile` — отдельная модель, её нужно создать отдельно и самостоятельно.
* И чтобы удобно редактировать профиль вместе с пользователем, обычно делают `InlineModelAdmin`:

```python
from django.contrib import admin
from django.contrib.auth.models import User
from .models import UserProfile

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class UserAdmin(admin.ModelAdmin):
    inlines = (UserProfileInline,)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
```

* После этого при открытии пользователя в админке будет возможность редактировать и поля профиля.

