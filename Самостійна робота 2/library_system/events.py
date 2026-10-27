"""Паттерн Observer: шина подій та спостерігачі."""
import logging
import threading
from collections import Counter
from datetime import datetime

logger = logging.getLogger("library.events")

BOOK_ADDED = "book_added"
BOOK_BORROWED = "book_borrowed"
BOOK_RETURNED = "book_returned"
READER_REGISTERED = "reader_registered"
ALL_EVENTS = "*"


class Observer:
    def update(self, event, payload):
        raise NotImplementedError


class EventBus:
    """Суб'єкт (Subject): розсилає події підписаним спостерігачам."""

    def __init__(self):
        self._subscribers = {}
        self._lock = threading.Lock()

    def subscribe(self, event, observer):
        with self._lock:
            self._subscribers.setdefault(event, []).append(observer)

    def publish(self, event, **payload):
        with self._lock:
            targets = (list(self._subscribers.get(event, []))
                       + list(self._subscribers.get(ALL_EVENTS, [])))
        for observer in targets:
            try:
                observer.update(event, payload)
            except Exception:  # збій спостерігача не повинен ламати систему
                logger.exception("Спостерігач %s завершився з помилкою", observer)


class AuditObserver(Observer):
    """Зберігає журнал усіх подій."""

    def __init__(self):
        self.records = []
        self._lock = threading.Lock()

    def update(self, event, payload):
        with self._lock:
            self.records.append((datetime.now().isoformat(timespec="milliseconds"),
                                 event, payload))


class StatisticsObserver(Observer):
    """Рахує кількість подій кожного типу."""

    def __init__(self):
        self.counter = Counter()
        self._lock = threading.Lock()

    def update(self, event, payload):
        with self._lock:
            self.counter[event] += 1
