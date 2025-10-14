## 6️ Кастомизация внешнего вида и поведения (Templates, CSS, JS)

### 1. **Статические файлы через `Media` в `ModelAdmin` или форме**

Можно подключить свой собственный CSS и JS для конкретной модели через вложенный класс `Media` в форме или `ModelAdmin`.  
Это удобно для 
- дополнительной валидации, 
- динамических эффектов, 
- кастомизации поведения полей 
- и т.д.

**Пример через `ModelAdmin`:**

```python
from django.contrib import admin
from .models import MyModel

@admin.register(MyModel)
class MyModelAdmin(admin.ModelAdmin):
    class Media:
        css = {
            'all': ('css/my_styles.css',)  # путь относительно STATICFILES_DIRS
        }
        js = ('js/my_scripts.js',)
```

**Пример через `ModelForm`:**

```python
from django import forms
from .models import MyModel

class MyModelForm(forms.ModelForm):
    class Meta:
        model = MyModel
        fields = '__all__'

    class Media:
        css = {'all': ('css/my_form_styles.css',)}
        js = ('js/my_form_scripts.js',)
```

И далее, подключаем эту форму в `ModelAdmin`:

```python
class MyModelAdmin(admin.ModelAdmin):
    form = MyModelForm
```

---

### 2. Глобальное подключение CSS/JS

При желании можно применить стили и скрипты ко всей админке в целом.  
И даже создать свою собственную админку.

#### 2.1. Переопределение шаблонов

Django прежде всего ищет шаблоны админки по пути `templates/admin/`,  
куда можно добавить собственные шаблоны. 


Например:

```
project/
└── templates/
    └── admin/
        └── change_form.html
```

---

##### 2.1.1. Основные базовые шаблоны Django Admin

| Шаблон                     | Назначение                                                                                                                       |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `change_list.html`         | Страница со списком всех объектов модели (`/admin/app/model/`). Показывает таблицу с записями, фильтры, поиск, кнопки «Добавить» |
| `change_form.html`         | Страница редактирования/создания объекта (`add`/`change`). Содержит форму, кнопки сохранения, sidebar                            |
| `delete_confirmation.html` | Подтверждение удаления объекта                                                                                                   |
| `object_history.html`      | История изменений объекта (если включен `LogEntry`)                                                                              |
| `login.html`               | Страница входа в админку                                                                                                         |
| `base_site.html`           | Основной шаблон админки, включает меню, навигацию и блоки для контента                                                           |
| `base.html`                | Ещё более базовый шаблон, на котором строится `base_site.html`. Содержит подключение CSS/JS Admin                                |
| `popup_response.html`      | Ответ для всплывающих окон при выборе ForeignKey через «плюс»                                                                    |
| `app_index.html`           | Страница со списком моделей внутри приложения (`/admin/app/`)                                                                    |

---

##### 2.1.2. Когда они используются

* `change_list.html` → таблица объектов и фильтры
* `change_form.html` → форма редактирования или добавления объекта
* `delete_confirmation.html` → окно подтверждения удаления
* `object_history.html` → журнал изменений объекта

Все остальные (login, base, popup) — вспомогательные, для базовой структуры и функционала админки.

---

##### 2.1.3. Как их можно переопределять

* Полностью: создать свой файл с таким же именем в `templates/admin/`
* Частично: использовать `{% extends "admin/change_list.html" %}` или `{% extends "admin/change_form.html" %}` и добавлять блоки (`extrahead`, `content`, `sidebar`)

Например, добавить CSS/JS на все страницы списка объектов:

```html
{% extends "admin/change_list.html" %}

{% block extrahead %}
    {{ block.super }}
    <link rel="stylesheet" href="{% static 'css/global_admin.css' %}">
    <script src="{% static 'js/global_admin.js' %}"></script>
{% endblock %}
```

**1. `extrahead`**

В административных шаблонах Django (`admin/change_list.html` и др.) уже есть определённые блоки,  
которые можно расширять. Блок `extrahead` находится внутри секции <head> HTML-документа.  
И предназначен как раз для этого. Обычно туда добавляют:
- дополнительные стили (<link>),
- скрипты (<script>),
- и т.д.

**2. `{{ block.super }}`**

`{{ block.super }}` — это специальная переменная, которая вставляет содержимое родительского блока   
(того, что было в родительском шаблоне внутри `extrahead`) перед пользовательскими изменениями.

Если её не написать, то новый пользовательский код полностью заменит содержимое родительского блока.

---

#### 2.2. Подключение через `admin.site.register()` или глобальный `AdminSite`

Можно создать кастомный `AdminSite` и подключать ресурсы в `each_context` или через шаблоны.

Пример кастомного `AdminSite`:

```python
from django.contrib.admin import AdminSite

class MyAdminSite(AdminSite):
    site_header = 'Моя Админка'

    def each_context(self, request):
        context = super().each_context(request)
        context['extra_css'] = ['css/global_admin.css']
        context['extra_js'] = ['js/global_admin.js']
        return context

admin_site = MyAdminSite()
```

Дальше используете `admin_site.register(MyModel)` вместо стандартного `admin.site.register()`.


