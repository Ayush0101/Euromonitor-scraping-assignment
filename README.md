# Euromonitor Data Engineer Scraping Test

Python scrapers developed for the two websites provided as part of the **Euromonitor Data Engineer Scraping Test**.

The project contains scrapers for:

- **Glossier**
- **Cellarbrations**

---

## Requirements

- Python 3.10+
- Internet connection

### Install Dependencies

Install the required Python packages using:

```bash
pip install -r requirements.txt
Project Structure
.
├── scrape_glossier.py
├── scrape_cellarbrations.py
├── requirements.txt
├── notes.txt
└── data/

The generated CSV files are stored in the data/ directory.

1. Glossier Scraper

The Glossier scraper collects products from the Shop All collection for the selected market.

To run the Scraper :

India
python scrape_glossier.py --locale in

US
python scrape_glossier.py --locale us

India variants
python scrape_glossier.py --locale in --variants

US variants
python scrape_glossier.py --locale us --variants


The scraper collects the following fields:

Product name
Product ID
Image
Product URL
Price
Description
Scraped timestamp


The Glossier scraper uses the site's public Shopify JSON endpoints, so browser automation is not required.


2. Cellarbrations Scraper

The Cellarbrations scraper targets the Whisky category for store 144981.

Run the Scraper
python scrape_cellarbrations.py


The scraper handles pagination automatically and collects all products available in the category.

Data Collected

The output contains:

Product name
Product ID
Image
Product URL
Price
Scraped timestamp
Description
Measuring unit
Units

The scraper:

Requests the category page.
Extracts the __PRELOADED_STATE__ data from the response.
Uses this data to discover the products and their SKUs.
Handles pagination to collect all products in the category.
Retrieves additional product details using the site's storefront API and SKU.
Extracts the required product information.
Writes the results to a CSV file in the data/ directory.
HTTP and Browser Rendering

Notes

Additional implementation details, assumptions, browser-rendering analysis, trade-offs, and AI usage are documented in:

notes.txt