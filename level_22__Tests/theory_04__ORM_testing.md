# Тестирование ORM  с помощью pytest

## 1. Как работает база данных в тестах Django

Когда мы запускаем тесты БД через `pytest-django`, происходит следующее:

### 1.1. Автоматически создаётся тестовая база данных

Это — временная копия нашей реальной БД (обычно `test_<имя_бд>`). 

Тестовая база данных создаётся в том же формате, что и основная — используется тот же движок (ENGINE), 
что указан в настройках `settings.py`:

Если необходимо выполнить тесты в БД другого типа, лучше создать отдельный файл `settings_test.py`:
```python
# settings_test.py
from .settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}
```

Который запускается с pytest с параметром `--settings=settings_test`.
     
```bash
pytest --ds=main.settings_test
```

Таким образом, тесты никогда "не трогают" наши реальные данные.

### 1.2. Django применяет миграции к этой тестовой БД.

Это делается для того, чтобы структура тестовой БД ПОЛНОСТЬЮ соответствовала бы моделям.

### 1.3. Тестовая БД автоматически удаляется после прохождения тестов.

Это происходит всегда.  

Однако, если запустить pytest с флагом `pytest --reuse-db`,   
то Django не удаляет тестовую БД после завершения тестов,  
а повторно использует её в следующих запусках, чтобы ускорить прогон.

Это экономит время, т.к. миграции не применяются заново.

---

### 1.4. Каждый тест запускается ИЗОЛИРОВАННО

**Изоляция** — это принцип, согласно которому:

* результат выполнения одного теста **не зависит** от результатов другого;
* тесты не влияют друг на друга через БД, файлы или глобальные переменные.

В pytest-django каждая тестовая функция выполняется в **отдельной транзакции**, 
и после её завершения изменения откатываются — поэтому база каждый раз "чистая" перед каждым новым тестом.

### 1.5. Схема прохождения тестов БД с помощью pytest

```text
pytest запускается
│
├─> создаёт тестовую БД
│
├─> перед каждым тестом: применяются фикстуры
│
├─> выполняется тест (ORM, сигналы, запросы)
│
├─> транзакция откатывается → база чистая
│
└─> после всех тестов тестовая БД удаляется
```

## 2. Фикстуры в pytest

**Фикстура** — это объект или функция, которая создаёт заранее подготовленные данные для теста.
pytest сам вызывает нужные фикстуры **перед запуском каждого теста**, где они указаны как аргументы.

### Пример фикстуры:

```python
@pytest.fixture
def author(db):
    return Author.objects.create(name="Булгаков")

def test_author(author):
    assert author.name == "Булгаков"
```

---

### Виды фикстур (по уровню жизни):

| Уровень                   | Когда выполняется        | Пример использования                 | Декоратор                          |
| ------------------------- | ------------------------ | ------------------------------------ | ---------------------------------- |
| `function` (по умолчанию) | перед **каждым** тестом  | создаёт свежие данные каждый раз     | `@pytest.fixture`                  |
| `module`                  | один раз для файла       | данные общие для всех тестов в файле | `@pytest.fixture(scope="module")`  |
| `session`                 | один раз для всех тестов | редко используется для БД            | `@pytest.fixture(scope="session")` |

Пример фикстуры уровня модуля, которая создаётся один раз для всех тестов в файле:

```python
@pytest.fixture(scope="module")
def sample_author(db):
    return Author.objects.create(name="Толстой")
```

---

### Фикстуры бывают:

* **данными** (модели, тестовые записи, токены и т.п.);
* **состоянием** (мок-объекты, настройки окружения, конфигурация);
* **ресурсами** (файлы, временные директории, соединения и т.д.).

---

## 3. Моккинг (Mocking)

Тестируя ORM и сигналы, крайне нежелательно вызывать побочные эффекты
(например, отправку email, создание файла, запрос к API).

Для этого используется **моккинг** — замена реальных функций или объектов «фиктивными» (mock),
которые **ведут себя как настоящие**, но ничего не делают.

