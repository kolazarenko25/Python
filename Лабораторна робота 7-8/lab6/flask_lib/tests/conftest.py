"""Спільні фікстури для тестів Flask-проєкту.

Кожен тест отримує власну порожню in-memory SQLite-базу: продуктивна
library.db не чіпається, а порядок виконання тестів не має значення.
"""
from datetime import date

import pytest

from app import create_app
from app.extensions import db as _db
from app.models import Author, Book, Genre, Loan, Reader, ReaderProfile


@pytest.fixture
def app():
    """Тестовий додаток (потрібна pytest-flask для фікстури client)."""
    app = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:"})
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def db(app):
    return _db


@pytest.fixture
def author(db):
    obj = Author(name="Тарас Шевченко", country="UA", birth_year=1814)
    db.session.add(obj)
    db.session.commit()
    return obj


@pytest.fixture
def genre(db):
    obj = Genre(name="Поезія", slug="poetry")
    db.session.add(obj)
    db.session.commit()
    return obj


@pytest.fixture
def book(db, author, genre):
    obj = Book(title="Кобзар", isbn="9789660001001", year=1840, author=author, genres=[genre])
    db.session.add(obj)
    db.session.commit()
    return obj


@pytest.fixture
def reader(db):
    obj = Reader(full_name="Олена Коваль", email="olena@example.com", card_number="LIB-000001")
    db.session.add(obj)
    db.session.commit()
    return obj


@pytest.fixture
def profile(db, reader):
    obj = ReaderProfile(reader=reader, phone="+380501112233", address="Київ")
    db.session.add(obj)
    db.session.commit()
    return obj


@pytest.fixture
def loan(db, reader, book):
    obj = Loan(reader=reader, book=book, loaned_at=date(2026, 1, 1), due_date=date(2026, 1, 15))
    db.session.add(obj)
    db.session.commit()
    return obj
