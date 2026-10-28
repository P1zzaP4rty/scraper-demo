#!/usr/bin/env python3
"""Scrape books.toscrape.com (a public scraping sandbox) into a CSV.

Usage: python scrape.py [--pages N] [--out books.csv]
"""
import argparse
import csv
import sys
import time

import requests
from bs4 import BeautifulSoup

BASE = "https://books.toscrape.com/catalogue/page-{}.html"
RATING = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
FIELDS = ["title", "price_gbp", "rating", "in_stock", "url"]


def parse_page(html: str):
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for card in soup.select("article.product_pod"):
        link = card.select_one("h3 a")
        price = card.select_one("p.price_color")
        rating = card.select_one("p.star-rating")
        avail = card.select_one("p.instock.availability")
        text = " ".join(avail.get_text(" ", strip=True).split()) if avail else ""
        rows.append({
            "title": link["title"].strip() if link else "",
            "price_gbp": "".join(c for c in (price.get_text() if price else "") if c.isdigit() or c == "."),
            "rating": RATING.get(rating["class"][1], 0) if rating else 0,
            "in_stock": "In stock" in text,
            "url": ("https://books.toscrape.com/catalogue/" + link["href"].replace("../", "")).strip()
            if link else "",
        })
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=3)
    ap.add_argument("--out", default="books.csv")
    args = ap.parse_args()

    session = requests.Session()
    session.headers["User-Agent"] = "portfolio-demo/1.0 (+scraping sandbox)"
    all_rows, seen = [], set()

    for page in range(1, args.pages + 1):
        url = BASE.format(page)
        r = session.get(url, timeout=20)
        r.raise_for_status()
        rows = parse_page(r.text)
        fresh = [x for x in rows if x["url"] not in seen]
        seen.update(x["url"] for x in fresh)
        all_rows.extend(fresh)
        print(f"page {page}: {len(rows)} parsed, {len(fresh)} new, http {r.status_code}")
        time.sleep(0.5)

    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(all_rows)

    print(f"\nwrote {args.out}: {len(all_rows)} rows, {len(FIELDS)} columns")
    return 0 if all_rows else 1


if __name__ == "__main__":
    sys.exit(main())
