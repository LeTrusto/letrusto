"""stage 2 ai tools foundation

Revision ID: 20260808_02
Revises: 20260804_01
Create Date: 2026-08-08
"""

from collections.abc import Sequence
import json
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "20260808_02"
down_revision: str | None = "20260804_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "ai_tool_categories",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_ai_tool_categories_slug", "ai_tool_categories", ["slug"], unique=False)

    op.create_table(
        "ai_tools",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("slug", sa.String(length=160), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("provider", sa.String(length=160), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("website_url", sa.Text(), nullable=False),
        sa.Column("logo_url", sa.Text(), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("lifecycle_status", sa.String(length=20), nullable=False, server_default="draft"),
        sa.Column("pricing_model", sa.String(length=20), nullable=True),
        sa.Column("pricing_amount", sa.Numeric(12, 2), nullable=True),
        sa.Column("pricing_currency", sa.String(length=8), nullable=True),
        sa.Column("pricing_period", sa.String(length=20), nullable=True),
        sa.Column("has_free_plan", sa.Boolean(), nullable=True),
        sa.Column("has_free_trial", sa.Boolean(), nullable=True),
        sa.Column("trial_days", sa.Integer(), nullable=True),
        sa.Column("pricing_notes", sa.Text(), nullable=True),
        sa.Column("pricing_url", sa.Text(), nullable=True),
        sa.Column("affiliate_available", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("affiliate_url", sa.Text(), nullable=True),
        sa.Column("letrusto_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("why_letrusto_recommends", sa.Text(), nullable=True),
        sa.Column("use_cases", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("features", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("pros", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("cons", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("best_for", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("not_ideal_for", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("tags", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("platforms", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("integrations", sa.JSON(), nullable=False, server_default="[]"),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["category_id"], ["ai_tool_categories.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_ai_tools_slug", "ai_tools", ["slug"], unique=False)
    op.create_index("ix_ai_tools_name", "ai_tools", ["name"], unique=False)
    op.create_index("ix_ai_tools_provider", "ai_tools", ["provider"], unique=False)
    op.create_index("ix_ai_tools_lifecycle_status", "ai_tools", ["lifecycle_status"], unique=False)
    op.create_index("ix_ai_tools_category_status", "ai_tools", ["category_id", "lifecycle_status"], unique=False)
    op.create_index("ix_ai_tools_last_verified", "ai_tools", ["last_verified_at"], unique=False)

    conn = op.get_bind()

    categories = [
        ("AI Assistants", "ai-assistants", 1),
        ("AI Writing", "ai-writing", 2),
        ("AI Image & Design", "ai-image-design", 3),
        ("AI Video & Audio", "ai-video-audio", 4),
        ("AI Coding & Developer Tools", "ai-coding-developer-tools", 5),
    ]

    for name, slug, position in categories:
        conn.execute(
            sa.text(
                "INSERT INTO ai_tool_categories (name, slug, position) "
                "VALUES (:name, :slug, :position)"
            ),
            {"name": name, "slug": slug, "position": position},
        )

    category_ids = {
        row.slug: row.id
        for row in conn.execute(sa.text("SELECT id, slug FROM ai_tool_categories")).fetchall()
    }

    tools = [
        {
            "slug": "chatgpt",
            "name": "ChatGPT",
            "provider": "OpenAI",
            "description": "General-purpose AI assistant for writing, reasoning, coding support, and research workflows.",
            "website_url": "https://chatgpt.com",
            "logo_url": "https://openai.com/favicon.ico",
            "category_slug": "ai-assistants",
            "pricing_model": "monthly",
            "pricing_amount": None,
            "pricing_currency": "USD",
            "pricing_period": "month",
            "has_free_plan": True,
            "has_free_trial": None,
            "trial_days": None,
            "pricing_notes": "Provider offers free and paid plans; exact plan prices change by region and plan tier.",
            "pricing_url": "https://openai.com/chatgpt/pricing",
            "use_cases": ["research", "writing", "productivity", "brainstorming"],
            "features": ["chat interface", "file understanding", "tool-assisted workflows"],
            "pros": ["broad task coverage", "strong ecosystem"],
            "cons": ["advanced capabilities depend on paid tier"],
            "best_for": ["teams needing a general AI assistant"],
            "not_ideal_for": ["buyers requiring fixed long-term pricing guarantees"],
            "why_letrusto_recommends": "Widely adopted assistant with strong general-purpose capability and broad workflow coverage.",
            "tags": ["assistant", "productivity", "research"],
            "platforms": ["web", "ios", "android", "desktop"],
            "integrations": ["openai api"],
            "last_verified_at": "2026-08-08T00:00:00+00:00",
        },
        {
            "slug": "claude",
            "name": "Claude",
            "provider": "Anthropic",
            "description": "AI assistant focused on writing, analysis, and long-context reasoning tasks.",
            "website_url": "https://claude.ai",
            "logo_url": "https://www.anthropic.com/images/icons/favicon.ico",
            "category_slug": "ai-assistants",
            "pricing_model": "monthly",
            "pricing_amount": None,
            "pricing_currency": "USD",
            "pricing_period": "month",
            "has_free_plan": True,
            "has_free_trial": None,
            "trial_days": None,
            "pricing_notes": "Free and paid plans are available; verify exact tiers on provider pricing page.",
            "pricing_url": "https://www.anthropic.com/pricing",
            "use_cases": ["analysis", "writing", "knowledge work"],
            "features": ["conversational assistant", "document analysis", "project workflows"],
            "pros": ["strong long-form writing quality", "good document handling"],
            "cons": ["capabilities vary by plan tier"],
            "best_for": ["teams working with long documents"],
            "not_ideal_for": ["teams that require on-prem deployment in Stage 2 scope"],
            "why_letrusto_recommends": "Reliable assistant for teams prioritizing clarity and long-context work.",
            "tags": ["assistant", "analysis", "writing"],
            "platforms": ["web", "ios", "android"],
            "integrations": ["anthropic api"],
            "last_verified_at": "2026-08-08T00:00:00+00:00",
        },
        {
            "slug": "jasper",
            "name": "Jasper",
            "provider": "Jasper AI",
            "description": "AI writing platform for marketing teams creating campaigns and brand content.",
            "website_url": "https://www.jasper.ai",
            "logo_url": "https://www.jasper.ai/favicon.ico",
            "category_slug": "ai-writing",
            "pricing_model": "monthly",
            "pricing_amount": None,
            "pricing_currency": "USD",
            "pricing_period": "month",
            "has_free_plan": None,
            "has_free_trial": None,
            "trial_days": None,
            "pricing_notes": "Pricing and plan limits are provider-managed and may change.",
            "pricing_url": "https://www.jasper.ai/pricing",
            "use_cases": ["marketing copy", "campaign content", "brand voice writing"],
            "features": ["brand voice controls", "campaign drafting", "team collaboration"],
            "pros": ["marketing workflow focus", "team-oriented features"],
            "cons": ["cost may be high for solo creators"],
            "best_for": ["marketing teams with structured content operations"],
            "not_ideal_for": ["buyers needing a free always-on plan"],
            "why_letrusto_recommends": "Purpose-built writing workflows for marketing operations and teams.",
            "tags": ["writing", "marketing", "content"],
            "platforms": ["web"],
            "integrations": [],
            "last_verified_at": "2026-08-08T00:00:00+00:00",
        },
        {
            "slug": "grammarly",
            "name": "Grammarly",
            "provider": "Grammarly",
            "description": "AI writing assistant for grammar, clarity, tone, and communication quality.",
            "website_url": "https://www.grammarly.com",
            "logo_url": "https://www.grammarly.com/favicon.ico",
            "category_slug": "ai-writing",
            "pricing_model": "monthly",
            "pricing_amount": None,
            "pricing_currency": "USD",
            "pricing_period": "month",
            "has_free_plan": True,
            "has_free_trial": None,
            "trial_days": None,
            "pricing_notes": "Free and paid plans exist; enterprise offerings are separately configured.",
            "pricing_url": "https://www.grammarly.com/plans",
            "use_cases": ["editing", "professional communication", "tone alignment"],
            "features": ["grammar suggestions", "tone suggestions", "rewrite assistance"],
            "pros": ["easy day-to-day writing support", "broad app coverage"],
            "cons": ["advanced features require paid plans"],
            "best_for": ["teams improving writing quality across tools"],
            "not_ideal_for": ["buyers looking for long-form generative ideation only"],
            "why_letrusto_recommends": "Mature writing assistant with consistent quality improvements for daily communication.",
            "tags": ["writing", "editing", "productivity"],
            "platforms": ["web", "browser extension", "desktop", "mobile"],
            "integrations": ["google docs", "microsoft office"],
            "last_verified_at": "2026-08-08T00:00:00+00:00",
        },
        {
            "slug": "midjourney",
            "name": "Midjourney",
            "provider": "Midjourney",
            "description": "AI image generation tool used for concept art, visual ideation, and design exploration.",
            "website_url": "https://www.midjourney.com",
            "logo_url": "https://www.midjourney.com/favicon.ico",
            "category_slug": "ai-image-design",
            "pricing_model": "monthly",
            "pricing_amount": None,
            "pricing_currency": "USD",
            "pricing_period": "month",
            "has_free_plan": None,
            "has_free_trial": None,
            "trial_days": None,
            "pricing_notes": "Subscription plans are available; verify latest tier limits and prices on official pricing page.",
            "pricing_url": "https://www.midjourney.com/pricing",
            "use_cases": ["concept art", "creative exploration", "visual ideation"],
            "features": ["text-to-image generation", "style variation", "upscaling"],
            "pros": ["high-quality artistic output", "strong creative community"],
            "cons": ["workflow differs from traditional design tools"],
            "best_for": ["design teams exploring visual directions"],
            "not_ideal_for": ["teams needing deterministic output every run"],
            "why_letrusto_recommends": "Strong option for creative teams that prioritize concept exploration speed.",
            "tags": ["image", "design", "creative"],
            "platforms": ["web"],
            "integrations": [],
            "last_verified_at": "2026-08-08T00:00:00+00:00",
        },
        {
            "slug": "canva-magic-studio",
            "name": "Canva Magic Studio",
            "provider": "Canva",
            "description": "Canva AI feature set for creating and editing marketing visuals and presentations.",
            "website_url": "https://www.canva.com/magic-studio/",
            "logo_url": "https://www.canva.com/favicon.ico",
            "category_slug": "ai-image-design",
            "pricing_model": "monthly",
            "pricing_amount": None,
            "pricing_currency": "USD",
            "pricing_period": "month",
            "has_free_plan": True,
            "has_free_trial": None,
            "trial_days": None,
            "pricing_notes": "Feature access varies by Free, Pro, and Teams plans.",
            "pricing_url": "https://www.canva.com/pricing/",
            "use_cases": ["social creatives", "presentations", "marketing assets"],
            "features": ["ai-assisted design", "template workflows", "brand kit support"],
            "pros": ["low learning curve", "collaborative editor"],
            "cons": ["advanced brand controls tied to paid plans"],
            "best_for": ["teams needing fast design execution"],
            "not_ideal_for": ["teams requiring advanced raster editing depth"],
            "why_letrusto_recommends": "Combines fast design workflows with accessible collaboration for non-design teams.",
            "tags": ["design", "image", "marketing"],
            "platforms": ["web", "ios", "android"],
            "integrations": ["google drive", "dropbox"],
            "last_verified_at": "2026-08-08T00:00:00+00:00",
        },
        {
            "slug": "runway",
            "name": "Runway",
            "provider": "Runway",
            "description": "AI video creation and editing platform for rapid content production workflows.",
            "website_url": "https://runwayml.com",
            "logo_url": "https://runwayml.com/favicon.ico",
            "category_slug": "ai-video-audio",
            "pricing_model": "monthly",
            "pricing_amount": None,
            "pricing_currency": "USD",
            "pricing_period": "month",
            "has_free_plan": True,
            "has_free_trial": None,
            "trial_days": None,
            "pricing_notes": "Credit and plan structure changes over time; verify latest details at official pricing page.",
            "pricing_url": "https://runwayml.com/pricing",
            "use_cases": ["video generation", "video editing", "creative production"],
            "features": ["text-to-video", "video editing tools", "team workspaces"],
            "pros": ["rapid concept-to-video iteration", "strong creator workflows"],
            "cons": ["high-volume production can require paid credits"],
            "best_for": ["content teams creating short-form video"],
            "not_ideal_for": ["teams requiring traditional NLE-only pipelines"],
            "why_letrusto_recommends": "Useful for teams testing AI-native video workflows quickly.",
            "tags": ["video", "creative", "editing"],
            "platforms": ["web"],
            "integrations": [],
            "last_verified_at": "2026-08-08T00:00:00+00:00",
        },
        {
            "slug": "elevenlabs",
            "name": "ElevenLabs",
            "provider": "ElevenLabs",
            "description": "AI voice platform for speech generation and voice-centric content workflows.",
            "website_url": "https://elevenlabs.io",
            "logo_url": "https://elevenlabs.io/favicon.ico",
            "category_slug": "ai-video-audio",
            "pricing_model": "monthly",
            "pricing_amount": None,
            "pricing_currency": "USD",
            "pricing_period": "month",
            "has_free_plan": True,
            "has_free_trial": None,
            "trial_days": None,
            "pricing_notes": "Plans are usage-based; verify current limits and pricing on provider site.",
            "pricing_url": "https://elevenlabs.io/pricing",
            "use_cases": ["voiceovers", "audio narration", "speech workflows"],
            "features": ["text-to-speech", "voice synthesis", "voice library"],
            "pros": ["high-quality speech output", "API availability"],
            "cons": ["advanced usage may require higher tiers"],
            "best_for": ["teams producing narration-heavy content"],
            "not_ideal_for": ["teams needing offline-only speech generation"],
            "why_letrusto_recommends": "Strong fit for audio-first teams needing scalable voice generation.",
            "tags": ["audio", "voice", "speech"],
            "platforms": ["web"],
            "integrations": ["elevenlabs api"],
            "last_verified_at": "2026-08-08T00:00:00+00:00",
        },
        {
            "slug": "github-copilot",
            "name": "GitHub Copilot",
            "provider": "GitHub",
            "description": "AI coding assistant integrated into popular editors and GitHub workflows.",
            "website_url": "https://github.com/features/copilot",
            "logo_url": "https://github.githubassets.com/favicons/favicon.svg",
            "category_slug": "ai-coding-developer-tools",
            "pricing_model": "monthly",
            "pricing_amount": None,
            "pricing_currency": "USD",
            "pricing_period": "month",
            "has_free_plan": None,
            "has_free_trial": None,
            "trial_days": None,
            "pricing_notes": "Individual, Business, and Enterprise plans are available; verify current prices on GitHub pricing page.",
            "pricing_url": "https://github.com/features/copilot/plans",
            "use_cases": ["code completion", "pull request assistance", "developer productivity"],
            "features": ["in-editor assistance", "chat", "multi-file coding support"],
            "pros": ["deep IDE integration", "developer workflow alignment"],
            "cons": ["best results require code review discipline"],
            "best_for": ["engineering teams improving coding throughput"],
            "not_ideal_for": ["teams without secure code review controls"],
            "why_letrusto_recommends": "Widely adopted coding assistant with mature ecosystem integration.",
            "tags": ["coding", "developer", "productivity"],
            "platforms": ["vscode", "jetbrains", "neovim", "github"],
            "integrations": ["github"],
            "last_verified_at": "2026-08-08T00:00:00+00:00",
        },
        {
            "slug": "cursor",
            "name": "Cursor",
            "provider": "Cursor",
            "description": "AI-first code editor designed for pair-programming style software development.",
            "website_url": "https://www.cursor.com",
            "logo_url": "https://www.cursor.com/favicon.ico",
            "category_slug": "ai-coding-developer-tools",
            "pricing_model": "monthly",
            "pricing_amount": None,
            "pricing_currency": "USD",
            "pricing_period": "month",
            "has_free_plan": True,
            "has_free_trial": None,
            "trial_days": None,
            "pricing_notes": "Free and paid plans are offered; verify latest plan details on official pricing page.",
            "pricing_url": "https://www.cursor.com/pricing",
            "use_cases": ["code generation", "refactoring", "debugging support"],
            "features": ["ai-native editor", "codebase chat", "agent-style coding"],
            "pros": ["workflow optimized for AI-assisted coding", "fast iteration loop"],
            "cons": ["team policies may require setup before adoption"],
            "best_for": ["developers adopting AI-assisted coding workflows"],
            "not_ideal_for": ["teams restricted to locked-down managed IDE stacks"],
            "why_letrusto_recommends": "Strong productivity fit for teams exploring AI-first editor workflows.",
            "tags": ["coding", "developer", "editor"],
            "platforms": ["desktop"],
            "integrations": ["git"],
            "last_verified_at": "2026-08-08T00:00:00+00:00",
        },
    ]

    insert_sql = sa.text(
        """
        INSERT INTO ai_tools (
            id, slug, name, provider, description, website_url, logo_url, category_id, lifecycle_status,
            pricing_model, pricing_amount, pricing_currency, pricing_period, has_free_plan, has_free_trial,
            trial_days, pricing_notes, pricing_url, affiliate_available, affiliate_url, letrusto_score,
            why_letrusto_recommends, use_cases, features, pros, cons, best_for, not_ideal_for,
            tags, platforms, integrations, last_verified_at
        ) VALUES (
            :id, :slug, :name, :provider, :description, :website_url, :logo_url, :category_id, 'published',
            :pricing_model, :pricing_amount, :pricing_currency, :pricing_period, :has_free_plan, :has_free_trial,
            :trial_days, :pricing_notes, :pricing_url, false, NULL, NULL,
            :why_letrusto_recommends, CAST(:use_cases AS JSON), CAST(:features AS JSON), CAST(:pros AS JSON),
            CAST(:cons AS JSON), CAST(:best_for AS JSON), CAST(:not_ideal_for AS JSON), CAST(:tags AS JSON),
            CAST(:platforms AS JSON), CAST(:integrations AS JSON), :last_verified_at
        )
        """
    )

    for tool in tools:
        conn.execute(
            insert_sql,
            {
                "slug": tool["slug"],
                "id": str(uuid.uuid4()),
                "name": tool["name"],
                "provider": tool["provider"],
                "description": tool["description"],
                "website_url": tool["website_url"],
                "logo_url": tool["logo_url"],
                "category_id": category_ids[tool["category_slug"]],
                "pricing_model": tool["pricing_model"],
                "pricing_amount": tool["pricing_amount"],
                "pricing_currency": tool["pricing_currency"],
                "pricing_period": tool["pricing_period"],
                "has_free_plan": tool["has_free_plan"],
                "has_free_trial": tool["has_free_trial"],
                "trial_days": tool["trial_days"],
                "pricing_notes": tool["pricing_notes"],
                "pricing_url": tool["pricing_url"],
                "why_letrusto_recommends": tool["why_letrusto_recommends"],
                "use_cases": json.dumps(tool["use_cases"]),
                "features": json.dumps(tool["features"]),
                "pros": json.dumps(tool["pros"]),
                "cons": json.dumps(tool["cons"]),
                "best_for": json.dumps(tool["best_for"]),
                "not_ideal_for": json.dumps(tool["not_ideal_for"]),
                "tags": json.dumps(tool["tags"]),
                "platforms": json.dumps(tool["platforms"]),
                "integrations": json.dumps(tool["integrations"]),
                "last_verified_at": tool["last_verified_at"],
            },
        )


def downgrade() -> None:
    op.drop_index("ix_ai_tools_last_verified", table_name="ai_tools")
    op.drop_index("ix_ai_tools_category_status", table_name="ai_tools")
    op.drop_index("ix_ai_tools_lifecycle_status", table_name="ai_tools")
    op.drop_index("ix_ai_tools_provider", table_name="ai_tools")
    op.drop_index("ix_ai_tools_name", table_name="ai_tools")
    op.drop_index("ix_ai_tools_slug", table_name="ai_tools")
    op.drop_table("ai_tools")

    op.drop_index("ix_ai_tool_categories_slug", table_name="ai_tool_categories")
    op.drop_table("ai_tool_categories")
