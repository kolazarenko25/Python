"""Завдання 5 (Django): тести моделей."""
from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.utils import timezone

from library.models import Book, Loan, ReaderProfile


def test_str_representations(author, genre, book, reader):
    assert str(author) == "Тарас Шевченко"
    assert str(genre) == "Поезія"
    assert str(book) == "Кобзар (Тарас Шевченко)"
    assert str(reader) == "Олена Коваль"


def test_book_default_values(book):
    assert book.copies_total == 1
    assert book.status == Book.STATUS_AVAILABLE
    assert book.created_at is not None


def test_isbn_must_be_unique(book, author):
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            Book.objects.create(title="Дублікат", isbn=book.isbn, author=author, year=2000)


@pytest.mark.parametrize(
    "isbn",
    ["123", "12345678901234"],  # закороткий (<13) і задовгий (>13)
    ids=["too_short", "too_long"],
)
def test_isbn_length_validation(author, isbn):
    candidate = Book(title="Тест", isbn=isbn, author=author, year=2000)
    with pytest.raises(ValidationError) as exc:
        candidate.full_clean()
    assert "isbn" in exc.value.message_dict


def test_many_to_many_books_and_genres(book, genre):
    assert list(book.genres.all()) == [genre]
    assert list(genre.books.all()) == [book]


def test_one_to_one_profile(reader, profile):
    assert reader.profile == profile
    assert profile.reader == reader
    with pytest.raises(IntegrityError):
        with transaction.atomic():
            ReaderProfile.objects.create(reader=reader, phone="000")


def test_protect_prevents_author_deletion(author, book):
    with pytest.raises(ProtectedError):
        author.delete()
    assert Book.objects.filter(pk=book.pk).exists()


def test_cascade_deletes_profile_and_loans(reader, profile, loan):
    reader.delete()
    assert not ReaderProfile.objects.filter(pk=profile.pk).exists()
    assert not Loan.objects.filter(pk=loan.pk).exists()


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
    today = timezone.localdate()  # та сама «поточна дата», що й у Loan.is_overdue()
    loan.due_date = today + timedelta(days=days_until_due)
    loan.returned_at = today if returned else None
    assert loan.is_overdue() is expected
