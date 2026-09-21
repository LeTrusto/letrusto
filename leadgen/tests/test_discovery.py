from pathlib import Path
from urllib.error import HTTPError
from io import BytesIO

from app.services import discovery_service as discovery
from app.services.db import connect


class FixedProvider(discovery.DiscoveryProvider):
    def discover(self, target_country, target_niche, limit):
        return [discovery.DiscoveryCandidate('https://shop.example', 'PUBLIC_DIRECTORY', 'https://directory.example/fashion')]


def test_crawler_limits_to_internal_pages_and_deduplicates_business_email(monkeypatch):
    pages = {
        'https://shop.example': '<title>Shop</title><a href="/products">Products</a><a href="https://outside.example">Outside</a>hello@shop.example hello@shop.example',
        'https://shop.example/products': '<title>Products</title><a href="/contact">Contact</a>buy now add to cart customer reviews',
        'https://shop.example/contact': 'mailto:contact@shop.example contact@shop.example',
    }
    monkeypatch.setattr(discovery, '_robots_allowed', lambda url: True)
    monkeypatch.setattr(discovery, '_fetch_html', lambda url, timeout=8: (pages[url], 200))
    result = discovery.crawl_business_website('https://shop.example', max_pages=2, delay=0)
    assert len(result['pages']) == 2
    assert result['emails'] == ['hello@shop.example']
    assert result['ecommerce_detected'] == 1 and result['reviews_detected'] == 1


def test_discovery_creates_qualified_lead_and_evidence_without_sending(tmp_path: Path, monkeypatch):
    html = '<title>Store</title><a href="/products">Products</a><a href="/contact">Contact</a>hello@shop.example buy now add to cart customer reviews testimonials'
    monkeypatch.setattr(discovery, '_robots_allowed', lambda url: True)
    monkeypatch.setattr(discovery, '_fetch_html', lambda url, timeout=8: (html, 200))
    db = connect(tmp_path / 'discovery.sqlite3')
    result = discovery.run_discovery(db, 'India', 'fashion', 1, 60, provider=FixedProvider(), max_pages=2)
    lead = dict(db.execute('SELECT * FROM leads WHERE id=?', (result['created_ids'][0],)).fetchone())
    assert result['qualified'] == 1
    assert lead['status'] == 'QUALIFIED'
    assert lead['personalization_status'] == 'READY'
    assert db.execute('SELECT COUNT(*) FROM discovery_pages').fetchone()[0] >= 1
    assert db.execute('SELECT COUNT(*) FROM discovery_emails').fetchone()[0] == 1
    assert db.execute('SELECT COUNT(*) FROM send_logs').fetchone()[0] == 0
    db.close()


def test_search_queries_and_filtering():
    assert discovery.generate_search_queries('India', 'fashion') == [
        'India fashion companies',
        'India fashion businesses official website',
        'India fashion SaaS company',
        'India fashion company contact',
    ]
    assert discovery._search_candidate_allowed('https://store.example/products', 'Fashion store', 'Buy online')
    assert not discovery._search_candidate_allowed('https://example.com/jobs', 'Fashion brand', '')
    assert not discovery._search_candidate_allowed('https://www.wikipedia.org/wiki/Fashion', 'Fashion', '')


def test_search_provider_paginates_and_deduplicates():
    class FakeSearch(discovery.SearchProvider):
        max_pages = 2

        def __init__(self):
            self.calls = []

        def search_businesses(self, query, country, limit, page=1):
            self.calls.append((query, country, limit, page))
            if page == 1:
                return [discovery.DiscoveryCandidate('https://one.example', 'SEARCH_TEST', 'https://search.test')]
            return [
                discovery.DiscoveryCandidate('https://one.example', 'SEARCH_TEST', 'https://search.test'),
                discovery.DiscoveryCandidate('https://two.example', 'SEARCH_TEST', 'https://search.test'),
            ]

    provider = FakeSearch()
    result = discovery.SearchDiscoveryProvider(provider).discover('India', 'fashion', 2)
    assert [candidate.website for candidate in result] == ['https://one.example', 'https://two.example']
    assert len(provider.calls) == 2


def test_no_search_provider_fails_closed(monkeypatch):
    monkeypatch.delenv('LEADGEN_SEARCH_PROVIDER', raising=False)
    monkeypatch.delenv('LEADGEN_SEARCH_API_KEY', raising=False)
    try:
        discovery.default_discovery_provider()
    except discovery.SearchProviderConfigurationError as exc:
        assert str(exc) == 'Automated discovery is not configured yet. Configure a supported search provider to start discovery.'
    else:
        raise AssertionError('expected provider configuration error')


