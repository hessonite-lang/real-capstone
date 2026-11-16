# DealForge

**CP-014 · Live Product Price Comparison**  
Intermediate · E-Commerce and Retail

DealForge is a Python terminal application that compares live product listings from Google Shopping for India. Add items to a cart, search current listings, and see the three lowest listed prices for each product.

## Requirements

- Python 3.10 or later
- A SerpApi account and API key for live search
- Internet connection

## Add your API key

Open the `.env` file in this project folder and replace the placeholder on the `SERPAPI_KEY=` line:

```text
SERPAPI_KEY=paste_your_key_here
```

Save the file. The `.env` file is excluded from version control so the key is not included in project commits. Do not share the key publicly.

## Run the project

Open a terminal in this project folder and run:

```bash
python3 main.py
```

Use the numbered menu to browse products, build your cart, compare live deals, or search for any product. Choose **Find best live deals for cart** to show up to three cheapest current listings for each item. Choose **Search any product online** to compare a product that is not in the sample catalog.

Press **Ctrl+C** or choose **0** to exit.

## How it works

- The terminal interface and cart are handled in Python.
- DealForge sends the product search to SerpApi's Google Shopping results and sorts listings by the returned price.
- Search results include the store, listed price, product title, and link.
- The same search is made separately for each distinct cart line.

Prices and stock can change; confirm the final details on the retailer's page. API usage limits depend on your SerpApi account.

## Project files

```text
main.py       Terminal interface and live shopping search
catalog.py    Sample product catalog
models.py     Product, category, and cart models
.env          Private SerpApi key configuration
.gitignore    Excludes the API key and Python cache files
```
