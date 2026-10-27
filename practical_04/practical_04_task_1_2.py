# practical_04_task_1_2.py

"""Паралельне обчислення з multiprocessing."""

import multiprocessing
import time
import os


def is_prime(n: int) -> bool:
    """Перевірка числа на простоту."""
    if n < 2:
        return False
    if n < 4:
        return True
    if n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i * i <= n:
        if n % i == 0 or n % (i + 2) == 0:
            return False
        i += 6
    return True


def sum_primes_in_range(start: int, end: int) -> tuple[int, int, int]:
    """Обчислює суму та кількість простих чисел у діапазоні [start, end).

    Returns:
        Кортеж (сума простих, кількість простих, PID процесу).
    """
    pid = os.getpid()
    total_sum = 0
    count = 0
    for n in range(start, end):
        if is_prime(n):
            total_sum += n
            count += 1
    return total_sum, count, pid


def print_results(title: str, ranges: list, results: list) -> None:
    """Виводить результати по кожному діапазону та загальні підсумки."""
    print(f"\n{title}")
    for (start, end), (s, c, pid) in zip(ranges, results):
        print(f"  [{start:>7}, {end:>7}): сума = {s:>13}, "
              f"простих = {c:>6}, PID = {pid}")
    print(f"  Разом: сума = {sum(r[0] for r in results)}, "
          f"простих = {sum(r[1] for r in results)}")


def main():
    total_range = 1_000_000
    num_workers = 4

    print(f"Головний процес PID = {os.getpid()}")

    # Розбиваємо діапазон [2, total_range) на num_workers частин
    chunk_size = total_range // num_workers
    ranges = []
    for i in range(num_workers):
        start = i * chunk_size if i > 0 else 2
        # Останній діапазон доходить до кінця, навіть якщо ділення не націло
        end = total_range if i == num_workers - 1 else (i + 1) * chunk_size
        ranges.append((start, end))

    # === Послідовне виконання ===
    start_time = time.perf_counter()
    seq_results = [sum_primes_in_range(s, e) for s, e in ranges]
    seq_time = time.perf_counter() - start_time

    # === Паралельне виконання з multiprocessing.Pool ===
    start_time = time.perf_counter()
    with multiprocessing.Pool(processes=num_workers) as pool:
        # starmap розпаковує кортежі (start, end) в аргументи функції
        par_results = pool.starmap(sum_primes_in_range, ranges)
    par_time = time.perf_counter() - start_time

    print_results("Послідовне виконання (усе в головному процесі):",
                  ranges, seq_results)
    print_results("Паралельне виконання (multiprocessing.Pool):",
                  ranges, par_results)

    # Перевірка коректності: обидва способи мають дати однаковий результат
    same = ([r[:2] for r in seq_results] == [r[:2] for r in par_results])
    print(f"\nРезультати послідовного та паралельного обчислення збігаються: "
          f"{same}")

    unique_pids = {r[2] for r in par_results}
    print(f"Унікальних PID робочих процесів: {len(unique_pids)} "
          f"{sorted(unique_pids)}")

    print(f"\nПослідовно: {seq_time:.3f} сек")
    print(f"Паралельно ({num_workers} процеси): {par_time:.3f} сек")
    print(f"Прискорення: {seq_time / par_time:.2f}x")


if __name__ == "__main__":
    main()
