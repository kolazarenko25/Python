"""Модель товару."""

from dataclasses import dataclass


@dataclass
class Product:
    """Описує товар у магазині."""
    name: str
    price: float
    quantity: int = 1

    def total(self) -> float:
        """Повертає вартість усієї кількості товару."""
        return self.price * self.quantity
