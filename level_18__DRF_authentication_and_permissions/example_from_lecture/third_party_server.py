import requests  # pip install requests

BASE_URL = "http://127.0.0.1:8000/api/books/"


def list_books():
    print("\n=== GET: список книг ===")
    resp = requests.get(BASE_URL)
    print(resp.status_code, resp.json())


def create_book():
    print("\n=== POST: создать книгу ===")
    data = {
        "title": "Мастер и Маргарита",
        "year_published": 1967,
        "author": 3
    }
    resp = requests.post(BASE_URL, json=data)
    print(resp.status_code, resp.json())
    return resp.json()["id"]


def get_book(book_id):
    print(f"\n=== GET: одна книга (id={book_id}) ===")
    resp = requests.get(f"{BASE_URL}{book_id}/")
    print(resp.status_code, resp.json())


def update_book(book_id):
    print(f"\n=== PUT: обновить книгу (id={book_id}) ===")
    data = {
        "title": "Мастер и Маргарита (обновлено)",
        "year_published": 1968,
        "author": 3
    }
    resp = requests.put(f"{BASE_URL}{book_id}/", json=data)
    print(resp.status_code, resp.json())


def patch_book(book_id):
    print(f"\n=== PATCH: частичное обновление книги (id={book_id}) ===")
    data = {"year_published": 1973}
    resp = requests.patch(f"{BASE_URL}{book_id}/", json=data)
    print(resp.status_code, resp.json())


def delete_book(book_id):
    print(f"\n=== DELETE: удалить книгу (id={book_id}) ===")
    resp = requests.delete(f"{BASE_URL}{book_id}/")
    print(resp.status_code, resp.text)


if __name__ == "__main__":
    # 1. Список книг
    list_books()

    # 2. Создать книгу
    new_id = create_book()

    # 3. Получить одну книгу
    get_book(new_id)

    # 4. Обновить книгу полностью (PUT)
    update_book(new_id)

    # 5. Обновить книгу частично (PATCH)
    patch_book(new_id)

    # 6. Удалить книгу
    delete_book(new_id)

    # 7. Снова вывести список книг
    list_books()
