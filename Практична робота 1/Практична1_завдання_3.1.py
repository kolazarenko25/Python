"""Використання циклу for для обчислень."""


def factorial(n: int) -> int:
    """Обчислює факторіал числа n."""
    if n < 0:
        raise ValueError("Факторіал визначений лише для n >= 0")
    result = 1
    for i in range(2, n + 1):  
        result *= i
    return result


def harmonic_sum(n: int) -> float:
    """Обчислює суму гармонічного ряду: 1 + 1/2 + 1/3 + ... + 1/n."""
    total = 0.0
    for i in range(1, n + 1):
        total += 1 / i
    return total


def multiplication_table(n: int) -> None:
    """Виводить таблицю множення n × n."""
    width = len(str(n * n)) + 1  
    for i in range(1, n + 1): 
        row = ""
        for j in range(1, n + 1):  
            row += f"{i * j:>{width}}"
        print(row)


def main():
    try:
        n = int(input("Введіть число n: "))
    except ValueError:
        print("Помилка: потрібно ціле число")
        return
    if n < 1:
        print("Помилка: n має бути додатним")
        return

    print(f"{n}! = {factorial(n)}")
    print(f"Гармонічна сума H({n}) = {harmonic_sum(n):.6f}")
    print(f"\nТаблиця множення {n}×{n}:")
    multiplication_table(n)

    # Демонстрація range() з параметром step
    print(f"\nПарні числа від 2 до {n}: {list(range(2, n + 1, 2))}")
    print(f"Числа від {n} до 1 у зворотному порядку: {list(range(n, 0, -1))}")


if __name__ == "__main__":
    main()
