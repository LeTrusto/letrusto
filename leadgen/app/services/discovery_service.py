from dataclasses import dataclass
from html.parser import HTMLParser
import os
import re
import time
import logging
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from urllib.robotparser import RobotFileParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
import json

from .lead_service import create_lead, update_lead

USER_AGENT = 'LeTrustoLeadgen/1.0 (+local public-business research)'
DEFAULT_MAX_PAGES = 6
EMAIL_RE = re.compile(r"(?i)\b[a-z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-z0-9-]+(?:\.[a-z0-9-]+)+\b")
BUSINESS_PREFIXES = ('info', 'hello', 'contact', 'sales', 'support', 'orders', 'enquiries', 'business', 'shop', 'help')
BLOCKED_HOST_PARTS = ('facebook.com', 'instagram.com', 'linkedin.com', 'twitter.com', 'x.com', 'youtube.com', 'tiktok.com')
PRIORITY_PATHS = ('contact', 'about', 'review', 'testimonial', 'product', 'shop', 'faq', 'return', 'shipping')
SEARCH_QUERY_VARIATIONS = (
    '{country} {niche} companies',
    '{country} {niche} businesses official website',
    '{country} {niche} SaaS company',
    '{country} {niche} company contact',
)
SEARCH_BLOCKED_TERMS = ('wikipedia', 'jobs', 'careers', 'news', 'blog', 'marketplace')
logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class DiscoveryCandidate:
    website: str
    source: str
    source_url: str
    business_name: str = ''
    title: str = ''
    snippet: str = ''
    country: str = ''


class SearchProvider:
    def search_businesses(self, query: str, country: str, limit: int, page: int = 1) -> list[DiscoveryCandidate]:
        raise NotImplementedError


class SearchProviderError(RuntimeError):
    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class SearchProviderConfigurationError(SearchProviderError, ValueError):
    pass


class SearchProviderAuthenticationError(SearchProviderError):
    pass


class SearchProviderRateLimitError(SearchProviderError):
    pass


class SearchProviderResponseError(SearchProviderError):
    pass


def generate_search_queries(country: str, niche: str) -> list[str]:
    country = ' '.join((country or '').split())
    niche = ' '.join((niche or '').split())
    if not country or not niche:
        raise ValueError('country and niche are required for automated discovery')
    return list(dict.fromkeys(template.format(country=country, niche=niche) for template in SEARCH_QUERY_VARIATIONS))


def _search_candidate_allowed(url: str, title: str = '', snippet: str = '') -> bool:
    domain = normalize_domain(url)
    if not domain:
        return False
    parsed = urlparse(url if '://' in url else f'https://{url}')
    haystack = f'{domain} {parsed.path} {title} {snippet}'.lower()
    return not any(term in haystack for term in SEARCH_BLOCKED_TERMS)


