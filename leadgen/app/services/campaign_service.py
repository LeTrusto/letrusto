from datetime import datetime, timedelta
import re
from .lead_service import get_lead, list_leads, now
from .template_service import render_email

CAMPAIGN_STATUSES = ['DRAFT', 'PAUSED', 'ENABLED', 'COMPLETED']
SEND_STATUSES = ['QUEUED', 'SENT', 'BOUNCED', 'FAILED', 'REPLIED', 'UNSUBSCRIBED', 'DO_NOT_CONTACT']


def create_campaign(connection, values: dict) -> int:
    name = (values.get('name') or '').strip()
    if not name: raise ValueError('campaign name is required')
    timestamp = now()
    cursor = connection.execute('INSERT INTO campaigns (name,target_niche,target_country,daily_send_limit,sending_window,template,status,start_date,created_at,updated_at) VALUES (?,?,?,?,?,?,?,?,?,?)', (name, values.get('target_niche',''), values.get('target_country',''), max(1, int(values.get('daily_send_limit', 20))), values.get('sending_window','09:00-17:00'), values.get('template','founder'), 'DRAFT', values.get('start_date') or timestamp[:10], timestamp, timestamp))
    connection.commit(); return cursor.lastrowid


def campaigns(connection): return [dict(row) for row in connection.execute('SELECT * FROM campaigns ORDER BY created_at DESC').fetchall()]


def get_campaign(connection, campaign_id: int):
    row = connection.execute('SELECT * FROM campaigns WHERE id=?', (campaign_id,)).fetchone()
    return dict(row) if row else None


def set_campaign_status(connection, campaign_id: int, status: str):
    if status not in CAMPAIGN_STATUSES: raise ValueError('invalid campaign status')
    connection.execute('UPDATE campaigns SET status=?,updated_at=? WHERE id=?', (status, now(), campaign_id)); connection.commit()


