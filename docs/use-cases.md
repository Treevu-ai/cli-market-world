# CLI Market — Use Cases

Three profiles. One API. Zero scraping.

---

## 1. AI Agent Builder

> _You build AI agents. They need to buy things._

**Problem.** Your agent can search the web and call APIs, but it can't buy a physical product. Every retailer means separate auth, separate search logic, no shared cart. Your agent fails before the first query.

**Solution.** 4 MCP calls, end to end:

```
market_search   "leche deslactosada" --country PE
  -> 12 products across 4 retailers, prices normalized per liter

market_compare  "aceite de girasol 900ml" --country AR
  -> Carrefour: ARS 1,200  |  Jumbo: ARS 1,350  |  Vea: ARS 1,180

market_basket   "arroz:1 aceite:1 leche:2" --country AR
  -> Best total: Vea ARS 4,230 (saves 8% vs Carrefour)

market_checkout --payment yape
  -> QR code ready. User scans and pays.
```

**Tech stack.** MCP protocol. Claude, Cursor, Copilot, or any MCP client. 43 tools available.

**Pricing.** Free tier: 1,000 requests/day. Pro: 10,000 + checkout. No credit card to start.

---

## 2. Data Scientist / Analyst

> _You need real shelf prices. Not scraped once. Normalized. Comparable._

**Problem.** Price tracking is a mess. You scrape 3 retailers and spend 80% of your time cleaning data: "1L", "1000 ml", "litro", "lt", "1 lt" are the same. Across countries it's worse — PEN, ARS, BRL, MXN all with different inflation rates.

**Solution.** Query and go:

```python
import requests

# Inflation index for cooking oil in Argentina, last 30 days
r = requests.get(
    "https://cli-market-production.up.railway.app/v1/prices",
    params={"category": "aceites", "country": "AR", "days": 30},
    headers={"Authorization": "Bearer YOUR_API_KEY"}
)

# Every price comes with:
# - canonical product ID (prod_primor_aceites_0.9l)
# - price per kg/L (unit_price)
# - confidence score
# - store and timestamp
```

**What you get.**
- 45,000+ verified prices, refreshed every 4 hours
- Normalized by kg/L — compare 900ml vs 1L vs 6x625ml directly
- P25/P50/P75 percentiles — median, not mean, for outlier-resistant analysis
- 8 currencies, 8 countries, 66 retailers
- CSV export up to 10K rows (Starter), unlimited (Pro+)

**Use cases.** Inflation tracking. Market basket cost analysis. Retailer price positioning. Brand penetration studies.

---

## 3. Retailer

> _Your products are on VTEX. AI agents should find them._

**Problem.** Your catalog is online, but AI agents can't navigate VTEX. No MCP tool knows your store exists. Every AI agent that wants to buy something skips you because there's no unified commerce API.

**Solution.** Get listed in CLI Market.

Once onboarded, your products enter the Semantic Refinery:
- Every SKU gets a canonical `prod_` ID
- Your prices appear in `market_search`, `market_compare`, `market_basket`
- AI agents can recommend and purchase your products
- You get a retailer dashboard with coverage stats

**Onboarding.** 24 hours. We need your VTEX store key. That's it.

Email: hello@cli-market.dev

**Already active.** 36 verified retailers across 8 countries — Tottus, Plaza Vea, Wong, Metro, Carrefour, Jumbo, Vea, and more.

---

## Why CLI Market over alternatives?

| Capability | CLI Market | DIY Scraping | Google Shopping |
|---|---|---|---|
| Retailers covered | 66 (36 active) | As many as you code | Varies |
| Refresh frequency | Every 4 hours | Manual or cron | Unknown |
| Normalized per kg/L | Yes | You code it | No |
| MCP tools for AI agents | 43 | No | No |
| Cross-retailer basket | Yes | No | No |
| Checkout from agent | Yes | No | No |
| Price per query | From $0/mo | Your infra cost | Free but limited |

---

[Get started](https://cli-market.dev) · [API docs](https://cli-market-production.up.railway.app/docs) · [Dashboard](https://cli-market-production.up.railway.app/dashboard)
