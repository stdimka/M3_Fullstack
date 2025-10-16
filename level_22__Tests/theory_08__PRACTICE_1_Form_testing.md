## Тестирование Форм Часть 1

## План тестирования

| Что тестируем         | Пример проверки                                                    | Цель                                                 |
| --------------------- | ------------------------------------------------------------------ | ---------------------------------------------------- |
| **Корректные данные** | `form = BookForm(data=valid_data)` → `form.is_valid()` → `True`    | Проверить, что форма принимает корректные данные     |
| **Ошибочные данные**  | `form = BookForm(data=invalid_data)` → `form.is_valid()` → `False` | Проверить, что валидация работает                    |
| **Ошибки валидации**  | `form.errors['title']`                                             | Проверить текст ошибки                               |
| **Рендеринг HTML**    | `'class="form-control"' in form.as_p()`                            | Проверить наличие нужных CSS-классов                 |
| **FormSet**           | `BookFormSet(data=formset_data)`                                   | Проверить, что inline-formset корректно валидируется |


## Структура проекта для тестов форм

```
myapp/
├── models.py
├── forms.py
├── tests/
│   ├── __init__.py
│   └── test_forms.py  ← тесты для форм
```

---


## 1, Тестируем обычную форму BookForm

Добавим первый набор тестов в `tests/test_forms.py`

```python
import pytest
from myapp.forms import BookForm
from myapp.models import Author, Book


@pytest.mark.django_db
class TestBookForm:
    def test_valid_data(self):
        """Форма должна быть валидной при корректных данных"""
        author = Author.objects.create(name="Толстой")
        form = BookForm(data={
            'title': 'Война и мир',
            'author': author.id,
            'year_published': 1869,
            'is_deleted': False
        })
        assert form.is_valid(), form.errors

    def test_invalid_data(self):
        """Форма должна быть невалидной при отсутствии обязательных полей"""
        form = BookForm(data={
            'title': '',  # пустое название
            'author': '',  # нет автора
            'year_published': '',
            'is_deleted': False
        })
        assert not form.is_valid()
        assert 'title' in form.errors
        assert 'author' in form.errors

    def test_rendering_contains_classes(self):
        """HTML формы должен содержать ожидаемые CSS-классы"""
        form = BookForm()
        html = form.as_p()
        assert 'class="form-control"' in html
        assert 'class="form-select"' in html or 'class="form-control"' in html
```

---

### Запуск тестов

```bash
# все тесты сразу
pytest -v

# запуск только test_forms.py
pytest -v myapp/tests/test_forms.py

```
---

### Детальный разбор тестов `TestBookForm`

#### 1. `@pytest.mark.django_db` - самая важная честь этого модуля:
  * `pytest` по умолчанию блокирует доступ к БД (чтобы не внести случайных изменений данных)
  * Попытка запуска без декоратора приведёт к ошибке:  
  ```
  RuntimeError: Database access not allowed, use the "django_db" mark, or the "db" or "transactional_db" fixtures to enable it.
  ``` 
  * Поэтому `@pytest.mark.django_db` - один из вариантов доступа. Правда, не к самой БД, а к её копии.
  * Этот декоратор гарантирует, что каждый тест (каждый метод класса `TestBookForm`)
    * будет выполнен на "чистой" (пустой) БД
    * будет выполнен в режиме транзакции, что означает:
    * все изменения БД внутри теста откатятся назад

#### 2. Класс `TestBookForm` - логически объединяет тесты одной формы (`BookForm`)

Когда pytest видит класс вроде этого:

```python
@pytest.mark.django_db
class TestBookForm:
    def test_valid_data(self):
        ...
    def test_invalid_data(self):
        ...
    def test_rendering_contains_classes(self):
        ...
```

он делает следующее:

1. Находит все методы, начинающиеся с `test_`.
2. Для **каждого метода** создаёт **новый экземпляр класса** `TestBookForm`.
3. Выполняет метод **в отдельном контексте**.

