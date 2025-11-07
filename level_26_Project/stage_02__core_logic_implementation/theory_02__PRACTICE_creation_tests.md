## 1. Создание тестов для БД

На начальной стадии небольшого проекта, удобнее всего с ним работать вне docker-контейнера.  
Поэтому в контейнере у нас будет только База данных.

### Создаём приложения `user` и `shop` 

```bash
./manage.py startapp user
./manage.py startapp shop
```

### Добавляем их в `main/settings.py` в блок `INSTALLED_APPS`

Заодно добавляем туда и DRF, который установили на предыдущей стадии.  
(И устанавливаем, если ещё не установили `pip install djangorestframework`)

```python
    # --- my apps ---
    'rest_framework',
    'user',
    'shop',
```

### Добавляем настройки PostgreSQL в `main/settings.py` и устанавливаем 

```bash
pip install python-dotenv
```

```python
import os
from dotenv import load_dotenv

# загрузка .env из корня проекта
load_dotenv()

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DJANGO_DB_NAME", "jr_project_db"),
        "USER": os.getenv("DJANGO_DB_USER", "user"),
        "PASSWORD": os.getenv("DJANGO_DB_PASSWORD", "password"),
        "HOST": os.getenv("DJANGO_DB_HOST", "localhost"),
        "PORT": os.getenv("DJANGO_DB_PORT", "5432"),
    }
}
```

```bash
# Устанавливаем
pip install psycopg2-binary

# И не забываем обновлять requirements:
pip freeze > requirements.txt
```


### Создаём структуру для `pytest`

#### 1. Инсталлируем `pytest` и `pytest-django`

`freezegun` - пакет, изменяющий время (для тестов)
```bash
pip install pytest pytest-django
pip install freezegun
```

Проверка установки:
```bash
pytest --version
pip show pytest-django
```

#### 2. Добавляем файл `pytest.ini`

```ini
[pytest]
DJANGO_SETTINGS_MODULE = main.settings
python_files = tests.py test_*.py *_tests.py
addopts = -v --tb=short
```

Последняя строчка 
* -v (verbose) — показывает имена тестов, вместо точек
* --tb=short — сокращает формат traceback (ошибок) для более компактного вывода

Для проверки создания БД можно при запуске однократно добавить флаг `--create-db`:
```bash
pytest --create-db
```

#### 3. Создаём папки `/tests` в корне проекта и в приложениях `user` и `shop` 

В результате структура должна стать примерно такой:

```
project_root/
│
├── pytest.ini           ← глобальные настройки pytest
├── conftest.py          ← общие фикстуры (user, product_factory, make_order и т.д.)
│
├── users/
│   ├── models.py
│   ├── views.py
│   └── tests/
│       ├── test_user_profile.py
│       └── test_user_token.py
│
├── shop/
│   ├── models.py
│   ├── views.py
│   └── tests/
│       ├── test_product.py
│       ├── test_order.py
│       ├── test_payment.py
│       ├── test_review.py
│       └── test_signals_and_jobs.py

```
#### 4. Файл общих фикстур всего проекта `conftest.py`

