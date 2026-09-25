
# ЗАВДАННЯ 1. TRY / EXCEPT / ELSE / FINALLY

def parse_number_basic(value: str) -> int:
    """Перетворює рядок у ціле число.

    Args:
        value: Рядок для перетворення.

    Returns:
        Ціле число.

    Raises:
        ValueError: Якщо рядок не є цілим числом.
    """
    try:
        return int(value)
    except ValueError:
        print(f"Помилка: '{value}' не є цілим числом.")
        raise


def parse_number_full(value: str) -> int:
    """Демонструє повну конструкцію try/except/else/finally.

    Args:
        value: Рядок для перетворення.

    Returns:
        Ціле число.

    Raises:
        ValueError: Якщо значення некоректне.
    """
    print("  Початок операції")
    try:
        result = int(value)
    except ValueError:
        print("  except: виникла помилка перетворення")
        raise
    else:
        print("  else: помилки немає")
        return result
    finally:
        print("  finally: цей блок виконується завжди")


def divide_numbers(value: str, divisor: str) -> float:
    """Ділить два числа та перехоплює кілька типів виключень.

    Args:
        value: Число у вигляді рядка.
        divisor: Дільник у вигляді рядка.

    Returns:
        Результат ділення.

    Raises:
        ValueError: Якщо введено не число.
        ZeroDivisionError: Якщо дільник дорівнює нулю.
    """
    try:
        return int(value) / int(divisor)
    except (ValueError, ZeroDivisionError) as exc:
        print(f"Помилка {type(exc).__name__}: {exc}")
        raise


def read_file(path: str) -> str:
    """Читає файл за допомогою контекстного менеджера with.

    Args:
        path: Шлях до файлу.

    Returns:
        Вміст файлу.

    Raises:
        FileNotFoundError: Якщо файл не існує.
    """
    with open(path, "r", encoding="utf-8") as file:
        return file.read()


# ЗАВДАННЯ 2. ВЛАСНІ ВИКЛЮЧЕННЯ

class AppError(Exception):
    """Базове виключення програми."""

    def __init__(self, message: str, code: str) -> None:
        """Створює базове виключення.

        Args:
            message: Текст помилки.
            code: Код помилки.

        Returns:
            None.
        """
        super().__init__(message)
        self.code = code

    def __str__(self) -> str:
        """Повертає текст помилки.

        Returns:
            Рядок з кодом і повідомленням.
        """
        return f"[{self.code}] {self.args[0]}"


class ValidationError(AppError):
    """Помилка перевірки даних."""

    def __init__(self, field: str, message: str) -> None:
        """Створює помилку валідації.

        Args:
            field: Назва некоректного поля.
            message: Текст помилки.

        Returns:
            None.
        """
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field

    def __str__(self) -> str:
        """Повертає опис помилки.

        Returns:
            Рядок з назвою поля та повідомленням.
        """
        return f"[{self.code}] поле '{self.field}': {self.args[0]}"


class ResourceAccessError(AppError):
    """Помилка доступу до ресурсу."""

    def __init__(self, resource_id: str, message: str) -> None:
        """Створює помилку доступу.

        Args:
            resource_id: Ідентифікатор ресурсу.
            message: Текст помилки.

        Returns:
            None.
        """
        super().__init__(message, "RESOURCE_ERROR")
        self.resource_id = resource_id

    def __str__(self) -> str:
        """Повертає опис помилки.

        Returns:
            Рядок з ресурсом і повідомленням.
        """
        return f"[{self.code}] ресурс '{self.resource_id}': {self.args[0]}"


class BusinessRuleError(AppError):
    """Помилка порушення бізнес-правила."""

    def __init__(self, rule: str, message: str) -> None:
        """Створює бізнес-помилку.

        Args:
            rule: Назва порушеного правила.
            message: Текст помилки.

        Returns:
            None.
        """
        super().__init__(message, "BUSINESS_ERROR")
        self.rule = rule

    def __str__(self) -> str:
        """Повертає опис помилки.

        Returns:
            Рядок з назвою правила та повідомленням.
        """
        return f"[{self.code}] правило '{self.rule}': {self.args[0]}"


def validate_user(name: str, age: int) -> None:
    """Перевіряє дані користувача.

    Args:
        name: Ім'я користувача.
        age: Вік користувача.

    Returns:
        None.

    Raises:
        ValidationError: Якщо дані некоректні.
    """
    if not name.strip():
        raise ValidationError("name", "ім'я не може бути порожнім")

    if age < 18:
        raise ValidationError("age", "користувач має бути повнолітнім")