То есть при запуске pytest фактически делает нечто вроде:

```python
for test_method in [test_valid_data, test_invalid_data, test_rendering_contains_classes]:
    obj = TestBookForm()  # новый объект каждый раз
    run(obj.test_method)
```

---

В результате:

* Каждый тест **изолирован**:
  если `test_valid_data` упадёт, это **не повлияет** на `test_invalid_data`.

* Pytest **запишет** один провал (failure) для конкретного теста, но **остальные продолжат выполняться**.

* В отчёте появится что-то вроде этого:

  ```
  TestBookForm::test_valid_data FAILED
  TestBookForm::test_invalid_data PASSED
  TestBookForm::test_rendering_contains_classes PASSED
  ```

---

Единственное, что может "завалить весь класс", — это если:

* в **фикстуре класса** (`@pytest.fixture(scope="class")`) или в **методе setup_class** произойдёт ошибка;
* тогда pytest не сможет даже инициализировать тесты внутри этого класса, и все методы будут **пропущены (xfailed)**.

Пример:

```python
@pytest.fixture(scope="class", autouse=True)
def broken_setup():
    raise ValueError("Ошибка при настройке класса")
```

→ в этом случае все тесты внутри `TestBookForm` не запустятся, потому что подготовка "упала" заранее.


| Ситуация                                 | Что происходит                         |
| ---------------------------------------- | -------------------------------------- |
| Один тест упал                           | Остальные тесты продолжают выполняться |
| Ошибка в фикстуре класса / setup_class   | Все тесты в классе не запускаются      |
| Ошибка в одном тесте не влияет на другие | Да, pytest изолирует каждый метод      |


### Рефакторинг `TestBookForm`

#### 1. Добавляем фикстуры

Фикстуры помогают существенно сократить объём кода.  
Создав объект `author` один раз с помощью фикстуры, мы можем во всех методах, где он требуется,  
сразу обращать к объекту `author` без предварительного его создания внутри теста.

Важно:
Если нам важно создавать этот объект в каждом тесте заново,  
мы просто НЕ указываем в декораторе фикстуры область видимости:

```python
@pytest.fixture
def author(db):
    return Author.objects.create(username='Лев Толстой')
```

#### 2. Убираем декоратор в классе `TestBookForm`

Создавая фикстуру `author` мы указываем `db` в качестве параметра, что означает:
"Создай в тестовой базе запись в указанной таблице".

Таким образом, "лёд сломлен", и запрет доступа к БД для выполнения тестов снят.  
Поэтому, если тести принимает объект, созданный фикстурой, в качестве параметра,  
то необходимость в декораторе `@pytest.mark.django_db` автоматически отпадает.

⚠️ Важно!  
Если метод не принимает объект фикстуры в качестве параметра, но всё равно обращается к БД,  
возникнет ошибка:
  ```
  RuntimeError: Database access not allowed, use the "django_db" mark, or the "db" or "transactional_db" fixtures to enable it.
  ``` 
Чтобы её избежать, можно передать в тест в качестве параметра фикстуру `db`.   

```python
def test_rendering_contains_classes(self, db):
    ...
```
(Либо оставить декоратор `@pytest.mark.django_db` для класса.)


#### 3. Тесты после рефакторинга:

```python
import pytest
from myapp.forms import BookForm
from myapp.models import Author, Book

# === ФИКСТУРЫ ================================================================

@pytest.fixture
def author(db):
    """Создаёт тестового автора"""
    return Author.objects.create(name="Пушкин")


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

```

## 2. Тестируем FormSet

Для FormSet важно указать не только значения полей, но и число форм, поступающих на валидацию.

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
        # если formset.is_valid() валидна, то возвращается True
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
```

Особое внимание здесь тесту на НЕ валидность: чтобы форма с незаполненным обязательным полем считалось ошибкой,  
пришлось заполнить одно из необязательных полей (`books-0-year_published`).

В противном случае, форма будет считаться пустой, и успешно пройдёт валидацию.

