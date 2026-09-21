import sqlite3
from pathlib import Path

SCHEMA = '''
CREATE TABLE IF NOT EXISTS leads (
 id INTEGER PRIMARY KEY AUTOINCREMENT, company_name TEXT NOT NULL, website TEXT DEFAULT '', contact_name TEXT DEFAULT '', contact_role TEXT DEFAULT '', business_email TEXT DEFAULT '', country TEXT DEFAULT '', city TEXT DEFAULT '', niche TEXT DEFAULT '', linkedin_url TEXT DEFAULT '', source TEXT DEFAULT 'OTHER', source_url TEXT DEFAULT '', review_signal TEXT DEFAULT '', review_count_signal TEXT DEFAULT '', social_proof_signal TEXT DEFAULT '', why_fit TEXT DEFAULT '', lead_score INTEGER DEFAULT 0, lead_grade TEXT DEFAULT 'D', status TEXT DEFAULT 'NEW', email_status TEXT DEFAULT 'NOT_SENT', last_contacted_at TEXT, next_followup_at TEXT, reply_status TEXT DEFAULT 'NONE', reply_date TEXT, trial_status TEXT DEFAULT 'NONE', trial_date TEXT, installation_status TEXT DEFAULT 'NONE', installation_date TEXT, paid_status TEXT DEFAULT 'NONE', paid_date TEXT, notes TEXT DEFAULT '', do_not_contact INTEGER DEFAULT 0, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_leads_status ON leads(status);
CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(business_email);
CREATE INDEX IF NOT EXISTS idx_leads_website ON leads(website);
CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS campaigns (
 id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, target_niche TEXT DEFAULT '', target_country TEXT DEFAULT '', daily_send_limit INTEGER NOT NULL DEFAULT 20, sending_window TEXT DEFAULT '09:00-17:00', template TEXT DEFAULT 'founder', status TEXT DEFAULT 'DRAFT', start_date TEXT, created_at TEXT NOT NULL, updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS send_logs (
 id INTEGER PRIMARY KEY AUTOINCREMENT, lead_id INTEGER NOT NULL, campaign_id INTEGER NOT NULL, sender TEXT NOT NULL, recipient TEXT NOT NULL, subject TEXT NOT NULL, body TEXT NOT NULL, sent_at TEXT NOT NULL, message_id TEXT DEFAULT '', status TEXT NOT NULL, followup_number INTEGER NOT NULL DEFAULT 0, FOREIGN KEY(lead_id) REFERENCES leads(id), FOREIGN KEY(campaign_id) REFERENCES campaigns(id)
);
CREATE INDEX IF NOT EXISTS idx_send_logs_campaign ON send_logs(campaign_id, status, sent_at);
CREATE TABLE IF NOT EXISTS discovery_runs (
 id INTEGER PRIMARY KEY AUTOINCREMENT, source TEXT NOT NULL, query TEXT DEFAULT '', target_country TEXT DEFAULT '', target_niche TEXT DEFAULT '', requested_count INTEGER DEFAULT 0, created_at TEXT NOT NULL, status TEXT DEFAULT 'RUNNING', finished_at TEXT, searches_performed INTEGER DEFAULT 0, discovered INTEGER DEFAULT 0, unique_domains INTEGER DEFAULT 0, websites_checked INTEGER DEFAULT 0, emails_found INTEGER DEFAULT 0, ecommerce_stores INTEGER DEFAULT 0, qualified INTEGER DEFAULT 0, rejected INTEGER DEFAULT 0, duplicates INTEGER DEFAULT 0
);
CREATE TABLE IF NOT EXISTS discovery_pages (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER NOT NULL, lead_id INTEGER, url TEXT NOT NULL, title TEXT DEFAULT '', text TEXT DEFAULT '', http_status INTEGER DEFAULT 0, discovered_links INTEGER DEFAULT 0, crawled_at TEXT NOT NULL, FOREIGN KEY(run_id) REFERENCES discovery_runs(id), FOREIGN KEY(lead_id) REFERENCES leads(id));
CREATE TABLE IF NOT EXISTS discovery_emails (id INTEGER PRIMARY KEY AUTOINCREMENT, run_id INTEGER NOT NULL, lead_id INTEGER, email TEXT NOT NULL, source_url TEXT NOT NULL, created_at TEXT NOT NULL, FOREIGN KEY(run_id) REFERENCES discovery_runs(id), FOREIGN KEY(lead_id) REFERENCES leads(id));
CREATE TABLE IF NOT EXISTS dry_run_reviews (
 id INTEGER PRIMARY KEY AUTOINCREMENT, campaign_id INTEGER NOT NULL UNIQUE, reviewed_at TEXT NOT NULL, FOREIGN KEY(campaign_id) REFERENCES campaigns(id)
);
'''


def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    existing = {row[1] for row in connection.execute('PRAGMA table_info(leads)').fetchall()}
    for name, definition in {
        'research_status': "TEXT DEFAULT 'NOT_STARTED'", 'personalization_status': "TEXT DEFAULT 'NOT_READY'", 'qualification_reason': "TEXT DEFAULT ''", 'personalization_facts': "TEXT DEFAULT ''", 'suggested_subject': "TEXT DEFAULT ''", 'suggested_body': "TEXT DEFAULT ''", 'ecommerce_detected': 'INTEGER DEFAULT 0', 'products_detected': 'INTEGER DEFAULT 0', 'reviews_detected': 'INTEGER DEFAULT 0', 'crawl_status': "TEXT DEFAULT 'NOT_STARTED'", 'discovery_run_id': 'INTEGER',
    }.items():
        if name not in existing:
            connection.execute(f'ALTER TABLE leads ADD COLUMN {name} {definition}')
    run_columns = {row[1] for row in connection.execute('PRAGMA table_info(discovery_runs)').fetchall()}
    for name, definition in {'status': "TEXT DEFAULT 'RUNNING'", 'finished_at': 'TEXT', 'searches_performed': 'INTEGER DEFAULT 0', 'discovered': 'INTEGER DEFAULT 0', 'unique_domains': 'INTEGER DEFAULT 0', 'websites_checked': 'INTEGER DEFAULT 0', 'emails_found': 'INTEGER DEFAULT 0', 'ecommerce_stores': 'INTEGER DEFAULT 0', 'qualified': 'INTEGER DEFAULT 0', 'rejected': 'INTEGER DEFAULT 0', 'duplicates': 'INTEGER DEFAULT 0'}.items():
        if name not in run_columns:
            connection.execute(f'ALTER TABLE discovery_runs ADD COLUMN {name} {definition}')
    connection.commit()
    return connection
