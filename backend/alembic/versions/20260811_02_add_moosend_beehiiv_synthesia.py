"""add Moosend, beehiiv, and Synthesia to AI tools catalog

Revision ID: 20260811_02
Revises: 20260811_01
Create Date: 2026-08-11
"""

from collections.abc import Sequence
import uuid

from alembic import op
import sqlalchemy as sa

revision: str = "20260811_02"
down_revision: str | None = "20260811_01"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    conn = op.get_bind()

    cat_marketing = conn.execute(
        sa.text("SELECT id FROM ai_tool_categories WHERE slug = 'marketing-automation'")
    ).fetchone()
    cat_video = conn.execute(
        sa.text("SELECT id FROM ai_tool_categories WHERE slug = 'ai-video-audio'")
    ).fetchone()

    marketing_id = cat_marketing.id  # type: ignore[union-attr]
    video_id = cat_video.id  # type: ignore[union-attr]

    tools = [
        {
            "id": str(uuid.uuid4()),
            "slug": "moosend",
            "name": "Moosend",
            "provider": "Moosend",
            "description": (
                "Email marketing and automation platform with drag-and-drop campaign builder, "
                "landing pages, subscription forms, and audience segmentation. Designed for "
                "businesses that need straightforward email marketing without enterprise complexity."
            ),
            "website_url": "https://moosend.com",
            "logo_url": None,
            "category_id": marketing_id,
            "lifecycle_status": "published",
            "pricing_model": "monthly",
            "pricing_amount": None,
            "pricing_currency": "USD",
            "pricing_period": "month",
            "has_free_plan": None,
            "has_free_trial": True,
            "trial_days": 30,
            "pricing_notes": "Offers a 30-day free trial. Paid plans are usage-based by subscriber count. Verify current pricing at moosend.com/pricing.",
            "pricing_url": "https://moosend.com/pricing/",
            "affiliate_available": True,
            "affiliate_url": "https://trymoo.moosend.com/kj491db9y05q",
            "letrusto_score": None,
            "why_letrusto_recommends": (
                "Moosend offers a clean email marketing experience with automation workflows "
                "and landing pages at a competitive price point. A practical option for teams "
                "that need email marketing without the complexity of enterprise platforms."
            ),
            "use_cases": '["email marketing campaigns", "marketing automation workflows", "newsletter management", "landing page creation", "audience segmentation"]',
            "features": '["drag-and-drop email editor", "marketing automation workflows", "landing page builder", "subscription forms", "audience segmentation", "A/B testing", "real-time analytics", "transactional emails"]',
            "pros": '["clean and intuitive email editor", "automation workflows included in paid plans", "landing page builder included", "competitive pricing for small-to-mid lists", "30-day free trial available"]',
            "cons": '["smaller ecosystem compared to Mailchimp or HubSpot", "advanced CRM features are limited", "template library is more modest than larger competitors"]',
            "best_for": '["small-to-medium businesses focused on email marketing", "teams that want automation without enterprise pricing", "newsletter operators needing a simple platform"]',
            "not_ideal_for": '["enterprises needing a full CRM suite", "teams requiring deep third-party integrations beyond email"]',
            "tags": '["email marketing", "automation", "newsletter", "landing pages", "saas"]',
            "platforms": '["web"]',
            "integrations": '["zapier", "wordpress", "woocommerce", "salesforce"]',
            "last_verified_at": "2026-08-11T00:00:00+00:00",
        },
        {
            "id": str(uuid.uuid4()),
            "slug": "beehiiv",
            "name": "beehiiv",
            "provider": "beehiiv",
            "description": (
                "Newsletter platform built for creators and media operators. Combines publishing, "
                "growth tools, monetization, and audience analytics in a single platform designed "
                "to help newsletter businesses scale."
            ),
            "website_url": "https://www.beehiiv.com",
            "logo_url": None,
            "category_id": marketing_id,
            "lifecycle_status": "published",
            "pricing_model": "monthly",
            "pricing_amount": None,
            "pricing_currency": "USD",
            "pricing_period": "month",
            "has_free_plan": True,
            "has_free_trial": None,
            "trial_days": None,
            "pricing_notes": "Free plan available (up to a subscriber limit). Paid plans scale by features and subscriber count. Verify current pricing at beehiiv.com/pricing.",
            "pricing_url": "https://www.beehiiv.com/pricing",
            "affiliate_available": True,
            "affiliate_url": "https://www.beehiiv.com/?via=letrusto",
            "letrusto_score": None,
            "why_letrusto_recommends": (
                "beehiiv is purpose-built for newsletter creators who want publishing, growth, "
                "and monetization tools in one place. The free plan makes it accessible, and the "
                "growth-focused features (referral programs, recommendations network) set it apart "
                "from general email marketing platforms."
            ),
            "use_cases": '["newsletter publishing", "audience growth and referral programs", "newsletter monetization", "content distribution", "subscriber analytics"]',
            "features": '["newsletter editor and publishing", "built-in referral program", "recommendation network for growth", "monetization tools (ads, paid subscriptions)", "custom website and landing pages", "audience segmentation", "analytics dashboard", "custom domains"]',
            "pros": '["free plan available for new creators", "built-in growth tools (referrals, recommendations)", "monetization features included natively", "modern editor and publishing experience", "designed specifically for newsletter businesses"]',
            "cons": '["focused on newsletters — not a general email marketing platform", "advanced automation is less developed than dedicated marketing tools", "paid plan pricing increases with subscriber count"]',
            "best_for": '["newsletter creators and independent publishers", "media operators building audience-driven businesses", "creators who want built-in monetization tools"]',
            "not_ideal_for": '["e-commerce businesses needing transactional email", "teams requiring complex marketing automation workflows", "organizations that need a full CRM alongside email"]',
            "tags": '["newsletter", "creator tools", "email", "monetization", "growth", "publishing"]',
            "platforms": '["web"]',
            "integrations": '["zapier", "wordpress", "custom api"]',
            "last_verified_at": "2026-08-11T00:00:00+00:00",
        },
        {
            "id": str(uuid.uuid4()),
            "slug": "synthesia",
            "name": "Synthesia",
            "provider": "Synthesia",
            "description": (
                "AI video generation platform that creates professional videos from text using "
                "AI avatars. Designed for corporate training, marketing, and internal communications "
                "teams that need to produce video content without cameras, studios, or actors."
            ),
            "website_url": "https://www.synthesia.io",
            "logo_url": None,
            "category_id": video_id,
            "lifecycle_status": "published",
            "pricing_model": "monthly",
            "pricing_amount": None,
            "pricing_currency": "USD",
            "pricing_period": "month",
            "has_free_plan": None,
            "has_free_trial": None,
            "trial_days": None,
            "pricing_notes": "Offers Starter, Creator, and Enterprise plans. Verify current pricing at synthesia.io/pricing.",
            "pricing_url": "https://www.synthesia.io/pricing",
            "affiliate_available": True,
            "affiliate_url": "https://www.synthesia.io/?via=basavanna",
            "letrusto_score": None,
            "why_letrusto_recommends": (
                "Synthesia removes the production overhead of video creation. For teams that need "
                "training videos, product explainers, or internal communications at scale, it "
                "provides a practical text-to-video workflow with multilingual AI avatars."
            ),
            "use_cases": '["corporate training videos", "product explainer videos", "internal communications", "marketing video content", "multilingual video production"]',
            "features": '["AI avatars for video presentation", "text-to-video generation", "140+ language support", "screen recording integration", "custom avatar creation (Enterprise)", "brand kit and templates", "video editing and collaboration"]',
            "pros": '["eliminates need for cameras, studios, and actors", "fast video production from text scripts", "broad language and avatar support", "useful for scaling training and onboarding content", "SOC 2 and GDPR compliant"]',
            "cons": '["AI avatar quality may not match live presenter feel for all use cases", "advanced custom avatars require Enterprise plan", "not designed for cinematic or creative video production", "pricing details require verification on provider site"]',
            "best_for": '["L&D and training teams producing educational video at scale", "marketing teams needing quick explainer or promotional videos", "organizations with multilingual communication needs"]',
            "not_ideal_for": '["creative agencies producing cinematic content", "teams needing real-time live video or streaming", "individual creators with very small video volume"]',
            "tags": '["video generation", "ai avatars", "training", "text-to-video", "enterprise", "saas"]',
            "platforms": '["web"]',
            "integrations": '["powerpoint", "lms platforms"]',
            "last_verified_at": "2026-08-11T00:00:00+00:00",
        },
    ]

    for tool in tools:
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
            tool,
        )


def downgrade() -> None:
    conn = op.get_bind()
    for slug in ("moosend", "beehiiv", "synthesia"):
        conn.execute(sa.text("DELETE FROM ai_tools WHERE slug = :slug"), {"slug": slug})
