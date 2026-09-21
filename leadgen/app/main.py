from datetime import datetime
from pathlib import Path
from urllib.parse import parse_qs
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, PlainTextResponse, Response
from .config import get_settings
from .services.db import connect
from .services.lead_service import create_lead, dashboard, get_lead, list_leads, mark_sent, update_lead
from .services.export_service import parse_csv, rows_to_csv, rows_to_xlsx
from .services.template_service import gmail_compose_url, render_email
from .services.campaign_service import campaigns, create_campaign, dry_run, dry_run_completed, get_campaign, mark_send_result, qualified_queue, set_campaign_status
from .services.discovery_service import SearchProviderConfigurationError, SearchProviderError, configured_search_provider, discover_urls, generate_search_queries, run_discovery, search_provider_status
from .services.gmail_service import GmailOAuth, GmailOAuthError, EXPECTED_ACCOUNT, OAUTH_CALLBACK_PATH, callback_uri_for_request
from .services.dns_service import check_domain

settings = get_settings()
app = FastAPI(title="LeTrusto Leadgen", docs_url="/api/docs")

CSS = """
:root{font-family:ui-sans-serif,system-ui,sans-serif;color:#17231f;background:#f3f5ef;--ink:#17231f;--muted:#66736c;--line:#d7ded6;--accent:#d85c38;--mint:#dbece0}*{box-sizing:border-box}body{margin:0}a{color:inherit}.shell{max-width:1240px;margin:auto;padding:28px 24px 64px}.top{display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid var(--line);padding-bottom:20px}.brand{font-family:Georgia,serif;font-size:26px;font-weight:700}.tag{color:var(--muted);font-size:13px}.nav a{margin-left:18px;text-decoration:none;font-size:14px}.hero{padding:36px 0 24px;display:flex;justify-content:space-between;gap:30px;align-items:end}.hero h1{font:52px Georgia,serif;line-height:.95;margin:0 0 12px;max-width:650px}.hero p{color:var(--muted);max-width:560px}.button,button{border:0;background:var(--ink);color:white;padding:11px 15px;border-radius:5px;cursor:pointer;text-decoration:none;font:inherit}.button.alt,button.alt{background:var(--accent)}.button.ghost,button.ghost{background:white;color:var(--ink);border:1px solid var(--line)}.metrics{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin:16px 0 30px}.metric,.panel,.card{background:white;border:1px solid var(--line);border-radius:7px;padding:16px}.metric b{display:block;font-size:25px}.metric span,.muted{font-size:12px;color:var(--muted)}.layout{display:grid;grid-template-columns:1fr 1.3fr;gap:18px}.panel h2{font:24px Georgia,serif;margin:0 0 16px}.queue{display:grid;gap:9px}.lead-row{display:flex;justify-content:space-between;gap:12px;padding:12px;border:1px solid var(--line);border-radius:5px}.lead-row strong{display:block}.score{color:var(--accent);font-weight:700}.badge{font-size:11px;padding:4px 7px;border-radius:20px;background:var(--mint);white-space:nowrap}.formgrid{display:grid;grid-template-columns:1fr 1fr;gap:10px}label{font-size:12px;color:var(--muted);display:grid;gap:5px}input,textarea,select{width:100%;font:inherit;border:1px solid var(--line);border-radius:4px;padding:9px;background:#fff}textarea{min-height:90px;resize:vertical}.full{grid-column:1/-1}.actions{display:flex;gap:8px;flex-wrap:wrap;margin-top:13px}.detail{display:grid;gap:12px}.email{background:#f8faf6;border:1px dashed #b8c9bb;padding:14px;white-space:pre-wrap;font-size:14px;line-height:1.5}.notice{padding:12px;background:#fff4df;border-left:4px solid #d89435;margin-bottom:14px}.pipeline{display:grid;grid-template-columns:repeat(5,1fr);gap:10px}.column{background:#e8ede7;padding:10px;border-radius:6px;min-height:150px}.column h3{font-size:12px;margin:0 0 10px}.mini{background:white;padding:9px;border-radius:5px;margin-bottom:7px;font-size:13px}.footer{margin-top:35px;color:var(--muted);font-size:12px}@media(max-width:850px){.metrics{grid-template-columns:repeat(3,1fr)}.layout,.pipeline{grid-template-columns:1fr}.hero{display:block}.hero h1{font-size:42px;margin-bottom:18px}}@media(max-width:520px){.shell{padding:18px 14px}.metrics{grid-template-columns:repeat(2,1fr)}.formgrid{grid-template-columns:1fr}.full{grid-column:auto}}
"""


