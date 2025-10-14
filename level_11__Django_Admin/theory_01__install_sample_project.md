Для этой темы создадим новый проект со слегка адаптированной БД.

На этот раз загрузка будет из фикстуры `books_fixture.json` -  
специального json-файла с dump'ом базы данных. 

Можно 
- либо скачать все файла проекта и выполнить следующие команды
```bash
./manage.py makemigratidons
./manage.py migrate
./manage.py loaddata books_fixture.json
./manage.py createsuperuser
```
- либо воспользоваться готовой установленной базой, для чего:
  - переименовать `db.sqlite3--` в `db.sqlite3--`
  - зайти в админку (`http://127.0.0.1:8000/admin/`) с логином `root` и паролем `123`
