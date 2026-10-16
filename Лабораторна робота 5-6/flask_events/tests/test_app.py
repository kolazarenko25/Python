"""Автотести: сторінки, валідація, flash та емпірична перевірка CSRF (завдання 4–6).
Запуск: python -m unittest discover -v
"""
import re
import unittest

from app import create_app

VALID = {
    "name": "Олена Петренко",
    "email": "olena@example.com",
    "event_type": "workshop",
    "message": "Хочу навчитися писати веб-застосунки на Python.",
}


class BaseCase(unittest.TestCase):
    def setUp(self):
        # CSRF залишається УВІМКНЕНИМ (WTF_CSRF_ENABLED не вимикаємо)
        self.app = create_app({"TESTING": True, "SECRET_KEY": "test-key"})
        self.client = self.app.test_client()

    def token(self):
        html = self.client.get("/register").get_data(as_text=True)
        return re.search(r'name="csrf_token"[^>]*value="([^"]+)"', html).group(1)


class PageTests(BaseCase):
    def test_pages_open(self):
        for url in ("/", "/events", "/register"):
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200, url)
            html = response.get_data(as_text=True)
            self.assertIn('lang="uk"', html)
            self.assertIn("Заходи", html)  # навігація з base.html


class FormTests(BaseCase):
    def post(self, **overrides):
        data = {**VALID, "csrf_token": self.token(), **overrides}
        return self.client.post("/register", data)

    def test_get_contains_csrf_field(self):
        html = self.client.get("/register").get_data(as_text=True)
        self.assertIn('name="csrf_token"', html)

    def test_valid_post_redirects_and_flashes(self):
        response = self.post()
        self.assertEqual(response.status_code, 302)
        page = self.client.get("/register").get_data(as_text=True)
        self.assertIn("Дякуємо, Олена Петренко!", page)

    def test_digits_in_name_rejected(self):
        response = self.post(name="Ол3на")
        html = response.get_data(as_text=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn("без цифр", html)
        self.assertIn('value="Ол3на"', html)  # введення збережено

    def test_short_message_rejected(self):
        html = self.post(message="Привіт усім").get_data(as_text=True)
        self.assertIn("щонайменше 5 слів", html)

    def test_invalid_email_and_empty_choice_rejected(self):
        html = self.post(email="oops", event_type="").get_data(as_text=True)
        self.assertIn("коректну адресу", html)
        self.assertIn("Оберіть тип заходу", html)


class CsrfTests(BaseCase):
    def test_post_without_token_is_rejected(self):
        response = self.client.post("/register", VALID)
        self.assertEqual(response.status_code, 400)
        self.assertIn("CSRF", response.get_data(as_text=True))

    def test_post_with_wrong_token_is_rejected(self):
        self.client.get("/register")
        response = self.client.post("/register", {**VALID, "csrf_token": "forged"})
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
