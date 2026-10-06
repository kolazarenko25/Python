# practical_03_task_3_1.py
"""Паттерни Singleton та Factory Method."""

import json
import threading
from abc import ABC, abstractmethod
from datetime import datetime


class SingletonMeta(type):
    """Метаклас для реалізації патерну Singleton."""
    _instances: dict[type, object] = {}
    _lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        # Подвійна перевірка із блокуванням — безпечно для потоків
        if cls not in SingletonMeta._instances:
            with SingletonMeta._lock:
                if cls not in SingletonMeta._instances:
                    SingletonMeta._instances[cls] = super().__call__(*args, **kwargs)
        return SingletonMeta._instances[cls]


class LogFormatter(ABC):
    """Абстрактний базовий клас форматера логів."""

    @abstractmethod
    def format(self, level: str, message: str, timestamp: datetime) -> str:
        """Форматувати повідомлення логу."""
        ...


class PlainFormatter(LogFormatter):
    """Простий текстовий формат: [РІВЕНЬ] ЧАС - Повідомлення"""

    def format(self, level, message, timestamp):
        return f"[{level}] {timestamp:%Y-%m-%d %H:%M:%S} - {message}"


class JSONFormatter(LogFormatter):
    """JSON-формат: {"level": "...", "time": "...", "message": "..."}"""

    def format(self, level, message, timestamp):
        return json.dumps(
            {"level": level, "time": timestamp.isoformat(timespec="seconds"),
             "message": message},
            ensure_ascii=False,
        )


class ColorFormatter(LogFormatter):
    """Кольоровий формат для терміналу (ANSI-коди).

    DEBUG=сірий, INFO=зелений, WARNING=жовтий, ERROR=червоний.
    """
    COLORS = {
        "DEBUG": "\033[90m",
        "INFO": "\033[92m",
        "WARNING": "\033[93m",
        "ERROR": "\033[91m",
    }
    RESET = "\033[0m"

    def format(self, level, message, timestamp):
        color = self.COLORS.get(level, "")
        return f"{color}[{level}] {timestamp:%H:%M:%S} - {message}{self.RESET}"


class FormatterFactory:
    """Фабрика форматерів із підтримкою реєстрації нових типів."""

    _formatters: dict[str, type[LogFormatter]] = {
        "plain": PlainFormatter,
        "json": JSONFormatter,
        "color": ColorFormatter,
    }

    @classmethod
    def register(cls, name: str, formatter_cls: type[LogFormatter]):
        """Зареєструвати новий тип форматера."""
        if not (isinstance(formatter_cls, type) and issubclass(formatter_cls, LogFormatter)):
            raise TypeError("Форматер має наслідувати LogFormatter")
        cls._formatters[name] = formatter_cls

    @classmethod
    def create(cls, name: str) -> LogFormatter:
        """Створити форматер за іменем. Викинути ValueError, якщо невідомий."""
        try:
            return cls._formatters[name]()
        except KeyError:
            raise ValueError(
                f"Невідомий форматер '{name}'. Доступні: {cls.available()}"
            ) from None

    @classmethod
    def available(cls) -> list[str]:
        """Повернути список доступних форматерів."""
        return list(cls._formatters)


class Logger(metaclass=SingletonMeta):
    """Логер із підтримкою рівнів та змінних форматерів."""

    LEVELS = {"DEBUG": 0, "INFO": 1, "WARNING": 2, "ERROR": 3}

    def __init__(self, formatter_name: str = "plain", min_level: str = "DEBUG"):
        self._formatter = FormatterFactory.create(formatter_name)
        self._min_level = min_level
        self._log_history: list[str] = []

    def set_formatter(self, name: str):
        self._formatter = FormatterFactory.create(name)

    def log(self, level: str, message: str):
        if level not in self.LEVELS:
            raise ValueError(f"Невідомий рівень: {level}")
        if self.LEVELS[level] < self.LEVELS[self._min_level]:
            return  # повідомлення нижче мінімального рівня
        line = self._formatter.format(level, message, datetime.now())
        print(line)
        self._log_history.append(line)

    def debug(self, msg: str):
        self.log("DEBUG", msg)

    def info(self, msg: str):
        self.log("INFO", msg)

    def warning(self, msg: str):
        self.log("WARNING", msg)

    def error(self, msg: str):
        self.log("ERROR", msg)

    def get_history(self) -> list[str]:
        return self._log_history[:]


class XmlFormatter(LogFormatter):
    """Приклад розширення фабрики без зміни її коду (Open/Closed)."""

    def format(self, level, message, timestamp):
        return f'<log level="{level}" time="{timestamp:%H:%M:%S}">{message}</log>'


def main():
    logger1 = Logger("plain", "DEBUG")
    logger2 = Logger("json", "INFO")  # аргументи ігноруються — екземпляр уже є
    print(f"Singleton: {logger1 is logger2}")

    logger1.info("Система запущена")
    logger1.warning("Мало пам'яті")
    logger1.error("Помилка з'єднання")

    print("\n-- JSON-форматер --")
    logger1.set_formatter("json")
    logger1.debug("Діагностика")

    print("\n-- Кольоровий форматер --")
    logger1.set_formatter("color")
    for lvl in Logger.LEVELS:
        logger1.log(lvl, f"Повідомлення рівня {lvl}")

    print("\n-- Реєстрація нового форматера (Open/Closed) --")
    FormatterFactory.register("xml", XmlFormatter)
    logger1.set_formatter("xml")
    logger1.info("Новий форматер працює")

    try:
        logger1.set_formatter("yaml")
    except ValueError as e:
        print(f"Очікувана помилка: {e}")

    print(f"\nФорматери: {FormatterFactory.available()}")
    print(f"Історія: {len(logger1.get_history())} записів")


if __name__ == "__main__":
    main()