```python
import pytest
from decimal import Decimal

from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from shop.models import Product, Order, OrderItem, Review, Payment
from user.models import UserToken, UserProfile


# ------------------------------
# USERS
# ------------------------------

@pytest.fixture
def user(db):
    """Создает обычного пользователя с профилем и нулевым балансом."""
    user = User.objects.create_user(username="testuser", password="pass123")
    # UserProfile создается автоматически через сигнал post_save
    profile = user.userprofile
    profile.balance = Decimal("0.0")
    profile.save()
    return user


@pytest.fixture
def user_with_balance(user):
    """Пользователь с ненулевым балансом."""
    profile = user.userprofile
    profile.balance = Decimal('200.00')
    profile.save()
    return user


@pytest.fixture
def token_factory(db):
    """Фабрика токенов разных типов для пользователя."""
    def create_token(user, token_type="refresh", expires_in_minutes=60):
        expires_at = timezone.now() + timedelta(minutes=expires_in_minutes)
        token = UserToken.objects.create(
            user=user,
            token_type=token_type,
            token="token_" + token_type,
            expires_at=expires_at
        )
        return token
    return create_token


# ------------------------------
# SHOP
# ------------------------------

@pytest.fixture
def product_factory(db):
    """Фабрика продуктов с настраиваемыми параметрами."""
    def create_product(**kwargs):
        defaults = {
            "name": "Test Product",
            "description": "Описание продукта",
            "price": Decimal("100.0"),
            "unit": "шт",
            "category_id": 1,
            "image": "",
            "specs": {"color": "red", "weight": "1kg"},
            "is_active": True,
            "stock": 10,
        }
        defaults.update(kwargs)
        return Product.objects.create(**defaults)
    return create_product


@pytest.fixture
def product(product_factory):
    """Обычный продукт по умолчанию."""
    return product_factory()


@pytest.fixture
def product_in_stock():
    """Простой товар с остатком на складе"""
    return Product.objects.create(
        name="Тестовый товар",
        price=Decimal("100.0"),
        stock=10,
        unit="шт",
        specs={"color": "red"}
    )


@pytest.fixture
def make_order(db, product_factory):
    """Фабрика заказов с позициями."""
    def create_order(user, status="cart", total_price=Decimal("0"), items_count=1):
        order = Order.objects.create(user=user, status=status)
        for _ in range(items_count):
            product = product_factory()
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=1,
                price=product.price
            )
        # Пересчет total_price
        if total_price is not None:
            order.total_price = Decimal(total_price)
            order.save()
        else:
            # Автопересчет суммы из OrderItem
            order.recalculate_total()
        return order
    return create_order


@pytest.fixture
def pending_order(make_order, user):
    """Заказ со статусом pending."""
    return make_order(user=user, status="pending")


@pytest.fixture
def paid_order(make_order, user_with_balance):
    """Оплаченный заказ для проверки инвойса и списания баланса."""
    order = make_order(user=user_with_balance, status="pending")
    Payment.process(order)  # предполагается, что метод списывает баланс и ставит статус paid
    order.refresh_from_db()
    return order


@pytest.fixture
def review_factory(db):
    """Фабрика отзывов."""
    def create_review(user, product, **kwargs):
        defaults = {"rating": 5, "comment": "Отличный товар!"}
        defaults.update(kwargs)
        return Review.objects.create(user=user, product=product, **defaults)
    return create_review


@pytest.fixture
def review(review_factory, user, product):
    """Простой отзыв."""
    return review_factory(user=user, product=product)

```

---

**Что покрывают эти фикстуры?**

| Фикстура            | Назначение                                                          |
| ------------------- |---------------------------------------------------------------------|
| `user`              | Обычный пользователь с профилем, баланс = 0                         |
| `user_with_balance` | Пользователь с балансом для проверки оплаты                         |
| `token_factory`     | Создание токенов разных типов для UserToken                         |
| `product_factory`   | Создание продуктов с любыми параметрами                             |
| `product`           | Обычный продукт по умолчанию                                        |
| `product_in_stock`  | Простой товар с остатком на складе                                  |
| `make_order`        | Создание заказов с `OrderItem` и пересчётом `total_price`           |
| `pending_order`     | Заказ со статусом `pending`                                         |
| `paid_order`        | Заказ со статусом `paid`, баланс пользователя списан, инвойс создан |
| `review_factory`    | Создание отзывов с кастомными параметрами                           |
| `review`            | Простой отзыв по умолчанию                                          |


#### 5. `user/tests/test_user_profile.py`

