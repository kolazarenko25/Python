# ==========================================
# ЗАВДАННЯ 1. КЛАСОВА ІЄРАРХІЯ ТА ПОЛІМОРФІЗМ
# ==========================================

class Transport:
    def __init__(self, brand, speed):
        self.brand = brand
        self.speed = speed

    def move(self):
        return f"{self.brand} рухається зі швидкістю {self.speed} км/год"

    def __str__(self):
        return f"{self.brand}, {self.speed} км/год"


class Car(Transport):
    def __init__(self, brand, speed, fuel):
        super().__init__(brand, speed)
        self.fuel = fuel

    def move(self):
        return f"Автомобіль {self.brand} їде на {self.fuel}"

    def __str__(self):
        return f"Автомобіль: {self.brand}, {self.speed} км/год, паливо: {self.fuel}"


class Bus(Transport):
    def __init__(self, brand, speed, passengers):
        super().__init__(brand, speed)
        self.passengers = passengers

    def move(self):
        return f"Автобус {self.brand} перевозить до {self.passengers} пасажирів"

    def __str__(self):
        return f"Автобус: {self.brand}, {self.speed} км/год, місць: {self.passengers}"


class Bicycle(Transport):
    def __init__(self, brand, speed, gears):
        super().__init__(brand, speed)
        self.gears = gears

    def move(self):
        return f"Велосипед {self.brand} рухається за рахунок педалей"

    def __str__(self):
        return f"Велосипед: {self.brand}, {self.speed} км/год, передач: {self.gears}"


print("=" * 50)
print("ЗАВДАННЯ 1. КЛАСОВА ІЄРАРХІЯ ТА ПОЛІМОРФІЗМ")
print("=" * 50)

transports = [
    Car("Toyota", 120, "бензин"),
    Bus("MAN", 80, 50),
    Bicycle("Trek", 30, 21)
]

print("\nПоліморфний обхід:")

for transport in transports:
    print(transport.move())

print("\nПеревірка типів:")

car = transports[0]

print("car є Car:", isinstance(car, Car))
print("car є Transport:", isinstance(car, Transport))
print("Car є підкласом Transport:", issubclass(Car, Transport))
print("Bus є підкласом Transport:", issubclass(Bus, Transport))

print("\nРядкове представлення:")
print(car)


# ==========================================
# ЗАВДАННЯ 2. ІНКАПСУЛЯЦІЯ, PROPERTY
# ==========================================

