"""Сервіси з зовнішніми/побічними залежностями (їх ми підміняємо моками у тестах)."""
import json
import random
from urllib.request import urlopen


def fetch_book_info(isbn):
    """Запит до відкритого API Open Library. Повертає {'title', 'pages'} або None."""
    url = f"https://openlibrary.org/api/books?bibkeys=ISBN:{isbn}&format=json&jscmd=data"
    with urlopen(url, timeout=5) as response:
        payload = json.load(response)
    info = payload.get(f"ISBN:{isbn}")
    if not info:
        return None
    return {"title": info.get("title"), "pages": info.get("number_of_pages")}


def generate_card_number():
    """Номер читацького квитка вигляду LIB-123456."""
    return f"LIB-{random.randint(100000, 999999)}"
