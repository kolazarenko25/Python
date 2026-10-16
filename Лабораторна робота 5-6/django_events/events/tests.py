"""Автотести: валідація форми, flash-повідомлення та емпірична перевірка CSRF (завдання 4–6)."""
import re

from django.test import Client, TestCase
from django.urls import reverse

VALID = {
    "name": "Олена Петренко",
    "email": "olena@example.com",
    "event_type": "workshop",
    "message": "Хочу навчитися писати веб-застосунки на Python.",
}


class PageTests(TestCase):
    def test_pages_open(self):
        for name in ("events:home", "events:list", "events:register"):
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, name)
            self.assertContains(response, 'lang="uk"')
            self.assertContains(response, "Заходи")  # навігація з base.html


class RegistrationFormTests(TestCase):
    url = None

    def setUp(self):
        self.url = reverse("events:register")

    def test_get_shows_empty_form_with_csrf_token(self):
        response = self.client.get(self.url)
        self.assertContains(response, "csrfmiddlewaretoken")
        self.assertFalse(response.context["form"].is_bound)

    def test_valid_post_redirects_and_flashes(self):
        response = self.client.post(self.url, VALID, follow=True)
        self.assertRedirects(response, self.url)
        self.assertContains(response, "Дякуємо, Олена Петренко!")

    def test_digits_in_name_rejected(self):
        response = self.client.post(self.url, {**VALID, "name": "Ол3на"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("name", response.context["form"].errors)
        self.assertContains(response, 'value="Ол3на"')  # введення збережено

    def test_short_message_rejected(self):
        response = self.client.post(self.url, {**VALID, "message": "Привіт усім"})
        self.assertIn("message", response.context["form"].errors)

    def test_invalid_email_and_empty_choice_rejected(self):
        response = self.client.post(self.url, {**VALID, "email": "oops", "event_type": ""})
        errors = response.context["form"].errors
        self.assertIn("email", errors)
        self.assertIn("event_type", errors)


class CsrfTests(TestCase):
    """Звичайний тестовий клієнт CSRF не перевіряє — вмикаємо перевірку явно."""

    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
        self.url = reverse("events:register")

    def test_post_without_token_is_forbidden(self):
        response = self.client.post(self.url, VALID)
        self.assertEqual(response.status_code, 403)

    def test_post_with_wrong_token_is_forbidden(self):
        self.client.get(self.url)
        response = self.client.post(self.url, {**VALID, "csrfmiddlewaretoken": "x" * 64})
        self.assertEqual(response.status_code, 403)

    def test_post_with_valid_token_is_accepted(self):
        page = self.client.get(self.url).content.decode()
        token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', page).group(1)
        response = self.client.post(self.url, {**VALID, "csrfmiddlewaretoken": token})
        self.assertEqual(response.status_code, 302)