```python
from decimal import Decimal

import pytest
from datetime import timedelta
from django.utils import timezone
from freezegun import freeze_time

from shop.models import Order, OrderItem, Product


@pytest.mark.django_db
class TestUserProfile:

    def test_get_balance_returns_correct_value(self, user):
        """Проверка метода get_balance."""
        profile = user.userprofile
        profile.balance = Decimal("150.75")
        profile.save()
        assert profile.get_balance() == Decimal("150.75")

    def test_cart_is_created_automatically(self, user):
        """При первом вызове get_cart создается корзина со статусом cart."""
        profile = user.userprofile
        cart = profile.get_cart()
        assert cart.status == "cart"
        assert cart.user == user

    def test_cart_auto_deleted_after_7_days(self, user):
        """Корзина старше 7 дней удаляется при следующем вызове get_cart."""
        profile = user.userprofile
        # cart = profile.get_cart()  # Убрали (user)
        # # Симулируем старую корзину
        # cart.updated_at = timezone.now() - timedelta(days=8)
        # cart.save()
        #
        many_days_ago = timezone.now() - timedelta(days=8)
        with freeze_time(many_days_ago):
            cart = profile.get_cart()

        new_cart = profile.get_cart()
        assert new_cart.id != cart.id  # старая корзина удалена, создана новая
        assert new_cart.status == "cart"

    def test_get_unpaid_orders_returns_only_pending_orders(self, user, make_order):
        """Метод get_unpaid_orders возвращает только заказы с статусом pending и правильную сумму."""
        pending_order = make_order(user=user, status="pending", total_price=50)
        _ = make_order(user=user, status="paid", total_price=30)

        result = user.userprofile.get_unpaid_orders()  # Убрали (user)
        orders = result["orders"]
        total = result["total"]

        assert pending_order in orders
        assert total == 50
        assert all(o.status == "pending" for o in orders)

    def test_get_cart_returns_existing_cart(self, user, make_order):
        """Если корзина существует и не старше 7 дней, get_cart возвращает её."""
        order = make_order(user=user, status="cart")
        profile = user.userprofile
        cart = profile.get_cart()
        assert cart.id == order.id

    def test_cart_created_if_none_exists(self, user):
        """Если корзины нет, get_cart создает новую."""
        profile = user.userprofile
        # Удаляем все корзины пользователя
        Order.objects.filter(user=user, status="cart").delete()
        cart = profile.get_cart()  # Убрали (user)
        assert cart is not None
        assert cart.status == "cart"
        assert cart.user == user

```

---

**Что проверяется?**

1. `get_balance(user)` возвращает корректный баланс
2. Корзина создается автоматически при первом добавлении товара
3. Старые корзины (старше 7 дней) удаляются автоматически
4. `get_unpaid_orders(user)` возвращает только заказы со статусом `pending` и правильную сумму
5. `get_cart` возвращает существующую корзину, если она актуальна
6. Если корзины нет, она создается автоматически

---

#### 6. `user/tests/test_user_token.py`

```python
import pytest
from django.utils import timezone
from datetime import timedelta
from user.models import UserToken


@pytest.mark.django_db
class TestUserToken:

    def test_generate_and_validate_email_token(self, user, token_factory):
        """Создание токена email_verify и проверка его валидности."""
        token = token_factory(user, token_type="email_verify")
        assert token.is_valid()
        assert token.token_type == "email_verify"
        assert token.user == user

    def test_expired_token_becomes_invalid(self, user):
        """Токен, срок действия которого истек, считается недействительным."""
        token = UserToken.objects.create(
            user=user,
            token_type="password_reset",
            token="expired_token",
            expires_at=timezone.now() - timedelta(minutes=1)
        )
        assert not token.is_valid()

    def test_revoke_token(self, user, token_factory):
        """Отозванный токен становится недействительным."""
        token = token_factory(user, token_type="refresh")
        token.revoke()
        token.refresh_from_db()
        assert token.revoked
        assert not token.is_valid()

    def test_cleanup_expired_tokens(self, user):
        """Удаление всех просроченных токенов."""
        expired_token = UserToken.objects.create(
            user=user,
            token_type="email_verify",
            token="expired",
            expires_at=timezone.now() - timedelta(days=1)
        )
        # Метод очистки должен удалить expired токен
        UserToken.cleanup_expired()
        assert not UserToken.objects.filter(id=expired_token.id).exists()

    def test_multiple_token_types(self, user, token_factory):
        """Проверка работы разных типов токенов для одного пользователя."""
        refresh_token = token_factory(user, token_type="refresh")
        email_token = token_factory(user, token_type="email_verify")
        password_token = token_factory(user, token_type="password_reset")

        assert refresh_token.is_valid()
        assert email_token.is_valid()
        assert password_token.is_valid()
        assert refresh_token.token_type == "refresh"
        assert email_token.token_type == "email_verify"
        assert password_token.token_type == "password_reset"

```

