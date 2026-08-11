# LeTrusto Current Project State

> Last verified from repository: 2026-08-11
> Latest commit: `a2c3b0d` feat: add ElevenLabs vs Murf AI comparison buying guide

---

## Current Business Direction

LeTrusto is an **AI tools and software discovery, comparison, recommendation, guides, and affiliate monetization platform**.

The platform helps users compare AI tools, discover trusted software recommendations, and choose confidently before they pay.

## Current Product Vision

1. Build a trustworthy AI/software discovery website.
2. Create useful comparison pages, reviews, guides, and recommendations for AI tools and software.
3. Build affiliate revenue through approved affiliate programs.
4. Build SEO-focused content around software and AI tools.
5. Create a professional, scalable platform for software/AI discovery.
6. Track affiliate programs, approval status, commission structures, and affiliate links.

## Current Website Structure

### Frontend Routes

| Route | Type | Purpose |
|-------|------|---------|
| `/` | Public | Homepage — AI tools/software advisor |
| `/ai` | Public | AI buying assistant conversation |
| `/ai-tools` | Public | AI tools category landing |
| `/ai-tools/[slug]` | Public | Individual AI tool detail |
| `/guides` | Public | Buying guides listing |
| `/guides/[slug]` | Public | Dynamic guide page |
| `/guides/elevenlabs-pricing` | Public | ElevenLabs pricing breakdown (static) |
| `/guides/elevenlabs-vs-murf-ai` | Public | ElevenLabs vs Murf AI comparison (static) |
| `/articles` | Public | Articles listing (fetches from API) |
| `/articles/[slug]` | Public | Individual article |
| `/categories` | Public | Category listing |
| `/category/[slug]` | Public | Category detail |
| `/category/electronics` | Public | Electronics hub (legacy) |
| `/compare` | Public | Tool/product comparison |
| `/search` | Public | Search |
| `/deals` | Public | Deals listing |
| `/products/[id]` | Public | Product detail (legacy product system) |
| `/about` | Public | About page |
| `/methodology` | Public | Methodology/scoring explanation |
| `/affiliate-disclosure` | Public | Affiliate disclosure |
| `/contact` | Public | Contact form |
| `/support` | Public | Support / FAQ |
| `/report-issue` | Public | Issue reporting |
| `/privacy-policy` | Public | Privacy policy |
| `/terms-of-use` | Public | Terms of use |
| `/login` | Auth | Login page |
| `/register` | Auth | Registration page |
| `/dashboard` | Private | User dashboard |
| `/favorites` | Private | Saved favorites |
| `/notifications` | Private | User notifications |

### Navigation

- Navbar: Logo, AI Tools (dropdown with 5 categories), Guides, Compare, Deals, Search, Favorites, Auth (Sign In / User menu)
- Footer: Site links, legal pages, social links

## Current Frontend Architecture

| Component | Technology |
|-----------|-----------|
| Framework | Next.js 16.2.12 (App Router) |
| React | 19.2.4 |
| Styling | Tailwind CSS 4 |
| Icons | lucide-react |
| Animation | framer-motion |
| Language | TypeScript 5 (strict) |
| Linting | ESLint 9 with eslint-config-next |

### Key Architecture Patterns

- **Config-driven homepage**: `config/homepage.ts` defines sections; `HomepageSectionRenderer` dynamically renders them.
- **AI tools taxonomy**: `config/aiTools.ts` defines 5 public categories (Assistants, Writing, Image & Design, Video & Audio, Coding & Dev Tools).
- **Affiliate registry**: `lib/softwareAffiliates.ts` — centralized registry. Only tools with `status: "active"` get affiliate URLs surfaced.
- **Product affiliates**: `lib/affiliate.ts` — Amazon ASIN-based URL builder + Flipkart URL passthrough + click tracking.
- **API layer**: `services/api.ts` — robust URL normalization, static build detection, `withApiFallback()` for graceful degradation.
- **Auth**: `lib/authContext.tsx` — JWT access/refresh tokens in localStorage, hydration-safe initialization.
- **Analytics**: Google Analytics (GA4 `G-J8SC0HRNT2`), production-only, `lib/analytics.ts`.
- **Hooks**: `useAuth`, `useFavorites`, `useProducts`, `useRecentlyViewed`.

### Frontend Services

