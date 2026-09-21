# LeTrusto Leadgen

A local-only customer-acquisition workspace for researching qualified ecommerce prospects and preparing one human-reviewed outreach message at a time. It is separate from the LeTrusto production application and uses its own SQLite database.

This tool does not scrape LinkedIn, log in to LinkedIn, send email automatically, use Resend, or deploy publicly. LinkedIn research and contact entry are manual. Gmail opens a prefilled compose window; the user must review and press Send.

Automation is opt-in. Campaigns begin as `DRAFT`, and real sends are blocked until Gmail OAuth is configured, the sender is verified, a dry run is reviewed, and the campaign is explicitly enabled. The worker sends only through the Gmail API with the `gmail.send` scope. It never uses Resend.

## Install and start

From this directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:LEADGEN_FOUNDER_NAME = "Your Name"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8765
```

Open `http://127.0.0.1:8765`. The server binds to `127.0.0.1` only. The default database is `leadgen/data/leadgen.sqlite3`; override it with `LEADGEN_DATABASE_PATH`. The daily limit defaults to 20 and can be changed with `LEADGEN_DAILY_LIMIT`.

## Discovery and campaigns

The primary workflow is **Discover -> search -> crawl -> extract -> qualify -> personalize -> campaign dry run**. Automated discovery uses a legitimate configured search API; it never falls back to fake or sample results. The supported provider is SerpApi, which calls its JSON search endpoint without scraping a search-results page:

```powershell
$env:LEADGEN_SEARCH_PROVIDER = "serpapi"
$env:LEADGEN_SEARCH_API_KEY = "your-key-from-your-local-secret-store"
# Optional: local proxy or test endpoint, delay between API calls, and page count.
# $env:LEADGEN_SEARCH_ENDPOINT = "https://serpapi.com/search.json"
# $env:LEADGEN_SEARCH_DELAY_SECONDS = "1"
# $env:LEADGEN_SEARCH_MAX_PAGES = "2"
```

Then open **Discover**, choose only country, niche, lead count, and minimum score. The niche field targets any B2B vertical, including SaaS (for example `B2B SaaS`, `HR software`, `logistics SaaS`). The app generates several niche/country queries, follows provider pagination with a bounded rate limit, normalizes and deduplicates business domains, filters social, news, jobs, blogs, directories, and marketplaces, and crawls up to six same-domain public HTML pages. It respects `robots.txt`, response limits, timeouts, delays, and internal-link boundaries. It extracts only publicly displayed business emails and records source pages, titles, status, and signal evidence. A lead qualifies when a public business email, an active/complete crawl, a minimum score, and detected business activity (ecommerce or SaaS/B2B signals such as pricing, demos, free trial, clients, or case studies) are all present. `LEADGEN_DISCOVERY_SOURCES` remains an optional legacy directory supplement when search is configured; it is not required for normal discovery.

No search-results-page scraping, LinkedIn automation, purchased lists, authentication bypass, CAPTCHA bypass, or email sending is used. Add Lead and CSV import remain available as manual fallbacks.

Open **Campaigns**, create a draft, run **Dry run**, and inspect every recipient, subject, body, and qualification reason. The campaign default is 20/day and the hard guard rejects invalid email, missing factual personalization, duplicate sends, suppressed leads, unqualified leads, paused campaigns, and daily-limit overflow.

### Gmail OAuth

Never paste OAuth secrets into chat. The app uses Google's installed/desktop application flow with exactly `https://www.googleapis.com/auth/gmail.send`, `openid`, and `email`. Before connecting:

1. Create a Google Cloud project.
2. Enable the Gmail API.
3. Create a Desktop OAuth client.
4. Download the credentials JSON outside the repository.
5. Set:

```powershell
$env:GMAIL_CREDENTIALS_FILE = "C:\private\google-client.json"
$env:GMAIL_TOKEN_FILE = "C:\private\letrusto-gmail-token.json"
# Optional when the server address cannot be derived from the browser request.
# Must be an HTTP localhost callback ending in /gmail/oauth2callback.
# $env:GMAIL_OAUTH_REDIRECT_URI = "http://127.0.0.1:8768/gmail/oauth2callback"
```

