# Лабораторна: Django / Flask — моделі, міграції, запити, PyTest

Предметна область: **Інтернет-бібліотека** (Author, Genre, Book, Reader, ReaderProfile, Loan).

```
lab6/
├── django_lib/        проєкт Django (застосунок library) + tests/
├── flask_lib/         проєкт Flask (Flask-SQLAlchemy + Flask-Migrate) + tests/
├── Звіт_ЛР.docx       звіт із жовтими рамками під 9 скріншотів
└── tools/build_report.py   (генератор звіту, для роботи не потрібен)
```

> Код написано без запуску (у середовищі, де його готували, не було доступу до PyPI).
> Якщо якась команда видасть помилку — надішліть текст помилки, я виправлю.

## Порядок виконання (9 скріншотів)

Скріншот = знімок вікна терміналу з командою **і** її виводом. Номери збігаються з «Рисунок N» у звіті.

### Django  (`cd django_lib`)

```bash
python -m venv .venv
.venv\Scripts\activate            # Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
```

| № | Команди | Примітка |
|---|---------|----------|
| 1 | `python manage.py makemigrations library` і `python manage.py migrate` | Створюється 0001_initial |
| — | **Відкрийте `library/models.py`, розкоментуйте рядок `pages = ...` у моделі Book** | Крок 2 |
| 2 | `python manage.py makemigrations library`, `python manage.py migrate`, `python manage.py showmigrations library` | Створюється 0002_book_pages |
| 3 | `python manage.py sqlmigrate library 0002` | |
| 6 | `python manage.py run_queries` | Завдання 4 (Django) |
| 8 | `pytest -v --cov=library --cov-report=term-missing` | Тести + coverage |

### Flask  (`cd flask_lib`)

```bash
pip install -r requirements.txt   # у тому самому або новому venv
```

| № | Команди | Примітка |
|---|---------|----------|
| 4 | `flask --app run db init`, `flask --app run db migrate -m "initial schema"`, `flask --app run db upgrade` | Перша ревізія |
| — | **Відкрийте `app/models.py`, розкоментуйте рядок `pages = ...` у моделі Book** | Крок 2 |
| 5 | `flask --app run db migrate -m "add book pages"`, `flask --app run db upgrade`, `flask --app run db history`, `python show_schema.py` | Друга ревізія |
| 7 | `python demo_queries.py` | Завдання 4 (Flask) |
| 9 | `pytest -v --cov=app --cov-report=term-missing` | Тести + coverage |

Скріншоти 4–5 робіть **до** скріншота 7 (демо працює з уже створеними таблицями).

## Що зробити у звіті

1. Відкрийте `Звіт_ЛР.docx`, на кожній жовтій рамці «СКРІНШОТ №N» клацніть усередину, вставте знімок, видаліть жовтий текст.
2. Заповніть жовті поля `[[...]]`: титульна сторінка, версії Python/пакетів (`python --version`, `pip show ...`).
3. Прочитайте розділ 7.3 «Аналіз прогалин» і звірте зі своїм coverage — підправте, якщо цифри/модулі відрізняються.

## Запуск з нуля (перевірка відтворюваності)

* Django: видаліть `db.sqlite3`, виконайте `python manage.py migrate`.
* Flask: видаліть `library.db`, виконайте `flask --app run db upgrade`.
