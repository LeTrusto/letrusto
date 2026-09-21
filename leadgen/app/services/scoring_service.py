from typing import Any


def score_lead(lead: dict[str, Any]) -> tuple[int, str, list[str]]:
    if lead.get("ecommerce_detected") or lead.get("business_detected") or lead.get("products_detected") or lead.get("reviews_detected"):
        score = 0
        reasons: list[str] = []
        for field, points, reason in [
            ("ecommerce_detected", 30, "ecommerce detected"),
            ("business_detected", 25, "active B2B/SaaS business signals detected"),
            ("products_detected", 20, "products detected"),
            ("reviews_detected", 20, "customer reviews or client proof detected"),
            ("business_email", 10, "public business email found"),
        ]:
            if lead.get(field):
                score += points; reasons.append(f"+{points} {reason}")
        if lead.get("reviews_detected") and lead.get("ecommerce_detected"):
            score += 15; reasons.append("+15 social proof opportunity detected")
        if lead.get("crawl_status") == "complete":
            score += 5; reasons.append("+5 website active")
        score = max(0, min(100, score)); grade = "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D"
        return score, grade, reasons
    score = 0
    reasons: list[str] = []
    checks = [
        ("website", 20, "active business website"),
        ("niche", 5, "target niche identified"),
        ("review_signal", 15, "visible customer reviews"),
        ("social_proof_signal", 10, "testimonials or social proof"),
        ("contact_name", 10, "identifiable founder or owner"),
        ("business_email", 10, "public business email"),
        ("contact_role", 10, "decision-maker role identified"),
        ("why_fit", 5, "clear social-proof opportunity"),
    ]
    for field, points, reason in checks:
        if str(lead.get(field, "")).strip():
            score += points
            reasons.append(f"+{points} {reason}")
    if str(lead.get("review_count_signal", "")).strip():
        score += 5
        reasons.append("+5 review activity signal")
    if lead.get("do_not_contact"):
        return 0, "D", ["-100 do_not_contact"]
    if str(lead.get("notes", "")).lower().find("dead") >= 0:
        score -= 30
        reasons.append("-30 dead or inactive website")
    if str(lead.get("notes", "")).lower().find("duplicate") >= 0:
        score -= 20
        reasons.append("-20 duplicate")
    score = max(0, min(100, score))
    grade = "A" if score >= 80 else "B" if score >= 60 else "C" if score >= 40 else "D"
    return score, grade, reasons
