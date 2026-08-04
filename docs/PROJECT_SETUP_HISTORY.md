# LeTrusto Project Setup History

## Purpose

This document records the completed setup work for LeTrusto from initial repository creation through the current milestone, `v0.3.0 - SEO, Analytics & Affiliate Foundation`.

## Project Vision

LeTrusto is intended to be an India-focused AI buying advisor that helps users:

- compare products across key consumer categories,
- discover the strongest value options using rules and AI-style recommendations,
- read buying guides and comparison content,
- track prices and retail links, and
- monetize responsibly through disclosed affiliate partnerships.

## Current Milestone Snapshot

| Item | Status | Source of truth |
| --- | --- | --- |
| Public site | Complete | `https://letrusto.com` |
| Frontend hosting | Complete | Vercel via `vercel.json` |
| Backend hosting | Complete | Railway via `railway.toml` and `backend/railway.toml` |
| API versioning | Complete | `/api/v1` |
| Database migrations | Complete | Alembic in `backend/alembic/versions` |
| SEO routes | Complete | `frontend/app/robots.ts`, `frontend/app/sitemap.ts` |
| GA4 integration | Complete | `frontend/components/GoogleAnalytics.tsx`, `frontend/lib/analytics.ts` |
| Affiliate foundation | Complete | frontend disclosures plus backend click tracking |

## Technology Stack

| Layer | Selection | Notes |
| --- | --- | --- |
| Frontend | Next.js 16.2.12 | App Router, metadata routes, `next/script`, production builds on Vercel |
| UI | React 19.2.4 | Client and server component mix |
| Language | TypeScript 5 | Frontend typed application code |
| Styling | Tailwind CSS 4 | Utility-based styling across app and components |
| Animation | Framer Motion | Hero and UI motion primitives |
| Backend | FastAPI | Versioned API in `backend/app/api/v1` |
| ORM | SQLAlchemy 2 | Database access and mapping |
| Migrations | Alembic | Schema evolution for products, users, analytics, affiliate tracking, and articles |
| Database | PostgreSQL | Production-oriented relational store |
| Deployment | Vercel + Railway | Split frontend/backend hosting model |
| Analytics | Google Analytics 4 | Production-only script loading |
| Affiliate stack | Amazon Associates + direct retailer links | Supports click tracking and disclosure-driven monetization |

## Setup Timeline

## 1. Inception and Monorepo Foundation

- Created the top-level monorepo with separate `frontend` and `backend` applications.
- Added deployment descriptors at the repository root for Vercel and Railway.
- Established LeTrusto branding and the core "Know Before You Buy" positioning.

### Completed outputs

- Root repository structure with deployable frontend and backend apps.
- Vercel build configuration in `vercel.json`.
- Railway deployment configuration in `railway.toml`.

## 2. Frontend Application Foundation

- Bootstrapped the frontend as a Next.js App Router application.
- Adopted TypeScript, Tailwind CSS 4, and `next/font` for the UI foundation.
- Added global layout structure with navbar, footer, and shared metadata.
- Built the first pass of homepage, category, product, compare, search, AI, and support experiences.

### Completed outputs

- App Router route structure under `frontend/app`.
- Shared component library under `frontend/components`.
- Frontend build and lint scripts in `frontend/package.json`.

## 3. Backend and Data Platform Foundation

- Built the backend as a FastAPI service with a versioned `/api/v1` surface.
- Added SQLAlchemy-based persistence and Alembic migration support.
- Standardized PostgreSQL connectivity and Railway runtime settings.
- Added seed and import scripts for products, hosting/SaaS data, and articles.

### Completed outputs

- FastAPI app and routing under `backend/app`.
- Alembic migrations under `backend/alembic/versions`.
- Railway backend startup command with `alembic upgrade head && uvicorn ...`.
- Config template in `backend/.env.example`.

## 4. Product, Content, and User Platform Expansion

- Added a richer catalog with product categories, price history, reviews, and AI scores.
- Added search, recommendations, compare flows, and related-product logic.
- Added auth, notifications, deals, support, and saved user flows.
- Introduced article support and content seeding for buying guides and comparisons.

