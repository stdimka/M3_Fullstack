# Тестирование Views и Middleware


## Что проверяем?

* Доступность страниц (`200 OK`) через GET;
* Редиректы после POST (`302 Found`);
* Контекст (например, наличие форм и объектов в шаблоне);
* Middleware (например, LoginRequiredMixin для защищённых view).


## Структура проекта для тестов шаблонов

```
myapp/
├── models.py
├── forms.py
├── tests/
│   ├── __init__.py
│   ├── test_forms.py       ← тесты для форм
│   ├── test_templates.py   ← тесты для шаблонов
│   └── test_views.py       ← тесты для вью
│

```

## `myapp/tests/test_views.py`:

```python
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from myapp.models import Book, BookDetail, Author


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
def auth_client(client, test_user):
    """Авторизует пользователя test_user в тестовом клиенте `client`.
    Возвращает клиент с авторизационной сессией, который можно использовать
    для доступа к защищённым view.
    """
    client.login(username='test_user', password='password')
    return client


# === ТЕСТЫ ===================================================================


class TestBookViews:
    """Тесты для всех Book view: List, Create, Update, Detail, Delete"""

    def test_book_list_view(self, auth_client, books):
        """Проверка списка книг"""
        url = reverse('book_list')
        response = auth_client.get(url)
        assert response.status_code == 200
        print("list(response.context['book_list']", list(response.context['book_list']))
        print("books",  books)
        assert list(response.context['book_list']) == books

    def test_book_create_view_get(self, auth_client):
        """GET-запрос на создание книги возвращает формы и корректный контекст"""
        url = reverse('book_create')
        response = auth_client.get(url)
        assert response.status_code == 200
        assert 'book_form' in response.context
        assert 'detail_form' in response.context
        assert response.context['form_action'] == 'Создать'

    def test_book_create_view_post_valid(self, auth_client, author):
        """POST-запрос с валидными данными создает книгу и детали"""
        url = reverse('book_create')
        data = {
            'title': 'Новая книга',
            'author': author.id,
            'year_published': 2025,
            'summary': 'Описание книги',
            'page_count': 777
        }
        response = auth_client.post(url, data)
        assert response.status_code == 302
        assert response.url == reverse('book_list')
        book = Book.objects.get(title='Новая книга')
        detail = BookDetail.objects.get(book=book)
        assert detail.summary == 'Описание книги'

    def test_book_update_view_get(self, auth_client, books):
        """GET-запрос на обновление книги возвращает формы с текущими данными"""
        book = books[0]
        url = reverse('book_update', args=[book.id])
        response = auth_client.get(url)
        assert response.status_code == 200
        assert response.context['form_action'] == 'Обновить'
        assert response.context['book_form'].instance == book
        if hasattr(book, 'detail'):
            assert response.context['detail_form'].instance == book.detail

    def test_book_update_view_post(self, auth_client, books):
        """POST-запрос обновляет книгу и детали"""
        book = books[0]
        url = reverse('book_update', args=[book.id])
        data = {
            'title': 'Обновлённая книга',
            'author': book.author.id,
            'year_published': 2025,
            'summary': 'Новое описание',
            'page_count': 777
        }
        response = auth_client.post(url, data)
        assert response.status_code == 302
        assert response.url == reverse('book_list')
        book.refresh_from_db()
        assert book.title == 'Обновлённая книга'
        if hasattr(book, 'detail'):
            assert book.detail.summary == 'Новое описание'

    def test_book_detail_view(self, auth_client, books):
        """Проверка detail view книги"""
        book = books[0]
        url = reverse('book_detail', args=[book.id])
        response = auth_client.get(url)
        assert response.status_code == 200
        assert response.context['book'] == book

    def test_book_delete_view(self, auth_client, books):
        """POST-запрос на удаление книги"""
        book = books[0]
        url = reverse('book_delete', args=[book.id])
        response = auth_client.post(url)
        assert response.status_code == 302
        assert response.url == reverse('book_list')
        with pytest.raises(Book.DoesNotExist):
            Book.objects.get(id=book.id)


@pytest.mark.django_db
class TestAuthorViews:
    """Тесты для AuthorListView"""

    def test_author_list_view(self, auth_client, author):
        """Список авторов возвращает корректный контекст"""
        url = reverse('author_list')
        response = auth_client.get(url)
        assert response.status_code == 200
        assert list(response.context['authors']) == [author]


@pytest.mark.django_db
class TestLoginRequired:
    """Проверка middleware LoginRequiredMixin"""

    def test_login_required_redirect(self, client):
        """Неавторизованный пользователь редиректится на /login/"""
        url = reverse('book_list')
        response = client.get(url)
        assert response.status_code == 302
        assert '/login/' in response.url

```

