## Проверка работы backend

### 1. Загрузка БД с помощью фикстур

1. **В корне проекта создаём файл `fixtures_for_filling_database.json`**
2. **Копируем в него фикстуры**
3. **Выполняем команду `./manage.py loaddata fixtures_for_filling_database.json`**


### 2. Проверка заполнения таблиц БД

#### 2.1. Создаём суперпользователя для входа в админку

```bash

./manage.py createsuperuser
```

### 2.2. Заполняем admin.py

#### `user/admin.py`

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile


class UserProfileInline(admin.StackedInline):  # или TabularInline
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

# Сначала нужно "отрегистировать" стандартный User и зарегистрировать свой
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
```

#### `shorp/admin.py`

```python
from django.contrib import admin
from .models import Product, Order, OrderItem, Payment, Review


admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(Review)
```

### 3. Проверяем автооплату заказов пользователей

1. **Находим неоплаченный заказ. Запоминаем пользователя и сумму**
2. **Пополняем баланс пользователя на сумму >= суммы заказа**
3. **Проверяем новый статус бывшего неоплаченного заказа.