def page(title: str, body: str) -> str:
    return f"<!doctype html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>{title} | LeTrusto Leadgen</title><style>{CSS}</style></head><body><div class='shell'><header class='top'><a class='brand' href='/'>LeTrusto / Leadgen</a><span class='tag'>LOCAL ONLY · OAUTH-GATED</span><nav class='nav'><a href='/'>Dashboard</a><a href='/discover'>Discover</a><a href='/campaigns'>Campaigns</a><a href='/leads/new'>Add lead</a><a href='/export.csv'>Export CSV</a><a href='/export.xlsx'>Export Excel</a></nav></header>{body}<footer class='footer'>Business outreach workspace. No LinkedIn scraping. No automatic email sending without explicit OAuth and campaign enablement. Keep this database local.</footer></div></body></html>"


def esc(value) -> str:
    import html
    return html.escape(str(value or ""))


def lead_card(lead: dict) -> str:
    return f"<div class='lead-row'><div><strong>{esc(lead['company_name'])}</strong><span class='muted'>{esc(lead.get('contact_name') or 'No contact')} · {esc(lead.get('niche') or 'Niche not set')}</span></div><div><span class='score'>{lead['lead_score']}</span> <span class='badge'>{esc(lead['status'])}</span><br><a class='muted' href='/leads/{lead['id']}'>Open</a></div></div>"


def pipeline_column(status: str, leads: list[dict]) -> str:
    cards = []
    for lead in leads:
        if lead['status'] == status:
            cards.append(f"<div class='mini'><b>{esc(lead['company_name'])}</b><br><span class='muted'>{lead['lead_score']} · <a href='/leads/{lead['id']}'>open</a></span></div>")
    return f"<section class='column'><h3>{status}</h3>{''.join(cards) or '<span class=\"muted\">Empty</span>'}</section>"


@app.get('/', response_class=HTMLResponse)
def home():
    db = connect(settings.database_path); metrics = dashboard(db); leads = list_leads(db); db.close(); gmail = GmailOAuth().status()
    ready = [lead for lead in leads if lead['status'] in ('READY_TO_CONTACT', 'QUALIFIED') and not lead['do_not_contact']][:8]
    due = [lead for lead in leads if lead['status'] in ('CONTACTED', 'FOLLOW_UP_1', 'FOLLOW_UP_2') and lead['next_followup_at']][:8]
    stats = ''.join(f"<div class='metric'><b>{metrics[key]}</b><span>{label}</span></div>" for key, label in [('total','Total leads'),('QUALIFIED','Qualified'),('READY_TO_CONTACT','Ready'),('CONTACTED','Contacted'),('REPLIED','Replies'),('PAID','Paid')])
    queue = ''.join(lead_card(l) for l in ready) or "<p class='muted'>No ready leads yet. Add or import your first prospects.</p>"
    followups = ''.join(lead_card(l) for l in due) or "<p class='muted'>No follow-ups due.</p>"
    pipeline = ''.join(pipeline_column(status, leads) for status in ['NEW','QUALIFIED','READY_TO_CONTACT','CONTACTED','REPLIED'])
    gmail_status = 'Authorized' if gmail['authorized'] else 'Not connected'
    gmail_account = esc(gmail.get('account') or EXPECTED_ACCOUNT)
    gmail_box = f"<section class='panel' style='margin-top:18px'><h2>Gmail Outreach</h2><p><b>Sender:</b> {EXPECTED_ACCOUNT}<br><b>Account:</b> {gmail_account}<br><b>Scope:</b> gmail.send<br><b>Status:</b> {gmail_status}</p><p class='muted'>{esc(gmail['message'])}</p><a class='button alt' href='/gmail/auth'>{'Reauthorize Gmail' if gmail['authorized'] else 'Connect Gmail'}</a></section>"
    body = f"<section class='hero'><div><h1>Find the next good customer.</h1><p>Research small ecommerce businesses, capture factual observations, and work through a focused one-at-a-time outreach queue.</p></div><a class='button alt' href='/leads/next'>Next lead →</a></section><section class='metrics'>{stats}</section><div class='layout'><section class='panel'><h2>Today's outreach</h2><p class='muted'>{metrics['sent_today']} sent today · {max(0, settings.daily_limit-metrics['sent_today'])} remaining · {len(ready)} ready in queue</p><div class='queue'>{queue}</div></section><section class='panel'><h2>Follow-up desk</h2><p class='muted'>Follow-up 1 after 4 days · Follow-up 2 after 10 days · stop after that</p><div class='queue'>{followups}</div></section></div><section class='panel' style='margin-top:18px'><h2>Pipeline</h2><div class='pipeline'>{pipeline}</div></section>{gmail_box}"
    return page('Dashboard', body)


