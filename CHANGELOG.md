# Changelog

All notable changes to LeTrusto are documented in this file.

## v0.3.0 - SEO, Analytics & Affiliate Foundation

Date: 2026-08-04

### Added

- Added Next.js metadata routes for `robots.txt` and `sitemap.xml` generation.
- Added GA4 integration with `next/script`, a reusable analytics utility, and App Router route-change page-view tracking.
- Added project-level setup history documentation in `docs/PROJECT_SETUP_HISTORY.md`.

### Changed

- Updated the root app layout to include structured metadata, schema markup, and production-only analytics loading.
- Extended affiliate readiness with disclosure UI, retailer buy-link support, and backend click tracking.
- Consolidated deployment and operational setup details in the root README.

### Infrastructure

- Frontend remains configured for Vercel builds through `vercel.json`.
- Backend remains configured for Railway Docker deployment and PostgreSQL-backed migrations.
- Google Search Console setup is documented as completed with DNS verification and sitemap submission.
- Amazon Associates registration is documented with store ID `letrusto-21` and completed tax onboarding.