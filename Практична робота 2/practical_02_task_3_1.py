# practical_02_task_3_1.py

"""Порівняння list comprehension та generator expression."""

import sys
import timeit


def memory_comparison():
    """Порівняння використання пам'яті."""
    sizes = [1_000, 10_000, 100_000, 1_000_000]

    print("=" * 60)
    print(f"{'N':>12} | {'list (байт)':>14} | {'gen (байт)':>12} | {'Ratio':>8}")
    print("-" * 60)

    for n in sizes:
        # list comprehension зберігає всі елементи; generator expression — ні
        data_list = [x ** 2 for x in range(n)]
        data_gen = (x ** 2 for x in range(n))

        list_size = sys.getsizeof(data_list)
        gen_size = sys.getsizeof(data_gen)

        print(f"{n:>12,} | {list_size:>14,} | {gen_size:>12,} | {list_size / gen_size:>7.0f}×")

    print("=" * 60)


def performance_comparison():
    """Порівняння продуктивності: sum через list vs generator."""
    n = 500_000
    runs = 5

    # Час виконання sum() для list comprehension
    time_list = timeit.timeit(
        lambda: sum([x ** 2 for x in range(n)]),
        number=runs,
    ) / runs

    # Час виконання sum() для generator expression
    time_gen = timeit.timeit(
        lambda: sum(x ** 2 for x in range(n)),
        number=runs,
    ) / runs

    print(f"\nsum() для {n:,} елементів (середнє з {runs} запусків):")
    print(f"  list comprehension: {time_list:.4f} с")
    print(f"  generator expression: {time_gen:.4f} с")
    faster = "list" if time_list < time_gen else "generator"
    print(f"  Швидше: {faster}")


def practical_usage():
    """Практичні приклади використання generator expression."""
    words = [
        "Python", "ітератор", "генератор", "yield", "comprehension",
        "дані", "пам'ять", "ефективність", "конвеєр", "ліниві",
        "обчислення", "протокол", "об'єкт", "клас", "функція",
    ]

    # Найдовше слово: max() + generator expression
    max_len = max(len(w) for w in words)
    longest = next(w for w in words if len(w) == max_len)
    print(f"Найдовше слово: '{longest}' ({len(longest)} символів)")

    # all() + generator expression
    all_nonempty = all(len(w) > 0 for w in words)
    print(f"Всі слова непорожні: {all_nonempty}")

    # any() + generator expression
    has_long = any(len(w) > 15 for w in words)
    print(f"Є слово > 15 символів: {has_long}")

    # ",".join() + generator expression
    csv_line = ",".join(w for w in words)
    print(f"CSV: {csv_line}")

    # sum() + generator expression
    total_length = sum(len(w) for w in words)
    print(f"Сума довжин: {total_length}")

    # dict comprehension
    word_lengths = {w: len(w) for w in words}
    print(f"Довжини: {word_lengths}")

    numbers = range(1, 101)

    # sum() + generator expression з умовою if
    even_squares_sum = sum(x ** 2 for x in numbers if x % 2 == 0)
    print(f"\nСума квадратів парних від 1 до 100: {even_squares_sum}")


def print_conclusions():
    """Висновки щодо вибору підходу."""
    print("""
Висновки:
  • List comprehension доцільний, коли результат потрібен як колекція:
    багаторазовий обхід, індексація, len(), зрізи, сортування.
  • Generator expression доцільний для одноразової потокової обробки
    (sum, max, min, any, all, join), особливо для великих обсягів даних:
    використовує O(1) пам'яті незалежно від N.
  • За швидкістю на невеликих даних list часто трохи швидший, бо
    генератор має накладні витрати на призупинення/відновлення;
    перевага генератора — в економії пам'яті, а не часу.
  • Генератор одноразовий: після вичерпання його не можна пройти повторно.""")


def main():
    print(">>> Порівняння використання пам'яті <<<\n")
    memory_comparison()

    print("\n>>> Порівняння продуктивності <<<")
    performance_comparison()

    print("\n>>> Практичне використання generator expression <<<\n")
    practical_usage()

    print_conclusions()


if __name__ == "__main__":
    main()
