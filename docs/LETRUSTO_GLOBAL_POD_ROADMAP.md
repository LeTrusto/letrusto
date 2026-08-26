# LeTrusto Global Relaunch Roadmap

> Domain: letrusto.com (keeping as-is)
> Direction: Global print-on-demand + digital products + India local commerce
> Payments: Razorpay (India) + Stripe (Global)
> Supplier: Printful/Printify (global POD) + Baapstore (India local, optional later)

---

## CURRENT STATE DIAGNOSIS

### What We Have (Working)

| Asset | Status | Keep/Remove |
|---|---|---|
| letrusto.com domain + SSL | Live | KEEP |
| Next.js 16 frontend on Vercel | Live | KEEP |
| FastAPI backend on Railway | Live | KEEP |
| PostgreSQL database | Live | KEEP |
| User auth (OTP + email) | Working | KEEP |
| Admin panel (/admin) | Working | KEEP |
| Product catalog system | Working | KEEP + modify |
| Cart + checkout flow | Working | KEEP + modify |
| Razorpay payments (LIVE) | Working | KEEP for India |
| Google Analytics (GA4) | Working | KEEP |
| SEO (sitemap, robots, schema) | Working | KEEP + update |
| Commerce homepage | Working | KEEP + update tagline |
| Product cards/gallery/reviews | Working | KEEP |
| User accounts/favorites | Working | KEEP |

### What We Have (Legacy — To Remove)

| Asset | Status | Action |
|---|---|---|
| AI Tools catalog (/ai-tools) | Dead weight | REMOVE pages + config |
| AI Shopping Assistant (/ai) | Not revenue-producing | REMOVE |
| AI_TOOLS_PUBLIC_CATEGORIES config | Legacy | REMOVE |
| SOFTWARE_AFFILIATES registry | Old direction | REMOVE |
| AIConversationExperience component | Legacy | REMOVE |
| AIShoppingAssistant component | Legacy | REMOVE |
| AI Recommendation component | Legacy | REMOVE |
| CompareSection (AI tool comparisons) | Legacy | REMOVE |
| HOMEPAGE_POPULAR_COMPARISONS | Legacy | REMOVE |
| HOMEPAGE_TRENDING_SEARCHES (AI queries) | Legacy | REMOVE |
| Old CATALOG_TREE (Electronics, SaaS, etc.) | Legacy | REPLACE |
| CJ supplier validation UI (/admin/supplier-validation) | Keep in backend, hide from public | HIDE |
| Old product seeds (smartphones, hosting) | Dead | IGNORE (already disabled) |

### What We Need (New)

| Need | Priority | Stage |
|---|---|---|
| Stripe payment integration | HIGH | Stage 1 |
| Printful/Printify API integration | HIGH | Stage 2 |
| Multi-currency support (USD, EUR, GBP, INR) | HIGH | Stage 1 |
| Global shipping display | HIGH | Stage 2 |
| New product categories (POD) | HIGH | Stage 1 |
| New tagline + global messaging | HIGH | Stage 1 |
| Design upload + mockup display | MEDIUM | Stage 2 |
| Etsy-style digital download support | MEDIUM | Stage 3 |
| Updated SEO for global keywords | HIGH | Stage 1 |
| Social media marketing foundation | HIGH | Stage 3 |

---

## STAGE 1: CLEAN + REBRAND (Days 1-5)

Goal: Remove legacy, update branding for global audience, add Stripe.

### 1.1 Remove Legacy AI Tools

Files to remove or empty:
- frontend/config/aiTools.ts — replace with empty export
- frontend/app/ai-tools/ — remove or redirect to homepage
- frontend/app/ai/ — remove or redirect
- frontend/components/AI Recommendation.tsx — delete
- frontend/components/AIConversationExperience.tsx — delete
- frontend/components/AIShoppingAssistant.tsx — delete
- frontend/components/CompareSection.tsx — delete
- frontend/lib/softwareAffiliates.ts — empty the registry array
- frontend/services/ai-tools.service.ts — keep file but make functions return empty
- frontend/services/ai.service.ts — keep file but make functions return empty

