"""Завдання 6 (Django): HTTP-тести маршрутів і views."""


def test_book_list_ok_and_template(client, book):
    response = client.get("/")
    assert response.status_code == 200
    assert "library/book_list.html" in [t.name for t in response.templates]
    assert "Кобзар" in response.content.decode()


def test_book_list_empty_catalog(client, db):
    response = client.get("/")
    assert response.status_code == 200
    assert "Книг поки немає." in response.content.decode()


def test_book_detail_ok(client, book):
    response = client.get(f"/books/{book.pk}/")
    assert response.status_code == 200
    body = response.content.decode()
    assert "Тарас Шевченко" in body
    assert book.isbn in body


def test_book_detail_not_found(client, db):
    response = client.get("/books/9999/")
    assert response.status_code == 404


def test_loans_redirects_anonymous_user(client, db):
    response = client.get("/loans/")
    assert response.status_code == 302
    assert response.url.startswith("/admin/login/")


def test_loans_available_for_authenticated_user(auth_client, loan):
    response = auth_client.get("/loans/")
    assert response.status_code == 200
    assert "Олена Коваль" in response.content.decode()
