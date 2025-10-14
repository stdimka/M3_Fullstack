## Реализация классического обратного запроса через `post.comments.all()`

Для этого придётся добавить в связанные модели поле обратной связи `GenericRelation`:

```python
from django.contrib.contenttypes.fields import GenericRelation

class Post(models.Model):
    title = models.CharField(max_length=100)
    comments = GenericRelation('Comment')  # связь с Comment

class Photo(models.Model):
    url = models.URLField()
    comments = GenericRelation('Comment')

class Comment(models.Model):
    text = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
```

Теперь:

```python
post = Post.objects.get(id=1)
comments = post.comments.all()  # уже работает напрямую
```

---

## Более читабельный вариант решения`post.comments.all()`

Сделать связанные модели более компактными можно с помощью переноса поля `comments` в миксин:

Этот миксин (`Commentable`) должен быть АБСТРАКТНЫМ.  
В противном случае Django создаст ненужную модель `Commentable`.


```python
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


class Comment(models.Model):
    text = models.TextField()
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')


class Commentable(models.Model):
    """Миксин для моделей, у которых могут быть комментарии"""
    comments = GenericRelation(Comment)

    class Meta:
        abstract = True


class Post(Commentable):
    title = models.CharField(max_length=100)


class Photo(Commentable):
    url = models.URLField()
```

---

Теперь всё становится гораздо проще:

```python
post = Post.objects.create(title="Первая запись")
photo = Photo.objects.create(url="https://example.com/photo.jpg")

# Добавляем комментарий к посту
Comment.objects.create(
    text="Отличная статья!",
    content_object=post
)

# Добавляем комментарий к фото
Comment.objects.create(
    text="Красивое фото!",
    content_object=photo
)

# Получаем комментарии напрямую
print(post.comments.all())   # <QuerySet [<Comment: Отличная статья!>]>
print(photo.comments.all())  # <QuerySet [<Comment: Красивое фото!>]>
```