class BankAccount:
    def __init__(self, owner, balance, limit):
        self.owner = owner
        self._limit = limit
        self.__balance = 0
        self.balance = balance

    @property
    def balance(self):
        return self.__balance

    @balance.setter
    def balance(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Баланс повинен бути числом")

        if value < 0:
            raise ValueError("Баланс не може бути від'ємним")

        if value > self._limit:
            raise ValueError("Баланс перевищує встановлений ліміт")

        self.__balance = value

    @property
    def available(self):
        return self._limit - self.__balance

    def __str__(self):
        return f"Власник: {self.owner}, баланс: {self.__balance} грн"


print("\n" + "=" * 50)
print("ЗАВДАННЯ 2. ІНКАПСУЛЯЦІЯ ТА PROPERTY")
print("=" * 50)

account = BankAccount("Кирило", 5000, 10000)

print("\nКоректне створення:")
print(account)

print("\nОбчислювана властивість:")
print("Доступний ліміт:", account.available, "грн")

print("\nЗміна балансу:")
account.balance = 7000
print("Новий баланс:", account.balance)
print("Доступний ліміт:", account.available, "грн")

print("\nСпроба встановити від'ємний баланс:")

try:
    account.balance = -500
except ValueError as error:
    print("Помилка:", error)

print("\nСпроба встановити текст замість числа:")

try:
    account.balance = "п'ять тисяч"
except TypeError as error:
    print("Помилка:", error)

print("\nСпроба перевищити ліміт:")

try:
    account.balance = 15000
except ValueError as error:
    print("Помилка:", error)

print("\nПрямий доступ до приватного атрибута:")

try:
    print(account.__balance)
except AttributeError:
    print("AttributeError: прямий доступ заборонений")

print("\nДоступ через name mangling:")
print(account._BankAccount__balance)


# ==========================================
# ЗАВДАННЯ 3. МАГІЧНІ МЕТОДИ
# ==========================================

class Vector:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"Вектор ({self.x}, {self.y})"

    def __repr__(self):
        return f"Vector(x={self.x}, y={self.y})"

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, number):
        return Vector(self.x * number, self.y * number)

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __len__(self):
        return 2

    def __abs__(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5


print("\n" + "=" * 50)
print("ЗАВДАННЯ 3. МАГІЧНІ МЕТОДИ")
print("=" * 50)

v1 = Vector(3, 4)
v2 = Vector(1, 2)

print("\nstr:")
print(str(v1))

print("\nrepr:")
print(repr(v1))

print("\nДодавання:")
print("v1 + v2 =", v1 + v2)

print("\nВіднімання:")
print("v1 - v2 =", v1 - v2)

print("\nМноження:")
print("v1 * 2 =", v1 * 2)

print("\nПорівняння:")
print("v1 == v2:", v1 == v2)
print("v1 == Vector(3, 4):", v1 == Vector(3, 4))

print("\nlen():")
print("len(v1) =", len(v1))

print("\nabs():")
print("abs(v1) =", abs(v1))


# ==========================================
# ЗАВДАННЯ 4. АБСТРАКТНІ КЛАСИ ТА КОМПОЗИЦІЯ
# ==========================================

from abc import ABC, abstractmethod


class PaymentProcessor(ABC):

    @property
    @abstractmethod
    def name(self):
        pass

    @abstractmethod
    def pay(self, amount):
        pass

    @abstractmethod
    def check(self):
        pass

    def info(self):
        return f"Платіжний метод: {self.name}"


class CardPayment(PaymentProcessor):

    @property
    def name(self):
        return "Банківська картка"

    def pay(self, amount):
        return f"Оплачено карткою: {amount} грн"

    def check(self):
        return "Картка перевірена"


class CashPayment(PaymentProcessor):

    @property
    def name(self):
        return "Готівка"

    def pay(self, amount):
        return f"Оплачено готівкою: {amount} грн"

    def check(self):
        return "Готівку прийнято"


class Logger:

    def log(self, message):
        print("[LOG]", message)


class PaymentSystem:

    def __init__(self, processor, logger):
        self.processor = processor
        self.logger = logger

    def make_payment(self, amount):
        self.logger.log(self.processor.check())

        result = self.processor.pay(amount)

        self.logger.log(result)

        return result


print("\n" + "=" * 50)
print("ЗАВДАННЯ 4. АБСТРАКТНІ КЛАСИ ТА КОМПОЗИЦІЯ")
print("=" * 50)

print("\nСпроба створити абстрактний клас:")

try:
    processor = PaymentProcessor()
except TypeError as error:
    print("Помилка:", error)


logger = Logger()

card = CardPayment()
cash = CashPayment()

print("\nІнформація про способи оплати:")
print(card.info())
print(cash.info())

print("\nПоліморфний виклик:")

processors = [card, cash]

for processor in processors:
    print(processor.pay(500))

print("\nРобота композиції:")

system = PaymentSystem(card, logger)
system.make_payment(1000)

print()

system = PaymentSystem(cash, logger)
system.make_payment(700)


# ==========================================
# ЗАВДАННЯ 5. ПАТТЕРН STRATEGY
# ==========================================

class DeliveryStrategy:

    def calculate(self, weight, distance):
        raise NotImplementedError


class NovaPoshtaDelivery(DeliveryStrategy):

    def calculate(self, weight, distance):
        return 70 + weight * 10 + distance * 0.5


class UkrPoshtaDelivery(DeliveryStrategy):

    def calculate(self, weight, distance):
        return 50 + weight * 8 + distance * 0.4


class CourierDelivery(DeliveryStrategy):

    def calculate(self, weight, distance):
        return 100 + weight * 15 + distance * 1.0


class Delivery:

    def __init__(self, strategy):
        self.strategy = strategy

    def calculate_price(self, weight, distance):
        return self.strategy.calculate(weight, distance)

    def change_strategy(self, strategy):
        self.strategy = strategy

class PostamatDelivery(DeliveryStrategy):

    def calculate(self, weight, distance):
        return 60 + weight * 9 + distance * 0.3


print("\n" + "=" * 50)
print("ЗАВДАННЯ 5. ПАТТЕРН STRATEGY")
print("=" * 50)

weight = 3
distance = 20

delivery = Delivery(NovaPoshtaDelivery())

print("\nНова пошта:")
print("Вартість:", delivery.calculate_price(weight, distance), "грн")

delivery.change_strategy(UkrPoshtaDelivery())

print("\nУкрпошта:")
print("Вартість:", delivery.calculate_price(weight, distance), "грн")

delivery.change_strategy(CourierDelivery())

print("\nКур'єр:")
print("Вартість:", delivery.calculate_price(weight, distance), "грн")

delivery.change_strategy(PostamatDelivery())

print("\nПоштомат:")
print("Вартість:", delivery.calculate_price(weight, distance), "грн")

print("\n" + "=" * 50)
print("ВИКОНАННЯ ВСІХ ЗАВДАНЬ ЗАВЕРШЕНО")
print("=" * 50)