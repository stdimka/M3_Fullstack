Предыдущий пример демонстрирует возможности Django по созданию форм:  
буквально несколько строк Python-кода и форма готова!  
Быстро, удобно, лаконично и безопасно.

Но главное достоинство Django-форм - возможность гибкой валидации вводимых данных.

## Изменение view и HTML-шаблона для удобного анализа результатов валидации

Изменим код так, чтобы можно было видеть одновременно все предыдущие результаты ввода в форму.

`feedback/view.py`:

```python
from django.shortcuts import render
from .forms import FeedbackForm

# Дла удобства будем хранить и отражать на странице 
# результаты нескольких вводов в форму
results_list = []

def feedback_view(request):
    global results_list
    if request.method == "POST":
        form = FeedbackForm(request.POST)
        if form.is_valid():
            # Получаем данные
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']

            # Добавляем результат в список
            results_list.append({
                "name": name,
                "email": email,
                "message": message
            })

            # Сброс формы
            form = FeedbackForm()
    else:
        form = FeedbackForm()

    return render(request, "feedback/feedback.html", {
        "active_page": 'feedback',       
        "form": form,
        "results": results_list  # передаём все результаты в шаблон
    })

```
### `feedback/feedback.html`  - Упрощённый вариант
```html
{% extends "base.html" %}
{% load static %}

{% block title %}Feedback page{% endblock %}

{% block content %}

<div class="container py-5 w-50 mx-auto">
    <h1 class="mb-4">Обратная связь</h1>

    <form method="post" novalidate>
        {% csrf_token %}
        {{ form.as_p }}
        <button type="submit" class="btn btn-primary">Отправить</button>
    </form>

    <!-- Вывод результатов предыдущих запросов -->
    {% if results %}
        <div class="mt-5">
            <h2>История вводов:</h2>
            <div class="list-group">
                {% for r in results %}
                    <div class="list-group-item">
                        <strong>Имя:</strong> {{ r.name }}<br>
                        <strong>Email:</strong> {{ r.email }}<br>
                        <strong>Сообщение:</strong> {{ r.message }}
                    </div>
                {% endfor %}
            </div>
        </div>
    {% endif %}
</div>

{% endblock %}
```


### `feedback/feedback.html`  - Максимальный вариант (для отображения глобальных ошибок в пункте 04_2)
```html
{% extends "base.html" %}
{% load static %}

{% block title %}Feedback page{% endblock %}

{% block content %}

<div class="container py-5 w-50 mx-auto">
    <h1 class="mb-4">Обратная связь</h1>

    <form method="post" novalidate>
        {% csrf_token %}
        
        <!-- Вывод глобальных ошибок формы -->
        
        {% if form.non_field_errors %}
            <div class="alert alert-danger">
                {{ form.non_field_errors }}
            </div>
        {% endif %}

        <!-- Поле Имя -->
        <div class="mb-3">
            {{ form.name.label_tag }}
            {{ form.name }}
            {% if form.name.errors %}
                <div class="invalid-feedback d-block">
                    {{ form.name.errors.0 }}
                </div>
            {% endif %}
        </div>

        <!-- Поле Email -->
        <div class="mb-3">
            {{ form.email.label_tag }}
            {{ form.email }}
            {% if form.email.errors %}
                <div class="invalid-feedback d-block">
                    {{ form.email.errors.0 }}
                </div>
            {% endif %}
        </div>

        <!-- Поле Сообщение -->
        <div class="mb-3">
            {{ form.message.label_tag }}
            {{ form.message }}
            {% if form.message.errors %}
                <div class="invalid-feedback d-block">
                    {{ form.message.errors.0 }}
                </div>
            {% endif %}
        </div>

        <button type="submit" class="btn btn-primary">Отправить</button>
    </form>

    <!-- Вывод результатов предыдущих запросов -->
    {% if results %}
        <div class="mt-5">
            <h2>История вводов:</h2>
            <div class="list-group">
                {% for r in results %}
                    <div class="list-group-item">
                        <strong>Имя:</strong> {{ r.name }}<br>
                        <strong>Email:</strong> {{ r.email }}<br>
                        <strong>Сообщение:</strong> {{ r.message }}
                    </div>
                {% endfor %}
            </div>
        </div>
    {% endif %}
</div>

{% endblock %}
```