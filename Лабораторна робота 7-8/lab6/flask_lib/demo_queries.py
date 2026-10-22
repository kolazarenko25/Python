"""Завдання 4 (Flask): CRUD, фільтрація, агрегація, joinedload, commit/rollback.

Запуск: python demo_queries.py   (спершу застосуйте міграції: flask --app run db upgrade)
Скрипт очищає таблиці на початку, тому його можна запускати повторно.
"""
from contextlib import contextmanager
from datetime import date, timedelta

from sqlalchemy import event, func, not_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app import create_app
from app.extensions import db
from app.models import Author, Book, Genre, Loan, Reader, ReaderProfile, book_genres
from app.services import generate_card_number

app = create_app()


def section(title):
    print(f"\n=== {title} ===")


@contextmanager
def count_queries():
    """Рахує SQL-запити, виконані всередині блоку."""
    counter = {"n": 0}

    def on_execute(conn, cursor, statement, parameters, context, executemany):
        counter["n"] += 1

    event.listen(db.engine, "before_cursor_execute", on_execute)
    try:
        yield counter
    finally:
        event.remove(db.engine, "before_cursor_execute", on_execute)


def reset_tables():
    Loan.query.delete()
    db.session.execute(book_genres.delete())
    Book.query.delete()
    ReaderProfile.query.delete()
    Reader.query.delete()
    Author.query.delete()
    Genre.query.delete()
    db.session.commit()


