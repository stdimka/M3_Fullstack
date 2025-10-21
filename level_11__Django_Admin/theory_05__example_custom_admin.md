Идея связанных выпадающих списков:
https://docs.google.com/spreadsheets/d/1hzuNn8Vj4Y7t0UEJ4herox6xFIPodDhYmEwQFQPAqVY/edit?gid=1128450929#gid=1128450929

Реализация в Django:
https://it4each.com/blog/sviazannye-vypadaiushchie-spiski-v-adminke-django/

### Нестандартные изменения админки:
```python
class OrderItemForm(forms.ModelForm):
    class Meta:
        model = OrderItem
        fields = "__all__"

    subcat = RestrictedModelChoiceField(
        Subcategory.objects.all(),
        restrict_on_form_field="cat",
        restrict_on_relation="allowedcombination__cat",
    )
    name_good = RestrictedModelChoiceField(
        Good.objects.all(),
        restrict_on_form_field="subcat",
        restrict_on_relation="allowedcombination__subcat",
    )
```

1. **Кастомная форма `OrderItemForm` (`dropdown/forms.py`)**:
- **Что добавлено**: 
    - В форме `OrderItemForm` создано собственное нестандартное поле Django, реализующее зависимость от выбора предыдущего поля.
    - Поля `subcat` и `name_good` используют `RestrictedModelChoiceField`. Это поле:
      - Ограничивает варианты выбора в выпадающих списках на основе значений других полей (`restrict_on_form_field` и `restrict_on_relation`).
      - Генерирует JSON-данные с ограничениями (`data-restrictions`) и связывает их с HTML-элементом `<select>` через кастомный виджет `RestrictedSelect`.
  - **Как меняет админку**: 
    - Стандартная админка не умеет динамически фильтровать опции выпадающих списков на основе выбора в другом поле. 
    - `OrderItemForm` встраивает эту логику в админку, заменяя стандартное поведение полей `ModelChoiceField`.

2. **JavaScript-скрипт (`static/js/restricted-model-choice-field.js`)**:
   - **Что добавлено**: 
     - Скрипт обрабатывает события `change` и `DOMContentLoaded`, чтобы:
       - Динамически скрывать/показывать опции в `<select>` на основе значения связанного поля, используя атрибуты `data-restrictions` и `data-restricted-on`.
       - Поддерживать динамические формсеты (например, в `TabularInline`), обрабатывая имена полей с `__prefix__` (`subcat` и `cat`).
   - **Как меняет админку**: 
     - Добавляем JS-логики для управления зависимыми выпадающими списками, чего нет у стандартной админки.

3. **Интеграция в админку (`dropdown/admin.py`)**:
   - **Что добавлено**: 
     - `OrderItemInline` и `OrderItemAdmin` используют `OrderItemForm` вместо стандартной формы.
     - Это нестандартно, так как стандартная админка не поддерживает динамическую фильтрацию опций в выпадающих списках.
   - **Как меняет админку**: 
     - Замена стандартной формы на `OrderItemForm` позволяет админке отображать выпадающие списки, где выбор зависит от выбора в предыдущем поле.

### Что именно меняется в стандартной админке:
- **Поля формы**: 
  - Стандартные поля `ModelChoiceField` заменяются на `RestrictedModelChoiceField`, которое добавляет логику ограничений.
- **Поведение выпадающих списков**: 
  - Стандартные `<select>` становятся динамическими благодаря JavaScript, который фильтрует опции на основе выбора в других полях.
- **Клиентская логика**: 
  - Добавлен кастомный скрипт для обработки событий и обновления интерфейса, что нет в стандартной админке.

### Итог:
Нестандартные изменения вносятся через:
- Кастомное поле `RestrictedModelChoiceField` и виджет `RestrictedSelect` в `forms.py`.
- JavaScript-скрипт `restricted-model-choice-field.js` для клиентской обработки.
- Применение `OrderItemForm` в `admin.py` для замены стандартной формы в `OrderItemInline` и `OrderItemAdmin`.

Эти изменения добавляют в админку функционал связанных выпадающих списков, которого нет в стандартном Django Admin. 
