from django.views.generic import TemplateView


class Item:
    def __init__(self, name, price):
        self.name = name
        self.price = price


class User:
    def __init__(self, username, email):
        self.username = username
        self.email = email


class ProductView(TemplateView):
    template_name = 'shop/products.html'

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