class SerpApiSearchProvider(SearchProvider):
    def __init__(self, api_key: str, endpoint: str | None = None, delay_seconds: float = 1.0, max_pages: int = 2):
        if not api_key:
            raise SearchProviderConfigurationError('LEADGEN_SEARCH_API_KEY is required for SerpApi discovery.')
        self.api_key = api_key
        self.endpoint = endpoint or 'https://serpapi.com/search.json'
        self.delay_seconds = max(0.0, delay_seconds)
        self.max_pages = max(1, min(max_pages, 5))
        self.calls = 0
        self.last_http_status = None

    def search_businesses(self, query: str, country: str, limit: int, page: int = 1) -> list[DiscoveryCandidate]:
        if page < 1 or page > self.max_pages:
            return []
        if self.calls:
            time.sleep(self.delay_seconds)
        params = urlencode({'engine': 'google', 'q': query, 'api_key': self.api_key, 'num': min(max(limit, 1), 20), 'start': (page - 1) * 10})
        request = Request(f'{self.endpoint}?{params}', headers={'User-Agent': USER_AGENT, 'Accept': 'application/json'})
        self.calls += 1
        logger.info('search provider request started; provider=SerpApi query=%s country=%s page=%s limit=%s', query, country, page, limit)
        try:
            with urlopen(request, timeout=12) as response:
                self.last_http_status = getattr(response, 'status', 200)
                logger.info('search provider response; provider=SerpApi status=%s', self.last_http_status)
                payload = json.loads(response.read(1_000_000).decode('utf-8'))
        except HTTPError as exc:
            self.last_http_status = exc.code
            logger.info('search provider response; provider=SerpApi status=%s', exc.code)
            if exc.code == 401 or exc.code == 403:
                raise SearchProviderAuthenticationError('SerpApi authentication failed.', exc.code) from exc
            if exc.code == 429:
                raise SearchProviderRateLimitError('SerpApi rate limit reached.', exc.code) from exc
            raise SearchProviderError(f'SerpApi request failed with HTTP {exc.code}.', exc.code) from exc
        except (URLError, TimeoutError) as exc:
            raise SearchProviderError('SerpApi request failed before receiving a response.') from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise SearchProviderResponseError('Search provider returned an invalid response.') from exc
        if not isinstance(payload, dict):
            raise SearchProviderResponseError('Search provider returned an invalid response.', self.last_http_status)
        if payload.get('error'):
            message = str(payload['error']).lower()
            if 'api key' in message or 'auth' in message or 'invalid key' in message:
                raise SearchProviderAuthenticationError('SerpApi authentication failed.', self.last_http_status)
            if 'rate' in message or 'limit' in message:
                raise SearchProviderRateLimitError('SerpApi rate limit reached.', self.last_http_status)
            raise SearchProviderError('SerpApi returned an error response.', self.last_http_status)
        organic_results = payload.get('organic_results')
        if organic_results is None or not isinstance(organic_results, list):
            raise SearchProviderResponseError('Search provider returned an invalid response.', self.last_http_status)
        candidates = []
        for item in organic_results:
            if not isinstance(item, dict):
                continue
            website = item.get('link', '')
            title = str(item.get('title', ''))
            snippet = str(item.get('snippet', ''))
            if not _search_candidate_allowed(website, title, snippet):
                continue
            candidates.append(DiscoveryCandidate(canonical_url(website), 'SEARCH_SERPAPI', website, str(item.get('source', '') or title), title, snippet, country))
        logger.info('search provider result count; provider=SerpApi results=%s candidates=%s', len(organic_results), len(candidates))
        return candidates


def configured_search_provider() -> SearchProvider | None:
    provider_name = os.getenv('LEADGEN_SEARCH_PROVIDER', '').strip().lower()
    if not provider_name:
        return None
    if provider_name != 'serpapi':
        raise SearchProviderConfigurationError(f'Unsupported LEADGEN_SEARCH_PROVIDER: {provider_name}. Supported providers: serpapi.')
    return SerpApiSearchProvider(os.getenv('LEADGEN_SEARCH_API_KEY', ''), os.getenv('LEADGEN_SEARCH_ENDPOINT') or None, float(os.getenv('LEADGEN_SEARCH_DELAY_SECONDS', '1.0')), int(os.getenv('LEADGEN_SEARCH_MAX_PAGES', '2')))


def search_provider_status() -> str:
    provider_name = os.getenv('LEADGEN_SEARCH_PROVIDER', '').strip().lower()
    if provider_name == 'serpapi' and os.getenv('LEADGEN_SEARCH_API_KEY', '').strip():
        return 'Search provider: SerpApi'
    if not provider_name or not os.getenv('LEADGEN_SEARCH_API_KEY', '').strip():
        return 'Automated search is not configured. Configure a supported search provider.'
    return 'Unsupported automated search provider. Configure a supported search provider.'


