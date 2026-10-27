"""Декоратори: валідація аргументів, логування викликів, синхронізація."""
import functools
import inspect
import logging
import time
import threading

logger = logging.getLogger("library.calls")


def validate_args(**rules):
    """Перевіряє аргументи функції перед викликом.

    @validate_args(name=non_empty_str(2, 50), year=int_range(1400, 2026))
    def __init__(self, name, year): ...
    """
    def decorator(func):
        signature = inspect.signature(func)

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            bound = signature.bind(*args, **kwargs)
            bound.apply_defaults()
            for param, check in rules.items():
                if param in bound.arguments:
                    check(param, bound.arguments[param])
            return func(*bound.args, **bound.kwargs)
        return wrapper
    return decorator


def log_call(func):
    """Логує виклик методу, час виконання, потік та можливі помилки."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        thread = threading.current_thread().name
        try:
            result = func(*args, **kwargs)
        except Exception as exc:
            logger.warning("[CALL] %s -> %s: %s [%s]",
                           func.__qualname__, type(exc).__name__, exc, thread)
            raise
        logger.debug("[CALL] %s виконано за %.6f с [%s]",
                     func.__qualname__, time.perf_counter() - start, thread)
        return result
    return wrapper


def synchronized(lock_attr="_lock"):
    """Виконує метод під блокуванням self.<lock_attr> (потокобезпека)."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            with getattr(self, lock_attr):
                return func(self, *args, **kwargs)
        return wrapper
    return decorator
