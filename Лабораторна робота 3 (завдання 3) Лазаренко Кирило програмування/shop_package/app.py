"""Головний модуль застосунку."""

import shop_package.utils.formatting as formatting
from shop_package.models import Cart, Product


def build_demo_cart() -> Cart:
    """Створює демонстраційний кошик."""
    cart = Cart()
    cart.add(Product("Зошит", 45.50, 2))
    cart.add(Product("Ручка", 18.00, 3))
    return cart


def run_demo() -> None:
    """Запускає демонстрацію роботи пакета."""
    cart = build_demo_cart()
    print(formatting.make_receipt(cart))
    print(f"Кількість товарів: {cart.total_items()}")
    print(f"Загальна сума: {cart.total_price():.2f} грн")


if __name__ == "__main__":
    run_demo()
