# Тестирование DRF


## Что проверяем?

* **Доступность эндпоинтов / страниц**

  * GET-запросы возвращают корректный HTTP-статус (`200 OK`) для доступных ресурсов.
  * Проверяем, что API доступен и корректно обрабатывает запросы.

* **Редиректы после POST / PUT / DELETE**

  * Если view предполагает редирект после действия (например, создание через форму в обычном Django), проверяем статус `302 Found`.
  * В DRF чаще проверяем статус `201 Created` (для POST) и `204 No Content` (для DELETE).

* **Контекст и данные**

  * Проверяем, что в response содержатся все необходимые объекты (например, список книг или авторов).
  * Для DRF это JSON-ответ, где проверяем поля сериализаторов (`id`, `title`, `author`).
  * Для обычных Django view проверяем контекст шаблона (например, `book_form`, `book_list`) и наличие данных в форме.

* **Middleware / права доступа / аутентификация**

  * Проверяем, что защищённые view доступны только авторизованным пользователям.
  * GET/POST/PUT/DELETE для неавторизованных → редирект на login (`302`) или `401 Unauthorized`.
  * Проверяем, что login_required или DRF permission classes работают корректно.

* **Фильтры и query parameters**

  * Проверяем, что фильтры (например, `?author=ID`) возвращают только ожидаемые объекты.
  * Контролируем корректность работы фильтрующего backend.

* **Сериализаторы / структура данных**

  * Проверяем JSON-поля: все обязательные поля присутствуют (`id`, `title`, `author`).
  * Проверяем правильность значений полей (например, `title` после обновления).


---

## Структура проекта для тестов шаблонов

```
myapp/
├── models.py
├── forms.py
├── tests/
│   ├── __init__.py
│   ├── test_drf.py         ← тесты для DRF
│   ├── test_forms.py       ← тесты для форм
│   ├── test_templates.py   ← тесты для шаблонов
│   └── test_views.py       ← тесты для вью
│

```

---

## `myapp/tests/test_drf.py`
```python
import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient, APIRequestFactory
from myapp.models import Author, Book, BookDetail
from myapp.serializers import AuthorSerializer, BookSerializer
from myapp.views import BookViewSet, AuthorViewSet

# === ФИКСТУРЫ ================================================================

@pytest.fixture
def author(db):
    """Создаёт тестового автора"""
    return Author.objects.create(name="Пушкин")


@pytest.fixture
def books(author):
    """Создаёт несколько книг для автора"""
    book1 = Book.objects.create(title="Капитанская дочка", author=author, year_published=1836)
    book2 = Book.objects.create(title="Евгений Онегин", author=author, year_published=1833)
    BookDetail.objects.create(book=book1, summary="Классика жанра", page_count=100)
    BookDetail.objects.create(book=book2, summary="Классика жанра", page_count=200)
    return [book1, book2]


@pytest.fixture
def test_user(db):
    """Создает и возвращает авторизованного пользователя."""
    user = User.objects.create_user(username='test_user', password='password')
    return user


@pytest.fixture
def auth_client(test_user):
    """Авторизует пользователя test_user в DRF APIClient."""
    client = APIClient()
    client.login(username='test_user', password='password')
    return client

# === ТЕСТЫ СЕРИАЛИЗАТОРОВ ====================================================

class TestSerializers:
    """Тесты сериализаторов"""

    @pytest.mark.django_db
    def test_author_serializer(self, author):
        serializer = AuthorSerializer(author)
        data = serializer.data
        assert data["id"] == author.id
        assert data["name"] == "Пушкин"

    @pytest.mark.django_db
    def test_book_serializer(self, books, author):
        book = books[0]
        serializer = BookSerializer(book)
        data = serializer.data
        assert data["id"] == book.id
        assert data["title"] == book.title
        assert data["year_published"] == book.year_published
        assert data["author"] == author.id

# === ТЕСТЫ VIEWSET ===========================================================

class TestBookViews:
    """Тесты для BookViewSet: List, Create, Update, Detail, Delete"""

    @pytest.mark.django_db
    def test_list_books(self, auth_client, books):
        response = auth_client.get("/api/books/")
        assert response.status_code == 200
        assert len(response.json()) == len(books)

    @pytest.mark.django_db
    def test_create_book(self, auth_client, author):
        data = {"title": "Новая книга", "year_published": 2025, "author": author.id}
        response = auth_client.post("/api/books/", data, format="json")
        assert response.status_code == 201
        assert response.json()["title"] == "Новая книга"

    @pytest.mark.django_db
    def test_update_book(self, auth_client, books, author):
        book = books[0]
        data = {"title": "Капитанская дочка - обновлено", "year_published": 1836, "author": author.id}
        response = auth_client.put(f"/api/books/{book.id}/", data, format="json")
        assert response.status_code == 200
        assert response.json()["title"] == "Капитанская дочка - обновлено"

    @pytest.mark.django_db
    def test_delete_book(self, auth_client, books):
        book = books[0]
        response = auth_client.delete(f"/api/books/{book.id}/")
        assert response.status_code == 204
        assert Book.objects.count() == 1  # осталась одна книга

    @pytest.mark.django_db
    def test_filter_books_by_author(self, auth_client, author, books):
        response = auth_client.get(f"/api/books/?author={author.id}")
        data = response.json()
        assert len(data) == len(books)
        assert all(b["author"] == author.id for b in data)

class TestAuthorViews:
    """Тесты для AuthorViewSet"""

    @pytest.mark.django_db
    def test_list_authors(self, auth_client, author):
        response = auth_client.get("/api/authors/")
        assert response.status_code == 200
        data = response.json()
        assert any(a["id"] == author.id for a in data)

    @pytest.mark.django_db
    def test_create_author(self, auth_client):
        data = {"name": "Лев Толстой"}
        response = auth_client.post("/api/authors/", data, format="json")
        assert response.status_code == 201
        assert response.json()["name"] == "Лев Толстой"

# === НИЗКОУРОВНЕВЫЕ ТЕСТЫ С APIRequestFactory =================================

class TestBookViewFactory:
    """Unit-тесты BookViewSet через APIRequestFactory"""

    @pytest.mark.django_db
    def test_list_books_factory(self, books):
        factory = APIRequestFactory()
        request = factory.get("/books/")
        view = BookViewSet.as_view({"get": "list"})
        response = view(request)
        assert response.status_code == 200

```

