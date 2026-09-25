"""Модель кошика."""

from .product import Product


class Cart:
    """Зберігає товари та виконує базові розрахунки."""

    def __init__(self) -> None:
        self.items: list[Product] = []

    def add(self, product: Product) -> None:
        self.items.append(product)

    def total_items(self) -> int:
        return sum(item.quantity for item in self.items)

    def total_price(self) -> float:
        return sum(item.total() for item in self.items)
