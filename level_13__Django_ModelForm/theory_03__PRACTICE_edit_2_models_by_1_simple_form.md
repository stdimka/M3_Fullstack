# Редактирование 2-х моделей (Book + BookDetail) через обычную форму

В Django есть удобные механизмы форм для редактирования (создания) нескольких моделей одновременно.

Но, завершая тему простых форм, реализуем эту задачу традиционными средствами, и всё    
будет оставаться в рамках простых форм — без inline-формсетов и сложных конструкци:

- `Book + BookDetail`**` создаются вместе.
- CRUD-операции используют одинаковые шаблоны (где это возможно).

И снова всё будет реализовано в двух вариантах: для FBV, и для CBV.

---

## 1. Формы и шаблоны (подходят и для FBV, и для CBV)

### 1.1. Формы  `myapp/forms.py`

```python
from django import forms
from .models import Book, BookDetail

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


class BookDetailForm(forms.ModelForm):
    class Meta:
        model = BookDetail
        fields = ['summary', 'page_count']
        widgets = {
            'summary': forms.Textarea(attrs={'class': 'form-control'}),
            'page_count': forms.NumberInput(attrs={'class': 'form-control'})
        }
```


---

### 1.2. Шаблоны

#### 1.2.1. `myapp/book_form.html`

Один шаблон для **Create** и **Update**:
* В обоих случаях будет использован `book_form.html`.
* Отличие только в заголовке и кнопке (`Создать` или `Обновить`).

```html
{% extends "base.html" %}
{% load static %}

{% block content %}
<div class="container mt-4">
    <h2>{{ form_action }} книгу</h2>
    <form method="post" class="w-50">
        {% csrf_token %}
        <fieldset>
            <legend>Book</legend>
            {{ book_form.as_p }}
        </fieldset>
        <fieldset>
            <legend>Book Detail</legend>
            {{ detail_form.as_p }}
        </fieldset>
        <button type="submit" class="btn btn-primary me-2">{{ form_action }}</button>
        <a href="{% url 'book_list' %}" class="btn btn-secondary">Отменить</a>
    </form>
</div>
{% endblock %}
```

#### 1.2.2. `myapp/book_confirm_delete.html`

```html
{% extends "base.html" %}
{% load static %}

{% block content %}
<div class="container mt-4">
    <h2>Удалить книгу "{{ book.title }}"?</h2>
    <form method="post">
        {% csrf_token %}
        <button type="submit" class="btn btn-danger me-2">Да, удалить</button>
        <a href="{% url 'book_detail' book.pk %}" class="btn btn-secondary">Отмена</a>
   </form>
</div>
{% endblock %}
```

#### 1.2.3. `myapp/book_detail.html`

```html
{% extends "base.html" %}
{% load static %}

{% block content %}
<div class="container mt-4 w-50">
    <h2>{{ book.title }} ({{ book.author }})</h2>
    <p><strong>Год:</strong> {{ book.year_published }}</p>
    <p><strong>Статус:</strong> {{ book.is_deleted|yesno:"Удалена,Активна" }}</p>

    {% if book.detail %}
        <h3>Детали</h3>
        <p><strong>Описание:</strong> {{ book.detail.summary }}</p>
        <p><strong>Страниц:</strong> {{ book.detail.page_count }}</p>
    {% endif %}

    <a href="{% url 'book_update' book.pk %}" class="btn btn-warning me-2">Редактировать</a>
    <a href="{% url 'book_delete' book.pk %}"class="btn btn-danger me-2">Удалить</a>
    <a href="{% url 'book_list' %}" class="btn btn-secondary me-2">Отменить</a>

</div>
{% endblock %}
```

## 2. Маршрутизаторы и вью (представления) для FBV (Function-Base View)

### 2.1. `myapp/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookView.as_view(), name='book_list'),

    path('book/add/', views.book_create, name='book_create'),
    path('book/<int:pk>/edit/', views.book_update, name='book_update'),
    path('book/<int:pk>/', views.book_detail, name='book_detail'),
    path('book/<int:pk>/delete/', views.book_delete, name='book_delete'),
]
```

---

### 2.2. FBV

```python
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView
from myapp.models import Book
from .forms import BookForm, BookDetailForm


