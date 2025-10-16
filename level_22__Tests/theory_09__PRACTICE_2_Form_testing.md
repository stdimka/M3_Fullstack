## Тестирование Форм Часть 2

## Итоговый файл тестов форм

```python
import pytest
from myapp.forms import (
    BookForm,
    AuthorForm,
    BookDetailForm,
    BookFormSet,
    BookModelFormSet
)
from myapp.models import Author, Book

# === ФИКСТУРЫ ================================================================

@pytest.fixture
def author(db):
    """Создаёт тестового автора"""
    return Author.objects.create(name="Пушкин")


@pytest.fixture
def books(author):
    """Создаёт несколько книг для автора"""
    return [
        Book.objects.create(title="Капитанская дочка", author=author, year_published=1836),
        Book.objects.create(title="Евгений Онегин", author=author, year_published=1833),
    ]


# === ТЕСТЫ ===================================================================

class TestBookForm:
    def test_valid_data(self, author):
        """Форма должна быть валидной при корректных данных"""
        form = BookForm(data={
            'title': 'Руслан и Людмила',
            'author': author,
            'year_published': 1820,
            'is_deleted': False
        })
        assert form.is_valid(), form.errors

    def test_invalid_data(self):
        """Форма должна быть невалидной при отсутствии обязательных полей"""
        form = BookForm(data={
            'title': '',
            'author': '',
            'year_published': '',
            'is_deleted': False
        })
        assert not form.is_valid()
        assert 'title' in form.errors
        assert 'author' in form.errors

    def test_rendering_contains_classes(self, db):
        """HTML формы должен содержать ожидаемые CSS-классы"""
        form = BookForm()
        html = form.as_p()
        assert 'class="form-control"' in html
        assert 'class="form-select"' in html or 'class="form-control"' in html


# =========================================================

@pytest.mark.django_db
class TestAuthorForm:
    def test_valid_author_form(self):
        form = AuthorForm(data={'name': 'Достоевский'})
        assert form.is_valid()

    def test_placeholder_present_in_html(self):
        """Проверяем, что placeholder присутствует"""
        form = AuthorForm()
        html = form.as_p()
        assert 'placeholder="Введите имя автора"' in html


@pytest.mark.django_db
class TestBookDetailForm:
    def test_page_count_must_be_integer(self):
        """Некорректное значение для page_count делает форму невалидной"""
        form = BookDetailForm(data={'summary': 'Описание', 'page_count': 'abc'})
        assert not form.is_valid()
        assert 'page_count' in form.errors

    def test_valid_data(self):
        form = BookDetailForm(data={'summary': 'Описание', 'page_count': 200})
        assert form.is_valid()


# ======================  TestBookInlineFormset =================================


class TestBookInlineFormset:
    def test_valid_formset(self, author, books):
        """InlineFormset должен быть валиден при корректных данных"""

        data = {
            'books-TOTAL_FORMS': '1',
            'books-INITIAL_FORMS': '0',
            'books-MIN_NUM_FORMS': '0',
            'books-MAX_NUM_FORMS': '1000',

            'books-0-title': books[0].title,
            'books-0-year_published': f'{books[0].year_published}',
            'books-0-is_deleted': '',

            'books-1-title': books[1].title,
            'books-1-year_published': f'{books[1].year_published}',
            'books-1-is_deleted': '',
        }

        formset = BookFormSet(data, instance=author)
        assert formset.is_valid(), formset.errors
        # если formset.is_valid() валидно, то возвращается True
        # если - нет, возвращается список ошибок formset.errors

    def test_invalid_formset_missing_field(self, author, books):
        """InlineFormset должен быть невалиден, если пропущено обязательное поле"""

        data = {
            'books-TOTAL_FORMS': '1',
            'books-INITIAL_FORMS': '0',
            'books-MIN_NUM_FORMS': '0',
            'books-MAX_NUM_FORMS': '1000',

            'books-0-title': '',  # ошибка
            'books-0-year_published': f'{books[0].year_published}',
            'books-0-is_deleted': '',
        }

        formset = BookFormSet(data, instance=author)
        assert not formset.is_valid()


# ======================  BookModelFormSet =================================


class TestBookModelFormSet:
    def test_valid_formset_with_existing_books(self, books, author):
        """BookModelFormSet должен обновлять существующие книги при корректных данных
           (чтобы форма сохранила обновлённые данные, надо изменить хотя бы одно поле:
           для этого мы добавляем текс < (ред.)> к каждому названию книги)
        """
        data = {
            'form-TOTAL_FORMS': '2',
            'form-INITIAL_FORMS': '2',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',

            'form-0-id': str(books[0].id),
            'form-0-title': books[0].title + ' (ред.)',
            'form-0-author': str(author.id),
            'form-0-year_published': f'{books[0].year_published}',
            'form-0-is_deleted': '',

            'form-1-id': str(books[1].id),
            'form-1-title': books[1].title + ' (ред.)',
            'form-1-author': str(author.id),
            'form-1-year_published': f'{books[1].year_published}',
            'form-1-is_deleted': '',
        }

        formset = BookModelFormSet(data, queryset=Book.objects.all())
        assert formset.is_valid(), formset.errors  # True, иначе - список ошибок formset.errors

        instances = formset.save()
        assert len(instances) == 2

    def test_invalid_formset_missing_field(self, books, author):
        """BookModelFormSet должен быть валиден при корректных данных существующих книг"""
        data = {
            'form-TOTAL_FORMS': '1',
            'form-INITIAL_FORMS': '1',
            'form-MIN_NUM_FORMS': '0',
            'form-MAX_NUM_FORMS': '1000',

            'form-0-id': str(books[0].id),
            'form-0-title': '',  # ошибка
            'form-0-author': str(author.id),
            'form-0-year_published': '1836',
            'form-0-is_deleted': '',
        }

        formset = BookModelFormSet(data)
        assert not formset.is_valid()
        assert 'title' in formset.forms[0].errors

```

