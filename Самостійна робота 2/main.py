"""Точка входу: python main.py [demo|threads|all]"""
import argparse
import logging
import os
import time

from demo_data import seed
from library_system import LibraryService
from library_system.concurrency import RequestProcessor
from library_system.exceptions import LibraryError
from library_system.logging_config import configure_logging
from library_system.metaclasses import SingletonMeta
from library_system.search import AvailableOnly, ByAuthor, ByTitle, ByYearRange
from library_system.validators import isbn13_with_check


def title(text):
    print(f"\n{'=' * 8} {text} {'=' * 8}")


def try_action(description, func, *args, **kwargs):
    """Виконує дію й показує, як система реагує на некоректні дані."""
    try:
        result = func(*args, **kwargs)
        print(f"[OK]     {description}: {result}")
        return result
    except LibraryError as exc:
        print(f"[ПОМИЛКА] {description}\n          -> {type(exc).__name__}: {exc}")


def demo():
    title("1. Наповнення бази (метаклас логує створення об'єктів)")
    service = LibraryService()
    seed(service)
    print("Статистика:", service.statistics())
    print("Singleton працює:", service is LibraryService())

    title("2. Пошук (паттерн Strategy)")
    for strategy, label in [(ByAuthor("франко"), "автор «франко»"),
                            (ByTitle("пісня"), "назва «пісня»"),
                            (ByYearRange(1900, 1999), "роки 1900–1999"),
                            (AvailableOnly(), "доступні")]:
        print(f"{label}: {[b.title for b in service.search(strategy)]}")

    title("3. Видача та повернення")
    try_action("Олена бере «Кобзар»", service.borrow_book, 1, 1)
    try_action("Андрій бере «Тіні забутих предків»", service.borrow_book, 2, 4)
    try_action("Марія бере «Тіні забутих предків» (1 примірник)", service.borrow_book, 3, 4)
    try_action("Андрій повертає «Тіні забутих предків»", service.return_book, 2, 4)
    try_action("Марія бере «Тіні забутих предків» ще раз", service.borrow_book, 3, 4)
    try_action("Олена повертає книгу, якої не брала", service.return_book, 1, 2)

    title("4. Захист від некоректного вводу")
    try_action("Автор з порожнім ім'ям", service.add_author, "  ", 1900)
    try_action("Автор з роком 'abc'", service.add_author, "Іван Тест", "abc")
    try_action("Книга з неправильним ISBN", service.add_book, "Тест", 1, 2000, "1234567890123")
    try_action("Книга з неіснуючим автором", service.add_book, "Тест", 99, 2000,
               isbn13_with_check("978966000099"))
    try_action("Дублікат ISBN", service.add_book, "Кобзар (копія)", 1, 1840,
               isbn13_with_check("978966000001"))
    try_action("Читач з поганим e-mail", service.register_reader, "Петро Тест", "not-an-email")
    try_action("Пошук зі стратегією неправильного типу", service.search, "Кобзар")
    try_action("Неіснуючий читач бере книгу", service.borrow_book, 42, 1)
    # ліміт видач
    for book_id in (2, 3):
        try_action(f"Олена бере книгу {book_id}", service.borrow_book, 1, book_id)
    try_action("Олена бере 4-ту книгу (ліміт 3)", service.borrow_book, 1, 5)

    title("5. Збереження та завантаження JSON")
    os.makedirs("data", exist_ok=True)
    service.save("data/library.json")
    before = service.statistics()
    service.load("data/library.json")
    print("Стан після load збігається:", before == service.statistics())
    try_action("Завантаження неіснуючого файлу", service.load, "data/missing.json")

    title("6. Журнал подій (паттерн Observer)")
    print("Лічильник подій:", dict(service.stats.counter))
    print("Останні 3 записи аудиту:")
    for ts, event, payload in service.audit.records[-3:]:
        print(" ", ts, event, payload)


def threads():
    SingletonMeta.reset(LibraryService)
    service = LibraryService()
    seed(service)
    popular = service.add_book("Бестселер", 1, 2020, isbn13_with_check("978966000100"), copies=5)

    title("A. 40 читачів одночасно реєструються")
    processor = RequestProcessor(workers=8)
    regs = [(f"reg-{i}", service.register_reader, (f"Читач Номер{i}", f"user{i}@example.com"))
            for i in range(40)]
    results = processor.run_batch(regs)
    ok = sum(r.ok for r in results)
    ids = {r.value.id for r in results if r.ok}
    print(f"Успішно: {ok}/40, унікальних id: {len(ids)}, потоків: {len({r.thread for r in results})}")

    title("B. 40 одночасних запитів на книгу з 5 примірниками")
    reader_ids = [r.value.id for r in results if r.ok]
    borrows = [(f"borrow-{rid}", service.borrow_book, (rid, popular.id)) for rid in reader_ids]
    results = processor.run_batch(borrows)
    granted = sum(r.ok for r in results)
    refused = [r for r in results if not r.ok]
    print(f"Видано: {granted}, відмов: {len(refused)} "
          f"({refused[0].error.split(':')[0] if refused else '-'})")
    print(f"Доступних примірників: {popular.available_copies}")
    stats = service.statistics()
    consistent = stats["copies_available"] + stats["active_loans"] == stats["copies_total"]
    print("Інваріант (доступно + видано = всього):", consistent, stats)

    title("C. Мішані запити (пошук, видача, повернення) паралельно")
    mixed = []
    for i, rid in enumerate(reader_ids[:20]):
        mixed.append((f"search-{i}", service.search, (ByAuthor("франко"),)))
        mixed.append((f"borrow-{i}", service.borrow_book, (rid, 3)))
        mixed.append((f"return-{i}", service.return_book, (rid, popular.id)))
    results = processor.run_batch(mixed)
    print(f"Запитів: {len(results)}, успішних: {sum(r.ok for r in results)}, "
          f"потоків: {len({r.thread for r in results})}")
    stats = service.statistics()
    print("Інваріант після мішаного навантаження:",
          stats["copies_available"] + stats["active_loans"] == stats["copies_total"])

    title("D. Продуктивність: послідовно vs пул потоків (затримка 50 мс/запит)")
    queries = [(f"q-{i}", service.search, (ByTitle("к"),)) for i in range(40)]
    for workers in (1, 4, 8, 16):
        proc = RequestProcessor(workers=workers, latency=0.05)
        start = time.perf_counter()
        proc.run_batch(queries) if workers > 1 else proc.run_sequential(queries)
        print(f"workers={workers:<2} час = {time.perf_counter() - start:.3f} с")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Система управління бібліотекою")
    parser.add_argument("mode", nargs="?", default="all", choices=["demo", "threads", "all"])
    args = parser.parse_args()
    if args.mode in ("demo", "all"):
        configure_logging(logging.INFO)
        demo()
    if args.mode in ("threads", "all"):
        configure_logging(logging.ERROR)
        threads()
