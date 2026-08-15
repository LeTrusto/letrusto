# LeTrusto Commerce — Development Roadmap

## Phase 1: Brand + Design System + Storefront Shell (current)

- [x] Repository audit
- [x] Branch & legacy preservation
- [x] Brand identity & design system docs
- [ ] New design tokens (globals.css)
- [ ] Commerce navbar, footer, mobile nav
- [ ] Commerce homepage (13 sections)
- [ ] Mock product data
- [ ] Product card component
- [ ] Product detail page
- [ ] Shop/category page
- [ ] Cart (local state)
- [ ] SEO updates
- [ ] Build/lint/test pass

## Phase 2: Commerce Backend Foundation

- Commerce database models (suppliers, inventory, orders, shipments, payments)
- Alembic migrations
- Supplier adapter abstraction
- Product ingestion pipeline (import → normalize → review → publish)
- Pricing/economics service
- Product scoring model
- Admin product approval workflow

## Phase 3: Supplier Integration

- First supplier adapter (CJ or Indian supplier)
- Automated product import
- Inventory sync
- Order placement
- Tracking integration

## Phase 4: Checkout & Payments

- Real checkout flow
- Payment gateway integration (Razorpay / similar)
- Order creation
- Order status tracking
- Email notifications

## Phase 5: Creator & Marketing

- Creator referral links
- Commission tracking
- Coupon system
- Campaign/UTM tracking
- WhatsApp integration

## Phase 6: Analytics & Optimization

- Product analytics dashboard
- Marketing attribution
- Conversion tracking
- Product scoring with real data

## Phase 7: Scale & Brand

- Private label preparation
- Exclusive products
- Brand packaging
- Customer retention programs
