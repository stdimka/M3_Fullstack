Попробуем реализовать всё сказанное по поводу `InlineFormset` нашем проекте.

## 1. Добавим новую ссылку в базовую страницу для отображения списка авторов

### 1.1. Добавляем view

`myapp/views.py`

```python
from myapp.models import Author, Book

class AuthorListView(ListView):
    model = Author
    template_name = 'myapp/author_list.html'
    context_object_name = 'authors'
```

### 1.2. Добавляем маршрут

`myapp/urls.py`

```python
    path('author-list/', views.AuthorListView.as_view(), name='author_list'),
```

### 1.3. Добавляем шаблон автора
`templates/myapp/author_list.html`

Реальная ссылка на форму авторов здесь пока закомментирована.  
(Так как пока у нас нет формы редактирования авторов и всего, что с ней связано).

А вместо этого вызывается ссылка на редактирование первой книги.

```html
{% extends "base.html" %}
{% load static %}

{% block content %}
<div class="container mt-4">
    <h1 class="mb-4">Список авторов</h1>

    <ul class="list-group">
        {% for author in authors %}
            <li class="list-group-item d-flex justify-content-between align-items-center">
                {{ author.name }}
                <div>
                    {# Временно отключена ссылка редактирования #}
                    {# <a href="{% url 'author_edit' author.id %}" class="btn btn-sm btn-warning">Редактировать</a> #}
                    <a href="{% url 'book_update' 1 %}" class="btn btn-sm btn-warning">Редактировать</a>
                </div>
            </li>
        {% endfor %}
    </ul>
</div>
{% endblock %}

```

### 1.4. Добавляем в главное меню базового шаблона ссылку на список автора

```html
                    <li class="nav-item">
                        <a class="nav-link {% if active_page == 'myapp' %}active{% endif %}" href="{% url 'book_list' %}">Book List</a>                    
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if active_page == 'myapp' %}active{% endif %}" href="{% url 'author_list' %}">Author List</a>                    
                    </li>

```

## 2. Добавляем `InlineFormSet` в форму автора

### 2.1. Добавляем `BookFormSet` и `AuthorForm`

Стилизуем сразу же под классы Bootstrap:

`myapp/forms.py`

```python
from django import forms
from django.forms import inlineformset_factory
from .models import Author, Book

class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите имя автора'
            })
        }

# InlineFormset для Book в контексте Author
BookFormSet = inlineformset_factory(
    Author,
    Book,
    fields=['title', 'year_published', 'is_deleted'],
    extra=1,
    can_delete=True,
    widgets={
        'title': forms.TextInput(attrs={
            'class': 'form-control', 'placeholder': 'Введите название книги'}),
        'year_published': forms.NumberInput(attrs={
            'class': 'form-control', 'placeholder': 'Введите год публикации книги'}),
        'is_deleted': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    }

)
```

### 2.2. Добавляем шаблон редактирования автора

`templates/myapp/author_edit.html`

```html
{% extends "base.html" %}
{% load static %}

{% block content %}
<div class="container mt-4">
    <h1 class="mb-4">Редактировать автора</h1>

    <form method="post">
        {% csrf_token %}

        <!-- Контейнер формы (все поля уже стилизованы виджетами) -->
        {{ form }}
        {{ formset.management_form }}
        {% for f in formset %}
            {{ f }}
        {% endfor %}

        <!-- Кнопка отправки -->
        <button type="submit" class="btn btn-primary mt-3">Сохранить</button>
    </form>
</div>
{% endblock %}

```

### 2.2. Добавляем view

`myapp/views.py`

```python
from .forms import AuthorForm, BookFormSet

def author_edit(request, pk):
    author = get_object_or_404(Author, pk=pk)
    if request.method == 'POST':
        form = AuthorForm(request.POST, instance=author)
        formset = BookFormSet(request.POST, instance=author)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()  # сохраняются все книги вместе
            return redirect('author_list')
    else:
        form = AuthorForm(instance=author)
        formset = BookFormSet(instance=author)
    return render(request, 'myapp/author_edit.html', {'form': form, 'formset': formset})
```

### 2.3. Раскомменчиваем ссылку на `InlineFormset` в шаблоне `author_list.html`


и ссылку в `urls.py`:  

`    # path('author-edit/<int:pk>/', views.author_edit, name='author_edit'),`



