## Что именно тестируется в Django-формах?

Тесты форм не проверяют “как форма выглядит”, а проверяют **её поведение и логику**.  
Форма — это слой валидации и подготовки данных перед записью в БД, поэтому основное внимание уделяется:

| Что проверяем                                     | Пример                                                            |
|---------------------------------------------------| ----------------------------------------------------------------- |
| Валидация корректных данных                       | форма должна быть `is_valid()`                                    |
| Ошибки при неверных данных                        | ожидаем конкретные сообщения                                      |
| Значения полей (cleaned_data)                     | поля должны очищаться правильно                                   |
| Поведение кастомных методов (`clean()`, `save()`) | правильно ли сохраняется                                          |
| Поведение связанных форм (FormSet, InlineFormSet) | формы внутри группы должны синхронно валидироваться и сохраняться |

---

## 1. Тестирование обычных форм `ModelForm`

Пример: `BookForm`.

```python
from myapp.forms import BookForm
from myapp.models import Author

def test_book_form_valid(db):
    author = Author.objects.create(name="Толстой")
    form = BookForm(data={
        'title': 'Война и мир',
        'author': author.id,
        'year_published': 1869,
        'is_deleted': False
    })
    assert form.is_valid()
    book = form.save()
    assert book.title == 'Война и мир'
```

Здесь тестируется, что:

* все обязательные поля присутствуют; 
* типы данных корректны;
* все валидаторы успешно прошли и не выявили никаких ошибок;
* `save()` создаёт правильный объект.

В случае валидации обычной формы достаточно нарушить одно из условий,  
и метод `form.is_valid()` обязательно вернёт `False`.  

Что легко можно проверить при тестировании.

---

## 2. Тестирование FormSet (несколько форм одного типа)

FormSet — это **группа одинаковых форм** (например, для массового редактирования нескольких `Book`).

```python
from myapp.forms import BookModelFormSet
from myapp.models import Author, Book

def test_book_formset_valid(db):
    author = Author.objects.create(name="Булгаков")
    book1 = Book.objects.create(author=author, title="Мастер", year_published=1928)
    book2 = Book.objects.create(author=author, title="Маргарита", year_published=1930)

    formset_data = {
        'form-TOTAL_FORMS': '2',
        'form-INITIAL_FORMS': '2',
        'form-0-id': str(book1.id),
        'form-0-title': 'Мастер и Маргарита',
        'form-0-author': author.id,
        'form-0-year_published': '1930',
        'form-0-is_deleted': '',
        'form-1-id': str(book2.id),
        'form-1-title': 'Белая гвардия',
        'form-1-author': author.id,
        'form-1-year_published': '1925',
        'form-1-is_deleted': '',
    }

    formset = BookModelFormSet(data=formset_data)
    assert formset.is_valid()
    instances = formset.save()
    assert len(instances) == 2
```

### Что важно знать:

* Django ожидает “служебные” поля:
  `TOTAL_FORMS`, `INITIAL_FORMS`, `MIN_NUM_FORMS`, `MAX_NUM_FORMS`.
* Далее идёт наборы форм. Каждый набор содержит свою группу значений полей формы:
  ```python
        'form-0-id': str(book1.id),
        'form-0-title': 'Мастер и Маргарита',
        'form-0-author': author.id,
        'form-0-year_published': '1930',
        'form-0-is_deleted': '',
  ```
* FormSet не валидируется, если ХОТЯ БЫ ОДНА из вложенных форм некорректна.
* Проверка заполнения обязательных полей здесь тоже необычна:
  * Если число форм `form-TOTAL_FORMS` > 1, то форма со всеми пустыми полями считается валидной
  * ВЫХОД: заполнять ХОТЯ БЫ одно поле (можно даже необязательное), чтобы сделать всю форму не похожей на пустую.
* После `save()` возвращается список сохранённых объектов.

---

## 3. Тестирование InlineFormSet (связанные формы через ForeignKey)

Это набор форм для зависимой модели (например, все `Book` для конкретного `Author`).

```python
from myapp.forms import BookFormSet
from myapp.models import Author

def test_inline_formset_valid(db):
    author = Author.objects.create(name="Пушкин")
    form_data = {
        'books-TOTAL_FORMS': '2',
        'books-INITIAL_FORMS': '0',
        'books-MIN_NUM_FORMS': '0',
        'books-MAX_NUM_FORMS': '1000',
        'books-0-title': 'Руслан и Людмила',
        'books-0-year_published': '1820',
        'books-0-is_deleted': '',
        'books-1-title': 'Евгений Онегин',
        'books-1-year_published': '1833',
        'books-1-is_deleted': '',
    }

    formset = BookFormSet(data=form_data, instance=author)
    assert formset.is_valid()
    formset.save()
    assert author.books.count() == 2
```

### Особенности:

* InlineFormSet требует `instance` родителя (в нашем случае `Author`).
* Данные полей форм начинаются с префикса `books-`.
* Поля `TOTAL_FORMS` и `INITIAL_FORMS` обязательны, иначе форма всегда невалидна.
* `formset.save()` автоматически связывает книги с автором.

---

## 4 Отличия между Form, FormSet и InlineFormSet

| Характеристика           | `Form`                 | `FormSet`                 | `InlineFormSet`                          |
| ------------------------ | ---------------------- | ------------------------- | ---------------------------------------- |
| Назначение               | Одна форма             | Несколько одинаковых форм | Формы, связанные с конкретным объектом   |
| Префикс данных           | Нет                    | `form-0-`, `form-1-`      | `<related_name>-0-`, `<related_name>-1-` |
| Нужно указывать instance | Иногда                 | Иногда                    | ✅ обязательно                            |
| Метод `save()`           | Возвращает один объект | Возвращает список         | Возвращает список связанных объектов     |
| Тип теста                | юнит                   | интеграционный            | интеграционный (родитель+дочерние)       |

---

## 5. Советы при написании тестов форм

| Рекомендация                                                    | Почему                                           |
| --------------------------------------------------------------- | ------------------------------------------------ |
| Используйте `assert form.is_valid()` — а не `form.errors == {}` | ошибки могут быть скрыты в `.non_field_errors()` |
| Проверяйте `.cleaned_data` и `.errors` явно                     | это основа бизнес-логики формы                   |
| Для FormSet всегда передавайте `TOTAL_FORMS` и `INITIAL_FORMS`  | иначе Django не поймёт, сколько форм в наборе    |
| Проверяйте `save(commit=False)` если логика изменена            | особенно при переопределённом `save()`           |
| Для InlineFormSet — не забывайте `instance=...`                 | иначе не создастся связь `ForeignKey`            |


