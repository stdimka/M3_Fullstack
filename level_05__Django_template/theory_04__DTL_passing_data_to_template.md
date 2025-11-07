## 🧩 Пример структуры

Допустим, у нас есть такой класс (или модель, или просто объект с атрибутами):

```python
class Item:
    def __init__(self, name, price):
        self.name = name
        self.price = price
```

---

## 📄 views.py

```python
from django.views.generic import TemplateView

class ProductView(TemplateView):
    template_name = 'products.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Список объектов
        items = [
            Item(name='Apple', price=1.2),
            Item(name='Banana', price=0.8),
            Item(name='Cherry', price=2.5)
        ]

        # Словарь с несколькими ключами
        data = {
            'title': 'Список товаров',
            'description': 'Пример передачи словаря в шаблон',
            'items': items  # список объектов
        }

        context['data'] = data
        return context
```

---

## 🧾 shop/products.html

```html
{% extends "base.html" %}

{% block title %}Продукты{% endblock %}

{% block content %}
    <h1>{{ data.title }}</h1>
    <p>{{ data.description }}</p>
    
    <ul>
      {% for item in data.items %}
        <li>{{ item.name }} — {{ item.price }} $</li>
      {% endfor %}
    </ul>

    <h2>Товары по индексу:</h2>
    <p>Первый товар: {{ data.items.0.name }} — {{ data.items.0.price }} $</p>
    <p>Второй товар: {{ data.items.1.name }} — {{ data.items.1.price }} $</p>

{% endblock %}
```

---

## 🔍 Результат

HTML отобразит заголовок, описание и список товаров с ценами.