def check_balance(balance: float, amount: float) -> float:
    """Перевіряє можливість списання коштів.

    Args:
        balance: Поточний баланс.
        amount: Сума списання.

    Returns:
        Баланс після списання.

    Raises:
        BusinessRuleError: Якщо сума перевищує баланс.
    """
    if amount < 0:
        raise BusinessRuleError(
            "positive_amount",
            "сума не може бути від'ємною"
        )

    if amount > balance:
        raise BusinessRuleError(
            "sufficient_balance",
            "недостатньо коштів"
        )

    return balance - amount


def load_profile(path: str) -> str:
    """Завантажує профіль та створює ланцюжок виключень.

    Args:
        path: Шлях до файлу.

    Returns:
        Вміст файлу.

    Raises:
        ResourceAccessError: Якщо файл не знайдено.
    """
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError as exc:
        raise ResourceAccessError(
            path,
            "профіль не знайдено"
        ) from exc


def operation_with_reraise(path: str) -> str:
    """Демонструє повторне піднесення виключення.

    Args:
        path: Шлях до файлу.

    Returns:
        Вміст файлу.

    Raises:
        FileNotFoundError: Якщо файл не знайдено.
    """
    try:
        with open(path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        print("Запис у журнал: файл не знайдено.")
        raise


# ЗАВДАННЯ 4. ІНТРОСПЕКЦІЯ ТА ДОКУМЕНТАЦІЯ

def show_introspection() -> None:
    """Показує приклад інтроспекції об'єкта.

    Returns:
        None.
    """
    print("\nІНТРОСПЕКЦІЯ")
    print("Ім'я функції:", validate_user.__name__)
    print("Анотації:", validate_user.__annotations__)
    print("Docstring:", validate_user.__doc__.splitlines()[0])


# ГОЛОВНА ДЕМОНСТРАЦІЯ


def main() -> None:
    """Запускає демонстрацію всіх завдань.

    Returns:
        None.
    """
    print("=" * 60)
    print("ЗАВДАННЯ 1. ОБРОБКА ВИКЛЮЧЕНЬ")
    print("=" * 60)

    print("\n1. Базовий try/except")
    print("Успішний шлях:", parse_number_basic("25"))

    try:
        parse_number_basic("abc")
    except ValueError:
        print("Помилковий шлях: ValueError перехоплено.")

    print("\n2. try/except/else/finally")
    print("Успішний шлях:")
    print("Результат:", parse_number_full("42"))

    print("Помилковий шлях:")
    try:
        parse_number_full("hello")
    except ValueError:
        print("Помилку оброблено.")

    print("\n3. Кілька типів в одному except")

    print("Успішний шлях:", divide_numbers("20", "4"))

    try:
        divide_numbers("20", "0")
    except ZeroDivisionError:
        print("Помилковий шлях: ділення на нуль.")

    try:
        divide_numbers("abc", "4")
    except ValueError:
        print("Помилковий шлях: введено не число.")

    print("\n4. Контекстний менеджер with")

    filename = "demo_file.txt"

    with open(filename, "w", encoding="utf-8") as file:
        file.write("Тестовий текст.")

    print("Успішний шлях:", read_file(filename))

    try:
        read_file("not_existing.txt")
    except FileNotFoundError:
        print("Помилковий шлях: файл не знайдено.")

    import os
    os.remove(filename)

    print("\n" + "=" * 60)
    print("ЗАВДАННЯ 2. ВЛАСНІ ВИКЛЮЧЕННЯ")
    print("=" * 60)

    print("\nІєрархія:")
    print("Exception")
    print("└── AppError")
    print("    ├── ValidationError")
    print("    ├── ResourceAccessError")
    print("    └── BusinessRuleError")

    print("\nValidationError:")
    try:
        validate_user("", 20)
    except ValidationError as exc:
        print(exc)
        print("Додатковий атрибут field:", exc.field)

    print("\nBusinessRuleError:")
    try:
        check_balance(100, 150)
    except AppError as exc:
        print("Перехоплення через базовий AppError:", exc)

        if isinstance(exc, BusinessRuleError):
            print("Додатковий атрибут rule:", exc.rule)

    print("\nResourceAccessError та raise ... from ...:")
    try:
        load_profile("missing_profile.txt")
    except ResourceAccessError as exc:
        print(exc)
        print("Оригінальна причина:", type(exc.__cause__).__name__)
        print("Текст причини:", exc.__cause__)

    print("\nПовторне піднесення raise:")
    try:
        operation_with_reraise("missing_again.txt")
    except FileNotFoundError:
        print("FileNotFoundError передано далі через raise.")

    print("\n" + "=" * 60)

    print("ЗАВДАННЯ 4. ДОКУМЕНТАЦІЯ ТА ІНТРОСПЕКЦІЯ")
    print("=" * 60)
    show_introspection()

    print("\nДля повного перегляду документації можна виконати:")
    print("help(validate_user)")


if __name__ == "__main__":
    main()