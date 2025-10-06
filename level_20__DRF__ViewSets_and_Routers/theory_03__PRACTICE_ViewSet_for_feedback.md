### 0. Постановка задача

Выполнить API для работы с приложением обратной связи Feedback.  
Имитировать работу модели с помощью json-файла.  
Поля "модели" `Feedback`:  
- `date` - дата в формате datetime
- `user_email` - адрес электронной почты
- `message` = сообщение

Реализовать проект на DRF с помощью ViewSet.

---

### 1. Модель-обёртка для JSON

`feedback/services.py`

```python
import traceback
import json
import os
from datetime import datetime

FILE_PATH = os.path.join(os.path.dirname(__file__), 'feedback.json')

class Feedback:
    """Минимальная «модель» для JSON-файла"""

    def __init__(self, id=None, date=None, user_email='anonymous_user@noname.com', message=''):
        self.id = id
        self.date = date or datetime.now().isoformat()
        self.user_email = user_email
        self.message = message

    @classmethod
    def _read_file(cls):
        """
        Читает данные из JSON-файла.
        Возвращает список записей. Если файл повреждён или отсутствует — возвращает пустой список.
        """
        if not os.path.exists(FILE_PATH):
            try:
                with open(FILE_PATH, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=4, default=str)
                return []
            except Exception as e:
                print(f"Ошибка при создании файла {FILE_PATH}: {e}")
                traceback.print_exc()
                return []
        try:
            with open(FILE_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError при чтении {FILE_PATH}: {e}. Возвращаю пустой список.")
            traceback.print_exc()
            return []
        except FileNotFoundError as e:
            print(f"FileNotFoundError при чтении {FILE_PATH}: {e}. Возвращаю пустой список.")
            traceback.print_exc()
            return []
        except PermissionError as e:
            print(f"PermissionError при чтении {FILE_PATH}: {e}. Возвращаю пустой список.")
            traceback.print_exc()
            return []
        except Exception as e:
            print(f"Неожиданная ошибка при чтении {FILE_PATH}: {e}. Возвращаю пустой список.")
            traceback.print_exc()
            return []

    @classmethod
    def _write_file(cls, data):
        """
        Пишет список записей в JSON-файл.
        Использует default=str для безопасной сериализации нестандартных объектов (например, datetime).
        """
        try:
            with open(FILE_PATH, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4, default=str)
        except TypeError as e:
            print(f"TypeError при записи в {FILE_PATH}: {e}")
            traceback.print_exc()
        except PermissionError as e:
            print(f"PermissionError при записи в {FILE_PATH}: {e}")
            traceback.print_exc()
        except Exception as e:
            print(f"Неожиданная ошибка при записи в {FILE_PATH}: {e}")
            traceback.print_exc()

    @classmethod
    def all(cls):
        data = cls._read_file()
        return [cls(**item) for item in data]

    @classmethod
    def get(cls, pk):
        item = next((x for x in cls._read_file() if str(x.get('id')) == str(pk)), None)
        return cls(**item) if item else None

    def save(self):
        data = self._read_file()
        if self.id is None:
            # генерация id
            self.id = (max([x['id'] for x in data], default=0) + 1) if data else 1
            data.append(self.__dict__)
        else:
            # обновление существующего
            index = next((i for i, x in enumerate(data) if x['id'] == self.id), None)
            if index is not None:
                data[index] = self.__dict__
            else:
                data.append(self.__dict__)
        self._write_file(data)
        return self

    def delete(self):
        data = self._read_file()
        data = [x for x in data if x['id'] != self.id]
        self._write_file(data)
```

---

### 2. Сериализатор (`serializers.py`)
`feedback/serializers.py`


```python
from rest_framework import serializers

class FeedbackSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    date = serializers.DateTimeField()
    user_email = serializers.EmailField()
    message = serializers.CharField()
```

---

### 3. ViewSet через ModelViewSet-подобный подход

`feedback/views.py`

```python
from rest_framework import viewsets, status
from rest_framework.response import Response
from .services import Feedback
from .serializers import FeedbackSerializer

class FeedbackViewSet(viewsets.ViewSet):
    """Используем JSON как «модель»"""

    def list(self, request):
        items = Feedback.all()
        serializer = FeedbackSerializer(items, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        item = Feedback.get(pk)
        if not item:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = FeedbackSerializer(item)
        return Response(serializer.data)

    def create(self, request):
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            item = Feedback(**serializer.validated_data)
            item.save()
            return Response(FeedbackSerializer(item).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        item = Feedback.get(pk)
        if not item:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = FeedbackSerializer(data=request.data)
        if serializer.is_valid():
            for key, value in serializer.validated_data.items():
                setattr(item, key, value)
            item.save()
            return Response(FeedbackSerializer(item).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def partial_update(self, request, pk=None):
        item = Feedback.get(pk)
        if not item:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
    
        serializer = FeedbackSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            for key, value in serializer.validated_data.items():
                setattr(item, key, value)
            item.save()
            return Response(FeedbackSerializer(item).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        item = Feedback.get(pk)
        if not item:
            return Response({"detail": "Not found"}, status=status.HTTP_404_NOT_FOUND)
        item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

#### Важное отличие `update` от `partial_update`:

1. **В `update`:**

   ```python
   serializer = FeedbackSerializer(data=request.data)
   ```

   * Вы не передаёте `instance` → сериализатор не знает про старый объект.
   * Все поля обязательны, даже если хотите поменять только одно.
   * Если не указать `date` или `user_email`, валидация упадёт.

---

2. **В `partial_update`:**

   ```python
   serializer = FeedbackSerializer(item, data=request.data, partial=True)
   ```

   * Тут вы передаёте **`instance`** (`item`).
   * Указываете `partial=True`.
   * В результате DRF разрешает обновлять только часть полей — остальные он возьмёт из `item`.

3. Таким образом, разница в двух вещах:

* `update` требует **полного объекта** → все поля обязательны.
* `partial_update` требует только **части данных** → остальные тянет из instance.

---

### 4. Маршрутизатор проекта

Добавить в `main/urls.py`:

```python

urlpatterns = [
    path('api/feedback/', include('feedback.api_urls')),
]
```

---

### 5. Маршрутизатор приложения

`feedback/api_urls.py`

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FeedbackViewSet

router = DefaultRouter()
router.register(r'', FeedbackViewSet, basename='feedback')

urlpatterns = [
    path('', include(router.urls)),
]
```

---


### 6. Настройки `settings.py`

Чтобы удобнее отслеживать ошибки в командной строке без "мусора" HTML,  
и чтобы кириллица была буквами, а не юникодом,   
и чтобы JSON был с отступами:

```python
DEBUG = False

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]


REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "rest_framework.views.exception_handler",
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",  # всегда JSON
    ],
    "DEFAULT_PARSER_CLASSES": [
        "rest_framework.parsers.JSONParser",
    ],
    'JSON_UNICODE': True,  # В новых версиях DRF для корректного вывода
    'JSON_INDENT': 4,
}
```


---

### Что получилось в итоге:

1. JSON-файл ведёт себя как «модель» с методами:

   * `all()` → список всех записей
   * `get(pk)` → получить одну запись
   * `save()` → создать/обновить
   * `delete()` → удалить

2. `ViewSet` почти полностью повторяет `ModelViewSet`.

3. И немаловажно: легко заменить на реальную модель в будущем, просто меняем класс `Feedback`.
