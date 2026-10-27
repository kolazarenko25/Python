"""Метакласи: логування створення класів/об'єктів та Singleton."""
import logging
import threading

logger = logging.getLogger("library.meta")


class LoggingMeta(type):
    """Метаклас, який логує створення класів та їхніх екземплярів
    і веде лічильник створених об'єктів для кожного класу."""

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        cls.created_count = 0
        logger.info("[META] Створено клас %s (бази: %s)",
                    name, ", ".join(b.__name__ for b in bases) or "object")
        return cls

    def __call__(cls, *args, **kwargs):
        try:
            instance = super().__call__(*args, **kwargs)
        except Exception as exc:
            logger.warning("[META] Не вдалося створити %s: %s: %s",
                           cls.__name__, type(exc).__name__, exc)
            raise
        cls.created_count += 1
        logger.info("[META] Створено об'єкт #%d класу %s: %r",
                    cls.created_count, cls.__name__, instance)
        return instance


class SingletonMeta(LoggingMeta):
    """Потокобезпечний Singleton (успадковує логування від LoggingMeta)."""

    _instances = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        if cls not in SingletonMeta._instances:
            with SingletonMeta._lock:
                if cls not in SingletonMeta._instances:  # double-checked locking
                    SingletonMeta._instances[cls] = super().__call__(*args, **kwargs)
        return SingletonMeta._instances[cls]

    def reset(cls):
        """Скидає єдиний екземпляр (потрібно для тестів)."""
        with SingletonMeta._lock:
            SingletonMeta._instances.pop(cls, None)
