# `ModelBackend` - система аутентификации в Django

`ModelBackend(BaseBackend)` — это **стандартная система аутентификации Django**,  
реализованная в `django.contrib.auth.backends.ModelBackend`.  
Она используется по умолчанию, если в настройках `AUTHENTICATION_BACKENDS` не указано что-то другое.

Основная задача `ModelBackend` — проверка учетных данных пользователя и управление разрешениями (permissions).

---

## Основное описание

* Работает с моделью пользователя (`AUTH_USER_MODEL`).
* Использует поля `username` (или `USERNAME_FIELD`, если переопределено) и `password`.
* Поддерживает систему **permissions** и **groups**.
* Проверяет, активен ли пользователь (`is_active`).
* Применяется в комбинации с другими backend-ами (можно указывать несколько в `AUTHENTICATION_BACKENDS`).

---

## Основные методы `ModelBackend`

### 1. `authenticate(request, username=None, password=None, **kwargs)`

* Проверяет учетные данные пользователя.
* Пытается найти пользователя по `USERNAME_FIELD`.
* Сравнивает хэш пароля.
* Возвращает объект пользователя или `None`.

Пример:

```python
from django.contrib.auth import authenticate

user = authenticate(request, username='john', password='secret')
if user is not None:
    print("Успешный вход")
else:
    print("Ошибка аутентификации")
```

---

### 2. `get_user(user_id)`

* Получает пользователя по его **ID**.
* Возвращает объект пользователя или `None`.

Используется внутри системы сессий для восстановления пользователя по ID.

---

### 3. `get_user_permissions(user_obj, obj=None)`

* Возвращает набор разрешений (**permissions**) для конкретного пользователя.
* Обычно используется системой `User.has_perm()`.

---

### 4. `get_group_permissions(user_obj, obj=None)`

* Возвращает разрешения, полученные пользователем через группы.

---

### 5. `get_all_permissions(user_obj, obj=None)`

* Комбинирует **права пользователя и группы**.
* Возвращает итоговый набор всех доступных разрешений.

---

### 6. `has_perm(user_obj, perm, obj=None)`

* Проверяет, есть ли у пользователя конкретное право доступа.
* Возвращает `True` или `False`.

Пример:

```python
if request.user.has_perm('app.change_model'):
    print("Можно редактировать объект")
```

---

### 7. `has_module_perms(user_obj, app_label)`

* Проверяет, есть ли у пользователя **любое разрешение** для указанного приложения.

Пример:

```python
if request.user.has_module_perms('blog'):
    print("У пользователя есть права на приложение blog")
```

---

## Как подключить

По умолчанию `ModelBackend` УЖЕ включен. Но если нужно указать явно:

```python
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]
```

Так поступают в случае, если используется несколько backend-ов, например, для аутентификации по email или LDAP.

