## Subquery / OuterRef

1. **OuterRef** — это «ссылка» на текущий объект в основном запросе.

   * Пример: мы перебираем авторов, OuterRef позволяет в подзапросе узнать `id` именно этого автора.

2. **Subquery** — это маленький запрос внутри основного запроса.

   * Пример: для каждого автора подзапрос ищет рейтинг его лучшей книги и возвращает это число как колонку.

3. **Как это работает?**:
   
   * Мы отдельно создаём QuerySet и затем помещаем его внутрь другого QuerySet

4. **Зачем мы это делаем?**: 
 
  * Чтобы в итоге получать один запрос и выполнить его в SQL, а не в Python.


---

### ПРИМЕР

Есть две модели:

```python
from django.db import models

class Author(models.Model):
    name = models.CharField(max_length=100)

class Book(models.Model):
    title = models.CharField(max_length=100)
    author = models.ForeignKey(Author, related_name='books', on_delete=models.CASCADE)
    rating = models.IntegerField()
```

**Задача**:  
для каждого автора получить рейтинг самой популярной книги (max `rating`) без загрузки всех книг в память.

---

#### Решение через `Subquery`

```python
from django.db.models import OuterRef, Subquery

# Подзапрос: выбираем рейтинг книги для данного автора (OuterRef('pk'))
best_book_rating = Book.objects.filter(
    author=OuterRef('pk')   # Ссылка на автора в основном запросе
).order_by('-rating').values('rating')[:1]  # Берём только лучший рейтинг

# Основной запрос: добавляем аннотацию с этим рейтингом
authors = Author.objects.annotate(
    top_rating=Subquery(best_book_rating)
)

# Выводим результат
for author in authors:
    print(author.name, author.top_rating)
```

---

#### Как это работает

1. `OuterRef('pk')` — ссылается на поле `pk` текущего объекта `Author` в основном запросе.
2. `Subquery(best_book_rating)` — превращает подзапрос в колонку, которую можно аннотировать в основном QuerySet.
3. `[:1]` — важно, чтобы подзапрос возвращал только одно значение, иначе будет ошибка.


---

#### Иными словами:

> Основной запрос — это «список авторов».
> Subquery + OuterRef — это «мини-запрос для каждого автора»,  
  который смотрит только его книги и считает что-то (например, лучший рейтинг).

Итог: **один SQL-запрос**, который считает для каждого автора рейтинг его лучшей книги, без загрузки всех книг в память.

