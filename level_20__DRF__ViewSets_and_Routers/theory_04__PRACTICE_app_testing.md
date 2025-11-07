Итак, у нас готово вью `FeedbackViewSet`, которое поддерживает **6 операций**:

* `list` → `GET /api/feedback/`
* `retrieve` → `GET /api/feedback/{id}/`
* `create` → `POST /api/feedback/`
* `update → PUT /api/feedback/{id}/` (полная замена)
* `partial_update → PATCH /api/feedback/{id}/` (частичная замена)
* `destroy` → `DELETE /api/feedback/{id}/`


---

## 1. Добавим несколько сообщений (`create`)

### Запрос 1

```bash
curl -X POST http://127.0.0.1:8000/api/feedback/ \
  -H "Content-Type: application/json" \
  -d '{"date":"2025-10-03T12:00:00Z","user_email":"alice@example.com","message":"Привет, это первое сообщение"}' \
| python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), ensure_ascii=False, indent=4))"
```

✅ Ответ:

```json
{
  "id": 1,
  "date": "2025-10-03T12:00:00Z",
  "user_email": "alice@example.com",
  "message": "Привет, это первое сообщение"
}
```

---

### Запрос 2

```bash
curl -X POST http://127.0.0.1:8000/api/feedback/ \
  -H "Content-Type: application/json" \
  -d '{"date":"2025-10-03T12:05:00Z","user_email":"bob@example.com","message":"А это второе сообщение"}' \
| python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), ensure_ascii=False, indent=4))"
```

✅ Ответ:

```json
{
  "id": 2,
  "date": "2025-10-03T12:05:00Z",
  "user_email": "bob@example.com",
  "message": "А это второе сообщение"
}
```

---

## 2. Получить список всех сообщений (`list`)

```bash
curl -X GET http://127.0.0.1:8000/api/feedback/ \
| python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), ensure_ascii=False, indent=4))"

```

✅ Ответ:

```json
[
  {
    "id": 1,
    "date": "2025-10-03T12:00:00Z",
    "user_email": "alice@example.com",
    "message": "Привет, это первое сообщение"
  },
  {
    "id": 2,
    "date": "2025-10-03T12:05:00Z",
    "user_email": "bob@example.com",
    "message": "А это второе сообщение"
  }
]
```

---

## 3. Получить одно сообщение (`retrieve`)

```bash
curl -X GET http://127.0.0.1:8000/api/feedback/1/
```

✅ Ответ:

```json
{
  "id": 1,
  "date": "2025-10-03T12:00:00Z",
  "user_email": "alice@example.com",
  "message": "Привет, это первое сообщение"
}
```

---

## 4. Обновить сообщение (`update`)

```bash
curl -X PUT http://127.0.0.1:8000/api/feedback/1/ \
  -H "Content-Type: application/json" \
  -d '{"date":"2025-10-03T12:10:00Z","user_email":"alice@example.com","message":"Сообщение обновлено"}' \
| python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), ensure_ascii=False, indent=4))"
```

✅ Ответ:

```json
{
  "id": 1,
  "date": "2025-10-03T12:10:00Z",
  "user_email": "alice@example.com",
  "message": "Сообщение обновлено полностью"
}
```

---

## 5. Частично обновить сообщение (`partial_update`)

```bash
curl -X PATCH http://127.0.0.1:8000/api/feedback/1/ \
  -H "Content-Type: application/json" \
  -d '{"message":"Обновлено только сообщение"}' \
| python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), ensure_ascii=False, indent=4))"
```

---

## 6. Удалить сообщение (`destroy`)

```bash
curl -i -X DELETE http://127.0.0.1:8000/api/feedback/2/ 
```

✅ Ответ:

```http
HTTP/1.1 204 No Content
Date: Fri, 03 Oct 2025 18:07:30 GMT
Server: WSGIServer/0.2 CPython/3.12.10
Allow: GET, PUT, PATCH, DELETE, HEAD, OPTIONS
X-Frame-Options: DENY
Content-Length: 0
Vary: Cookie
X-Content-Type-Options: nosniff
Referrer-Policy: same-origin
Cross-Origin-Opener-Policy: same-origin
```

---

## 7. Проверить список после удаления (`list`)

```bash
curl -X GET http://127.0.0.1:8000/api/feedback/ \
| python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), ensure_ascii=False, indent=4))"
```

✅ Ответ:

```json
[
  {
    "id": 1,
    "date": "2025-10-03T12:10:00Z",
    "user_email": "alice@example.com",
    "message": "Сообщение обновлено"
  }
]
```

## 8. Проверить надёжность работы `update`

```bash
curl -X PUT http://127.0.0.1:8000/api/feedback/1/ \
  -H "Content-Type: application/json" \
  -d '{"date": "2025-10-03T12:30:00Z"}' \
| python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), ensure_ascii=False, indent=4))"
```

❌ ошибка валидации.

Результат:

```json
{
    "user_email": [
        "This field is required."
    ],
    "message": [
        "This field is required."
    ]
}
```

---

### 9. Тот же запрос для частичного обновления (`partial_update`)`

```bash
curl -X PATCH http://127.0.0.1:8000/api/feedback/1/ \
  -H "Content-Type: application/json" \
  -d '{"message": "Изменено частично"}' \
| python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), ensure_ascii=False, indent=4))"
```

✅ Работает даже без `date` и `user_email`.

Результат:

```json
{"id": 2, "date": "2025-10-03T12:05:00Z", "user_email": "bob@example.com", "message": "Изменено частично"}
```

-