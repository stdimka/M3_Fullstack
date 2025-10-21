## Создание приложения для аутентификации

### Задание

1. Создать модель пользователя с полями 
   1. (username, email, password, first_name, last_name, phone, is_verified)
2. Поля, которые нет по умолчанию в модели `User`, добавить в модель `UserProfile`
3. Обеспечить возможность регистрации, авторизации и выхода пользователя
4. Неавторизированный пользователь может только просматривать главную страницу.

### Создание (перенос) проекта

1. Создаём папку проекта
1. Копируем файлы из [example_from_lecture](./example_from_lecture) 
1. Переименовываем `db.sqlite3--` в `db.sqlite3`
1. Создаём виртуальное окружение `pyton3 -m venv .venv`
1. Активируем его `source .venv/bin/activate`
1. Устанавливаем пакеты `pip install -r requirements.txt`


### 1 Создаём и регистрируем приложение `accounts`

```bash
./manage.py startapp accounts
```

`main/settings.py`
```python
INSTALLED_APPS = [
    ...
    # --- my apps ---
    'myapp',
    'feedback',
    'accounts',
]
```


---

### 2 Модель UserProfile

Модель User c нужными полями у нас уже есть по умолчанию.  
Поэтому создаём модель `UserProfile` с полями, которых нет у `User`

`accounts/models.py`

```python
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

    
# Создаём профиль автоматически при регистрации пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

        
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userprofile.save()

```

---

### 3 Формы для регистрации и логина

`accounts/forms.py`

```python
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    
class LoginForm(AuthenticationForm):
    username = forms.TextInput(attrs={'class': 'form-control'})
    password = forms.PasswordInput(attrs={'class': 'form-control'})

```

---

### 4 Вью

`accounts/views.py`

```python
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm, LoginForm


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

```

---

### 5 URLs

`main/urls.py`

```python
urlpatterns = [
    ...
    path('accounts/', include('accounts.urls')),
]
```

`accounts/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]
```

---

### 6 Шаблоны с Bootstrap 5.3

**base.html**


`templates/accounts/register.html`

```html
{% extends 'base.html' %}
{% block title %}Register{% endblock %}
{% block content %}
<h2>Register</h2>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit" class="btn btn-primary">Register</button>
</form>
<p>Already have an account? <a href="{% url 'login' %}">Login</a></p>
{% endblock %}
```

`templates/accounts/login.html`

```html
{% extends 'base.html' %}
{% block title %}Login{% endblock %}
{% block content %}
<h2>Login</h2>
<form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit" class="btn btn-primary">Login</button>
</form>
<p>No account? <a href="{% url 'register' %}">Register</a></p>
{% endblock %}
```

`templates/accounts/base.html`

Полностью заменяем содержимое тегов `<nav></nav>` на код ниже:

```html
    <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
        <div class="container-fluid">
            <a class="navbar-brand" href="{% url 'home' %}">MySite</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
                    aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto mb-2 mb-lg-0">
                    <li class="nav-item">
                        <a class="nav-link {% if active_page == 'home' %}active{% endif %}" href="{% url 'home' %}">Home</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if active_page == 'about' %}active{% endif %}" href="/">About</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if active_page == 'contacts' %}active{% endif %}" href="/">Contacts</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if active_page == 'feedback' %}active{% endif %}" href="{% url 'feedback' %}">Feedback</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if active_page == 'myapp' %}active{% endif %}" href="{% url 'book_list' %}">Book List</a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link {% if active_page == 'myapp' %}active{% endif %}" href="{% url 'author_list' %}">Author List</a>
                    </li>
                </ul>
    
                <!-- Правая часть navbar: приветствие и кнопки -->
                <ul class="navbar-nav ms-auto mb-2 mb-lg-0">
                    {% if user.is_authenticated %}
                        <li class="nav-item">
                            <span class="navbar-text me-3">
                                Welcome, {{ user.username }}
                            </span>
                        </li>
                        <li class="nav-item">
                            <form action="{% url 'logout' %}" method="post">
                                {% csrf_token %}
                                <button class="btn btn-outline-light btn-sm" type="submit">Logout</button>
                            </form>
                        </li>
                    {% else %}
                        <li class="nav-item me-2">
                            <a class="btn btn-outline-light btn-sm" href="{% url 'login' %}">Login</a>
                        </li>
                        <li class="nav-item">
                            <a class="btn btn-light btn-sm" href="{% url 'register' %}">Register</a>
                        </li>
                    {% endif %}
                </ul>
            </div>
        </div>
    </nav>
```

---

### 7 Миграции и запуск

```bash
python manage.py makemigrations
python manage.py migrate
```

### 8 Добавить UserProfile уже существующим пользователям

Если в базе уже есть пользователи (а они есть), необходимо выполнить:


1. Открыть shell

```bash
./manage.py shell
```

2. Добавить `UserProfile` каждому пользователю БД

```python
from django.contrib.auth.models import User
from accounts.models import UserProfile

# Создаем профили для всех пользователей, у которых их нет
created_count = 0
for user in User.objects.all():
    if not hasattr(user, 'userprofile'):
        UserProfile.objects.create(user=user)
        created_count += 1

print(f"Создано профилей: {created_count}")
```

