## Django ListView 

`ListView` — это универсальное представление для отображения списка объектов из базы данных.

Очень удобно, когда нужно вывести таблицу, список записей, постов, товаров и т.п.

---

### 📌 Основные особенности `ListView`:

* Автоматически получает набор объектов (queryset) из модели
* По умолчанию передаёт в шаблон переменную с объектами — `object_list` или `<model>_list`
* Позволяет задавать модель через `model` или собственный `queryset`
* Позволяет переопределять метод `get_context_data` для дополнительного контекста
* Поддерживает пагинацию (через атрибут `paginate_by`)

---

### ✅ Простой пример ListView

**models.py:**

```python
from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)

    def __str__(self):
        return self.title
```

**views.py:**

```python
from django.views.generic import ListView
from .models import Book

class BookListView(ListView):
    model = Book
    template_name = "library/book_list.html"  # по умолчанию: library/book_list.html
    context_object_name = "books"  # в шаблоне переменная будет books (вместо object_list)
    paginate_by = 10  # по 10 книг на страницу
```

**urls.py:**

```python
from django.urls import path
from . import views

urlpatterns = [
    path("books/", views.BookListView.as_view(), name="books"),
]
```

**templates/library/book_list.html:**

```html
<h1>Список книг</h1>

<ul>
  {% for book in books %}
    <li>{{ book.title }} — {{ book.author }}</li>
  {% empty %}
    <li>Книг нет</li>
  {% endfor %}
</ul>

{% if is_paginated %}
  <div>
    {% if page_obj.has_previous %}
      <a href="?page={{ page_obj.previous_page_number }}">Назад</a>
    {% endif %}

    Страница {{ page_obj.number }} из {{ page_obj.paginator.num_pages }}

    {% if page_obj.has_next %}
      <a href="?page={{ page_obj.next_page_number }}">Вперёд</a>
    {% endif %}
  </div>
{% endif %}
```

---

### 📝 Ключевые моменты:

* `context_object_name` задаёт имя переменной для списка в шаблоне (по умолчанию — `object_list`)
* Пагинация включается через `paginate_by`
* Можно фильтровать queryset, переопределяя метод `get_queryset()`

---

### Пример с фильтрацией queryset:

```python
class BookListView(ListView):
    model = Book

    def get_queryset(self):
        return Book.objects.filter(author__icontains="Толстой")
```



