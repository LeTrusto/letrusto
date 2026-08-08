"""
Reconcile ai_tool_fact_provenance for published AI tools with strict, verified sources.
Run: python -m scripts.seed_ai_tool_provenance
"""
from __future__ import annotations

import sys
from dataclasses import dataclass

sys.path.insert(0, ".")

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.entities import AITool, AIToolFactProvenance
from app.services.ai_tool_provenance_catalog import (
    build_specific_candidates,
    canonical_url,
    classify_row,
    normalize_fact_key,
    verified_at_or_now,
)


@dataclass(slots=True)
class ReconcileReport:
    before_count: int
    after_count: int
    removed_count: int
    inserted_count: int
    replaced_count: int
    verified_specific_count: int
    questionable_remaining_count: int
    tools_with_zero_provenance: list[str]
    tools_with_complete_provenance: list[str]


def _row_key(ai_tool_id: str, fact_type: str, fact_key: str, source_url: str | None) -> tuple[str, str, str, str]:
    return (
        ai_tool_id,
        fact_type,
        normalize_fact_key(fact_key),
        canonical_url(source_url or ""),
    )


def reconcile(session) -> ReconcileReport:
    published_tools = session.scalars(select(AITool).where(AITool.lifecycle_status == "published")).all()
    if not published_tools:
        return ReconcileReport(
            before_count=0,
            after_count=0,
            removed_count=0,
            inserted_count=0,
            replaced_count=0,
            verified_specific_count=0,
            questionable_remaining_count=0,
            tools_with_zero_provenance=[],
            tools_with_complete_provenance=[],
        )

    tool_by_id = {str(tool.id): tool for tool in published_tools}
    tool_ids = [tool.id for tool in published_tools]
    existing_rows = list(
        session.scalars(select(AIToolFactProvenance).where(AIToolFactProvenance.ai_tool_id.in_(tool_ids))).all()
    )

    before_count = len(existing_rows)
    removed_count = 0
    inserted_count = 0
    replaced_count = 0

    existing_by_fact: dict[tuple[str, str, str], set[str]] = {}
    kept_keys: set[tuple[str, str, str, str]] = set()

    for row in existing_rows:
        tool = tool_by_id.get(str(row.ai_tool_id))
        if tool is None:
            continue

        fact_triplet = (str(row.ai_tool_id), row.fact_type, normalize_fact_key(row.fact_key))
        existing_by_fact.setdefault(fact_triplet, set()).add(canonical_url(row.source_url or ""))

        clazz = classify_row(
            slug=tool.slug,
            fact_type=row.fact_type,
            fact_key=row.fact_key,
            source_kind=row.source_kind,
            source_url=row.source_url,
        )

        if clazz == "A":
            row.fact_key = normalize_fact_key(row.fact_key)
            row.source_url = canonical_url(row.source_url or "")
            kept_keys.add(_row_key(str(row.ai_tool_id), row.fact_type, row.fact_key, row.source_url))
            continue

        session.delete(row)
        removed_count += 1

    for tool in published_tools:
        expected = build_specific_candidates(tool)
        for candidate in expected:
            key = _row_key(str(tool.id), candidate.fact_type, candidate.fact_key, candidate.source_url)
            if key in kept_keys:
                continue

            fact_triplet = (str(tool.id), candidate.fact_type, normalize_fact_key(candidate.fact_key))
            previous_sources = existing_by_fact.get(fact_triplet, set())
            if previous_sources and canonical_url(candidate.source_url) not in previous_sources:
                replaced_count += 1

            session.add(
                AIToolFactProvenance(
                    ai_tool_id=tool.id,
                    fact_type=candidate.fact_type,
                    fact_key=normalize_fact_key(candidate.fact_key),
                    source_url=canonical_url(candidate.source_url),
                    source_kind="official_provider",
                    verified_at=verified_at_or_now(tool.last_verified_at),
                )
            )
            kept_keys.add(key)
            inserted_count += 1

    session.flush()

    final_rows = list(
        session.scalars(select(AIToolFactProvenance).where(AIToolFactProvenance.ai_tool_id.in_(tool_ids))).all()
    )

    after_count = len(final_rows)
    questionable_remaining_count = 0
    rows_by_tool: dict[str, list[AIToolFactProvenance]] = {str(tool.id): [] for tool in published_tools}
    for row in final_rows:
        rows_by_tool.setdefault(str(row.ai_tool_id), []).append(row)
        tool = tool_by_id.get(str(row.ai_tool_id))
        if tool is None:
            continue
        if (
            classify_row(
                slug=tool.slug,
                fact_type=row.fact_type,
                fact_key=row.fact_key,
                source_kind=row.source_kind,
                source_url=row.source_url,
            )
            != "A"
        ):
            questionable_remaining_count += 1

    verified_specific_count = after_count - questionable_remaining_count

    tools_with_zero_provenance: list[str] = []
    tools_with_complete_provenance: list[str] = []
    for tool in published_tools:
        rows = rows_by_tool.get(str(tool.id), [])
        if not rows:
            tools_with_zero_provenance.append(tool.slug)

        expected_keys = {
            (candidate.fact_type, normalize_fact_key(candidate.fact_key), canonical_url(candidate.source_url))
            for candidate in build_specific_candidates(tool)
        }
        actual_keys = {
            (row.fact_type, normalize_fact_key(row.fact_key), canonical_url(row.source_url or "")) for row in rows
        }
        if expected_keys and expected_keys.issubset(actual_keys):
            tools_with_complete_provenance.append(tool.slug)

    return ReconcileReport(
        before_count=before_count,
        after_count=after_count,
        removed_count=removed_count,
        inserted_count=inserted_count,
        replaced_count=replaced_count,
        verified_specific_count=verified_specific_count,
        questionable_remaining_count=questionable_remaining_count,
        tools_with_zero_provenance=sorted(tools_with_zero_provenance),
        tools_with_complete_provenance=sorted(tools_with_complete_provenance),
    )


def run() -> None:
    session = SessionLocal()
    try:
        report = reconcile(session)
        session.commit()
        print(f"Before rows: {report.before_count}")
        print(f"After rows: {report.after_count}")
        print(f"Verified specific rows: {report.verified_specific_count}")
        print(f"Removed rows: {report.removed_count}")
        print(f"Inserted rows: {report.inserted_count}")
        print(f"Replaced rows: {report.replaced_count}")
        print(f"Questionable remaining rows: {report.questionable_remaining_count}")
        print(f"Tools with zero provenance: {', '.join(report.tools_with_zero_provenance) if report.tools_with_zero_provenance else 'none'}")
        print(
            "Tools with complete provenance: "
            f"{', '.join(report.tools_with_complete_provenance) if report.tools_with_complete_provenance else 'none'}"
        )
    finally:
        session.close()


if __name__ == "__main__":
    run()
