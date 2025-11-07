## Отправка сообщений

Django Messages API позволяет добавлять уведомления из кода Python (чаще всего во views)  
и показывать их пользователю на следующей странице.

### 1. Базовая функция `add_message`

```python
from django.contrib import messages

def my_view(request):
    messages.add_message(request, messages.INFO, "Это информационное сообщение")
```

* **Аргументы**:

  1. `request` — объект запроса.
  2. `level` — уровень сообщения (`DEBUG`, `INFO`, `SUCCESS`, `WARNING`, `ERROR`).
  3. `message` — текст сообщения.
  4. `extra_tags` (опционально) — дополнительные CSS-классы.

---

### 2. Удобные сокращения

Для каждого уровня есть отдельная функция, чтобы не писать `add_message`:

```python
messages.debug(request, "Сообщение для отладки")
messages.info(request, "Информационное сообщение")
messages.success(request, "Операция прошла успешно!")
messages.warning(request, "Это предупреждение")
messages.error(request, "Произошла ошибка")
```

* Эти функции автоматически назначают соответствующий уровень и упрощают код.

---

### 3. Примеры использования

#### a) При обработке формы

```python
from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm

def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Спасибо! Ваша заявка отправлена.")
            return redirect("contact")
        else:
            messages.error(request, "Ошибка при заполнении формы. Проверьте поля.")
    else:
        form = ContactForm()
    return render(request, "contact.html", {"form": form})
```

#### b) При логине

```python
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect
from django.contrib import messages

def login_view(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Добро пожаловать, {user.username}!")
            return redirect("home")
        else:
            messages.error(request, "Неправильный логин или пароль")
```

#### c) При CRUD-действиях

```python
def delete_item(request, pk):
    item = get_object_or_404(Item, pk=pk)
    item.delete()
    messages.warning(request, f"Элемент {item.name} был удален")
    return redirect("item_list")
```

---

**Важно**: сообщения сохраняются в хранилище (сессии или cookie)  
до следующего запроса пользователя.  
То есть если после добавления сообщения делается `redirect`,  
оно не исчезнет и будет доступно на следующей странице,  
которая рендерится после редиректа.
