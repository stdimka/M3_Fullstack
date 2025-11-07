## Комбинирование фильтров

В Django REST Framework можно одновременно использовать несколько фильтров.   
Это позволяет комбинировать 
- точечную фильтрацию по полям, 
- поиск по тексту 
- и сортировку результатов.

---

### 1. Подключение нескольких фильтров

В `filter_backends` можно перечислить несколько классов:

```python
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Book
from .serializers import BookSerializer

class BookListView(generics.ListAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    # DjangoFilterBackend
    filterset_fields = ["year_published", "author"]

    # SearchFilter
    search_fields = ["title", "author__name"]

    # OrderingFilter
    ordering_fields = ["title", "year_published"]
    ordering = ["title"]  # сортировка по умолчанию
```


## 2. Алгоритм работы фильтрации для нескольких параметров:

1. **Берётся базовый `queryset`** из вью.
2. DRF по порядку прогоняет его через каждый backend в `filter_backends`.
3. Каждый backend:

   * если видит свои параметры в запросе → модифицирует `queryset`;
   * если параметров нет → возвращает `queryset` без изменений.
4. Итоговый результат возвращается в сериализатор.

---

### 2.2. Возможные сценарии для нашего примера

### 2.2.1. Только фильтрация (`DjangoFilterBackend`)

Запрос:

```
GET /api/books/?year_published=2020
```

* `DjangoFilterBackend` → `.filter(year_published=2020)`
* `SearchFilter` → ничего не делает
* `OrderingFilter` → сортировка по умолчанию (`title`)

Результат: книги за 2020 год, отсортированные по названию.

---

### 2.2.2. Только поиск (`SearchFilter`)

Запрос:

```
GET /api/books/?search=Пушкин
```

* `DjangoFilterBackend` → ничего не делает
* `SearchFilter` → `.filter(Q(title__icontains="Пушкин") | Q(author__name__icontains="Пушкин"))`
* `OrderingFilter` → сортировка по умолчанию (`title`)

* Результат: книги, где в названии или авторе есть «Пушкин», отсортированные по названию.

---

### 2.2.3. Только сортировка (`OrderingFilter`)

Запрос:

```
GET /api/books/?ordering=-year_published
```

* `DjangoFilterBackend` → ничего не делает
* `SearchFilter` → ничего не делает
* `OrderingFilter` → `.order_by("-year_published")`

Результат: все книги, отсортированные по году публикации (от новых к старым).

---

### 2.2.4. Фильтрация + сортировка

Запрос:

```
GET /api/books/?year_published=2020&ordering=-title
```

* `DjangoFilterBackend` → `.filter(year_published=2020)`
* `SearchFilter` → ничего не делает
* `OrderingFilter` → `.order_by("-title")`

Результат: книги за 2020 год, отсортированные по названию в обратном порядке.

---

### 2.2.5. Поиск + фильтрация

Запрос:

```
GET /api/books/?search=Пушкин&year_published=1833
```

* `DjangoFilterBackend` → `.filter(year_published=1833)`
* `SearchFilter` → дополнительно `.filter(Q(...))`
* `OrderingFilter` → сортировка по умолчанию (`title`)

Результат: книги 1833 года, где встречается «Пушкин», отсортированные по названию.

---

### 2.2.6. Поиск + фильтрация + сортировка

Запрос:

```
GET /api/books/?search=django&year_published=2015&ordering=-year_published
```

* `DjangoFilterBackend` → `.filter(year_published=2015)`
* `SearchFilter` → `.filter(Q(...icontains="django"))`
* `OrderingFilter` → `.order_by("-year_published")`

Результат: книги 2015 года, где встречается «django», отсортированные по году публикации (от новых к старым).


---



### 3. Приоритет применения

Фильтры применяются в порядке, указанном в `filter_backends`.  
Обычно порядок не критичен, но логика примерно такая:

1. `DjangoFilterBackend` — сужает набор данных по заданным полям.
2. `SearchFilter` — выполняет поиск по строкам внутри уже отфильтрованных данных.
3. `OrderingFilter` — сортирует результат после применения предыдущих фильтров.

---

### 4. Практические рекомендации

Лучше всего подключать **все три фильтра** (`DjangoFilterBackend`, `SearchFilter`, `OrderingFilter`) сразу. Тогда API получится гибким:

* разработчики смогут получать точные результаты;
* пользователи смогут искать по ключевым словам;
* фронтенд легко организует сортировку.
