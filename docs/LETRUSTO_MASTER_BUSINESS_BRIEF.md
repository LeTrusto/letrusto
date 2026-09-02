# LeTrusto Master Business Brief

> Strategy reference updated: 2026-09-02

## Current Direction

LeTrusto is transitioning from a physical-product-first ecommerce website into an India-first digital business platform offering:

1. Practical free tools
2. Useful digital products and templates
3. Affordable, productized digital services

The existing Next.js, Vercel, FastAPI, Railway, PostgreSQL, Alembic, authentication, admin, Resend, GA4, SEO, support, affiliate, customer-account, Razorpay, product, cart, order, and Printful infrastructure must be preserved where practical. Physical commerce is reusable infrastructure, not the primary public identity during the initial digital-first launch.

## Business Flywheel

```text
Attract -> Help -> Build Trust -> Sell -> Upsell -> Retain

Search / Social / Referral
        -> Free Tool
        -> Useful Result
        -> Related Template
        -> Digital Sale
        -> Service Offer
        -> Custom Service
        -> Repeat Customer
```

The objective is real users, real value, real enquiries, real purchases, and real profit. Do not optimize for feature count.

## Primary Pillars

### 1. LeTrusto Tools: traffic engine

Free tools should normally work without login and should solve genuine problems. Initial candidates include:

- Invoice generator
- Profit margin calculator
- Pricing calculator
- Break-even calculator
- Expense calculator
- Salary or hike calculator

Select future tools using search demand, user problems, competition, development effort, maintenance, SEO potential, monetization, and relevance to LeTrusto products or services.

Free tools can lead naturally to related templates, premium versions, bundles, services, or email/contact opportunities. Avoid aggressive upselling.

### 2. LeTrusto Templates: repeatable digital revenue

Prioritize practical products with a clear target customer and immediate usefulness:

- Invoice and quotation systems
- Expense, profit, cash-flow, inventory, and customer trackers
- Freelancer and agency onboarding, proposal, invoice, and project kits
- Small-business starter bundles
- Canva business and social-media templates
- Resume, portfolio, interview, and job-search resources
- Business planning and finance systems
- Google Sheets, Excel, Notion, dashboards, and focused AI-assisted resources later

Avoid generic motivational PDFs, generic planners, low-value prompt collections, mass-generated content, and products customers can easily recreate without meaningful value.

Every product should have a clear audience, professional previews, useful instructions, licensing, delivery method, and refund terms.

### 3. LeTrusto Services: cash-flow and high-value revenue

Services must be productized, with flexible pricing based on scope, effort, demand, complexity, margin, and support requirements. Candidate services include:

- Business website setup
- Landing pages and website redesign
- Ecommerce setup
- WhatsApp and lead-form integrations
- Business automation
- Dashboards
- Custom business tools and web applications

Use approachable entry offers, but never promise unlimited work at a low price. Every service must define scope, exclusions, delivery expectations, revision limits, and add-ons.

Possible add-ons include extra pages, revisions, content upload, SEO, analytics, WhatsApp integration, Google Business setup, maintenance, functionality, automation, and custom dashboards.

Do not hardcode business prices into the application architecture. Prices are commercial configuration and may change.

## Secondary and Future Areas

### Minku & Dinku

Treat Minku & Dinku as a separate sub-brand or section for coloring books, activity books, worksheets, printable activities, and educational packs. Do not mix children's products heavily with the main business-services identity.

### Global digital products

Expand globally only after India-first validation. Downloadable products are expected to be easier to internationalize than custom services or physical products.

Recommended progression:

```text
India services -> India digital products -> Global digital products
-> Global tools/content -> Global services
```

Global requirements may include local pricing, international payment methods, licensing, privacy, refunds, VAT or sales-tax handling, GST/export rules, foreign-exchange records, and payment-provider eligibility.

### Premium tools, SaaS, memberships, affiliates, and physical products

These are future options, not immediate commitments. Evaluate them using demand, competition, differentiation, development effort, maintenance, profitability, acquisition potential, cross-sell potential, legal implications, and fit with LeTrusto.

Keep Printful and physical commerce available as secondary infrastructure. Do not expand the POD catalogue during the initial digital-first launch. Do not delete existing physical product records solely because they are not publicly displayed.

## India-First Market

Initial audiences:

- Small businesses
- Freelancers and agencies
- Creators
- Local businesses
- Startups
- Professionals
- Job seekers

Benefits include INR pricing, WhatsApp support, UPI familiarity, localized products, familiar problems, and easier service delivery. The first goal is to prove acquisition and profitable conversion, not worldwide scale.

## Customer Experience

The eventual account area should support:

- Orders
- Digital purchases
- Secure downloads
- Service enquiries or orders
- Profile management

Keep the initial experience simple. Free tools should not require accounts unless a real use case requires saved history or delivery.

## SEO and Analytics

SEO should be useful rather than mass-produced. Prioritize tool and template pages that genuinely help users, such as invoice generator, profit calculator, pricing calculator, invoice template, business tracker, freelancer template, and small-business spreadsheet pages.

