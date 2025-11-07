## 3. Создание схемы для моделей

### 3.1 Подключение моделей и необходимых классов

В файле `myapp/schema.py` импортируем всё, что нужно:

```python
import graphene
from graphene_django import DjangoObjectType
from .models import Author, Book, BookDetail, Genre
```

* `graphene` — основной модуль GraphQL для Python.
* `DjangoObjectType` — класс, который автоматически превращает модель Django в тип GraphQL.

---

### 3.2 Описание типов для моделей

```python
class AuthorType(DjangoObjectType):
    class Meta:
        model = Author
        fields = '__all__'


class BookDetailType(DjangoObjectType):
    class Meta:
        model = BookDetail
        fields = '__all__'


class BookType(DjangoObjectType):
    class Meta:
        model = Book
        fields = '__all__'

class GenreType(DjangoObjectType):
    class Meta:
        model = Genre
        fields = ('name',)
```
Связи между моделями graphQL находит автоматически.  
Поэтому нет необходимости указывать поля обратного вызова типа `genres` и `detail`.  
Но мы можем убрать из запросов лишние поля, тип `id` в Genre.

---

### 3.3 Описание Query (запросов)

Создаём корневой объект Query, через который будем получать данные.

```python
class Query(graphene.ObjectType):
    all_books = graphene.List(BookType)
    all_authors = graphene.List(AuthorType)
    book_by_id = graphene.Field(BookType, id=graphene.Int(required=True))

    def resolve_all_books(root, info):
        return Book.objects.filter(is_deleted=False)

    def resolve_all_authors(root, info):
        return Author.objects.all()

    def resolve_book_by_id(root, info, id):
        return Book.objects.get(pk=id)
```

* `all_books` — возвращает все книги, кроме удалённых (`is_deleted=False`).
* `all_authors` — список всех авторов.
* `book_by_id(id: Int!)` — возвращает книгу по `id`.

---
### 3.4. Что такое резолвер в GraphQL?

* **Resolver (резолвер)** — это функция, которая отвечает за получение данных для конкретного поля в GraphQL.
* Для каждого поля, которое мы запрашиваете, GraphQL вызывает соответствующий резолвер.
* Если резолвер явно не написан, Graphene автоматически возвращает значение поля модели (для `DjangoObjectType`).
* Резолвер позволяет:

  * Фильтровать данные
  * Проверять права доступа
  * Форматировать или объединять данные перед отправкой клиенту

⚠️ В GraphQL резолвер не является методом класса, даже если он определён внутри класса.  
Graphene просто инспектирует класс (например, Query) и ищет методы, начинающиеся с `resolve_`.  
Когда запрос GraphQL доходит до поля (например, all_books),  
Graphene вызывает этот метод, передавая два аргумента:

* `root` — это родительский объект, из которого пришёл запрос к текущему полю.
  * Для корневого запроса (Query) это обычно None или сам объект запроса.
  * Для вложенных полей — это результат работы предыдущего резолвера.

* `info` — это объект, содержащий контекст запроса, метаданные, и т. д.
  * (Например, `info.context.user` даёт текущего пользователя, для проверки авторизации)

Поэтому у резолвера нет декоратора `@staticmethod`.
(Хотя его можно добавить для чистоты Python кода).

#### 3.4.1 resolve_all_books

```python
def resolve_all_books(root, info):
    return Book.objects.filter(is_deleted=False)
```

* Вызывается, когда клиент делает запрос типа:

```graphql
query {
  allBooks {
    id
    title
  }
}
```

* Что делает резолвер:

  1. Обращается к модели `Book`.
  2. Фильтрует книги, где `is_deleted=False`.
  3. Возвращает список объектов `Book`, которые Graphene превращает в `BookType` с нужными полями.

> Иными словами, резолвер отвечает за **получение и фильтрацию данных для поля `all_books`**.

---

#### 3.4.2 resolve_all_authors

```python
def resolve_all_authors(root, info):
    return Author.objects.all()
```

* Вызывается при запросе типа:

```graphql
query {
  allAuthors {
    id
    name
  }
}
```

* Просто возвращает все объекты `Author` из базы данных.
* Резолвер превращает их в `AuthorType` и возвращает клиенту.

---

#### 3.4.3 resolve_book_by_id

```python
def resolve_book_by_id(root, info, id):
    return Book.objects.get(pk=id)
```

* Вызывается при запросе типа:

```graphql
query {
  bookById(id: 1) {
    id
    title
    author {
      name
    }
  }
}
```

* Аргумент `id` передаётся в резолвер автоматически.
* Резолвер ищет книгу с этим `id` и возвращает объект `Book`.
* Graphene превращает его в `BookType`, включая вложенные связи (`author`, `detail`, `genres`).

---

#### 3.4.4. Резюме

* Резолвер — это **функция, которая говорит GraphQL, как получить данные для конкретного поля**.
* В вашем примере:

  1. `resolve_all_books` → возвращает все книги, кроме удалённых.
  2. `resolve_all_authors` → возвращает всех авторов.
  3. `resolve_book_by_id` → возвращает книгу по конкретному `id`.
* Без резолвера Graphene не знает, как достать данные из базы.

---

### 3.5 Создание схемы

В конце файла `schema.py` создаём объект схемы:

```python
schema = graphene.Schema(query=Query)
```

* На этом этапе `/graphql/` уже может принимать запросы `query { allBooks { id title } }`.

---

### 3.6 Проверка работы

1. Запускаем сервер:

```bash
python manage.py runserver
```

2. Открываем `http://127.0.0.1:8000/graphql/`
3. Пример запросов:

* Только книги с автором и названием
```graphql
query {
  allBooks {
    title
    author {
      name
    }
```

* Полный запрос
```graphql
query {
  allBooks {
    id
    title
    yearPublished
    author {
      name
    }
    detail {
      summary
      pageCount
    }
    genres {
      name
    }
  }
}
```

4. Ответ JSON будет содержать все поля, которые вы запросили, с учётом связей.

---

### 3.7 Итог

Теперь у нас есть:

* GraphQL типы для всех моделей (`Book`, `Author`, `BookDetail`, `Genre`)
* Базовые запросы (`allBooks`, `allAuthors`, `bookById`)
* Связи между моделями (OneToOne, ForeignKey, ManyToMany)