Do NOT delete backend AI services yet (they have tests and models). Just disconnect frontend.

### 1.2 Update Branding + Messaging

Current: "Discover trending beauty, jewellery and style finds at everyday prices"
New: "Unique designs. Global delivery. Your style, printed fresh."

Update in:
- frontend/app/layout.tsx (metadata title, description, keywords, OG tags)
- frontend/app/page.tsx (metadata)
- frontend/components/home/Hero.tsx (headline, subheadline, CTA buttons)
- frontend/components/SchemaOrg.tsx (if hardcoded text)

New keywords:
- custom t-shirts, printed products, unique designs, global shipping
- custom mugs, phone cases, wall art, tote bags
- print on demand, fresh prints, made to order

New Hero:
- Headline: "YOUR DESIGN. FRESHLY PRINTED. DELIVERED WORLDWIDE."
- Subtext: "Custom apparel, accessories and home decor — printed on demand and shipped to your door."
- CTA 1: "SHOP DESIGNS" → /shop
- CTA 2: "HOW IT WORKS" → /how-it-works

### 1.3 Update Categories

Replace current ShopByStyle categories:
- Old: jewellery, hair-style, beauty-tools, accessories, gifts
- New: apparel, wall-art, accessories, home-living, stationery

Update:
- frontend/types/commerce.ts (CommerceCategory type)
- frontend/components/home/ShopByStyle.tsx (category list)
- frontend/constants/index.ts (CATALOG_TREE — replace with POD categories)

New CATALOG_TREE:
```
Apparel: T-Shirts, Hoodies, Sweatshirts, Tank Tops, Crop Tops
Wall Art: Posters, Canvas Prints, Framed Prints
Accessories: Phone Cases, Tote Bags, Backpacks, Hats
Home & Living: Mugs, Cushion Covers, Coasters, Blankets
Stationery: Notebooks, Stickers, Magnets
```

### 1.4 Multi-Currency Support

Update:
- frontend/types/commerce.ts: change `currency: "INR"` to `currency: "INR" | "USD" | "EUR" | "GBP"`
- Add currency detection based on visitor geo (or manual selector)
- Product prices stored in USD as base, converted for display
- Backend: add `base_currency` and `price_usd` fields to Product model

### 1.5 Add Stripe Integration

Backend:
- Add stripe Python package to requirements.txt
- Create backend/app/services/stripe_service.py
- Create Stripe checkout session endpoint: POST /api/v1/payments/stripe/create-session
- Create Stripe webhook endpoint: POST /api/v1/webhooks/stripe
- Add STRIPE_SECRET_KEY and STRIPE_WEBHOOK_SECRET to config

Frontend:
- Add @stripe/stripe-js to package.json
- Create frontend/services/stripe.service.ts
- Update checkout page: show Razorpay for IN visitors, Stripe for others
- Add Stripe publishable key to env: NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY

### 1.6 Updated SEO

- frontend/app/robots.ts: keep allowing /shop, /product, remove /ai-tools
- frontend/app/sitemap.ts: remove AI tools routes, add new category routes
- Update OG image to reflect new brand direction
- Add hreflang tags for multi-region (en-IN, en-US, en-GB, en)

---

## STAGE 2: PRINTFUL INTEGRATION (Days 6-14)

Goal: Connect Printful API, import products, display mockups, enable ordering.

### 2.1 Printful API Setup

- Sign up at printful.com (free)
- Get API key from Printful dashboard
- Add PRINTFUL_API_KEY to backend config

### 2.2 Backend: Printful Adapter

Create: backend/app/suppliers/adapters/printful_adapter.py

Implement SupplierAdapter protocol:
- authenticate() — validate API key
- get_categories() — map Printful product types
- search_products() — list Printful catalog items
- get_product() — get product details + variants + mockup URLs
- calculate_shipping() — Printful shipping rates by destination
- create_order() — submit order to Printful with customer address + design

Update: backend/app/suppliers/factory.py
- Add `if name == "printful": return PrintfulAdapter(api_key=...)`

### 2.3 Product Import Flow

