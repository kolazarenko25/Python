"""Паттерн Strategy: взаємозамінні алгоритми пошуку книг."""
from .decorators import validate_args
from .exceptions import ValidationError
from .validators import int_range, non_empty_str


class SearchStrategy:
    def matches(self, book):
        raise NotImplementedError


class ByTitle(SearchStrategy):
    @validate_args(text=non_empty_str(1, 100))
    def __init__(self, text):
        self.text = text.strip().lower()

    def matches(self, book):
        return self.text in book.title.lower()


class ByAuthor(SearchStrategy):
    @validate_args(text=non_empty_str(1, 100))
    def __init__(self, text):
        self.text = text.strip().lower()

    def matches(self, book):
        return self.text in book.author.name.lower()


class ByYearRange(SearchStrategy):
    @validate_args(start=int_range(1400, 3000), end=int_range(1400, 3000))
    def __init__(self, start, end):
        if start > end:
            raise ValidationError("Початковий рік не може бути більшим за кінцевий")
        self.start, self.end = start, end

    def matches(self, book):
        return self.start <= book.year <= self.end


class AvailableOnly(SearchStrategy):
    def matches(self, book):
        return book.available_copies > 0
