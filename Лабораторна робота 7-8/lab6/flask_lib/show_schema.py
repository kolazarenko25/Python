"""Виводить структуру таблиць SQLite (для перевірки результату міграцій).

Запуск: python show_schema.py
"""
from sqlalchemy import inspect

from app import create_app
from app.extensions import db

app = create_app()

with app.app_context():
    print("СУБД: SQLite")
    print("URI :", app.config["SQLALCHEMY_DATABASE_URI"])
    inspector = inspect(db.engine)
    for table in sorted(inspector.get_table_names()):
        columns = ", ".join(col["name"] for col in inspector.get_columns(table))
        print(f"\n{table}: {columns}")
        for fk in inspector.get_foreign_keys(table):
            print(f"    FK {fk['constrained_columns'][0]} -> {fk['referred_table']}.{fk['referred_columns'][0]}")