Admin workflow:
1. Admin selects Printful base product (e.g., "Unisex Staple T-Shirt")
2. Admin uploads design file (PNG/SVG)
3. System generates mockup via Printful Mockup Generator API
4. Admin sets selling price, title, description
5. Product saved to catalog as status=DRAFT
6. Admin activates → product appears in store

Database: Products from Printful stored with:
- supplier = "printful"
- supplier_product_id = Printful product ID
- Variant records for each size/color
- Image URLs from Printful mockup API

### 2.4 Frontend: Product Display

Product pages show:
- Mockup images (from Printful)
- Size/color variant selector
- Price in visitor's currency
- Shipping estimate by region
- "Made to order — ships in 2-5 business days" badge
- Size guide link

### 2.5 Order Flow

1. Customer adds to cart
2. Checkout: enters address
3. System detects country → shows Stripe (global) or Razorpay (India)
4. Payment confirmed
5. Backend creates Printful order via API with:
   - Customer shipping address
   - Selected variant (product + size + color)
   - Design file URL
   - Shipping method
6. Printful prints + ships
7. Tracking number synced back to LeTrusto order
8. Customer notified

### 2.6 Shipping Rates

Printful provides real-time shipping rates:
- US: $4-8 (3-5 days)
- EU: $4-10 (5-10 days)
- India: $8-15 (10-20 days)
- Rest of world: varies

Display to customer at checkout based on their address.

---

## STAGE 3: DESIGNS + MARKETING (Days 15-30)

Goal: Create initial product catalog, launch marketing.

### 3.1 Create 30 Designs

Niches that sell on POD:
1. Indian art / mandala patterns (global appeal)
2. Yoga / meditation / spiritual quotes
3. Minimalist typography
4. Abstract art / geometric
5. Nature / botanical illustrations
6. Funny quotes / memes
7. Motivational / hustle culture
8. Pet lover designs
9. Zodiac / astrology
10. Travel / wanderlust

Tools:
- Midjourney or DALL-E for base artwork
- Canva for text overlays and variants
- Remove.bg for transparent backgrounds
- Ensure 300 DPI, minimum 4500x5400px for t-shirt prints

### 3.2 Product Catalog (Initial)

| Product | Variants | Price (USD) | Your Cost | Profit |
|---|---|---|---|---|
| Unisex T-Shirt | 5 sizes, 6 colors | $28-32 | ~$13 | ~$15-19 |
| Hoodie | 5 sizes, 4 colors | $42-48 | ~$28 | ~$14-20 |
| Poster (18x24) | 3 sizes | $18-28 | ~$8-14 | ~$10-14 |
| Mug (11oz) | White/black | $16-20 | ~$8 | ~$8-12 |
| Tote Bag | Natural/black | $22-26 | ~$13 | ~$9-13 |
| Phone Case | Per model | $22-28 | ~$11 | ~$11-17 |
| Canvas Print | 3 sizes | $38-65 | ~$20-35 | ~$18-30 |
| Stickers | Sheet | $5-8 | ~$2-3 | ~$3-5 |

30 designs × 3-4 product types = 90-120 product listings

### 3.3 Marketing Channels (Free/Low Cost)

**Pinterest (highest ROI for POD):**
- Create business account
- Pin every product with keyword-rich descriptions
- Create boards: "Mandala Art", "Yoga Gifts", "Minimalist Home Decor"
- Pin 10-20 per day for first month
- Pinterest drives purchase-intent traffic

**Instagram:**
- Post product mockups daily
- Use Reels showing design process
- Hashtags: #printedtee #customdesign #yogalife #mandalaart
- Link in bio → letrusto.com

**TikTok:**
- Short videos: "Designing a t-shirt in 60 seconds"
- Behind-the-scenes content
- Trending audio + product showcase

**Etsy (parallel sales channel):**
- List same products on Etsy
- Etsy has built-in traffic (millions of buyers)
- Printful integrates directly with Etsy
- $0.20 per listing + 6.5% transaction fee

**SEO (long-term):**
- Blog posts: "Best Mandala Gifts for Yoga Lovers"
- Product pages optimized for long-tail keywords
- Category pages targeting "custom [product] online"

