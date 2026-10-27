"""Ієрархія власних виключень бібліотечної системи."""


class LibraryError(Exception):
    """Базовий клас усіх помилок системи."""


class ValidationError(LibraryError, ValueError):
    """Некоректні вхідні дані (тип, діапазон, формат)."""


class NotFoundError(LibraryError):
    """Сутність із заданим ідентифікатором не знайдено."""


class DuplicateError(LibraryError):
    """Спроба додати сутність, яка вже існує."""


class NoCopiesAvailableError(LibraryError):
    """Усі примірники книги вже видані."""


class LoanLimitError(LibraryError):
    """Читач досяг ліміту одночасно виданих книг."""


class BookNotBorrowedError(LibraryError):
    """Читач намагається повернути книгу, якої не брав."""


class StorageError(LibraryError):
    """Помилка збереження/завантаження даних."""
