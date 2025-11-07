Помимо наследования шаблонов, DTL позволяет вставлять (включать) один шаблон в другой.  
Рассмотрим пример

## 📦 Цель

Сделать страницу `/profile/`, которая показывает имя и email пользователя, используя `{% include %}`.

---

## 🧩 1. View-функция (`views.py`)

Для простоты сгенерируем десяток пользователей прямо во view
```python
class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email

class ProfileView(TemplateView):
    template_name = "shop/profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Генерируем список из 10 пользователей
        users = [
            User(username=f"user{i}", email=f"user{i}@example.com")
            for i in range(1, 11)
        ]

        context['users'] = users
        return context
```

---

## 🌐 2. URL-маршрут (`urls.py`)

```python
urlpatterns = [
    path('profile/', views.ProfileView.as_view(), name='profile'),
]
```

---

## 🗂 3. Структура шаблонов

```
templates/
└── shop/
    ├── products.html
    ├── profile.html         ← основной шаблон
    └── includes/
        └── user_card.html    ← вставляемый фрагмент
```

---

## 📄 4. `profile.html` (основной шаблон)

```django
{% extends "base.html" %}

{% block title %}Профиль{% endblock %}

{% block content %}
<h1>Профиль пользователя</h1>

{# Вставка блока с данными пользователя #}
<ul>
    {% for user in users %}
    <li>
        {% include "shop/includes/user_card.html" with user=user %}
    </li>
    {% endfor %}
</ul>

<p>Здесь может быть дополнительная информация...</p>
{% endblock %}
```

---

## 🧩 5. `includes/user_card.html` (фрагмент)

```django
<div class="user-card">
  <h2>{{ user.username }}</h2>
  <p>Email: {{ user.email }}</p>
</div>
```