class _Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title, self.text, self.links, self.mailto = [], [], [], []
        self._in_title = False
        self._title_done = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == 'title' and not self._title_done: self._in_title = True
        if tag == 'a' and attributes.get('href'):
            href = attributes['href'].strip(); self.links.append(href)
            if href.lower().startswith('mailto:'): self.mailto.append(href[7:].split('?', 1)[0])

    def handle_endtag(self, tag):
        if tag == 'title':
            self._in_title = False
            self._title_done = True

    def handle_data(self, data):
        value = ' '.join(data.split())
        if value:
            self.text.append(value)
            if self._in_title: self.title.append(value)


def normalize_domain(value: str) -> str:
    raw = (value or '').strip(); parsed = urlparse(raw if '://' in raw else f'https://{raw}')
    host = (parsed.hostname or '').lower().rstrip('.')
    if host.startswith('www.'): host = host[4:]
    if not host or parsed.username or parsed.password or any(part in host for part in BLOCKED_HOST_PARTS): return ''
    return host


def canonical_url(value: str) -> str:
    domain = normalize_domain(value)
    return f'https://{domain}' if domain else ''


def _public_url(value: str, base: str | None = None) -> str:
    absolute = urljoin(base, value) if base else value; parsed = urlparse(absolute if '://' in absolute else f'https://{absolute}')
    if parsed.scheme not in ('http', 'https') or not parsed.netloc or not normalize_domain(absolute): return ''
    return absolute.split('#', 1)[0]


def _robots_allowed(url: str) -> bool:
    parsed = urlparse(url); parser = RobotFileParser(); parser.set_url(f'{parsed.scheme}://{parsed.netloc}/robots.txt')
    try: parser.read()
    except Exception: return False
    return parser.can_fetch(USER_AGENT, url)


def _fetch_html(url: str, timeout: int = 8) -> tuple[str, int]:
    if not _robots_allowed(url): raise ValueError('robots.txt disallows this URL or could not be read')
    request = Request(url, headers={'User-Agent': USER_AGENT})
    with urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get('content-type', ''); raw = response.read(500_000); status = getattr(response, 'status', 200)
    if 'text/html' not in content_type.lower(): raise ValueError('URL is not an HTML page')
    return raw.decode('utf-8', 'ignore'), status


