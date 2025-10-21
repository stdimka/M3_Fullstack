# 2. Базовые сериализаторы


Базовый сериализатор (`serializers.Serializer`) отличается от `ModelSerializer` в основном тем, что он более "ручной":

* нужно самим описывать все поля,
* самим реализовать `create()` и `update()`,
* самим заботиться о валидации моделей и сохранении.

Поэтому основные принципы построения, методы валидации и т.д. удобнее всего рассмореть именноа на нём


---

## 1. Таблица полей (модель / форма / сериализатор)

| Модель (`models`)        | Форма (`forms`)                          | Сериализатор (`serializers`)                                                          |
| ------------------------ | ---------------------------------------- | ------------------------------------------------------------------------------------- |
| `models.CharField`       | `forms.CharField`                        | `serializers.CharField`                                                               |
| `models.TextField`       | `forms.CharField(widget=forms.Textarea)` | `serializers.CharField`                                                               |
| `models.IntegerField`    | `forms.IntegerField`                     | `serializers.IntegerField`                                                            |
| `models.FloatField`      | `forms.FloatField`                       | `serializers.FloatField`                                                              |
| `models.BooleanField`    | `forms.BooleanField`                     | `serializers.BooleanField`                                                            |
| `models.DateField`       | `forms.DateField`                        | `serializers.DateField`                                                               |
| `models.DateTimeField`   | `forms.DateTimeField`                    | `serializers.DateTimeField`                                                           |
| `models.TimeField`       | `forms.TimeField`                        | `serializers.TimeField`                                                               |
| `models.EmailField`      | `forms.EmailField`                       | `serializers.EmailField`                                                              |
| `models.URLField`        | `forms.URLField`                         | `serializers.URLField`                                                                |
| `models.SlugField`       | `forms.SlugField`                        | `serializers.SlugField`                                                               |
| `models.UUIDField`       | `forms.UUIDField`                        | `serializers.UUIDField`                                                               |
| `models.DecimalField`    | `forms.DecimalField`                     | `serializers.DecimalField`                                                            |
| `models.FileField`       | `forms.FileField`                        | `serializers.FileField`                                                               |
| `models.ImageField`      | `forms.ImageField`                       | `serializers.ImageField`                                                              |
| `models.ForeignKey`      | `forms.ModelChoiceField`                 | `serializers.PrimaryKeyRelatedField` (или вложенный `Serializer`)                     |
| `models.ManyToManyField` | `forms.ModelMultipleChoiceField`         | `serializers.PrimaryKeyRelatedField(many=True)` или вложенный `Serializer(many=True)` |
| `models.OneToOneField`   | `forms.ModelChoiceField`                 | `serializers.PrimaryKeyRelatedField` или вложенный `Serializer`                       |

---

## 2. Методы базового сериализатора

### 1. Основные методы для работы с данными
* `is_valid(raise_exception=False)`
  * Проверка входных данных.
  * Сравнение с `form.is_valid()`.
* `save(**kwargs)`
  * Создание или обновление объекта.
  * Вызов `create` или `update` под капотом.
* `data`
  * Доступ к сериализованным данным (аналог `form.cleaned_data`, но уже готовый к JSON).
* `errors`
  * Список ошибок валидации (аналог `form.errors`).

---

### 2. Методы преобразования данных

* `to_internal_value(self, data)`
  * Преобразует внешние данные (JSON, dict) → Python объекты.
  * Сравнение с `form.cleaned_data`. 
* `to_representation(self, instance)`
  * Преобразует объект Python / модель → JSON-совместимый dict.
  * Можно кастомизировать вывод (например, поля, формат даты).

---

### 3. Методы валидации

* `validate_<field>(self, value)`
  * Валидация конкретного поля (аналог `clean_<field>`).
* `validate(self, attrs)`
  * Валидация всего набора данных (аналог `clean`).
* Пользовательские валидаторы через `validators=[...]`

---

### 4. Методы для работы с объектами

* `create(self, validated_data)`
  * Создание нового объекта на основе `validated_data`.
* `update(self, instance, validated_data)`
  * Обновление существующего объекта.
* Связь с `save()`: вызывается автоматически при `serializer.save()`.

---

### 5. Методы вспомогательные / кастомные

* `get_<field>(self, obj)`
  * Для `SerializerMethodField` (кастомное вычисляемое поле).
* `run_validation(self, data)`
  * Запускает всю цепочку валидации: `to_internal_value` → `validate_<field>` → `validate`.
* `build_instance(self, validated_data)` (редко используется)
  * Создает объект без сохранения (внутренне в DRF).


## 3. Особые свойства полей сериализаторов

| Свойство           | Назначение                                                                         |
| ------------------ | ---------------------------------------------------------------------------------- |
| `read_only=True`   | Поле только для чтения (возвращается в JSON, но не принимается во входных данных). |
| `write_only=True`  | Поле только для записи (например, пароль: можно передать, но не получишь обратно). |
| `required=False`   | Поле необязательное.                                                               |
| `default=...`      | Значение по умолчанию.                                                             |
| `allow_null=True`  | Разрешено `null`.                                                                  |
| `allow_blank=True` | Разрешена пустая строка (для CharField).                                           |
| `validators=[...]` | Кастомные валидаторы.                                                              |



## 4. Что ещё важно знать про базовый сериализатор?

1. **Гибкость:**

   * можно сериализовать не только модели, но и вообще любые Python-объекты (словарь, кортеж, результат внешнего API).

2. **Философия:**

   * `Serializer` ближе к "слою трансформации данных", чем к формам;
   * Forms жёстко завязаны на HTML, Serializer — на JSON.

3. **Сложность:**

   * писать дольше, чем `ModelSerializer`;
   * зато он полезен, когда модельной привязки **нет** или нужна полная кастомизация.

