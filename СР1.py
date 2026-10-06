import math

# 1. Математичні задачі: умовні конструкції та цикли

def factorial(n: int) -> int:
    """Факторіал числа n обчислюється циклом for."""
    if n < 0:
        raise ValueError("Факторіал визначений лише для n >= 0")
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def is_prime(n: int) -> bool:
    """Перевірка числа на простоту перебором дільників до sqrt(n)."""
    if n < 2:
        return False
    d = 2
    while d * d <= n:          
        if n % d == 0:
            return False
        d += 1
    return True


def read_number(prompt: str, as_type=float, positive=False):
    """Безпечне введення числа з перевіркою (цикл + try/except)."""
    while True:
        try:
            value = as_type(input(prompt))
            if positive and value <= 0:
                print("  Значення має бути додатним.")
                continue
            return value
        except ValueError:
            print("  Некоректне введення, спробуйте ще раз.")


def task_factorial():
    print("\n--- Факторіал та перевірка на простоту ---")
    n = read_number("Введіть ціле n >= 0: ", int)
    if n < 0:
        print("Факторіал від'ємного числа не існує.")
        return
    print(f"{n}! = {factorial(n)}")
    print(f"Число {n} {'просте' if is_prime(n) else 'не є простим'}")

def circle(r):
    return math.pi * r ** 2, 2 * math.pi * r


def rectangle(a, b):
    return a * b, 2 * (a + b)


def triangle(a, b, c):
    """Трикутник за трьома сторонами (формула Герона)."""
    if a + b <= c or a + c <= b or b + c <= a:
        raise ValueError("Такого трикутника не існує")
    p = (a + b + c) / 2
    return math.sqrt(p * (p - a) * (p - b) * (p - c)), a + b + c


FIGURES = {
    "1": ("Коло", circle, ["радіус"]),
    "2": ("Прямокутник", rectangle, ["сторона a", "сторона b"]),
    "3": ("Трикутник", triangle, ["сторона a", "сторона b", "сторона c"]),
}


def task_geometry():
    print("\n--- Геометричні фігури ---")
    for key, (name, _, _) in FIGURES.items():
        print(f"{key}. {name}")
    choice = input("Оберіть фігуру: ").strip()
    if choice not in FIGURES:
        print("Невідомий вибір.")
        return
    name, func, params = FIGURES[choice]
    values = [read_number(f"  {p}: ", float, positive=True) for p in params]
    try:
        area, perimeter = func(*values)
        print(f"{name}: площа = {area:.2f}, периметр = {perimeter:.2f}")
    except ValueError as err:
        print("Помилка:", err)

# 2. Типи та структури даних

def task_data_structures():
    print("\n--- Типи та структури даних ---")
    # Базові типи
    i, f, s, b = 42, 3.14, "Python", True
    print("Типи:", type(i).__name__, type(f).__name__,
          type(s).__name__, type(b).__name__)

    
    marks = [85, 92, 70, 100, 64]
    marks.append(88)
    marks.sort(reverse=True)
    print("Список оцінок:", marks)
    print(f"Середнє = {sum(marks) / len(marks):.1f}, "
          f"max = {max(marks)}, min = {min(marks)}")
    print("Зріз перших трьох:", marks[:3])

    point = (3, 4)
    x, y = point                     
    print(f"Кортеж {point}: відстань до початку координат = "
          f"{math.hypot(x, y)}")

    students = {"Іваненко": 90, "Петренко": 75, "Сидоренко": 82}
    students["Коваленко"] = 95
    for name, mark in students.items():
        grade = "відмінно" if mark >= 90 else "добре" if mark >= 75 else "задовільно"
        print(f"  {name:<10} {mark:>3}  {grade}")
    best = max(students, key=students.get)
    print("Найкращий результат:", best)

    a, b_set = {1, 2, 3, 4}, {3, 4, 5}
    print("Об'єднання:", a | b_set, "| Перетин:", a & b_set,
          "| Різниця:", a - b_set)

    # Генератор списку та словника
    squares = {n: n ** 2 for n in range(1, 6)}
    print("Квадрати:", squares)


# 3. Ітератори

class Countdown:
    """Власний ітератор: зворотний відлік від start до 1."""

    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current -= 1
        return value


class Group:
    """Колекція студентів із власним ітератором (лише тих, хто склав)."""

    def __init__(self, data: dict, passing=60):
        self.data = data
        self.passing = passing

    def __iter__(self):
        return GroupIterator(self)


class GroupIterator:
    def __init__(self, group):
        self._items = iter(group.data.items())
        self._passing = group.passing

    def __iter__(self):
        return self

    def __next__(self):
        for name, mark in self._items:   
            if mark >= self._passing:
                return name, mark
        raise StopIteration


def task_iterators():
    print("\n--- Ітератори ---")

    it = iter(["a", "b", "c"])
    print("next():", next(it), next(it), next(it))
    try:
        next(it)
    except StopIteration:
        print("Ітератор вичерпано (StopIteration)")

    print("Countdown(5):", list(Countdown(5)))

    group = Group({"Іваненко": 90, "Петренко": 55, "Сидоренко": 82,
                   "Коваленко": 40})
    print("Студенти, що склали:")
    for name, mark in group:
        print(f"  {name}: {mark}")


# 4. Генератори

def fibonacci(limit):
    """Генератор чисел Фібоначчі, що не перевищують limit."""
    a, b = 0, 1
    while a <= limit:
        yield a
        a, b = b, a + b


def primes(count):
    """Генератор перших count простих чисел."""
    found, n = 0, 2
    while found < count:
        if is_prime(n):
            yield n
            found += 1
        n += 1


def chain(*collections):
    """Об'єднує колекції в один потік (yield from)."""
    for c in collections:
        yield from c


def task_generators():
    print("\n--- Генератори ---")
    print("Фібоначчі до 100:", list(fibonacci(100)))
    print("10 простих чисел:", list(primes(10)))
    print("chain:", list(chain([1, 2], (3, 4), "ab")))

    total = sum(x * x for x in range(1, 1_000_001))
    print("Сума квадратів 1..1 000 000 =", total)

    # Ручне керування генератором
    gen = fibonacci(10)
    print("next(gen):", next(gen), next(gen), next(gen))



# Головне меню

def main():
    actions = {
        "1": ("Факторіал та прості числа", task_factorial),
        "2": ("Геометричні фігури", task_geometry),
        "3": ("Типи та структури даних", task_data_structures),
        "4": ("Ітератори", task_iterators),
        "5": ("Генератори", task_generators),
    }
    while True:
        print("\n===== МЕНЮ =====")
        for key, (title, _) in actions.items():
            print(f"{key}. {title}")
        print("0. Вихід")
        choice = input("Ваш вибір: ").strip()
        if choice == "0":
            print("До побачення!")
            break
        if choice in actions:
            actions[choice][1]()
        else:
            print("Невірний пункт меню.")


if __name__ == "__main__":
    main()