---

## Запуск тестов

```bash
# все тесты сразу
pytest -v

# запуск только test_views.py
pytest -v myapp/tests/test_views.py
```

---


## Что здесь тестируется?

| Раздел / тест                          | Проверка      | Что проверяется / смысл                                                       | Тип теста                        |
| -------------------------------------- | ------------- | ----------------------------------------------------------------------------- | -------------------------------- |
| **`test_book_list_view`**              | статус ответа | GET-запрос на список книг возвращает `200 OK`                                 | **Rendering / HTTP**             |
|                                        | контекст      | `book_list` содержит все книги из фикстуры                                    | **Integration (view + context)** |
|                                        | HTML-контент  | (если проверять шаблон) наличие списка книг                                   | **UI / HTML**                    |
| **`test_book_create_view_get`**        | статус ответа | GET-запрос возвращает `200 OK`                                                | **Rendering / HTTP**             |
|                                        | контекст      | `book_form`, `detail_form` переданы, `form_action='Создать'`                  | **Integration (view + context)** |
|                                        | HTML-контент  | Форма присутствует, кнопка «Создать» есть                                     | **UI / HTML**                    |
| **`test_book_create_view_post_valid`** | редирект      | После успешного POST происходит редирект на список книг (`302`)               | **Behavior / HTTP**              |
|                                        | данные в БД   | Создаются `Book` и `BookDetail` с правильными полями                          | **Integration (view + DB)**      |
| **`test_book_update_view_get`**        | статус ответа | GET-запрос возвращает `200 OK`                                                | **Rendering / HTTP**             |
|                                        | контекст      | `book_form` и `detail_form` содержат текущие данные книги                     | **Integration (view + context)** |
|                                        | HTML-контент  | Кнопка «Обновить» и формы отображаются корректно                              | **UI / HTML**                    |
| **`test_book_update_view_post`**       | редирект      | POST-запрос успешно обновляет книгу и детали, редирект на список книг (`302`) | **Behavior / HTTP**              |
|                                        | данные в БД   | Проверка, что изменения применились к `Book` и `BookDetail`                   | **Integration (view + DB)**      |
| **`test_book_detail_view`**            | статус ответа | GET-запрос возвращает `200 OK`                                                | **Rendering / HTTP**             |
|                                        | контекст      | `book` передан, все данные книги и детали доступны                            | **Integration (view + context)** |
|                                        | HTML-контент  | Название книги, автор, summary, page_count отображаются                       | **UI / HTML**                    |
| **`test_book_delete_view`**            | редирект      | POST-запрос на удаление книги → редирект на список (`302`)                    | **Behavior / HTTP**              |
|                                        | данные в БД   | Проверка, что книга удалена (`Book.DoesNotExist`)                             | **Integration (view + DB)**      |
| **`test_author_list_view`**            | статус ответа | GET-запрос возвращает `200 OK`                                                | **Rendering / HTTP**             |
|                                        | контекст      | `authors` содержит правильный список авторов                                  | **Integration (view + context)** |
|                                        | HTML-контент  | (если проверять шаблон) список авторов в `<ul>` / `<li>`                      | **UI / HTML**                    |
| **`test_login_required_redirect`**     | редирект      | Неавторизованный GET-запрос редиректится на `/login/`                         | **Behavior / Middleware**        |
