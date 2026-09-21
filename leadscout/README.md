# LeadScout

A single-file, no-database lead discovery agent. No paid API key required.
Separate from `leadgen/` — this does not touch or depend on it.

## What it does

For each candidate company website, it crawls a few public pages (home,
contact, about), extracts the publicly displayed business email, a phone
number if present, and social links, then appends one row per company to an
Excel file. Running it again only adds new companies — existing rows
(matched by website domain) are never duplicated.

It never scrapes LinkedIn, never bypasses robots.txt or CAPTCHAs, and never
sends email. It only reads public pages of the company's own website.

## Install

```powershell
cd leadscout
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Two ways to find companies

### 1. You already have a list (most reliable)

Put one website per line in a text file (or a `.csv` with a `website`/`url`/`domain` column):

```
acme-software.com
https://example-saas.io
brightpath-labs.com
```

Run:

```powershell
python leadscout.py --input domains.txt --output leads.xlsx
```

### 2. Auto-search with DuckDuckGo (no API key, best-effort)

```powershell
python leadscout.py --query "b2b saas companies" --location "India" --count 30 --output leads.xlsx
```

This uses DuckDuckGo's public, no-JavaScript HTML results page. It is **not
an official API** — it can be rate-limited or change without notice. Use a
reasonable `--count` (20-30) and keep the default `--delay`. If a search run
fails or returns nothing, switch to `--input` with a manually compiled list
(from Google, directories, G2, Product Hunt, industry associations, etc.) —
that path has no dependency on any search engine's behavior.

## Output columns

`company_name, website, business_email, all_emails, phone, linkedin_url, other_social, pages_crawled, status, source_query, discovered_at`

`status` is `OK` when a public business email was found, otherwise
`NO_EMAIL_FOUND`. Open `leads.xlsx` directly in Excel/Google Sheets.

## Options

| Flag | Default | Meaning |
|---|---|---|
| `--query` | - | Free-text search (mutually exclusive with `--input`) |
| `--input` | - | Path to a `.txt` or `.csv` domain list |
| `--location` | '' | Appended to `--query` |
| `--count` | 25 | Max websites to discover in `--query` mode |
| `--output` | leads.xlsx | Excel file to append to |
| `--max-pages` | 4 | Public pages crawled per website |
| `--delay` | 1.0 | Seconds between requests (politeness) |

## Notes

- Respect the target site's `robots.txt`; pages it disallows are skipped.
- Phone-number extraction is best-effort and may include false positives
  (prices, dates) — verify manually before outreach.
- This tool only researches; it does not send messages. Pair it with your
  own manual outreach or the existing `leadgen/` outreach workflow if useful.
