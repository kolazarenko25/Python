from datetime import date

from django.contrib import messages
from django.shortcuts import redirect, render

from .forms import RegistrationForm

# Демонстраційні дані (у реальному проєкті — модель і база даних).
EVENTS = [
    {
        "title": "Python для початківців",
        "date": date(2026, 11, 12),
        "place": "Київ, КПІ ім. Ігоря Сікорського",
        "seats": 30,
        "description": "Вступний воркшоп: встановлення середовища, змінні, цикли, функції та перші власні скрипти під керівництвом ментора.",
    },
    {
        "title": "Веброзробка на Django",
        "date": date(2026, 11, 26),
        "place": "Онлайн",
        "seats": None,
        "description": "Лекція про архітектуру MVT, маршрутизацію, шаблони та форми: від порожнього проєкту до робочого застосунку за одне заняття.",
    },
    {
        "title": "Конференція PyUA Autumn",
        "date": date(2026, 12, 5),
        "place": "Львів, Дім Футболу",
        "seats": 150,
        "description": "Одноденна конференція зі спільнотою Python-розробників України: доповіді про Flask, асинхронність, тестування та DevOps.",
    },
]


def home(request):
    context = {
        "site_title": "Реєстрація на події",       # рядок
        "events_count": len(EVENTS),                # число
        "upcoming": EVENTS[:2],                     # список
    }
    return render(request, "events/home.html", context)


def event_list(request):
    context = {
        "page_title": "Усі заходи",
        "total": len(EVENTS),
        "events": EVENTS,
    }
    return render(request, "events/event_list.html", context)


def register(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            messages.success(request, f"Дякуємо, {name}! Вашу заявку прийнято.")
            return redirect("events:register")   # PRG: запобігає повторній відправці
        # невалідна форма повертається з помилками та збереженим введенням
    else:
        form = RegistrationForm()
    return render(request, "events/register.html", {"form": form})
