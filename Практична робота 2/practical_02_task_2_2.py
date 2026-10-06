# practical_02_task_2_2.py

"""Конвеєр генераторів для обробки даних про оцінки студентів."""

from collections import defaultdict

SAMPLE_DATA = [
    "Олена,Математика,95",
    "Іван,Математика,78",
    "",
    "Марія,Фізика,92",
    "Петро,Математика,INVALID",
    "Анна,Фізика,88",
    "Олена,Фізика,90",
    "Іван,Програмування,85",
    "Марія,Програмування,91",
    "Петро,Фізика,76",
    "Анна,Математика,93",
    "Олена,Програмування,97",
    "",
    "Марія,Математика,89",
    "Іван,Фізика,72",
    "Петро,Програмування,80",
    "Анна,Програмування,86",
]


def data_source(records: list[str]):
    """Етап 1: Генератор, що видає записи по одному."""
    for record in records:
        yield record


def filter_empty(records):
    """Етап 2: Фільтрувати порожні рядки."""
    for record in records:
        if record.strip():
            yield record


def parse_records(records):
    """Етап 3: Парсинг рядків у структуровані дані.

    Yields:
        dict з ключами "student", "subject", "grade" (int).
        Пропускає записи з некоректними оцінками.
    """
    for record in records:
        parts = record.split(",")
        if len(parts) != 3:
            continue  # некоректний формат рядка
        student, subject, grade_str = (p.strip() for p in parts)
        try:
            grade = int(grade_str)
        except ValueError:
            continue  # нечислова оцінка — пропускаємо запис
        yield {"student": student, "subject": subject, "grade": grade}


def filter_passed(records, min_grade: int = 60):
    """Етап 4: Залишити лише студентів, що склали (>= min_grade)."""
    for record in records:
        if record["grade"] >= min_grade:
            yield record


def format_output(records):
    """Етап 5: Форматувати для виведення."""
    for record in records:
        yield f"[{record['subject']}] {record['student']}: {record['grade']} балів"


def main():
    # Конвеєр 1: фільтрований вивід
    pipeline = format_output(
        filter_passed(
            parse_records(
                filter_empty(
                    data_source(SAMPLE_DATA)
                )
            ),
            min_grade=75,
        )
    )

    print("=== Результати (>= 75 балів) ===")
    for line in pipeline:
        print(line)

    # Конвеєр 2: агрегація — середній бал по кожному предмету
    print("\n=== Середній бал по предметах ===")
    subject_grades = defaultdict(list)
    for record in parse_records(filter_empty(data_source(SAMPLE_DATA))):
        subject_grades[record["subject"]].append(record["grade"])

    for subject, grades in sorted(subject_grades.items()):
        avg = sum(grades) / len(grades)
        print(f"  {subject}: {avg:.1f} (з {len(grades)} оцінок)")


if __name__ == "__main__":
    main()
