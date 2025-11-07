## ➕ Django CreateView — краткий обзор и пример

`CreateView` — универсальное представление для **создания нового объекта** с использованием формы.

---

### 📌 Особенности `CreateView`:

* Основано на модели (`model`)
* Автоматически создаёт форму по полям модели
* Можно указать `fields`, `form_class` или переопределить методы
* После успешного создания — редирект (по умолчанию на `object.get_absolute_url()`)

---

## ✅ Создание новой книги

**views.py:**

```python
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from .models import Book

class BookCreateView(CreateView):
    model = Book
    fields = ["title", "author", "year", "description"]
    template_name = "library/book_form.html"
    success_url = reverse_lazy("books")  # редирект после успешного добавления
```

---

**urls.py:**

```python
from django.urls import path
from . import views

urlpatterns = [
    path("books/", views.BookListView.as_view(), name="books"),
    path("books/add/", views.BookCreateView.as_view(), name="book-add"),
    path("books/<int:pk>/", views.BookDetailView.as_view(), name="book-detail"),
]
```

---

## 🖋️ Шаблон формы

**templates/library/book_form.html:**

```html
<h1>Добавить новую книгу</h1>

<form method="post">
    {% csrf_token %}
    {{ form.as_p }}

    <button type="submit">Сохранить</button>
</form>

<a href="{% url 'books' %}">← Назад к списку</a>
```

---

## ✅ Как это работает:

* URL `/books/add/` открывает форму
* После отправки POST-запроса и успешного сохранения — редирект на список
* Поля формы формируются автоматически из модели

---

## 📝 Подсказка:

Если хотите управлять валидацией или поведением до/после сохранения, вы можете:

* Переопределить `form_valid(self, form)`
* Использовать собственный `ModelForm`


