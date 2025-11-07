## **4️ Доступ и права (Permissions)**

Управление видимостью и возможностями пользователя в админке:

---

### 1. `has_add_permission(self, request)`

**Что делает:** определяет, может ли пользователь добавлять новые объекты.

**Применение:**

```python
class BookAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # только суперпользователь может добавлять книги
        return request.user.is_superuser
```

✅ Если возвращает `False`, кнопка **«Добавить книгу»** исчезает.

---

### 2. `has_change_permission(self, request, obj=None)`

**Что делает:** разрешает редактирование объектов.

**Применение:**

```python
class BookAdmin(admin.ModelAdmin):
    def has_change_permission(self, request, obj=None):
        # пользователи могут менять только свои книги (например, если у Book есть поле owner)
        if obj is None:
            return True  # для списка объектов
        return obj.author.user == request.user
```

---

### 3. `has_delete_permission(self, request, obj=None)`

**Что делает:** разрешает удаление объектов.



```python
class BookAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        # запрещаем удаление всех книг
        return False
```

По умолчанию (`obj=None`) разрешение касается всех без исключения объектов модели.  
Но, при желании, можно указать разрешения для конкретных объектов.

```python
class BookAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        if obj is None:
            # проверка на уровне списка: кнопка "Удалить выбранное"
            return request.user.is_superuser
        # проверка для конкретного объекта
        return obj.author.user == request.user  # удалять может только автор книги

```

✅ В админке исчезает кнопка удаления.

---

### 4. `has_view_permission(self, request, obj=None)`

**Что делает:** разрешает просмотр объекта.

```python
class BookAdmin(admin.ModelAdmin):
    def has_view_permission(self, request, obj=None):
        # только сотрудники фирмы могут видеть список и отдельные книги
        if not request.user.is_staff:
            return False
        
        # если obj=None, проверка списка объектов
        if obj is None:
            return True
        
        # проверка для конкретного объекта
        return True
```

---

### 5. `get_queryset(self, request)`

**Что делает:** кастомизирует набор объектов, которые видит пользователь в списке.

**Применение:**

```python
class BookAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # показываем только книги текущего пользователя
        return qs.filter(author__user=request.user)
```

✅ Это влияет на **все списки и фильтры** в админке.

---

### 6. `get_readonly_fields(self, request, obj=None)`

**Что делает:** динамически делает поля только для чтения.

**Применение:**

```python
class BookAdmin(admin.ModelAdmin):
    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('year_published',)  # обычный пользователь не сможет менять год
        return ()
```

✅ Полезно для динамического контроля доступа в форме редактирования.


## Почему все этих прав не достаточно?


---

### 1 Необходимы системные права на саму модель

* Django админка проверяет встроенные права модели (`view`, `add`, `change`, `delete`) из `auth_permission`.
* Если пользователь не имеет системного права `view_book`,   
* то даже если `has_view_permission` возвращает `True`, админка скроет всю модель.

> То есть метод `has_view_permission` позволяет дополнительно ограничивать права, но он не заменяет системные права.

---

### 2 `obj=None` vs `obj=<Book>`

* Ваш метод разрешает `obj=None` → пользователь видит список.
* Но если **у пользователя нет права `view_book`**, то Django **даже список не покажет**.

---


### Решение: добавить права пользователя через админку Django

1. Зайдите в админку под суперпользователем.
2. Найдите модель User.
3. Выберите пользователя, которому хотите дать право (пользователь УЖЕ должен быть зарегистрирован!).
4. В разделе `User permissions` (Права пользователя) отметьте “Can view book”.
5. Сохраните изменения.