| Service | File | Purpose |
|---------|------|---------|
| API client | `services/api.ts` | Base HTTP client, URL normalization, fallback handling |
| AI tools | `services/ai-tools.service.ts` | `getAiTools()`, `getAiToolBySlug()`, `searchAiTools()`, `compareAiTools()`, `getAiToolRecommendations()` |
| AI assistant | `services/ai.service.ts` | Conversation, comparison summaries, review summaries, buying guides |
| Auth | `services/auth.service.ts` | Login, register, refresh, logout |
| Products | `services/product.service.ts` | Product search, filtering, details |
| Homepage | `services/homepage.service.ts` | Aggregates homepage data sources |

### Components (25 files)

Homepage section components (17): `HomepageSectionRenderer`, `HomeSectionHeader`, `HomeCategoryShowcase`, `HomeTrustSignalsSection`, `HomePopularComparisonsSection`, `HomeLatestGuidesSection`, `HomeProductRailSection`, `HomeProductGridSection`, `HomeFeaturedBrandsSection`, `HomeTrendingSearchesSection`, `HomeNewsletterSection`, `HomeAskAiCtaSection`, `HomeAIPicksFeaturedSection`, `HomeDealsSpotlightSection`, `HomeComingSoonRoadmapSection`, `HomeComingSoonVerticalSection`, `CategoryArtwork`.

Shared components (8+): `Navbar`, `Footer`, `SchemaOrg`, `AffiliateDisclosure`, `GoogleAnalytics`, `SearchBar`, `ProductCard`, `ProductCardSkeleton`, `ProductImageGallery`, `ProductBuyButtons`, `PriceHistoryChart`, `ProductReviews`, `CompareSection`, `SearchEnhancements`.

### Type Definitions

| File | Key Types |
|------|-----------|
| `types/ai-tools.ts` | `AITool`, `AIToolPricing`, `AIToolCategory`, `AIToolsCatalogResponse`, `AIToolSearchResponse`, `AIToolCompareResponse`, `AIToolRecommendationCandidateResponse` |
| `types/products.ts` | `Product`, `ProductBuyLink`, `ProductQueryOptions`, `PaginatedProductsResponse` (40+ types) |
| `types/auth.ts` | `AuthUser`, `AuthState`, `AuthResponse`, `LoginPayload`, `RegisterPayload` |
| `types/catalog.ts` | `CatalogCategoryNode`, `CatalogBrandEntry` |
| `types/ai.ts` | `ShoppingIntent`, `RankedRecommendation`, `RecommendationWorkflow`, `ComparisonSummary`, `ReviewSummary`, `BuyingGuide` |

### Static Assets

- Favicons: `favicon.ico`, `favicon-16x16.png`, `favicon-32x32.png`, `apple-touch-icon.png`, Android Chrome icons, `safari-pinned-tab.svg`, `site.webmanifest`
- Images: `public/images/` — `categories/`, `icons/`, `logo/`, `products/`, `og-default.svg`

## Current Backend Architecture

| Component | Technology |
|-----------|-----------|
| Framework | FastAPI (0.116.0+) |
| ORM | SQLAlchemy 2.0+ |
| Migrations | Alembic |
| DB driver | pg8000 |
| Auth | python-jose (JWT), passlib + bcrypt |
| Email | Resend |
| Config | pydantic-settings |
| Testing | pytest |
| Python | 3.11+ |

### API Endpoints (18 router modules)

All under `/api/v1/`:

| Module | Key Routes |
|--------|-----------|
| `health` | Health check |
| `ai` | `POST /assistant`, `GET /recommendations`, `POST /compare-summary`, `GET /products/{id}/review-summary`, `GET /products/{id}/buying-guide` |
| `ai_tools` | `GET /ai-tools`, `GET /ai-tools/search`, `GET /ai-tools/{slug}`, `POST /ai-tools/compare`, `GET /ai-tools/recommendations` |
| `auth` | `POST /auth/register`, `POST /auth/login`, `POST /auth/refresh`, `POST /auth/logout` |
| `users` | User profile CRUD |
| `products` | Product listing, search, detail |
| `categories` | Category listing |
| `articles` | Article listing, detail |
| `search` | Unified search |
| `compare` | Product comparison |
| `recommendations` | Product recommendations |
| `favorites` | User favorites CRUD |
| `notifications` | User notifications |
| `deals` | Deal listings |
| `support` | FAQ + support tickets |
| `analytics` | Event tracking |
| `admin` | Admin operations |
| `affiliate` | Affiliate link management |

### Backend Services (16 modules)

`ai_service`, `ai_tool_service`, `ai_tool_intent_router`, `ai_tool_mapper`, `ai_tool_provenance_catalog`, `ai_tool_recommendation_service`, `analytics_service`, `auth_service`, `admin_service`, `deal_service`, `email_service`, `favorite_service`, `notification_service`, `product_service` + `product_mapper`, `support_service`, `user_service`.

