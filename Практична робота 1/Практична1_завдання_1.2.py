"""Конвертор типів та форматоване виведення."""


def main():

    raw_input = input("Введіть число: ")
    print(f"Ви ввели: {raw_input!r}, тип: {type(raw_input).__name__}, "
          f"довжина рядка: {len(raw_input)}")

    try:
        as_float = float(raw_input)
        print(f"float: {as_float} -> {type(as_float).__name__}, "
              f"isinstance float: {isinstance(as_float, float)}")

        as_int = int(as_float) 
        print(f"int:   {as_int} -> {type(as_int).__name__}, "
              f"isinstance int: {isinstance(as_int, int)}")

        as_bool = bool(as_float)  
        print(f"bool:  {as_bool} -> {type(as_bool).__name__}")

        as_str = str(as_float)
        print(f"str:   {as_str!r} -> {type(as_str).__name__}")
    except ValueError:
        print("Помилка: введене значення не є числом, перетворення неможливе")

    # Ім'я та вік, форматоване повідомлення
    name = input("\nВведіть ім'я: ")
    try:
        age = int(input("Введіть вік: "))
    except ValueError:
        print("Вік має бути цілим числом, використано значення 0")
        age = 0

    print("\n--- Форматований вивід ---")
    print(f"Привіт, {name}! Вам {age} років.")
    print(f"Вирівнювання вліво:   [{name:<15}]")
    print(f"Вирівнювання вправо:  [{name:>15}]")
    print(f"По центру:            [{name:^15}]")
    print(f"З доповненням нулями: [{age:05d}]")
    print(f"Дробове, 2 знаки:     [{age / 3:.2f}]")
    print(f"Ширина 10, 3 знаки:   [{age / 7:10.3f}]")
    print(f"Двійковий вигляд:     {age:b}, шістнадцятковий: {age:x}")

    # Демонстрація id(), len(), range()
    numbers = list(range(1, 11, 2))  
    print("\n--- id(), len(), range() ---")
    print(f"Список з range(1, 11, 2): {numbers}")
    print(f"len(numbers) = {len(numbers)}")
    print(f"id(numbers)  = {id(numbers)}")
    print(f"sum = {sum(numbers)}, min = {min(numbers)}, max = {max(numbers)}")
    print(f"abs(-7) = {abs(-7)}, round(3.14159, 2) = {round(3.14159, 2)}")


if __name__ == "__main__":
    main()