@app.get('/leads/new', response_class=HTMLResponse)
def new_lead():
    body = "<section class='hero'><div><h1>Add a prospect.</h1><p>Enter only public business information. LinkedIn fields are manual only.</p></div></section><section class='panel'><form method='post' action='/leads'><div class='formgrid'><label>Company*<input name='company_name' required></label><label>Website<input name='website'></label><label>Contact name<input name='contact_name'></label><label>Contact role<input name='contact_role'></label><label>Business email<input type='email' name='business_email'></label><label>Country<input name='country'></label><label>City<input name='city'></label><label>Niche<input name='niche'></label><label>LinkedIn URL (manual)<input name='linkedin_url'></label><label>Source<select name='source'><option>COMPANY_WEBSITE</option><option>GOOGLE</option><option>LINKEDIN_MANUAL</option><option>EXPO</option><option>EVENT_DIRECTORY</option><option>REFERRAL</option><option>OTHER</option></select></label><label class='full'>Source URL<input name='source_url'></label><label class='full'>Review signal<textarea name='review_signal' placeholder='Only factual observations, or leave blank / Not verified'></textarea></label><label>Review count signal<input name='review_count_signal'></label><label>Social proof signal<input name='social_proof_signal'></label><label class='full'>Why LeTrusto may fit<textarea name='why_fit' placeholder='Use a factual reason; write Not verified if unknown'></textarea></label><label class='full'>Notes<textarea name='notes'></textarea></label></div><div class='actions'><button class='alt'>Create lead</button><a class='button ghost' href='/'>Cancel</a></div></form></section>"
    return page('Add lead', body)


@app.post('/leads')
async def add_lead(request: Request):
    body = await request.body()
    values = {key: items[-1] for key, items in parse_qs(body.decode('utf-8'), keep_blank_values=True).items()}
    db = connect(settings.database_path)
    try: lead_id = create_lead(db, values)
    except ValueError as exc: db.close(); return HTMLResponse(page('Duplicate', f"<section class='panel'><div class='notice'>{esc(exc)}</div><a class='button' href='/leads/new'>Back</a></section>"), status_code=409)
    db.close(); return RedirectResponse(f'/leads/{lead_id}', status_code=303)


@app.get('/leads/next', response_class=HTMLResponse)
def next_lead():
    db = connect(settings.database_path); leads = list_leads(db); db.close()
    lead = next((l for l in leads if l['status'] in ('READY_TO_CONTACT','QUALIFIED') and not l['do_not_contact']), None)
    return RedirectResponse(f"/leads/{lead['id']}" if lead else '/', status_code=303)


