"""LeadScout: a single-file, no-database lead discovery agent.

Two modes, no paid API key required:
  1. --input domains.txt   Crawl a list of company websites you already have.
  2. --query "b2b saas"    Best-effort discovery via DuckDuckGo's public,
                            no-JavaScript HTML results page.

For every candidate company website, it crawls a handful of public pages
(home, contact, about), extracts the publicly displayed business email,
phone number, and social links, and appends the result to an Excel file.
Runs are safe to repeat: rows are de-duplicated by website domain.

This is a local script. It does not scrape LinkedIn, does not bypass
robots.txt, does not use CAPTCHA bypass, and does not send email.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
import time
from dataclasses import dataclass
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, quote_plus, unquote, urljoin, urlparse
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser

USER_AGENT = "LeadScout/1.0 (+local public-business research)"
# DuckDuckGo's HTML endpoint rejects non-browser user agents; this is only used for search requests.
SEARCH_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
EMAIL_RE = re.compile(r"(?i)\b[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9-]+(?:\.[a-z0-9-]+)+\b")
PHONE_RE = re.compile(r"\+?\d[\d\-.\s()]{8,16}\d")
CONTACT_PATHS = ("contact", "about", "about-us", "support", "team")
# Directories, social networks, and marketplaces are not the target company's own site.
SKIP_DOMAIN_PARTS = (
    "wikipedia.org", "youtube.com", "facebook.com", "instagram.com", "linkedin.com",
    "twitter.com", "x.com", "tiktok.com", "amazon.", "reddit.com", "quora.com",
    "medium.com", "crunchbase.com", "g2.com", "capterra.com", "glassdoor.", "pinterest.com",
    "f6s.com", "builtin.com", "softwaresuggest.com", "getapp.com", "trustradius.com",
    "clutch.co", "goodfirms.co", "producthunt.com", "angel.co", "wellfound.com",
    "indeed.com", "glassdoor.com", "saasdatabase.net", "owler.com", "zoominfo.com",
    "apollo.io", "tracxn.com", "inc42.com", "yourstory.com", "forbes.com", "techcrunch.com",
)
# Automatically widen a single base query into several phrasings that tend to surface
# individual company sites rather than directories/listicles about a category.
QUERY_VARIATIONS = (
    "{query}",
    "{query} official website",
    "{query} pricing contact",
    "{query} \"request a demo\"",
)
FREE_MAIL_HOSTS = {"gmail.com", "yahoo.com", "hotmail.com", "outlook.com", "proton.me", "icloud.com", "aol.com"}
BUSINESS_PREFIXES = ("info", "hello", "contact", "sales", "support", "press", "media", "careers", "help", "team", "enquir", "admin", "office", "service")
# Error-tracking SDKs, CDNs, and known AI-agent canary domains that leak into page HTML/JS but are not business contacts.
NOISE_HOST_PARTS = ("sentry.io", "sentry-cdn.com", "ingest.", "bugsnag.com", "rollbar.com", "anthropic.com", "openai.com", "jsdelivr.net", "unpkg.com", "googleapis.com", "gstatic.com", "cloudflare.com", "w3.org")
PLACEHOLDER_MARKERS = ("example.com", "yourdomain.com", "domain.com", "test.com", "yourname", "firstname", "lastname", "name@domain", "loremipsum", "@email.com")
SOCIAL_PROOF_KEYWORDS = ("review", "testimonial", "rating", "rated", "customer feedback", "trusted by", "case study", "case studies", "our clients", "our customers")
FIELDS = [
    "company_name", "website", "business_email", "all_emails", "phone",
    "linkedin_url", "other_social", "social_proof_note", "pages_crawled", "status", "source_query", "discovered_at",
]


class _PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title: list[str] = []
        self.text: list[str] = []
        self.links: list[str] = []
        self.mailto: list[str] = []
        self._in_title = False
        self._title_done = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if tag == "title" and not self._title_done:
            self._in_title = True
        if tag == "a" and attributes.get("href"):
            href = attributes["href"].strip()
            self.links.append(href)
            if href.lower().startswith("mailto:"):
                self.mailto.append(href[7:].split("?", 1)[0])

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
            self._title_done = True

    def handle_data(self, data: str) -> None:
        value = " ".join(data.split())
        if value:
            self.text.append(value)
            if self._in_title:
                self.title.append(value)


class _ResultParser(HTMLParser):
    """Parses DuckDuckGo's no-JS HTML results page for result links."""

    def __init__(self) -> None:
        super().__init__()
        self.results: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attributes = dict(attrs)
        if "result__a" in (attributes.get("class") or "") and attributes.get("href"):
            self.results.append(attributes["href"])


