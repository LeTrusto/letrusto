"""Opt-in local worker. Start only after Gmail OAuth and campaign review."""
import os
import time
from .config import get_settings
from .services.db import connect
from .services.campaign_service import campaigns, due_followups, mark_send_result, queue_email, qualified_queue
from .services.gmail_service import GmailOAuth


def run_once():
    if os.getenv('LEADGEN_GLOBAL_PAUSED', '0') == '1': return {'status': 'PAUSED_GLOBAL'}
    settings = get_settings(); gmail = GmailOAuth(); auth = gmail.status()
    if not auth['authorized']: return {'status': 'OAUTH_REQUIRED'}
    db = connect(settings.database_path); sent = 0; skipped = 0
    for campaign in campaigns(db):
        if campaign['status'] != 'ENABLED': continue
        queue = qualified_queue(db, campaign['id'])
        if not queue: continue
        try:
            log = queue_email(db, campaign['id'], queue[0]['id'], settings.founder_name)
            try:
                message_id = gmail.send(log['recipient'], log['subject'], log['body'])
                mark_send_result(db, log['id'], 'SENT', message_id); sent += 1
            except Exception:
                mark_send_result(db, log['id'], 'FAILED'); skipped += 1
        except ValueError: skipped += 1
        for lead in due_followups(db, campaign['id']):
            followup_number = 1 if lead['status'] == 'CONTACTED' else 2
            try:
                log = queue_email(db, campaign['id'], lead['id'], settings.founder_name, followup_number)
                message_id = gmail.send(log['recipient'], log['subject'], log['body'])
                mark_send_result(db, log['id'], 'SENT', message_id); sent += 1
            except Exception:
                if 'log' in locals(): mark_send_result(db, log['id'], 'FAILED')
                skipped += 1
    db.close(); return {'status': 'OK', 'sent': sent, 'skipped': skipped}


if __name__ == '__main__':
    interval = max(60, int(os.getenv('LEADGEN_WORKER_INTERVAL_SECONDS', '900')))
    while True:
        print(run_once(), flush=True)
        time.sleep(interval)
