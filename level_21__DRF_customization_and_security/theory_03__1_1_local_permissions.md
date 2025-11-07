### 1.1. Локальное применение `permissions`

---

### 1.1.1. На уровне вью

```python
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response

class MyView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"message": "Вы авторизованы!"})
```

---

### 1.1.2. На уровне методов вью

#### 1.1.2.1. Через метод `get_permissions()`

Для `ViewSet`:

```python
from rest_framework import permissions, viewsets
from .models import MyModel
from .serializers import MyModelSerializer

class MyModelViewSet(viewsets.ModelViewSet):
    queryset = MyModel.objects.all()
    serializer_class = MyModelSerializer

    def get_permissions(self):
        if self.action == 'list':
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'create':
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]
```

Для `APIView`:

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

class ExampleAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get(self, request):
        return Response({"message": "GET доступен всем"})

    def post(self, request):
        return Response({"message": "POST только для аутентифицированных"})
```

---

#### 1.1.2.2. Через декоратор `@action()`

```python
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import permissions, viewsets

class MyViewSet(viewsets.ViewSet):
    @action(detail=False, permission_classes=[permissions.IsAdminUser])
    def special(self, request):
        return Response({"message": "Только для админа"})
```

---

### 1.1.3. На уровне сериализатора

Хотя DRF нет встроенной поддержки `permission_classes` непосредственно в сериализаторах,   
мы можем  можно выполнить проверки доступа вручную,     
внутри методов `validate()`, `create()`, `update()` или `to_representation()`.

```python
from rest_framework import serializers, exceptions

class MyModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyModel
        fields = ['id', 'name', 'owner']

    def validate(self, attrs):
        user = self.context['request'].user
        if not user.is_staff:
            raise exceptions.PermissionDenied("Доступ запрещён: только админы могут изменять данные.")
        return attrs
```

Здесь сериализатор сам проверяет права и выбрасывает `PermissionDenied`, если правило нарушено.

Это удобно, когда доступ зависит от конкретных данных, а не от типа запроса.

---

### 1.1.4. На уровне модели

На уровне модели можно использовать стандартную систему **разрешений Django** —   
она интегрируется с DRF.

```python
from django.db import models

class MyModel(models.Model):
    name = models.CharField(max_length=100)

    class Meta:
        permissions = [
            ("can_publish", "Может публиковать объект"),
        ]
```

Проверка в коде:

```python
from rest_framework.exceptions import PermissionDenied

def perform_publish(self, request, obj):
    if not request.user.has_perm('app_name.can_publish'):
        raise PermissionDenied("У вас нет разрешения на публикацию.")
    obj.publish()
```

Такие разрешения можно применять как на уровне ORM (например, в бизнес-логике),   
так и в методах view, если требуется доступ к конкретной модели.


---

### Итого на локальном уровне возможно следующие разрешения:

| Уровень                 | Поддерживается напрямую | Комментарий                                  |
| ----------------------- | ----------------------- | -------------------------------------------- |
| **View / ViewSet**      | ✅                       | `permission_classes` или `get_permissions()` |
| **Метод View / Action** | ✅                       | Через `@action` или `get_permissions()`      |
| **Serializer**          | ⚙️ Частично             | Проверки вручную через `validate()`          |
| **Model**               | ⚙️ Частично             | Через стандартные Django permissions         |