def _looks_like_real_email(email: str) -> bool:
    # Filters version strings / asset paths like "pkg@1.0.28" that pass the email regex.
    host = email.rsplit("@", 1)[-1]
    last_label = host.rsplit(".", 1)[-1]
    return not last_label.isdigit() and len(last_label) >= 2


def _looks_like_real_email(email: str) -> bool:
    local, _, host = email.partition("@")
    if not host:
        return False
    last_label = host.rsplit(".", 1)[-1]
    if last_label.isdigit() or len(last_label) < 2:
        return False
    # Error-tracking/CDN/AI-agent-canary domains found embedded in page JS, not real business contacts.
    if any(part in host for part in NOISE_HOST_PARTS):
        return False
    # Template placeholders left in unfilled forms (e.g. firstnamelastname@email.com).
    if any(marker in email for marker in PLACEHOLDER_MARKERS):
        return False
    # Personal free-mail addresses are excluded unless they use a recognizable business prefix.
    if host in FREE_MAIL_HOSTS and not local.startswith(BUSINESS_PREFIXES):
        return False
    # Long hex strings as the local part are almost always tracking IDs/DSN keys, not mailboxes.
    if re.fullmatch(r"[0-9a-f]{16,}", local):
        return False
    return True


def _clean_company_name(title: str, domain: str) -> str:
    domain_fallback = domain.split(".")[0].replace("-", " ").replace("_", " ").title()
    # Long marketing taglines (e.g. "X: Makeup, Skincare... | Brand Name") read as spammy in outreach; prefer a clean domain-derived name instead.
    if not title or len(title) > 40 or "|" in title or ":" in title:
        return domain_fallback
    return title


def normalize_domain(value: str) -> str:
    raw = (value or "").strip()
    parsed = urlparse(raw if "://" in raw else f"https://{raw}")
    host = (parsed.hostname or "").lower().rstrip(".")
    if host.startswith("www."):
        host = host[4:]
    if not host or parsed.username or parsed.password:
        return ""
    return host


def canonical_url(value: str) -> str:
    domain = normalize_domain(value)
    return f"https://{domain}" if domain else ""


def _public_url(value: str, base: str) -> str:
    absolute = urljoin(base, value)
    parsed = urlparse(absolute)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        return ""
    return absolute.split("#", 1)[0]


def _robots_allowed(url: str) -> bool:
    parsed = urlparse(url)
    parser = RobotFileParser()
    parser.set_url(f"{parsed.scheme}://{parsed.netloc}/robots.txt")
    try:
        parser.read()
    except Exception:
        return True
    return parser.can_fetch(USER_AGENT, url)


def _fetch_html(url: str, timeout: int = 8) -> str:
    if not _robots_allowed(url):
        raise ValueError("robots.txt disallows this page")
    request = Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html"})
    with urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("content-type", "")
        raw = response.read(500_000)
    if "text/html" not in content_type.lower():
        raise ValueError("not an HTML page")
    return raw.decode("utf-8", "ignore")


def _resolve_ddg_redirect(href: str) -> str:
    if href.startswith("//"):
        href = "https:" + href
    parsed = urlparse(href)
    if "duckduckgo.com" in parsed.netloc and parsed.path.startswith("/l/"):
        target = parse_qs(parsed.query).get("uddg", [""])[0]
        return unquote(target)
    return href


