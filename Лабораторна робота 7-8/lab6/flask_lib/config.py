import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """СУБД: SQLite. Файл бази лежить у корені проєкту (library.db)."""

    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "library.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
