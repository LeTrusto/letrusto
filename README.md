# LeTrusto

AI Shopping Assistant for India-focused product discovery, comparison, buying guides, and affiliate-ready commerce journeys.

## Completed Infrastructure

| Area | Status | Notes |
| --- | --- | --- |
| Frontend platform | Complete | Next.js 16 App Router app deployed through Vercel. |
| Backend platform | Complete | FastAPI service packaged for Railway Docker deployment. |
| Database | Complete | PostgreSQL schema managed with Alembic migrations and seed scripts. |
| Domain | Complete | Primary production domain is `https://letrusto.com` with `www` support in CORS and deployment config. |
| SSL / HTTPS | Complete | HTTPS is expected to be terminated by Vercel on the frontend and Railway-managed infrastructure on the backend. |
| SEO foundation | Complete | `robots.txt`, `sitemap.xml`, metadata, Open Graph, Twitter cards, and structured data are implemented. |
| Search indexing ops | Complete | Google Search Console DNS verification and sitemap submission are documented as completed operational steps. |
| Analytics | Complete | GA4 is integrated with production-only loading and App Router page-view tracking. |
| Affiliate foundation | Complete | Amazon Associates registration is documented with store ID `letrusto-21`, disclosure copy is live, and click tracking exists in the backend. |

## Documentation

- Full setup history: [docs/PROJECT_SETUP_HISTORY.md](docs/PROJECT_SETUP_HISTORY.md)
- Release notes: [CHANGELOG.md](CHANGELOG.md)

## Workspace Overview

```text
letrusto/
	frontend/   Next.js App Router frontend
	backend/    FastAPI backend with Alembic migrations
	docs/       Project and milestone documentation
```

## Core Stack

| Layer | Technology |
| --- | --- |
| Frontend | Next.js 16, React 19, TypeScript, Tailwind CSS 4 |
| Backend | FastAPI, SQLAlchemy 2, Alembic, Pydantic Settings |
| Database | PostgreSQL |
| Hosting | Vercel (frontend), Railway (backend) |
| Analytics | Google Analytics 4 |
| Commerce | Amazon Associates and retailer affiliate links |
