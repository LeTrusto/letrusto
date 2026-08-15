# LeTrusto Commerce — Architecture

## Stack

| Layer | Technology | Host |
|-------|-----------|------|
| Frontend | Next.js 16, React 19, TypeScript, Tailwind 4 | Vercel |
| Backend | Python 3.11+, FastAPI, SQLAlchemy 2.0 | Railway |
| Database | PostgreSQL (pg8000 driver) | Railway |
| Email | Resend | — |
| Analytics | Google Analytics 4 | — |

## Frontend Structure

```
frontend/
├── app/                        # Next.js App Router
│   ├── layout.tsx              # Root layout (navbar, footer, providers)
│   ├── page.tsx                # Commerce homepage
│   ├── globals.css             # Design tokens + component classes
│   ├── shop/                   # Category browse + filtering
│   ├── product/[slug]/         # Product detail
│   ├── cart/                   # Cart page
│   ├── login/ register/       # Auth (existing)
│   ├── dashboard/ favorites/  # Account (existing)
│   ├── about/ contact/ ...    # Info pages
│   └── (legacy AI routes parked, not deleted)
├── components/
│   ├── layout/                 # CommerceNavbar, CommerceFooter, MobileNav
│   ├── home/                   # Hero, section components
│   ├── products/               # ProductCard, ProductDetail
│   ├── cart/                   # CartDrawer, CartProvider
│   └── (existing components preserved)
├── config/homepage.ts          # Commerce homepage section config
├── lib/mockData.ts             # Mock product data (dev only)
├── lib/cartContext.tsx         # Cart state (React Context)
├── hooks/                      # useAuth, useFavorites, etc.
├── services/                   # API client, auth, products
└── types/commerce.ts           # Commerce type definitions
```

## Backend Structure

Existing backend preserved. AI endpoints remain operational.

New commerce endpoints will be added in future phases:
- `/api/v1/cart/`
- `/api/v1/orders/`
- `/api/v1/suppliers/`

## Data Flow (Phase 1)

All product data is mock (frontend only). No backend changes in Phase 1.

Future: Supplier → Raw Product → Normalized → Approved → Published → Customer.

## State Management

- Auth: React Context (`authContext.tsx`)
- Cart: React Context (`cartContext.tsx`)
- Favorites: localStorage + API sync (`useFavorites`)
- Recently Viewed: localStorage (`useRecentlyViewed`)

## Deployment

- Frontend: Vercel (preview on branches, production on main)
- Backend: Railway (auto-deploy, migrations on startup)
- Branch strategy: `feature/letrusto-commerce-v1` → PR → main