def duckduckgo_search(query: str, max_results: int = 20, delay: float = 1.5) -> list[str]:
    """Best-effort discovery via DuckDuckGo's public no-JS HTML results page.

    This is not an official API and may be rate-limited or change at any time.
    For reliable, repeatable runs, prefer --input with a domain list instead.
    """
    websites: list[str] = []
    seen: set[str] = set()
    variations = [variation.format(query=query) for variation in QUERY_VARIATIONS]
    last_error: Exception | None = None
    for variation in variations:
        if len(websites) >= max_results:
            break
        offset = 0
        while len(websites) < max_results and offset < 60:
            url = f"https://html.duckduckgo.com/html/?q={quote_plus(variation)}&s={offset}"
            request = Request(url, headers={"User-Agent": SEARCH_USER_AGENT, "Accept": "text/html", "Accept-Language": "en-US,en;q=0.9"})
            html = None
            for attempt in range(3):
                try:
                    with urlopen(request, timeout=10) as response:
                        html = response.read(1_000_000).decode("utf-8", "ignore")
                    break
                except (HTTPError, URLError, TimeoutError) as exc:
                    last_error = exc
                    time.sleep(delay * (attempt + 1))
            if html is None:
                break
            parser = _ResultParser()
            parser.feed(html)
            if not parser.results:
                break
            for href in parser.results:
                target = _resolve_ddg_redirect(href)
                domain = normalize_domain(target)
                if not domain or domain in seen or any(part in domain for part in SKIP_DOMAIN_PARTS):
                    continue
                seen.add(domain)
                websites.append(f"https://{domain}")
                if len(websites) >= max_results:
                    break
            offset += 30
            time.sleep(delay)
    if not websites and last_error is not None:
        raise RuntimeError(f"DuckDuckGo search request failed: {last_error}")
    return websites


def crawl_site(website: str, max_pages: int = 4, timeout: int = 8, delay: float = 0.5) -> dict:
    root = canonical_url(website)
    if not root:
        raise ValueError("not a usable public website")
    domain = normalize_domain(root)
    pending, visited = [root], set()
    company_title = ""
    emails: set[str] = set()
    phones: set[str] = set()
    linkedin_url = ""
    other_social: set[str] = set()
    social_proof_detected = False
    pages_crawled = 0
    while pending and pages_crawled < max_pages:
        current = pending.pop(0)
        if current in visited or normalize_domain(current) != domain:
            continue
        visited.add(current)
        try:
            html = _fetch_html(current, timeout)
        except Exception:
            continue
        parser = _PageParser()
        parser.feed(html)
        pages_crawled += 1
        text = " ".join(parser.text)
        if not social_proof_detected and any(word in text.lower() for word in SOCIAL_PROOF_KEYWORDS):
            social_proof_detected = True
        if not company_title and parser.title:
            company_title = " ".join(parser.title).strip()
        for email in EMAIL_RE.findall(text) + parser.mailto:
            cleaned = email.strip().lower()
            if EMAIL_RE.fullmatch(cleaned) and _looks_like_real_email(cleaned):
                emails.add(cleaned)
        for phone in PHONE_RE.findall(text):
            digits = re.sub(r"\D", "", phone)
            if 9 <= len(digits) <= 13:
                phones.add(phone.strip())
        for href in parser.links:
            lowered = href.lower()
            if "linkedin.com/company" in lowered and not linkedin_url:
                linkedin_url = href
            elif any(site in lowered for site in ("twitter.com", "x.com", "facebook.com", "instagram.com")):
                other_social.add(href)
            target = _public_url(href, current)
            if target and normalize_domain(target) == domain and target not in visited and target not in pending:
                if any(path in target.lower() for path in CONTACT_PATHS):
                    pending.insert(0, target)
                else:
                    pending.append(target)
        if pending and delay:
            time.sleep(delay)
    if pages_crawled == 0:
        raise ValueError("no pages could be crawled (robots.txt or network)")
    business_emails = sorted(emails)
    return {
        "company_name": _clean_company_name(company_title, domain),
        "website": root,
        "business_email": business_emails[0] if business_emails else "",
        "all_emails": ", ".join(business_emails),
        "phone": sorted(phones)[0] if phones else "",
        "linkedin_url": linkedin_url,
        "other_social": ", ".join(sorted(other_social)[:2]),
        "social_proof_note": "Customer reviews, ratings, testimonials, or client mentions are visible on the site." if social_proof_detected else "",
        "pages_crawled": pages_crawled,
        "status": "OK" if business_emails else "NO_EMAIL_FOUND",
    }


