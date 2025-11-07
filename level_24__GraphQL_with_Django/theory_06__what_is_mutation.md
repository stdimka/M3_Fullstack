## 4. Мутации

### 4.1 Что такое мутация?

* Мутация — это **операция для изменения данных** на сервере: 
  * создание, 
  * обновление 
  * или удаление объектов.
* В отличие от `Query`, которая только **читает данные**, мутация **вносит изменения**.


```python
class CreateBook(graphene.Mutation):
    class Arguments:
        title = graphene.String(required=True)      # обязательный аргумент
        author_id = graphene.Int(required=True)     # обязательный аргумент
        year_published = graphene.Int(required=False)  # необязательный
        summary = graphene.String()
        page_count = graphene.Int()

    book = graphene.Field(BookType)

    def mutate(root, info, title, author_id, year_published=None, summary=None, page_count=None):
        author = Author.objects.get(id=author_id)
        book = Book.objects.create(
            title=title,
            author=author,
            year_published=year_published,
            summary=summary,
            page_count=page_count
        )
        return CreateBook(book=book)
```

**Таким образом:**

* **Класс `CreateBook`** описывает структуру самой мутации: 
  * (какие аргументы она принимает и что возвращает).
* **Метод `mutate`** содержит реализацию логики мутации:
  * (что именно произойдёт с переданными данными во время мутации).
  
---

### 4.2. Что передаём в мутацию?

* **Arguments (аргументы)** — это данные, которые серверу нужны для изменения объекта.
* Пример для создания книги:

```graphql
mutation {
  createBook(
    title: "Новая книга",
    authorId: 1,
    yearPublished: 2025,
    summary: "Описание",
    pageCount: 120
  ) {
    book { id title }  # что хотим получить обратно
  }
}
```

* Аргументы могут быть обязательными (`required=True`) или необязательными.
* Можно передавать любые поля модели или данные для связанных объектов (`ForeignKey`, `OneToOne`, `ManyToMany`).

---

### 4.3 Что получаем из мутации?

* Любые **поля объектов**, которые вернём в блоке ответа.
* Пример выше вернёт `id` и `title` созданной книги.
* Можно вернуть также связанные объекты:

```graphql
book {
  id
  title
  author { name }
  detail { summary pageCount }
}
```

* Это похоже на `return` из функции: клиент получает актуальные данные сразу после изменения.

---

**Итог:**

* **Мутация** = операция изменения данных
* **Вход** = аргументы (`Arguments`) → управляют, что изменяем
* **Выход** = любые поля (`book { ... }`) → клиент получает результат
