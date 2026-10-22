from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from .extensions import db
from .models import Author, Book

bp = Blueprint("main", __name__)

REQUIRED_FIELDS = ("title", "isbn", "author_id", "year")


@bp.get("/api/books")
def list_books():
    books = Book.query.order_by(Book.title).all()
    return jsonify([b.to_dict() for b in books])


@bp.get("/api/books/<int:book_id>")
def get_book(book_id):
    book = db.get_or_404(Book, book_id)
    return jsonify(book.to_dict())


@bp.post("/api/books")
def create_book():
    data = request.get_json(silent=True) or {}
    missing = [f for f in REQUIRED_FIELDS if f not in data]
    if missing:
        return jsonify(error="Відсутні поля: " + ", ".join(missing)), 400
    if db.session.get(Author, data["author_id"]) is None:
        return jsonify(error="Автора не знайдено"), 400

    book = Book(
        title=data["title"],
        isbn=data["isbn"],
        year=data["year"],
        author_id=data["author_id"],
    )
    db.session.add(book)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify(error="Книга з таким ISBN уже існує"), 409
    return jsonify(book.to_dict()), 201