---

**Что проверяется?**

1. **Создание токена** заданного типа (`email_verify`, `refresh`, `password_reset`)
2. **Валидация токена** (валидный / истёкший / отозванный)
3. **Истечение срока действия токена** делает его недействительным
4. **Отзыв токена** делает его недействительным
5. **Автоматическая очистка** просроченных токенов
6. **Связь токена с пользователем**

---

#### 7. `shop/tests/test_product.py`

```python
import pytest
from shop.models import Product


@pytest.mark.django_db
class TestProduct:

    def test_product_creation(self, product):
        """Проверка создания продукта по умолчанию."""
        assert product.id is not None
        assert product.name == "Test Product"
        assert product.is_active
        assert product.stock > 0
        assert isinstance(product.specs, dict)

    def test_product_search_by_name(self, product_factory):
        """Поиск продукта по имени."""
        product1 = product_factory(name="Red Chair")
        product2 = product_factory(name="Blue Table")
        results = Product.objects.filter(name__icontains="Chair")
        assert product1 in results
        assert product2 not in results

    # TODO подумать, надо ли это
    def test_product_filter_by_stock(self, product_factory):
        """Проверка наличия продукта на складе."""
        available = product_factory(stock=5)
        sold_out = product_factory(stock=0)
        assert available.is_in_stock() is True
        assert sold_out.is_in_stock() is False

    def test_edit_product_specs(self, product):
        """Редактирование характеристик JSON."""
        product.specs["color"] = "blue"
        product.save()
        updated_product = Product.objects.get(id=product.id)
        assert updated_product.specs["color"] == "blue"

```

---

**Что проверяется?**

* Создание продукта по умолчанию
* Поиск по имени (`name__icontains`)
* Редактирование и сохранение характеристик JSON `(specs`)

---

#### 8. `shop/tests/test_order.py`

```python
import pytest
from datetime import timedelta
from django.utils import timezone
from freezegun import freeze_time

from shop.models import Order, OrderItem


@pytest.mark.django_db
class TestOrder:

    def test_total_price_recalculates_on_item_change(self, user, product_factory):
        """Автоматический пересчет total_price при изменении корзины."""
        product1 = product_factory(price=50)
        product2 = product_factory(price=30)

        order = Order.objects.create(user=user, status="cart")
        OrderItem.objects.create(order=order, product=product1, quantity=2, price=product1.price)
        OrderItem.objects.create(order=order, product=product2, quantity=1, price=product2.price)

        order.recalculate_total()
        assert order.total_price == 2*50 + 30

    def test_order_id_generated_on_pending(self, user, product_factory):
        """При переходе корзины в заказ генерируется order_id."""
        order = Order.objects.create(user=user, status="cart")
        product = product_factory()
        OrderItem.objects.create(order=order, product=product, quantity=1, price=product.price)

        order.to_pending()  # метод перевода корзины в pending и генерации order_id
        assert order.status == "pending"
        assert "__" in order.order_id
        assert str(user.id) in order.order_id

    def test_old_pending_orders_deleted(self, user, make_order):
        """Проверка удаления старых заказов в статусе pending."""
        # Симулируем старый заказ
        # old_order.created_at = timezone.now() - timedelta(days=120)
        # old_order.save()

        # Создаём второй заказ «10 дней назад»
        many_days_ago = timezone.now() - timedelta(days=120)
        with freeze_time(many_days_ago):
            old_order = make_order(user=user, status="pending")

        Order.cleanup_old_pending()
        assert not Order.objects.filter(id=old_order.id).exists()

```

---

**Что проверяется?**

* Автоматический пересчет `total_price` при добавлении/удалении/изменении товаров
* Генерация номера заказа (`order_id`) при переходе корзины в статус `pending`
* Автоматическое удаление старых заказов в статусе `pending` (>100 дней)

---

#### 9. `shop/tests/test_payment.py`