def extract_business_emails(text: str, mailto: list[str] | None = None, domain: str = '') -> list[str]:
    found = {email.strip().lower() for email in EMAIL_RE.findall(text or '')}
    found.update(email.strip().lower() for email in (mailto or []) if EMAIL_RE.fullmatch(email.strip()))
    result = []
    for email in sorted(found):
        local, host = email.split('@', 1)
        if host in {'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'proton.me'} and not local.startswith(BUSINESS_PREFIXES): continue
        if domain and host != domain and not host.endswith(f'.{domain}'): continue
        result.append(email)
    return sorted(result, key=lambda email: (not email.split('@', 1)[0].startswith(BUSINESS_PREFIXES), email))


def _signals(text: str, page_count: int) -> dict:
    lowered = text.lower(); ecommerce = any(word in lowered for word in ('product', 'shop', 'store', 'price', 'add to cart', 'buy now', 'checkout')); products = any(word in lowered for word in ('product', 'products', 'shop', 'add to cart', 'buy now'))
    saas_signal = any(word in lowered for word in ('pricing', 'request a demo', 'book a demo', 'free trial', 'start free trial', 'our customers', 'our clients', 'trusted by', 'case study', 'case studies', 'integrations', 'api docs', 'dashboard', 'platform', 'sign up'))
    reviews = any(word in lowered for word in ('review', 'reviews', 'testimonial', 'rating', 'rated', 'customer feedback', 'star rating', 'trusted by', 'case study', 'case studies', 'our customers', 'our clients'))
    business = ecommerce or saas_signal
    return {'ecommerce_detected': int(ecommerce), 'products_detected': int(products), 'business_detected': int(business), 'reviews_detected': int(reviews), 'review_signal': 'Customer reviews, ratings, testimonials, or client proof found on public pages.' if reviews else '', 'social_proof_signal': 'Customer feedback, client, or rating language found on public pages.' if reviews else '', 'review_count_signal': 'Review or client-proof activity detected.' if reviews else '', 'why_fit': 'Business activity and customer-proof signals were detected; social proof may be easier to surface.' if business and reviews else ('Public business activity detected on the website.' if business else ''), 'notes': f'Researched {page_count} public internal page(s); signals are based only on visible page text.'}


def crawl_business_website(website: str, max_pages: int = DEFAULT_MAX_PAGES, timeout: int = 8, delay: float = 0.25) -> dict:
    root = canonical_url(website)
    if not root: raise ValueError('public business website required')
    root_domain, pending, visited, pages, all_text, all_emails = normalize_domain(root), [root], set(), [], [], []
    while pending and len(pages) < max_pages:
        current = pending.pop(0)
        if current in visited or normalize_domain(current) != root_domain: continue
        visited.add(current)
        try: html, status = _fetch_html(current, timeout)
        except ValueError:
            if not pages: raise
            continue
        parser = _Page(); parser.feed(html); text = ' '.join(parser.text); emails = extract_business_emails(text, parser.mailto, root_domain)
        all_text.append(text); all_emails.extend(emails); pages.append({'url': current, 'title': ' '.join(parser.title), 'text': text[:2000], 'status': status, 'links': len(parser.links)})
        links = sorted(parser.links, key=lambda item: (not any(path in item.lower() for path in PRIORITY_PATHS), item))
        for link in links:
            target = _public_url(link, current)
            if target and normalize_domain(target) == root_domain and target not in visited and target not in pending: pending.append(target)
        if pending and delay: time.sleep(delay)
    if not pages: raise ValueError('crawl_status=blocked')
    emails = sorted(set(all_emails), key=lambda email: (not email.split('@', 1)[0].startswith(BUSINESS_PREFIXES), email))
    return {'website': root, 'pages': pages, 'emails': emails, **_signals(' '.join(all_text), len(pages)), 'crawl_status': 'complete'}


class DiscoveryProvider:
    def discover(self, target_country: str, target_niche: str, limit: int) -> list[DiscoveryCandidate]: raise NotImplementedError


class ConfiguredPublicDirectoryProvider(DiscoveryProvider):
    def __init__(self, source_urls: list[str] | None = None):
        configured = source_urls if source_urls is not None else re.split(r'[\r\n,]+', os.getenv('LEADGEN_DISCOVERY_SOURCES', ''))
        self.source_urls = [url for url in (_public_url(item.strip()) for item in configured) if url]

    def discover(self, target_country: str, target_niche: str, limit: int) -> list[DiscoveryCandidate]:
        candidates, seen = [], set()
        for source_url in self.source_urls:
            html, _ = _fetch_html(source_url); parser = _Page(); parser.feed(html)
            for link in parser.links:
                website = canonical_url(urljoin(source_url, link))
                if not website or normalize_domain(website) == normalize_domain(source_url) or website in seen: continue
                seen.add(website); candidates.append(DiscoveryCandidate(website, 'PUBLIC_DIRECTORY', source_url))
                if len(candidates) >= limit: return candidates
        return candidates


class SearchDiscoveryProvider(DiscoveryProvider):
    def __init__(self, search_provider: SearchProvider):
        self.search_provider = search_provider
        self.last_stats = {'searches_performed': 0}

    def discover(self, target_country: str, target_niche: str, limit: int) -> list[DiscoveryCandidate]:
        candidates, seen = [], set()
        queries = generate_search_queries(target_country, target_niche)
        logger.info('discovery queries generated; country=%s niche=%s query_count=%s', target_country, target_niche, len(queries))
        for query in queries:
            logger.info('discovery query; query=%s', query)
            for page in range(1, getattr(self.search_provider, 'max_pages', 1) + 1):
                self.last_stats['searches_performed'] += 1
                for candidate in self.search_provider.search_businesses(query, target_country, min(20, limit), page):
                    domain = normalize_domain(candidate.website)
                    if not domain or domain in seen:
                        continue
                    seen.add(domain)
                    candidates.append(candidate)
                    if len(candidates) >= limit:
                        logger.info('discovery candidate count; candidates=%s unique_domains=%s', len(candidates), len(seen))
                        return candidates
        logger.info('discovery candidate count; candidates=%s unique_domains=%s', len(candidates), len(seen))
        return candidates


class CombinedDiscoveryProvider(DiscoveryProvider):
    def __init__(self, providers: list[DiscoveryProvider]):
        self.providers = providers
        self.last_stats = {'searches_performed': 0}

    def discover(self, target_country: str, target_niche: str, limit: int) -> list[DiscoveryCandidate]:
        candidates, seen = [], set()
        for provider in self.providers:
            for candidate in provider.discover(target_country, target_niche, limit - len(candidates)):
                domain = normalize_domain(candidate.website)
                if domain and domain not in seen:
                    seen.add(domain); candidates.append(candidate)
                if len(candidates) >= limit:
                    break
            self.last_stats['searches_performed'] += getattr(provider, 'last_stats', {}).get('searches_performed', 0)
            if len(candidates) >= limit:
                break
        return candidates


def default_discovery_provider() -> DiscoveryProvider:
    search = configured_search_provider()
    if search is None:
        raise SearchProviderConfigurationError('Automated discovery is not configured yet. Configure a supported search provider to start discovery.')
    providers: list[DiscoveryProvider] = [SearchDiscoveryProvider(search)]
    directory = ConfiguredPublicDirectoryProvider()
    if directory.source_urls:
        providers.append(directory)
    return CombinedDiscoveryProvider(providers)


def _company_name(domain: str) -> str: return domain.split('.')[0].replace('-', ' ').replace('_', ' ').title()


def run_discovery(connection, target_country: str, target_niche: str, requested_count: int, minimum_score: int, provider: DiscoveryProvider | None = None, max_pages: int = DEFAULT_MAX_PAGES) -> dict:
    provider = provider or default_discovery_provider(); requested_count = max(1, min(int(requested_count), 500)); timestamp = __import__('datetime').datetime.now().isoformat(timespec='seconds')
    logger.info('discovery run started; country=%s niche=%s requested_count=%s provider=%s', target_country, target_niche, requested_count, type(provider).__name__)
    source_name = 'SEARCH_PROVIDER' if isinstance(provider, (SearchDiscoveryProvider, CombinedDiscoveryProvider)) else 'CONFIGURED_PUBLIC_DIRECTORY'
    cursor = connection.execute('INSERT INTO discovery_runs (source, query, target_country, target_niche, requested_count, created_at, status) VALUES (?,?,?,?,?,?,?)', (source_name, f'{target_country} {target_niche}'.strip(), target_country, target_niche, requested_count, timestamp, 'RUNNING')); run_id = cursor.lastrowid
    result = {'run_id': run_id, 'searches_performed': 0, 'discovered': 0, 'unique_domains': 0, 'websites_checked': 0, 'emails_found': 0, 'ecommerce_stores': 0, 'qualified': 0, 'rejected': 0, 'duplicates': 0, 'created_ids': [], 'errors': [], 'leads': []}
    try:
        candidates = provider.discover(target_country, target_niche, requested_count); result['searches_performed'] = getattr(provider, 'last_stats', {}).get('searches_performed', 0); result['discovered'] = len(candidates); domains = set()
        for candidate in candidates:
            domain = normalize_domain(candidate.website)
            if not domain or domain in domains: result['duplicates'] += 1; continue
            domains.add(domain)
            try:
                logger.info('discovery crawl started; website=%s crawl_count=%s', candidate.website, result['websites_checked'] + 1)
                research = crawl_business_website(candidate.website, max_pages=max_pages); result['websites_checked'] += 1; result['emails_found'] += len(research['emails']); result['ecommerce_stores'] += research['ecommerce_detected']; email = research['emails'][0] if research['emails'] else ''
                lead = {'company_name': _company_name(domain), 'website': research['website'], 'business_email': email, 'country': target_country, 'niche': target_niche, 'source': candidate.source, 'source_url': candidate.source_url, **research}; lead_id = create_lead(connection, lead); score = int(connection.execute('SELECT lead_score FROM leads WHERE id=?', (lead_id,)).fetchone()['lead_score']); qualified = bool(email and score >= minimum_score and research['business_detected']); reason = 'Qualified because an active business website, public business email, and score threshold were met.' if qualified else 'Rejected because required business-activity, score, or public business-email criteria were not met.'; facts = research['why_fit']; subject = f"Quick idea for {lead['company_name']}"; body = f"I noticed {facts or 'public business activity'} while reviewing {lead['website']}." if qualified else ''
                update_lead(connection, lead_id, {'status': 'QUALIFIED' if qualified else 'BAD_LEAD', 'research_status': 'COMPLETE', 'personalization_status': 'READY' if qualified else 'NOT_READY', 'qualification_reason': reason, 'personalization_facts': facts, 'suggested_subject': subject if qualified else '', 'suggested_body': body, 'discovery_run_id': run_id});
                for page in research['pages']:
                    connection.execute('INSERT INTO discovery_pages (run_id, lead_id, url, title, text, http_status, discovered_links, crawled_at) VALUES (?,?,?,?,?,?,?,?)', (run_id, lead_id, page['url'], page['title'], page['text'], page['status'], page['links'], timestamp))
                for discovered_email in research['emails']:
                    connection.execute('INSERT INTO discovery_emails (run_id, lead_id, email, source_url, created_at) VALUES (?,?,?,?,?)', (run_id, lead_id, discovered_email, research['pages'][0]['url'], timestamp))
                result['qualified' if qualified else 'rejected'] += 1; result['created_ids'].append(lead_id); result['leads'].append({'id': lead_id, 'company_name': lead['company_name'], 'website': lead['website'], 'business_email': email, 'score': score, 'qualified': qualified})
            except ValueError as exc:
                if 'duplicate' in str(exc).lower(): result['duplicates'] += 1
                else: result['errors'].append({'website': candidate.website, 'reason': str(exc)})
        result['unique_domains'] = len(domains); finished = __import__('datetime').datetime.now().isoformat(timespec='seconds'); connection.execute('UPDATE discovery_runs SET status=?, finished_at=?, searches_performed=?, discovered=?, unique_domains=?, websites_checked=?, emails_found=?, ecommerce_stores=?, qualified=?, rejected=?, duplicates=? WHERE id=?', ('COMPLETE', finished, result['searches_performed'], result['discovered'], result['unique_domains'], result['websites_checked'], result['emails_found'], result['ecommerce_stores'], result['qualified'], result['rejected'], result['duplicates'], run_id)); connection.commit(); logger.info('discovery run finished; discovered=%s unique_domains=%s websites_checked=%s emails_found=%s ecommerce_stores=%s qualified=%s rejected=%s duplicates=%s errors=%s', result['discovered'], result['unique_domains'], result['websites_checked'], result['emails_found'], result['ecommerce_stores'], result['qualified'], result['rejected'], result['duplicates'], len(result['errors'])); return result
    except Exception as exc:
        logger.error('discovery run failed; provider=%s error_type=%s', type(provider).__name__, type(exc).__name__)
        connection.execute('UPDATE discovery_runs SET status=? WHERE id=?', ('FAILED', run_id)); connection.commit(); raise


def fetch_public_page(url: str, timeout: int = 8) -> dict:
    research = crawl_business_website(url, max_pages=1, timeout=timeout, delay=0); return {'website': research['website'], 'source_url': url, 'business_email': research['emails'][0] if research['emails'] else '', **research}


def discover_urls(connection, urls: list[str], country: str = '', niche: str = '') -> dict:
    class UrlProvider(DiscoveryProvider):
        def discover(self, target_country, target_niche, limit): return [DiscoveryCandidate(url, 'COMPANY_WEBSITE', url) for url in urls[:limit]]
    return run_discovery(connection, country, niche, len(urls), 0, provider=UrlProvider(), max_pages=1)
