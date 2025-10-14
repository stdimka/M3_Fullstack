## Самый простой вариант созданий админки `admin.py`

- импортируем нужные модели  
```python
from django.contrib import admin
from .models import Book
```

- и регистрируем их
```python
admin.site.register(Book)
```

**Результат**:  
Простое отображение списка строк в стили, описанном в методе `__str__()` выбранной модели.

Однако, гораздо больше возможностей даёт
## Создание собственного класса `BookAdmin(admin.ModelAdmin)`

```python
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'year_published')

admin.site.register(Book, BookAdmin)
```

**Результат**:  
- Вывод больше не зависит от `__str__()` выбранной модели;
- Модель отображается в удобном табличном виде.

Как видим, одновременно приходится регистрировать и модель, и класс:
```python
admin.site.register(Book, BookAdmin)
```

Эту регистрацию можно сделать более наглядной и компактной с декоратором `@admin.register`

## Использование декоратора `@admin.register()`

```python
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'year_published')
```