---

###  Пример моккинга через pytest-mock:

```python
@pytest.mark.django_db
def test_signal_triggers(mocker):
    handler = mocker.patch('myapp.signals.send_notification')
    Author.objects.create(name="Достоевский")
    handler.assert_called_once()
```

* `mocker.patch(...)` заменяет реальную функцию фиктивной.
* Мы можете проверить, **была ли она вызвана** и **с какими аргументами**.
* Но не получить результат этого вызова.

Таким образом, этот тест проверяет, что при создании автора (`Author.objects.create(...)`)  
действительно вызывается функция send_notification.

Но замена реальной функции вызова на фиктивную (через `mocker.patch`) проверяет ТОЛЬКО факт вызова —  
без выполнения реального кода уведомления.

---

## 4. Структура тестов ORM

| Что тестировать       | Пример проверки                                |
| --------------------- | ---------------------------------------------- |
| ✅ Сохранение объектов | Проверить, что запись появляется в БД          |
| ✅ Валидация полей     | Проверить `ValidationError` при `full_clean()` |
| ✅ Каскадное удаление  | Проверить удаление связанных объектов          |
| ✅ Сигналы             | Проверить, что сигнал сработал                 |
| ✅ Запросы и фильтры   | Проверить правильность выборки данных          |
| ✅ Методы модели       | Проверить бизнес-логику внутри модели          |

---

## 5. Тестирование сохранения и создания объектов

```python
import pytest
from myapp.models import Author

@pytest.mark.django_db
def test_create_author():
    author = Author.objects.create(name="Булгаков")
    assert Author.objects.count() == 1
    assert author.id is not None
```

Проверка обновления:

```python
@pytest.mark.django_db
def test_update_author():
    author = Author.objects.create(name="Толстой")
    author.name = "Л. Н. Толстой"
    author.save()
    assert Author.objects.get(pk=author.pk).name == "Л. Н. Толстой"
```

---

## 6. Тестирование валидации модели

```python
import pytest
from django.core.exceptions import ValidationError
from myapp.models import Author

@pytest.mark.django_db
def test_validation_error():
    author = Author(name="")
    with pytest.raises(ValidationError):
        author.full_clean()
```

⚠️ `save()` по умолчанию не вызывает валидацию.
Поэтому, 
* либо проверяем валидацию "вручную" (вызовом метода `.full_clean()`)
* либо переопределяем `save()`:
```python
    def save(self, *args, **kwargs):
        self.full_clean()  # теперь проверка всегда выполняется
        super().save(*args, **kwargs)
```
---

## 7. Тестирование каскадного удаления

```python
import pytest
from myapp.models import Author, Book

@pytest.mark.django_db
def test_cascade_delete():
    author = Author.objects.create(name="Толстой")
    Book.objects.create(title="Война и мир", author=author)

    author.delete()

    assert Book.objects.count() == 0  # удалилось каскадно
```

---

## 8. Тестирование сигналов (`post_save`, `pre_delete` и др.)

Используется `mocker` (фикстура pytest) или `django.db.models.signals`.

```python
import pytest
from django.db.models.signals import post_save
from myapp.models import Author
from myapp import signals

@pytest.mark.django_db
def test_post_save_signal_triggered(mocker):
    handler = mocker.patch.object(signals, "create_profile")
    Author.objects.create(name="Гоголь")
    handler.assert_called_once()
```

> ⚠️ Тестируем **факт вызова сигнала**, а не сам сигнал Django.

---

## 9. Тестирование запросов и фильтрации

```python
@pytest.mark.django_db
def test_filter_books():
    author = Author.objects.create(name="Булгаков")
    Book.objects.create(title="Мастер и Маргарита", author=author)
    Book.objects.create(title="Собачье сердце", author=author)

    books = Book.objects.filter(title__icontains="собачье")
    assert books.count() == 1
    assert books.first().title == "Собачье сердце"
```