@app.get('/leads/{lead_id}', response_class=HTMLResponse)
def detail(lead_id: int, template: str = 'founder', followup: int = 0):
    db = connect(settings.database_path); lead = get_lead(db, lead_id); db.close()
    if not lead: raise HTTPException(404, 'Lead not found')
    subject, email = render_email(lead, settings.founder_name, template, followup)
    compose = gmail_compose_url(lead['business_email'], subject, email)
    suppressed = lead['do_not_contact'] or lead['status'] == 'DO_NOT_CONTACT'
    warning = "<div class='notice'>Suppressed: this lead will never appear in the outreach queue until you explicitly remove suppression.</div>" if suppressed else ""
    action = "" if suppressed else f"<a class='button alt' target='_blank' rel='noopener' href='{esc(compose)}'>Open in Gmail</a><form method='post' action='/leads/{lead_id}/sent' style='display:inline'><button>Mark sent</button></form>"
    body = f"<section class='hero'><div><h1>{esc(lead['company_name'])}</h1><p>{esc(lead.get('contact_name') or 'Contact not identified')} · {esc(lead.get('niche') or 'Niche not verified')} · score <b>{lead['lead_score']} / 100 ({lead['lead_grade']})</b></p></div><span class='badge'>{esc(lead['status'])}</span></section>{warning}<div class='layout'><section class='panel detail'><h2>Research</h2><p><b>Website:</b> {esc(lead['website']) or 'Not verified'}<br><b>Email:</b> {esc(lead['business_email']) or 'Not verified'}<br><b>Role:</b> {esc(lead['contact_role']) or 'Not verified'}<br><b>LinkedIn:</b> {esc(lead['linkedin_url']) or 'Not entered'}<br><b>Source:</b> {esc(lead['source'])}</p><label>Customer-proof observations<textarea id='review_signal'>{esc(lead['review_signal'])}</textarea></label><label>Why LeTrusto fits<textarea id='why_fit'>{esc(lead['why_fit'])}</textarea></label><label>Notes<textarea id='notes'>{esc(lead['notes'])}</textarea></label><div class='actions'><button onclick='saveResearch()'>Save research</button><form method='post' action='/leads/{lead_id}/suppress'><button class='ghost'>Do not contact</button></form></div><p class='muted'>Score explanation: website +20 · reviews +15 · social proof +10 · contact +10 · email +10 · role +10 · fit +5 · niche +5 · review activity +5.</p></section><section class='panel'><h2>Review → Gmail → Send → Mark sent</h2><form method='get' action='/leads/{lead_id}'><label>Template<select name='template'><option value='founder'>Founder outreach</option><option value='opportunity'>Store opportunity</option><option value='expo'>Expo/event follow-up</option></select></label><label>Follow-up<select name='followup'><option value='0'>Initial outreach</option><option value='1'>Follow-up 1</option><option value='2'>Follow-up 2</option></select></label><button class='ghost' style='margin-top:10px'>Regenerate</button></form><h3>{esc(subject)}</h3><div class='email'>{esc(email)}</div><div class='actions'>{action}<a class='button ghost' href='/'>Skip</a></div><p class='muted'>Edit the email in Gmail before sending. This tool never sends automatically.</p></section></div><script>async function saveResearch(){{const body={{review_signal:document.getElementById('review_signal').value,why_fit:document.getElementById('why_fit').value,notes:document.getElementById('notes').value}};await fetch('/api/leads/{lead_id}',{{method:'PATCH',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(body)}});location.reload()}}</script>"
    return page('Lead detail', body)


@app.post('/leads/{lead_id}/sent')
def sent(lead_id: int):
    db = connect(settings.database_path); metrics = dashboard(db)
    if metrics['sent_today'] >= settings.daily_limit: db.close(); return HTMLResponse(page('Daily limit', "<section class='panel'><div class='notice'>Daily outreach limit reached. No lead was marked sent.</div><a class='button' href='/'>Back to dashboard</a></section>"), status_code=429)
    mark_sent(db, lead_id); db.close(); return RedirectResponse('/leads/next', status_code=303)


@app.post('/leads/{lead_id}/suppress')
def suppress(lead_id: int):
    db = connect(settings.database_path); update_lead(db, lead_id, {'status':'DO_NOT_CONTACT', 'do_not_contact':1}); db.close(); return RedirectResponse(f'/leads/{lead_id}', status_code=303)


@app.patch('/api/leads/{lead_id}')
async def patch_lead(lead_id: int, request: Request):
    db = connect(settings.database_path); update_lead(db, lead_id, await request.json()); lead = get_lead(db, lead_id); db.close(); return lead


@app.post('/import', response_class=HTMLResponse)
async def import_csv(request: Request):
    form = await request.form()
    file = form.get('file')
    if not hasattr(file, 'read'):
        raise HTTPException(400, 'CSV file is required')
    db = connect(settings.database_path); imported = 0; skipped = 0
    for lead in parse_csv((await file.read()).decode('utf-8-sig')):
        try: create_lead(db, lead); imported += 1
        except ValueError: skipped += 1
    db.close(); return HTMLResponse(page('Import complete', f"<section class='panel'><h2>Import complete</h2><p>{imported} created · {skipped} duplicates or invalid rows skipped.</p><a class='button' href='/'>Dashboard</a></section>"))


