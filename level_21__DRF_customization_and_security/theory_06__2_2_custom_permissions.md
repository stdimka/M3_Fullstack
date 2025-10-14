# Кастомные разрешения в DRF

**Кастомные разрешения (permissions)** — это классы, унаследованные от  
`rest_framework.permissions.BasePermission`, которые позволяют реализовать **свою бизнес-логику доступа**.

---

## 1. Когда нужны кастомные permissions

Создаются, если встроенных недостаточно.  

Типичные случаи:

| Ситуация                           | Пример кастомной логики                                             |
|------------------------------------| ------------------------------------------------------------------- |
| Доступ только владельцу объекта    | Пользователь может редактировать только свои посты                  |
| Разрешение зависит от роли         | Только модераторы могут удалять комментарии                         |
| Доступ ограничен по времени        | Можно редактировать запись только в течение 24 часов после создания |
| Комбинированные условия            | Только авторизованные и при этом владелец или админ                 |
| Уровень доступа по статусу объекта | Например, редактировать можно только пока статус — “draft”          |

---

## 2. Базовая структура кастомного разрешения

Любой permission — это класс с методами:

* `has_permission(self, request, view)` — проверка на уровне **всего запроса** (view-level)
* `has_object_permission(self, request, view, obj)` — проверка на уровне **объекта** (object-level)

**Пример шаблона:**

```python
from rest_framework.permissions import BasePermission, SAFE_METHODS

class CustomPermission(BasePermission):
    message = "Доступ запрещён."  # Сообщение для 403 Forbidden

    def has_permission(self, request, view):
        # Проверка на уровне представления
        return True  # или любая логика

    def has_object_permission(self, request, view, obj):
        # Проверка на уровне конкретного объекта
        return True  # или любая логика
```

---

## 3. Основные типы кастомных permissions

### 3.1. По владельцу (Owner-based)

Разрешить доступ только владельцу объекта.

```python
from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    message = "Вы не владелец этого объекта."

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
```

Использование:

```python
class BookDetailView(RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated, IsOwner]
```

---

### 3.2. По роли пользователя

Разрешить действие только пользователям с определённой ролью.

```python
class IsModerator(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, 'role') and request.user.role == 'moderator'
```

---

### 3.3. По времени (ограничение по дате/времени)

```python
from datetime import timedelta
from django.utils import timezone

class IsEditableFor24Hours(BasePermission):
    message = "Редактировать можно только в течение 24 часов после создания."

    def has_object_permission(self, request, view, obj):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return True
        return timezone.now() - obj.created_at < timedelta(hours=24)
```

---

### 3.4. Комбинированные условия (роль + владение)

```python
class IsOwnerOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user or request.user.is_staff
```

---

### 3.5. Только для чтения

Часто используется, чтобы сделать объект доступным только для просмотра.

```python
from rest_framework.permissions import BasePermission, SAFE_METHODS

class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS
```

---

## 4. Как использовать кастомный permission

Указывается точно так же, как встроенный:

```python
class ArticleViewSet(ModelViewSet):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrAdmin]
```

---

## 5. Можно комбинировать permissions

DRF применяет **все классы из списка `permission_classes`**.
Если **хотя бы один** вернул `False` → доступ запрещён.

Можно создавать **цепочки условий** через наследование или композицию.

Пример композиции:

```python
permission_classes = [IsAuthenticated, IsOwner]
```

или через комбинированный класс:

```python
class IsAuthenticatedOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
```

---

## 6. Где работают кастомные permissions

| Уровень | Метод                     | Когда вызывается                  | Пример                               |
|---------| ------------------------- | --------------------------------- | ------------------------------------ |
| Вью     | `has_permission()`        | перед выполнением запроса к view  | Проверка роли, авторизации           |
| Объект  | `has_object_permission()` | при доступе к конкретному объекту | Проверка владельца, времени, статуса |

---

## 7. Частые ошибки

| Ошибка                                                        | Причина                                            | Решение                                                     |
| ------------------------------------------------------------- | -------------------------------------------------- | ----------------------------------------------------------- |
| `AttributeError: 'AnonymousUser' object has no attribute ...` | Проверка атрибута у неавторизованного пользователя | Всегда проверяйте `request.user.is_authenticated`           |
| Permission не срабатывает                                     | Метод `has_object_permission` не вызывается        | Для `list` и `create` DRF не вызывает object-level проверки |
| Отсутствует `message`                                         | DRF возвращает стандартное “Permission denied.”    | Добавляйте атрибут `message` для информативных ошибок       |

---

## 8. Пример полного кастомного permission

```python
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAuthorOrReadOnly(BasePermission):
    message = "Редактировать может только автор."

    def has_object_permission(self, request, view, obj):
        # Безопасные методы (GET, HEAD, OPTIONS) — разрешены всем
        if request.method in SAFE_METHODS:
            return True
        # Остальные — только автору
        return obj.author == request.user
```

Использование:

```python
class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthorOrReadOnly]
```

## Итого: классификация кастомных permissions

| Тип             | Пример класса                    | Логика                                   |
| --------------- | -------------------------------- | ---------------------------------------- |
| По владельцу    | `IsOwner`, `IsAuthorOrReadOnly`  | Проверка `obj.owner == request.user`     |
| По роли         | `IsModerator`, `IsAdminOrEditor` | Проверка `user.role` или `user.is_staff` |
| По времени      | `IsEditableFor24Hours`           | Проверка `obj.created_at`                |
| По статусу      | `IsDraftEditable`                | Проверка `obj.status == 'draft'`         |
| Комбинированные | `IsOwnerOrAdmin`                 | Объединение нескольких условий           |
| Только чтение   | `ReadOnly`                       | Разрешены только безопасные методы       |