---

## 10. Тестирование методов модели

Если в модели есть пользовательская логика — тестируйте её напрямую.

```python
class Book(models.Model):
    title = models.CharField(max_length=100)
    def upper_title(self):
        return self.title.upper()

@pytest.mark.django_db
def test_model_method():
    book = Book.objects.create(title="Мастер")
    assert book.upper_title() == "МАСТЕР"
```

---

## 11. Использование фикстур для моделей

Можно создать **фикстуры для часто используемых данных**:

```python
@pytest.fixture
def author(db):
    return Author.objects.create(name="Достоевский")

@pytest.fixture
def book(author):
    return Book.objects.create(title="Преступление и наказание", author=author)

def test_book_has_author(book):
    assert book.author.name == "Достоевский"
```

---

## 12. Проверка каскада и сигналов совместно

```python
@pytest.mark.django_db
def test_delete_signal_triggers(mocker):
    handler = mocker.patch('myapp.signals.handle_book_delete')

    author = Author.objects.create(name="Пушкин")
    book = Book.objects.create(title="Капитанская дочка", author=author)

    book.delete()

    handler.assert_called_once_with(sender=Book, instance=book)
```

---

## 13. Проверка агрегирующих запросов

```python
from django.db.models import Count

@pytest.mark.django_db
def test_annotation_count():
    author = Author.objects.create(name="Булгаков")
    Book.objects.create(title="Мастер", author=author)
    Book.objects.create(title="Собачье сердце", author=author)

    result = Author.objects.annotate(total=Count('book')).get(pk=author.pk)
    assert result.total == 2
```

---

## 14. Итого: Тестирование ORM в pytest

| Что тестируется                     | Как проверить                                           | Пример pytest                                                                                                                                                                                                                                                                                                                     |
| ----------------------------------- | ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Создание объекта**                | Проверить, что запись создаётся и сохраняется           | `python<br>@pytest.mark.django_db<br>def test_create():<br>    obj = Author.objects.create(name="Пушкин")<br>    assert Author.objects.count() == 1`                                                                                                                                                                              |
| **Обновление объекта**              | Изменить поля и проверить, что изменения сохранились    | `python<br>@pytest.mark.django_db<br>def test_update():<br>    a = Author.objects.create(name="Толстой")<br>    a.name = "Л. Н. Толстой"<br>    a.save()<br>    assert Author.objects.get(pk=a.pk).name == "Л. Н. Толстой"`                                                                                                       |
| **Валидация модели**                | Проверить `ValidationError` при некорректных данных     | `python<br>@pytest.mark.django_db<br>def test_validation():<br>    a = Author(name="")<br>    with pytest.raises(ValidationError):<br>        a.full_clean()`                                                                                                                                                                     |
| **Каскадное удаление**              | Убедиться, что связанные объекты удаляются вместе       | `python<br>@pytest.mark.django_db<br>def test_cascade_delete():<br>    a = Author.objects.create(name="Гоголь")<br>    Book.objects.create(title="Мертвые души", author=a)<br>    a.delete()<br>    assert Book.objects.count() == 0`                                                                                             |
| **Сигналы (post_save, pre_delete)** | Использовать `mocker` и проверить вызов обработчика     | `python<br>@pytest.mark.django_db<br>def test_post_save_signal(mocker):<br>    handler = mocker.patch('myapp.signals.create_profile')<br>    Author.objects.create(name="Гончаров")<br>    handler.assert_called_once()`                                                                                                          |
| **Фильтрация и запросы**            | Проверить корректность `filter()` и `exclude()`         | `python<br>@pytest.mark.django_db<br>def test_filter():<br>    Author.objects.create(name="Булгаков")<br>    qs = Author.objects.filter(name__icontains="бул")<br>    assert qs.count() == 1`                                                                                                                                     |
| **Методы модели**                   | Проверить, что метод возвращает ожидаемый результат     | `python<br>@pytest.mark.django_db<br>def test_method():<br>    b = Book.objects.create(title="Мастер")<br>    assert b.upper_title() == "МАСТЕР"`                                                                                                                                                                                 |
| **Агрегации / аннотации**           | Проверить количество связанных записей                  | `python<br>@pytest.mark.django_db<br>def test_count():<br>    a = Author.objects.create(name="Булгаков")<br>    Book.objects.create(title="Мастер", author=a)<br>    Book.objects.create(title="Собачье сердце", author=a)<br>    result = Author.objects.annotate(cnt=Count('book')).get(pk=a.pk)<br>    assert result.cnt == 2` |
| **Фикстуры моделей**                | Использовать `pytest.fixture` для часто нужных объектов | `python<br>@pytest.fixture<br>def author(db):<br>    return Author.objects.create(name="Достоевский")`                                                                                                                                                                                                                            |




