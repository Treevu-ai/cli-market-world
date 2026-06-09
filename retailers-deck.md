# CLI Market — Retailer Partnership Deck

> **1-page overview for outreach to Shopify, Magento, and VTEX retailers.**

---

## Problem

AI agents can't shop in physical retail. They need structured product data — prices, stock, SKUs — in a format they can reason about. Most retailers have this data but don't expose it to agents.

## Solution

**CLI Market** is commerce infrastructure for AI agents. We index your product catalog and make it discoverable by autonomous agents. No scraping. No middleware. Just your API + our platform.

## By the numbers

| Metric | Value |
|---|---|
| Retailers live | 38 verified active (68 in catalog) |
| Prices indexed | 52,000+ |
| Products tracked | 8,000+ |
| Countries | 8 (PE, AR, BR, MX, CO, CL, US, +) |
| MCP tools | 22 default / 43 full (search, compare, basket, checkout, inflation, enrichment…) |
| Refresh cycle | Every 4 hours |
| License | MIT (open source) |

## What you get

| Benefit | Detail |
|---|---|
| **Agent-driven traffic** | Your products appear when AI agents search, compare, and purchase |
| **Competitive intelligence** | Real-time price benchmarking against 27 retailers |
| **Zero integration cost** | Shopify: 30-second token generation. Magento: read-only integration |
| **No lock-in** | Open source. Delete your token anytime. We stop indexing |

## How it works

1. **You**: Generate a read-only API token (Shopify Storefront token, Magento integration, or VTEX public endpoint)
2. **Us**: Add your store config to our collector (1 line of code)
3. **Automated**: Every 4 hours, our collector indexes your catalog into PostgreSQL
4. **Agents**: AI agents discover your products via MCP tools, CLI, or REST API

## Integration guides

### Shopify (15 brands)
```
Shopify Admin → Settings → Apps and sales channels → Develop apps
→ Create an app → Configure Admin API scopes → read_products
→ Install app → Copy Admin API access token
```
Send us the token + your `.myshopify.com` domain.

### Magento / Adobe Commerce (7 retailers)
```
System → Integrations → Add New Integration
→ Name: "CLI Market" → Your Password → API Permissions: Catalog (read)
→ Activate → Copy Access Token
```
Send us the token + your store URL.

### VTEX (public, 27 live)
No credentials needed. VTEX exposes a public catalog API. If your store is on VTEX, send us your domain and we'll verify if your API is reachable.

## Who's already indexed (examples)

| Retailer | Country | Platform | Line |
|---|---|---|---|
| Wong | PE | VTEX | Supermarket |
| Metro | PE | VTEX | Supermarket |
| Carrefour | AR/BR | VTEX | Supermarket |
| Chedraui | MX | VTEX | Supermarket |
| Motorola | AR/BR/MX/CL | VTEX | Electronics |
| Samsung | BR/MX | VTEX | Electronics |
| Electrolux | AR/MX/CL | VTEX | Electronics |
| Whirlpool | AR/IT/FR | VTEX | Electronics |
| Plaza Vea | PE | VTEX | Supermarket |
| HEB | MX | VTEX | Supermarket |

## Contact

**Email:** hello@cli-market.dev  
**Website:** https://cli-market.dev  
**Docs:** https://cli-market.dev/docs
**Dashboard:** https://cli-market-production.up.railway.app/dashboard

---

*CLI Market · MIT License · Built by SINAPSIS INNOVADORA S.A.C. · Lima, Peru*
