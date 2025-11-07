Добавим в приложение:
- модель `MyappModel`, 
- шаблон `myapp/myappmodel_list.html`,
- вью `MyappListView`,
- маршрут`urls.py`,
- и меню `base.html` добавляем ссылку на страницу приложения,
- добавим отображение для админки

А также добавим метод `ready()`, который будет запускаться при каждой инициализации приложения:

## ✅ Когда вызывается `ready()`:

| Сценарий                                                   | `ready()`                   |
| ---------------------------------------------------------- | --------------------------- |
| Запуск `runserver`                                         | ✅ Да                        |
| Запуск `shell`, `shell_plus`                               | ✅ Да                        |
| Запуск `celery` с Django                                   | ✅ Да (если настроен Django) |
| Запуск тестов (`test`)                                     | ✅ Да                        |
| Запуск `migrate`, `makemigrations`, `collectstatic` и т.п. | ✅ Да                        |

---

* `ready()` вызывается **один раз на процесс**, когда Django **загружает конфигурацию приложений** (`AppConfig`).
* Это происходит **до обработки HTTP-запросов** и **до выполнения middleware/view**.
* Вы **можете безопасно подключать сигналы, логирование, регистрацию плагинов и т.п.** в `ready()`.


## НО❗️ : 
* `ready()` ≠ `migrations`
* Следовательно, в `ready()` **нельзя гарантировать**, что БД уже существует и применены миграции.
* Поэтому при обращении к моделям стоит использовать `try...except` для перехвата ошибок, таких как `OperationalError` или `ProgrammingError`.

---


### 1. `models.py`
```djngo
from django.db import models

class MyappModel(models.Model):
    code = models.CharField(max_length=50, unique=True)
    value = models.TextField()

    def __str__(self):
        return f"{self.code}: {self.value}"

```

### 2. В `temlates` добавляем `myapp/myappmodel_list.html`

```html
{% extends "base.html" %}
{% load static %}

{% block title %}Myapp Page{% endblock %}

{% block content %}
<h2>This is Myapp Page</h2>
<ul>
{% for obj in object_list %}
    <li>{{ obj.code }} - {{ obj.value }}</li>
{% empty %}
    <li>Sorry, no data in this list.</li>
{% endfor %}
</ul>

{% endblock %}
```


### 3. Во `views.py` создаём `MyappListView`

```django
from django.views.generic import ListView
from .models import MyappModel


class MyAppListView(ListView):
    model = MyappModel

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data()

        context['active_page'] = 'myapp'
        return context
```

### 4. `urls.py`

```django
from django.urls import path
from . import views

urlpatterns = [
    path('', views.MyAppListView.as_view(), name='myapp'),
]
```

### 5. В меню `base.html` добавляем ссылку на страницу приложения (строка 25)

```html
<a class="nav-link {% if active_page == 'myapp' %}active{% endif %}" href="{% url 'myapp' %}">MyApp</a>
```

### 6. `apps.py`

```djangourlpath
from django.apps import AppConfig
from django.db import OperationalError, ProgrammingError


# Конфигурация по умолчанию (достаточно краткого пути)
class MyappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'


# Кастомная конфигурация (необходим полный путь к MyappAutoInitConfig)
class MyappAutoInitConfig(MyappConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'myapp'
    verbose_name = 'My App with Auto Init'

    def ready(self):
        # Защитный импорт внутри метода (избегает проблем с ранним импортом)
        from .models import MyappModel

        try:
            # Проверка существования записи с кодом 'default'
            if not MyappModel.objects.filter(code='default').exists():
                MyappModel.objects.create(code='default', value='Автоматически добавлено')
        except (OperationalError, ProgrammingError) as e:
            # База может быть не готова (например, миграции ещё не применены)
            print(e)

```
