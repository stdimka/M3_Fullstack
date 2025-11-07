from django.db import models


class MyappModel(models.Model):
    code = models.CharField(max_length=50, unique=True)
    value = models.TextField()

    def __str__(self):
        return f"{self.code}: {self.value}"

