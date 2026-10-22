"""Завдання 7 (Flask): мок-тести.

Мок 1 — зовнішня залежність: HTTP-запит до Open Library (urllib.request.urlopen).
Мок 2 — внутрішня залежність: генератор випадкових чисел (random.randint).
"""
import json
from unittest.mock import MagicMock, patch

from app.services import fetch_book_info, generate_card_number

ISBN = "9789660001001"
EXPECTED_URL = f"https://openlibrary.org/api/books?bibkeys=ISBN:{ISBN}&format=json&jscmd=data"


def _fake_http_response(payload):
    response = MagicMock()
    response.read.return_value = json.dumps(payload).encode("utf-8")
    return response


def test_fetch_book_info_without_real_network():
    payload = {f"ISBN:{ISBN}": {"title": "Кобзар", "number_of_pages": 704}}
    with patch("app.services.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value = _fake_http_response(payload)
        info = fetch_book_info(ISBN)

    assert info == {"title": "Кобзар", "pages": 704}
    mock_urlopen.assert_called_once_with(EXPECTED_URL, timeout=5)


def test_fetch_book_info_unknown_isbn_returns_none():
    with patch("app.services.urlopen") as mock_urlopen:
        mock_urlopen.return_value.__enter__.return_value = _fake_http_response({})
        info = fetch_book_info(ISBN)

    assert info is None
    mock_urlopen.assert_called_once_with(EXPECTED_URL, timeout=5)


def test_generate_card_number_with_mocked_random():
    with patch("app.services.random.randint", return_value=123456) as mock_randint:
        number = generate_card_number()

    assert number == "LIB-123456"
    mock_randint.assert_called_once_with(100000, 999999)