with app.app_context():
    reset_tables()
    today = date.today()

    # ---------- CREATE ----------
    section("CREATE: створення об'єктів")
    shevchenko = Author(name="Тарас Шевченко", country="UA", birth_year=1814)
    franko = Author(name="Іван Франко", country="UA", birth_year=1856)
    orwell = Author(name="George Orwell", country="GB", birth_year=1903)
    poetry = Genre(name="Поезія", slug="poetry")
    novel = Genre(name="Роман", slug="novel")
    dystopia = Genre(name="Антиутопія", slug="dystopia")
    db.session.add_all([shevchenko, franko, orwell, poetry, novel, dystopia])
    db.session.flush()  # отримуємо id без завершення транзакції

    kobzar = Book(title="Кобзар", isbn="9789660001001", year=1840, copies_total=3, author=shevchenko, genres=[poetry])
    zakhar = Book(title="Захар Беркут", isbn="9789660001002", year=1883, author=franko, genres=[novel])
    b1984 = Book(title="1984", isbn="9789660001003", year=1949, copies_total=2, author=orwell, genres=[dystopia, novel])
    farm = Book(title="Animal Farm", isbn="9789660001004", year=1945, copies_total=2, author=orwell, genres=[dystopia])
    moisei = Book(title="Мойсей", isbn="9789660001005", year=1905, author=franko, genres=[poetry])
    olena = Reader(full_name="Олена Коваль", email="olena@example.com", card_number=generate_card_number())
    olena.profile = ReaderProfile(phone="+380501112233", address="Київ", newsletter=True)
    andrii = Reader(full_name="Андрій Мельник", email="andrii@example.com", card_number=generate_card_number())
    andrii.profile = ReaderProfile(phone="+380671112233", address="Львів")
    db.session.add_all([kobzar, zakhar, b1984, farm, moisei, olena, andrii])
    db.session.flush()
    db.session.add_all([
        Loan(reader=olena, book=kobzar, loaned_at=today - timedelta(days=20), due_date=today - timedelta(days=6)),
        Loan(reader=olena, book=b1984, loaned_at=today - timedelta(days=2), due_date=today + timedelta(days=12)),
        Loan(reader=andrii, book=b1984, loaned_at=today - timedelta(days=30),
             due_date=today - timedelta(days=16), returned_at=today - timedelta(days=15)),
        Loan(reader=andrii, book=zakhar, loaned_at=today - timedelta(days=1), due_date=today + timedelta(days=13)),
    ])
    db.session.commit()  # усі зміни фіксуються однією транзакцією
    print(f"Авторів: {Author.query.count()}, жанрів: {Genre.query.count()}, книг: {Book.query.count()}, "
          f"читачів: {Reader.query.count()}, видач: {Loan.query.count()}")

    # ---------- READ ----------
    section("READ: filter() — книги, видані до 1900 року")
    for b in Book.query.filter(Book.year < 1900).order_by(Book.year):
        print(f"  {b.title} ({b.year})")

    section("READ: filter_by() — книги автора Orwell")
    for b in Book.query.join(Author).filter_by(name="George Orwell").order_by(Book.title):
        print(f"  {b.title}")

    section("READ: not_() — книги не українських авторів")
    for b in Book.query.join(Author).filter(not_(Author.country == "UA")):
        print(f"  {b.title} — {b.author.name}")

    section("READ: or_() — (рік >= 1940 АБО назва містить 'Коб')")
    for b in Book.query.filter(or_(Book.year >= 1940, Book.title.contains("Коб"))).order_by(Book.year):
        print(f"  {b.title} ({b.year})")

    section("READ: get по первинному ключу та first()")
    print(f"  {db.session.get(Book, kobzar.id)}")
    print(f"  {Book.query.filter_by(isbn='9789660001003').first()}")

    # ---------- Агрегація ----------
    section("AGGREGATE: func.count / avg / sum по книгах")
    total, avg_year, copies = db.session.query(
        func.count(Book.id), func.avg(Book.year), func.sum(Book.copies_total)
    ).one()
    print(f"  книг={total}, середній рік={avg_year:.1f}, примірників={copies}")

    section("GROUP BY: кількість книг у кожного автора")
    rows = (
        db.session.query(Author.name, func.count(Book.id).label("n"))
        .outerjoin(Book, Book.author_id == Author.id)
        .group_by(Author.id)
        .order_by(func.count(Book.id).desc(), Author.name)
    )
    for name, n in rows:
        print(f"  {name}: {n}")

    # ---------- Зв'язки та оптимізація ----------
    section("Зв'язки: backref та relationship")
    print(f"  Книги Франка: {[b.title for b in franko.books]}")
    print(f"  Книги жанру 'Антиутопія': {[b.title for b in dystopia.books]}")
    print(f"  Видачі Олени: {len(olena.loans)}, телефон з профілю: {olena.profile.phone}")
    print(f"  Прострочені видачі: {[str(ln) for ln in Loan.query.all() if ln.is_overdue()]}")

    section("N+1: порівняння кількості SQL-запитів")
    db.session.expire_all()
    with count_queries() as naive:
        for b in Book.query.all():
            _ = b.author.name
    db.session.expire_all()
    with count_queries() as eager:
        for b in Book.query.options(joinedload(Book.author)).all():
            _ = b.author.name
    print(f"  ледаче завантаження:  {naive['n']} запитів")
    print(f"  joinedload('author'): {eager['n']} запит")

    # ---------- UPDATE ----------
    section("UPDATE: зміна атрибута + commit, масове оновлення")
    kobzar = Book.query.filter_by(isbn="9789660001001").one()
    kobzar.copies_total = 10
    db.session.commit()
    print(f"  'Кобзар' тепер має {db.session.get(Book, kobzar.id).copies_total} примірників")
    updated = Book.query.filter_by(author_id=orwell.id).update({Book.copies_total: Book.copies_total + 1})
    db.session.commit()
    print(f"  масове оновлення: змінено рядків {updated}")

    # ---------- Транзакційна атомарність ----------
    section("ТРАНЗАКЦІЯ 1: кілька змін фіксуються разом (commit)")
    maria = Reader(full_name="Марія Шевчук", email="maria@example.com", card_number=generate_card_number())
    db.session.add(maria)
    db.session.flush()
    db.session.add(Loan(reader_id=maria.id, book_id=moisei.id, due_date=today + timedelta(days=14)))
    moisei.copies_total -= 1
    db.session.commit()
    print(f"  читач збережений: {Reader.query.filter_by(email='maria@example.com').count() == 1}, "
          f"видач у Марії: {Loan.query.filter_by(reader_id=maria.id).count()}")

    section("ТРАНЗАКЦІЯ 2: помилка -> rollback скасовує ВСІ зміни")
    try:
        db.session.add(Reader(full_name="Тимчасовий читач", email="temp@example.com"))
        db.session.add(Book(title="Дублікат", isbn="9789660001001", year=2000, author_id=orwell.id))  # ISBN вже існує
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        print(f"  перехоплено IntegrityError: {str(exc.orig)}")
    print(f"  'Тимчасовий читач' у базі: {Reader.query.filter_by(email='temp@example.com').count()} (очікується 0)")

    # ---------- DELETE ----------
    section("DELETE: видалення та каскад")
    try:
        db.session.delete(db.session.get(Author, shevchenko.id))
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        print("  автора з книгами видалити не вдалося (author_id NOT NULL) — rollback")
    removed = Loan.query.filter(Loan.returned_at.isnot(None)).delete()
    db.session.commit()
    print(f"  delete() за умовою (повернені видачі): {removed}")
    db.session.delete(db.session.get(Reader, andrii.id))
    db.session.commit()
    print(f"  cascade: читача Андрія видалено разом із профілем і видачами; "
          f"профілів: {ReaderProfile.query.count()}, видач: {Loan.query.count()}")