@app.get('/import', response_class=HTMLResponse)
def import_page():
    return page('Import', "<section class='hero'><div><h1>Bring in a list.</h1><p>Choose a CSV to preview the first rows locally before importing. Duplicate websites and emails are skipped.</p></div></section><section class='panel'><form method='post' action='/import' enctype='multipart/form-data' onsubmit='return Boolean(document.querySelector(\"input[name=file]\").files.length)'><input id='csv-file' type='file' name='file' accept='.csv' required><div id='preview' class='muted' style='margin-top:14px'>No file selected.</div><div class='actions'><button class='alt'>Import CSV</button><a class='button ghost' href='/'>Cancel</a></div></form><p class='muted'>Recognized columns: Company, Company Name, Website, Email, Business Email, Founder, Owner, Contact, LinkedIn, LinkedIn URL, Country, Niche.</p></section><script>document.getElementById('csv-file').addEventListener('change', async (event) => { const file = event.target.files[0]; if (!file) return; const text = await file.slice(0, 12000).text(); const lines = text.split(/\\r?\\n/).filter(Boolean).slice(0, 6); document.getElementById('preview').innerHTML = '<b>Preview</b><pre style=\"overflow:auto;white-space:pre-wrap\">' + lines.map(line => line.replaceAll('&','&amp;').replaceAll('<','&lt;')).join('\\n') + '</pre>'; });</script>")


@app.get('/export.csv')
def export_csv():
    db = connect(settings.database_path); content = rows_to_csv(list_leads(db)); db.close(); return Response(content, media_type='text/csv', headers={'Content-Disposition':'attachment; filename=letrusto-leads.csv'})