### Completed outputs

- Catalog and recommendation services in `frontend/lib` and `frontend/services`.
- Backend user-platform migration: `backend/alembic/versions/20260802_02_phase5_user_platform.py`.
- Revenue and content migration: `backend/alembic/versions/20260803_04_phase3_revenue_engine.py`.

## 5. SEO, Analytics and Affiliate Foundation

This is the current milestone documented by `v0.3.0`.

### Domain Configuration

| Setting | Value | Notes |
| --- | --- | --- |
| Primary domain | `https://letrusto.com` | Used in metadata, robots, sitemap, and canonical-style URLs |
| Secondary domain | `https://www.letrusto.com` | Included in backend CORS allowlist |
| Preview / deployment domain | `https://letrusto.vercel.app` | Included in backend CORS allowlist |
| API prefix | `/api/v1` | Consistent across frontend services and backend routes |

### SSL / HTTPS Setup

- Frontend traffic is expected to terminate over HTTPS on Vercel.
- Backend production traffic is expected to terminate over Railway-managed HTTPS endpoints.
- Application metadata, sitemap entries, robots sitemap reference, and CORS configuration all assume HTTPS-first production traffic.

### robots.txt Implementation

LeTrusto uses a Next.js metadata route instead of a static text file.

```ts
// frontend/app/robots.ts
export default function robots() {
  return {
    rules: [{ userAgent: "*", allow: "/", disallow: ["/dashboard", "/notifications", "/admin"] }],
    sitemap: "https://letrusto.com/sitemap.xml",
  };
}
```

### robots.txt status checklist

- [x] Public pages allowed for crawling
- [x] Private or authenticated sections disallowed
- [x] Sitemap location declared

### sitemap.xml Generation

LeTrusto generates its sitemap dynamically through a Next.js metadata route.

| Sitemap area | Included |
| --- | --- |
| Homepage | Yes |
| Compare | Yes |
| AI advisor | Yes |
| Search | Yes |
| Deals | Yes |
| Articles index | Yes |
| Support | Yes |
| Category pages | Yes |
| Launch article pages | Yes |

```ts
// frontend/app/sitemap.ts
export default function sitemap() {
  return [...STATIC_ROUTES, ...CATEGORY_ROUTES, ...ARTICLE_ROUTES];
}
```

### Google Search Console Setup

The following steps are recorded as completed operational work outside the source tree:

- [x] DNS ownership verification completed for `letrusto.com`
- [x] Property added in Google Search Console
- [x] Sitemap submitted: `https://letrusto.com/sitemap.xml`
- [x] Search indexing foundation aligned with robots and metadata routes

### Google Analytics GA4 Setup

| Setting | Value |
| --- | --- |
| Measurement ID | `G-J8SC0HRNT2` |
| Loading strategy | `next/script` with `afterInteractive` |
| Environment gating | Production only |
| Tracking mode | Manual `page_view` events on route changes |
| Duplicate prevention | `send_page_view: false` plus last-tracked URL guard |

#### Measurement ID configuration

- The public GA4 Measurement ID is stored in the frontend analytics configuration module: `frontend/lib/analytics.ts`.
- No private GA secrets or server credentials are committed to the repository.
- Future environment-based migration can be done without changing the rest of the route-tracking API because the integration is isolated behind the analytics utility.

#### Production-only loading using `next/script`

```tsx
// frontend/components/GoogleAnalytics.tsx
if (process.env.NODE_ENV !== "production") {
  return null;
}
```

#### Route change tracking with App Router

- `usePathname()` is used to detect route changes in the App Router.
- Query-string awareness comes from `window.location.search` at runtime.
- Page views are emitted through a shared `trackPageView(url)` utility.

#### Duplicate `page_view` prevention

- Automatic GA page views are disabled with `send_page_view: false`.
- The tracker caches the last sent URL in a `useRef` value.
- A new event is emitted only when the effective URL changes.

### Affiliate Foundation

