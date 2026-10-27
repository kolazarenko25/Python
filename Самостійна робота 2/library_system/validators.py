"""Фабрики перевірок для декоратора validate_args.
Кожна перевірка має сигнатуру check(name, value) і кидає ValidationError."""
import re
from datetime import date

from .exceptions import ValidationError


def non_empty_str(min_len=1, max_len=200):
    def check(name, value):
        if not isinstance(value, str):
            raise ValidationError(
                f"Поле '{name}' має бути рядком, отримано {type(value).__name__}")
        if not (min_len <= len(value.strip()) <= max_len):
            raise ValidationError(
                f"Поле '{name}' має містити від {min_len} до {max_len} символів")
    return check


def int_range(min_value, max_value):
    def check(name, value):
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValidationError(
                f"Поле '{name}' має бути цілим числом, отримано {type(value).__name__}")
        if not (min_value <= value <= max_value):
            raise ValidationError(
                f"Поле '{name}' має бути в межах {min_value}..{max_value}, отримано {value}")
    return check


def positive_int():
    return int_range(1, 10 ** 9)


def current_year():
    return date.today().year


def email_format():
    pattern = re.compile(r"^[\w.+-]+@[\w-]+(\.[\w-]+)+$")

    def check(name, value):
        if not isinstance(value, str) or not pattern.match(value.strip()):
            raise ValidationError(f"Поле '{name}' має містити коректну e-mail адресу")
    return check


def _isbn13_check_digit(body12):
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(body12))
    return (10 - total % 10) % 10


def isbn13_with_check(body12):
    """Допоміжна функція: додає контрольну цифру до 12 цифр ISBN."""
    return body12 + str(_isbn13_check_digit(body12))


def normalize_isbn(value):
    return value.replace("-", "").replace(" ", "")


def isbn13():
    def check(name, value):
        if not isinstance(value, str):
            raise ValidationError(f"Поле '{name}' має бути рядком")
        digits = normalize_isbn(value)
        if len(digits) != 13 or not digits.isdigit():
            raise ValidationError(f"Поле '{name}': ISBN-13 має містити 13 цифр")
        if _isbn13_check_digit(digits[:12]) != int(digits[12]):
            raise ValidationError(f"Поле '{name}': неправильна контрольна цифра ISBN")
    return check


def instance_of(expected_type):
    def check(name, value):
        if not isinstance(value, expected_type):
            raise ValidationError(
                f"Поле '{name}' має бути типу {expected_type.__name__}, "
                f"отримано {type(value).__name__}")
    return check