def load_domain_seeds(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8-sig", errors="ignore")
    if path.suffix.lower() == ".csv":
        reader = csv.DictReader(text.splitlines())
        key = next((name for name in (reader.fieldnames or []) if name.strip().lower() in ("website", "url", "domain")), None)
        if not key:
            raise ValueError("CSV must have a website, url, or domain column")
        return [row[key].strip() for row in reader if row.get(key, "").strip()]
    return [line.strip() for line in text.splitlines() if line.strip() and not line.strip().startswith("#")]


def append_leads_to_excel(path: Path, leads: list[dict]) -> int:
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font

    if path.exists():
        workbook = load_workbook(path)
        sheet = workbook.active
        existing_domains = {
            normalize_domain(str(row[1].value)) for row in sheet.iter_rows(min_row=2) if row[1].value
        }
    else:
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Leads"
        sheet.append(FIELDS)
        for cell in sheet[1]:
            cell.font = Font(bold=True)
        sheet.freeze_panes = "A2"
        existing_domains = set()

    added = 0
    for lead in leads:
        domain = normalize_domain(lead.get("website", ""))
        if not domain or domain in existing_domains:
            continue
        existing_domains.add(domain)
        sheet.append([lead.get(field, "") for field in FIELDS])
        added += 1

    for column_cells in sheet.columns:
        length = max((len(str(cell.value)) for cell in column_cells if cell.value is not None), default=8)
        sheet.column_dimensions[column_cells[0].column_letter].width = min(48, max(10, length + 2))
    workbook.save(path)
    return added


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Simple lead discovery agent -> Excel.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--query", help="Free-text search, e.g. 'b2b saas companies'")
    source.add_argument("--input", help="Path to a .txt (one website per line) or .csv (website column) domain list")
    source.add_argument("--queries-file", help="Path to a .txt file with one query per line, to batch many niches/locations into one run")
    parser.add_argument("--location", default="", help="Optional location to append to --query / each line of --queries-file")
    parser.add_argument("--count", type=int, default=25, help="Max candidate websites to discover per query")
    parser.add_argument("--output", default="leads.xlsx", help="Excel file to append results to")
    parser.add_argument("--max-pages", type=int, default=4, help="Public pages to crawl per website")
    parser.add_argument("--delay", type=float, default=1.0, help="Politeness delay in seconds between requests")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.input:
        seeds_by_query = {f"input:{args.input}": load_domain_seeds(Path(args.input))}
    elif args.queries_file:
        raw_queries = [line.strip() for line in Path(args.queries_file).read_text(encoding="utf-8-sig").splitlines() if line.strip() and not line.strip().startswith("#")]
        seeds_by_query = {}
        for raw_query in raw_queries:
            query = f"{raw_query} {args.location}".strip() if args.location else raw_query
            print(f"Searching DuckDuckGo for: {query}")
            try:
                seeds_by_query[f"query:{query}"] = duckduckgo_search(query, args.count, args.delay)
            except RuntimeError as exc:
                print(f"  search failed: {exc}")
                seeds_by_query[f"query:{query}"] = []
    else:
        query = f"{args.query} {args.location}".strip() if args.location else args.query
        print(f"Searching DuckDuckGo for: {query}")
        try:
            seeds_by_query = {f"query:{query}": duckduckgo_search(query, args.count, args.delay)}
        except RuntimeError as exc:
            print(f"Search failed: {exc}")
            print("Tip: use --input domains.txt with a manual list of company websites instead.")
            return 1

    all_seeds = [(source_label, website) for source_label, websites in seeds_by_query.items() for website in websites]
    if not all_seeds:
        print("No candidate websites found. Try a different query, --queries-file, or use --input.")
        return 1

    print(f"Found {len(all_seeds)} candidate website(s) across {len(seeds_by_query)} quer(y/ies). Crawling public pages...")
    leads = []
    seen_domains: set[str] = set()
    for index, (source_label, website) in enumerate(all_seeds, start=1):
        domain = normalize_domain(website)
        if not domain or domain in seen_domains:
            continue
        seen_domains.add(domain)
        print(f"[{index}/{len(all_seeds)}] {website}")
        try:
            lead = crawl_site(website, max_pages=args.max_pages, delay=args.delay)
        except Exception as exc:
            print(f"  skipped: {exc}")
            continue
        lead["source_query"] = source_label
        lead["discovered_at"] = datetime.now().isoformat(timespec="seconds")
        leads.append(lead)
        print(f"  -> {lead['business_email'] or 'no public email'} | {lead['company_name']}")

    added = append_leads_to_excel(Path(args.output), leads)
    with_email = sum(1 for lead in leads if lead["business_email"])
    print(f"Saved {added} new lead(s) to {Path(args.output).resolve()} ({len(leads)} crawled, {with_email} with a public email, {len(leads) - added} already in file).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
