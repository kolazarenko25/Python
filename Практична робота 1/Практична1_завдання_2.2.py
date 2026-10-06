"""Визначення типу трикутника та обчислення площі."""

import math

EPS = 1e-9  


def is_valid_triangle(a: float, b: float, c: float) -> bool:
    """Перевіряє нерівність трикутника."""
    return (a > 0 and b > 0 and c > 0
            and a + b > c and a + c > b and b + c > a)


def is_right_triangle(a: float, b: float, c: float) -> bool:
    """Перевіряє прямокутність за теоремою Піфагора (з похибкою)."""
    x, y, z = sorted((a, b, c))  
    return abs(x ** 2 + y ** 2 - z ** 2) < EPS


def triangle_type(a: float, b: float, c: float) -> str:
    """Визначає тип трикутника за сторонами.

    Returns:
        Рядок з типом: 'рівносторонній', 'рівнобедрений',
        'прямокутний', 'різносторонній' або 'не є трикутником'.
    """
    if not is_valid_triangle(a, b, c):
        return "не є трикутником"

    if abs(a - b) < EPS and abs(b - c) < EPS:
        return "рівносторонній"
    elif abs(a - b) < EPS or abs(b - c) < EPS or abs(a - c) < EPS:
        return "рівнобедрений"
    else:
        if is_right_triangle(a, b, c):
            return "прямокутний"
        else:
            return "різносторонній"


def triangle_area(a: float, b: float, c: float) -> float:
    """Обчислює площу трикутника за формулою Герона."""
    p = (a + b + c) / 2
    return math.sqrt(p * (p - a) * (p - b) * (p - c))


def main():
    try:
        a = float(input("Введіть сторону a: "))
        b = float(input("Введіть сторону b: "))
        c = float(input("Введіть сторону c: "))
    except ValueError:
        print("Помилка: потрібно ввести числа")
        return

    t = triangle_type(a, b, c)
    print(f"Тип трикутника: {t}")

    if t != "не є трикутником":
        
        if t == "рівнобедрений" and is_right_triangle(a, b, c):
            print("Також є прямокутним")
        print(f"Площа (формула Герона): {triangle_area(a, b, c):.2f}")


if __name__ == "__main__":
    main()
