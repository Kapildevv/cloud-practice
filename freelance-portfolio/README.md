# Freelance Portfolio — Python Data Automation

Three small, working tools that match the most common fixed-price gigs on
Fiverr and Upwork. Each one runs on bundled sample data, so a client can see
the input and the output.

```bash
pip install -r requirements.txt
```

| # | Project | Gig it sells | Demo |
|---|---------|--------------|------|
| 1 | [Invoice extractor](01-invoice-extractor) | "PDF invoices / bills to Excel" | `python make_samples.py && python extract.py samples output/invoices.xlsx` |
| 2 | [Product scraper](02-product-scraper) | "Scrape website data to CSV/Excel" | `python scrape.py --pages 3` (or `--fixture fixtures/page.html` offline) |
| 3 | [Lead cleaner](03-lead-cleaner) | "Clean, dedupe and validate contact lists" | `python make_samples.py && python clean.py samples/messy_leads.csv output/clean_leads.xlsx` |

## 1. Invoice extractor
Reads every PDF in a folder and pulls out invoice number, date, GSTIN,
subtotal, GST and grand total into one Excel workbook (with a per-vendor
summary sheet). Each row is checked: missing fields or totals that don't add
up are flagged, so nothing wrong goes out silently.

To adapt it to a client's layout, edit the regexes in `PATTERNS`. For scanned
or very irregular invoices, add OCR (`pytesseract`) or an LLM extraction step
and keep the same validation.

## 2. Product scraper
Paginated catalogue scraper with retries, backoff, a polite delay and
de-duplication. It outputs CSV and Excel. It targets books.toscrape.com, a
site built for scraping practice.

Only take scraping jobs for public data on sites whose terms allow it. Turn
down jobs that involve logins, personal data or getting around anti-bot
measures.

## 3. Lead cleaner
Takes a messy contact sheet and:
- normalises Indian phone numbers to `+91XXXXXXXXXX` and labels them mobile or landline
- lower-cases emails and checks their format
- unifies city aliases (Bombay → Mumbai, Gurgaon → Gurugram)
- merges duplicates on phone, email or name + city, keeping the most complete record

Rows with a bad phone number or email go to a separate **Needs Review** sheet
instead of being dropped.

Sample run: 8 rows in → 6 unique leads, 2 duplicates merged, 2 rows flagged.
