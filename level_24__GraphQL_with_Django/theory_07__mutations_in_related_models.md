## 5. Мутации в связанных моделях

### 5.1. OneToOne — BookDetail

* У каждой книги есть детализация (`BookDetail`).
* В мутации при создании книги мы можем сразу создавать детализацию:

```python
BookDetail.objects.create(book=book, summary=summary, page_count=page_count)
```

* При обновлении книги:

```python
detail = getattr(book, 'detail', None)
if detail:
    detail.summary = kwargs.get('summary', detail.summary)
    detail.page_count = kwargs.get('page_count', detail.page_count)
    detail.save()
```

* **Идея:** в мутацию передаём поля детали (`summary`, `pageCount`), сервер создаёт или обновляет связанный объект.

---

### 5.2. ManyToMany — Genres

* Книга может принадлежать к **нескольким жанрам**.
* В GraphQL передаём **список id жанров**:

```python
genres_ids = [1, 3, 5]  # например
book.genres.set(genres_ids)  # заменяем жанры книги
```

* Пример мутации для добавления жанров при создании книги:

```python
class CreateBook(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)
        author_id = graphene.Int(required=True)
        genre_ids = graphene.List(graphene.Int)  # список id жанров

    book = graphene.Field(BookType)

    def mutate(root, info, title, author_id, genre_ids=None):
        author = Author.objects.get(pk=author_id)
        book = Book.objects.create(title=title, author=author)
        if genre_ids:
            book.genres.set(genre_ids)  # ManyToMany
        return CreateBook(book=book)
```

* При обновлении можно использовать `.set()` для замены жанров или `.add()` для добавления:

```python
book.genres.set(new_genre_ids)  # заменить все жанры
book.genres.add(genre_id)       # добавить один жанр
book.genres.remove(genre_id)    # удалить один жанр
```

---

### 5.3. Пример запроса GraphQL

#### Создание книги с деталями и жанрами:

```graphql
mutation {
  createBook(
    title: "Новая книга",
    authorId: 1,
    summary: "Описание книги",
    pageCount: 200,
    genreIds: [1,2]
  ) {
    book {
      id
      title
      detail {
        summary
        pageCount
      }
      genres {
        name
      }
    }
  }
}
```

#### Обновление книги (детали + жанры):

```graphql
mutation {
  updateBook(
    id: 1,
    summary: "Обновлённое описание",
    pageCount: 250,
    genreIds: [2,3]
  ) {
    book {
      id
      title
      detail { summary pageCount }
      genres { name }
    }
  }
}
```

---

### 5.4. Итог

* **OneToOne (BookDetail)** — передаём поля детали в мутацию, сервер создаёт/обновляет объект.
* **ManyToMany (genres)** — передаём список id жанров, используем `.set()`, `.add()`, `.remove()`.
* Мутации позволяют работать со связями **в одной операции**, как мы ранее делали с формами и formsets.
