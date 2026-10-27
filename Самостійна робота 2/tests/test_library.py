import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from library_system import LibraryService
from library_system.concurrency import RequestProcessor
from library_system.exceptions import (DuplicateError, LoanLimitError, NoCopiesAvailableError,
                                       NotFoundError, StorageError, ValidationError,
                                       BookNotBorrowedError)
from library_system.factory import EntityFactory
from library_system.metaclasses import SingletonMeta
from library_system.models import Author, Book, Reader
from library_system.search import ByAuthor, ByTitle, ByYearRange
from library_system.validators import isbn13_with_check


def isbn(n):
    return isbn13_with_check(f"978966{n:06d}")


class BaseCase(unittest.TestCase):
    def setUp(self):
        SingletonMeta.reset(LibraryService)
        self.s = LibraryService()
        self.author = self.s.add_author("Іван Франко", 1856)


class ValidationTests(BaseCase):
    def test_empty_author_name(self):
        with self.assertRaises(ValidationError):
            self.s.add_author(" ", 1900)

    def test_wrong_type_year(self):
        with self.assertRaises(ValidationError):
            self.s.add_author("Тест Тестов", "1900")

    def test_future_year(self):
        with self.assertRaises(ValidationError):
            self.s.add_book("Книга", self.author.id, 3000, isbn(1))

    def test_bad_isbn(self):
        with self.assertRaises(ValidationError):
            self.s.add_book("Книга", self.author.id, 2000, "9780000000000")

    def test_bad_email(self):
        with self.assertRaises(ValidationError):
            self.s.register_reader("Іван Іванов", "bad")

    def test_author_must_be_instance(self):
        with self.assertRaises(ValidationError):
            Book(1, "Книга", "не автор", 2000, isbn(1))

    def test_failed_creation_does_not_consume_id(self):
        with self.assertRaises(ValidationError):
            self.s.add_book("", self.author.id, 2000, isbn(1))
        self.assertEqual(self.s.add_book("Ок", self.author.id, 2000, isbn(1)).id, 1)


class MetaclassTests(BaseCase):
    def test_instance_logging(self):
        with self.assertLogs("library.meta", level="INFO") as cm:
            Author(100, "Леся Українка", 1871)
        self.assertTrue(any("Створено об'єкт" in m for m in cm.output))

    def test_counter_increments(self):
        before = Author.created_count
        Author(101, "Леся Українка", 1871)
        self.assertEqual(Author.created_count, before + 1)

    def test_singleton(self):
        self.assertIs(LibraryService(), self.s)

    def test_failed_creation_logged(self):
        with self.assertLogs("library.meta", level="WARNING"):
            with self.assertRaises(ValidationError):
                Author(102, "", 1871)


