## 5 Поведение и кастомизация (Behavior & Customization)

---

### 1. Автозаполнение и подготовка полей

#### 1.1. `prepopulated_fields` – автоматически заполняет в slug-формате одно поле на основе значений других полей.

Иными словами, алгоритма заполнения `prepopulated_fields`:
- Пользователь вводит текст в поле(я)-источник.
- `JS` в админке следит за вводом.
- Django вызывает JS-скрипт `slugify`, который конвертирует символы поля-источника по правилу:
  - пробелы → -
  - заглавные → строчные
  - кириллица → транслитерация (зависит от локали и реализации slugify)
  - убираются символы вроде `!?@#$%^&*`
- Получившаяся строка подставляется в поле назначения.

```python
class Book(models.Model):
    title = models.CharField(max_length=200)
    year_published = models.IntegerField()
    code = models.SlugField(max_length=200, unique=True)  # ← это поле


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    prepopulated_fields = {
        'code': ('title', 'year_published')
    }

# title="Война и мир", year_published=1869 → code="voyna-i-mir-1869"
```

В примере выше в админке, после заполнения полей `title` ("Война и мир") и `year_published` (1869),  
поле `code` автоматически заполнится значением `"voyna-i-mir-1869"`

⚠️ Стоит обратить внимание!
#### 1.2. `autocomplete_fields` – делает поле связи (`ForeignKey`, `ManyToMany`) с автоподбором через поиск:

  В форме редактирования можно будет искать автора или жанры через строку поиска, по первым символам.
  В результате в выпадающем списке появятся релевантные варианты, а не весь длиннющий список.

  Основные требования:
  - работает только для `ForeignKey`, `ManyToMany` 
  - поля поиска должны быть указаны в `search_fields` связанных моделей `AuthorAdmin` и `AuthorAdmin`
  - из формы модели `Book` НЕ ДОЛЖНЫ быть исключены поля автозаполнения (`author`, `genres`)


- Настройка основной модели (Book)
  * `autocomplete_fields = ['author', 'genres']`

- Настройка модели `AuthorAdmin` 
  * ` search_fields = ('name',) `

- Настройка модели `GenreAdmin`
  * `search_fields = ('name',)` 

  Всего изменений в админке:

```python
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    autocomplete_fields = ['author', 'genres']

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    search_fields = ('name',)   # теперь поиск автора работает

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = ('name',)   # теперь поиск жанра работает
```

---

### 2. Действия и массовые операции

* `actions` – список действий, доступных для выбранных объектов в списке.  

  Можно создавать свои функции, которые будут в том же меню, что и удаление

```python
def mark_deleted(modeladmin, request, queryset):
    queryset.update(is_deleted=True)
mark_deleted.short_description = "Пометить выбранные книги как удалённые"

class BookAdmin(admin.ModelAdmin):
    actions = [mark_deleted]
```

* `actions_on_top` / `actions_on_bottom` – включение отображения кнопок действий сверху и снизу списка объектов:

  Если оба параметра = True, кнопка будет и сверху, и снизу
```python
class BookAdmin(admin.ModelAdmin):
  actions_on_top = True
  actions_on_bottom = True
```

---

### 3. Сохранение и копирование объектов

* `save_as` – добавляет кнопку **"Сохранить как новый"**, позволяя копировать объект:

```python
class BookAdmin(admin.ModelAdmin):
    save_as = True
```
Зачем это нужно?  
- Если новый объект содержит много одинаковых значений полей с текущим
- Если нужно быстро заполнить базу значениями для демо или тестового режима

Важно:
- Поля ManyToMany нужно будет выбрать заново (или использовать инлайны с поддержкой копирования).
- Кнопка появляется только при редактировании существующего объекта, а не при создании нового.

* `save_on_top` – дублирует кнопки сохранения вверху формы, чтобы не скроллить:

```python
class BookAdmin(admin.ModelAdmin):
    save_on_top = True
```

---

### 4. Оптимизация запросов

* `list_select_related` – для ForeignKey и OneToOne загружает связанные объекты одним SQL-запросом.

```python
class BookAdmin(admin.ModelAdmin):
    list_select_related = ['author']  # авторы загружаются вместе с книгами
```

* `list_prefetch_related` – для ManyToMany и обратных связей (`reverse ForeignKey`) использует `prefetch_related`, чтобы избежать N+1 запросов:

```python
class BookAdmin(admin.ModelAdmin):
      list_prefetch_related = ['genres']
```

---

### 5. Другие полезные настройки

* `date_hierarchy` – добавляет навигацию по датам, обычно для `DateField`/`DateTimeField`:

```python
class BookAdmin(admin.ModelAdmin):
    date_hierarchy = 'published_date'
```

Недостаток: работает ТОЛЬКО в DateField или DateTimeField.  
Как вариант, можно использовать похожий параметр `list_filter = ('year_published',)`,  
что даст выпадающий список с годами слева.

* `empty_value_display` – текст, который будет показан, если поле пустое:

```python
class BookAdmin(admin.ModelAdmin):
    empty_value_display = '-пусто-'
```

* `radio_fields` – вместо выпадающего списка отображает поле как радио-кнопки (для `ForeignKey` или `ChoiceField`):

```python
class BookAdmin(admin.ModelAdmin):
    radio_fields = {"author": admin.VERTICAL}
```

Параметр `admin.VERTICAL`/`admin.HORIZONTAL` задаёт расположение радио-кнопок.

Важно:
- для полей, указанных в `autocomplete_fields` работать не будет!