### AI Tool Recommendation Engine

- 7-factor weighted scoring: category (20%), use case (20%), features (20%), platform (10%), integration (10%), budget (15%), experience level (5%).
- Confidence scoring based on provenance, freshness, and metadata completeness.
- Fact provenance catalog: hardcoded sources for ChatGPT, Claude, Grammarly, GitHub Copilot, ElevenLabs.
- Intent routing via `AIToolIntentRouter`.

### Middleware

- **CORS**: Vercel wildcard + hardcoded domain list.
- **Rate limiting**: Sliding window per IP — 10 req/min for auth, 120 req/min global.
- **JWT exception handler**.

### Repositories

`ai_tool_repository` (search, provenance), `product_repository` (search, similarity), `favorite_repository`, `user_repository`.

## Current Database State

**Engine**: PostgreSQL (local service `postgresql-x64-18`), pg8000 driver. SQLite fallback (`letrusto.db`) exists.

### Migrations (8 total)

| # | File | Description |
|---|------|-------------|
| 1 | `20260731_01_init_schema` | Initial schema |
| 2 | `20260802_02_phase5_user_platform` | Users, refresh tokens, saved comparisons, price alerts, notifications, AI conversations/messages |
| 3 | `20260803_03_phase61_catalog_expansion` | Enriched product catalog (series, model, variant, storage, RAM, color) |
| 4 | `20260803_04_phase3_revenue_engine` | Revenue/analytics tables |
| 5 | `20260804_01_affiliate_links` | Product affiliate link fields |
| 6 | `20260808_02_stage2_ai_tools_foundation` | `AITool`, `AIToolCategory` tables |
| 7 | `20260808_03_stage3_recommendation_foundation` | `AIToolFactProvenance` table |
| 8 | `20260810_01_elevenlabs_affiliate_url` | Sets ElevenLabs `affiliate_available=true`, `affiliate_url` |

### Key Models

- **AITool** (22 fields): slug, provider, pricing, affiliate URL, scores, use cases, features, platforms, integrations.
- **AIToolCategory**, **AIToolFactProvenance** (source tracking).
- **Product** (50+ fields): full product catalog with affiliate fields (Amazon ASIN, Flipkart URL).
- **User**, **RefreshToken**, **SavedComparison**, **PriceAlert**, **Notification**.
- **AiConversation**, **AiMessage**.
- **AnalyticsEvent** (18+ event types), **Article**, **SupportTicket**, **Deal**.

## Current AI Features

- AI buying assistant conversation (`/ai` page, `AIConversationExperience` component).
- AI tool recommendation engine (7-factor scoring + confidence + provenance).
- AI tool comparison (`POST /ai-tools/compare`).
- Product review summaries, buying guides (backend endpoints).
- Intent routing for AI tool queries.

## Current Content/SEO System

### Published Guides

| Guide | Route | Last Verified |
|-------|-------|---------------|
| ElevenLabs Pricing | `/guides/elevenlabs-pricing` | 2026-08-10 |
| ElevenLabs vs Murf AI | `/guides/elevenlabs-vs-murf-ai` | 2026-08-10 |

### SEO Infrastructure

- `robots.ts`: Allows public routes, disallows auth/private routes.
- `sitemap.ts`: Static routes + category routes + 10 article slugs.
- Root layout: `metadataBase`, OG defaults, Twitter card, `%s | LeTrusto` title template.
- `SchemaOrg` component for structured data.
- Favicons and `site.webmanifest` for PWA.
- Google Analytics: `G-J8SC0HRNT2`.

### Catalog Tree (constants/index.ts)

Defines category hierarchy, brand catalog (smartphones: 12 brands, laptops: 8, etc.), and ~40 category label mappings. This is a legacy structure from the product marketplace phase — still referenced by sitemap and some routes.

## Current Affiliate System

### Software Affiliate Registry

File: `frontend/lib/softwareAffiliates.ts`

Centralized registry with `SoftwareAffiliate` type. Only entries with `status: "active"` are surfaced to users. Current entries:

| Tool | Status | Network | URL |
|------|--------|---------|-----|
| ElevenLabs | active | PartnerStack | `try.elevenlabs.io/l893urztlad5` |

### Product Affiliate System (Legacy)

File: `frontend/lib/affiliate.ts`

- Amazon Associates: ASIN-based URL builder, tag `letrusto-21` (env-configurable).
- Flipkart: URL passthrough.
- Click tracking via `trackAffiliateClick()`.

### Affiliate Disclosure

`components/AffiliateDisclosure.tsx` — renders disclosure banners near affiliate CTAs.

