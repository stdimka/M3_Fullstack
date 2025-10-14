# Пример добавления книги с помощью `ModelForm`

## 1. Изменения / добавления в проект

### 1.1. Добавляем `myapp/forms.py`

```python
from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'year_published', 'is_deleted']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'year_published': forms.NumberInput(attrs={'class': 'form-control'}),
            'is_deleted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'author': forms.Select(attrs={'class': 'form-select'})
        }

```

### 1.2. Изменяем шаблон `templates/myapp/book_list.html`

```html
{% extends "base.html" %}
{% load static %}

{% block title %}Books{% endblock %}

{% block content %}
<div class="container mt-4">
    <div class="d-flex justify-content-between align-items-center mb-3">
        <h2>Books List</h2>
        <a href="{% url 'book_create' %}" class="btn btn-primary">Add Book</a>
    </div>

    {% if object_list %}
        <table class="table table-hover table-bordered align-middle">
            <thead class="table-light">
                <tr>
                    <th>Author</th>
                    <th>Title</th>
                    <th class="text-center" style="width: 200px;">Actions</th>
                </tr>
            </thead>
            <tbody>
                {% for book in object_list %}
                    <tr>
                        <td>{{ book.author.name }}</td>
                        <td>{{ book.title }}</td>
                        <td class="text-center">
                            <a href="{% url 'book_detail' book.pk %}" class="btn btn-sm btn-info">View</a>
                            <a href="{% url 'book_update' book.pk %}" class="btn btn-sm btn-warning">Edit</a>
                            <a href="{% url 'book_delete' book.pk %}" class="btn btn-sm btn-danger">Delete</a>
                        </td>
                    </tr>
                {% endfor %}
            </tbody>
        </table>
    {% else %}
        <div class="alert alert-warning" role="alert">
            Sorry, no data in this list.
        </div>
    {% endif %}
</div>
{% endblock %}

```

### 1.3. Изменяем ссылку на список книг `myapp/forms.py`

Меняем это на 

```html
<a class="nav-link {% if active_page == 'myapp' %}active{% endif %}" href="{% url 'myapp' %}">MyApp</a>
```

это:

```html
<a class="nav-link {% if active_page == 'myapp' %}active{% endif %}" href="{% url 'book_list' %}">Book List</a>
```

### 1.4. Добавляем шаблон `myapp/book_confirm_delete.html`

```html
{% extends "base.html" %}
{% block content %}
<div class="container mt-4">
    <h2>Delete Book</h2>
    <p>Are you sure you want to delete "{{ object }}"?</p>
    <form method="post">{% csrf_token %}
        <button type="submit" class="btn btn-danger">Delete</button>
        <a href="{% url 'book_list' %}" class="btn btn-secondary">Cancel</a>
    </form>
</div>
{% endblock %}
```


### 1.5. Добавляем шаблон `myapp/book_detail.html`

`DetailView` наследуется от `SingleObjectMixin` и `TemplateResponseMixin`,  
но не от `FormMixin` (как `CreateView`.  
Цель `DetailView` — показ объекта, а не редактирование.  

Поэтому формы по умолчанию нет, есть только объект object и мы расписываем поля вручную:

```html
{% extends "base.html" %}
{% block content %}
<div class="container mt-4">
    <h2>Book Details</h2>
    <form class="w-50">
        <div class="mb-3">
            <label class="form-label">Title</label>
            <input type="text" class="form-control" value="{{ object.title }}" readonly>
        </div>
        <div class="mb-3">
            <label class="form-label">Author</label>
            <input type="text" class="form-control" value="{{ object.author.name }}" readonly>
        </div>
        <div class="mb-3">
            <label class="form-label">Author</label>
            <input type="text" class="form-control" value="{{ object.year_published }}" readonly>
        </div>
        <div class="mb-3">
            <label class="form-label">Author</label>
            <input type="text" class="form-control" value="{{ object.is_deleted }}" readonly>
        </div>
        <a href="{% url 'book_list' %}" class="btn btn-secondary">Back to list</a>
    </form>
</div>
{% endblock %}

```


### 1.6. Добавляем шаблон `myapp/book_form.html`

Для `CreateView` и `UpdateView`.

```html
{% extends "base.html" %}
{% block content %}
<div class="container mt-4">
    <h2>{{ view.object|default:"New Book" }}</h2>
    <form method="post">{% csrf_token %}
        {{ form.as_p }}
        <button type="submit" class="btn btn-success">Save</button>
        <a href="{% url 'book_list' %}" class="btn btn-secondary">Cancel</a>
    </form>
</div>
{% endblock %}

```


`
## 2. Вариант 1: FBV (function-based view)

### 3.1. Изменяем  `myapp/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('create/', views.book_create, name='book_create'),
    path('<int:pk>/', views.book_detail, name='book_detail'),
    path('<int:pk>/update/', views.book_update, name='book_update'),
    path('<int:pk>/delete/', views.book_delete, name='book_delete'),
]
```



### 2.2. Добавляем новые view `myapp/views.py`


```python
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from myapp.models import Book
from myapp.forms import BookForm  # создадим ModelForm для Create/Update


def book_list(request):
    books = Book.objects.all()
    context = {
        'object_list': books,
        'active_page': 'myapp',
    }
    return render(request, 'myapp/book_list.html', context)


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    # Создаем форму с disabled полями, чтобы переиспользовать шаблон book_form.html
    form = BookForm(instance=book)
    for field in form.fields.values():
        field.disabled = True
    context = {
        'object': book,
        'form': form,
        'readonly': True,  # можно использовать в шаблоне
    }
    return render(request, 'myapp/book_form.html', context)


def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('book_list'))
    else:
        form = BookForm()
    return render(request, 'myapp/book_form.html', {'form': form})


def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            return redirect(reverse_lazy('book_list'))
    else:
        form = BookForm(instance=book)
    return render(request, 'myapp/book_form.html', {'form': form})


def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        return redirect(reverse_lazy('book_list'))
    return render(request, 'myapp/book_confirm_delete.html', {'object': book})

```


## 3.Вариант 2: CBV (class-based view)

### 3.1. Изменяем  `myapp/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookView.as_view(), name='book_list'),
    path('create/', views.BookCreateView.as_view(), name='book_create'),
    path('<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('<int:pk>/update/', views.BookUpdateView.as_view(), name='book_update'),
    path('<int:pk>/delete/', views.BookDeleteView.as_view(), name='book_delete'),
]
```

### 3.2. Добавляем новые view `myapp/views.py`

```python
from django.urls import reverse_lazy
from django.views.generic import (ListView, CreateView,
                                  UpdateView, DetailView, DeleteView)
from myapp.models import Book


class BookView(ListView):
    model = Book

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()

        context['active_page'] = 'myapp'
        return context


class BookDetailView(DetailView):
    model = Book
    # template_name = "myapp/book_detail.html"


class BookCreateView(CreateView):
    model = Book
    # template_name = "myapp/book_form.html"
    fields = ['author', 'title', 'year_published', 'is_deleted']
    success_url = reverse_lazy('book_list')


class BookUpdateView(UpdateView):
    model = Book
    # template_name = "myapp/book_form.html"
    fields = ['author', 'title', 'year_published', 'is_deleted']
    success_url = reverse_lazy('book_list')


class BookDeleteView(DeleteView):
    model = Book
    # template_name = "myapp/book_confirm_delete.html"
    success_url = reverse_lazy('book_list')
```
