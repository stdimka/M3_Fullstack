## Основные компоненты Django Messages

### 1. Messages API

   * Это модуль `django.contrib.messages`, который предоставляет удобный интерфейс для отправки сообщений пользователям.
     * Примеры использования:

    ```python
    from django.contrib import messages

    messages.success(request, "Пользователь успешно создан!")
    messages.error(request, "Произошла ошибка при сохранении данных.")
    ```

    * Позволяет добавлять сообщения в коде Python и отображать их в шаблонах.

### 2. Message storage

   * Определяет, **как и где сообщения будут храниться** до того,  
     как пользователь их увидит.
   * В Django есть разные механизмы хранения:

     * `CookieStorage` — хранение сообщений в cookie браузера.
     * `SessionStorage` — хранение сообщений в сессии пользователя.
   * Настраивается через `MESSAGE_STORAGE` в `settings.py`:

     ```python
     MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'
     ```

### 3. Message levels

   * Уровень важности сообщения, который помогает 
     визуально выделять или фильтровать сообщения в шаблонах.
   * Стандартные уровни:

     * `DEBUG` — для отладочной информации.
     * `INFO` — информационные сообщения.
     * `SUCCESS` — сообщение об успешной операции.
     * `WARNING` — предупреждение.
     * `ERROR` — сообщение об ошибке.
   * В шаблонах можно использовать фильтрацию по уровню:

     ```html
     {% if messages %}
         <ul>
         {% for message in messages %}
             <li class="{{ message.tags }}">{{ message }}</li>
         {% endfor %}
         </ul>
     {% endif %}
     ```

