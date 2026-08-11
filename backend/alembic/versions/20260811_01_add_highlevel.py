"""add HighLevel to AI tools catalog

Revision ID: 20260811_01
Revises: 20260810_01
Create Date: 2026-08-11
"""

from collections.abc import Sequence
import uuid

from alembic import op
import sqlalchemy as sa

revision: str = "20260811_01"
down_revision: str | None = "20260810_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()

    # Add Marketing & Automation category
    conn.execute(
        sa.text(
            "INSERT INTO ai_tool_categories (name, slug, position) "
            "VALUES (:name, :slug, :position) "
            "ON CONFLICT (slug) DO NOTHING"
        ),
        {"name": "Marketing & Automation", "slug": "marketing-automation", "position": 6},
    )

    cat_row = conn.execute(
        sa.text("SELECT id FROM ai_tool_categories WHERE slug = :slug"),
        {"slug": "marketing-automation"},
    ).fetchone()
    category_id = cat_row.id  # type: ignore[union-attr]

    tool_id = str(uuid.uuid4())
    conn.execute(
        sa.text(
            """INSERT INTO ai_tools (
                id, slug, name, provider, description, website_url, logo_url,
                category_id, lifecycle_status,
                pricing_model, pricing_amount, pricing_currency, pricing_period,
                has_free_plan, has_free_trial, trial_days,
                pricing_notes, pricing_url,
                affiliate_available, affiliate_url,
                letrusto_score, why_letrusto_recommends,
                use_cases, features, pros, cons, best_for, not_ideal_for,
                tags, platforms, integrations, last_verified_at
            ) VALUES (
                :id, :slug, :name, :provider, :description, :website_url, :logo_url,
                :category_id, :lifecycle_status,
                :pricing_model, :pricing_amount, :pricing_currency, :pricing_period,
                :has_free_plan, :has_free_trial, :trial_days,
                :pricing_notes, :pricing_url,
                :affiliate_available, :affiliate_url,
                :letrusto_score, :why_letrusto_recommends,
                :use_cases, :features, :pros, :cons, :best_for, :not_ideal_for,
                :tags, :platforms, :integrations, :last_verified_at
            )"""
        ),
        {
            "id": tool_id,
            "slug": "highlevel",
            "name": "HighLevel",
            "provider": "HighLevel",
            "description": (
                "All-in-one AI-powered marketing, CRM, and business automation platform "
                "designed for agencies and small-to-medium businesses. Consolidates lead capture, "
                "nurturing, pipeline management, appointment booking, email and SMS marketing, "
                "website/funnel building, and reputation management into a single system."
            ),
            "website_url": "https://www.gohighlevel.com",
            "logo_url": None,
            "category_id": category_id,
            "lifecycle_status": "published",
            "pricing_model": "monthly",
            "pricing_amount": 97,
            "pricing_currency": "USD",
            "pricing_period": "month",
            "has_free_plan": False,
            "has_free_trial": True,
            "trial_days": 14,
            "pricing_notes": (
                "Starter plan at $97/month; Unlimited plan at $297/month. "
                "14-day free trial available. Verify current pricing at gohighlevel.com."
            ),
            "pricing_url": "https://www.gohighlevel.com/pricing",
            "affiliate_available": True,
            "affiliate_url": None,
            "letrusto_score": None,
            "why_letrusto_recommends": (
                "HighLevel consolidates CRM, email marketing, SMS, funnel building, "
                "appointment scheduling, and automation into one platform. For agencies and "
                "service businesses currently paying for multiple separate tools, it can "
                "significantly reduce software costs and complexity."
            ),
            "use_cases": '["lead capture and nurturing", "appointment booking and scheduling", "email and SMS marketing campaigns", "sales pipeline management", "website and funnel building", "reputation and review management", "client reporting for agencies"]',
            "features": '["CRM and pipeline management", "email and SMS marketing", "website and funnel builder", "appointment scheduling", "AI-powered voice and conversation tools", "workflow automation", "forms, surveys, and quizzes", "social media planner", "call tracking", "white-label for agencies"]',
            "pros": '["replaces multiple software subscriptions with one platform", "strong automation and workflow capabilities", "white-label option for agencies to resell", "14-day free trial with no obligation", "active community and ecosystem", "AI features integrated across the platform"]',
            "cons": '["learning curve due to the breadth of features", "interface can feel complex for non-technical users", "Starter plan limits sub-accounts to 3", "not purpose-built for enterprise-scale CRM needs", "pricing may be high for solo freelancers with simple needs"]',
            "best_for": '["marketing agencies managing multiple clients", "small-to-medium businesses wanting to consolidate tools", "service businesses needing CRM and appointment booking", "teams that want marketing automation without multiple subscriptions"]',
            "not_ideal_for": '["enterprise organizations with existing Salesforce or HubSpot investments", "solo creators who only need email marketing", "teams that prefer best-of-breed individual tools over an all-in-one platform"]',
            "tags": '["crm", "marketing automation", "lead generation", "funnel builder", "agency", "saas", "all-in-one"]',
            "platforms": '["web", "ios", "android"]',
            "integrations": '["stripe", "google calendar", "facebook ads", "google ads", "zapier", "quickbooks", "mailgun", "twilio"]',
            "last_verified_at": "2026-08-11T00:00:00+00:00",
        },
    )


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM ai_tools WHERE slug = 'highlevel'"))
    conn.execute(sa.text("DELETE FROM ai_tool_categories WHERE slug = 'marketing-automation'"))
