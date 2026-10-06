"""Обчислення математичних виразів."""

import math


def read_number(prompt: str) -> float:
    """Зчитує число від користувача, повторюючи запит при помилці."""
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Помилка: введіть число (наприклад, 3 або 2.5)")


def main():
    a = read_number("Введіть a: ")
    b = read_number("Введіть b: ")
    c = read_number("Введіть c: ")

    # 1. Сума квадратів: a² + b² + c²
    sum_squares = a ** 2 + b ** 2 + c ** 2

    # 2. Середнє арифметичне
    average = (a + b + c) / 3

    # 3. Дискримінант квадратного рівняння ax² + bx + c = 0
    discriminant = b ** 2 - 4 * a * c

    # 4. Гіпотенуза прямокутного трикутника з катетами a, b
    hypotenuse = math.sqrt(a ** 2 + b ** 2)

    # 5. Нерівність трикутника (всі сторони додатні, сума двох > третьої)
    is_triangle = (
        a > 0 and b > 0 and c > 0
        and a + b > c and a + c > b and b + c > a
    )

    print(f"\nСума квадратів:      {sum_squares:.2f}")
    print(f"Середнє арифметичне: {average:.2f}")
    print(f"Дискримінант:        {discriminant:.2f}")
    print(f"Гіпотенуза (a, b):   {hypotenuse:.2f}")
    print(f"Утворюють трикутник: {'так' if is_triangle else 'ні'}")

    if a == 0:
        print("Рівняння не квадратне (a = 0)")
    elif discriminant > 0:
        x1 = (-b + math.sqrt(discriminant)) / (2 * a)
        x2 = (-b - math.sqrt(discriminant)) / (2 * a)
        print(f"Корені рівняння:     x1 = {x1:.2f}, x2 = {x2:.2f}")
    elif discriminant == 0:
        print(f"Корінь рівняння:     x = {-b / (2 * a):.2f}")
    else:
        print("Дійсних коренів немає")

    if b != 0:
        print(f"a // b = {a // b:.2f}, a % b = {a % b:.2f}")
    else:
        print("a // b та a % b: ділення на нуль неможливе")


if __name__ == "__main__":
    main()
