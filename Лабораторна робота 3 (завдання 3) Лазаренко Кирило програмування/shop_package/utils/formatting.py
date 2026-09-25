"""Форматування результатів."""

from ..models import Cart


def format_money(value: float) -> str:
    """Форматує суму у гривнях."""
    return f"{value:.2f} грн"


def make_receipt(cart: Cart) -> str:
    """Створює текстовий чек."""
    lines = ["=== ЧЕК ==="]
    for item in cart.items:
        lines.append(
            f"{item.name}: {item.quantity} x {format_money(item.price)} = "
            f"{format_money(item.total())}"
        )
    lines.append(f"Разом: {format_money(cart.total_price())}")
    return "\n".join(lines)
