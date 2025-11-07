## 1. Проблема N+1 запросов

GraphQL по умолчанию резолвит каждый уровень по отдельности.
Пример запроса:

```graphql
query {
  allAuthors {
    id
    name
    books {
      id
      title
      detail {
        summary
      }
    }
  }
}
```

Если у нас 10 авторов, и у каждого по 5 книг, GraphQL (без оптимизации) может сделать:

* 1 запрос, чтобы получить авторов,
* затем 10 запросов, чтобы получить книги,
* и ещё 50 запросов, чтобы получить `BookDetail` для каждой книги.
  Итого — **61 запрос** вместо одного объединённого.

Для **Django + Graphene** оптимизация обычно строится **по двум уровням**:

---

## 1 Оптимизация на уровне Django ORM

Используем **жадную загрузку** связей через:

* `select_related` — для **ForeignKey** и **OneToOne**
* `prefetch_related` — для **ManyToMany** и **reverse ForeignKey**

Пример:

```python
# Загружаем книги с авторами и жанрами за минимум запросов
books = Book.objects.select_related("author").prefetch_related("genres")
```

Эффект: при резолвере `books` данные всех связанных моделей будут загружены в  
одном/двух SQL-запросах, вместо множества отдельных.

---

## 2 Оптимизация на уровне GraphQL с DataLoader

Даже при использовании `select_related/prefetch_related` могут возникать  
**N+1 проблемы** в полях GraphQL, где данные получаются через резолверы:

```python
class BookType(graphene.ObjectType):
    author = graphene.Field(AuthorType)

    def resolve_author(book, info):
        return info.context["author_loader"].load(book.author_id)
```

* **DataLoader** собирает все `.load()` за один “тик” выполнения и делает один SQL-запрос
* **Кэширует** результаты на время запроса

Особенно важно для **вложенных GraphQL-запросов**, где одни и те же авторы/жанры могут запрашиваться несколько раз.

---

## 3 Комбинированный подход (лучший вариант)

| Уровень | Инструмент         | Как используется                                                                                 |
| ------- | ------------------ | ------------------------------------------------------------------------------------------------ |
| ORM     | `select_related`   | Для ForeignKey/OneToOne внутри запроса, чтобы не делать отдельные `.get()`                       |
| ORM     | `prefetch_related` | Для ManyToMany или обратных связей, чтобы собрать все связанные объекты                          |
| GraphQL | DataLoader         | Для всех резолверов, вызывающих `.get()` или отдельные ORM-запросы, особенно при вложенных полях |

Пример оптимизированного резолвера:

```python
def resolve_books(root, info):
    # ORM загружает книги + авторов + жанры за минимальное количество запросов
    return Book.objects.select_related("author").prefetch_related("genres")

class BookType(graphene.ObjectType):
    author = graphene.Field(AuthorType)

    def resolve_author(book, info):
        # GraphQL DataLoader собирает всех авторов и делает один батч-запрос
        return info.context["author_loader"].load(book.author_id)
```

---

### Вывод

* **Всегда сначала оптимизируйте ORM-запросы** (`select_related`/`prefetch_related`).
* **Затем подключайте DataLoader**, чтобы решить проблему N+1 на уровне **GraphQL резолверов**.
* **Комбинация** этих подходов даёт **максимальную производительность** и минимальное количество SQL-запросов.
