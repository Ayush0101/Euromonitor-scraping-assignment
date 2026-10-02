import argparse
import csv
import json
import re
import unicodedata
from datetime import datetime, timezone

from curl_cffi import requests


BASE_URL = "https://www.cellarbrations.com.au"

CATEGORY_URL = (
    f"{BASE_URL}/sm/delivery/rsid/144981/"
    "categories/spirits/whisky-id-Whisky_Food"
)

PRODUCT_API = "https://storefrontgateway.cellarbrations.com.au"
TIMEOUT = 30

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ",
    "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
    "Referer": BASE_URL + "/",
}


# Remove HTML tags and collapse whitespace to a readable plain-text string.
def clean(value: str) -> str:
    return " ".join(
        re.sub(r"<[^>]+>", " ", value or "").split()
    )


# Convert a product name or text into a URL-friendly slug.
def slugify(value: str) -> str:
    value = (
        unicodedata.normalize("NFKD", value)
        .encode("ascii", "ignore")
        .decode("ascii")
    )
    return re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")


# Build the public product URL using a slugified name and product ID.
def build_product_url(product_name: str, product_id: str) -> str:
    return (
        f"{BASE_URL}/sm/delivery/rsid/144981/product/"
        f"{slugify(product_name)}-id-{product_id}"
    )


# Pull the storefront's preloaded JSON state from the page HTML.
def extract_preloaded_state(html: str) -> dict:
    match = re.search(
        r"window\.__PRELOADED_STATE__\s*=\s*(\{.*?\})\s*;",
        html,
        re.DOTALL,
    )

    if not match:
        raise RuntimeError("window.__PRELOADED_STATE__ not found")

    return json.loads(match.group(1))


# Scrape all whisky products across paginated category pages and collect details.
def scrape() -> list[dict]:
    session = requests.Session(impersonate="chrome")
    session.headers.update(HEADERS)

    rows = []
    page = 1
    skip = 0
    items_per_page = 30

    while True:
        page_url = (
            CATEGORY_URL
            if page == 1
            else f"{CATEGORY_URL}?page={page}&skip={skip}"
        )

        response = session.get(page_url, timeout=TIMEOUT)
        response.raise_for_status()

        state = extract_preloaded_state(response.text)
        search = state.get("search", {})
        products = search.get("products", {})

        product_ids = products.get("category", [])
        product_dictionary = search.get("productCardDictionary", {})

        if not product_ids:
            break

        pagination = search.get("pagination", {}).get("category", {})
        total_items = pagination.get("totalItems", 0)

        for product_id in product_ids:
            product = product_dictionary.get(str(product_id))

            if not product:
                continue

            sku = product.get("sku", str(product_id))

            product_response = session.get(
                f"{PRODUCT_API}/api/stores/144981/products/{sku}",
                timeout=TIMEOUT,
            )
            product_response.raise_for_status()

            full_product = product_response.json()

            units_of_size = full_product.get("unitsOfSize") or {}

            product_name = full_product.get(
                "name",
                product.get("name", ""),
            )

            rows.append({
                "product_name": product_name,
                "product_id": sku,
                "image": json.dumps(
                    full_product.get(
                        "primaryImage",
                        product.get("image", {}),
                    ),
                    ensure_ascii=False,
                ),
                "url": build_product_url(product_name, sku),
                "price": full_product.get(
                    "price",
                    product.get("price", ""),
                ),
                "scraped_at": datetime.now(timezone.utc).isoformat(),
                "description": clean(
                    full_product.get(
                        "description",
                        product.get("description", ""),
                    )
                ),
                "measuring_unit": units_of_size.get(
                    "abbreviation",
                    "",
                ),
                "units": units_of_size.get(
                    "size",
                    "",
                ),
            })

        if len(rows) >= total_items:
            break

        skip += items_per_page
        page += 1

    return rows


def write_csv(rows: list[dict], output_path: str) -> None:
    fields = [
        "product_name",
        "product_id",
        "image",
        "url",
        "price",
        "scraped_at",
        "description",
        "measuring_unit",
        "units",
    ]

    with open(output_path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scrape Cellarbrations whisky products."
    )
    parser.add_argument(
        "--output",
        default="data/cellarbrations_whisky.csv",
        help="Output CSV path.",
    )

    args = parser.parse_args()

    write_csv(scrape(), args.output)


if __name__ == "__main__":
    main()