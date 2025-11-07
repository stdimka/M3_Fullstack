
# Сериалайзеры в DRF — это "формы для API"

* Они принимают **Python-объекты / QuerySet** и превращают их в JSON (или XML, YAML).
* Принимают **данные от клиента (JSON)** и превращают их обратно в Python-объекты + делают валидацию.

---

## Типы сериалайзеров

### 1. `Serializer`

Аналог **`forms.Form`**.

* Определяете поля вручную.
* Всё поведение контролируется явно.

```python
from rest_framework import serializers

class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(max_length=100)
    email = serializers.EmailField()
```

#### Использование сериализатора:

1. Десериализация (получаем данные от пользователя и валидируем)

```python
# Входные данные (например, из POST запроса)
data = {"username": "john", "email": "john@example.com"}

# Создаем сериализатор для десериализации
serializer = UserSerializer(data=data)

# Проверяем валидность данных
if serializer.is_valid():
    validated_data = serializer.validated_data
    print(validated_data)  # {'username': 'john', 'email': 'john@example.com'}
```

2. Сериализация (берём объект и готовим его для ответа клиенту)

```python
# Предположим, есть объект пользователя (например, из базы)
user_instance = {
    "id": 1,
    "username": "john",
    "email": "john@example.com"
}

# Создаем сериализатор для сериализации
serializer = UserSerializer(user_instance)

# Получаем dict
data_dict = serializer.data
print(data_dict)

# Конвертация в JSON строку
from rest_framework.renderers import JSONRenderer

json_bytes = JSONRenderer().render(serializer.data)
print(json_bytes)  # b'{"id":1,"username":"john","email":"john@example.com"}'

json_str = json_bytes.decode('utf-8')
print(json_str)  # '{"id":1,"username":"john","email":"john@example.com"}'
```
---

### 2. `ModelSerializer`

Аналог **`forms.ModelForm`**.

* Автоматически генерирует поля на основе модели.
* Может явно переопределяться.

```python
from rest_framework import serializers
from myapp.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email"]
```

---

### 3. `ListSerializer`

Используется **для коллекций объектов**.  
Обычно не пишется вручную — DRF применяет автоматически, если `many=True`.

```python
users = User.objects.all()
serializer = UserSerializer(users, many=True)
serializer.data  
# [{'id': 1, 'username': 'john'}, ...]
```

---

### 4. `HyperlinkedModelSerializer`

Как `ModelSerializer`, но вместо `id` вставляет ссылки (`url`). Удобно для **REST-стиля с гиперссылками**.

```python
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ["url", "username", "email"]
```

---

## Типы полей сериалайзеров

Почти как у Django Forms, но для API:

| Поле в DRF                   | Аналог в Forms       | Пример                                                                           |
| ---------------------------- | -------------------- | -------------------------------------------------------------------------------- |
| `CharField`                  | `forms.CharField`    | `username = serializers.CharField(max_length=100)`                               |
| `EmailField`                 | `forms.EmailField`   | `email = serializers.EmailField()`                                               |
| `IntegerField`               | `forms.IntegerField` | `age = serializers.IntegerField(min_value=0)`                                    |
| `BooleanField`               | `forms.BooleanField` | `is_active = serializers.BooleanField()`                                         |
| `DateField`, `DateTimeField` | `forms.DateField`    | `birthday = serializers.DateField()`                                             |
| `ChoiceField`                | `forms.ChoiceField`  | `role = serializers.ChoiceField(choices=[("admin", "Admin"), ("user", "User")])` |
| `SerializerMethodField`      | — (только в DRF)     | `full_name = serializers.SerializerMethodField()`                                |

Для связей моделей:

* `PrimaryKeyRelatedField` — хранит id связанной модели.
* `StringRelatedField` — выводит `__str__`.
* `SlugRelatedField` — работает по `slug_field`.
* `Nested Serializer` — прямо вложенный сериалайзер.

---

## Методы валидации

### 1. `validate_<field>()`

Проверка **отдельного поля** (аналог `clean_<field>()` в Forms).

```python
class UserSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        if "spam" in value:
            raise serializers.ValidationError("Email недопустим")
        return value
```

---

### 2. `validate(self, data)`

Проверка **всех полей вместе** (аналог `clean()` в Forms).

```python
class RegisterSerializer(serializers.Serializer):
    password = serializers.CharField()
    confirm_password = serializers.CharField()

    def validate(self, data):
        if data["password"] != data["confirm_password"]:
            raise serializers.ValidationError("Пароли не совпадают")
        return data
```

---

### 3. `create()` и `update()`

Аналог `save()` у форм.

* `create()` вызывается при `serializer.save()` для новых объектов.
* `update()` — для обновления.

```python
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "email"]

    def create(self, validated_data):
        return User.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        instance.save()
        return instance
```

---

## Переопределение поведения

1. Добавить новое вычисляемое поле:

```python
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["username", "email", "full_name"]

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
```

---

2. Вложенные сериалайзеры:

```python
class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ["bio", "location"]

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer()

    class Meta:
        model = User
        fields = ["username", "email", "profile"]
```

---

3. Использование `many=True`:

```python
class BookSerializer(serializers.Serializer):
    title = serializers.CharField()

class AuthorSerializer(serializers.Serializer):
    name = serializers.CharField()
    books = BookSerializer(many=True)
```

---

✅ Если свести в аналогию:

* `Serializer` ≈ `Form`
* `ModelSerializer` ≈ `ModelForm`
* `validate_<field>` ≈ `clean_<field>`
* `validate` ≈ `clean`
* `create/update` ≈ `save`

