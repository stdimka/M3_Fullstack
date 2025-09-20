Рассмотрим простой пример DRF на базе нашего проекта.

### Задание

Реализуем CRUD операции для модели `Book`. (автор будет вводиться по id)

Для начала обойдёмся простым сериализатором без вложенности, с применением `ModelViewSet`. 

---

### 0. Создание (перенос) проекта

1. Создаём папку проекта
1. Копируем файлы из [example_from_lecture](./example_from_lecture) 
1. Переименовываем `db.sqlite3--` в `db.sqlite3`
1. Создаём виртуальное окружение `pyton3 -m venv .venv`
1. Активируем его `source .venv/bin/activate`
1. Устанавливаем пакеты `pip install -r requirements.txt`


---

### 1. Установите DRF (если ещё не установлено)

Устанавливаем пакет DRF:

```bash
pip install djangorestframework
```

И тут же добавляем его в `requirements.txt`":

```bash
pip freeze > requirements.txt
```

---

### 2. Добавьте DRF в `INSTALLED_APPS`

В `settings.py`:

```python
INSTALLED_APPS = [
    ...,
    'rest_framework',
    'myapp',
]
```

---

### 3. Сериализатор

`myapp/serializers.py`

```python
from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'
```

---

### 4. ViewSet

`myapp/views.py`

```python
from rest_framework import viewsets
from .models import Book
from .serializers import BookSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
```

---

### 5. Маршрутизация

Добавляем модуль для маршрутизатора DRF: `myapp/api_urls.py`:

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookViewSet

router = DefaultRouter()
router.register(r'books', BookViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
```

А в `main/urls.py` подключаем `myapp/api_urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('myapp.api_urls')),
]
```


#### Краткое пояснение для `myapp/api_urls.py`
`router.urls` - это атрибут объекта `DefaultRouter` (или любого `SimpleRouter`) из DRF.  
Он не хранит просто одну ссылку на что-то, а генерирует список ссылок на основе зарегистрированных ViewSet.

1. `router.urls` — это свойство, а не метод, который 
   - перебирает все зарегистрированные маршруты (`ViewSet`), 
   - строит для каждого URL-шаблон 
   - и возвращает список.

2. **Что именно возвращается:**

`router.urls` возвращает **список URL-паттернов**, которые можно вставлять в `urlpatterns`. 
Очено грубо и упрощённо

```python
urlpatterns = [
    path('', include(router.urls)),
]
```
по факту представляет из себя целую коллекцию ссылок `url: method`:

```python
[
    path('books/', BookViewSet.as_view({'get': 'list', 'post': 'create'}), name='book-list'),
    path('books/{pk}/', 
         BookViewSet.as_view({'get': 'retrieve', 'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}),
         name='book-detail'
         ),
]
```

Иными словами, `router.urls` фактически превращает ViewSet в Django URL-объекты,  
которые затем подключаются через `include()`.

---


### 6. Проверка

Теперь можно запустить сервер:

```bash
python manage.py runserver
```

И открыть в браузере:
[http://127.0.0.1:8000/api/books/](http://127.0.0.1:8000/api/books/)

Там будет готовый DRF-браузер, где можно:

* **GET**: список книг
* **POST**: создать книгу
* **GET /api/books/{id}/**: получить одну книгу
* **PUT/PATCH**: обновить книгу
* **DELETE**: удалить книгу

### 7. Эмуляция работы стороннего сервера

После запуска основного сервера, запустите в режиме отладки ["сторонний сервер"](theory_05_third_party_server.py)  

Проверьте выполнение указанных запросов.