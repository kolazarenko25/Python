"""Фасад системи: LibraryService (Singleton) поєднує репозиторії, фабрику,
шину подій і стратегії пошуку. Усі публічні методи потокобезпечні."""
import json
import threading

from . import events
from .decorators import log_call, synchronized
from .events import AuditObserver, EventBus, StatisticsObserver
from .exceptions import (DuplicateError, LibraryError, StorageError,
                         ValidationError)
from .factory import EntityFactory
from .metaclasses import SingletonMeta
from .repository import Repository
from .search import SearchStrategy
from .validators import normalize_isbn


class LibraryService(metaclass=SingletonMeta):
    def __init__(self):
        self._lock = threading.RLock()
        self.factory = EntityFactory()
        self.authors = Repository("Автор")
        self.books = Repository("Книга")
        self.readers = Repository("Читач")
        self.events = EventBus()
        self.audit = AuditObserver()
        self.stats = StatisticsObserver()
        self.events.subscribe(events.ALL_EVENTS, self.audit)
        self.events.subscribe(events.ALL_EVENTS, self.stats)

    # ---------- додавання сутностей ----------
    @log_call
    @synchronized()
    def add_author(self, name, birth_year, country="Україна"):
        author = self.factory.create("author", name=name,
                                     birth_year=birth_year, country=country)
        return self.authors.add(author)

    @log_call
    @synchronized()
    def add_book(self, title, author_id, year, isbn, copies=1):
        author = self.authors.get(author_id)
        if isinstance(isbn, str):
            normalized = normalize_isbn(isbn)
            if self.books.find(lambda b: b.isbn == normalized):
                raise DuplicateError(f"Книга з ISBN {normalized} уже є в каталозі")
        book = self.factory.create("book", title=title, author=author,
                                   year=year, isbn=isbn, copies=copies)
        self.books.add(book)
        self.events.publish(events.BOOK_ADDED, book_id=book.id, title=book.title)
        return book

    @log_call
    @synchronized()
    def register_reader(self, name, email):
        if self.readers.find(lambda r: r.email.lower() == str(email).strip().lower()):
            raise DuplicateError(f"Читач з e-mail {email} уже зареєстрований")
        reader = self.factory.create("reader", name=name, email=email)
        self.readers.add(reader)
        self.events.publish(events.READER_REGISTERED, reader_id=reader.id)
        return reader

    # ---------- видача та повернення ----------
    @log_call
    @synchronized()
    def borrow_book(self, reader_id, book_id):
        reader = self.readers.get(reader_id)
        book = self.books.get(book_id)
        reader.ensure_can_borrow(book.id)   # усі перевірки до зміни стану
        book.take_copy()
        reader.add_loan(book.id)
        self.events.publish(events.BOOK_BORROWED, reader_id=reader.id, book_id=book.id)
        return book

    @log_call
    @synchronized()
    def return_book(self, reader_id, book_id):
        reader = self.readers.get(reader_id)
        book = self.books.get(book_id)
        reader.remove_loan(book.id)
        book.return_copy()
        self.events.publish(events.BOOK_RETURNED, reader_id=reader.id, book_id=book.id)
        return book

    # ---------- запити ----------
    @log_call
    @synchronized()
    def search(self, strategy):
        if not isinstance(strategy, SearchStrategy):
            raise ValidationError("Стратегія пошуку має наслідувати SearchStrategy")
        return self.books.find(strategy.matches)

    @synchronized()
    def statistics(self):
        return {"authors": len(self.authors), "books": len(self.books),
                "readers": len(self.readers),
                "copies_total": sum(b.total_copies for b in self.books.all()),
                "copies_available": sum(b.available_copies for b in self.books.all()),
                "active_loans": sum(len(r.borrowed) for r in self.readers.all())}

    # ---------- збереження ----------
    @synchronized()
    def save(self, path):
        data = {"authors": [a.to_dict() for a in self.authors.all()],
                "books": [b.to_dict() for b in self.books.all()],
                "readers": [r.to_dict() for r in self.readers.all()]}
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except OSError as exc:
            raise StorageError(f"Не вдалося зберегти файл {path}: {exc}") from exc

    @synchronized()
    def load(self, path):
        """Завантажує стан атомарно: спочатку будує нові репозиторії,
        і лише за успіху підміняє поточні."""
        factory = EntityFactory()
        authors, books, readers = Repository("Автор"), Repository("Книга"), Repository("Читач")
        try:
            with open(path, encoding="utf-8") as f:
                data = json.load(f)
            for a in data["authors"]:
                authors.add(factory.restore("author", **a))
            for b in data["books"]:
                b = dict(b)
                author = authors.get(b.pop("author_id"))
                available = b.pop("available_copies")
                book = factory.restore("book", author=author, **b)
                if not 0 <= available <= book.total_copies:
                    raise ValidationError("Некоректна кількість доступних примірників")
                book.available_copies = available
                books.add(book)
            for r in data["readers"]:
                r = dict(r)
                borrowed = r.pop("borrowed")
                reader = factory.restore("reader", **r)
                reader.borrowed = set(borrowed)
                readers.add(reader)
        except (OSError, json.JSONDecodeError, KeyError, TypeError, LibraryError) as exc:
            raise StorageError(f"Не вдалося прочитати файл {path}: {exc}") from exc
        self.factory, self.authors, self.books, self.readers = factory, authors, books, readers
