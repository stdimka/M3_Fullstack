Функционал ТЗ удобно описать на языке приложений и ссылок:

## Приложения и ссылки

### 1. Приложение `users` — Аутентификация и Авторизация

#### Аутентификация

* `auth/registration/` — регистрация пользователя
* `auth/login/` — вход
* `auth/logout/` — выход
* `auth/email/verify/` — подтверждение email
* `auth/email/resend-verification/` — повторная отправка письма
* `auth/password/reset/` — запрос на сброс пароля
* `auth/password/reset/confirm/` — подтверждение сброса пароля
* `auth/password/change/` — смена пароля

#### Управление аккаунтом пользователя

* `/account/` — профиль пользователя
* `/account/orders/` — история заказов
* `/account/profile/edit/` — редактирование профиля
* `/account/addresses/` — адреса доставки

---

### 2. Приложение `shop` — Каталог, Заказы, Оплаты и Reviews

#### Каталог товаров

* `/shop/` — главная страница (список товаров)
* `/shop/products/` — каталог с пагинацией
* `/shop/products/?category=&price_min=&price_max=&sort=` — фильтрация и сортировка
* `/shop/products/search/?q=` — поиск
* `/shop/product/<slug>/` — страница товара
* `/shop/product/<slug>/review/add/` — добавление отзыва
* `/shop/product/<slug>/reviews/` — список отзывов (для подзагрузки, если много отзывов)

#### Заказы (включая корзину и оформление заказа)

* `/shop/order/` — текущий заказ (корзина)
* `/shop/order/add/<product_id>/` — добавить товар
* `/shop/order/remove/<product_id>/` — удалить товар
* `/shop/order/update/<product_id>/` — изменить количество
* `/shop/order/checkout/` — оформить заказ (из корзины → ожидающий оплаты)
* `/shop/order/<order_id>/` — просмотр конкретного заказа
* `/shop/orders/` — история заказов пользователя

#### Оплаты

* `/shop/payment/process/<order_id>/` — процесс оплаты
* `/shop/payment/confirm/<order_id>/` — подтверждение оплаты
* `/shop/payment/cancel/<order_id>/` — отмена оплаты

#### Review

* `/shop/review/add/<product_id>/` — добавить комментарий продукта
* `/shop/review/update/<product_id>/` — изменить комментарий продукта
* `/shop/review/delete/<product_id>/` — оценить комментарий продукта

---

### 3. Приложение `admin` — Админ-панель

* `/admin/` — стандартная админка Django
* `/admin/stats/` — аналитика и отчёты

---

### 4. Приложение `api` — REST API (DRF)

#### Товары

* `/api/products/` — список товаров (GET, пагинация, фильтрация, поиск)
* `/api/products/<id>/` — детальная информация о товаре (GET)

#### Заказы

* `/api/orders/` — создание заказа (POST, JWT)
* `/api/orders/` — список своих заказов (GET, JWT)
* `/api/orders/<id>/` — детальная информация о своём заказе (GET, JWT)
* `/api/orders/<id>/` — обновление или отмена заказа (PATCH / PUT / DELETE, JWT)

#### Пользователи

* `/api/users/register/` — регистрация (POST)
* `/api/users/login/` — получение JWT токенов (POST)

#### Корзина

* `/api/cart/` — просмотр, добавление, обновление, удаление товаров в корзине (GET, POST, PATCH, DELETE, JWT или сессия)

#### Отзывы

* `/api/products/<id>/reviews/` — просмотр и добавление отзывов (GET, POST, JWT)

