"""Завдання 7 (Django): мок-тести.

Мок 1 — зовнішня залежність: надсилання пошти (django.core.mail.send_mail).
Мок 2 — внутрішня залежність: поточна дата (timezone.localdate).
"""
from datetime import date
from unittest.mock import patch

from django.conf import settings

from library.services import notify_overdue


def test_notify_overdue_sends_email(overdue_loan):
    with patch("library.services.send_mail") as mock_send:
        result = notify_overdue(overdue_loan)

    assert result is True
    mock_send.assert_called_once_with(
        subject="Прострочення: Кобзар",
        message=(
            "Шановний(а) Олена Коваль, термін повернення книги "
            f"«Кобзар» минув {overdue_loan.due_date:%d.%m.%Y}."
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=["olena@example.com"],
    )


def test_notify_overdue_skips_when_not_overdue(loan):
    loan.due_date = date(2999, 1, 1)
    with patch("library.services.send_mail") as mock_send:
        result = notify_overdue(loan)

    assert result is False
    mock_send.assert_not_called()


def test_is_overdue_with_mocked_today(loan):
    loan.due_date = date(2026, 1, 10)
    loan.returned_at = None
    with patch("library.models.timezone.localdate", return_value=date(2026, 1, 11)) as mock_today:
        assert loan.is_overdue() is True
    mock_today.assert_called_once_with()

    with patch("library.models.timezone.localdate", return_value=date(2026, 1, 10)) as mock_today:
        assert loan.is_overdue() is False  # у день дедлайну ще не прострочена
    mock_today.assert_called_once_with()