@app.get('/export.xlsx')
def export_xlsx():
    db = connect(settings.database_path); content = rows_to_xlsx(list_leads(db)); db.close(); return Response(content, media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', headers={'Content-Disposition':'attachment; filename=letrusto-leads.xlsx'})


@app.get('/campaigns', response_class=HTMLResponse)
def campaigns_page():
    db = connect(settings.database_path); rows = campaigns(db); db.close()
    cards = ''.join(f"<div class='lead-row'><div><strong>{esc(row['name'])}</strong><span class='muted'>{esc(row['target_country'])} · {esc(row['target_niche'])} · {row['daily_send_limit']}/day</span></div><div><span class='badge'>{row['status']}</span><br><a class='muted' href='/campaigns/{row['id']}'>Open</a></div></div>" for row in rows) or '<p class="muted">No campaigns yet.</p>'
    body = f"<section class='hero'><div><h1>Campaign control.</h1><p>Dry-run first. Real sending requires Gmail OAuth, explicit enablement, and every safety gate.</p></div><a class='button alt' href='/campaigns/new'>Create campaign</a></section><section class='panel'><div class='queue'>{cards}</div><p class='muted'>Sender: hello@letrusto.com · Global pause is available through <code>LEADGEN_GLOBAL_PAUSED=1</code>.</p></section>"
    return page('Campaigns', body)


@app.get('/campaigns/new', response_class=HTMLResponse)
def new_campaign():
    body = "<section class='hero'><div><h1>Set a careful campaign.</h1><p>Start with 20/day or less. The campaign begins as DRAFT.</p></div></section><section class='panel'><form method='post' action='/campaigns'><div class='formgrid'><label>Campaign name*<input name='name' required></label><label>Target country<input name='target_country'></label><label>Target niche<input name='target_niche'></label><label>Daily limit<input type='number' name='daily_send_limit' value='20' min='1' max='100'></label><label>Sending window<input name='sending_window' value='09:00-17:00'></label><label>Start date<input type='date' name='start_date'></label><label>Template<select name='template'><option value='founder'>Founder outreach</option><option value='opportunity'>Store opportunity</option><option value='expo'>Expo/event</option></select></label></div><div class='actions'><button class='alt'>Create draft</button><a class='button ghost' href='/campaigns'>Cancel</a></div></form></section>"
    return page('New campaign', body)


@app.post('/campaigns')
async def add_campaign(request: Request):
    body = await request.body(); values = {key: items[-1] for key, items in parse_qs(body.decode('utf-8'), keep_blank_values=True).items()}
    db = connect(settings.database_path)
    try: campaign_id = create_campaign(db, values)
    except ValueError as exc: db.close(); return HTMLResponse(page('Campaign error', f"<section class='panel'><div class='notice'>{esc(exc)}</div></section>"), status_code=400)
    db.close(); return RedirectResponse(f'/campaigns/{campaign_id}', status_code=303)


@app.get('/campaigns/{campaign_id}', response_class=HTMLResponse)
def campaign_detail(campaign_id: int):
    db = connect(settings.database_path); campaign = get_campaign(db, campaign_id)
    if not campaign: db.close(); raise HTTPException(404, 'Campaign not found')
    queue = qualified_queue(db, campaign_id); auth = GmailOAuth().status(); db.close()
    rows = ''.join(f"<div class='lead-row'><div><strong>{esc(row['company_name'])}</strong><span class='muted'>{esc(row['business_email'])} · score {row['lead_score']}</span></div><span class='badge'>READY</span></div>" for row in queue[:20]) or '<p class="muted">No qualified leads match this campaign.</p>'
    auth_note = '<div class="notice">Gmail OAuth is not ready. Dry-run is available; real sending is blocked until browser authorization is completed.</div>' if not auth['authorized'] else '<div class="notice">OAuth token found. Verify the authorized account is hello@letrusto.com before enabling.</div>'
    body = f"<section class='hero'><div><h1>{esc(campaign['name'])}</h1><p>{esc(campaign['target_country'])} · {esc(campaign['target_niche'])} · {campaign['daily_send_limit']}/day</p></div><span class='badge'>{campaign['status']}</span></section>{auth_note}<section class='panel'><div class='actions'><a class='button' href='/campaigns/{campaign_id}/dry-run'>Dry run</a><form method='post' action='/campaigns/{campaign_id}/status'><input type='hidden' name='status' value='ENABLED'><button class='alt'>Enable campaign</button></form><form method='post' action='/campaigns/{campaign_id}/status'><input type='hidden' name='status' value='PAUSED'><button class='ghost'>Pause campaign</button></form></div><p class='muted'>Enablement is explicit. The worker still refuses sends without OAuth, personalization, qualification, suppression checks, and daily-limit capacity.</p></section><section class='panel'><h2>Qualified queue ({len(queue)})</h2><div class='queue'>{rows}</div></section>"
    return page('Campaign', body)


@app.post('/campaigns/{campaign_id}/status')
async def campaign_status(campaign_id: int, request: Request):
    form = parse_qs((await request.body()).decode('utf-8')); status = form.get('status', ['PAUSED'])[-1]
    db = connect(settings.database_path)
    if status == 'ENABLED':
        gmail = GmailOAuth().status()
        if not gmail['authorized'] or gmail.get('account') != EXPECTED_ACCOUNT:
            db.close(); return HTMLResponse(page('Campaign blocked', '<section class="panel"><div class="notice">Campaign remains disabled. Connect Gmail and verify hello@letrusto.com first.</div><a class="button" href="/gmail/auth">Connect Gmail</a></section>'), status_code=403)
        if not dry_run_completed(db, campaign_id):
            db.close(); return HTMLResponse(page('Campaign blocked', '<section class="panel"><div class="notice">Campaign remains disabled. Complete and review the dry run first.</div><a class="button" href="/campaigns">Back to campaigns</a></section>'), status_code=403)
    set_campaign_status(db, campaign_id, status); db.close(); return RedirectResponse(f'/campaigns/{campaign_id}', status_code=303)


@app.get('/campaigns/{campaign_id}/dry-run', response_class=HTMLResponse)
def campaign_dry_run(campaign_id: int):
    db = connect(settings.database_path); rows = dry_run(db, campaign_id, settings.founder_name); db.close()
    cards = ''.join(f"<article class='card'><b>{esc(row['company_name'])}</b><p class='muted'>{esc(row['recipient'])} · {esc(row['subject'])}</p><div class='email'>{esc(row['body'])}</div><p class='muted'>{esc(row['why_qualified'])}</p></article>" for row in rows) or '<p class="muted">No safe recipients in the queue.</p>'
    return page('Dry run', f"<section class='hero'><div><h1>Dry run.</h1><p>No email was sent. Review the exact recipients, subjects, bodies, and qualification reasons.</p></div><a class='button ghost' href='/campaigns/{campaign_id}'>Back</a></section><section class='queue'>{cards}</section>")


@app.get('/discover', response_class=HTMLResponse)
def discover_page():
    body = f"<section class='hero'><div><h1>Automated lead discovery.</h1><p>Automatically discover B2B and SaaS businesses, research their public websites, find public business contact emails, qualify prospects, and prepare personalized outreach.</p></div></section><section class='panel'><form method='post' action='/discover'><div class='formgrid'><label>Country or region<input name='country' value='India'></label><label>Industry or niche<input name='niche' placeholder='B2B SaaS' required></label><label>Leads wanted<input type='number' name='requested_count' value='25' min='1' max='500'></label><label>Minimum score<input type='number' name='minimum_score' value='60' min='0' max='100'></label></div><div class='actions'><button class='alt'>Start discovery</button></div></form><p class='muted'>{esc(search_provider_status())}</p><p class='muted'>No LinkedIn automation, search-results scraping, or automatic email sending.</p></section>"
    return page('Lead discovery', body)


@app.post('/discover', response_class=HTMLResponse)
async def discover(request: Request):
    form = parse_qs((await request.body()).decode('utf-8'), keep_blank_values=True)
    country, niche = form.get('country', [''])[0], form.get('niche', [''])[0]
    db = connect(settings.database_path)
    try:
        result = run_discovery(db, country, niche, int(form.get('requested_count', ['25'])[0]), int(form.get('minimum_score', ['60'])[0]))
    except (SearchProviderConfigurationError, SearchProviderError, ValueError, RuntimeError) as exc:
        db.close()
        status_code = 400 if isinstance(exc, SearchProviderConfigurationError) else 502 if isinstance(exc, SearchProviderError) else 400
        return HTMLResponse(page('Discovery failed', f"<section class='panel'><h2>Discovery did not complete</h2><div class='notice'>{esc(exc)}</div><p class='muted'>No leads were created from this run. The provider error was recorded and the API key is never displayed here.</p></section>"), status_code=status_code)
    db.close()
    rows = ''.join(f"<div class='lead-row'><div><strong>{esc(row['company_name'])}</strong><span class='muted'>{esc(row['website'])} · {esc(row['business_email']) or 'no business email'}</span></div><div><span class='score'>{row['score']}</span> <span class='badge'>{'QUALIFIED' if row['qualified'] else 'REJECTED'}</span></div></div>" for row in result['leads']) or '<p class="muted">No candidate websites produced a lead.</p>'
    stats = f"<div class='metrics'><div class='metric'><b>{result['searches_performed']}</b><span>Searches</span></div><div class='metric'><b>{result['discovered']}</b><span>Discovered</span></div><div class='metric'><b>{result['unique_domains']}</b><span>Unique domains</span></div><div class='metric'><b>{result['websites_checked']}</b><span>Websites checked</span></div><div class='metric'><b>{result['qualified']}</b><span>Qualified</span></div><div class='metric'><b>{result['duplicates']}</b><span>Duplicates</span></div></div>"
    return HTMLResponse(page('Discovery complete', f"<section class='hero'><div><h1>Discovery complete.</h1><p>Research finished without sending email. Review qualified leads, then create a campaign and run its dry run.</p></div><a class='button alt' href='/campaigns'>Campaigns</a></section>{stats}<section class='panel'><h2>Results</h2><div class='queue'>{rows}</div><p class='muted'>{result['rejected']} rejected · {len(result['errors'])} errors · run {result['run_id']}</p><a class='button ghost' href='/discover'>New discovery run</a></section>"))


@app.get('/discover/provider-check', response_class=HTMLResponse)
def discover_provider_check(country: str = 'India', niche: str = 'B2B SaaS'):
    try:
        provider = configured_search_provider()
        if provider is None:
            raise SearchProviderConfigurationError('SerpApi is not configured.')
        query = generate_search_queries(country, niche)[0]
        candidates = provider.search_businesses(query, country, 5, page=1)
        domains = [candidate.website for candidate in candidates[:5]]
        body = f"<section class='panel'><h2>Search provider check</h2><p>Provider: SerpApi<br>Request: successful<br>HTTP status: {provider.last_http_status}<br>Results returned: {len(candidates)}<br>Candidate domains: {esc(', '.join(domains) or 'None')}</p><p class='muted'>This check made one search request only. It did not crawl sites, create leads, send email, or create campaigns.</p></section>"
        return HTMLResponse(page('Search provider check', body))
    except SearchProviderConfigurationError as exc:
        return HTMLResponse(page('Search provider check', f"<section class='panel'><h2>Search provider check</h2><div class='notice'>{esc(exc)}</div></section>"), status_code=400)
    except SearchProviderError as exc:
        status = exc.status_code if exc.status_code in (401, 403, 429) else 502
        return HTMLResponse(page('Search provider check', f"<section class='panel'><h2>Search provider check</h2><p>Provider: SerpApi<br>Request: failed<br>HTTP status: {exc.status_code or 'unavailable'}</p><div class='notice'>{esc(exc)}</div></section>"), status_code=status)


@app.get('/api/gmail/status')
def gmail_status(): return GmailOAuth().status()


@app.get('/gmail/status')
def gmail_status_public(): return GmailOAuth().status()


@app.get('/gmail/auth', response_class=HTMLResponse)
def gmail_auth(request: Request):
    try:
        redirect_uri = callback_uri_for_request(request)
        authorization_url = GmailOAuth(redirect_uri=redirect_uri).start_authorization()
        body = f"<section class='hero'><div><h1>Connect Gmail.</h1><p>Sign in with {EXPECTED_ACCOUNT} and approve only Gmail send plus OpenID email identity permissions. No campaign will be enabled.</p></div></section><section class='panel'><p>Google authorization is ready.</p><a class='button alt' target='_blank' rel='noopener' href='{esc(authorization_url)}'>Open Google authorization</a><p class='muted'>After approval, Google returns to the local callback at {esc(redirect_uri)}.</p></section>"
        return page('Connect Gmail', body)
    except GmailOAuthError as exc:
        return HTMLResponse(page('Gmail setup', f"<section class='panel'><h2>Gmail setup required</h2><div class='notice'>{esc(exc)}</div><p class='muted'>Set GMAIL_CREDENTIALS_FILE and GMAIL_TOKEN_FILE, then reload this page.</p></section>"), status_code=400)


@app.get('/gmail/oauth2callback', response_class=HTMLResponse)
def gmail_oauth_callback(code: str | None = None, state: str | None = None, error: str | None = None):
    if error:
        return HTMLResponse(page('Gmail authorization', f"<section class='panel'><h2>Authorization was not completed</h2><div class='notice'>{esc(error)}</div><a class='button' href='/gmail/auth'>Try again</a></section>"), status_code=400)
    try:
        account = GmailOAuth().finish_authorization(code or '', state)
        return page('Gmail authorized', f"<section class='panel'><h2>Gmail authorized</h2><p>Connected account: <b>{esc(account)}</b></p><p class='muted'>No campaign was enabled and no email was sent.</p><a class='button' href='/'>Return to Leadgen</a></section>")
    except GmailOAuthError as exc:
        return HTMLResponse(page('Gmail authorization', f"<section class='panel'><h2>Authorization failed</h2><div class='notice'>{esc(exc)}</div><a class='button' href='/gmail/auth'>Try again</a></section>"), status_code=400)


@app.get('/api/dns/status')
def dns_status(): return check_domain('letrusto.com')


@app.post('/api/leads/{lead_id}/reply')
async def classify_lead_reply(lead_id: int, request: Request):
    from .services.campaign_service import classify_reply
    payload = await request.json(); db = connect(settings.database_path)
    try: classify_reply(db, lead_id, payload.get('classification', 'UNKNOWN'))
    except ValueError as exc: db.close(); raise HTTPException(400, str(exc))
    lead = get_lead(db, lead_id); db.close(); return lead


@app.get('/healthz')
def healthz(): return {'status':'ok', 'database': str(settings.database_path)}


if __name__ == '__main__':
    import uvicorn
    uvicorn.run('app.main:app', host='127.0.0.1', port=int(__import__('os').getenv('LEADGEN_PORT', '8765')), reload=False)