def _valid_email(email: str) -> bool: return bool(re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', email or ''))


def _already_sent(connection, lead_id: int, campaign_id: int, followup_number: int = 0) -> bool:
    return connection.execute('SELECT 1 FROM send_logs WHERE lead_id=? AND campaign_id=? AND followup_number=? AND status IN ("QUEUED","SENT","REPLIED")', (lead_id, campaign_id, followup_number)).fetchone() is not None


def qualified_queue(connection, campaign_id: int) -> list[dict]:
    campaign = get_campaign(connection, campaign_id)
    if not campaign: raise ValueError('campaign not found')
    result = []
    for lead in list_leads(connection):
        if campaign['target_niche'] and campaign['target_niche'].lower() not in (lead.get('niche') or '').lower(): continue
        if campaign['target_country'] and campaign['target_country'].lower() not in (lead.get('country') or '').lower(): continue
        if lead.get('do_not_contact') or lead.get('status') in ('DO_NOT_CONTACT','BAD_LEAD','NOT_INTERESTED','NO_RESPONSE','PAID') or lead.get('email_status') in ('SENT','SUPPRESSED'): continue
        if lead.get('status') not in ('QUALIFIED','READY_TO_CONTACT','NEW'): continue
        if lead.get('discovery_run_id') and lead.get('personalization_status') != 'READY': continue
        if not _valid_email(lead.get('business_email')) or not lead.get('company_name') or not (lead.get('review_signal') or lead.get('social_proof_signal')): continue
        if _already_sent(connection, lead['id'], campaign_id): continue
        result.append(lead)
    return sorted(result, key=lambda row: (-row['lead_score'], row['created_at']))


def today_sent(connection, campaign_id: int) -> int:
    today = datetime.now().date().isoformat()
    return connection.execute('SELECT COUNT(*) FROM send_logs WHERE campaign_id=? AND status="SENT" AND substr(sent_at,1,10)=?', (campaign_id, today)).fetchone()[0]


def dry_run(connection, campaign_id: int, founder: str, limit: int = 20) -> list[dict]:
    campaign = get_campaign(connection, campaign_id)
    if not campaign: raise ValueError('campaign not found')
    rows = []
    for lead in qualified_queue(connection, campaign_id)[:min(limit, campaign['daily_send_limit'])]:
        subject, body = render_email(lead, founder, campaign['template'])
        rows.append({'lead_id': lead['id'], 'company_name': lead['company_name'], 'recipient': lead['business_email'], 'subject': subject, 'body': body, 'why_qualified': f"Grade {lead['lead_grade']} / score {lead['lead_score']}; factual observation recorded."})
    connection.execute('INSERT INTO dry_run_reviews (campaign_id, reviewed_at) VALUES (?,?) ON CONFLICT(campaign_id) DO UPDATE SET reviewed_at=excluded.reviewed_at', (campaign_id, now()))
    connection.commit()
    return rows


def dry_run_completed(connection, campaign_id: int) -> bool:
    return connection.execute('SELECT 1 FROM dry_run_reviews WHERE campaign_id=?', (campaign_id,)).fetchone() is not None


def queue_email(connection, campaign_id: int, lead_id: int, founder: str, followup_number: int = 0) -> dict:
    campaign = get_campaign(connection, campaign_id); lead = get_lead(connection, lead_id)
    if not campaign or not lead: raise ValueError('campaign or lead not found')
    if campaign['status'] != 'ENABLED': raise ValueError('campaign is not enabled')
    if not dry_run_completed(connection, campaign_id): raise ValueError('dry run review is required')
    if today_sent(connection, campaign_id) >= campaign['daily_send_limit']: raise ValueError('daily campaign limit reached')
    if lead.get('do_not_contact') or lead.get('email_status') == 'SUPPRESSED' or (followup_number == 0 and lead.get('email_status') == 'SENT') or not _valid_email(lead.get('business_email')): raise ValueError('lead failed send safety checks')
    if lead.get('discovery_run_id') and lead.get('personalization_status') != 'READY': raise ValueError('discovery personalization is missing')
    if not lead.get('company_name') or not (lead.get('review_signal') or lead.get('social_proof_signal')): raise ValueError('factual personalization is missing')
    if _already_sent(connection, lead_id, campaign_id, followup_number): raise ValueError('duplicate send blocked')
    subject, body = render_email(lead, founder, campaign['template'], followup_number)
    timestamp = now()
    cursor = connection.execute('INSERT INTO send_logs (lead_id,campaign_id,sender,recipient,subject,body,sent_at,message_id,status,followup_number) VALUES (?,?,?,?,?,?,?,?,?,?)', (lead_id,campaign_id,'hello@letrusto.com',lead['business_email'],subject,body,timestamp,'','QUEUED',followup_number))
    connection.commit(); return {'id': cursor.lastrowid, 'lead_id': lead_id, 'recipient': lead['business_email'], 'subject': subject, 'body': body}


def mark_send_result(connection, log_id: int, status: str, message_id: str = ''):
    if status not in SEND_STATUSES: raise ValueError('invalid send status')
    log = connection.execute('SELECT * FROM send_logs WHERE id=?', (log_id,)).fetchone()
    if not log: raise ValueError('send log not found')
    connection.execute('UPDATE send_logs SET status=?,message_id=?,sent_at=? WHERE id=?', (status, message_id, now(), log_id))
    if status == 'SENT':
        if log['followup_number'] == 0:
            next_date = datetime.now() + timedelta(days=4)
            lead_status = 'CONTACTED'
        elif log['followup_number'] == 1:
            next_date = datetime.now() + timedelta(days=6)
            lead_status = 'FOLLOW_UP_1'
        else:
            next_date = None
            lead_status = 'NO_RESPONSE'
        connection.execute('UPDATE leads SET status=?,email_status="SENT",last_contacted_at=?,next_followup_at=?,updated_at=? WHERE id=?', (lead_status, now(), next_date.isoformat(timespec='seconds') if next_date else None, now(), log['lead_id']))
    elif status in ('UNSUBSCRIBED','DO_NOT_CONTACT'):
        connection.execute('UPDATE leads SET status="DO_NOT_CONTACT",do_not_contact=1,email_status="SUPPRESSED",updated_at=? WHERE id=?', (now(), log['lead_id']))
    connection.commit()


def due_followups(connection, campaign_id: int) -> list[dict]:
    return [dict(row) for row in connection.execute('SELECT * FROM leads WHERE next_followup_at IS NOT NULL AND next_followup_at <= ? AND status IN ("CONTACTED","FOLLOW_UP_1") AND do_not_contact=0 AND reply_status="NONE" AND trial_status="NONE" AND paid_status="NONE"', (now(),)).fetchall()]


def classify_reply(connection, lead_id: int, classification: str):
    allowed = {'INTERESTED','NOT_INTERESTED','QUESTION','UNSUBSCRIBE','OUT_OF_OFFICE','BOUNCE','UNKNOWN'}
    if classification not in allowed: raise ValueError('invalid reply classification')
    status = 'DO_NOT_CONTACT' if classification == 'UNSUBSCRIBE' else 'INTERESTED' if classification == 'INTERESTED' else 'REPLIED'
    changes = {'reply_status': classification, 'reply_date': now(), 'status': status}
    if status == 'DO_NOT_CONTACT': changes['do_not_contact'] = 1; changes['email_status'] = 'SUPPRESSED'
    assignments = ','.join(f'{key}=?' for key in changes)
    connection.execute(f'UPDATE leads SET {assignments},updated_at=? WHERE id=?', list(changes.values()) + [now(), lead_id]); connection.execute('UPDATE send_logs SET status=? WHERE lead_id=? AND status IN ("QUEUED","SENT")', ('UNSUBSCRIBED' if status == 'DO_NOT_CONTACT' else 'REPLIED', lead_id)); connection.commit()