```python
from decimal import Decimal

import pytest
from shop.models import Payment


@pytest.mark.django_db
class TestPayment:

    def test_payment_not_allowed_for_cart(self, user, make_order):
        """Невозможно оплатить заказ в статусе 'cart'."""
        order = make_order(user=user, status="cart")
        result = Payment.process(order)
        assert result is None
        assert order.status == "cart"

    def test_changing_order_status_on_paid(self, user_with_balance, make_order):
        """При оплате заказа меняются статусы и заказа, и оплаты."""
        order = make_order(user=user_with_balance, status="pending", total_price=Decimal("100"))
        payment = Payment.process(order)  # метод должен менять статус на paid и создавать инвойс

        order.refresh_from_db()
        assert order.status == "paid"
        assert payment.status == "completed"

    def test_balance_decreased_after_payment(self, user_with_balance, make_order):
        """Баланс пользователя уменьшается на сумму оплаченного заказа."""
        initial_balance = user_with_balance.userprofile.balance
        order = make_order(user=user_with_balance, status="pending", total_price=100)
        Payment.process(order)
        user_with_balance.userprofile.refresh_from_db()
        assert user_with_balance.userprofile.balance == initial_balance - 100

    def test_auto_payment_of_multiple_pending_orders(self, user_with_balance, make_order):
        """Если баланс достаточно, оплачиваются несколько заказов одновременно."""
        user_profile = user_with_balance.userprofile
        user_profile.balance = 300
        user_profile.save()

        # создаем несколько заказов
        order1 = make_order(user=user_with_balance, status="pending", total_price=100)
        order2 = make_order(user=user_with_balance, status="pending", total_price=150)
        order3 = make_order(user=user_with_balance, status="pending", total_price=100)

        # создаем платёж, который проверяет все неоплаченные заказы
        Payment.process_auto(user_with_balance)

        # проверка статусов и остатка баланса
        order1.refresh_from_db()
        order2.refresh_from_db()
        order3.refresh_from_db()
        user_profile.refresh_from_db()

        assert order1.status == "paid"
        assert order2.status == "paid"
        assert order3.status == "pending"  # недостаточно средств для третьего
        assert user_profile.balance == 50  # 300 - (100+150)


```

---

**Что проверяется?**

1. **Невозможность оплаты корзины** (`cart`)
2. **Генерация номера инвойса** при оплате заказа (`yyyymmdd_hhmmss_userid`)
3. **Списание средств с баланса** пользователя
4. **Автоматическая оплата нескольких заказов**, если баланс покрывает несколько `pending` заказов

---

#### 10. `shop/tests/test_review.py`

```python
import pytest
from shop.models import Review


@pytest.mark.django_db
class TestReview:

    def test_add_review(self, user, product):
        """Пользователь может добавить отзыв на товар."""
        review = Review.objects.create(
            user=user,
            product=product,
            rating=5,
            comment="Отлично!"
        )
        assert review.id is not None
        assert review.user == user
        assert review.product == product
        assert review.rating == 5
        assert review.comment == "Отлично!"

    def test_review_factory(self, review_factory, user, product):
        """Проверка работы фабрики отзывов."""
        review = review_factory(user=user, product=product, rating=4, comment="Хорошо")
        assert review.rating == 4
        assert review.comment == "Хорошо"
        assert review.user == user
        assert review.product == product

    def test_reviews_are_listed_correctly(self, product, review_factory, user):
        """Проверка получения всех отзывов по товару."""
        review1 = review_factory(user=user, product=product, rating=5)
        review2 = review_factory(user=user, product=product, rating=4)

        reviews = Review.objects.filter(product=product)
        assert len(reviews) == 2
        assert review1 in reviews
        assert review2 in reviews

    def test_review_links_to_product_and_user(self, review):
        """Проверка связи отзыва с пользователем и товаром."""
        assert review.user is not None
        assert review.product is not None

```

---

**Что проверяется?**

1. **Добавление отзыва** пользователем
2. **Работа фабрики отзывов** (`review_factory`)
3. **Просмотр всех отзывов** для конкретного товара
4. **Корректная связь** отзыва с товаром и пользователем

---

### 11. `shop/tests/test_signals_and_jobs.py`

