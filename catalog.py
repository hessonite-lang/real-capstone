"""Sample DealForge product catalog."""

from decimal import Decimal

from models import Category, Product


PRODUCTS = [
    Product("Everyday T-Shirt", Category.FASHION, Decimal("799.00")),
    Product("Running Shoes", Category.FASHION, Decimal("2499.00")),
    Product("Wireless Headphones", Category.ELECTRONICS, Decimal("3499.00")),
    Product("Desk Lamp", Category.HOME, Decimal("1199.00")),
    Product("Coffee Beans", Category.GROCERY, Decimal("499.00")),
    Product("Python Programming Guide", Category.BOOKS, Decimal("899.00")),
]