Dedicated page: `/affiliate-disclosure`.

## Current Affiliate Programs

See `docs/LETRUSTO_AFFILIATE_TRACKER.md` for the full tracker.

## Current Authentication

- JWT access tokens (15 min) + refresh tokens (7 days, stored hashed in DB).
- bcrypt password hashing (SHA256 pre-hash + bcrypt).
- `AuthProvider` context with localStorage token persistence.
- Routes: `/auth/register`, `/auth/login`, `/auth/refresh`, `/auth/logout`.
- Frontend pages: `/login`, `/register`, `/dashboard`.
- Google OAuth fields exist in User model (`google_id`) but OAuth flow is not wired.

## Current Testing Status

### Backend Tests (8 files)

| Test File | Coverage Area |
|-----------|--------------|
| `test_ai_service.py` | AI assistant service |
| `test_ai_tool_provenance_catalog.py` | Provenance catalog integrity |
| `test_ai_tool_recommendation_endpoint.py` | Recommendation API endpoint |
| `test_ai_tool_recommendation_service_stage3.py` | Recommendation scoring logic |
| `test_ai_tool_recommendation.py` | Recommendation flow |
| `test_ai_tool_service.py` | AI tool CRUD operations |
| `test_analytics_schema_stage3.py` | Analytics schema validation |
| `test_support_service.py` | Support ticket service |

### Frontend Tests

No dedicated test files. Validation relies on `npm run lint` and `npm run build`.

## Current Production Status

- **Frontend**: Deployed on Vercel (`vercel.json` present).
- **Backend**: Deployed on Railway (`railway.toml`, `Dockerfile`, `start.sh` present).
- **Domain**: `letrusto.com` (configured in metadata).
- **Email**: Resend integration for support/transactional emails.
- **Database**: PostgreSQL on Railway (production), local `postgresql-x64-18` (development).

## Known Issues

- Legacy product marketplace routes (`/products/[id]`, `/category/electronics`, product-focused components) still exist alongside the new AI tools direction. Not broken, but represent architectural debt.
- `sitemap.ts` references 10 hardcoded article slugs that may not exist in the backend.
- `constants/index.ts` `CATALOG_TREE` and `BRAND_CATALOG` are from the product marketplace phase — still used by sitemap category routes.
- Google OAuth fields exist in the User model but the OAuth flow is not implemented.
- Frontend has no dedicated test suite.

## Current Priorities

1. Build more AI tool comparison and pricing guide content.
2. Grow approved affiliate partnerships (see `docs/LETRUSTO_AFFILIATE_TRACKER.md`).
3. Expand the AI tools catalog in the backend.
4. Build SEO-focused content pages for high-value software keywords.
5. Clean up legacy product marketplace artifacts when appropriate.

## Completed Recently

| Date | Task |
|------|------|
| 2026-08-10 | ElevenLabs vs Murf AI comparison guide |
| 2026-08-10 | ElevenLabs pricing guide |
| 2026-08-10 | ElevenLabs affiliate link configured (PartnerStack) |
| 2026-08-10 | Affiliate-ready foundation (softwareAffiliates registry, disclosure component) |
| 2026-08-08 | Deterministic AI tool recommendation engine (7-factor scoring) |
| 2026-08-08 | AI tools Stage 2 foundation (catalog, search, provenance) |
| 2026-08-08 | AI tools domain foundation + strategy reset |

## Next Recommended Tasks

1. Create additional comparison guides for high-traffic AI tool matchups.
2. Apply for and onboard additional affiliate programs.
3. Add more AI tools to the backend catalog.
4. Create category-level content pages for each of the 5 AI tool categories.
5. Implement frontend testing (e.g., Vitest or Playwright).
6. Clean up legacy product marketplace code if the direction is confirmed permanent.

## Important Decisions

| Date | Decision |
|------|----------|
| 2026-08-08 | Pivoted from broad product marketplace to AI tools/software discovery platform. Old routes kept but hidden from primary navigation. |
| 2026-08-10 | Affiliate links served from centralized `softwareAffiliates.ts` registry and backend `affiliate_url` — never hardcoded in guide pages. |
| 2026-08-10 | Guide pages must cite official source URLs and verification dates for all pricing/feature claims. |

## Change Log

| Date | Change | Files | Validated |
|------|--------|-------|-----------|
| 2026-08-11 | Created project context system (.github/copilot-instructions.md, .github/agents/letrusto-builder.agent.md, docs/LETRUSTO_PROJECT_STATE.md, docs/LETRUSTO_AFFILIATE_TRACKER.md) | 4 new files | Pending build verification |