class FakeSearchResponse:
    def __init__(self, payload, status=200):
        self.payload = payload
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def read(self, limit):
        return self.payload


def test_serpapi_request_parses_candidates_and_supplies_key(monkeypatch):
    seen = {}

    def fake_urlopen(request, timeout):
        seen['url'] = request.full_url
        seen['headers'] = dict(request.header_items())
        seen['timeout'] = timeout
        return FakeSearchResponse(b'{"organic_results":[{"link":"https://shop.example/products","title":"Shop","snippet":"Buy online"}]}')

    monkeypatch.setattr(discovery, 'urlopen', fake_urlopen)
    provider = discovery.SerpApiSearchProvider('secret-test-key', delay_seconds=0, max_pages=1)
    candidates = provider.search_businesses('India fashion companies', 'India', 5)
    assert 'api_key=secret-test-key' in seen['url']
    assert 'q=India+fashion+companies' in seen['url']
    assert seen['timeout'] == 12
    assert [candidate.website for candidate in candidates] == ['https://shop.example']


def test_serpapi_zero_results_is_success(monkeypatch):
    monkeypatch.setattr(discovery, 'urlopen', lambda request, timeout: FakeSearchResponse(b'{"organic_results":[]}'))
    provider = discovery.SerpApiSearchProvider('test-key', delay_seconds=0, max_pages=1)
    assert provider.search_businesses('India fashion', 'India', 5) == []


def test_serpapi_auth_rate_limit_and_server_errors(monkeypatch):
    for status, error_type in ((401, discovery.SearchProviderAuthenticationError), (429, discovery.SearchProviderRateLimitError), (500, discovery.SearchProviderError)):
        def fake_urlopen(request, timeout, status=status):
            raise HTTPError(request.full_url, status, 'provider error', {}, BytesIO(b''))
        monkeypatch.setattr(discovery, 'urlopen', fake_urlopen)
        provider = discovery.SerpApiSearchProvider('test-key', delay_seconds=0, max_pages=1)
        try:
            provider.search_businesses('India fashion', 'India', 5)
        except error_type as exc:
            assert exc.status_code == status
        else:
            raise AssertionError(f'expected {error_type.__name__}')


def test_serpapi_error_payload_and_malformed_response_fail_loudly(monkeypatch):
    monkeypatch.setattr(discovery, 'urlopen', lambda request, timeout: FakeSearchResponse(b'{"error":"Invalid API key"}'))
    provider = discovery.SerpApiSearchProvider('test-key', delay_seconds=0, max_pages=1)
    try:
        provider.search_businesses('India fashion', 'India', 5)
    except discovery.SearchProviderAuthenticationError:
        pass
    else:
        raise AssertionError('expected authentication error')

    monkeypatch.setattr(discovery, 'urlopen', lambda request, timeout: FakeSearchResponse(b'{"unexpected":[]}'))
    try:
        provider.search_businesses('India fashion', 'India', 5)
    except discovery.SearchProviderResponseError:
        pass
    else:
        raise AssertionError('expected invalid response error')


def test_serpapi_pagination_uses_start_offset(monkeypatch):
    urls = []

    def fake_urlopen(request, timeout):
        urls.append(request.full_url)
        return FakeSearchResponse(b'{"organic_results":[{"link":"https://shop.example"}]}')

    monkeypatch.setattr(discovery, 'urlopen', fake_urlopen)
    provider = discovery.SerpApiSearchProvider('test-key', delay_seconds=0, max_pages=2)
    provider.search_businesses('India fashion', 'India', 5, page=2)
    assert 'start=10' in urls[0]


def test_provider_failure_marks_run_failed(tmp_path: Path):
    class FailingProvider(discovery.DiscoveryProvider):
        def discover(self, target_country, target_niche, limit):
            raise discovery.SearchProviderAuthenticationError('SerpApi authentication failed.', 401)

    db = connect(tmp_path / 'failed.sqlite3')
    try:
        discovery.run_discovery(db, 'India', 'fashion ecommerce', 25, 50, provider=FailingProvider())
    except discovery.SearchProviderAuthenticationError:
        pass
    else:
        raise AssertionError('expected provider failure')
    assert db.execute('SELECT status FROM discovery_runs').fetchone()['status'] == 'FAILED'
    db.close()