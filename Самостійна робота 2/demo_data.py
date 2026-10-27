"""Початкові дані для демонстрації."""
from library_system.validators import isbn13_with_check


def seed(service):
    shevchenko = service.add_author("Тарас Шевченко", 1814)
    ukrainka = service.add_author("Леся Українка", 1871)
    franko = service.add_author("Іван Франко", 1856)
    kotsiubynsky = service.add_author("Михайло Коцюбинський", 1864)
    books = [
        ("Кобзар", shevchenko, 1840, "978966000001", 3),
        ("Лісова пісня", ukrainka, 1911, "978966000002", 2),
        ("Захар Беркут", franko, 1883, "978966000003", 2),
        ("Тіні забутих предків", kotsiubynsky, 1911, "978966000004", 1),
        ("Мойсей", franko, 1905, "978966000005", 1),
    ]
    for title, author, year, body, copies in books:
        service.add_book(title, author.id, year, isbn13_with_check(body), copies)
    for name, email in [("Олена Коваль", "olena@example.com"),
                        ("Андрій Мельник", "andriy@example.com"),
                        ("Марія Бойко", "maria@example.com")]:
        service.register_reader(name, email)
