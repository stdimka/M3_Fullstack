# Добавление messages в проект

## HTML

Логичнее всего блок с сообщениями один раз разместить в `base.html`,   
чем дублировать его в каждом шаблоне для каждой страницы.


```html
    {% if messages %}
        {% for message in messages %}
            <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            </div>
        {% endfor %}
    {% endif %}
```

Хорошо, давайте подробно разберём все теги и элементы этого фрагмента кода. Он написан на **Django Template Language (DTL)** и сочетает в себе HTML + Bootstrap-классы + Django-шаблонные теги.

---

### HTML --> Bootstrap элементы

* **`<div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">`**

  * `class="alert"` — базовый класс Bootstrap для сообщений.
  * `alert-{{ message.tags }}` — динамический класс. Подставляется в зависимости от типа сообщения:

    * `alert-success` (зелёный, успешная операция)
    * `alert-danger` (красный, ошибка)
    * `alert-warning` (жёлтый, предупреждение)
    * `alert-info` (синий, информационное)
  * `alert-dismissible` — делает алерт закрываемым (появляется крестик для закрытия).
  * `fade show` — анимация появления/исчезновения.
  * `role="alert"` — атрибут доступности (для скринридеров), обозначает этот элемент как сообщение.

* **`<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>`**
  Кнопка для закрытия сообщения.

  * `class="btn-close"` — Bootstrap-класс, который рисует крестик.
  * `data-bs-dismiss="alert"` — говорит Bootstrap: при клике нужно закрыть элемент с классом `alert`.
  * `aria-label="Close"` — атрибут доступности (читатели экрана произнесут "Закрыть").

---

## Вызов сообщений (`views.py`)

### 1 Импорт

В любом случае нужен импорт:

```python
from django.contrib import messages
```

---

### 2 FBV (Function-Based View)

#### a) Пример с GET (сообщение будет показываться **каждый раз**, когда открывают страницу)

```python
from django.shortcuts import render
from django.contrib import messages

def my_get_view(request):
    # Сообщение в GET – будет отображаться всегда при открытии страницы
    messages.info(request, "Это информационное сообщение при GET-запросе.")

    return render(request, "my_template.html")
```

**ВАЖНО:** такое сообщение будет показываться **каждый раз**, даже если пользователь просто обновит страницу.

---

#### b) Пример с POST (сообщение после действия, например, формы)

```python
from django.shortcuts import render, redirect
from django.contrib import messages

def my_post_view(request):
    if request.method == "POST":
        # Здесь обычно обработка формы
        form_data = request.POST.get("name")
        if form_data:
            messages.success(request, "Форма успешно отправлена!")
            return redirect("home")  # Перенаправление, чтобы сообщение не повторялось
        else:
            messages.error(request, "Ошибка: данные не заполнены!")

    return render(request, "my_template.html")
```

**ВАЖНО:** сообщения после POST обычно **ставят перед redirect**, чтобы избежать их повторного отображения при обновлении страницы.

---

### 3 CBV (Class-Based View)

#### a) Сообщение в GET

```python
from django.views.generic import TemplateView
from django.contrib import messages

class MyGetView(TemplateView):
    template_name = "my_template.html"

    def get(self, request, *args, **kwargs):
        messages.info(request, "Это сообщение для GET-запроса.")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Сообщение при GET
        messages.info(self.request, "Сообщение через get_context_data")
        
        # Можно добавить данные в context, если нужно
        context['extra'] = "Дополнительные данные"
        return context
```

Сообщение будет показываться **каждый раз при GET**, как и в FBV.

---

#### b) Сообщение после POST (например, форма)

```python
from django.views.generic import FormView
from django.contrib import messages
from django.urls import reverse_lazy
from .forms import MyForm

class MyFormView(FormView):
    template_name = "my_form.html"
    form_class = MyForm
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        messages.success(self.request, "Форма успешно отправлена!")
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Форма заполнена неверно.")
        return super().form_invalid(form)
```

**Особенность CBV:** используем `self.request`, а сообщения ставим в методы обработки POST (`form_valid`, `form_invalid`),  
чтобы не дублировать их при GET.

---

## `Настройки settings.py`

По умолчанию, если не указано значение `MESSAGE_STORAGE` Django использует `FallbackStorage`.      
Что более чем достаточно для нормальной работы сообщений.

Но если желание, это значение можно задать и явно:

```python
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
# или
MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'
```

Кроме того, по умолчание, ни Django, ни Bootstrap не отображают сообщений уровня `debug`.

Если этот уровень всё-таки нужен, нужно изменить настойки в `settings.py`:

```python
from django.contrib.messages import constants as messages

MESSAGE_LEVEL = messages.DEBUG
```

И форму шаблона:

```html
{% for message in messages %}
    <div class="alert 
        {% if message.tags == 'debug' %}alert-secondary
        {% elif message.tags == 'info' %}alert-info
        {% elif message.tags == 'success' %}alert-success
        {% elif message.tags == 'warning' %}alert-warning
        {% elif message.tags == 'error' %}alert-danger
        {% else %}alert-primary{% endif %} 
        alert-dismissible fade show" 
        role="alert">
        {{ message }}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
{% endfor %}

```
