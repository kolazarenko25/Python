from flask import Flask, jsonify

from config import Config

from .extensions import db, migrate


def create_app(test_config=None):
    """Фабрика додатка. test_config перевизначає налаштування (для тестів)."""
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)

    app.json.ensure_ascii = False  # кирилиця у JSON-відповідях без \uXXXX
    db.init_app(app)
    # Імпорт моделей потрібен, щоб Flask-Migrate/Alembic «бачили» всі таблиці.
    from . import models  # noqa: F401

    migrate.init_app(app, db)

    from .routes import bp

    app.register_blueprint(bp)

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify(error="Не знайдено"), 404

    return app
