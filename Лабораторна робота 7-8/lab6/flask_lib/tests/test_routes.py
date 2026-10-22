"""Завдання 6 (Flask): HTTP-тести REST API через тестовий клієнт pytest-flask."""
import pytest

from app.models import Book


def test_list_books_ok(client, book):
    response = client.get("/api/books")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 1
    assert data[0]["title"] == "Кобзар"
    assert data[0]["author"] == "Тарас Шевченко"


def test_get_book_ok(client, book):
    response = client.get(f"/api/books/{book.id}")
    assert response.status_code == 200
    assert response.get_json()["isbn"] == "9789660001001"


def test_get_book_not_found(client):
    response = client.get("/api/books/9999")
    assert response.status_code == 404
    assert response.get_json() == {"error": "Не знайдено"}


def test_create_book_returns_201(client, db, author):
    payload = {"title": "Гайдамаки", "isbn": "9789660002001", "author_id": author.id, "year": 1841}
    response = client.post("/api/books", json=payload)
    assert response.status_code == 201
    assert response.get_json()["title"] == "Гайдамаки"
    assert Book.query.filter_by(isbn="9789660002001").count() == 1


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"title": "Без ISBN"},
        {"title": "Без автора", "isbn": "9789660002002", "year": 2000},
    ],
    ids=["empty", "no_isbn", "no_author_id"],
)
def test_create_book_missing_fields_returns_400(client, db, payload):
    response = client.post("/api/books", json=payload)
    assert response.status_code == 400
    assert "Відсутні поля" in response.get_json()["error"]


def test_create_book_unknown_author_returns_400(client, db):
    payload = {"title": "X", "isbn": "9789660002003", "author_id": 12345, "year": 2000}
    response = client.post("/api/books", json=payload)
    assert response.status_code == 400


def test_create_book_duplicate_isbn_returns_409(client, db, book, author):
    payload = {"title": "Дубль", "isbn": book.isbn, "author_id": author.id, "year": 2000}
    response = client.post("/api/books", json=payload)
    assert response.status_code == 409
    assert Book.query.count() == 1  # rollback залишив базу без змін
