Отлично, завершаем CRUD-цикл с помощью `DeleteView` — добавим удаление книги с подтверждением.

---

## 🗑️ Django `DeleteView` — краткий обзор и пример

`DeleteView` используется для **удаления объекта** с предварительным подтверждением.

---

### 📌 Особенности `DeleteView`:

* Отображает страницу с подтверждением удаления (GET)
* Удаляет объект при POST
* Требует `success_url` — куда перенаправлять после удаления
* По умолчанию ожидает шаблон `app/model_confirm_delete.html`

---

## ✅ Реализация удаления книги

### **views.py**

```python
from django.views.generic.edit import DeleteView
from django.urls import reverse_lazy
from .models import Book

class BookDeleteView(DeleteView):
    model = Book
    template_name = "library/book_confirm_delete.html"
    success_url = reverse_lazy("books")
    context_object_name = "book"
```

---

### **urls.py**

Добавим путь к удалению:

```python
from . import views

urlpatterns = [
    path("books/", views.BookListView.as_view(), name="book-list"),
    path("books/add/", views.BookCreateView.as_view(), name="book-add"),
    path("books/<int:pk>/", views.BookDetailView.as_view(), name="book-detail"),
    path("books/<int:pk>/edit/", views.BookUpdateView.as_view(), name="book-edit"),
    path("books/<int:pk>/delete/", views.BookDeleteView.as_view(), name="book-delete"),
]
```

---

### **templates/library/book\_confirm\_delete.html**

```html
<h1>Удалить книгу: "{{ book.title }}"?</h1>

<p><strong>Автор:</strong> {{ book.author }}</p>
<p><strong>Год издания:</strong> {{ book.year }}</p>
<p><strong>Описание:</strong> {{ book.description }}</p>

<form method="post">
    {% csrf_token %}
    <button type="submit">Да, удалить</button>
    <a href="{% url 'book-detail' book.pk %}">Отмена</a>
</form>
```

---

### 📌 Добавим ссылку на удаление

**В `book_detail.html`:**

```html
<a href="{% url 'book-delete' book.pk %}">🗑️ Удалить книгу</a>
```

**Или в списке `book_list.html`:**

```html
[<a href="{% url 'book-delete' book.pk %}">Удалить</a>]
```

---

## ✅ Как это работает:

* Переход по `/books/3/delete/` показывает страницу подтверждения
* POST удаляет объект и делает редирект на список
* GET показывает шаблон подтверждения

---

🎯 Теперь у вас полный набор CRUD:

* 📄 `ListView` — список
* 🔍 `DetailView` — подробности
* ➕ `CreateView` — добавление
* ✏️ `UpdateView` — редактирование
* 🗑️ `DeleteView` — удаление