---

## Что здесь тестируется

| Раздел                 | Проверка                        | Что проверяется / смысл                                                              | Тип теста                          |
| ---------------------- | ------------------------------- | ------------------------------------------------------------------------------------ | ---------------------------------- |
| **`BookForm`**         | корректные данные               | форма валидна при нормальном вводе                                                   | **Unit (валидация)**               |
|                        | отсутствующие обязательные поля | форма невалидна, проверяется наличие ошибок по `title` и `author`                    | **Unit (валидация)**               |
|                        | HTML-классы                     | проверяется, что поля формы рендерятся с CSS-классами `form-control` / `form-select` | **Rendering / UI**                 |
| **`AuthorForm`**       | корректные данные               | форма валидна при корректном имени автора                                            | **Unit (валидация)**               |
|                        | placeholder в HTML              | у поля `name` присутствует `placeholder="Введите имя автора"`                        | **Rendering / UI**                 |
| **`BookDetailForm`**   | неверный тип данных             | `page_count` должен быть числом, иначе форма невалидна                               | **Unit (валидация)**               |
|                        | корректные данные               | форма проходит валидацию при правильных типах данных                                 | **Unit (валидация)**               |
| **`BookFormSet`**      | валидный inline formset         | formset для книг автора (`Author → Books`) валиден при корректных данных             | **Integration (formset)**          |
|                        | пропущено обязательное поле     | formset невалиден, если отсутствует обязательное поле (`title`)                      | **Integration (formset)**          |
| **`BookModelFormSet`** | валидные данные                 | корректно редактируются существующие книги, данные сохраняются                       | **Integration (модель + formset)** |
|                        | пропущено обязательное поле     | formset невалиден, если отсутствует `title`, проверяется наличие ошибки в форме      | **Integration (валидация)**        |
