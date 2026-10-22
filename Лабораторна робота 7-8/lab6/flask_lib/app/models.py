"""Моделі Flask-SQLAlchemy — та сама предметна область «Інтернет-бібліотека».

Відповідність зв'язків до Django-версії:
    Author 1─* Book            db.ForeignKey + db.relationship(backref="author")
    Book   *─* Genre           явна проміжна таблиця db.Table("book_genres")
    Reader 1─1 ReaderProfile   db.ForeignKey(unique=True) + relationship(uselist=False)
    Reader 1─* Loan            cascade="all, delete-orphan"
    Book   1─* Loan
"""
from datetime import date, datetime, timezone

from .extensions import db

# Проміжна таблиця для зв'язку «багато-до-багатьох» Book <-> Genre.
book_genres = db.Table(
    "book_genres",
    db.Column("book_id", db.Integer, db.ForeignKey("books.id"), primary_key=True),
    db.Column("genre_id", db.Integer, db.ForeignKey("genres.id"), primary_key=True),
)


def _utcnow():
    return datetime.now(timezone.utc)


class Author(db.Model):
    __tablename__ = "authors"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    country = db.Column(db.String(2), nullable=False, default="UA")
    birth_year = db.Column(db.Integer)
    bio = db.Column(db.Text, default="")

    # backref="author" створює атрибут book.author; lazy="select" — завантаження за вимогою.
    books = db.relationship("Book", backref="author", lazy="select")

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Author {self.name!r}>"


class Genre(db.Model):
    __tablename__ = "genres"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False, unique=True)
    slug = db.Column(db.String(80), nullable=False, unique=True)
    description = db.Column(db.Text, default="")

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Genre {self.slug!r}>"


class Book(db.Model):
    __tablename__ = "books"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    isbn = db.Column(db.String(13), nullable=False, unique=True)
    year = db.Column(db.Integer, nullable=False)
    copies_total = db.Column(db.Integer, nullable=False, default=1)
    author_id = db.Column(db.Integer, db.ForeignKey("authors.id"), nullable=False)

    # --- КРОК 2 (Завдання 3) -------------------------------------------------
    # Після першої ревізії РОЗКОМЕНТУЙТЕ наступний рядок і виконайте
    #   flask --app run db migrate -m "add book pages"
    #   flask --app run db upgrade
    # pages = db.Column(db.Integer, default=0)
    # -------------------------------------------------------------------------

    genres = db.relationship("Genre", secondary=book_genres, backref=db.backref("books", lazy="select"))

    def __str__(self):
        return f"{self.title} ({self.author.name})"

    def __repr__(self):
        return f"<Book {self.isbn}>"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "isbn": self.isbn,
            "year": self.year,
            "author": self.author.name,
            "genres": sorted(g.name for g in self.genres),
        }


class Reader(db.Model):
    __tablename__ = "readers"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(254), nullable=False, unique=True)
    card_number = db.Column(db.String(12), unique=True)
    registered_at = db.Column(db.DateTime, default=_utcnow)

    # Видалення читача каскадно видаляє профіль і видачі.
    profile = db.relationship(
        "ReaderProfile", backref="reader", uselist=False, cascade="all, delete-orphan"
    )
    loans = db.relationship("Loan", backref="reader", cascade="all, delete-orphan")

    def __str__(self):
        return self.full_name

    def __repr__(self):
        return f"<Reader {self.email!r}>"


class ReaderProfile(db.Model):
    __tablename__ = "reader_profiles"

    id = db.Column(db.Integer, primary_key=True)
    # unique=True на зовнішньому ключі робить зв'язок «один-до-одного».
    reader_id = db.Column(db.Integer, db.ForeignKey("readers.id"), nullable=False, unique=True)
    phone = db.Column(db.String(20), default="")
    address = db.Column(db.String(255), default="")
    newsletter = db.Column(db.Boolean, nullable=False, default=False)

    def __str__(self):
        return f"Профіль: {self.reader.full_name}"


class Loan(db.Model):
    __tablename__ = "loans"

    id = db.Column(db.Integer, primary_key=True)
    reader_id = db.Column(db.Integer, db.ForeignKey("readers.id"), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    loaned_at = db.Column(db.Date, nullable=False, default=date.today)
    due_date = db.Column(db.Date, nullable=False)
    returned_at = db.Column(db.Date)

    book = db.relationship("Book", backref="loans")

    def __str__(self):
        return f"{self.reader.full_name} → {self.book.title}"

    def is_overdue(self):
        if self.returned_at is not None:
            return False
        return self.due_date < date.today()
