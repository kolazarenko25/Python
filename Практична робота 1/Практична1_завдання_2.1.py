"""Класифікація оцінок за шкалою ЄКТС."""


def classify_grade(score: int) -> str:
    """Повертає літерну оцінку ЄКТС за числовим балом.

    Args:
        score: числовий бал від 0 до 100.

    Returns:
        Літерна оцінка (A, B, C, D, E, FX, F).
    """
    if score >= 90:
        return "A"
    elif score >= 82:
        return "B"
    elif score >= 74:
        return "C"
    elif score >= 64:
        return "D"
    elif score >= 60:
        return "E"
    elif score >= 35:
        return "FX"
    else:
        return "F"


def main():
    raw = input("Введіть оцінку (0-100): ")

    try:
        score = int(raw)
    except ValueError:
        print("Помилка: потрібно ввести ціле число")
        return

    if score < 0 or score > 100:
        print("Помилка: оцінка має бути від 0 до 100")
    else:
        grade = classify_grade(score)
        print(f"Оцінка {score} → ЄКТС: {grade}")
        passed = grade not in ("FX", "F")
        print(f"Результат: {'Зараховано' if passed else 'Не зараховано'}")


if __name__ == "__main__":
    main()
