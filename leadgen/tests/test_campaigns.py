import pytest
from app.services.db import connect
from app.services.lead_service import create_lead, get_lead
from app.services.campaign_service import create_campaign, dry_run, mark_send_result, queue_email, set_campaign_status, today_sent, classify_reply
from app.services.gmail_service import GmailOAuth


def good_lead():
    return {'company_name':'Synthetic Store','website':'https://synthetic.example','business_email':'hello@synthetic.example','country':'India','niche':'fashion','contact_name':'Asha','review_signal':'Reviews visible on product pages','why_fit':'Existing reviews are not prominent'}


def test_campaign_dry_run_limit_and_send_guard(tmp_path):
    db = connect(tmp_path/'campaign.sqlite3'); lead_id = create_lead(db, good_lead()); campaign_id = create_campaign(db, {'name':'India Fashion','target_country':'India','target_niche':'fashion','daily_send_limit':1});
    assert len(dry_run(db, campaign_id, 'Founder')) == 1
    with pytest.raises(ValueError, match='not enabled'): queue_email(db, campaign_id, lead_id, 'Founder')
    set_campaign_status(db, campaign_id, 'ENABLED'); log = queue_email(db, campaign_id, lead_id, 'Founder'); assert log['recipient'] == 'hello@synthetic.example'
    with pytest.raises(ValueError, match='duplicate'): queue_email(db, campaign_id, lead_id, 'Founder')
    mark_send_result(db, log['id'], 'SENT', 'synthetic-message'); assert today_sent(db, campaign_id) == 1; assert get_lead(db, lead_id)['status'] == 'CONTACTED'
    db.close()


def test_unsubscribe_stops_future_contact(tmp_path):
    db = connect(tmp_path/'reply.sqlite3'); lead_id = create_lead(db, good_lead()); classify_reply(db, lead_id, 'UNSUBSCRIBE'); saved = get_lead(db, lead_id); assert saved['status'] == 'DO_NOT_CONTACT' and saved['do_not_contact'] == 1; db.close()


def test_oauth_is_disabled_without_files(tmp_path, monkeypatch):
    monkeypatch.setenv('GMAIL_CREDENTIALS_FILE', str(tmp_path/'missing.json')); monkeypatch.setenv('GMAIL_TOKEN_FILE', str(tmp_path/'missing-token.json'))
    status = GmailOAuth().status(); assert status['authorized'] is False


def test_followup_is_explicitly_scheduled_and_stops(tmp_path):
    db = connect(tmp_path/'followup.sqlite3'); lead_id = create_lead(db, good_lead()); campaign_id = create_campaign(db, {'name':'Followups'}); set_campaign_status(db, campaign_id, 'ENABLED')
    dry_run(db, campaign_id, 'Founder')
    initial = queue_email(db, campaign_id, lead_id, 'Founder'); mark_send_result(db, initial['id'], 'SENT')
    first = queue_email(db, campaign_id, lead_id, 'Founder', 1); mark_send_result(db, first['id'], 'SENT')
    second = queue_email(db, campaign_id, lead_id, 'Founder', 2); mark_send_result(db, second['id'], 'SENT')
    assert get_lead(db, lead_id)['status'] == 'NO_RESPONSE'
    db.close()
