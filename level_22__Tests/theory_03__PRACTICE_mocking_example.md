Идея: при тестировании скрипта, который читает параметры из командной строки через `sys.argv`,  
мы можем **заменить содержимое `sys.argv` на нужное тестовое значение**, чтобы проверить поведение функции.

---

## Пример скрипта

Допустим, есть скрипт `my_script.py`:

```python
import sys

def main():
    # Например, ожидаем: python my_script.py input.txt output.txt
    if len(sys.argv) != 3:
        return "Error: expected 2 arguments"
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    return f"Processing {input_file} -> {output_file}"
```

Мы хотим протестировать `main()` с разными аргументами.

---

## Тест с мокингом `sys.argv`

```python
# test_my_script.py
import sys
from my_script import main
import pytest

def test_main_with_args(monkeypatch):
    # Задаём sys.argv для теста
    test_args = ["my_script.py", "input.txt", "output.txt"]
    monkeypatch.setattr(sys, "argv", test_args)

    result = main()
    assert result == "Processing input.txt -> output.txt"

def test_main_wrong_args(monkeypatch):
    # Недостаточно аргументов
    test_args = ["my_script.py", "input.txt"]
    monkeypatch.setattr(sys, "argv", test_args)

    result = main()
    assert result == "Error: expected 2 arguments"
```

---

## Ключевые моменты

1. **`monkeypatch.setattr(sys, "argv", test_args)`**

   * Временно заменяет атрибут `argv` в модуле `sys` на объект `test_args`.
   * Следовательно, внутри теста любые обращения к `sys.argv` будут возвращать `test_args`,    
      а не реальные аргументы командной строки.
   * После завершения теста pytest автоматически восстанавливает исходное значение `sys.argv`,     
      чтобы изменения не влияли на другие тесты.

2. Тестируем **разные сценарии**:

   * Правильные аргументы.
   * Недостаточно аргументов.
   * Можно добавить лишние аргументы.

3. Используем `pytest`, без запуска из командной строки, что делает тест изолированным.

Запуск теста в `pytest` пошагово:

---

### 1. Структура файлов

Размещаем файл и его тест в папку `my_project`:

```
my_project/
│
├─ my_script.py
└─ test_my_script.py
```

* `my_script.py` — скрипт с функцией `main()`.
* `test_my_script.py` — тесты с `pytest`.

---

### 2. Установка pytest (если ещё не установлен)

```bash
pip install pytest
```

---

### 3. Запуск всех тестов в проекте

Находясь в папке `my_project/`:

```bash
pytest
```

* `pytest` автоматически найдёт файлы, начинающиеся с `test_` или заканчивающиеся на `_test.py`.
* Автоматически выполнит все функции, начинающиеся с `test_`.

---

### 4. Запуск конкретного файла теста

```bash
pytest test_my_script.py
```

---

### 5. Более подробный вывод

Если хотите видеть, какие тесты проходят/падают и сообщения `assert`:

```bash
pytest -v
```

---

### 6. Проверка конкретного теста внутри файла

```bash
pytest -k test_main_with_args -v
```

* `-k` ищет тест по имени функции.

---

После запуска мы увидим что-то вроде:

```
test_my_script.py::test_main_with_args PASSED                              [ 50%]
test_my_script.py::test_main_wrong_args PASSED                             [100%]
```
