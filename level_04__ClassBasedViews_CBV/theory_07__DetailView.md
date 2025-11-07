## 🔍 Django DetailView — краткий обзор и пример

`DetailView` используется для отображения **одного объекта** по его идентификатору (обычно `pk` или `slug`).

---

### 📌 Особенности `DetailView`:

* Получает объект из модели (`model = Book`)
* Передаёт его в шаблон через `object` или имя, заданное в `context_object_name`
* URL должен содержать `pk` (или `slug`, если используете его)

---

## ✅ Пример `DetailView` для книги

**views.py:**

```python
from django.views.generic import DetailView
from .models import Book

class BookDetailView(DetailView):
    model = Book
    template_name = "library/book_detail.html"
    context_object_name = "book"
```

---

**urls.py:**

```python
from django.urls import path
from . import views

urlpatterns = [
    path("books/", views.BookListView.as_view(), name="books"),
    path("books/<int:pk>/", views.BookDetailView.as_view(), name="book-detail"),
]
```

---

**templates/library/book_detail.html:**

```html
<h1>{{ book.title }}</h1>
<p><strong>Автор:</strong> {{ book.author }}</p>
<p><strong>Год издания:</strong> {{ book.year }}</p>
<p><strong>Описание:</strong> {{ book.description }}</p>

<a href="{% url 'books' %}">← Назад к списку книг</a>
```

---

## 💡 Как это работает:

* При переходе на `books/3/` будет показана книга с `id=3`
* Если объект не найден, Django вернёт `404`
* По умолчанию ищется `pk`, но можно использовать `slug` — если захотите, покажу, как

---

## 🎯 Итог:

| View         | Что делает                       | Шаблон по умолчанию     |
| ------------ | -------------------------------- | ----------------------- |
| `ListView`   | Список объектов                  | `app/model_list.html`   |
| `DetailView` | Один объект (по `pk` или `slug`) | `app/model_detail.html` |