6. Start:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8768
```

7. Open the same host and port used to start Uvicorn, for example `http://127.0.0.1:8768`.
8. Click **Connect Gmail**.
9. Sign in using `hello@letrusto.com`.
10. Approve Gmail send plus OpenID email identity permissions.
11. Return to LeadGen through the local callback.
12. Confirm `/gmail/status` reports `authorized: true`, `account: hello@letrusto.com`, and `token_valid: true`.
13. No campaign is automatically enabled.

The callback is local-only and is derived from the browser request host and port, for example `http://127.0.0.1:8768/gmail/oauth2callback`. Set `GMAIL_OAUTH_REDIRECT_URI` only when an explicit localhost callback is needed. Account validation uses the verified OpenID email identity and requests exactly `https://www.googleapis.com/auth/gmail.send`, `openid`, and `email`; it does not request Gmail profile-read scope. Existing tokens missing any required scope are stale and require reauthorization. The token is written to `GMAIL_TOKEN_FILE`; its parent directory is created and the file is written with restrictive permissions. If the token path is inside the repository, move it outside the repository yourself and update the environment variable; the app does not move user files.

If the account is wrong, authorization completes but sending remains blocked with `Connected Gmail account is not hello@letrusto.com.` Expired tokens refresh when possible; failed refresh reports `OAUTH_REQUIRED` and the Connect/Reauthorize action can be used again.

The safe status endpoint is `GET /gmail/status`. It never returns access tokens, refresh tokens, client secrets, or credentials JSON contents.

To run the opt-in worker after dry-run review and explicit campaign enablement:

```powershell
python -m app.worker
```

The worker polls every 15 minutes, sends gradually, records message IDs/statuses, schedules follow-up 1 after 4 days and follow-up 2 six days later, and stops on reply, unsubscribe, interest, trial, or paid status. OAuth authorization alone never starts the worker and never enables a campaign. Set `LEADGEN_GLOBAL_PAUSED=1` for a global emergency pause. Reply classification is manual through the lead API; the system never auto-replies.

DNS health is read-only at `/api/dns/status`. It reports SPF/DMARC when `dnspython` is installed and does not change DNS. DKIM requires the provider's selector and is not guessed.

## Workflow

1. Add a lead manually or open Import and upload a CSV. Common columns such as `Company`, `Website`, `Email`, `Founder`, `Owner`, `LinkedIn URL`, `Country`, and `Niche` are mapped automatically. Duplicate normalized websites or emails are skipped.
2. Open a lead, enter factual review and social-proof observations, and record why LeTrusto may fit. Use `Not verified` when you cannot confirm an observation.
3. Review the score explanation and select an outreach template. The generated subject and body are editable in Gmail.
4. Click **Open in Gmail**, review the message, and press Send yourself. Return to the lead and click **Mark sent**. The system records `CONTACTED` and schedules follow-up 1 after four days.
5. Follow-up 1 is due after four days; follow-up 2 is due ten days after initial contact. After follow-up 2, mark `NO_RESPONSE`. Replies are never answered automatically.
6. Use **Do not contact** for an opt-out. Suppressed leads remain for audit, never appear in the queue, and never receive generated outreach.

## Scoring

Maximum 100 points: active website 20, reviews 15, social proof 10, founder/contact 10, public business email 10, decision-maker role 10, clear fit 5, target niche 5, and review activity 5. Grades are A (80-100), B (60-79), C (40-59), and D (under 40). A lead marked `do_not_contact` receives 0 and grade D.

## Data operations

- Export with the **Export CSV** or **Export Excel** links, or `GET /export.csv` / `GET /export.xlsx`. The Excel file includes bold headers, sized columns, and a frozen header row.
- Back up by copying `data/leadgen.sqlite3` while the app is stopped.
- Reset the local database by stopping the app and deleting `data/leadgen.sqlite3`; it will be recreated on the next start. Do not point this setting at the LeTrusto production database.
- Synthetic sample data is in `data/sample_leads.csv`.

## Tests

```powershell
pytest -q
```

Tests use temporary SQLite databases and synthetic data only. They do not send email or contact any external service.

## First 30 leads

- Day 1: find 10 prospects from company websites, Google results, public directories, or manually researched LinkedIn pages.
- Day 2: find 10 more prospects and record factual proof observations.
- Day 3: find the final 10, score all 30, and qualify the best 20.
- Work through the best 20 one at a time: find, enter, score, personalize, open Gmail, review, send, mark sent, and move to the next.