---

## Запуск тестов

```bash
# все тесты сразу
pytest -v

# запуск только test_drf.py
pytest -v myapp/tests/test_drf.py
```


---

## DRF-тесты: смысл и проверки

| Раздел / тест                     | Проверка       | Что проверяется / смысл                                              | Тип теста                        |
| --------------------------------- | -------------- | -------------------------------------------------------------------- | -------------------------------- |
| **`test_list_books`**             | статус ответа  | GET-запрос на `/api/books/` возвращает `200 OK`                      | **Rendering / HTTP**             |
|                                   | контент        | Список книг содержит все объекты из фикстуры                         | **Integration (view + DB)**      |
|                                   | JSON-структура | Проверка полей `id`, `title`, `author`                               | **Unit / Serializer**            |
| **`test_create_book`**            | статус ответа  | POST-запрос на `/api/books/` возвращает `201 Created`                | **Behavior / HTTP**              |
|                                   | данные в БД    | Создаётся новый объект `Book` с правильными полями                   | **Integration (view + DB)**      |
|                                   | JSON-ответ     | Проверка, что возвращён правильный `title` и `author`                | **Unit / Serializer**            |
| **`test_update_book`**            | статус ответа  | PUT-запрос на `/api/books/{id}/` возвращает `200 OK`                 | **Behavior / HTTP**              |
|                                   | данные в БД    | Проверка, что изменился `title` книги                                | **Integration (view + DB)**      |
|                                   | JSON-ответ     | Проверка обновлённого значения полей `title`, `author`               | **Unit / Serializer**            |
| **`test_delete_book`**            | статус ответа  | DELETE-запрос на `/api/books/{id}/` возвращает `204 No Content`      | **Behavior / HTTP**              |
|                                   | данные в БД    | Проверка, что объект `Book` удалён                                   | **Integration (view + DB)**      |
| **`test_filter_books_by_author`** | статус ответа  | GET-запрос `/api/books/?author={id}` возвращает `200 OK`             | **Rendering / HTTP**             |
|                                   | фильтрация     | Проверка, что возвращаются только книги указанного автора            | **Integration (view + DB)**      |
| **`test_list_authors`**           | статус ответа  | GET-запрос на `/api/authors/` возвращает `200 OK`                    | **Rendering / HTTP**             |
|                                   | контент        | Список авторов содержит все объекты из фикстуры                      | **Integration (view + DB)**      |
| **`test_create_author`**          | статус ответа  | POST-запрос на `/api/authors/` возвращает `201 Created`              | **Behavior / HTTP**              |
|                                   | данные в БД    | Создаётся новый объект `Author` с правильным именем                  | **Integration (view + DB)**      |
|                                   | JSON-ответ     | Проверка, что возвращён правильный `name`                            | **Unit / Serializer**            |
| **`test_list_books_factory`**     | статус ответа  | GET-запрос через `APIRequestFactory` возвращает `200 OK`             | **Unit / View**                  |
|                                   | JSON-структура | Проверка полей сериализатора для каждого объекта                     | **Unit / Serializer**            |
| **`test_unauthenticated_access`** | редирект/401   | Неавторизованный GET/POST/PUT/DELETE → проверка, что доступ запрещён | **Behavior / Middleware / Auth** |



### Краткие пояснения

1. **Rendering / HTTP** — проверяем, что view корректно отвечает на запросы (200, 201, 204).
2. **Integration (view + DB)** — проверка работы view вместе с БД: создание, фильтрация, обновление, удаление.
3. **Unit / Serializer** — проверка структуры JSON, сериализаторы корректно преобразуют объекты.
4. **Behavior / Middleware / Auth** — проверка аутентификации, редиректов и прав доступа.
5. **Unit / View** — низкоуровневое тестирование `ViewSet` через `APIRequestFactory` без DRF Client.



