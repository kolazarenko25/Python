"""Паттерн Repository: уніфіковане сховище сутностей у пам'яті."""
from .exceptions import DuplicateError, NotFoundError


class Repository:
    def __init__(self, entity_name):
        self.entity_name = entity_name
        self._items = {}

    def add(self, entity):
        if entity.id in self._items:
            raise DuplicateError(f"{self.entity_name} з id={entity.id} уже існує")
        self._items[entity.id] = entity
        return entity

    def get(self, entity_id):
        try:
            return self._items[entity_id]
        except KeyError:
            raise NotFoundError(f"{self.entity_name} з id={entity_id} не знайдено") from None

    def all(self):
        return list(self._items.values())

    def find(self, predicate):
        return [item for item in self._items.values() if predicate(item)]

    def clear(self):
        self._items.clear()

    def __len__(self):
        return len(self._items)
