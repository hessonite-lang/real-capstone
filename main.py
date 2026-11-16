"""DealForge terminal interface for live product price comparison."""

import json
import os
import ssl
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from catalog import PRODUCTS
from models import Cart

ROOT = Path(__file__).resolve().parent
ENV_FILE = ROOT / ".env"
GREEN, CYAN, YELLOW, RED, RESET = "\033[92m", "\033[96m", "\033[93m", "\033[91m", "\033[0m"


def load_api_key():
    """Read SERPAPI_KEY from the environment or project-local .env file."""
    key = os.environ.get("SERPAPI_KEY", "").strip()
    if key:
        return key
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                name, value = line.split("=", 1)
                if name.strip() == "SERPAPI_KEY":
                    key = value.strip().strip("\"'")
                    if key and "PASTE_" not in key.upper() and key != "your_api_key":
                        return key
    return ""


def search_prices(query, api_key):
    params = urlencode({
        "engine": "google_shopping", "q": query, "api_key": api_key,
        "gl": "in", "hl": "en", "google_domain": "google.co.in",
    })
    request = Request(
        f"https://serpapi.com/search.json?{params}",
        headers={"User-Agent": "DealForge/1.0"},
    )
    try:
        with urlopen(request, timeout=20, context=ssl.create_default_context()) as response:
            data = json.loads(response.read().decode("utf-8"))
        if data.get("error"):
            return [], str(data["error"])
        items = data.get("shopping_results", [])
        items.sort(key=lambda item: (
            not isinstance(item.get("extracted_price"), (int, float)),
            item.get("extracted_price", float("inf"))
            if isinstance(item.get("extracted_price"), (int, float)) else float("inf"),
        ))
        return items[:3], None
    except HTTPError as error:
        try:
            data = json.loads(error.read().decode("utf-8"))
            detail = data.get("error", "Request rejected")
        except (ValueError, UnicodeDecodeError):
            detail = "Request rejected"
        return [], f"SerpApi HTTP {error.code}: {detail}"
    except URLError as error:
        return [], f"Could not connect to SerpApi: {error.reason}"
    except (TimeoutError, json.JSONDecodeError) as error:
        return [], f"Search failed: {error.__class__.__name__}"


def heading(title):
    print(f"\n{CYAN}{'─' * 64}{RESET}")
    print(f"  {title}")
    print(f"{CYAN}{'─' * 64}{RESET}")


def show_products():
    heading("PRODUCT CATALOG")
    for number, product in enumerate(PRODUCTS, 1):
        print(f"  {number}. {product.name:<30} {product.category.value:<14} ₹{product.price:,.2f}")


def show_cart(cart):
    heading("YOUR CART")
    if not cart.items:
        print("  Cart is empty. Add products from the catalog first.")
        return
    for number, (product, quantity) in enumerate(cart.items, 1):
        print(f"  {number}. {product.name} × {quantity} — ₹{product.price * quantity:,.2f}")
    print(f"\n  Cart subtotal: ₹{cart.subtotal:,.2f}")


def add_product(cart):
    show_products()
    try:
        choice = int(input("\nProduct number (0 to cancel): "))
        if choice == 0:
            return
        product = PRODUCTS[choice - 1]
        if not 1 <= choice <= len(PRODUCTS):
            raise ValueError
        quantity = int(input("Quantity (1–100): "))
        cart.add(product, quantity)
        print(f"{GREEN}Added {product.name} × {quantity}.{RESET}")
    except (ValueError, IndexError):
        print(f"{RED}Enter a valid product number and quantity.{RESET}")


def compare_product(name, api_key):
    print(f"\n{YELLOW}Searching current listings for {name}…{RESET}")
    listings, error = search_prices(name, api_key)
    if error:
        print(f"{RED}{error}{RESET}")
        return
    if not listings:
        print("No listings found for this product.")
        return
    print(f"{GREEN}Top {len(listings)} cheapest listings:{RESET}")
    for rank, item in enumerate(listings, 1):
        title = item.get("title", name)
        store = item.get("source", "Online store")
        price = item.get("price", "Price unavailable")
        link = item.get("product_link") or item.get("link") or "No product link returned"
        print(f"\n  #{rank}  {store} — {price}")
        print(f"      {title}")
        print(f"      {link}")


def compare_cart(cart, api_key):
    if not cart.items:
        print(f"{YELLOW}Add a product to your cart first.{RESET}")
        return
    if not api_key:
        print(f"{RED}SerpApi key is missing.{RESET}")
        print(f"Paste it into this project’s .env file on the SERPAPI_KEY= line, then restart DealForge.")
        return
    heading("CHEAPEST LIVE STORE PRICES")
    for product, _quantity in cart.items:
        compare_product(product.name, api_key)
    print(f"\n{YELLOW}Prices and availability can change. Confirm on the retailer page.{RESET}")


def main():
    api_key = load_api_key()
    cart = Cart()
    while True:
        print(f"\n{GREEN}╭──────────────────────────────────────────────────────────────╮")
        print("│                    DEALFORGE · CP-014                        │")
        print("│             Live product price comparison                    │")
        print("╰──────────────────────────────────────────────────────────────╯" + RESET)
        print("  1. Browse products and add to cart")
        print("  2. View cart")
        print("  3. Find best live deals for cart")
        print("  4. Search any product online")
        print("  5. Remove a cart item")
        print("  0. Exit")
        choice = input("\nChoose an option: ").strip()
        if choice == "1":
            add_product(cart)
        elif choice == "2":
            show_cart(cart)
        elif choice == "3":
            compare_cart(cart, api_key)
        elif choice == "4":
            query = input("Product to search: ").strip()
            if query:
                compare_product(query, api_key) if api_key else print(f"{RED}Add your SerpApi key to the .env file first.{RESET}")
        elif choice == "5":
            show_cart(cart)
            if cart.items:
                try:
                    number = int(input("Item number to remove (0 to cancel): "))
                    if number:
                        removed = cart.items.pop(number - 1)
                        print(f"{GREEN}Removed {removed[0].name}.{RESET}")
                except (ValueError, IndexError):
                    print(f"{RED}Choose an item number from the cart.{RESET}")
        elif choice == "0":
            print("\nThanks for using DealForge.\n")
            break
        else:
            print(f"{RED}Choose one of the listed options.{RESET}")


if __name__ == "__main__":
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print("\nDealForge closed.")
