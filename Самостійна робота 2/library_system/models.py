"""Предметна область: автори, книги, читачі."""
from .decorators import validate_args
from .exceptions import (BookNotBorrowedError, LibraryError, LoanLimitError,
                         NoCopiesAvailableError)
from .metaclasses import LoggingMeta
from .validators import (current_year, email_format, instance_of, int_range,
                         isbn13, non_empty_str, normalize_isbn, positive_int)


class Author(metaclass=LoggingMeta):
    @validate_args(author_id=positive_int(), name=non_empty_str(2, 100),
                   birth_year=int_range(1000, current_year()),
                   country=non_empty_str(2, 60))
    def __init__(self, author_id, name, birth_year, country="Україна"):
        self.id = author_id
        self.name = name.strip()
        self.birth_year = birth_year
        self.country = country.strip()

    def to_dict(self):
        return {"author_id": self.id, "name": self.name,
                "birth_year": self.birth_year, "country": self.country}

    def __repr__(self):
        return f"Author(id={self.id}, name={self.name!r})"


class Book(metaclass=LoggingMeta):
    @validate_args(book_id=positive_int(), title=non_empty_str(1, 200),
                   author=instance_of(Author), year=int_range(1400, current_year()),
                   isbn=isbn13(), copies=int_range(1, 1000))
    def __init__(self, book_id, title, author, year, isbn, copies=1):
        self.id = book_id
        self.title = title.strip()
        self.author = author
        self.year = year
        self.isbn = normalize_isbn(isbn)
        self.total_copies = copies
        self.available_copies = copies

    def take_copy(self):
        if self.available_copies <= 0:
            raise NoCopiesAvailableError(
                f"Усі примірники книги «{self.title}» вже видані")
        self.available_copies -= 1

    def return_copy(self):
        if self.available_copies >= self.total_copies:
            raise LibraryError(f"Книга «{self.title}»: усі примірники вже в бібліотеці")
        self.available_copies += 1

    def to_dict(self):
        return {"book_id": self.id, "title": self.title, "author_id": self.author.id,
                "year": self.year, "isbn": self.isbn, "copies": self.total_copies,
                "available_copies": self.available_copies}

    def __repr__(self):
        return (f"Book(id={self.id}, title={self.title!r}, "
                f"available={self.available_copies}/{self.total_copies})")


class Reader(metaclass=LoggingMeta):
    MAX_LOANS = 3

    @validate_args(reader_id=positive_int(), name=non_empty_str(2, 100),
                   email=email_format())
    def __init__(self, reader_id, name, email):
        self.id = reader_id
        self.name = name.strip()
        self.email = email.strip()
        self.borrowed = set()

    def ensure_can_borrow(self, book_id):
        if book_id in self.borrowed:
            raise LibraryError(f"Читач {self.name} вже має цю книгу (id={book_id})")
        if len(self.borrowed) >= self.MAX_LOANS:
            raise LoanLimitError(
                f"Читач {self.name} досяг ліміту ({self.MAX_LOANS}) виданих книг")

    def add_loan(self, book_id):
        self.ensure_can_borrow(book_id)
        self.borrowed.add(book_id)

    def remove_loan(self, book_id):
        if book_id not in self.borrowed:
            raise BookNotBorrowedError(
                f"Читач {self.name} не брав книгу з id={book_id}")
        self.borrowed.remove(book_id)

    def to_dict(self):
        return {"reader_id": self.id, "name": self.name, "email": self.email,
                "borrowed": sorted(self.borrowed)}

    def __repr__(self):
        return f"Reader(id={self.id}, name={self.name!r}, loans={len(self.borrowed)})"
