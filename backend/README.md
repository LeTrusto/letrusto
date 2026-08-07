# LeTrusto Backend

FastAPI backend with clean architecture, PostgreSQL support, API versioning, and seed scripts.

## Run

1. Create and activate a Python 3.11+ virtual environment.
2. Install dependencies:

```bash
pip install -e .
```

3. Copy environment config:

```bash
cp .env.example .env
```

4. Create schema (dev shortcut):

```bash
python -m app.db.init_db
```

5. Seed realistic catalog data:

```bash
python scripts/seed_products.py
```

6. Start API:

```bash
uvicorn app.main:app --reload --port 8000
```

Docs: http://localhost:8000/docs

## Support Email

Support ticket submissions are saved to the database and also sent via Resend.

Required environment variables:

- `RESEND_API_KEY`
- `SUPPORT_EMAIL` (defaults to `hello@letrusto.com`)
- `FROM_EMAIL` (defaults to `support@letrusto.com`)

If email delivery fails, ticket creation still succeeds and the error is logged.

## Frontend switch

Set frontend API base URL only:

- `NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1`

The frontend service layer already has local fallback support.
