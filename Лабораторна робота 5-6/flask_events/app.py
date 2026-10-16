"""Flask-застосунок «Реєстрація на події» (аналог Django-проєкту)."""
import os
import secrets
from datetime import date, datetime

from flask import Flask, flash, redirect, render_template, url_for
from flask_wtf.csrf import CSRFError, CSRFProtect

from forms import RegistrationForm

csrf = CSRFProtect()

EVENTS = [
    {
        "title": "Python для початківців",
        "date": date(2026, 11, 12),
        "place": "Київ, КПІ ім. Ігоря Сікорського",
        "seats": 30,
        "taken": 12,
        "description": "Вступний воркшоп: встановлення середовища, змінні, цикли, функції та перші власні скрипти під керівництвом ментора.",
    },
    {
        "title": "Веброзробка на Django",
        "date": date(2026, 11, 26),
        "place": "Онлайн",
        "seats": None,
        "taken": 0,
        "description": "Лекція про архітектуру MVT, маршрутизацію, шаблони та форми: від порожнього проєкту до робочого застосунку за одне заняття.",
    },
    {
        "title": "Конференція PyUA Autumn",
        "date": date(2026, 12, 5),
        "place": "Львів, Дім Футболу",
        "seats": 150,
        "taken": 97,
        "description": "Одноденна конференція зі спільнотою Python-розробників України: доповіді про Flask, асинхронність, тестування та DevOps.",
    },
]


def create_app(test_config=None):
    app = Flask(__name__)  # шаблони: ./templates, статика: ./static
    # Секретний ключ — зі змінної оточення; запасний випадковий ключ діє лише до перезапуску.
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY") or secrets.token_hex(32)
    if test_config:
        app.config.update(test_config)

    csrf.init_app(app)  # глобальна перевірка CSRF-токена для всіх POST-запитів

    @app.context_processor
    def inject_globals():
        return {"current_year": datetime.now().year}

    @app.route("/")
    def home():
        return render_template(
            "home.html",
            site_title="Реєстрація на події",   # рядок
            events_count=len(EVENTS),           # число
            upcoming=EVENTS[:2],                # список
        )

    @app.route("/events")
    def event_list():
        return render_template("event_list.html", page_title="Усі заходи", events=EVENTS)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        form = RegistrationForm()
        if form.validate_on_submit():
            flash(f"Дякуємо, {form.name.data.strip()}! Вашу заявку прийнято.", "success")
            return redirect(url_for("register"))   # PRG
        # GET або невалідний POST: форма з помилками та збереженим введенням
        return render_template("register.html", form=form)

    @app.errorhandler(CSRFError)
    def handle_csrf_error(error):
        return render_template("csrf_error.html", reason=error.description), 400

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
