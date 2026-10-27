# practical_04_task_3_1.py

"""Порівняння ThreadPoolExecutor та ProcessPoolExecutor."""

from concurrent.futures import (
    ThreadPoolExecutor,
    ProcessPoolExecutor,
    as_completed,
)
import time
import hashlib


def io_bound_task(url: str) -> dict:
    """Імітація I/O-bound задачі (завантаження сторінки)."""
    time.sleep(0.5)
    return {"url": url, "status": 200, "size": len(url) * 42}


def cpu_bound_task(n: int) -> dict:
    """CPU-bound задача: обчислення хеш-суми великого діапазону."""
    hasher = hashlib.sha256()
    for i in range(n):
        hasher.update(str(i).encode())
    return {"n": n, "hash": hasher.hexdigest()[:16]}


def risky_task(value: int) -> float:
    """Задача, що може згенерувати виключення."""
    if value == 0:
        raise ZeroDivisionError("Ділення на нуль!")
    if value < 0:
        raise ValueError(f"Від'ємне значення: {value}")
    return 1000.0 / value


def benchmark_io_bound():
    """Порівняння послідовного та ThreadPoolExecutor для I/O-bound."""
    urls = [f"https://api.example.com/data/{i}" for i in range(20)]

    # Послідовне виконання
    start = time.perf_counter()
    seq_results = [io_bound_task(url) for url in urls]
    seq_time = time.perf_counter() - start
    print(f"Послідовно ({len(urls)} задач):           {seq_time:.2f} сек")

    # ThreadPoolExecutor: executor.map зберігає порядок результатів
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=5) as executor:
        thread_results = list(executor.map(io_bound_task, urls))
    thread_time = time.perf_counter() - start
    print(f"ThreadPoolExecutor (5 потоків):     {thread_time:.2f} сек")

    print(f"Результати однакові: {seq_results == thread_results}")
    print(f"Прискорення: {seq_time / thread_time:.2f}x")


def benchmark_cpu_bound():
    """Порівняння послідовного та ProcessPoolExecutor для CPU-bound."""
    tasks = [500_000] * 8

    # Послідовне виконання
    start = time.perf_counter()
    seq_results = [cpu_bound_task(n) for n in tasks]
    seq_time = time.perf_counter() - start
    print(f"Послідовно ({len(tasks)} задач):            {seq_time:.2f} сек")

    # ProcessPoolExecutor: кожен процес має власний інтерпретатор і GIL
    start = time.perf_counter()
    with ProcessPoolExecutor(max_workers=4) as executor:
        proc_results = list(executor.map(cpu_bound_task, tasks))
    proc_time = time.perf_counter() - start
    print(f"ProcessPoolExecutor (4 процеси):    {proc_time:.2f} сек")

    print(f"Результати однакові: {seq_results == proc_results}")
    print(f"Прискорення: {seq_time / proc_time:.2f}x")

    # Для порівняння: ті самі CPU-задачі в потоках (через GIL
    # байт-код виконується по черзі, тож великого виграшу не буде)
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(cpu_bound_task, tasks))
    thread_time = time.perf_counter() - start
    print(f"\n(для порівняння) ThreadPoolExecutor (4 потоки): "
          f"{thread_time:.2f} сек")
    print(f"Прискорення потоків: {seq_time / thread_time:.2f}x")


def handle_exceptions():
    """Демонстрація обробки виключень у concurrent.futures."""
    values = [10, 5, 0, -3, 8, 2]

    ok_count = 0
    error_count = 0

    # --- Спосіб 1: submit() + as_completed() ---
    print("submit() + as_completed():")
    with ThreadPoolExecutor(max_workers=3) as executor:
        # Запам'ятовуємо, якому значенню відповідає кожен Future
        future_to_value = {
            executor.submit(risky_task, value): value for value in values
        }
        for future in as_completed(future_to_value):
            value = future_to_value[future]
            try:
                # Виключення з потоку "повторно піднімається" саме тут
                result = future.result()
            except ZeroDivisionError as exc:
                error_count += 1
                print(f"  risky_task({value:>3}) -> ZeroDivisionError: {exc}")
            except ValueError as exc:
                error_count += 1
                print(f"  risky_task({value:>3}) -> ValueError: {exc}")
            else:
                ok_count += 1
                print(f"  risky_task({value:>3}) = {result:.2f}")

    print(f"Успішно: {ok_count}, з помилками: {error_count}")

    # --- Спосіб 2: executor.map() ---
    # map піднімає виключення під час ітерації за результатами
    # і припиняє видачу наступних значень
    print("\nexecutor.map():")
    with ThreadPoolExecutor(max_workers=3) as executor:
        collected = []
        try:
            for result in executor.map(risky_task, values):
                collected.append(round(result, 2))
        except ZeroDivisionError as exc:
            print(f"  map перервано на помилці: {exc}")
        print(f"  Отримано до помилки: {collected}")


def main():
    print("=" * 60)
    print("=== I/O-bound: ThreadPoolExecutor ===")
    print("=" * 60)
    benchmark_io_bound()

    print(f"\n{'=' * 60}")
    print("=== CPU-bound: ProcessPoolExecutor ===")
    print("=" * 60)
    benchmark_cpu_bound()

    print(f"\n{'=' * 60}")
    print("=== Обробка виключень у пулах ===")
    print("=" * 60)
    handle_exceptions()


if __name__ == "__main__":
    main()
