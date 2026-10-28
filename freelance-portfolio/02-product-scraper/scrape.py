"""Scrape a paginated product catalogue into CSV + Excel.

Targets https://books.toscrape.com (a public practice site built for scraping).
Usage:
    python scrape.py --pages 3                  # live
    python scrape.py --fixture fixtures/page.html   # offline demo
"""
import argparse
import time
from pathlib import Path
from urllib.parse import urljoin

import pandas as pd
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://books.toscrape.com/catalogue/page-{}.html"
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
HEADERS = {"User-Agent": "Mozilla/5.0 (portfolio demo scraper)"}


def session() -> requests.Session:
    s = requests.Session()
    retry = Retry(total=3, backoff_factor=1, status_forcelist=(429, 500, 502, 503, 504))
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers.update(HEADERS)
    return s


def parse_page(html: str, page_url: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for card in soup.select("article.product_pod"):
        link = card.select_one("h3 a")
        price = card.select_one(".price_color").get_text(strip=True)
        rating_cls = card.select_one("p.star-rating")["class"]
        rows.append({
            "title": link["title"],
            "price_gbp": float(price.lstrip("£Â")),
            "rating": next((RATINGS[c] for c in rating_cls if c in RATINGS), None),
            "in_stock": "In stock" in card.select_one(".availability").get_text(),
            "url": urljoin(page_url, link["href"]),
        })
    return rows


def scrape_live(pages: int, delay: float) -> list[dict]:
    s, rows = session(), []
    for n in range(1, pages + 1):
        url = BASE.format(n)
        resp = s.get(url, timeout=15)
        if resp.status_code == 404:
            break
        resp.raise_for_status()
        rows += parse_page(resp.text, url)
        print(f"page {n}: {len(rows)} products so far")
        time.sleep(delay)  # be polite
    return rows


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=2)
    ap.add_argument("--delay", type=float, default=1.0)
    ap.add_argument("--fixture", help="parse a saved HTML file instead of fetching")
    ap.add_argument("--out", default="output/products")
    args = ap.parse_args()

    if args.fixture:
        rows = parse_page(Path(args.fixture).read_text(encoding="utf-8"), BASE.format(1))
    else:
        rows = scrape_live(args.pages, args.delay)

    df = pd.DataFrame(rows).drop_duplicates(subset="url")
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(f"{args.out}.csv", index=False)
    df.to_excel(f"{args.out}.xlsx", index=False)
    print(f"{len(df)} products -> {args.out}.csv / .xlsx")


if __name__ == "__main__":
    main()
