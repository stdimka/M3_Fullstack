from django.contrib.auth.views import LoginView, LogoutView
from django.conf import settings
from django.shortcuts import resolve_url

from django.urls import reverse_lazy
from django.views.generic.edit import View, FormView

from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from .tokens import email_verification_token
from .forms import RegistrationForm

from django.core.mail import send_mail

from django.http import HttpResponse
from django.contrib.auth import get_user_model

from django.contrib.auth.views import (
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView,
)


class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = RegistrationForm
    success_url = reverse_lazy('login')  # логиним только после подтверждения

    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.is_active = False  # блокируем вход
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
            recipient_list=[user.email],  # получатель (почта из формы)
        )

        return super().form_valid(form)

    def get_success_url(self):
        # пробуем взять ?next= из GET или POST
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url:
            return next_url
        return resolve_url(settings.LOGIN_REDIRECT_URL or self.success_url)


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True


class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('login')


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


# Встроенные Django views (django.contrib.auth.views)

class MyPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset_form.html"


class MyPasswordResetDoneView(PasswordResetDoneView):
    template_name = "accounts/password_reset_done.html"


class MyPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"


class MyPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = "accounts/password_reset_complete.html"
