### Пример
```python
from django.db import models
from django.utils.translation import gettext_lazy as _  # ленивый перевод (из вариантов готовых значений)
import uuid

class Product(models.Model):
    CATEGORY_CHOICES = (
        ('EL', _("Электроника")),
        ('BK', _("Книги")),
        ('CL', _("Одежда")),
        ('FD', _("Еда")),
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(verbose_name=_("Название"), max_length=100,unique=True)
    # допустимо указать verbose_name как позиционный аргумент
    # но следует помнить - это снижает читабельность
    category = models.CharField(_("Категория"), max_length=2, choices=CATEGORY_CHOICES, default='EL')
    description = models.TextField(verbose_name=_("Описание"), blank=True)  # можно оставить пустым в форме
    price = models.DecimalField(verbose_name=_("Цена"), max_digits=10, decimal_places=2)
    is_available = models.BooleanField(verbose_name=_("В наличии"), default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Продукт")
        verbose_name_plural = _("Продукты")
        ordering = ['-created_at']

    def __str__(self):
        return self.name
```

---

### Что можно указывать в поле:

| Аргумент                    | Назначение                                                     |
| --------------------------- | -------------------------------------------------------------- |
| `verbose_name`              | Читаемое имя поля (используется в админке, формах и т.д.)      |
| `max_length`                | Максимальная длина строки (`CharField`, `SlugField` и др.)     |
| `blank`                     | Можно ли оставить пустым в формах (в БД может быть `NOT NULL`) |
| `null`                      | Хранить ли `NULL` в БД (для чисел, дат и т.д.)                 |
| `default`                   | Значение по умолчанию                                          |
| `unique`                    | Должно ли значение быть уникальным                             |
| `choices`                   | Ограничение набора допустимых значений                         |
| `editable`                  | Показывать ли поле в админке/формах                            |
| `primary_key`               | Делает поле основным ключом                                    |
| `auto_now` / `auto_now_add` | Автоматически сохраняет дату/время                             |

---

### Что делает `editable`:

| Параметр         | Поведение поля                                                     |
| ---------------- | ------------------------------------------------------------------ |
| `editable=True`  | Поле **видно и доступно** в формах (в админке, ModelForm и т.п.)   |
| `editable=False` | Поле **не отображается** и **не редактируется** в админке и формах |

---

### Когда указывать `blank=True`:

* Когда поле **необязательное в формах** (например, описание, изображение, коммент).
* Для `CharField`, `TextField`, `EmailField` и т.п., если вы хотите разрешить пустые строки.
* **Важно:** если поле допускает пустое значение и в форме, и в БД — указывайте оба: `blank=True, null=True`.

---

### Нужно ли указывать `verbose_name`?

* **Необязательно**, но **рекомендуется**, особенно если:

  * Вы используете админку.
  * Проект мультиязычный (используйте `_()` для перевода).
  * Хотите задать понятные подписи для форм и таблиц.

---

### Кратко — хорошие практики:

✅ Чётко указывайте `max_length`, `blank`, `null` и `default`  
✅ Используйте `verbose_name` и `Meta.verbose_name` для читаемости  
✅ Всегда определяйте `__str__`  
✅ Указывайте `ordering` в `Meta`  
✅ Используйте `UUIDField` для публичных ID, если не нужны автоинкременты    
    (показывать реальный id публично - плохая практика с точки зрения безопасности)  
✅ Разграничивайте `blank=True` (для форм) и `null=True` (для БД)  