class ServiceTests(BaseCase):
    def setUp(self):
        super().setUp()
        self.book = self.s.add_book("Захар Беркут", self.author.id, 1883, isbn(1), copies=1)
        self.r1 = self.s.register_reader("Олена Коваль", "o@example.com")
        self.r2 = self.s.register_reader("Андрій Мельник", "a@example.com")

    def test_borrow_and_return(self):
        self.s.borrow_book(self.r1.id, self.book.id)
        self.assertEqual(self.book.available_copies, 0)
        self.s.return_book(self.r1.id, self.book.id)
        self.assertEqual(self.book.available_copies, 1)

    def test_no_copies(self):
        self.s.borrow_book(self.r1.id, self.book.id)
        with self.assertRaises(NoCopiesAvailableError):
            self.s.borrow_book(self.r2.id, self.book.id)

    def test_return_not_borrowed(self):
        with self.assertRaises(BookNotBorrowedError):
            self.s.return_book(self.r1.id, self.book.id)

    def test_loan_limit(self):
        for i in range(2, 5):
            self.s.add_book(f"Книга {i}", self.author.id, 1900, isbn(i), copies=2)
        for book_id in (1, 2, 3):
            self.s.borrow_book(self.r1.id, book_id)
        with self.assertRaises(LoanLimitError):
            self.s.borrow_book(self.r1.id, 4)
        self.assertEqual(self.s.books.get(4).available_copies, 2)  # стан не змінено

    def test_duplicates(self):
        with self.assertRaises(DuplicateError):
            self.s.add_book("Інша", self.author.id, 1900, isbn(1))
        with self.assertRaises(DuplicateError):
            self.s.register_reader("Хтось Інший", "O@example.com")

    def test_not_found(self):
        with self.assertRaises(NotFoundError):
            self.s.borrow_book(999, self.book.id)

    def test_search_strategies(self):
        self.assertEqual(len(self.s.search(ByAuthor("франко"))), 1)
        self.assertEqual(len(self.s.search(ByTitle("беркут"))), 1)
        self.assertEqual(self.s.search(ByYearRange(1900, 2000)), [])
        with self.assertRaises(ValidationError):
            ByYearRange(2000, 1900)

    def test_factory_unknown_kind(self):
        with self.assertRaises(ValidationError):
            EntityFactory().create("magazine")

    def test_observer_statistics(self):
        self.s.borrow_book(self.r1.id, self.book.id)
        self.assertEqual(self.s.stats.counter["book_borrowed"], 1)
        self.assertEqual(self.s.stats.counter["book_added"], 1)

    def test_save_load_roundtrip(self):
        self.s.borrow_book(self.r1.id, self.book.id)
        before = self.s.statistics()
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "db.json")
            self.s.save(path)
            self.s.load(path)
            self.assertEqual(self.s.statistics(), before)
            self.assertEqual(self.s.add_book("Нова", self.author.id, 1900, isbn(9)).id, 2)

    def test_load_errors(self):
        with tempfile.TemporaryDirectory() as d:
            bad = os.path.join(d, "bad.json")
            with open(bad, "w") as f:
                f.write("{не json")
            with self.assertRaises(StorageError):
                self.s.load(bad)
            with self.assertRaises(StorageError):
                self.s.load(os.path.join(d, "nope.json"))
        self.assertEqual(len(self.s.books), 1)  # стан не пошкоджено


class ConcurrencyTests(BaseCase):
    def test_parallel_borrow_respects_copies(self):
        book = self.s.add_book("Бестселер", self.author.id, 2000, isbn(1), copies=5)
        readers = [self.s.register_reader(f"Читач Номер{i}", f"u{i}@example.com") for i in range(60)]
        proc = RequestProcessor(workers=16)
        results = proc.run_batch([(f"b{r.id}", self.s.borrow_book, (r.id, book.id)) for r in readers])
        self.assertEqual(sum(r.ok for r in results), 5)
        self.assertEqual(book.available_copies, 0)
        self.assertTrue(all("NoCopiesAvailableError" in r.error for r in results if not r.ok))

    def test_parallel_registration_unique_ids(self):
        proc = RequestProcessor(workers=16)
        results = proc.run_batch([(f"r{i}", self.s.register_reader,
                                   (f"Читач Номер{i}", f"x{i}@example.com")) for i in range(100)])
        ids = [r.value.id for r in results]
        self.assertEqual(len(set(ids)), 100)

    def test_parallel_duplicate_email(self):
        proc = RequestProcessor(workers=16)
        results = proc.run_batch([(f"r{i}", self.s.register_reader,
                                   ("Той Самий", "same@example.com")) for i in range(30)])
        self.assertEqual(sum(r.ok for r in results), 1)

    def test_inventory_invariant_under_mixed_load(self):
        book = self.s.add_book("Книга", self.author.id, 2000, isbn(1), copies=3)
        readers = [self.s.register_reader(f"Читач Номер{i}", f"m{i}@example.com") for i in range(30)]
        reqs = []
        for r in readers:
            reqs += [("b", self.s.borrow_book, (r.id, book.id)),
                     ("r", self.s.return_book, (r.id, book.id)),
                     ("s", self.s.search, (ByTitle("кн"),))]
        RequestProcessor(workers=12).run_batch(reqs)
        st = self.s.statistics()
        self.assertEqual(st["copies_available"] + st["active_loans"], st["copies_total"])

    def test_speedup(self):
        reqs = [(f"q{i}", self.s.search, (ByTitle("а"),)) for i in range(20)]
        import time
        t = time.perf_counter(); RequestProcessor(1, 0.03).run_sequential(reqs); seq = time.perf_counter() - t
        t = time.perf_counter(); RequestProcessor(10, 0.03).run_batch(reqs); par = time.perf_counter() - t
        self.assertLess(par, seq / 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
