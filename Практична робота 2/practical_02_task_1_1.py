# practical_02_task_1_1.py

"""Реалізація власного ітератора CyclicRange."""


class CyclicRange:
    """Ітератор, що циклічно генерує числа у заданому діапазоні.

    Args:
        start: початок діапазону (включно).
        stop: кінець діапазону (не включно).
        step: крок ітерації (за замовчуванням 1).
        repeats: кількість повних циклів (за замовчуванням 1).
    """

    def __init__(self, start: int, stop: int, step: int = 1, repeats: int = 1):
        if step <= 0:
            raise ValueError("step має бути додатним числом")
        self._start = start
        self._stop = stop
        self._step = step
        self._repeats = repeats
        # Внутрішній стан: поточна позиція та кількість завершених циклів
        self._current = start
        self._cycle = 0

    def __iter__(self):
        # Ітератор повертає самого себе
        return self

    def __next__(self) -> int:
        # 1. Усі цикли завершені (або діапазон порожній) — зупинка
        if self._cycle >= self._repeats or self._start >= self._stop:
            raise StopIteration

        # 2. Зберігаємо поточне значення
        value = self._current

        # 3. Зсуваємо позицію на крок
        self._current += self._step

        # 4. Якщо досягли кінця діапазону — починаємо новий цикл
        if self._current >= self._stop:
            self._current = self._start
            self._cycle += 1

        # 5. Повертаємо збережене значення
        return value


def main():
    # Базове використання
    print("CyclicRange(1, 4, repeats=3):")
    for num in CyclicRange(1, 4, repeats=3):
        print(num, end=" ")
    # Очікуваний результат: 1 2 3 1 2 3 1 2 3
    print()

    # З кроком
    print("\nCyclicRange(0, 10, step=3, repeats=2):")
    for num in CyclicRange(0, 10, step=3, repeats=2):
        print(num, end=" ")
    # Очікуваний результат: 0 3 6 9 0 3 6 9
    print()

    # Перетворення на список
    result = list(CyclicRange(5, 8, repeats=2))
    print(f"\nЯк список: {result}")
    # Очікуваний результат: [5, 6, 7, 5, 6, 7]

    # Обчислення суми елементів через sum()
    total = sum(CyclicRange(1, 5, repeats=2))
    print(f"Сума CyclicRange(1, 5, repeats=2): {total}")  # 20


if __name__ == "__main__":
    main()
