from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from app.models.entities import AITool, AIToolCategory, AIToolFactProvenance
from app.services.ai_tool_provenance_catalog import (
    SPECIFIC_FACT_SOURCES,
    VERIFIED_PRICING_SOURCES,
    build_specific_candidates,
    classify_row,
    is_strict_supported_row,
)
from scripts.seed_ai_tool_provenance import reconcile


@pytest.fixture()
def session():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    AIToolCategory.__table__.create(bind=engine)
    AITool.__table__.create(bind=engine)
    AIToolFactProvenance.__table__.create(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _seed_tools(session):
    writing = AIToolCategory(name="AI Writing", slug="ai-writing", position=1)
    design = AIToolCategory(name="AI Image & Design", slug="ai-image-design", position=2)
    coding = AIToolCategory(name="AI Coding & Developer Tools", slug="ai-coding-developer-tools", position=3)
    session.add_all([writing, design, coding])
    session.flush()

    grammarly = AITool(
        id=uuid.uuid4(),
        slug="grammarly",
        name="Grammarly",
        provider="Grammarly",
        description="Writing assistant",
        website_url="https://www.grammarly.com",
        category_id=writing.id,
        lifecycle_status="published",
        pricing_model="monthly",
        pricing_url="https://www.grammarly.com/plans",
        use_cases=["editing"],
        features=["grammar suggestions", "tone suggestions", "rewrite assistance"],
        pros=[],
        cons=[],
        best_for=[],
        not_ideal_for=[],
        tags=[],
        platforms=["web", "browser extension", "desktop", "mobile"],
        integrations=["google docs", "microsoft office"],
        affiliate_available=False,
        last_verified_at=datetime.now(timezone.utc),
    )

    canva = AITool(
        id=uuid.uuid4(),
        slug="canva-magic-studio",
        name="Canva Magic Studio",
        provider="Canva",
        description="Design workflows",
        website_url="https://www.canva.com/magic-studio/",
        category_id=design.id,
        lifecycle_status="published",
        pricing_model="monthly",
        pricing_url="https://www.canva.com/pricing/",
        use_cases=["design"],
        features=["ai-assisted design"],
        pros=[],
        cons=[],
        best_for=[],
        not_ideal_for=[],
        tags=[],
        platforms=["web", "ios", "android"],
        integrations=["google drive", "dropbox"],
        affiliate_available=False,
        last_verified_at=datetime.now(timezone.utc),
    )

    cursor = AITool(
        id=uuid.uuid4(),
        slug="cursor",
        name="Cursor",
        provider="Anysphere",
        description="AI-native editor",
        website_url="https://www.cursor.com",
        category_id=coding.id,
        lifecycle_status="published",
        pricing_model="monthly",
        pricing_url="https://www.cursor.com/pricing",
        use_cases=["coding"],
        features=["agent-style coding"],
        pros=[],
        cons=[],
        best_for=[],
        not_ideal_for=[],
        tags=[],
        platforms=["desktop"],
        integrations=["git"],
        affiliate_available=False,
        last_verified_at=datetime.now(timezone.utc),
    )

    session.add_all([grammarly, canva, cursor])
    session.flush()

    return grammarly, canva, cursor


def test_generic_homepage_is_not_strict_supported_for_android_or_git(session):
    _, canva, cursor = _seed_tools(session)

    assert not is_strict_supported_row(
        slug=canva.slug,
        fact_type="platform",
        fact_key="android",
        source_kind="official_provider",
        source_url=canva.website_url,
    )
    assert not is_strict_supported_row(
        slug=cursor.slug,
        fact_type="integration",
        fact_key="git",
        source_kind="official_provider",
        source_url=cursor.website_url,
    )


def test_official_provider_source_kind_is_required(session):
    _, _, cursor = _seed_tools(session)

    assert classify_row(
        slug=cursor.slug,
        fact_type="pricing",
        fact_key="monthly",
        source_kind="community",
        source_url="https://www.cursor.com/pricing",
    ) == "C"


def test_pricing_provenance_uses_verified_pricing_url(session):
    _, _, cursor = _seed_tools(session)

    candidates = build_specific_candidates(cursor)
    pricing = [row for row in candidates if row.fact_type == "pricing"]

    assert pricing
    assert pricing[0].source_url == VERIFIED_PRICING_SOURCES["cursor"]


def test_no_fabricated_urls_are_generated_for_candidates(session):
    grammarly, canva, cursor = _seed_tools(session)

    allowed_urls = set(VERIFIED_PRICING_SOURCES.values())
    for mapping in SPECIFIC_FACT_SOURCES.values():
        allowed_urls.update(mapping.values())

    all_candidates = []
    for tool in (grammarly, canva, cursor):
        all_candidates.extend(build_specific_candidates(tool))

    assert all_candidates
    assert all(row.source_url in allowed_urls for row in all_candidates)


def test_reconcile_removes_questionable_and_keeps_only_strict_rows(session):
    grammarly, _, _ = _seed_tools(session)

    session.add_all(
        [
            AIToolFactProvenance(
                ai_tool_id=grammarly.id,
                fact_type="feature",
                fact_key="grammar suggestions",
                source_url="https://www.grammarly.com",
                source_kind="official_provider",
                verified_at=datetime.now(timezone.utc),
            ),
            AIToolFactProvenance(
                ai_tool_id=grammarly.id,
                fact_type="platform",
                fact_key="desktop",
                source_url="https://example.com/grammarly-desktop",
                source_kind="official_provider",
                verified_at=datetime.now(timezone.utc),
            ),
            AIToolFactProvenance(
                ai_tool_id=grammarly.id,
                fact_type="pricing",
                fact_key="monthly",
                source_url="https://www.grammarly.com/plans",
                source_kind="official_provider",
                verified_at=datetime.now(timezone.utc),
            ),
        ]
    )
    session.commit()

    report = reconcile(session)
    session.commit()

    assert report.before_count >= 3
    assert report.removed_count >= 2
    assert report.questionable_remaining_count == 0
    assert report.verified_specific_count == report.after_count

    rows = list(session.scalars(select(AIToolFactProvenance)).all())
    slug_by_tool_id = {
        str(grammarly.id): "grammarly",
    }
    for tool in session.scalars(select(AITool).where(AITool.lifecycle_status == "published")).all():
        slug_by_tool_id[str(tool.id)] = tool.slug

    assert rows
    assert all(
        classify_row(
            slug=slug_by_tool_id[str(row.ai_tool_id)],
            fact_type=row.fact_type,
            fact_key=row.fact_key,
            source_kind=row.source_kind,
            source_url=row.source_url,
        )
        == "A"
        for row in rows
    )
