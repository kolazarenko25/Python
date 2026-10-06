"""Інтерактивний калькулятор на основі циклу while."""


def calculate(x: float, op: str, y: float) -> float:
    """Виконує операцію; кидає ZeroDivisionError або ValueError."""
    if op == "+":
        return x + y
    elif op == "-":
        return x - y
    elif op == "*":
        return x * y
    elif op == "/":
        return x / y
    elif op == "//":
        return x // y
    elif op == "%":
        return x % y
    elif op == "**":
        return x ** y
    else:
        raise ValueError(f"Невідомий оператор '{op}'")


def calculator():
    """Інтерактивний калькулятор з підтримкою +, -, *, /, //, %, **."""
    print("=== Калькулятор ===")
    print("Введіть вираз у форматі: число оператор число")
    print("Введіть 'quit' для виходу, 'history' для історії")

    history = []

    while True:
        user_input = input("\n> ").strip()

       
        if user_input.lower() == "quit":
            print("До побачення!")
            break

      
        if user_input.lower() == "history":
            if not history:
                print("Історія порожня")
            else:
                for i, record in enumerate(history, start=1):
                    print(f"{i}. {record}")
            continue

        
        parts = user_input.split()
        if len(parts) != 3:
            print("Некоректний формат. Приклад: 5 + 3")
            continue  

        left, op, right = parts
        try:
            x = float(left)
            y = float(right)
        except ValueError:
            print("Операнди мають бути числами")
            continue

        
        try:
            result = calculate(x, op, y)
        except ZeroDivisionError:
            print("Помилка: ділення на нуль")
            continue
        except ValueError as e:
            print(e)
            continue
        except OverflowError:
            print("Помилка: результат занадто великий")
            continue

        
        if isinstance(result, complex):
            print("Помилка: результат не є дійсним числом")
            continue

        record = f"{x:g} {op} {y:g} = {result:g}"
        history.append(record)
        print(f"Результат: {result:g}")


if __name__ == "__main__":
    calculator()
