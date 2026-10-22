"""Завдання 4 (Django): CRUD, фільтрація, Q, агрегація, анотація, select_related.

Запуск:  python manage.py run_queries
Команда перед кожним запуском очищає таблиці, тому результат відтворюваний.
"""
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import Avg, Count, F, Q, Sum
from django.db.models.deletion import ProtectedError
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from library.models import Author, Book, Genre, Loan, Reader, ReaderProfile


class Command(BaseCommand):
    help = "Демонстрація ORM-запитів Django для предметної області «Бібліотека»"

    def section(self, title):
        self.stdout.write(f"\n=== {title} ===")

    def handle(self, *args, **options):
        out = self.stdout.write

        # ---------- очищення (порядок враховує PROTECT) ----------
        Loan.objects.all().delete()
        Book.objects.all().delete()
        Reader.objects.all().delete()
        Author.objects.all().delete()
        Genre.objects.all().delete()

        # ---------- CREATE ----------
        self.section("CREATE: створення об'єктів")
        shevchenko = Author.objects.create(name="Тарас Шевченко", country="UA", birth_year=1814)
        franko = Author.objects.create(name="Іван Франко", country="UA", birth_year=1856)
        orwell = Author.objects.create(name="George Orwell", country="GB", birth_year=1903)

        poetry = Genre.objects.create(name="Поезія", slug="poetry")
        novel = Genre.objects.create(name="Роман", slug="novel")
        dystopia = Genre.objects.create(name="Антиутопія", slug="dystopia")

        kobzar = Book.objects.create(
            title="Кобзар", isbn="9789660001001", author=shevchenko, year=1840, copies_total=3
        )
        kobzar.genres.add(poetry)
        zakhar = Book.objects.create(
            title="Захар Беркут", isbn="9789660001002", author=franko, year=1883
        )
        zakhar.genres.add(novel)
        b1984 = Book.objects.create(title="1984", isbn="9789660001003", author=orwell, year=1949, copies_total=2)
        b1984.genres.add(dystopia, novel)
        farm = Book.objects.create(title="Animal Farm", isbn="9789660001004", author=orwell, year=1945, copies_total=2)
        farm.genres.add(dystopia)
        moisei = Book.objects.create(title="Мойсей", isbn="9789660001005", author=franko, year=1905)
        moisei.genres.add(poetry)

        olena = Reader.objects.create(full_name="Олена Коваль", email="olena@example.com")
        ReaderProfile.objects.create(reader=olena, phone="+380501112233", address="Київ", newsletter=True)
        andrii = Reader.objects.create(full_name="Андрій Мельник", email="andrii@example.com")
        ReaderProfile.objects.create(reader=andrii, phone="+380671112233", address="Львів")
        maria = Reader.objects.create(full_name="Марія Шевчук", email="maria@example.com")

        today = timezone.localdate()
        Loan.objects.create(reader=olena, book=kobzar, loaned_at=today - timedelta(days=20),
                            due_date=today - timedelta(days=6))            # прострочена
        Loan.objects.create(reader=olena, book=b1984, loaned_at=today - timedelta(days=2),
                            due_date=today + timedelta(days=12))           # активна
        Loan.objects.create(reader=andrii, book=b1984, loaned_at=today - timedelta(days=30),
                            due_date=today - timedelta(days=16), returned_at=today - timedelta(days=15))
        Loan.objects.create(reader=andrii, book=zakhar, loaned_at=today - timedelta(days=1),
                            due_date=today + timedelta(days=13))           # активна
        out(f"Авторів: {Author.objects.count()}, жанрів: {Genre.objects.count()}, "
            f"книг: {Book.objects.count()}, читачів: {Reader.objects.count()}, видач: {Loan.objects.count()}")

        # ---------- READ ----------
        self.section("READ: filter() — книги, видані до 1900 року")
        for b in Book.objects.filter(year__lt=1900):
            out(f"  {b.title} ({b.year})")

        self.section("READ: exclude() — книги не українських авторів")
        for b in Book.objects.exclude(author__country="UA"):
            out(f"  {b.title} — {b.author.name}")

        self.section("READ: Q-об'єкти — (рік >= 1940 АБО назва містить 'Коб')")
        for b in Book.objects.filter(Q(year__gte=1940) | Q(title__icontains="Коб")):
            out(f"  {b.title} ({b.year})")

        self.section("READ: Q з NOT — книги, що НЕ належать до жанру 'Поезія'")
        for b in Book.objects.filter(~Q(genres__slug="poetry")).distinct():
            out(f"  {b.title}")

        self.section("READ: get() — книга за ISBN")
        out(f"  {Book.objects.get(isbn='9789660001003')}")

        # ---------- Агрегація та анотація ----------
        self.section("AGGREGATE: зведені значення по книгах")
        stats = Book.objects.aggregate(
            books=Count("id"), avg_year=Avg("year"), copies=Sum("copies_total")
        )
        out(f"  {stats}")

        self.section("ANNOTATE: кількість книг у кожного автора")
        for a in Author.objects.annotate(n_books=Count("books")).order_by("-n_books", "name"):
            out(f"  {a.name}: {a.n_books}")

        self.section("ANNOTATE + filter: активні видачі (не повернені) на читача")
        readers = Reader.objects.annotate(
            active=Count("loans", filter=Q(loans__returned_at__isnull=True))
        ).order_by("-active", "full_name")
        for r in readers:
            out(f"  {r.full_name}: {r.active}")

        # ---------- Зворотні зв'язки ----------
        self.section("Зворотні зв'язки (related_name)")
        out(f"  Книги Франка: {[b.title for b in franko.books.all()]}")
        out(f"  Книги жанру 'Антиутопія': {[b.title for b in dystopia.books.all()]}")
        out(f"  Видачі Олени: {olena.loans.count()}, телефон з профілю: {olena.profile.phone}")
        out(f"  Читач за профілем (O2O у зворотний бік): {olena.profile.reader.full_name}")
        out(f"  Прострочені видачі: {[str(ln) for ln in Loan.objects.all() if ln.is_overdue()]}")

        # ---------- Проблема N+1 ----------
        self.section("N+1: порівняння кількості SQL-запитів")
        with CaptureQueriesContext(connection) as naive:
            for b in Book.objects.all():
                _ = b.author.name
        with CaptureQueriesContext(connection) as joined:
            for b in Book.objects.select_related("author"):
                _ = b.author.name
        with CaptureQueriesContext(connection) as prefetched:
            for b in Book.objects.prefetch_related("genres"):
                _ = [g.name for g in b.genres.all()]
        out(f"  без оптимізації:            {len(naive)} запитів")
        out(f"  select_related('author'):   {len(joined)} запит")
        out(f"  prefetch_related('genres'): {len(prefetched)} запити")

        # ---------- UPDATE ----------
        self.section("UPDATE: save(), update() та F-вираз")
        kobzar = Book.objects.get(isbn="9789660001001")
        kobzar.copies_total = 10
        kobzar.save()
        out(f"  save(): 'Кобзар' тепер має {Book.objects.get(pk=kobzar.pk).copies_total} примірників")
        updated = Book.objects.filter(author=orwell).update(copies_total=F("copies_total") + 1)
        out(f"  update() + F: змінено рядків: {updated}")
        out(f"  Примірники 'Animal Farm': {Book.objects.get(isbn='9789660001004').copies_total}")

        # ---------- DELETE ----------
        self.section("DELETE: політики on_delete")
        try:
            shevchenko.delete()
        except ProtectedError:
            out("  PROTECT: автора з книгами видалити не можна (ProtectedError)")
        deleted = Loan.objects.filter(returned_at__isnull=False).delete()
        out(f"  delete() за умовою (повернені видачі): {deleted}")
        result = andrii.delete()
        out(f"  CASCADE: видалено читача разом із профілем і видачами: {result}")
        out(f"  Лишилось читачів: {Reader.objects.count()}, видач: {Loan.objects.count()}")
