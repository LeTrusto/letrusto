# First-Market Experiments

## Purpose

Use the existing tools, digital products, and services to learn which audience and workflow show real commercial intent. These are comparative experiments, not forecasts. Do not treat an event, click, or purchase as evidence of product-market fit until real users generate enough consented data to compare the same periods and traffic sources.

## Measurement rules

- Measure consented events only; analytics must remain optional and privacy-safe.
- Compare experiments by the same time window, traffic source where available, tool views, tool completions, product clicks, product views, authentication starts, checkout starts, verified purchases, downloads, and service enquiries.
- Use product slugs and tool names as identifiers. Do not collect email addresses, payment IDs, form contents, or secrets in analytics.
- A purchase counts only after backend payment verification and entitlement creation. A service enquiry is a lead, not a purchase.
- Record the observation period, traffic source, event counts, and notable qualitative feedback before making a decision.

## Segment A: Small Businesses

### Experiment C: Financial and pricing workflow

- **Target audience:** Small-business owners and operators reviewing costs, margins, prices, break-even points, or invoices.
- **Entry points:** Profit Margin Calculator, Pricing Calculator, Break-Even Calculator, Expense Calculator, and Invoice Generator.
- **Intended product:** Small Business Finance & Pricing Toolkit at INR 499.
- **Primary CTA:** Review the toolkit after a completed calculator result.
- **Primary conversion event:** `digital_product_purchase_completed` for the finance toolkit.
- **Supporting events:** `tool_view`, `tool_complete`, `digital_product_cta_clicked`, `digital_product_view`, `digital_product_auth_required`, `digital_product_checkout_started`, `digital_product_payment_failed`, `digital_product_download_completed`.
- **Meaningful interest signal:** Compared with the other segment and other tools, a repeatable pattern of completed calculations followed by finance-toolkit product views, authenticated checkout starts, verified purchases, or downloads.
- **Decision after measurement:** Keep the strongest entry tools and CTA relationships, improve the weakest step in the funnel, or pause a low-intent relationship. Do not add a new product based on clicks alone.

## Segment B: Freelancers and Agencies

### Experiment A: Rate to project pricing

- **Target audience:** Freelancers, consultants, and small agencies deciding hourly rates, day rates, and project prices.
- **Entry points:** Freelancer Rate Calculator and Pricing Calculator.
- **Intended product:** Freelancer Rate & Project Pricing Toolkit.
- **Primary CTA:** Move from the rate or pricing result to the rate-and-project-pricing product page.
- **Primary conversion event:** `digital_product_purchase_completed` for the rate-and-project-pricing toolkit.
- **Supporting events:** `tool_view`, `tool_complete`, `digital_product_cta_clicked`, `digital_product_view`, `digital_product_auth_required`, `digital_product_checkout_started`, `digital_product_payment_failed`, `digital_product_download_completed`.
- **Meaningful interest signal:** A stronger rate/pricing completion-to-product-view and checkout-start pattern than unrelated tool paths during the same observation period.
- **Decision after measurement:** Keep or refine the rate/pricing relationship, improve the point where users leave, or redirect attention to the client-work product if post-pricing intent is stronger there.

### Experiment B: Invoice to client-work management

- **Target audience:** Freelancers and agencies who already create invoices and need visibility across scope, delivery, follow-up, and project profitability.
- **Entry point:** Invoice Generator, with supporting links from Freelancer Rate Calculator and Pricing Calculator.
- **Intended product:** Freelancer & Agency Client-Work Workbook at INR 599.
- **Primary CTA:** Use the workbook after generating an invoice or reviewing client-work requirements.
- **Primary conversion event:** `digital_product_purchase_completed` for the client-work workbook.
- **Supporting events:** `tool_view`, `tool_complete`, `digital_product_cta_clicked`, `digital_product_view`, `digital_product_auth_required`, `digital_product_checkout_started`, `digital_product_payment_failed`, `digital_product_download_completed`.
- **Meaningful interest signal:** Repeatable invoice completion followed by client-work product views, checkout starts, verified purchases, or downloads, compared with Experiment A.
- **Decision after measurement:** Strengthen invoice-to-workbook links if the downstream intent is clear, clarify product differentiation if users view both products, or keep the relationship as a secondary path.

### Experiment D: Tools and products to services

- **Target audience:** Small businesses, freelancers, and agencies whose needs extend beyond a self-serve calculation or workbook.
- **Entry points:** Relevant tool pages, digital-product pages, the services catalog, and Website Setup service detail.
- **Intended offer:** The most relevant productized service, with Website Setup as the flagship route when the need is a website.
- **Primary CTA:** Request a quote only when the page context indicates a genuine service need.
- **Primary conversion event:** `service_enquiry_submitted`.
- **Supporting events:** `get_quote_clicked`, `quote_form_started`, `service_detail_view`, `service_enquiry_failed`, `tool_complete`, `digital_product_view`, and `digital_product_cta_clicked` where applicable.
- **Meaningful interest signal:** Service detail views and quote starts that result in completed enquiries, compared by entry page and segment without treating form starts as completed leads.
- **Decision after measurement:** Improve the highest-intent service path, clarify scope on pages with repeated failed or abandoned enquiries, or keep the service CTA limited where self-serve tools better fit the need.

## Questions to answer

1. Which segment engages most deeply from tool view through verified purchase or service enquiry?
2. Which tools attract the strongest completion and downstream intent?
3. Which product receives the most qualified interest?
4. Which product converts after authentication and verified payment?
5. Which tools produce service enquiries rather than only page views?
6. Which segment merits future investment after the current catalog has been measured?

No benchmark or success claim is defined in advance. The next decision should follow observed comparative data, customer feedback, operational capacity, and the safety of the existing payment and support flows.
