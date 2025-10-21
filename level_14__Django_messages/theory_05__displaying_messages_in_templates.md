## Вывод сообщений в шаблонах

После того как сообщения были добавлены во view,   
их можно вывести в шаблоне с помощью встроенной переменной `messages`.

### 1. Базовый синтаксис

```django
{% if messages %}
  <ul>
    {% for message in messages %}
      <li class="{{ message.tags }}">{{ message }}</li>
    {% endfor %}
  </ul>
{% endif %}
```

* `{% if messages %}` — проверка, есть ли сообщения.
* `{% for message in messages %}` — перебор всех сообщений в текущем запросе.
* `{{ message }}` — вывод текста сообщения.
* `{{ message.tags }}` — CSS-класс, автоматически соответствует уровню сообщения (настраивается через `MESSAGE_TAGS`).

---

### 2. Доступные свойства объекта message

Каждое сообщение — это объект с несколькими полезными свойствами:

| Свойство             | Описание                                                                                   |
| -------------------- | ------------------------------------------------------------------------------------------ |
| `message.level`      | Уровень сообщения (`DEBUG`, `INFO`, `SUCCESS`, `WARNING`, `ERROR`)                         |
| `message.tags`       | Теги для CSS, по умолчанию совпадают с уровнем, можно кастомизировать через `MESSAGE_TAGS` |
| `message.message`    | Текст сообщения, который выводится пользователю                                            |
| `message.extra_tags` | Дополнительные теги, переданные при добавлении сообщения через `extra_tags`                |

Пример использования:

```django
{% for message in messages %}
  <div class="alert {{ message.tags }}">
    {{ message.message }}
  </div>
{% endfor %}
```

---

### 3. Стилизация сообщений

Сообщения можно стилизовать с помощью CSS или готовых фреймворков, например, Bootstrap:

**Пример с Bootstrap 5:**

```django
{% if messages %}
  {% for message in messages %}
    <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
      {{ message }}
      <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    </div>
  {% endfor %}
{% endif %}
```

* Здесь `alert-{{ message.tags }}` автоматически подставляет классы:

  * `success` → `alert-success`
  * `error` → `alert-danger`
  * `warning` → `alert-warning`
  * `info` → `alert-info`

**Свой CSS для кастомных сообщений:**

```css
.success { color: green; background: #e6f7e6; padding: 10px; border-radius: 5px; }
.error   { color: red; background: #fbeaea; padding: 10px; border-radius: 5px; }
.warning { color: orange; background: #fff4e5; padding: 10px; border-radius: 5px; }
.info    { color: blue; background: #e5f0ff; padding: 10px; border-radius: 5px; }
```

