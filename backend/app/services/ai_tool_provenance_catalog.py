from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from urllib.parse import urlparse

from app.models.entities import AITool


SPECIFIC_FACT_SOURCES: dict[str, dict[tuple[str, str], str]] = {
    "chatgpt": {
        ("platform", "web"): "https://chatgpt.com/pricing",
        ("platform", "ios"): "https://chatgpt.com/pricing",
        ("platform", "android"): "https://chatgpt.com/pricing",
        ("integration", "openai api"): "https://developers.openai.com/api/docs",
    },
    "claude": {
        ("platform", "web"): "https://claude.com/pricing",
        ("platform", "ios"): "https://claude.com/pricing",
        ("platform", "android"): "https://claude.com/pricing",
        ("integration", "anthropic api"): "https://claude.com/platform/api",
    },
    "grammarly": {
        ("feature", "grammar suggestions"): "https://www.grammarly.com/plans",
        ("feature", "tone suggestions"): "https://www.grammarly.com/plans",
        ("feature", "rewrite assistance"): "https://www.grammarly.com/plans",
        ("platform", "browser extension"): "https://www.grammarly.com/browser",
        ("platform", "desktop"): "https://www.grammarly.com/desktop",
        ("platform", "mobile"): "https://www.grammarly.com/mobile",
        ("integration", "google docs"): "https://www.grammarly.com/google-docs",
        ("integration", "microsoft office"): "https://www.grammarly.com/microsoft-office",
    },
    "github-copilot": {
        ("feature", "in-editor assistance"): "https://github.com/features/copilot",
        ("feature", "chat"): "https://github.com/features/copilot",
        ("feature", "multi-file coding support"): "https://github.com/features/copilot",
        ("platform", "github"): "https://github.com/features/copilot",
        ("platform", "vscode"): "https://docs.github.com/en/copilot/configuring-github-copilot/installing-the-github-copilot-extension-in-your-environment?tool=vscode",
        ("platform", "jetbrains"): "https://docs.github.com/en/copilot/configuring-github-copilot/installing-the-github-copilot-extension-in-your-environment?tool=jetbrains",
        ("platform", "neovim"): "https://docs.github.com/en/copilot/configuring-github-copilot/installing-the-github-copilot-extension-in-your-environment?tool=neovim",
        ("integration", "github"): "https://github.com/features/copilot",
    },
    "elevenlabs": {
        ("integration", "elevenlabs api"): "https://elevenlabs.io/docs/api-reference/introduction",
        ("feature", "text-to-speech"): "https://elevenlabs.io/pricing",
    },
}

VERIFIED_PRICING_SOURCES: dict[str, str] = {
    "canva-magic-studio": "https://www.canva.com/pricing/",
    "chatgpt": "https://chatgpt.com/pricing",
    "claude": "https://claude.com/pricing",
    "cursor": "https://www.cursor.com/pricing",
    "elevenlabs": "https://elevenlabs.io/pricing",
    "github-copilot": "https://github.com/features/copilot/plans",
    "grammarly": "https://www.grammarly.com/plans",
    "jasper": "https://www.jasper.ai/pricing",
    "runway": "https://runway.com/pricing",
}

OFFICIAL_HOSTS: dict[str, set[str]] = {
    "canva-magic-studio": {"www.canva.com", "canva.com"},
    "chatgpt": {"chatgpt.com", "openai.com", "platform.openai.com", "developers.openai.com"},
    "claude": {"claude.com", "anthropic.com", "www.anthropic.com", "platform.claude.com", "docs.anthropic.com"},
    "cursor": {"cursor.com", "www.cursor.com", "docs.cursor.com"},
    "elevenlabs": {"elevenlabs.io", "www.elevenlabs.io"},
    "github-copilot": {"github.com", "docs.github.com", "code.visualstudio.com"},
    "grammarly": {"grammarly.com", "www.grammarly.com", "support.grammarly.com"},
    "jasper": {"jasper.ai", "www.jasper.ai", "help.jasper.ai"},
    "midjourney": {"midjourney.com", "www.midjourney.com"},
    "runway": {"runway.com", "www.runway.com", "runwayml.com"},
}


@dataclass(slots=True)
class ProvenanceCandidate:
    fact_type: str
    fact_key: str
    source_url: str


def normalize_fact_key(value: str) -> str:
    return " ".join(value.strip().lower().split())


def normalize_slug(value: str) -> str:
    return value.strip().lower()


def canonical_url(value: str) -> str:
    parsed = urlparse(value.strip())
    scheme = parsed.scheme.lower() if parsed.scheme else "https"
    netloc = parsed.netloc.lower()
    path = parsed.path or "/"
    query = f"?{parsed.query}" if parsed.query else ""
    return f"{scheme}://{netloc}{path}{query}"


def is_generic_source_url(url: str | None) -> bool:
    if not url:
        return True
    parsed = urlparse(url)
    path = (parsed.path or "").strip("/")
    return path == ""


def is_official_provider_url(slug: str, url: str | None) -> bool:
    if not url:
        return False
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if not host:
        return False
    return host in OFFICIAL_HOSTS.get(normalize_slug(slug), set())


def classify_row(
    slug: str,
    fact_type: str,
    fact_key: str,
    source_kind: str,
    source_url: str | None,
) -> str:
    if source_kind != "official_provider":
        return "C"

    normalized_slug = normalize_slug(slug)
    normalized_fact_key = normalize_fact_key(fact_key)
    expected = SPECIFIC_FACT_SOURCES.get(normalized_slug, {}).get((fact_type, normalized_fact_key))
    if fact_type == "pricing":
        expected = VERIFIED_PRICING_SOURCES.get(normalized_slug)

    if expected and source_url and canonical_url(source_url) == canonical_url(expected):
        return "A"

    if is_official_provider_url(normalized_slug, source_url):
        return "B"

    return "C"


def is_strict_supported_row(
    slug: str,
    fact_type: str,
    fact_key: str,
    source_kind: str,
    source_url: str | None,
) -> bool:
    return classify_row(
        slug=slug,
        fact_type=fact_type,
        fact_key=fact_key,
        source_kind=source_kind,
        source_url=source_url,
    ) == "A"


def build_specific_candidates(tool: AITool) -> list[ProvenanceCandidate]:
    slug = normalize_slug(tool.slug)
    rows: list[ProvenanceCandidate] = []

    pricing_url = VERIFIED_PRICING_SOURCES.get(slug)
    if pricing_url and is_official_provider_url(slug, pricing_url):
        rows.append(
            ProvenanceCandidate(
                fact_type="pricing",
                fact_key=normalize_fact_key(tool.pricing_model or "monthly"),
                source_url=pricing_url,
            )
        )

    mapped = SPECIFIC_FACT_SOURCES.get(slug, {})

    feature_keys = {normalize_fact_key(item) for item in (tool.features or [])}
    platform_keys = {normalize_fact_key(item) for item in (tool.platforms or [])}
    integration_keys = {normalize_fact_key(item) for item in (tool.integrations or [])}

    for (fact_type, fact_key), source_url in mapped.items():
        if not is_official_provider_url(slug, source_url):
            continue
        if is_generic_source_url(source_url):
            continue

        if fact_type == "feature" and fact_key not in feature_keys:
            continue
        if fact_type == "platform" and fact_key not in platform_keys:
            continue
        if fact_type == "integration" and fact_key not in integration_keys:
            continue

        rows.append(
            ProvenanceCandidate(
                fact_type=fact_type,
                fact_key=fact_key,
                source_url=source_url,
            )
        )

    return rows


def verified_at_or_now(value: datetime | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value
