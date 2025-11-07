
## 1.2. Глобальные уровни применения `permissions`

Глобальные разрешения действуют на весь проект (или на все API-вью) сразу,   
без явного указания в каждом классе.

Основные варианты:

1. В `settings.py` (через `REST_FRAMEWORK`)
2. Через Middleware (уровень запроса до DRF)
3. Через базовый класс View (например, `BaseAPIView`)
4. Через кастомный DRF Permission класс (универсальный фильтр)

---

### 1.2.1. В `settings.py` — глобальные разрешения DRF

Это основной и рекомендуемый способ задать базовый уровень доступа ко всем API-вью DRF.

```python
# settings.py

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',  # все запросы требуют аутентификации
    ],
}
```

Теперь **все** вью (APIView, ViewSet, GenericView и т.д.) по умолчанию используют `IsAuthenticated`,  
если у них явно не переопределено `permission_classes`.

#### Примеры других глобальных настроек:

```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',         # всё открыто
        # 'rest_framework.permissions.IsAdminUser',    # только для админов
        # 'rest_framework.permissions.DjangoModelPermissions',  # на основе модели
    ],
}
```

⚠️ ВАЖНО ПОМНИТЬ!  
Локальные настройки `permission_classes` **перекрывают глобальные**!

---

### 1.2.2. Middleware — проверки до попадания в DRF

**Middleware** — это более "низкий" уровень, чем DRF.  
Она срабатывает **до того**, как Django передаст управление в DRF view.

Подходит, если нужно ограничить доступ по глобальным параметрам, независимо от конкретной вью:
- по пути, 
- IP клиента, 
- User-Agent 
  - тип клиента (браузер, бот, приложение), 
  - платформу (Windows, Android, iOS и т. д.) 
  - и т.д.
- домену 
- заголовку

#### Пример:

```python
# core/middleware.py
from django.http import JsonResponse

class BlockAnonymousAPIMiddleware:
    """Блокирует анонимных пользователей для всех /api/ путей."""
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/') and not request.user.is_authenticated:
            return JsonResponse({'detail': 'Authentication required'}, status=403)
        return self.get_response(request)
```

Добавляем в `settings.py`:

```python
MIDDLEWARE = [
    ...,
    'core.middleware.BlockAnonymousAPIMiddleware',
]
```

Можно добавить дополнительную логику, например:

* блокировать доступ в нерабочее время;
* проверять наличие API-ключа в заголовках;
* логировать попытки доступа.

> ⚠️ ВАЖНО: Middleware действует **на все запросы**, включая не-DRF маршруты.   
> Поэтому, будьте ПРЕДЕЛЬНО аккуратны с фильтрацией `request.path`!

---

### 2.3. Базовый класс View (через наследование)

Идея: создать свой базовый класс (`BaseAPIView` и / или `BaseViewSet`), 
от которого будут наследоваться все остальные вью-классы.

```python
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

class BaseAPIView(APIView):
    """Базовая вью со стандартными разрешениями."""
    permission_classes = [IsAuthenticated]
```

Теперь все наследники автоматически будут иметь разрешения родительского класса:

```python
class UserListView(BaseAPIView):
    def get(self, request):
        ...
```

---

### 2.4. Глобальные permission-классы (универсальный фильтр)

Можно создать **кастомный permission**, который проверяется *всегда*, и подключить его глобально в `settings.py`.

#### Пример кастомного permission-а:

```python
from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

class BlockBannedUsers(BasePermission):
    """Запрещает доступ пользователям с флагом is_banned."""
    def has_permission(self, request, view):
        if request.user and getattr(request.user, 'is_banned', False):
            raise PermissionDenied("Ваш аккаунт заблокирован.")
        return True
```

И включить его глобально:

```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'core.permissions.BlockBannedUsers',
        'rest_framework.permissions.IsAuthenticated',
    ],
}
```

Здесь **оба класса** применяются: пользователь должен быть аутентифицирован и не заблокирован.

---

### 2.5. Через Django permissions (уровень ORM)

На уровне моделей можно объявить разрешения, которые потом будут использоваться глобально через DRF-permission классы:

```python
class MyModel(models.Model):
    ...
    class Meta:
        permissions = [
            ('can_view_reports', 'Может просматривать отчёты'),
        ]
```

Если в настройках DRF указать:

```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissions',
    ],
}
```

то пользователю понадобится соответствующее Django-разрешение (`user.has_perm(...)`) для выполнения операций над моделью.

> ⚠️ Работает только для ViewSet, у которых есть `queryset` и `model`.

---

## Итого: уровни глобальных разрешений

| Уровень                                          | Пример реализации                               | Когда использовать                 |
| ------------------------------------------------ | ----------------------------------------------- | ---------------------------------- |
| **`settings.py` (`DEFAULT_PERMISSION_CLASSES`)** | Задаёт базовые права для всех API               | Основной и рекомендуемый способ    |
| **Middleware**                                   | Проверка пути, токена, IP, и т.д. до DRF        | Для фильтрации всего трафика /api/ |
| **Базовый класс View**                           | Наследование от `BaseAPIView`                   | Для корпоративных шаблонов API     |
| **Глобальный кастомный permission**              | Проверяет общее условие (например, `is_banned`) | Для общих логик безопасности       |
| **Django Model Permissions**                     | Использует `user.has_perm()`                    | Для ролевой модели доступа (RBAC)  |

