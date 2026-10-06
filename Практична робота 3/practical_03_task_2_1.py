# practical_03_task_2_1.py
"""Декоратори функцій з параметрами."""

import functools
import time


def cache(max_size: int = 128, verbose: bool = True):
    """Декоратор кешування результатів функції (спрощений LRU-кеш).

    Args:
        max_size: максимальна кількість закешованих результатів.
        verbose: виводити "cache hit"/"cache miss" при кожному виклику.
    """
    def decorator(func):
        _cache = {}
        _call_order = []  # від найстарішого використання до найновішого
        stats = {"hits": 0, "misses": 0}

        @functools.wraps(func)
        def wrapper(*args):
            if args in _cache:
                stats["hits"] += 1
                _call_order.remove(args)
                _call_order.append(args)  # оновлюємо "свіжість" запису
                if verbose:
                    print(f"  cache hit: {func.__name__}{args}")
                return _cache[args]

            stats["misses"] += 1
            if verbose:
                print(f"  cache miss: {func.__name__}{args}")
            result = func(*args)
            _cache[args] = result
            _call_order.append(args)
            if len(_cache) > max_size:
                oldest = _call_order.pop(0)
                del _cache[oldest]
            return result

        wrapper.cache_info = lambda: {
            "size": len(_cache), "max_size": max_size, **stats
        }
        wrapper.cache_clear = lambda: (
            _cache.clear(), _call_order.clear(), stats.update(hits=0, misses=0)
        )
        return wrapper
    return decorator


def rate_limit(max_calls: int, period: float = 60.0):
    """Декоратор обмеження частоти викликів функції.

    Args:
        max_calls: максимальна кількість викликів за період.
        period: тривалість періоду в секундах.
    """
    def decorator(func):
        call_times = []

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = time.monotonic()
            # Видаляємо записи, старші за period
            call_times[:] = [t for t in call_times if now - t < period]
            if len(call_times) >= max_calls:
                raise RuntimeError(
                    f"Перевищено ліміт: {max_calls} викликів за {period} с "
                    f"для {func.__name__}"
                )
            call_times.append(now)
            return func(*args, **kwargs)

        return wrapper
    return decorator


def log(level: str = "INFO"):
    """Декоратор логування виклику функції з зазначенням рівня.

    Args:
        level: рівень логування (DEBUG, INFO, WARNING, ERROR).
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            parts = [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
            print(f"[{level}] Виклик {func.__name__}({', '.join(parts)})")
            start = time.perf_counter()
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                elapsed = time.perf_counter() - start
                print(f"[ERROR] {func.__name__} → {type(e).__name__}: {e} "
                      f"(час: {elapsed:.4f}с)")
                raise
            elapsed = time.perf_counter() - start
            print(f"[{level}] {func.__name__} → {result} (час: {elapsed:.4f}с)")
            return result

        return wrapper
    return decorator


@cache(max_size=64, verbose=False)  # verbose=False, щоб не друкувати ~60 рядків
def fibonacci(n: int) -> int:
    """Обчислює n-е число Фібоначчі рекурсивно."""
    if n < 2:
        return n
    return fibonacci(n - 1) + fibonacci(n - 2)


@cache(max_size=2)  # малий кеш для демонстрації hit/miss та витіснення
def square(n: int) -> int:
    return n * n


@rate_limit(max_calls=5, period=10.0)
def send_notification(message: str) -> str:
    """Імітує відправку сповіщення."""
    return f"Надіслано: {message}"


@log(level="DEBUG")
def divide(a: float, b: float) -> float:
    """Ділення з можливим ZeroDivisionError."""
    return a / b


def main():
    print("== cache ==")
    print(f"fibonacci(30) = {fibonacci(30)}")
    print(f"cache_info: {fibonacci.cache_info()}")
    print("Демонстрація hit/miss та LRU-витіснення (max_size=2):")
    square(2); square(3); square(2); square(4); square(3)
    print(f"cache_info: {square.cache_info()}")
    print(f"Метадані збережено: {fibonacci.__name__!r}, {fibonacci.__doc__!r}")

    print("\n== rate_limit ==")
    for i in range(1, 7):
        try:
            print(f"  {i}: {send_notification(f'повідомлення {i}')}")
        except RuntimeError as e:
            print(f"  {i}: RuntimeError: {e}")

    print("\n== log ==")
    divide(10, 3)
    try:
        divide(10, 0)
    except ZeroDivisionError:
        print("Помилку оброблено у main()")


if __name__ == "__main__":
    main()
