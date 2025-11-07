## ✏️ Django `UpdateView` — краткий обзор и пример

`UpdateView` используется для **редактирования существующего объекта**. Он похож на `CreateView`, но:

* получает объект по `pk` (или `slug`)
* отображает форму с уже заполненными данными
* сохраняет изменения после POST

---

## ✅ Реализация редактирования книги

### **views.py**

```python
from django.views.generic.edit import UpdateView
from django.urls import reverse_lazy
from .models import Book

class BookUpdateView(UpdateView):
    model = Book
    fields = ["title", "author", "year", "description"]
    template_name = "library/book_form.html"  # тот же шаблон, что и у CreateView
    success_url = reverse_lazy("books")   # редирект после сохранения
```

---

### **urls.py**

Добавим путь к редактированию:

```python
from . import views

urlpatterns = [
    path("books/", views.BookListView.as_view(), name="books"),
    path("books/add/", views.BookCreateView.as_view(), name="book-add"),
    path("books/<int:pk>/", views.BookDetailView.as_view(), name="book-detail"),
    path("books/<int:pk>/edit/", views.BookUpdateView.as_view(), name="book-edit"),
]
```

---

### 🔁 Используем тот же шаблон: `templates/library/book_form.html`

Он автоматически будет показывать текущие значения полей.

---

## 📌 Добавим ссылку на редактирование

**В шаблоне detail: `book_detail.html`**

```html
<a href="{% url 'book-edit' book.pk %}">✏️ Редактировать книгу</a>
```

**В списке, например в `book_list.html`:**

```html
<li>
  {{ book.title }} — {{ book.author }}
  [<a href="{% url 'book-detail' book.pk %}">Подробнее</a>]
  [<a href="{% url 'book-edit' book.pk %}">Редактировать</a>]
</li>
```

---

## ✅ Как работает:

* Переход по `/books/3/edit/` открывает форму с уже введёнными данными книги №3
* После сохранения — редирект на `books` (можно изменить)