```python
import pytest
from datetime import timedelta
from freezegun import freeze_time
from django.utils import timezone
from user.models import UserToken
from shop.models import Order, Payment


@pytest.mark.django_db
class TestSystemSignalsAndJobs:
    """Тестирование сигналов и фоновых задач"""

    def test_generate_order_id_on_pending_transition(self, user_with_balance, product_in_stock):
        """Проверка генерации order_id"""
        order = Order.objects.create(user=user_with_balance, status="cart")
        order.add_product(product_in_stock, quantity=2)
        order.save()

        # Переход корзины в заказ
        order.to_pending()

        assert order.status == "pending"
        assert order.order_id.startswith(timezone.now().strftime("%Y%m%d"))
        assert str(user_with_balance.id) in order.order_id

    def test_auto_payment_trigger_on_pending(self, user_with_balance, product_in_stock):
        """Проверка автооплаты при переходе в pending"""
        userprofile = user_with_balance.userprofile
        initial_balance = userprofile.balance
        print("userprofile.balance =", userprofile.balance)

        order = Order.objects.create(user=user_with_balance, status="cart")
        order.add_product(product_in_stock, quantity=2)
        print("order.total_price = ", order.total_price)
        order.to_pending()  # должно автоматически списать средства

        userprofile.refresh_from_db()
        order.refresh_from_db()
        assert order.status == "paid"
        assert userprofile.balance == initial_balance - order.total_price

    def test_auto_payment_trigger_on_balance_increase(self, user, product_in_stock):
        """Проверка автооплаты при пополнении баланса"""
        order = Order.objects.create(user=user, status="cart")
        order.add_product(product_in_stock, quantity=3)
        order.to_pending()  # недостаточно средств — заказ остаётся pending

        assert order.status == "pending"

        # Пополняем баланс
        profile = user.userprofile
        profile.balance = order.total_price
        profile.save()

        # После сигнала проверки — заказ должен быть оплачен
        order.refresh_from_db()
        assert order.status == "paid"

    def test_cart_auto_deletion(self, user):
        """Автоудаление корзины старше 7 дней"""
        # Создаём новый заказ
        fresh_order = Order.objects.create(user=user, status="cart")

        # Создаём второй заказ «10 дней назад»
        ten_days_ago = timezone.now() - timedelta(days=10)
        with freeze_time(ten_days_ago):
            old_order = Order.objects.create(user=user, status="cart")

        Order.cleanup_expired_carts()

        assert not Order.objects.filter(id=old_order.id).exists()
        assert Order.objects.filter(id=fresh_order.id).exists()

    def test_pending_order_auto_deletion(self, user):
        """Автоудаление pending-заказов старше 100 дней"""

        fresh_order = Order.objects.create(user=user, status="pending")

        # Создаём второй заказ «101 дней назад»
        many_days_ago = timezone.now() - timedelta(days=101)
        with freeze_time(many_days_ago):
            old_order = Order.objects.create(user=user, status="pending")

        Order.cleanup_old_pending()

        assert not Order.objects.filter(id=old_order.id).exists()
        assert Order.objects.filter(id=fresh_order.id).exists()

    def test_auto_delete_expired_tokens(self, user):
        """Автоматическое удаление просроченных токенов"""
        token_valid = UserToken.objects.create(
            user=user,
            token="valid_token",
            token_type="refresh",
            expires_at=timezone.now() + timedelta(days=1)
        )
        token_expired = UserToken.objects.create(
            user=user,
            token="expired_token",
            token_type="refresh",
            expires_at=timezone.now() - timedelta(days=1)
        )

        UserToken.cleanup_expired()

        assert UserToken.objects.filter(id=token_valid.id).exists()
        assert not UserToken.objects.filter(id=token_expired.id).exists()


```

---

**Что проверяется?**

* Автоматическая генерация `order_id`, переходы статусов 
* Создание `invoice_number`, списание средств
* Проверка автосписания при переходе в `pending` и при пополнении баланса 
* Автоудаление старых корзин и заказов
* Очистка просроченных токенов 


---
Теперь у нас есть **полный набор тестов для моделей**:

* `users` → `UserProfile`, `UserToken`
* `shop` → `Product`, `Order/OrderItem`, `Payment`, `Review`

Все тесты используют **фикстуры из `conftest.py`**, можно запускать сразу через `pytest`.

### TODO: Добавить проверку покрытия бизнес-логики, чтобы убедиться, что весь функционал проверяется.
