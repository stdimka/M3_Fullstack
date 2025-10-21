
## Создаём `BookFormSet`

`myapp/forms.py`

```python
from django import forms
from django.forms import inlineformset_factory, modelformset_factory
from .models import Book


# FormSet для массового редактирования записей модели Book
BookFormSet = modelformset_factory(
    Book,
    form=BookForm,
    extra=0,            # Не добавляем пустых форм
    can_delete=False    # Не даём удалять из формсета
)
```

---

## 2. Создаём FBV для ModelFormSet

`myapp/views.py`

```python
from django.shortcuts import render, redirect
from .forms import BookModelFormSet
from .models import Book

def edit_all_books(request):
    if request.method == "POST":
        formset = BookModelFormSet(request.POST, queryset=Book.objects.all())
        if formset.is_valid():
            formset.save()
            return redirect("edit_all_books")  # Перезагрузка страницы после сохранения
    else:
        formset = BookModelFormSet(queryset=Book.objects.all())

    return render(request, "edit_all_books.html", {"formset": formset})
```

---

## 3. Добавляем ссылку в маршрутизатор

`myapp/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    path("edit_all_books/", views.edit_all_books, name="edit_all_books"),
]
```

---

## 4. Добавляем шаблон 

`templates/myapp/edit_all_books.html`


```html
<div class="container py-4">
    <h1 class="mb-4">Редактирование книг</h1>

    <form method="post" class="card p-3 shadow-sm bg-white">
        {% csrf_token %}
        {{ formset.management_form }}
        
        <div class="table-responsive">
            <table class="table table-bordered align-middle">
                <thead class="table-secondary">
                <tr>
                    <th>Автор</th>
                    <th>Название</th>
                    <th>Год</th>
                    <th>Удалена?</th>
                </tr>
                </thead>
                <tbody>
                {% for form in formset %}
                    <tr>
                        <td>{{ form.author }}</td>
                        <td>{{ form.title }}</td>
                        <td>{{ form.year_published }}</td>
                        <td class="text-center">{{ form.is_deleted }}</td>
                    </tr>
                {% endfor %}
                </tbody>
            </table>
        </div>

        <div class="d-flex justify-content-between mt-3">
            <a href="{% url 'edit_all_books' %}" class="btn btn-secondary">Отменить</a>
            <button type="submit" class="btn btn-primary">Сохранить изменения</button>
        </div>
    </form>
</div>
```

## 5. Добавляем ссылка на массовое редактирование в `myapp/book_list.html` 

`templates/myapp/edit_all_books.html`

```html
{% block content %}
    <div class="container mt-4 mb-4">
        <h2>Books List</h2>
        <a href="{% url 'edit_all_books' %}" class="btn btn-warning me-3">Edit ALL Books</a>
        <a href="{% url 'book_create' %}" class="btn btn-primary">Add Book</a>
    </div>
```