# Реализации проверки пользователя по email

## 1. Добавим поле `is_verified` в `UserProfile`

(Уже добавили при создании модели!!!)

`accounts/tokens.py`

```python
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    is_verified = models.BooleanField(default=False)
```

---

## 2. Добавим генерацию токена (для ссылки в письме)

Создаём новый модуль `tokens.py` в приложении `accounts`

`accounts/tokens.py`

```python
from django.contrib.auth.tokens import PasswordResetTokenGenerator

class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    pass

email_verification_token = EmailVerificationTokenGenerator()
```

---

## 🔹 3. Обновим `RegisterView`

* Создаём пользователя с `is_active=False`, чтобы он не мог войти до подтверждения.
* Генерируем "письмо" (для имитации — выводим в консоль).


`accounts/views.py`

```python
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.shortcuts import resolve_url
from django.views.generic.edit import FormView
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import redirect
from django.contrib.auth.models import User
from .tokens import email_verification_token
from .forms import RegistrationForm
from .models import UserProfile
from django.core.mail import send_mail

class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('login')  # логиним только после подтверждения

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.is_active = False   # блокируем вход
        user.save()

        phone = form.cleaned_data.get('phone')
        user.userprofile.phone = phone
        user.userprofile.save()

        # генерируем токен
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)
        domain = get_current_site(self.request).domain
        verification_link = f"http://{domain}/accounts/verify/{uid}/{token}/"
             
        send_mail(
            subject="Подтверждение email",
            message=f"Привет, {user.username}!\n"
                    f"Подтвердите email, перейдя по ссылке: {verification_link}",
            from_email="noreply@example.com",  # адрес отправителя
            recipient_list=[user.email],       # получатель (почта из формы)
        )
        
        return super().form_valid(form)


    def get_success_url(self):
        # пробуем взять ?next= из GET или POST
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url:
            return next_url
        return resolve_url(settings.LOGIN_REDIRECT_URL or self.success_url)

```

---

## 4. Добавим обработчик подтверждения email


`accounts/views.py`


```python
from django.http import HttpResponse
from django.contrib.auth import get_user_model

class VerifyEmailView(View):
    def get(self, request, uidb64, token):
        UserModel = get_user_model()
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = UserModel.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            user = None

        if user and not user.is_active and email_verification_token.check_token(user, token):
            user.is_active = True
            user.save()
            user.userprofile.is_verified = True
            user.userprofile.save()
            return HttpResponse(f"✅ Email для {user.email} подтвержден! Теперь вы можете войти.")
        else:
            return HttpResponse("❌ Ссылка недействительна или уже использована.")
```

Чтобы реально установить флаг использования токенов - нужна БД.
Поэтому имитируем повторное использование ссылки условием `and not user.is_active`
---

## 5. urls.py

`accounts/urls.py`

```python
from django.urls import path
from . import views

urlpatterns = [
    path('verify/<uidb64>/<token>/', views.VerifyEmailView.as_view(), name='verify_email'),
]
```

---

## 6. settings.py

Переводим "отправку" писем в консоль

```python
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
```

После отладки можно либо удалить этот параметр (по умолчанию отправки идёт через email),  
либо заменить на этот параметр:  

```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
```

---

## 7. Workflow для пользователя

1. Пользователь заполняет форму регистрации.
2. Пользователь создаётся с `is_active=False`.
3. В консоли Django появляется «письмо» с ссылкой.
4. Пользователь кликает ссылку → аккаунт активируется, в `UserProfile.is_verified=True`.
5. Теперь он может войти.



