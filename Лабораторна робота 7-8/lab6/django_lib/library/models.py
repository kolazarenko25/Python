"""Моделі предметної області «Інтернет-бібліотека».

Сутності та зв'язки:
    Author  1 ── * Book          (ForeignKey, on_delete=PROTECT)
    Book    * ── * Genre         (ManyToManyField)
    Reader  1 ── 1 ReaderProfile (OneToOneField, on_delete=CASCADE)
    Reader  1 ── * Loan          (ForeignKey, on_delete=CASCADE)
    Book    1 ── * Loan          (ForeignKey, on_delete=PROTECT)
"""
from django.core.validators import MinLengthValidator
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Author(models.Model):
    COUNTRY_CHOICES = [
        ("UA", "Україна"),
        ("GB", "Велика Британія"),
        ("US", "США"),
        ("PL", "Польща"),
        ("OT", "Інша"),
    ]

    name = models.CharField("Ім'я", max_length=150)
    country = models.CharField("Країна", max_length=2, choices=COUNTRY_CHOICES, default="UA")
    birth_year = models.PositiveSmallIntegerField("Рік народження", null=True, blank=True)
    bio = models.TextField("Біографія", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Автор"
        verbose_name_plural = "Автори"

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField("Назва", max_length=80, unique=True)
    slug = models.SlugField("Слаг", max_length=80, unique=True)
    description = models.TextField("Опис", blank=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Жанр"
        verbose_name_plural = "Жанри"

    def __str__(self):
        return self.name


class Book(models.Model):
    STATUS_AVAILABLE = "available"
    STATUS_ARCHIVED = "archived"
    STATUS_CHOICES = [
        (STATUS_AVAILABLE, "Доступна"),
        (STATUS_ARCHIVED, "В архіві"),
    ]

    title = models.CharField("Назва", max_length=200)
    isbn = models.CharField(
        "ISBN",
        max_length=13,
        unique=True,
        validators=[MinLengthValidator(13)],
    )
    # Автора не можна видалити, поки в каталозі є його книги -> PROTECT.
    author = models.ForeignKey(
        Author,
        on_delete=models.PROTECT,
        related_name="books",
        verbose_name="Автор",
    )
    genres = models.ManyToManyField(Genre, related_name="books", blank=True, verbose_name="Жанри")
    year = models.PositiveSmallIntegerField("Рік видання")
    copies_total = models.PositiveIntegerField("Кількість примірників", default=1)
    status = models.CharField("Статус", max_length=10, choices=STATUS_CHOICES, default=STATUS_AVAILABLE)
    created_at = models.DateTimeField("Додано", auto_now_add=True)

    # --- КРОК 2 (Завдання 2) -------------------------------------------------
    # Після першої міграції (0001_initial) РОЗКОМЕНТУЙТЕ наступний рядок
    # і виконайте makemigrations -> буде створено 0002_book_pages.
    pages = models.PositiveIntegerField("Кількість сторінок", default=0)
    # -------------------------------------------------------------------------

    class Meta:
        ordering = ["title"]
        verbose_name = "Книга"
        verbose_name_plural = "Книги"
        indexes = [models.Index(fields=["year"], name="book_year_idx")]

    def __str__(self):
        return f"{self.title} ({self.author.name})"

    def get_absolute_url(self):
        return reverse("book_detail", args=[self.pk])


class Reader(models.Model):
    full_name = models.CharField("ПІБ", max_length=150)
    email = models.EmailField("Email", unique=True)
    registered_at = models.DateTimeField("Дата реєстрації", auto_now_add=True)

    class Meta:
        ordering = ["full_name"]
        verbose_name = "Читач"
        verbose_name_plural = "Читачі"

    def __str__(self):
        return self.full_name


class ReaderProfile(models.Model):
    # Профіль не існує без читача -> CASCADE; unique-ключ гарантує зв'язок 1:1.
    reader = models.OneToOneField(
        Reader,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Читач",
    )
    phone = models.CharField("Телефон", max_length=20, blank=True)
    address = models.CharField("Адреса", max_length=255, blank=True)
    birth_date = models.DateField("Дата народження", null=True, blank=True)
    newsletter = models.BooleanField("Підписка на розсилку", default=False)

    class Meta:
        ordering = ["reader__full_name"]
        verbose_name = "Профіль читача"
        verbose_name_plural = "Профілі читачів"

    def __str__(self):
        return f"Профіль: {self.reader.full_name}"


class Loan(models.Model):
    # Історія видач не повинна лишатися без читача -> CASCADE,
    # але книгу з історією видач видалити не можна -> PROTECT.
    reader = models.ForeignKey(
        Reader,
        on_delete=models.CASCADE,
        related_name="loans",
        verbose_name="Читач",
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.PROTECT,
        related_name="loans",
        verbose_name="Книга",
    )
    loaned_at = models.DateField("Дата видачі", default=timezone.localdate)
    due_date = models.DateField("Повернути до")
    returned_at = models.DateField("Дата повернення", null=True, blank=True)

    class Meta:
        ordering = ["-loaned_at"]
        verbose_name = "Видача"
        verbose_name_plural = "Видачі"
        constraints = [
            models.UniqueConstraint(
                fields=["reader", "book", "loaned_at"],
                name="unique_loan_per_day",
            )
        ]

    def __str__(self):
        return f"{self.reader.full_name} → {self.book.title}"

    def is_overdue(self):
        """Книга прострочена, якщо не повернена і термін минув."""
        if self.returned_at is not None:
            return False
        return self.due_date < timezone.localdate()
