"""Завдання 5 (Flask): тести моделей."""
from datetime import date, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from app.models import Author, Book, Loan, ReaderProfile


def test_str_and_repr(author, genre, book, reader):
    assert str(author) == "Тарас Шевченко"
    assert str(genre) == "Поезія"
    assert str(book) == "Кобзар (Тарас Шевченко)"
    assert repr(book) == "<Book 9789660001001>"
    assert str(reader) == "Олена Коваль"


def test_book_default_values(book):
    assert book.copies_total == 1
    assert book.to_dict()["genres"] == ["Поезія"]


def test_isbn_must_be_unique(db, book, author):
    db.session.add(Book(title="Дублікат", isbn=book.isbn, year=2000, author=author))
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()


def test_many_to_many_books_and_genres(book, genre):
    assert book.genres == [genre]
    assert genre.books == [book]


def test_one_to_one_profile(db, reader, profile):
    assert reader.profile is profile
    assert profile.reader is reader
    db.session.add(ReaderProfile(reader_id=reader.id, phone="000"))
    with pytest.raises(IntegrityError):  # unique=True на reader_id
        db.session.commit()
    db.session.rollback()


def test_author_with_books_cannot_be_deleted(db, author, book):
    author_id = author.id
    db.session.delete(author)
    with pytest.raises(IntegrityError):  # books.author_id NOT NULL
        db.session.commit()
    db.session.rollback()
    assert db.session.get(Author, author_id) is not None


def test_cascade_deletes_profile_and_loans(db, reader, profile, loan):
    profile_id, loan_id = profile.id, loan.id
    db.session.delete(reader)
    db.session.commit()
    assert db.session.get(ReaderProfile, profile_id) is None
    assert db.session.get(Loan, loan_id) is None


@pytest.mark.parametrize(
    "days_until_due, returned, expected",
    [
        (-1, False, True),    # термін минув вчора, не повернена
        (0, False, False),    # граничний випадок: термін спливає сьогодні
        (7, False, False),    # ще є час
        (-10, True, False),   # прострочена, але вже повернена
    ],
    ids=["overdue", "due_today", "in_time", "returned_late"],
)
def test_loan_is_overdue(loan, days_until_due, returned, expected):
    today = date.today()
    loan.due_date = today + timedelta(days=days_until_due)
    loan.returned_at = today if returned else None
    assert loan.is_overdue() is expected
