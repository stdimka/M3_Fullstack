# Проверка входа зарегистрированного пользователя

## 1. Добавляем ссылки аутентификации и редиректа в `settings.py`

`main/settings.py`

```python
LOGIN_URL = '/accounts/login/'          # форма логина
LOGIN_REDIRECT_URL = '/'       # куда редиректить после успешного входа
```

## 2. Добавляем декораторы `@login_required`  

`myapp/views.py`

### 2.1. Добавляем декоратор `@login_required` в редактирование списка авторов
```python
from django.contrib.auth.decorators import login_required

@login_required()
def author_edit(request, pk):
    ...
```

### 2.2. Добавляем декоратор `LoginRequiredMixin` в список книг
```python
from django.contrib.auth.mixins import LoginRequiredMixin

class BookView(LoginRequiredMixin, ListView):
    ...
```

## 3. Меняем шаблон

`accounts/login.html`

```html
{% extends 'base.html' %}
{% block title %}Login{% endblock %}
{% block content %}
<h2>Login</h2>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <input type="hidden" name="next" value="{{ next }}">
    <button type="submit" class="btn btn-primary">Login</button>
</form>
<p>No account? <a href="{% url 'register' %}?next={{ request.GET.next }}">Register</a></p>
{% endblock %}
```


## 3. Добавляем считывание и редирект `next` в `register_view()` и `login_view()`

И там, и там меняем 
```python
            return redirect('home')
```
на

```python
            next_url = request.POST.get('next') or request.GET.get('next') or '/'
            return redirect(next_url)
```
