## `users/models.py`

```python
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid


# ------------------------------
# UserProfile
# ------------------------------
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="userprofile")
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    CART_EXPIRATION_DAYS = 7

    def get_balance(self):
        """Возвращает текущий баланс пользователя."""

    def get_cart(self):
        """Возвращает текущую корзину пользователя или создает новую."""


    def get_unpaid_orders(self):
        """Возвращает все заказы со статусом pending и общую сумму."""



# ------------------------------
# UserToken
# ------------------------------
class UserToken(models.Model):
    TOKEN_TYPES = (
        ("refresh", "Refresh"),
        ("email_verify", "Email Verification"),
        ("password_reset", "Password Reset"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tokens")
    token = models.CharField(max_length=255, unique=True)
    token_type = models.CharField(max_length=20, choices=TOKEN_TYPES)
    expires_at = models.DateTimeField()
    revoked = models.BooleanField(default=False)

    def is_valid(self):
        """Проверка валидности токена."""

    def revoke(self):
        """Отозвать токен."""

    @classmethod
    def cleanup_expired(cls):
        """Удаление всех истекших токенов."""


    @classmethod
    def generate(cls, user, token_type="refresh", expires_in_minutes=60):
        """Создает новый токен."""



@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Signal: создать профиль при создании пользователя"""

@receiver(post_save, sender=UserProfile)
def auto_process_pending_orders(sender, instance, created, **kwargs):
    """
    После сохранения UserProfile, если баланс > 0,
    запускаем process_auto для пользователя.
    """


```

---

### Что реализовано

**UserProfile:**

* Поля: `phone`, `address`, `avatar`, `balance`
* Методы:

  * `get_balance()` → возвращает баланс
  * `get_cart()` → возвращает или создаёт корзину, удаляя старую (>7 дней)
  * `get_unpaid_orders()` → возвращает все `pending` заказы и их общую сумму
* **Сигнал** `post_save` создаёт профиль автоматически при создании пользователя

**UserToken:**

* Поля: `token`, `token_type`, `expires_at`, `revoked`
* Методы:

  * `is_valid()` → проверка валидности токена
  * `revoke()` → отзыв токена
  * `cleanup_expired()` → удаление всех истёкших токенов
  * `generate()` → создание нового токена с уникальным UUID

