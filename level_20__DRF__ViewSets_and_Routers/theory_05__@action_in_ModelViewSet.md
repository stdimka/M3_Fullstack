## 1 Суть и зачем нужен `@action`

`@action` — это декоратор, который позволяет добавлять **кастомные методы к ViewSet**,   
помимо стандартных CRUD-операций (`list`, `retrieve`, `create`, `update`, `partial_update`, `destroy`).

(ранее мы уже имели с ним дело: [level_17__DRF_serializer/theory_05__PRACTICE_nested_serializers.md](../level_17__DRF_serializer/theory_05__PRACTICE_nested_serializers.md])

### Зачем это нужно

* Иногда стандартных операций недостаточно. Например:

  * Хочу добавить `/api/users/{id}/activate/` для активации пользователя.
  * Хочу добавить `/api/posts/{id}/like/` для лайка поста.
* Используя `@action`, вы можете:

  * Создавать **методы на уровне экземпляра** (`detail=True`) или на уровне коллекции (`detail=False`).
  * Задавать **HTTP-методы** (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`).
  * Встроенно использовать **permissions, serializers и фильтры** как в обычных методах ViewSet.

---

## 2 Классификация `@action`

### 2.1. По уровню

| Параметр `detail` | Где доступен URL      | Пример URL                  |
| ----------------- | --------------------- | --------------------------- |
| `detail=True`     | На конкретный объект  | `/api/users/5/activate/`    |
| `detail=False`    | На коллекцию объектов | `/api/users/send_reminder/` |

### 2.2. По HTTP-методу

* По умолчанию `methods=['get']`.
* Можно указать любой метод: `methods=['post']`, `methods=['put']` и т.д.

---

## 3 Пример использования

Допустим, есть модель `User`:

```python
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer
```

### 3.1. Действие на уровне объекта (`detail=True`)

```python
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        user = self.get_object()  # получает конкретного пользователя по pk
        user.is_active = True
        user.save()
        return Response({"status": "activated"})
```

* Доступно по URL: `/api/users/5/activate/`
* Используется метод `POST`.

### 3.2. Действие на уровне коллекции (`detail=False`)

```python
    @action(detail=False, methods=['get'])
    def active_users(self, request):
        active = User.objects.filter(is_active=True)
        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)
```

* Доступно по URL: `/api/users/active_users/`
* Используется метод `GET`.

---

### 4 Итого

* `@action` нужен для кастомных действий, которые **не входят в стандартный CRUD**.
* Можно делать действия:

  * На уровне одного объекта (`detail=True`)
  * На уровне коллекции (`detail=False`)
* Можно указывать HTTP-методы (`methods=['get','post']`) и использовать стандартные возможности  
  ViewSet (`serializer_class`, `permission_classes`).




