## 1️ Отображение списка объектов (List Display)

### Отображение и переходы

* `list_display` – какие поля или методы модели показывать в таблице списка.
* `list_display_links` – какие поля в списке будут кликабельны и ведут на страницу редактирования объекта.
* `list_editable` – какие поля можно редактировать прямо в списке без перехода(!) на страницу редактирования.

### **Фильтры и поиск**

* `list_filter` – фильтры по полям (например, даты, Boolean, ForeignKey) для удобной навигации.
* `search_fields` – поля, по которым работает поиск через строку поиска в админке.

### Сортировка и оптимизация

* `ordering` – порядок сортировки объектов по умолчанию.
* `list_select_related` – оптимизация запросов через `select_related` для ForeignKey (уменьшает количество SQL-запросов).
* `list_prefetch_related` – оптимизация для ManyToMany и обратных связей (reverse ForeignKey) через `prefetch_related`.

### Пагинация

* `list_per_page` – количество объектов на одной странице (по умолчанию 100).
* `list_max_show_all` – максимальное количество объектов, если нажать «Показать все».


**ВНИМАНИЕ!**  
В `list_display` мы можем показывать не только реальные поля модели, но и вычисляемые.   
Например, поле жанров в примере ниже.

```python
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author', 'year_published', 'is_deleted', 'genre_list')
    list_display_links = ('title',)
    list_editable = ('is_deleted',)
    list_filter = ('year_published', 'is_deleted', 'author', 'genres')
    search_fields = ('title', 'author__name')
    ordering = ('-year_published',)
    list_select_related = ('author',)  # оптимизация для ForeignKey
    list_prefetch_related = ('genres',)  # оптимизация для ManyToMany

    list_per_page = 4
    list_max_show_all = 15

    def genre_list(self, obj):
        return ", ".join([genre.name for genre in obj.genres.all()])
    genre_list.short_description = 'Жанры'
```

Метод `.short_description` меняет дефолтное имя `Genre list` на пользовательское имя 'Жанры'.