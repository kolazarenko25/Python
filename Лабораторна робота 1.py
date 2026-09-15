import timeit

print("=== ЗАВДАННЯ 1: Списки ===")

numbers = [10, 20, 30, 40, 50, 60, 70, 80]
print(f"Початковий список: {numbers}")

print(f"Перший елемент [0]: {numbers[0]}")
print(f"Останній елемент [-1]: {numbers[-1]}")

print(f"Зріз 1 [1:4]: {numbers[1:4]}")
print(f"Зріз 2 [:5]: {numbers[:5]}")
print(f"Зріз 3 [0:8:2] (з кроком 2): {numbers[0:8:2]}")

numbers.append(90)
print(f"Після append(90): {numbers} | Довжина: {len(numbers)} (очікувано: 9)")

del numbers[2]
print(f"Після del numbers[2]: {numbers} | Довжина: {len(numbers)} (очікувано: 8)")



print("\n=== ЗАВДАННЯ 2: Кортежі ===")

products = [
    (101, "Ноутбук", 2, 25000.0),
    (102, "Мишка", 5, 600.0),
    (103, "Клавіатура", 3, 1200.0)
]

def print_product(product_tuple):
    prod_id, name, qty, price = product_tuple
    print(f"ID: {prod_id:<3} | Товар: {name:<10} | К-сть: {qty:<2} | Ціна: {price:.2f} грн")

def calculate_total(product_list):
    total = sum(item[2] * item[3] for item in product_list)
    return round(total, 2)

print("Перелік товарів:")
for p in products:
    print_product(p)

total_cost = calculate_total(products)
print(f"Загальна вартість товарів: {total_cost:.2f} грн")

try:
    products[0][1] = "Планшет"
except TypeError as error:
    print(f"Спроба зміни кортежу викликала помилку: {error}")

student = ("Лазаренко К", [5, 4, 5])
print(f"До зміни вкладеного списку: {student}")
student[1].append(5)
print(f"Після зміни вкладеного списку: {student}")



print("\n=== ЗАВДАННЯ 3: Словники ===")

raw_text = "Яблуко груша яблуко БАНАН груша яблуко"
words = raw_text.lower().split()

frequency = {}
for word in words:
    frequency[word] = frequency.get(word, 0) + 1

sorted_freq = sorted(frequency.items(), key=lambda x: x[1], reverse=True)

print("Частота слів (відсортовано за спаданням):")
for word, count in sorted_freq:
    print(f"  {word:<10}: {count}")

frequent_words = {k: v for k, v in frequency.items() if v > 1}
print(f"Похідний словник (слова з частотою > 1): {frequent_words}")



print("\n=== ЗАВДАННЯ 4: Множини ===")

list_a = ["101", "102", "103", "101", "104"]
list_b = ["103", "104", "105", "106"]

set_a = set(list_a)
set_b = set(list_b)

print(f"Множина A (унікальні): {sorted(list(set_a))}")
print(f"Множина B (унікальні): {sorted(list(set_b))}")
print(f"Перетин (A & B): {sorted(list(set_a & set_b))}")
print(f"Об'єднання (A | B): {sorted(list(set_a | set_b))}")
print(f"Симетрична різниця (A ^ B): {sorted(list(set_a ^ set_b))}")

subset_test = {"101", "102"}
print(f"Чи є {{'101', '102'}} підмножиною A?: {subset_test.issubset(set_a)}")
print(f"Чи є B підмножиною A?: {set_b.issubset(set_a)}")



print("\n=== ЗАВДАННЯ 5: Порівняння продуктивності ===")

sizes = [1000, 10000, 50000]

print(f"{'N (Розмір)':<10} | {'Пошук у List (сек)':<20} | {'Пошук у Set (сек)':<20}")
print("-" * 55)

for n in sizes:
    data_list = list(range(n))
    data_set = set(data_list)
    target = n - 1

    time_list = timeit.timeit(lambda: target in data_list, number=1000)
    time_set = timeit.timeit(lambda: target in data_set, number=1000)

    print(f"{n:<10} | {time_list:<20.6f} | {time_set:<20.6f}")