class BookView(ListView):
    model = Book

    
def book_create(request):
    if request.method == 'POST':
        book_form = BookForm(request.POST)
        detail_form = BookDetailForm(request.POST)
        if book_form.is_valid() and detail_form.is_valid():
            book = book_form.save()
            detail = detail_form.save(commit=False)
            detail.book = book
            detail.save()
            return redirect('book_list')
    else:
        book_form = BookForm()
        detail_form = BookDetailForm()

    return render(request, 'myapp/book_form.html', {
        'book_form': book_form,
        'detail_form': detail_form,
        'form_action': 'Создать',
    })


def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    detail = getattr(book, 'detail', None)

    if request.method == 'POST':
        book_form = BookForm(request.POST, instance=book)
        detail_form = BookDetailForm(request.POST, instance=detail)
        if book_form.is_valid() and detail_form.is_valid():
            book = book_form.save()
            detail = detail_form.save(commit=False)
            detail.book = book
            detail.save()
            return redirect('book_list')
    else:
        book_form = BookForm(instance=book)
        detail_form = BookDetailForm(instance=detail)

    return render(request, 'myapp/book_form.html', {
        'book_form': book_form,
        'detail_form': detail_form,
        'form_action': 'Обновить',
    })


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'myapp/book_detail.html', {'book': book})


def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        book.delete()
        return redirect('book_list')  # сюда можно вывести список книг
    return render(request, 'myapp/book_confirm_delete.html', {'book': book})
```


## 3. Маршрутизаторы и вью (представления) для CBV (Class-Base View)

### 3.1. `myapp/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    path('', views.BookView.as_view(), name='book_list'),

    path('book/add/', views.BookCreateView.as_view(), name='book_create'),
    path('book/<int:pk>/edit/', views.BookUpdateView.as_view(), name='book_update'),
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('book/<int:pk>/delete/', views.BookDeleteView.as_view(), name='book_delete'),
]

```

### 3.2. СBV

```python
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import (ListView, CreateView, UpdateView,
                                  DetailView, DeleteView)
from myapp.models import Book
from .forms import BookForm, BookDetailForm


class BookView(ListView):
    model = Book


class BookCreateView(CreateView):
    model = Book
    form_class = BookForm
    template_name = 'myapp/book_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['book_form'] = BookForm(self.request.POST or None)
        context['detail_form'] = BookDetailForm(self.request.POST or None)
        context['form_action'] = 'Создать'
        return context

    def form_valid(self, form):
        detail_form = BookDetailForm(self.request.POST)
        if detail_form.is_valid():
            book = form.save()
            detail = detail_form.save(commit=False)
            detail.book = book
            detail.save()
            return redirect('book_list')
        return self.form_invalid(form)


class BookUpdateView(UpdateView):
    model = Book
    form_class = BookForm
    template_name = 'myapp/book_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        detail = getattr(self.object, 'detail', None)
        context['book_form'] = BookForm(self.request.POST or None, instance=self.object)
        context['detail_form'] = BookDetailForm(self.request.POST or None, instance=detail)
        context['form_action'] = 'Обновить'
        return context

    def form_valid(self, form):
        detail = getattr(self.object, 'detail', None)
        detail_form = BookDetailForm(self.request.POST, instance=detail)
        if detail_form.is_valid():
            book = form.save()
            detail = detail_form.save(commit=False)
            detail.book = book
            detail.save()
            return redirect('book_list')
        return self.form_invalid(form)


class BookDetailView(DetailView):
    model = Book
    template_name = 'myapp/book_detail.html'
    context_object_name = 'book'


class BookDeleteView(DeleteView):
    model = Book
    template_name = 'myapp/book_confirm_delete.html'
    success_url = reverse_lazy('book_list')
    context_object_name = 'book'
```
