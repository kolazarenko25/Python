# practical_03_task_2_2.py
"""Декоратори класів."""

import functools
import inspect
import time


def auto_repr(cls):
    """Декоратор класу: додає __repr__ на основі __init__ параметрів."""
    # inspect.signature слідує за __wrapped__, тому декоратор коректно
    # комбінується з іншими (на відміну від __init__.__code__.co_varnames,
    # який після @frozen показував би лише *args, **kwargs).
    params = [p for p in inspect.signature(cls.__init__).parameters if p != "self"]

    def __repr__(self):
        args = ", ".join(f"{p}={getattr(self, p, None)!r}" for p in params)
        return f"{cls.__name__}({args})"

    cls.__repr__ = __repr__
    return cls


def frozen(cls):
    """Декоратор класу: забороняє зміну атрибутів після __init__.

    Після ініціалізації будь-яка спроба змінити атрибут
    викликає AttributeError.
    """
    original_init = cls.__init__

    @functools.wraps(original_init)
    def __init__(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        object.__setattr__(self, "_frozen", True)  # обходимо власний __setattr__

    def __setattr__(self, name, value):
        if getattr(self, "_frozen", False):
            raise AttributeError(
                f"Неможливо змінити '{name}': екземпляр {type(self).__name__} заморожений"
            )
        object.__setattr__(self, name, value)

    cls.__init__ = __init__
    cls.__setattr__ = __setattr__
    return cls


def log_methods(cls):
    """Декоратор класу: логує виклики всіх публічних методів."""
    def make_wrapper(method):
        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            shown = args[1:]  # без self
            print(f"[LOG] {cls.__name__}.{method.__name__}{shown} {kwargs or ''}".rstrip())
            start = time.perf_counter()
            try:
                result = method(*args, **kwargs)
            except Exception as e:
                print(f"[LOG] {method.__name__} → виняток {type(e).__name__}: {e}")
                raise
            print(f"[LOG] {method.__name__} → {result} "
                  f"({time.perf_counter() - start:.6f}с)")
            return result
        return wrapper

    for name, attr in list(vars(cls).items()):
        # Лише звичайні функції (не staticmethod/classmethod) без префікса '_'
        if not name.startswith("_") and inspect.isfunction(attr):
            setattr(cls, name, make_wrapper(attr))
    return cls


@auto_repr
class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance_to(self, other: "Point") -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5


@frozen
class ImmutableConfig:
    def __init__(self, host: str, port: int, debug: bool = False):
        self.host = host
        self.port = port
        self.debug = debug


@log_methods
class MathService:
    def add(self, a: float, b: float) -> float:
        return a + b

    def multiply(self, a: float, b: float) -> float:
        return a * b

    def divide(self, a: float, b: float) -> float:
        if b == 0:
            raise ValueError("Ділення на нуль")
        return a / b


# Комбінування декораторів
@auto_repr
@frozen
class Settings:
    def __init__(self, name: str, level: int = 1):
        self.name = name
        self.level = level


def main():
    print("== @auto_repr ==")
    p = Point(3.0, 4.0)
    print(repr(p))
    print(f"Відстань до початку координат: {p.distance_to(Point(0, 0))}")

    print("\n== @frozen ==")
    cfg = ImmutableConfig("localhost", 8080, debug=True)
    print(f"Config: {cfg.host}:{cfg.port}")
    try:
        cfg.host = "remote"
    except AttributeError as e:
        print(f"Очікувана помилка: {e}")

    print("\n== @log_methods ==")
    svc = MathService()
    svc.add(10, 20)
    svc.multiply(3, 7)
    try:
        svc.divide(10, 0)
    except ValueError:
        pass

    print("\n== Комбінація @auto_repr + @frozen ==")
    s = Settings("prod", level=3)
    print(repr(s))
    try:
        s.level = 5
    except AttributeError as e:
        print(f"Очікувана помилка: {e}")


if __name__ == "__main__":
    main()
