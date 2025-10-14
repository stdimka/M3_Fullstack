# Объединение всех приложений в отдельную папку `apps`

Если есть желание объединить все приложения в одну общую папку `apps`,  
то его можно реализовать, как минимум двумя способами.

### Пример изменённой структуры Django-проекта:

```
your_project/
├── manage.py
├── apps/
│   ├── __init__.py         ← важно!!!
│   └── my_app/
│       ├── __init__.py
│       ├── apps.py
│       └── models.py
```

## Способ 1: изменения в списке приложений INSTALLED_APPS в settings.py

То есть перед именем файла ставится имя общей папки:

### `settings.py`

```python
INSTALLED_APPS = [
    'apps.my_app',    
]
```

## Способ 2: добавить новый путь к приложениям в settings.py

### `settings.py`

```python
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / 'apps'))

INSTALLED_APPS = [
    'my_app',         # если apps в sys.path
    # или можно и так:
    'apps.my_app',    # если apps не в sys.path, но это путь из корня проекта
]
```

✅ **Оба варианта работают**, но:

* `'my_app'` короче и используется чаще, если `apps` уже в `sys.path`;
* `'apps.my_app'` — более явно указывает путь, можно использовать без модификации `sys.path`.

---

### Резюме:

| Способ                       | Нужно ли править `sys.path`?              | Вид в `INSTALLED_APPS` |
| ---------------------------- | ----------------------------------------- | ---------------------- |
| `'my_app'`                   | ✅ Да, нужно добавить `apps/` в `sys.path` |                        |
| `'apps.my_app'`              | ❌ Нет, если `apps/` в корне проекта       |                        |
| `'project_name.apps.my_app'` | ❌ Нет, если путь от `BASE_DIR`            |                        |

https://www.youtube.com/watch?v=6uWSmqZCz2o

