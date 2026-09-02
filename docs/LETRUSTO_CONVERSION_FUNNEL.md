# LeTrusto Conversion Funnel

Visitor -> Tools -> Digital Products -> Services

## Conversion definitions

- Primary conversion: `service_enquiry_submitted`, a service enquiry accepted by the support endpoint.
- Secondary engagement: `tool_complete`, a meaningful successful interaction with a tool.
- Digital product lead: `digital_product_cta_clicked`, a meaningful product-detail CTA interaction. Secure checkout and purchase are not active, so no `purchase` event is emitted.

## Analytics events

All events require affirmative analytics consent, run only in production, and use static identifiers or interaction types. User-entered values are never event parameters.

| Event | Safe parameters |
| --- | --- |
| `tool_view` | `tool_name` |
| `tool_complete` | `tool_name` |
| `digital_products_view` | `page` |
| `digital_product_view` | `product_name`, `product_slug` |
| `digital_product_cta_clicked` | `product_name`, `product_slug`, `interaction` |
| `services_view` | `page` |
| `service_detail_view` | `service_name`, `service_slug` |
| `get_quote_clicked` | `service_name`, `service_slug`, `location` |
| `quote_form_started` | `service_name`, `service_slug` |
| `service_enquiry_submitted` | `service_name`, `service_slug` |
| `service_enquiry_failed` | `service_name`, `service_slug`, `failure_type` |