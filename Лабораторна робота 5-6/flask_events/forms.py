import re

from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, TextAreaField, ValidationError
from wtforms.fields import EmailField
from wtforms.validators import DataRequired, Email, Length

EVENT_TYPES = [
    ("", "— оберіть тип заходу —"),
    ("workshop", "Воркшоп"),
    ("lecture", "Лекція"),
    ("conference", "Конференція"),
]

# Ті самі бізнес-правила, що й у Django-формі (для коректного порівняння).
NAME_RE = re.compile(r"[^\W\d_]+(?:[ '’-][^\W\d_]+)*")
MIN_WORDS = 5


class RegistrationForm(FlaskForm):
    name = StringField(
        "Ім'я",
        validators=[
            DataRequired(message="Вкажіть ім'я."),
            Length(min=2, max=50, message="Ім'я має містити від 2 до 50 символів."),
        ],
    )
    email = EmailField(
        "Електронна пошта",
        validators=[
            DataRequired(message="Вкажіть адресу електронної пошти."),
            Email(message="Введіть коректну адресу електронної пошти."),
        ],
    )
    event_type = SelectField(
        "Тип заходу",
        choices=EVENT_TYPES,
        validators=[DataRequired(message="Оберіть тип заходу зі списку.")],
    )
    message = TextAreaField(
        "Повідомлення",
        validators=[DataRequired(message="Напишіть кілька слів про свої очікування.")],
        render_kw={"rows": 5},
    )

    # --- кастомні валідатори: WTForms автоматично викликає validate_<поле> ---
    def validate_name(self, field):
        if not NAME_RE.fullmatch(field.data.strip()):
            raise ValidationError(
                "Ім'я може містити лише літери, пробіли, апостроф і дефіс (без цифр та спецсимволів)."
            )

    def validate_message(self, field):
        if len(field.data.split()) < MIN_WORDS:
            raise ValidationError(f"Повідомлення має містити щонайменше {MIN_WORDS} слів.")
