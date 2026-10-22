"""Спільні фікстури для тестів Django-проєкту."""
from datetime import date, timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone

from library.models import Author, Book, Genre, Loan, Reader, ReaderProfile


@pytest.fixture
def user(db):
    """Тестовий користувач (персонал бібліотеки)."""
    return get_user_model().objects.create_user(username="tester", password="pass12345")


@pytest.fixture
def auth_client(client, user):
    """HTTP-клієнт, уже залогінений як тестовий користувач."""
    client.force_login(user)
    return client


@pytest.fixture
def author(db):
    return Author.objects.create(name="Тарас Шевченко", country="UA", birth_year=1814)


@pytest.fixture
def genre(db):
    return Genre.objects.create(name="Поезія", slug="poetry")


@pytest.fixture
def book(db, author, genre):
    b = Book.objects.create(title="Кобзар", isbn="9789660001001", author=author, year=1840)
    b.genres.add(genre)
    return b


@pytest.fixture
def reader(db):
    return Reader.objects.create(full_name="Олена Коваль", email="olena@example.com")


@pytest.fixture
def profile(db, reader):
    return ReaderProfile.objects.create(reader=reader, phone="+380501112233", address="Київ")


@pytest.fixture
def loan(db, reader, book):
    return Loan.objects.create(
        reader=reader,
        book=book,
        loaned_at=date(2026, 1, 1),
        due_date=date(2026, 1, 15),
    )


@pytest.fixture
def overdue_loan(loan):
    """Видача, прострочена відносно реальної поточної дати."""
    loan.due_date = timezone.localdate() - timedelta(days=3)
    return loan
