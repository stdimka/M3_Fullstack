from django.db import models


class Book(models.Model):
    title = models.CharField("Название", max_length=200)
    author = models.CharField("Автор", max_length=100)
    year = models.PositiveIntegerField("Год издания")
    description = models.TextField("Описание", blank=True)

    def __str__(self):
        return f"{self.title} ({self.author})"
