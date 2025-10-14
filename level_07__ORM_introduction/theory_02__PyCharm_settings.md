Есть много способов получить доступ к Django БД.

Один из них - через `Django shell`: 
```bash
./manage.py shell
```

Эта команда, выполненная в виртуальном окружении проекта,  
автоматически загрузить все переменные окружения.

Если вы используете PyCharm (в том числе Community), то гораздо удобнее  
будет работать через Python-консоль:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()
```

В этом случае вы получаете доступ к интерактивным подсказкам.

