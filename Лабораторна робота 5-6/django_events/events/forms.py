import re

from django import forms

EVENT_TYPES = [
    ("", "— оберіть тип заходу —"),
    ("workshop", "Воркшоп"),
    ("lecture", "Лекція"),
    ("conference", "Конференція"),
]

# Літери (будь-якої абетки), окремі слова розділені пробілом, апострофом або дефісом.
NAME_RE = re.compile(r"[^\W\d_]+(?:[ '’-][^\W\d_]+)*")
MIN_WORDS = 5


class RegistrationForm(forms.Form):
    name = forms.CharField(
        label="Ім'я",
        min_length=2,
        max_length=50,
        error_messages={
            "required": "Вкажіть ім'я.",
            "min_length": "Ім'я має містити щонайменше 2 символи.",
            "max_length": "Ім'я не може бути довшим за 50 символів.",
        },
    )
    email = forms.EmailField(
        label="Електронна пошта",
        error_messages={
            "required": "Вкажіть адресу електронної пошти.",
            "invalid": "Введіть коректну адресу електронної пошти.",
        },
    )
    event_type = forms.ChoiceField(
        label="Тип заходу",
        choices=EVENT_TYPES,
        error_messages={
            "required": "Оберіть тип заходу зі списку.",
            "invalid_choice": "Оберіть один із запропонованих варіантів.",
        },
    )
    message = forms.CharField(
        label="Повідомлення",
        widget=forms.Textarea(attrs={"rows": 5}),
        error_messages={"required": "Напишіть кілька слів про свої очікування."},
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-control")

    # --- кастомні бізнес-правила (завдання 4) ---
    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not NAME_RE.fullmatch(name):
            raise forms.ValidationError(
                "Ім'я може містити лише літери, пробіли, апостроф і дефіс (без цифр та спецсимволів)."
            )
        return name

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message.split()) < MIN_WORDS:
            raise forms.ValidationError(
                f"Повідомлення має містити щонайменше {MIN_WORDS} слів."
            )
        return message
