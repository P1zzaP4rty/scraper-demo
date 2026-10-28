# Scraper demo — paginated site → clean CSV

Public scraping sandbox target, real working code, committed output. This is the
proof artifact for a Upwork portfolio: a buyer can run it and diff the CSV.

## Input

`https://books.toscrape.com/catalogue/page-1.html` (pagination, 20 items/page)

## Output

`books.csv` — one row per book, 5 columns:

```
title,price_gbp,rating,in_stock,url
A Light in the Attic,51.77,3,True,https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html
Tipping the Velvet,53.74,1,True,https://books.toscrape.com/catalogue/tipping-the-velvet_999/index.html
Soumission,50.10,1,True,https://books.toscrape.com/catalogue/soumission_998/index.html
```

`rating` is normalised from the CSS class to an integer 1–5. `price_gbp` is a
float, digits parsed out of the currency string. `url` is absolute.

## Run

```bash
pip install requests beautifulsoup4
python scrape.py --pages 3 --out books.csv
```

Verified run (`run.log`):

```
page 1: 20 parsed, 20 new, http 200
page 2: 20 parsed, 20 new, http 200
page 3: 20 parsed, 20 new, http 200

wrote books.csv: 60 rows, 5 columns
```

## What it handles

- pagination (`--pages N`), 0.5s delay between requests
- dedupe by URL across pages, so a site that repeats items can't double-count
- explicit User-Agent, timeouts, `raise_for_status` — fails loudly instead of
  writing a half-empty file
- exit code 1 when zero rows parsed, so a cron job can detect breakage

## What it does not handle (said out loud, not hidden)

- JS-rendered pages (this target is server-rendered; Playwright is the swap for
  those — different script)
- logins, captchas, proxy rotation
- sites whose terms of service forbid scraping. Check before scraping; this demo
  target is a sandbox built for the purpose.
