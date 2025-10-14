## Что такое "ленивый запрос"?

"Ленивость" (`laziness`) для `QuerySet` означает: SQL-запрос к БД **не выполняется, пока не потребуется результат**.
Например:
 - при итерации, 
 - преобразовании в список,
 - при явном доступе к данным,
 - и т.д.

Для доказательства "ленивости" импортируем `connection.queries` - это специальный список,  
в который Django добавляет все выполненные SQL-запросы в рамках одного HTTP-запроса.  
При условии, что `DEBUG = True`

## Что считается "одним SQL-запросом"?

Каждый отдельно отправленный SQL-запрос к базе данных считается одним элементом в `connection.queries`. 
Например:
```
    SELECT * FROM myapp_model ... — один запрос
    UPDATE ... WHERE ... — другой
    INSERT INTO ... — третий
    И т.д.
```

## Важно: 
Один вызов QuerySet'а не обязательно = один SQL-запрос!
Но, чаще всего, один вызов QuerySet'а == один SQL-запрос


## Внесём изменение в `MyAppListView`, чтобы протестировать обращения к БД

```python

from django.db import connection

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        qs = MyappModel.objects.all()  # QuerySet создан, но не выполнен
        print(f'[DEBUG] After QuerySet creation: {len(connection.queries)} SQL queries')
        print('qs.query:', qs.query)
        print('qs._result_cache:', qs._result_cache)
        for q in qs:
            print(q)
            print(f'[DEBUG] in loop: {len(connection.queries)} SQL queries')
        print(f'[DEBUG] after loop: {len(connection.queries)} SQL queries')
        print('qs._result_cache:', qs._result_cache)

       context['active_page'] = 'myapp'
        print(f'[DEBUG] After context_data: {len(connection.queries)} SQL queries')
        return context
```


Результат запроса будет примерно таким:
```djangourlpath
[DEBUG] After QuerySet creation: 0 SQL queries
default: Автоматически добавлено мной лично
[DEBUG] in loop: 1 SQL queries
example 1: comment 1
[DEBUG] in loop: 1 SQL queries
example_3: example volume 3
[DEBUG] in loop: 1 SQL queries
[DEBUG] after loop: 1 SQL queries
[DEBUG] After context_data: 1 SQL queries
[29/Jul/2025 13:14:20] "GET /myapp/ HTTP/1.1" 200 1422
```

## Вывод

Как видим, запрос к БД был сделан ТОЛЬКО один раз - когда был обращение в цикле `[DEBUG] in loop`

Причём, повторные обращение к одному и тому же QuerySet НЕ инициировали новый запрос к БД.


## Перенос выполнения запроса на страницу шаблона

Мы можем добавить вывод `connection.query` непосредственно в шаблон.  
Причём дважды: перед выводом списка и после:

### `templates/myapp/myappmodel_list.html`

```djangourlpath
{% block content %}
<h2>This is Myapp Page</h2>
connection.queries: {{ connection.queries | length }}
<ul>
{% for obj in object_list %}
    <li>{{ obj.code }} - {{ obj.value }}</li>
{% empty %}
    <li>Sorry, no data in this list.</li>
{% endfor %}
</ul>
connection.queries: {{ connection.queries | length }}
{% endblock %}
```

Теперь изменим метод в нашей view:
- закомментим цикл, который ранее инициировал запрос;
- добавим в `context` объект `connection;
- изменим в `context` переменную `object_list`, чтобы избежать параллельного запроса самой generic view по умолчанию

```python
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        qs = MyappModel.objects.all()  # QuerySet создан, но не выполнен
        print(f'[DEBUG] After QuerySet creation: {len(connection.queries)} SQL queries')
        print('qs.query:', qs.query)
        print('qs._result_cache:', qs._result_cache)
        # for q in qs:
        #     print(q)
        #     print(f'[DEBUG] in loop: {len(connection.queries)} SQL queries')
        print(f'[DEBUG] after loop: {len(connection.queries)} SQL queries')
        print('qs._result_cache:', qs._result_cache)

        context['active_page'] = 'myapp'
        context['connection'] = connection
        context['object_list'] = qs
        print(f'[DEBUG] After context_data: {len(connection.queries)} SQL queries')
        return context
```

Теперь на самой страницы `len(connection.queries)` будет равно 0 вплоть до вывода списка значений.

И станет равно 1 только ПОСЛЕ вывода содержимого QuerySet на страницу шаблона.


## Запрос будет выполнен только один раз

Если раскомментировать цикл во view, мы увидим,   
что запрос будет выполнен только один раз - в теле цикла.  
А в HTML-шаблоне будет лишь повторён закэшированный результат этого запроса.

После первого "прогона", атрибут QuerySet'a `_result_cache`  
изменит своё дефолтное None на результат запроса.  
(в нашем случае - список строк таблицы)