### 3.4 Digital Products (Zero Fulfillment)

Add digital download capability:
- Printable wall art (PDF/PNG, instant download)
- Canva templates
- Digital planners
- Priced at $3-$15
- Near 100% margin after Stripe fees

Backend: Add `is_digital` flag to Product model
Frontend: After payment, show download link instead of shipping tracking

---

## STAGE 4: OPTIMIZE + SCALE (Month 2+)

### 4.1 Analytics-Driven Decisions
- Track which designs sell best
- Track which products have highest margin
- Track traffic sources (Pinterest vs Instagram vs direct)
- Double down on winners, remove losers

### 4.2 Email Marketing
- Collect emails via newsletter signup (already built)
- Send weekly "New Designs" email
- Abandoned cart emails
- Use Resend (already integrated) or switch to free tier of Mailchimp

### 4.3 Paid Ads (When Profitable)
- Start with $5-10/day on Pinterest Ads
- Target high-intent keywords: "custom yoga t-shirt", "mandala wall art"
- Only scale after positive ROAS confirmed

### 4.4 Expand Product Line
- Add seasonal designs (Christmas, Diwali, Valentine's)
- Add niche collections based on what sells
- Consider all-over-print products (higher margins)
- Add embroidered items (premium pricing)

### 4.5 India Local Commerce (Optional)
- If Indian traffic grows, add Baapstore products
- Beauty, jewellery, accessories for Indian audience
- Razorpay + COD for India orders
- Keep as separate category or section

---

## TECHNICAL CHANGES SUMMARY

### Frontend Changes Required

| File/Area | Change | Effort |
|---|---|---|
| app/layout.tsx | Update metadata, description, keywords | 30 min |
| app/page.tsx | Update metadata | 15 min |
| components/home/Hero.tsx | New headline, CTA | 30 min |
| components/home/ShopByStyle.tsx | New POD categories | 30 min |
| types/commerce.ts | Add currency types, digital flag | 30 min |
| constants/index.ts | Replace CATALOG_TREE with POD categories | 45 min |
| config/homepage.ts | Remove AI references, update trust signals | 30 min |
| config/aiTools.ts | Empty or delete | 15 min |
| Remove AI pages (ai-tools/, ai/) | Delete or redirect | 30 min |
| Remove AI components (5+ files) | Delete | 15 min |
| lib/softwareAffiliates.ts | Empty array | 5 min |
| services/stripe.service.ts | NEW — Stripe checkout | 2 hrs |
| app/checkout/ | Add Stripe vs Razorpay selection | 2 hrs |
| Currency selector component | NEW — geo-based or manual | 1 hr |
| Product page size guide | NEW | 1 hr |
| "How It Works" page | NEW | 1 hr |
| Shipping info page | UPDATE for global | 1 hr |

### Backend Changes Required

| File/Area | Change | Effort |
|---|---|---|
| requirements.txt | Add stripe, httpx (if not present) | 5 min |
| app/core/config.py | Add STRIPE_SECRET_KEY, PRINTFUL_API_KEY | 15 min |
| app/services/stripe_service.py | NEW — create session, handle webhook | 3 hrs |
| app/api/v1/endpoints/payments.py | Add Stripe endpoints | 2 hrs |
| app/suppliers/adapters/printful_adapter.py | NEW — full adapter | 4 hrs |
| app/suppliers/factory.py | Add printful case | 15 min |
| app/models/entities.py | Add is_digital, base_price_usd fields | 30 min |
| alembic migration | New migration for schema changes | 30 min |
| app/services/fulfillment_service.py | Add Printful order submission | 2 hrs |
| tests/ | New tests for Stripe + Printful | 2 hrs |

### Total Estimated Development Effort

| Stage | Days | What |
|---|---|---|
| Stage 1 (Clean + Rebrand) | 3-5 days | Remove legacy, update branding, add Stripe |
| Stage 2 (Printful Integration) | 5-7 days | API adapter, product import, order flow |
| Stage 3 (Designs + Marketing) | 7-14 days | Create products, launch channels |
| Stage 4 (Optimize) | Ongoing | Scale based on data |

**Total to first sale: approximately 2-3 weeks of focused work.**

---

## COSTS

| Item | Monthly Cost | Notes |
|---|---|---|
| Vercel (frontend) | Free (hobby) or $20/mo (pro) | Current plan |
| Railway (backend) | ~$5-10/mo | Current plan |
| Printful | $0 | Free until orders come in |
| Stripe | 2.9% + $0.30 per transaction | Only when selling |
| Razorpay | 2% per transaction | Only for India orders |
| Canva Pro | ₹500/mo (~$6) | For design creation |
| Domain (letrusto.com) | Already paid | Existing |
| Etsy listings | $0.20 each | Only if listing there |
| **Total fixed monthly cost** | **~$10-35** | Before any revenue |

---

## REVENUE PROJECTIONS (Conservative)

### Month 1 (Setup + First Sales)
- Products listed: 30-50
- Orders: 5-15
- Average order: $25
- Revenue: $125-375
- Profit (after Printful cost): $60-180
- Status: Testing, learning what sells

### Month 2-3 (Growing)
- Products listed: 80-120
- Orders: 30-60/month
- Average order: $28
- Revenue: $840-1,680/month
- Profit: $400-850/month
- Status: Scaling winners, removing losers

### Month 6+ (Established)
- Products listed: 200+
- Orders: 100-300/month
- Average order: $30
- Revenue: $3,000-9,000/month
- Profit: $1,500-4,500/month
- Status: Sustainable business with multiple channels

These are conservative estimates. Many POD stores do $0 because they quit in week 2. Consistency matters more than perfection.

---

## IMMEDIATE NEXT STEPS (Today)

1. Confirm: "Yes, start Stage 1" → I begin removing legacy and updating branding
2. Sign up for Printful (printful.com) — free, takes 5 minutes
3. Sign up for Stripe India (stripe.com/in) — needs your business PAN/GST
4. Start collecting design ideas (save inspiring images from Pinterest)

---

## WHAT I (COPILOT) WILL DO

- Remove all legacy AI tools code from frontend
- Update homepage, metadata, and SEO for global POD
- Add Stripe payment integration (backend + frontend)
- Build Printful adapter using existing SupplierAdapter pattern
- Add multi-currency support
- Create "How It Works" page
- Update shipping and returns pages
- Write tests for new integrations
- Help with product descriptions and SEO content

## WHAT YOU NEED TO DO

- Sign up for Printful + Stripe
- Create designs (I can help with prompts and concepts)
- Upload designs to Printful
- Set prices
- Start posting on Pinterest and Instagram
- Monitor orders and customer feedback
- Decide on Etsy (recommended as parallel channel)

---

## RISKS AND MITIGATION

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| No traffic | High initially | No sales | Pinterest + Etsy provide discovery; SEO builds over time |
| Design competition | High | Lower margins | Niche down; unique Indian-origin art has less competition |
| Printful quality issues | Low | Returns | Order samples first; stick to their top-rated products |
| Stripe approval delay | Low | Can't accept global payments | Apply early; have all documents ready |
| Currency fluctuation | Medium | Margin variance | Price in USD; accept INR margin variation |
| Burnout / giving up | Medium | Business dies | Start small (30 products), don't over-commit |

---

## DECISION LOG

| Date | Decision | Reason |
|---|---|---|
| 2026-08-26 | Drop CJ as primary supplier | 12-50 day India delivery unsuitable |
| 2026-08-26 | Keep letrusto.com domain | Already purchased, works globally |
| 2026-08-26 | Global POD as primary direction | Low cost, high margin, no inventory |
| 2026-08-26 | Razorpay (India) + Stripe (Global) | Cover all customer regions |
| 2026-08-26 | Printful as primary POD supplier | Free, reliable, good API, global warehouses |
| 2026-08-26 | Remove AI tools frontend | Legacy, confusing, not revenue-producing |
| 2026-08-26 | Keep backend intact (CJ, admin) | Tests pass, no reason to break things |
