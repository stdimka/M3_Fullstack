## Задание:
1.) Заменить  id автора при вывода на имя
2.) Разрешить ввод книги, где автор будет - имя, а не id


## Замена в сериалайзере Book id автора на его имя

У вас сейчас всё работает «в лоб» — `BookSerializer` возвращает `author` как `id`.
Давайте перепишем его на **базовый `Serializer`**, добавим `to_representation()` и `to_internal_value()`, чтобы:

1. При выводе `author` был **имя автора**.
2. При вводе книги можно было передавать `author` в виде строки (имени).


```python
from rest_framework import serializers
from .models import Author, Book

class BookSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(max_length=200)
    year_published = serializers.IntegerField()
    is_deleted = serializers.BooleanField(default=False)
    author = serializers.CharField(max_length=100)  # будем принимать/отдавать имя

    def to_representation(self, instance: Book):
        """Отдаем author как имя"""
        rep = super().to_representation(instance)
        rep['author'] = instance.author.name
        return rep

    def to_internal_value(self, data):
        """Принимаем author как имя, а внутри храним id"""
        validated_data = super().to_internal_value(data)

        author_name = validated_data.pop('author')
        try:
            author = Author.objects.get(name=author_name)
        except Author.DoesNotExist:
            raise serializers.ValidationError(
                {"author": f"Автор '{author_name}' не найден"}
            )

        validated_data['author'] = author
        return validated_data

    def create(self, validated_data):
        return Book.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.year_published = validated_data.get('year_published', instance.year_published)
        instance.is_deleted = validated_data.get('is_deleted', instance.is_deleted)
        instance.author = validated_data.get('author', instance.author)
        instance.save()
        return instance
```

---

### Пример работы:

**POST запрос**

```json
{
  "title": "Война и мир +++",
  "year_published": 1869,
  "author": "Лев Толстой"
}
```

Если в БД уже есть `Author(name="Лев Толстой")`, книга создастся.

---

**GET ответ**

```json
{
  "id": 1,
  "title": "Война и мир +++",
  "year_published": 1869,
  "is_deleted": false,
  "author": "Лев Толстой"
}
```

---

## Изменение ТЗ: если автора нет, то он должен создаться

Решение проще некуда: вместо поиска автора, и возврата ошибки, если не найден

```python
        author_name = validated_data.pop('author')
        try:
            author = Author.objects.get(name=author_name)
        except Author.DoesNotExist:
            raise serializers.ValidationError(
                {"author": f"Автор '{author_name}' не найден"}
            )

        validated_data['author'] = author
```

просто сразу же ищем или создаём:

```python
        author, _ = Author.objects.get_or_create(name=author_name)

        validated_data['author'] = author
```

Обновлённый сериализатор:

```python

    def to_internal_value(self, data):
        """Принимаем author как имя, а внутри храним объект"""
        validated_data = super().to_internal_value(data)

        author_name = validated_data.pop('author')
        author, _ = Author.objects.get_or_create(name=author_name)

        validated_data['author'] = author
        return validated_data
```


### Теперь как работает:

📌 **POST**

```json
{
  "title": "Белая гвардия",
  "year_published": 1925,
  "author": "Михаил Булгаков"
}
```

Если автора «Михаил Булгаков» нет в БД, он создастся автоматически.

---

**GET**

```json
{
  "id": 21,
  "title": "Белая гвардия",
  "year_published": 1925,
  "is_deleted": false,
  "author": "Михаил Булгаков"
}
```

--- 

## Проверка книг на дубликаты

Добавим проверку валидации: у **одного автора не может быть две книги с одинаковым названием**.

Для этого добавим метод `validate` сериализатора (аналог `clean` в формах)

```python
    def validate(self, attrs):
        """Запрещаем дублирование книг у одного автора"""
        author = attrs.get("author")
        title = attrs.get("title")

        if self.instance:  # update
            exists = Book.objects.filter(
                author=author, title=title
            ).exclude(id=self.instance.id).exists()
        else:  # create
            exists = Book.objects.filter(author=author, title=title).exists()

        if exists:
            raise serializers.ValidationError(
                {"title": f"У автора '{author.name}' книга '{title}' уже существует"}
            )

        return attrs
```

---

### Теперь примеры

**Создание**

```json
{
  "title": "Белая гвардия",
  "year_published": 1925,
  "author": "Михаил Булгаков"
}
```

**Вернёт ошибку:**

```json
{
  "title": ["У автора 'Михаил Булгаков' книга 'Белая гвардия' уже существует"]
}
```

---

**Создание другой книги того же автора**

```json
{
  "title": "Собачье сердце",
  "year_published": 1925,
  "author": "Михаил Булгаков"
}
```

**Результат:**

```json

{
    "id": 22,
    "title": "Собачье сердце",
    "year_published": 1925,
    "is_deleted": false,
    "author": "Михаил Булгаков"
}
``