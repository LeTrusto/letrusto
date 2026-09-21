from pathlib import Path

from fastapi.testclient import TestClient

from app import main
from app.services import discovery_service


def test_health_and_dashboard(tmp_path, monkeypatch):
    monkeypatch.setattr(main.settings, "database_path", tmp_path / "web.sqlite3")
    client = TestClient(main.app)
    assert client.get("/healthz").status_code == 200
    assert "Today's outreach" in client.get("/").text


def test_new_lead_and_detail(tmp_path, monkeypatch):
    monkeypatch.setattr(main.settings, "database_path", tmp_path / "web.sqlite3")
    client = TestClient(main.app)
    response = client.post("/leads", data={"company_name": "Web Store", "business_email": "hello@web.example", "website": "web.example", "niche": "Beauty"})
    assert response.status_code == 200 and "Web Store" in response.text


def test_discover_page_shows_search_provider_status(tmp_path, monkeypatch):
    monkeypatch.setattr(main.settings, "database_path", tmp_path / "web.sqlite3")
    monkeypatch.setenv("LEADGEN_SEARCH_PROVIDER", "serpapi")
    monkeypatch.setenv("LEADGEN_SEARCH_API_KEY", "test-key")
    response = TestClient(main.app).get("/discover")
    assert response.status_code == 200
    assert "Automatically discover B2B and SaaS businesses" in response.text
    assert "Search provider: SerpApi" in response.text
    assert "LEADGEN_DISCOVERY_SOURCES" not in response.text


def test_discover_page_shows_unconfigured_search_status(tmp_path, monkeypatch):
    monkeypatch.setattr(main.settings, "database_path", tmp_path / "web.sqlite3")
    monkeypatch.delenv("LEADGEN_SEARCH_PROVIDER", raising=False)
    monkeypatch.delenv("LEADGEN_SEARCH_API_KEY", raising=False)
    response = TestClient(main.app).get("/discover")
    assert "Automated search is not configured. Configure a supported search provider." in response.text


def test_discover_post_uses_default_search_provider_factory(tmp_path, monkeypatch):
    monkeypatch.setattr(main.settings, "database_path", tmp_path / "web.sqlite3")
    calls = []

    class EmptySearchProvider(discovery_service.DiscoveryProvider):
        def discover(self, target_country, target_niche, limit):
            calls.append((target_country, target_niche, limit))
            return []

    monkeypatch.setattr(discovery_service, "default_discovery_provider", lambda: EmptySearchProvider())
    response = TestClient(main.app).post("/discover", data={"country": "India", "niche": "fashion", "requested_count": "3", "minimum_score": "60"})
    assert response.status_code == 200
    assert calls == [("India", "fashion", 3)]
    assert "Discovery complete." in response.text
