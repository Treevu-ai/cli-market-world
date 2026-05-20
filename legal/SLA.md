# CLI Market — Service Level Agreement (SLA)

**Effective date:** May 20, 2026
**Applies to:** Paid subscription tiers

---

## 1. Uptime Commitment

CLI Market commits to 99.5% API availability, measured monthly ("Uptime").

**Excluded from Uptime calculation:**
- Scheduled maintenance (announced 48 hours in advance)
- Force majeure events
- VTEX retailer API outages beyond CLI Market's control
- Customer-side issues (network, credentials, client code)

## 2. Data Freshness

CLI Market commits to:
- **Pricing data:** refreshed every 24 hours (± 4 hours)
- **SKU index:** updated weekly
- **Retailer index:** updated monthly

## 3. Support Response Times

| Severity | Definition | Response | Resolution |
|----------|-----------|----------|------------|
| Critical | Service unavailable | 1 hour | 4 hours |
| High | Major feature broken | 4 hours | 24 hours |
| Medium | Minor feature degraded | 1 business day | 5 business days |
| Low | Cosmetic or documentation | 3 business days | Next release |

Support available via: hello@cli-market.dev (business hours, UTC-5)

## 4. Service Credits

If CLI Market fails to meet the Uptime commitment in a calendar month, you are entitled to:

| Uptime | Credit |
|--------|--------|
| 99.0% - 99.49% | 10% of monthly fee |
| 95.0% - 98.99% | 25% of monthly fee |
| Below 95.0% | 50% of monthly fee |

Credits are applied to the following month's invoice. To claim, email billing@cli-market.dev within 30 days of the incident.

Credits are your sole remedy for Uptime failures.

## 5. API Deprecation

CLI Market will provide 90 days notice before deprecating any API endpoint, MCP tool, or data schema. During the notice period, the deprecated feature remains fully functional.

## 6. Data Export on Termination

On plan cancellation or termination, you may export your data in JSON or CSV format for 30 days at no additional charge.

## 7. Limitations

This SLA does not apply to:
- Free or trial tiers (best-effort only)
- Beta or pre-release features
- Third-party integrations not maintained by CLI Market

---

**Last updated:** May 20, 2026