## 15. Типичные ошибки при тестировании ORM с pytest

| Ошибка                                                                      | Причина                                                          | Как исправить / рекомендация                                                      |
|-----------------------------------------------------------------------------| ---------------------------------------------------------------- | --------------------------------------------------------------------------------- |
| ❌ `django.db.utils.ProgrammingError: no such table`                         | Тест обращается к БД без подключения тестовой среды              | Добавьте `@pytest.mark.django_db` или фикстуру `db` в тест                        |
| ❌ Тест не сохраняет данные в БД                                             | Создан объект, но не вызван `.save()`                            | После создания объекта вручную вызывайте `obj.save()`                             |
| ❌ Валидация не срабатывает                                                  | Django не вызывает `full_clean()` при `save()`                   | Явно вызывайте `obj.full_clean()` или переопределите `save()`                     |
| ❌ Объекты "утекают" между тестами                                           | Используются общие объекты без фикстур или без очистки           | Используйте фикстуры и не храните состояние между тестами                         |
| ❌ Сигнал не срабатывает                                                     | Обработчик сигнала не импортирован при запуске                   | Убедитесь, что модуль с сигналами импортируется в `apps.py` (`ready()`)           |
| ❌ Ошибка `AssertionError: Expected call not found` при тестировании сигналов | Используется неправильный путь в `mocker.patch()`                | Патчить нужно **путь к месту использования**, а не к объявлению                   |
| ❌ Проверка QuerySet через `==`                                              | QuerySet — это ленивый объект, он не равен списку напрямую       | Сравнивайте `list(qs)` или используйте `.count()`, `.exists()`, `.values_list()`  |
| ❌ Использование `transactional_db` без надобности                           | Медленные тесты, так как транзакции не откатываются быстро       | Используйте `db`, если не тестируете поведение транзакций                         |
| ❌ Проверка значений после `delete()` без обновления объекта                 | Удалённый объект остаётся в памяти                               | После `.delete()` не обращайтесь к объекту, повторно получите данные из БД        |
| ❌ Использование `Model.objects.create()` и `full_clean()` одновременно      | `create()` вызывает `save()` без `full_clean()`                  | Создавайте объект вручную: `obj = Model(...); obj.full_clean(); obj.save()`       |
| ⚠️ Неочевидные результаты `get()`                                           | `get()` выбрасывает `DoesNotExist` или `MultipleObjectsReturned` | Проверяйте данные перед `get()` или используйте `filter().first()`                |
| ⚠️ Неправильное тестирование ManyToMany                                     | Django требует, чтобы объект был сохранён перед `add()`          | Сначала вызовите `obj.save()`, потом `obj.m2m_field.add(item)`                    |
| ⚠️ Тесты ломаются после изменения моделей                                   | Миграции не были применены перед тестом                          | Выполните `pytest --reuse-db --migrations` или удалите старую тестовую БД         |
| ⚠️ Случайные сбои тестов сигналов                                           | Сигналы остаются активны между тестами                           | Используйте `@receiver` только при импорте и не регистрируйте сигналы динамически |

