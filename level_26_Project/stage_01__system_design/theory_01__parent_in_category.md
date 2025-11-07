# Иерархия категорий

Поле `parent` в модели `Category` добавляется для реализации **иерархии категорий** — то есть вложенных категорий


## 1. Зачем нужна иерархия?

В интернет-магазине часто бывает не просто список категорий, а **дерево**:

* Электроника

  * Смартфоны
  * Ноутбуки
  * Телевизоры
* Одежда

  * Мужская
  * Женская
* Аксессуары

Несколько уровней категорий помогают лучше ориентироваться в большом и сложном ассортименте.

---

## 2. Как работает поле `parent`

```python
class Category(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='children'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

* `parent` — **ссылка на ту же модель** (`'self'`)
* Если `parent = None`, категория — **верхнего уровня** (например, «Электроника»)
* Если `parent` указан, категория — **подкатегория** (например, «Смартфоны» → parent = «Электроника»)
* `related_name='children'` позволяет получать все подкатегории:

  ```python
  electronics.children.all()  # возвращает смартфоны, ноутбуки, телевизоры
  ```

---

## 3. Примеры использования

### 3.1. Пример создания категорий

```python
# Верхняя категория
electronics = Category.objects.create(name="Электроника", slug="electronics")

# Подкатегории
smartphones = Category.objects.create(name="Смартфоны", slug="smartphones", parent=electronics)
laptops = Category.objects.create(name="Ноутбуки", slug="laptops", parent=electronics)

# Плоская категория (без родителя)
clothing = Category.objects.create(name="Одежда", slug="clothing")
```
* electronics.parent → None  
* smartphones.parent → <Category: Электроника>  
* electronics.children.all() → вернёт `[smartphones, laptops]`


### 3.2. Пример получения категорий

```python
for category in Category.objects.filter(parent=None):
    print(category.name)
    for sub in category.children.all():
        print(" -", sub.name)
```

Вывод:

```
Электроника
 - Смартфоны
 - Ноутбуки
 - Телевизоры
Одежда
 - Мужская
 - Женская
```

### 3.3. Фильтрация товаров по категории и её подкатегориям

```python
# Все товары в "Электроника" и её подкатегориях
category = Category.objects.get(name="Электроника")
subcategories = category.children.all()
products = Product.objects.filter(category__in=[category, *subcategories])
```

### 3.4. Получение иерархии категорий с помощью рекурсии

Предложенная схема `models.ForeignKey('self', ...)`позволяет создавать иерархию ЛЮБОЙ глубины,   
потому что каждая категория может ссылаться на любую другую категорию в качестве родителя.

#### Обойти всё дерево категорий удобнее всего с помощью рекурсии

Django сам рекурсивно не строит дерево, но можно через Python:

```python
def get_all_subcategories(category):
    subcategories = []
    for child in category.children.all():
        subcategories.append(child)
        subcategories.extend(get_all_subcategories(child))
    return subcategories

all_subs = get_all_subcategories(root)
print([c.name for c in all_subs])
# ['Смартфоны', 'Android', 'Samsung']

```

#### Применение рекурсии в фильтрации товаров

Если нужно выбрать все товары в категории и её подкатегориях на любом уровне:

```python
from itertools import chain

all_subcategories = get_all_subcategories(root)
products = Product.objects.filter(category__in=chain([root], all_subcategories))

```

## 4. Рекурсивная модель VS Фиксированные модели


| Критерий                | Рекурсивная модель (`parent = ForeignKey('self')`) | Фиксированные модели (`Category`, `SubCategory`, ...) |
| ----------------------- | -------------------------------------------------- | ----------------------------------------------------- |
| **Гибкость**            | Любая глубина вложенности                          | Жёстко ограничена (например, 2–3 уровня)              |
| **Простота структуры**  | Одна таблица                                       | Несколько таблиц                                      |
| **Запросы к БД**        | Часто рекурсивные или множественные JOIN           | Простые прямые запросы                                |
| **Производительность**  | Умеренная при малых данных, снижается с глубиной   | Быстрая, предсказуемая                                |
| **Администрирование**   | Удобно (одна форма, дерево)                        | Сложнее (разные модели и связи)                       |
| **Масштабируемость**    | Отличная                                           | Плохая при увеличении глубины                         |
| **Реализация в Django** | Простая, но возможна рекурсия                      | Простая, но негибкая                                  |
| **Типичные случаи**     | Интернет-магазин с динамической категоризацией     | Магазин с фиксированными категориями (1–2 уровня)     |

---

### Вывод

* **Рекурсивная модель (`self`)** — универсальна, подходит для деревьев произвольной глубины.

  > Хороша для каталогов, где структура может меняться.
* **Фиксированные модели** — быстрее и проще при известной структуре (например, максимум 2 уровня).

  > Идеальны для стабильных, заранее известных иерархий.

