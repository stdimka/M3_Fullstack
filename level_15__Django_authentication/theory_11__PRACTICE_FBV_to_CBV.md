# Замена FBV на CBV

`accounts/views.py`

## 1. Регистрация (CBV)

В нашей версии `RegistrationForm` добавлено поле `phone`, которого нет в `User`.

Поэтому приходится использовать `FormView` для кастомной регистрации.

```python
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import resolve_url
from django.urls import reverse_lazy
from django.views.generic.edit import FormView
from .forms import RegistrationForm
from django.contrib.auth import login

class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()

        # обновляем UserProfile
        phone = form.cleaned_data.get('phone')
        user.userprofile.phone = phone
        user.userprofile.save()

        login(self.request, user)
        return super().form_valid(form)
    
    def get_success_url(self):
        # пробуем взять ?next= из GET или POST
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url:
            return next_url
        return resolve_url(settings.LOGIN_REDIRECT_URL or self.success_url)
```

---

## 2. Логин (CBV)

Для логина можно взять готовый `LoginView` из Django.

```python
from django.contrib.auth.views import LoginView

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
```

---

## 3. Логаут (CBV)

Аналогично используем готовый `LogoutView`.

```python
from django.contrib.auth.views import LogoutView

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')
```

---

## 4. Дополнительно Profile (CBV)

Страницу редактирования профиля через `UpdateView`.

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import UpdateView
from .models import UserProfile
from .forms import UserProfileForm

class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = UserProfile
    form_class = UserProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('home')

    def get_object(self, queryset=None):
        return self.request.user.userprofile
```

---

## 5. urls.py

```python
# accounts/urls.py
from django.urls import path
from . import views


urlpatterns = [
    # path('register/', views.register_view, name='register'),
    # path('login/', views.login_view, name='login'),
    # path('logout/', views.logout_view, name='logout'),

    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    # path('profile/', views.ProfileUpdateView.as_view(), name='profile'),
]
```

