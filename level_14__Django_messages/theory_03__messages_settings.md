## 3. Подключение и настройка Django Messages

### 1. Добавление в `INSTALLED_APPS`

Чтобы использовать Messages API, необходимо убедиться,  
что приложение подключено в `settings.py`:

```python
INSTALLED_APPS = [
    # другие приложения
    'django.contrib.messages',
]
```

* Это гарантирует, что модели и вспомогательные функции для сообщений 
  будут доступны в проекте.
* Без этого подключение middleware и использование API не будут работать.

---

### 2. Middleware

Middleware нужен для обработки сообщений между запросом и ответом.  
В `settings.py` нужно добавить:

```python
MIDDLEWARE = [
    # другие middleware
    'django.contrib.sessions.middleware.SessionMiddleware',  # обязательно перед MessageMiddleware
    'django.contrib.messages.middleware.MessageMiddleware',
]
```

* **Важно:** `MessageMiddleware` должен идти ПОСЛЕ `SessionMiddleware`,  
  так как сообщения часто хранятся в сессии.
* Middleware отвечает за сохранение сообщений в хранилище и передачу их в шаблоны.

---

### 3. Настройка `MESSAGE_STORAGE`

Это определяет, где будут храниться сообщения до их отображения.

Примеры:

```python
# хранение сообщений в сессии
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# хранение сообщений в cookie
# MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'
```

* `SessionStorage` — чаще используется, особенно если сообщения могут быть длинными.
* `CookieStorage` — хранит сообщения в cookie, подходит для небольших текстов  
  и простых уведомлений.

---

### 4. Настройка тегов и кастомизация стилей через `MESSAGE_TAGS`

Сообщения имеют уровни (`DEBUG`, `INFO`, `SUCCESS`, `WARNING`, `ERROR`).  
Через `MESSAGE_TAGS` можно сопоставить CSS-классы для этих уровней:

```python
from django.contrib.messages import constants as messages

MESSAGE_TAGS = {
    messages.DEBUG: 'debug',
    messages.INFO: 'info',
    messages.SUCCESS: 'success',
    messages.WARNING: 'warning',
    messages.ERROR: 'error',
}
```

* В шаблоне можем использовать эти теги для оформления:

```html
{% if messages %}
<ul>
  {% for message in messages %}
    <li class="{{ message.tags }}">{{ message }}</li>
  {% endfor %}
</ul>
{% endif %}
```

* Это позволяет задать стили в CSS, например:

```css
.success { color: green; }
.error { color: red; }
.warning { color: orange; }
.info { color: blue; }
```
