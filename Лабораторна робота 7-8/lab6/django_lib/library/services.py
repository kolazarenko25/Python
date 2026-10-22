"""Сервісний шар: побічні ефекти (надсилання пошти) винесено окремо від моделей."""
from django.conf import settings
from django.core.mail import send_mail


def notify_overdue(loan):
    """Надсилає читачу лист про прострочену книгу.

    Повертає True, якщо лист надіслано, і False, якщо видача не прострочена.
    """
    if not loan.is_overdue():
        return False
    send_mail(
        subject=f"Прострочення: {loan.book.title}",
        message=(
            f"Шановний(а) {loan.reader.full_name}, термін повернення книги "
            f"«{loan.book.title}» минув {loan.due_date:%d.%m.%Y}."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[loan.reader.email],
    )
    return True
