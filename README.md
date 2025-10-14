https://ccbv.co.uk

Если вы используете PyCharm (в том числе Community), то гораздо удобнее  
будет работать через Python-консоль, чем `через shell`:

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()
```

