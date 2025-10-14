from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Book(models.Model):
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='books')
    title = models.CharField(max_length=200)
    year_published = models.IntegerField()
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.author})"


class BookDetail(models.Model):
    book = models.OneToOneField(Book, on_delete=models.CASCADE, related_name='detail')
    summary = models.TextField()
    page_count = models.IntegerField()

    def __str__(self):
        return f"Details for {self.book.title}"


class Genre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    books = models.ManyToManyField(Book, related_name='genres')

    def __str__(self):
        return self.name
