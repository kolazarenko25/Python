"""Паттерн Factory: централізоване створення сутностей з авто-ідентифікаторами."""
import threading

from .exceptions import ValidationError
from .models import Author, Book, Reader


class EntityFactory:
    _registry = {"author": (Author, "author_id"),
                 "book": (Book, "book_id"),
                 "reader": (Reader, "reader_id")}

    def __init__(self):
        self._next = {kind: 1 for kind in self._registry}
        self._lock = threading.Lock()

    def create(self, kind, **kwargs):
        """Створює сутність, призначаючи їй наступний вільний id.
        Лічильник збільшується лише після успішної валідації."""
        cls, id_field = self._get(kind)
        with self._lock:
            entity = cls(**{id_field: self._next[kind]}, **kwargs)
            self._next[kind] += 1
            return entity

    def restore(self, kind, **kwargs):
        """Відновлює сутність із наперед відомим id (завантаження з файлу)."""
        cls, id_field = self._get(kind)
        with self._lock:
            entity = cls(**kwargs)
            self._next[kind] = max(self._next[kind], kwargs[id_field] + 1)
            return entity

    def reset(self):
        with self._lock:
            self._next = {kind: 1 for kind in self._registry}

    def _get(self, kind):
        try:
            return self._registry[kind]
        except KeyError:
            raise ValidationError(
                f"Невідомий тип сутності '{kind}'. Доступні: {', '.join(self._registry)}"
            ) from None
