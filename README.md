mcp-name: io.github.Treevu-ai/cli-market-world

<p align="center"><img src="https://raw.githubusercontent.com/Treevu-ai/cli-market-world/main/social-preview.svg" alt="CLI Market" width="600"/></p>

<p align="center">
  <img src="https://img.shields.io/badge/retailers-60-brightgreen" alt="60 retailers">
  <img src="https://img.shields.io/badge/platforms-3-blue" alt="3 platforms">
  <img src="https://img.shields.io/badge/countries-8-orange" alt="8 countries">
  <img src="https://img.shields.io/badge/prices-43k-3cffd0" alt="43,000 prices">
  <img src="https://img.shields.io/badge/MCP%20tools-36-00d75f" alt="36 MCP tools">
  <img src="https://img.shields.io/badge/payments-PayPal_email-ffbd2e" alt="PayPal email billing">
  <img src="https://img.shields.io/badge/dashboard-live-3cffd0" alt="dashboard">
  <img src="https://img.shields.io/badge/python-3.10+-306998" alt="py">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" alt="MIT">
</p>

<p align="center">
  <a href="https://pypi.org/project/cli-market/"><img src="https://img.shields.io/pypi/v/cli-market?color=00FF88" alt="PyPI version"></a>
  <a href="https://pypi.org/project/cli-market/"><img src="https://img.shields.io/pypi/dm/cli-market?color=00FF88" alt="PyPI downloads"></a>
  <a href="https://github.com/Treevu-ai/cli-market-world"><img src="https://img.shields.io/github/stars/Treevu-ai/cli-market-world?style=social" alt="GitHub stars"></a>
</p>

<h1 align="center">CLI Market</h1>
<p align="center"><b>Commerce infrastructure for AI agents.</b><br>60 retailers (30 verified). 8 countries. 3 platforms. 36 MCP tools. PayPal + QR (Yape/Plin).<br>43,000+ verified shelf prices, normalized per kg/L, refreshed every 8 hours.<br>One <code>pip install</code>. One API. Zero scraping.</p>

---

## What is CLI Market?

AI agents can't comparison-shop in physical retail. Every retailer requires separate auth, separate search logic, no unified cart. Agents fail before the first query.

**CLI Market fixes this.** One `pip install`. One API call across 60 retailers (30 verified). One JSON schema.

- **Search** any product across 30 verified retailers in 8 countries
- **Compare** prices cross-border — PEN, ARS, BRL, MXN, COP, CLP, EUR, USD — normalized per kg/L where parseable
- **Basket** — compare your full shopping cart across retailers (e.g. Carrefour vs Jumbo vs Vea in AR)
- **Inflation** — track real price changes from supermarket shelves, updated every 8 hours
- **Buy** — checkout with PayPal or QR (Yape/Plin)
- **Build** — data moat with quality-filtered spreads, canasta matching, and live dashboard

> Stripe turned payments into APIs. We turn commerce into APIs.

Posicionamiento en español (API / landing / ventas): [`docs/api-positioning-es.md`](docs/api-positioning-es.md)

<p align="center"><a href="https://cli-market.dev"><b>cli-market.dev</b></a> · <a href="https://cli-market-production.up.railway.app/docs"><b>API docs</b></a> · <a href="https://cli-market-production.up.railway.app/dashboard"><b>Dashboard</b></a></p>

---

## Quick start

```bash
pip install cli-market
market hello          # post-install: stats + next steps
export MARKET_API_URL=https://cli-market-production.up.railway.app
market login
market search "leche" --country PE
market compare "aceite de girasol 900ml" --country AR
market basket "arroz:1 aceite:1 leche:1" --country AR
market checkout --payment yape
market ask "compra arroz al mejor precio"
```

---

## Multi-platform coverage

| Platform | Count | Examples |
|---|---|---|
| **VTEX** | 38 | Wong, Metro, Plaza Vea, Carrefour, Jumbo, Motorola, Electrolux, Whirlpool, Samsung, HEB, Chedraui, Easy, Promart, Coppel, Ripley, C&A, Hering |
| **Shopify** | 15 | Adidas, Gymshark, Allbirds, Alo Yoga, Glossier, Fenty Beauty, Kylie Cosmetics, ColourPop, Brooklinen, Casper, On Running |
| **Magento** | 7 | Falabella PE/CL/CO, Paris CL, Ripley CL, Liverpool MX, El Palacio MX |

---

## 36 MCP tools

`market_login` `market_lines` `market_search` `market_compare` `market_add` `market_cart` `market_cart_update` `market_cart_remove` `market_checkout` `market_orders` `market_reorder` `market_ask` `market_basket` `market_inflation` `market_categories` `market_barcode` `market_enrich` `market_stores` `market_countries` `market_ticket` `market_voice` `market_price_history` `market_stats` `market_alerts` `market_whoami` `market_preferences` `market_subscription` `market_export` `market_trending` `market_scan` `market_stock` `market_intel` `market_notify` `market_brands` `market_favorites` `market_delivery`

---

## Payments

**Pro plan (default):** request via email → PayPal Hosted Button → manual activation within 24 h.  
See [ops/E2E_CLIENT_JOURNEY.md](ops/E2E_CLIENT_JOURNEY.md) and [ops/BILLING_MANUAL.md](ops/BILLING_MANUAL.md).

| Method | Use | Type |
|---|---|---|
| **PayPal Hosted Button** | Pro subscription ($49/mo) | Email + link (manual activate) |
| **PayPal REST** | Optional automation | Webhooks (future) |
| **Yape / Plin** | Checkout orders (Pro tier) | QR code |

### Upgrade to Pro

```bash
market login
market upgrade --email you@example.com
# Pay via link in email → reply with CLI username → ops activates Pro
```

Ops after payment confirmed:

```bash
python3 ops/activate_pro.py username --request-id PRO-XXXXXXXX
```

---

## Pricing

| | Free | Pro | Enterprise |
|---|---|---|---|
| **Price** | $0 | $49/mo | Custom |
| **Requests** | 1,000/day | 10,000/day | Unlimited |
| **API keys** | 1 (read) | 10 (read+write) | Unlimited |
| **Checkout** | — | ✅ (after email activation) | ✅ |
| **Data export** | — | JSON/CSV | ✅ |
| **Support** | Community | Email | 24/7 + onboarding |

---

## Architecture

```
cli-market (PyPI)
├── market_cli.py            → CLI (rich tables, natural language)
├── market_server.py         → FastAPI backend (54 endpoints)
├── market_mcp.py            → MCP server (36 tools)
├── market_core.py           → Shared core (SQLite/PG, connectors)
├── collect_prices.py        → Price collector (8h daemon, 228 queries)
├── market_stores.py         → 60 retailer definitions
├── market_connectors/
│   ├── vtex.py              → VTEX public API (38 stores)
│   ├── shopify.py           → Shopify API (15 stores)
│   ├── magento.py           → Magento REST API (7 stores)
│   ├── paypal_payments.py   → PayPal checkout
│   ├── sunat_invoicing.py   → SUNAT + PSE
│   └── minimax.py           → TTS, image, video generation
└── landing/                 → Next.js (Cloudflare Pages)
```

---

**SINAPSIS INNOVADORA S.A.C.** — RUC 20613045563 — Lima, Peru  
Founder: **Antonio Cuba**  
[cli-market.dev](https://cli-market.dev) · [GitHub](https://github.com/Treevu-ai/cli-market-world)
