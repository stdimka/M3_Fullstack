# Проверка входа зарегистрированного пользователя

## Задача: 

Реализовать возможность посещения определённых страниц ТОЛЬКО зарегистрированным пользователям.


## Решение: 

В Django это решается довольно просто – через встроенную систему аутентификации.  
Нам потребуется всего три шага:

---

### 1. Защитить представление (view) декоратором

Для FBV:

```python
from django.contrib.auth.decorators import login_required

@login_required(login_url='/login/')
def my_protected_view(request):
    return render(request, 'protected.html')
```

Для CBV:

```python
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

class MyProtectedView(LoginRequiredMixin, TemplateView):
    template_name = 'protected.html'
    login_url = '/login/'          # куда отправлять незалогиненных
    redirect_field_name = 'next'   # параметр возврата
```

Если же в настройках `settings.py` сразу указать:

```python
LOGIN_URL = '/accounts/login/'          # форма логина
LOGIN_REDIRECT_URL = '/'       # куда редиректить после успешного входа
```

то во всех вью НЕ ПРИДЁТСЯ БОЛЬШЕ УКАЗЫВАТЬ 
 - в FBV 
   - `@login_required(login_url='/login/')` 
 - а в CBV 
   - `login_url = '/login/'` и `redirect_field_name = 'next'`

---

### 2. Реализовать возврат на исходную страницу

Django автоматически добавляет параметр `?next=...` к URL при редиректе на страницу логина.  
В форме входа достаточно обработать его:

`login.html`

```html
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <input type="hidden" name="next" value="{{ next }}">
  <button type="submit">Войти</button>
</form>

<a href="{% url 'register' %}?next={{ request.GET.next }}">Регистрация</a>
```
`register.html`

```html
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <input type="hidden" name="next" value="{{ request.GET.next }}">
  <button type="submit">Зарегистрироваться</button>
</form>

<p>Already have an account? <a href="{% url 'login' %}?next={{ request.GET.next }}">Login</a></p>

```

---

### 3. Реализовать возврат на исходную страницу

Cтандартная `LoginView` уже сама учитывает `next` и вернёт пользователя на страницу, с которой он пришёл. 

А, вот, в FBV `login_view` и / или в CBV `RegisterView` такой опции нет.   

Поэтому её придётся добавить самостоятельно:

Для FBV `login_view` и `register_view`:

```python
        if form.is_valid():
            user = form.save()
            login(request, user)  # сразу логиним нового юзера
            # берем next из POST или GET
            next_url = request.POST.get('next') or request.GET.get('next') or '/'
            return redirect(next_url)
```

Для CBV `RegisterView`:

```python
class RegisterView(FormView):
    template_name = 'register.html'
    form_class = MyRegisterForm
    success_url = reverse_lazy('home')

    def get_success_url(self):
        # пробуем взять ?next= из GET или POST
        next_url = self.request.POST.get('next') or self.request.GET.get('next')
        if next_url:
            return next_url
        return resolve_url(settings.LOGIN_REDIRECT_URL or self.success_url)
```











