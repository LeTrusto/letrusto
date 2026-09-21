from datetime import datetime
from pathlib import Path

import pytest

from app.services.db import connect
from app.services.export_service import parse_csv, rows_to_csv
from app.services.lead_service import create_lead, dashboard, get_lead, mark_sent, update_lead
from app.services.scoring_service import score_lead
from app.services.template_service import gmail_compose_url, render_email


@pytest.fixture
def db(tmp_path: Path):
    connection = connect(tmp_path / "test.sqlite3")
    yield connection
    connection.close()


def lead(**overrides):
    values = {"company_name": "North Star Apparel", "website": "https://northstar.example", "business_email": "hello@northstar.example", "contact_name": "Asha", "contact_role": "Founder", "niche": "Apparel", "review_signal": "Reviews visible on product pages", "social_proof_signal": "Customer stories in footer", "why_fit": "Reviews are not prominent on the home page"}
    values.update(overrides)
    return values


def test_create_update_and_duplicate(db):
    lead_id = create_lead(db, lead())
    assert get_lead(db, lead_id)["lead_grade"] == "A"
    with pytest.raises(ValueError, match="duplicate"):
        create_lead(db, lead(company_name="Copy", contact_name="Other"))
    update_lead(db, lead_id, {"status": "QUALIFIED", "notes": "verified"})
    assert get_lead(db, lead_id)["status"] == "QUALIFIED"
    assert get_lead(db, lead_id)["notes"] == "verified"


def test_scoring_and_do_not_contact():
    score, grade, reasons = score_lead(lead())
    assert score == 85 and grade == "A" and reasons
    score, grade, reasons = score_lead({"company_name": "Suppressed", "do_not_contact": 1})
    assert (score, grade) == (0, "D")


def test_csv_import_export(db):
    rows = parse_csv("Company,Website,Email,Founder,Niche\nExample Store,example.com,hello@example.com,Sam,Beauty\n")
    assert rows[0]["company_name"] == "Example Store"
    lead_id = create_lead(db, rows[0])
    exported = rows_to_csv([get_lead(db, lead_id)])
    assert "Example Store" in exported and "hello@example.com" in exported


def test_personalization_and_gmail_url():
    subject, body = render_email(lead(), "Founder")
    assert subject == "Quick idea for North Star Apparel"
    assert "Reviews visible on product pages" in body
    assert "don't want to receive" in body
    url = gmail_compose_url("hello@example.com", subject, body)
    assert url.startswith("https://mail.google.com/mail/?view=cm")
    assert "hello%40example.com" in url


def test_status_transition_followup_and_daily_metrics(db):
    lead_id = create_lead(db, lead())
    mark_sent(db, lead_id)
    saved = get_lead(db, lead_id)
    assert saved["status"] == "CONTACTED"
    assert saved["email_status"] == "SENT"
    assert saved["next_followup_at"]
    metrics = dashboard(db)
    assert metrics["CONTACTED"] == 1 and metrics["sent_today"] == 1


def test_suppression_is_preserved(db):
    lead_id = create_lead(db, lead())
    update_lead(db, lead_id, {"status": "DO_NOT_CONTACT", "do_not_contact": 1})
    saved = get_lead(db, lead_id)
    assert saved["status"] == "DO_NOT_CONTACT"
    assert saved["email_status"] == "SUPPRESSED"
