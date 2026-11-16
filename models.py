"""Core data models for DealForge."""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum


class Category(str, Enum):
    FASHION = "Fashion"
    ELECTRONICS = "Electronics"
    HOME = "Home"
    GROCERY = "Grocery"
    BOOKS = "Books"


@dataclass(frozen=True)
class Product:
    name: str
    category: Category
    price: Decimal


@dataclass
class Cart:
    items: list[tuple[Product, int]] = field(default_factory=list)

    def add(self, product: Product, quantity: int) -> None:
        if quantity < 1 or quantity > 100:
            raise ValueError("Quantity must be between 1 and 100.")
        self.items.append((product, quantity))

    @property
    def subtotal(self) -> Decimal:
        return sum((product.price * quantity for product, quantity in self.items), Decimal("0.00"))
