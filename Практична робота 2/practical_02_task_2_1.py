# practical_02_task_2_1.py

"""Функції-генератори для числових послідовностей."""

import itertools


def arithmetic_progression(start: float, step: float):
    """Нескінченний генератор арифметичної прогресії.

    Yields:
        start, start+step, start+2*step, ...
    """
    value = start
    while True:
        yield value
        value += step


def geometric_progression(start: float, ratio: float, limit: float = float("inf")):
    """Генератор геометричної прогресії до заданої межі.

    Yields:
        start, start*ratio, start*ratio², ... (поки значення <= limit)
    """
    value = start
    while value <= limit:
        yield value
        value *= ratio


def fibonacci(n: int | None = None):
    """Генератор чисел Фібоначчі.

    Args:
        n: кількість чисел (None — нескінченна послідовність).
    """
    a, b = 0, 1
    if n is None:
        # Нескінченний режим
        while True:
            yield a
            a, b = b, a + b
    else:
        # Скінченний режим: рівно n чисел
        for _ in range(n):
            yield a
            a, b = b, a + b


def collatz_sequence(n: int):
    """Генератор послідовності Коллатца (3n+1 задача).

    Правила:
        - Якщо n парне: n = n // 2
        - Якщо n непарне: n = 3*n + 1
        - Завершити при n == 1

    Yields:
        Кожне число послідовності, починаючи з n і закінчуючи 1.
    """
    while n != 1:
        yield n
        n = n // 2 if n % 2 == 0 else 3 * n + 1
    yield 1


def flatten(nested):
    """Рекурсивний генератор для розгортання вкладених списків.

    Використовує yield from для делегування підгенераторам.
    """
    for item in nested:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item


def main():
    # Арифметична прогресія: перші 10 елементів
    ap = arithmetic_progression(2, 3)
    first_10 = list(itertools.islice(ap, 10))
    print(f"Арифметична прогресія (2, 3): {first_10}")
    # Очікувано: [2, 5, 8, 11, 14, 17, 20, 23, 26, 29]

    # Геометрична прогресія до 1000
    gp = list(geometric_progression(1, 2, limit=1000))
    print(f"Геометрична прогресія (1, 2): {gp}")
    # Очікувано: [1, 2, 4, 8, 16, 32, 64, 128, 256, 512]

    # Фібоначчі: перші 15 чисел
    fib_15 = list(fibonacci(15))
    print(f"Фібоначчі (15): {fib_15}")

    # Послідовність Коллатца
    coll = list(collatz_sequence(27))
    print(f"Коллатц (27): довжина={len(coll)}, макс={max(coll)}")

    # Розгортання вкладених списків
    nested = [1, [2, 3], [4, [5, 6]], 7, [8, [9, [10]]]]
    flat = list(flatten(nested))
    print(f"Розгортання: {flat}")
    # Очікувано: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # Перше число Фібоначчі > 10000 (нескінченний генератор + break)
    for fib_num in fibonacci(None):
        if fib_num > 10000:
            print(f"Перше число Фібоначчі > 10000: {fib_num}")
            break


if __name__ == "__main__":
    main()
