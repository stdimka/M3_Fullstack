### Django TemplateView — краткий обзор и пример

`TemplateView` — это встроенное представление (view) из Django `django.views.generic.base.TemplateView`, которое предназначено для отображения HTML-шаблона без необходимости вручную писать метод `get()` или `render()`.

Идеально подходит для простых статических страниц, например: "О нас", "Контакты", "Главная", и т.п.

---

### 📌 Основные особенности `TemplateView`:

* Наследуется от `View`
* Использует метод `get()` по умолчанию
* Требует указания атрибута `template_name`
* Можно передать дополнительные данные в шаблон через метод `get_context_data`

---

### ✅ Пример

**views.py:**

```
from django.views.generic import TemplateView

class AboutView(TemplateView):
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "О нас"
        context["author"] = "Компания My Company"
        return context
```

**urls.py:**

```
from django.urls import path
from .views import AboutView

urlpatterns = [
    path("about/", AboutView.as_view(), name="about"),
]
```

**templates/about.html:**

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ page_title }}</title>
</head>
<body>
    <h1>{{ page_title }}</h1>
    <p>Эта страница создана: {{ author }}</p>
</body>
</html>
```

---

При желании, можно обойтись и без `views.py`:
```
urlpatterns = [
    path('', TemplateView.as_view(
        template_name="index.html",
        extra_context={"page_title": "О нас", "author": "Компания My Company"}
    ), name="home"),
]
```

### 📝 Когда использовать:

* Для отображения шаблонов без сложной логики
* Когда нужны простые статические страницы
* Когда требуется переиспользовать шаблоны с данными контекста

