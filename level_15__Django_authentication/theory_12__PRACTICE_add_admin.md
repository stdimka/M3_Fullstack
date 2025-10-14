## Настройка админки для новых моделей

Сейчас (по умолчанию) доступна только модель `User`.


### 1 Создаём UserProfile `admin.py`

`accounts/admin.py`

```python
from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import UserProfile

admin.site.register(UserProfile)
```

Есть возможность редактировать отдельно `User` и `UserProfile`
---

### 2 Создаём инлайн для UserProfile

```python
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
```

* `StackedInline` — вертикальное отображение полей.
* `can_delete = False` — нельзя удалить профиль через инлайн, создаётся автоматически.

---

### 3 Расширяем UserAdmin

```python
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
```

---

### 4 Регистрируем User с новым админом

```python
# Снимаем стандартную регистрацию User и регистрируем наш вариант
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
```

---


* В админке Django на стандартной странице `User` появился блок **Profile** с полями `phone` и `is_verified`.
* Профиль редактируется прямо вместе с пользователем.
* Новый пользователь автоматически получает `UserProfile` благодаря сигналам `post_save`.


