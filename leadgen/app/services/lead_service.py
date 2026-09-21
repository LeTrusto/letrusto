from datetime import datetime, timedelta
from urllib.parse import urlparse
from .db import connect
from .scoring_service import score_lead


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def normalize_website(value: str) -> str:
    value = (value or "").strip().lower()
    if not value: return ""
    parsed = urlparse(value if "://" in value else "https://" + value)
    return (parsed.netloc or parsed.path).removeprefix("www.").rstrip("/")


def normalize_email(value: str) -> str:
    return (value or "").strip().lower()


def row_dict(row):
    return dict(row) if row else None


def duplicate_exists(connection, lead: dict, exclude_id: int | None = None) -> bool:
    website, email = normalize_website(lead.get("website", "")), normalize_email(lead.get("business_email", ""))
    query = "SELECT id FROM leads WHERE (website != '' AND website = ?) OR (business_email != '' AND lower(business_email) = ?)"
    params = [website, email]
    if exclude_id:
        query += " AND id != ?"; params.append(exclude_id)
    existing = connection.execute(query, params).fetchone()
    return existing is not None


def create_lead(connection, lead: dict) -> int:
    if not lead.get("company_name", "").strip(): raise ValueError("company_name is required")
    if duplicate_exists(connection, lead): raise ValueError("duplicate lead")
    timestamp = now(); score, grade, _ = score_lead(lead)
    values = {"company_name": "", "website": "", "contact_name": "", "contact_role": "", "business_email": "", "country": "", "city": "", "niche": "", "linkedin_url": "", "source": "OTHER", "source_url": "", "review_signal": "", "review_count_signal": "", "social_proof_signal": "", "why_fit": "", "lead_score": score, "lead_grade": grade, "status": "NEW", "email_status": "NOT_SENT", "reply_status": "NONE", "trial_status": "NONE", "installation_status": "NONE", "paid_status": "NONE", "notes": "", "do_not_contact": 0, "research_status": "NOT_STARTED", "personalization_status": "NOT_READY", "qualification_reason": "", "personalization_facts": "", "suggested_subject": "", "suggested_body": "", "ecommerce_detected": 0, "products_detected": 0, "reviews_detected": 0, "crawl_status": "NOT_STARTED", "discovery_run_id": None, "created_at": timestamp, "updated_at": timestamp}
    values.update({k: v for k, v in lead.items() if k in values and v is not None})
    values["lead_score"], values["lead_grade"], _ = score_lead(values)
    columns = ",".join(values); cursor = connection.execute(f"INSERT INTO leads ({columns}) VALUES ({','.join('?' for _ in values)})", list(values.values())); connection.commit(); return cursor.lastrowid


def update_lead(connection, lead_id: int, changes: dict) -> None:
    current = row_dict(connection.execute("SELECT * FROM leads WHERE id=?", (lead_id,)).fetchone())
    if not current: raise ValueError("lead not found")
    if changes.get("status") == "DO_NOT_CONTACT": changes.update({"do_not_contact": 1, "email_status": "SUPPRESSED"})
    merged = {**current, **changes}; score, grade, _ = score_lead(merged); changes.update({"lead_score": score, "lead_grade": grade, "updated_at": now()})
    assignments = ",".join(f"{key}=?" for key in changes if key in current and key != "id")
    connection.execute(f"UPDATE leads SET {assignments} WHERE id=?", [changes[key] for key in changes if key in current and key != "id"] + [lead_id]); connection.commit()


def list_leads(connection, status: str | None = None) -> list[dict]:
    query = "SELECT * FROM leads"; args = []
    if status: query += " WHERE status=?"; args.append(status)
    query += " ORDER BY lead_score DESC, created_at ASC"
    return [dict(row) for row in connection.execute(query, args).fetchall()]


def get_lead(connection, lead_id: int) -> dict | None: return row_dict(connection.execute("SELECT * FROM leads WHERE id=?", (lead_id,)).fetchone())


def mark_sent(connection, lead_id: int, followup_days: int = 4) -> None:
    contacted = datetime.now(); update_lead(connection, lead_id, {"status": "CONTACTED", "email_status": "SENT", "last_contacted_at": contacted.isoformat(timespec="seconds"), "next_followup_at": (contacted + timedelta(days=followup_days)).isoformat(timespec="seconds")})


def dashboard(connection) -> dict:
    rows = list_leads(connection); counts = {status: sum(1 for row in rows if row["status"] == status) for status in ["NEW", "QUALIFIED", "READY_TO_CONTACT", "CONTACTED", "FOLLOW_UP_1", "REPLIED", "INTERESTED", "TRIAL", "INSTALLED", "PAID"]}
    today = datetime.now().date().isoformat(); sent_today = sum(1 for row in rows if (row.get("last_contacted_at") or "").startswith(today)); replies = sum(1 for row in rows if row["reply_status"] not in ("", "NONE"))
    return {**counts, "total": len(rows), "sent_today": sent_today, "replies": replies, "reply_rate": round(replies / sent_today * 100, 1) if sent_today else 0, "followup_due": sum(1 for row in rows if row["next_followup_at"] and row["next_followup_at"] <= datetime.now().isoformat(timespec="minutes"))}