Affiliate setup now spans disclosure, outbound link presentation, and backend analytics.

| Item | Status | Notes |
| --- | --- | --- |
| Amazon Associates registration | Complete | Operating store ID: `letrusto-21` |
| Tax information | Complete | Recorded as completed operational onboarding |
| Retailer links | Complete | Amazon, Flipkart, Croma, and selected SaaS/hosting brands |
| Affiliate disclosure | Complete | Present in footer and buy-button flows |
| Click tracking | Complete | Backend endpoint records click counts and analytics events |

#### Affiliate implementation notes

- The frontend surfaces affiliate disclosures in `frontend/components/Footer.tsx` and `frontend/components/ProductBuyButtons.tsx`.
- The backend click endpoint lives in `backend/app/api/v1/endpoints/affiliate.py`.
- Affiliate-capable schema support was introduced in `backend/alembic/versions/20260803_04_phase3_revenue_engine.py`.

## Files Added and Modified for the Current Milestone

### SEO and metadata

| File | Role |
| --- | --- |
| `frontend/app/layout.tsx` | Global metadata, schema mounting, and analytics mount point |
| `frontend/app/robots.ts` | Dynamic `robots.txt` generation |
| `frontend/app/sitemap.ts` | Dynamic sitemap generation |

### Analytics

| File | Role |
| --- | --- |
| `frontend/components/GoogleAnalytics.tsx` | Production-only GA script loading and route tracking |
| `frontend/lib/analytics.ts` | Reusable GA configuration and event helpers |

### Affiliate and monetization foundation

| File | Role |
| --- | --- |
| `frontend/components/ProductBuyButtons.tsx` | Outbound retailer buttons and click tracking |
| `frontend/components/Footer.tsx` | Affiliate disclosure copy |
| `backend/app/api/v1/endpoints/affiliate.py` | Affiliate click ingest endpoint |
| `backend/alembic/versions/20260803_04_phase3_revenue_engine.py` | Affiliate schema columns and articles table |
| `backend/scripts/seed_hosting_saas.py` | SaaS and hosting affiliate seed data |
| `backend/scripts/seed_products.py` | Marketplace link generation |

### Deployment and configuration

| File | Role |
| --- | --- |
| `vercel.json` | Frontend Vercel build configuration |
| `railway.toml` | Root Railway deployment configuration |
| `backend/railway.toml` | Backend deploy and startup configuration |
| `backend/.env.example` | CORS, API prefix, token, and environment template |

## Current Infrastructure Status

| System | Status | Detail |
| --- | --- | --- |
| Frontend build | Healthy | `npm run build` completes successfully in the current milestone |
| Homepage prerender | Healthy | Homepage has fallback-safe static generation behavior |
| Backend API | Configured | FastAPI app with Railway deployment path and `/api/v1` namespace |
| Database migrations | Healthy | Alembic migrations cover core schema, user platform, and revenue/content engine |
| SEO endpoints | Healthy | `robots.txt` and `sitemap.xml` are generated by the app |
| Analytics integration | Healthy | GA4 production-only load and App Router page-view tracking are wired |
| Affiliate tracking | Healthy | Buy-link click tracking endpoint is available |

## Pending Roadmap

- [ ] Move GA Measurement ID to environment-based runtime configuration if multi-environment analytics separation becomes necessary.
- [ ] Add Search Console and analytics dashboards to operational runbooks.
- [ ] Expand sitemap coverage to dynamically generated product detail pages and article inventory from the API.
- [ ] Add first-party event taxonomy for search, compare, AI prompt, deal click, and article engagement events.
- [ ] Add affiliate reporting dashboards for retailer, category, and article conversion views.
- [ ] Add explicit privacy policy and terms pages instead of temporary support-page placeholders.
- [ ] Formalize canonical URL strategy for every long-tail page type.

## Operational Notes

```bash
# Frontend validation
cd frontend
npm run build

# Backend local run
cd backend
uvicorn app.main:app --reload --port 8000
```

This document should be updated whenever production infrastructure, analytics, SEO, domain operations, or affiliate systems materially change.