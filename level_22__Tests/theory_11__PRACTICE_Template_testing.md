# Тестируем шаблоны


## Что и как будет тестировать?

Мы проверяем **шаблоны целиком**, включая:

1. **HTTP-ответ и статус** (`200 OK`)
2. **Используемый шаблон** (`template_name`)
3. **Переданный контекст** (`response.context`)
4. **HTML-контент** (наличие форм, таблиц, кнопок, текста)

Все тесты используют **`client`** — объект, который 
* имитирует поведение браузера  
* и позволяет безопасно тестировать рендеринг страниц и работу view без реального запуска сервера.


## Устанавливаем `beautifulsoup4`

Для проверки элементов HTML нам потребуется установить этот пакет:

```bash
pip install beautifulsoup4
```

## Структура проекта для тестов шаблонов

```
myapp/
├── models.py
├── forms.py
├── tests/
│   ├── __init__.py
│   ├── test_forms.py       ← тесты для форм
│   └── test_templates.py   ← тесты для шаблонов
│
templates/
│   ├── book_list.html
│   ...
```

## Заполним новый файл `tests/test_templates.py`:

```python
import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from bs4 import BeautifulSoup

# === ФИКСТУРЫ ================================================================

@pytest.fixture
def authors(db):
    """ Создает двух авторов для теста.
    Импорт моделей делаем внутри фикстуры, чтобы избежать циклического импорта.
    """
    from myapp.models import Author

    author1 = Author.objects.create(name="Author 1")
    author2 = Author.objects.create(name="Author 2")
    return [author1, author2]


@pytest.fixture
def books(db, authors):
    """ Создает двух авторов для теста.
    Импорт моделей делаем внутри фикстуры, чтобы избежать циклического импорта.
    """
    from myapp.models import Book, BookDetail

    book1 = Book.objects.create(title="Book 1", year_published="2000", author=authors[0])
    book2 = Book.objects.create(title="Book 2", year_published="2001", author=authors[0])
    BookDetail.objects.create(book=book1, summary="Summary text", page_count=100)
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

class TestAuthors:
    def test_author_list_template(self, auth_client, authors):
        """Тестируем шаблон author_list.html"""
        url = reverse('author_list')
        response = auth_client.get(url)

        assert response.status_code == 200  # Проверяем статус

        # Проверяем есть ли наш шаблон в списке всех отредоренных шаблонов
        templates = [t.name for t in response.templates]
        assert 'myapp/author_list.html' in templates

        # context — это словарь, который view передаёт в шаблон. Мы проверяем:
        # - Есть ли там ключ 'authors'
        # - Содержит ли он ровно 2 объекта, которые мы создали в тесте.
        assert 'authors' in response.context
        assert len(response.context['authors']) == 2

        # Получаем авторов по тегам списков авторов
        # И убеждаемся, что авторов точно 2
        soup = BeautifulSoup(response.content, 'html.parser')
        author_items = soup.select('ul.list-group li.list-group-item')
        assert len(author_items) == 2
        assert "Author 1" in author_items[0].text
        assert "Author 2" in author_items[1].text



class TestBooks:
    def test_book_list_template(self, auth_client, books):
        """Тестируем шаблон book_list.html"""
        url = reverse('book_list')  # предполагаемое имя URL для ListView книг
        response = auth_client.get(url)

        assert response.status_code == 200
        templates = [t.name for t in response.templates]
        assert 'myapp/book_list.html' in templates

        assert 'object_list' in response.context
        assert len(response.context['object_list']) == 2

        soup = BeautifulSoup(response.content, 'html.parser')
        table_rows = soup.select('table tbody tr')
        assert len(table_rows) == 2
        assert "Book 1" in table_rows[0].text
        assert "Book 2" in table_rows[1].text

    def test_book_create_template(self, auth_client):
        """Тестируем шаблон book_create.html"""
        url = reverse('book_create')
        response = auth_client.get(url)

        assert response.status_code == 200
        templates = [t.name for t in response.templates]
        assert 'myapp/book_form.html' in templates

        # Проверяем контекст
        assert 'book_form' in response.context
        assert 'detail_form' in response.context
        assert response.context['form_action'] == 'Создать'

        # Проверяем наличие форм в HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        assert soup.find('form') is not None
        assert soup.find('button', string='Создать') is not None


    def test_book_detail_template(self, auth_client, authors, books):
        """Тестируем шаблон book_detail.html"""
        url = reverse('book_detail', args=[books[0].pk])
        response = auth_client.get(url)

        assert response.status_code == 200
        templates = [t.name for t in response.templates]
        assert 'myapp/book_detail.html' in templates

        assert 'book' in response.context
        soup = BeautifulSoup(response.content, 'html.parser')
        assert "Book 1" in soup.text
        assert "Author 1" in soup.text
        assert "Summary text" in soup.text
        assert "100" in soup.text
```

---

## Запуск тестов

```bash
# все тесты сразу
pytest -v

# запуск только test_templates.py
pytest -v myapp/tests/test_templates.py
```

---

## Что здесь тестируется

| Раздел / тест                   | Проверка      | Что проверяется / смысл                                                       | Тип теста                        |
| ------------------------------- | ------------- | ----------------------------------------------------------------------------- | -------------------------------- |
| **`test_author_list_template`** | статус ответа | проверяем, что GET-запрос возвращает `200 OK`                                 | **Rendering / HTTP**             |
|                                 | шаблон        | проверяем, что используется `author_list.html`                                | **Rendering / UI**               |
|                                 | контекст      | `authors` передан в шаблон, содержит правильное количество объектов           | **Integration (view + context)** |
|                                 | HTML-контент  | проверяем наличие `<ul>` и `<li>` с именами авторов                           | **UI / HTML**                    |
| **`test_book_list_template`**   | статус ответа | GET-запрос возвращает `200 OK`                                                | **Rendering / HTTP**             |
|                                 | шаблон        | используется `book_list.html`                                                 | **Rendering / UI**               |
|                                 | контекст      | `object_list` содержит все книги                                              | **Integration (view + context)** |
|                                 | HTML-контент  | проверяем таблицу с книгами, наличие кнопок View/Edit/Delete                  | **UI / HTML**                    |
| **`test_book_create_template`** | статус ответа | GET-запрос возвращает `200 OK`                                                | **Rendering / HTTP**             |
|                                 | шаблон        | используется `book_form.html`                                                 | **Rendering / UI**               |
|                                 | контекст      | `book_form`, `detail_form` переданы, `form_action='Создать'`                  | **Integration (view + context)** |
|                                 | HTML-контент  | форма присутствует, кнопка «Создать» есть                                     | **UI / HTML**                    |
| **`test_book_detail_template`** | статус ответа | GET-запрос возвращает `200 OK`                                                | **Rendering / HTTP**             |
|                                 | шаблон        | используется `book_detail.html`                                               | **Rendering / UI**               |
|                                 | контекст      | `book` передан, отображаются все данные книги и детали                        | **Integration (view + context)** |
|                                 | HTML-контент  | проверяем, что в HTML есть название книги, автор, summary, количество страниц | **UI / HTML**                    |



## ⚠️ Авторизация пользователя

Важное отличие от предыдущего примера:

* Создание и авторизация пользователя `test_user`.
* Для этого создана специальная фикстура `auth_client`, которая заменяет обычного клиента на авторизированного.

Иными словами: теперь мы использует виртуальные браузер, в котором все запросы делаются авторизованным пользователем.

```python
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
```

⚠️  Если смысл зайти обычным клиентом (`client` вместо `auth_client`)  
и увидеть ответ 302 вместо ответа 200 (редирект на страницу `login.html`).