Measure:

- Tool visits and completion
- Template views and purchases
- Downloads
- Service enquiries
- WhatsApp clicks
- Checkout starts
- Conversion rates
- Traffic source
- Product and service performance
- Refunds, support cost, delivery time, and repeat purchases

Use analytics to discover what actually makes money rather than assuming every idea will succeed.

## Payment and Commerce Direction

### India

Use Razorpay for India payments. The existing Razorpay flow is tied to physical `Order` records and Printful fulfillment. Do not force digital downloads into that flow.

The intended future digital flow is:

```text
Template -> DigitalOrder -> Razorpay order -> server verification -> DownloadGrant
```

The backend must verify order ID, payment ID, signature, amount, currency, and captured status before granting a download. Paid files must use secure, non-permanent download access.

For services, begin with an enquiry, manual proposal, and 30% to 50% advance payment through an approved Razorpay flow or payment link. Full service project management is not an initial requirement.

### Global

Do not activate the existing Stripe path blindly. It is tied to the physical order architecture and is not the active frontend production flow. Evaluate Stripe, Lemon Squeezy, Paddle, or Gumroad based on Indian availability, payouts, fees, tax handling, currency support, and merchant-of-record responsibilities.

Global digital products should be considered before global services.

## Tax and Compliance Guardrail

Do not market LeTrusto as a GST-free business. Digital products, website development, automation, affiliate commissions, advertising, and other income can have different tax treatment.

Use neutral wording:

> Taxes are handled according to applicable law.

Before regular paid sales or international expansion, confirm with an Indian CA:

- Whether GST registration is required for each activity
- Applicable turnover thresholds
- Interstate implications
- Export-of-services treatment
- LUT and export documentation
- Invoice requirements
- Payment settlement reconciliation
- Digital product, service, affiliate, and advertising treatment

Application configuration must never be treated as proof of legal tax exemption.

## Architecture Rules

- This is an evolution of the existing project, not a new project.
- Preserve physical commerce and Printful infrastructure.
- Do not make physical commerce the primary public identity during the initial launch.
- Do not force digital products into physical product, inventory, shipping, or fulfillment models.
- Create additive Alembic migrations; never modify existing migrations.
- Reuse authentication, admin authorization, email, analytics, SEO, support, articles, and API patterns.
- Keep credentials server-side and never expose payment or supplier secrets.
- Do not add payment providers automatically.
- Do not add large feature areas without evidence of demand.
- Do not use fake discounts, fake scarcity, misleading claims, or unlimited low-price promises.

## Likely New Technical Layer

When paid digital products are validated, add a separate digital domain beside physical commerce:

- Digital tools and calculator metadata
- Digital templates with versions, previews, licenses, and secure file delivery
- Digital orders and payment attempts
- Download grants with expiry, revocation, and download limits
- Service leads and enquiry status
- Optional tool usage and download analytics

Use new database tables and migrations. Keep `Product`, `ProductVariant`, `Cart`, `Order`, `PrintfulShippingRate`, fulfillment, and supplier models focused on physical commerce.

Simple calculators can initially run client-side without database persistence.

## Implementation Sequence

### Phase 1: Reposition

- Update homepage and navigation to Tools, Templates, and Services.
- Move physical/POD commerce to a secondary or hidden public position.
- Add service enquiry and WhatsApp calls to action.
- Preserve existing backend records and integrations.

### Phase 2: Validate tools

- Launch a small number of genuinely useful free tools.
- Add related content and natural template/service links.
- Track usage and search performance.

### Phase 3: Validate services

- Publish clearly scoped entry, standard, and custom service offers.
- Add portfolio examples, delivery times, exclusions, revision limits, and enquiry handling.
- Use manual proposals and advance payments initially.

### Phase 4: Validate digital products

- Launch a small number of high-value bundles.
- Add previews, licensing, secure delivery, refunds, and India payment handling.
- Build separate digital payment/order models only when sales justify them.

### Phase 5: Expand carefully

- Improve products based on real usage and sales.
- Consider global digital products.
- Consider premium tools, SaaS, memberships, affiliates, Minku & Dinku, and selected physical products only after validation.

## Product Evaluation Checklist

Before implementing a new product or feature, evaluate:

1. Demand
2. Competition
3. Differentiation
4. Development effort
5. Maintenance
6. Profitability
7. Customer acquisition potential
8. Cross-sell potential
9. Legal and compliance implications
10. Fit with LeTrusto

Individual tools, categories, products, and prices are not permanently locked. The digital-first direction, Tools, Templates, Services, India-first strategy, affordable entry offers, practical value, productized services, useful SEO, Minku & Dinku separation, and physical-products-secondary strategy are the current strategic constraints.

## Core Identity

> LeTrusto is an India-first digital business platform offering practical free tools, ready-to-use digital products, and affordable digital services, with a long-term path toward global digital products, premium tools, recurring revenue, affiliate opportunities, and selected physical products.
