<p align="center"><img src="https://raw.githubusercontent.com/Treevu-ai/cli-market-world/main/social-preview.svg" alt="CLI Market" width="600"/></p>

<p align="center">
  <img src="https://img.shields.io/badge/retailers-30-brightgreen" alt="30 retailers">
  <img src="https://img.shields.io/badge/platforms-3-blue" alt="3 platforms">
  <img src="https://img.shields.io/badge/countries-7-orange" alt="7 countries">
  <img src="https://img.shields.io/badge/prices-13k-3cffd0" alt="13,000 prices">
  <img src="https://img.shields.io/badge/MCP%20tools-36-00d75f" alt="36 MCP tools">
  <img src="https://img.shields.io/badge/payments-5-ffbd2e" alt="5 payments">
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
<p align="center"><b>Commerce infrastructure for AI agents.</b><br>30 retailers. 7 countries. 3 platforms. 36 MCP tools. 5 payment methods.<br>13,000+ real prices, refreshed every 8 hours.<br>One <code>pip install</code>. One API. Zero scraping.</p>

---

## What is CLI Market?

AI agents can't comparison-shop in physical retail. Every retailer requires separate auth, separate search logic, no unified cart. Agents fail before the first query.

**CLI Market fixes this.** One `pip install`. One API call across 30 verified retailers. One JSON schema.

- **Search** any product across 30 verified retailers in 7 countries
- **Compare** prices cross-border — PEN, ARS, BRL, MXN, COP, CLP, EUR, USD
- **Basket** — compare your full shopping cart across retailers, find the cheapest
- **Inflation** — track real price changes from supermarket shelves, updated every 8 hours
- **Buy** — checkout with Yape, Plin, Wise, PayPal, or Lemon
- **Build** — data moat with thousands of verified prices, historical snapshots, SKU normalization

> Stripe turned payments into APIs. We turn commerce into APIs.

<p align="center"><a href="https://cli-market.dev"><b>cli-market.dev</b></a> · <a href="https://cli-market-production.up.railway.app/docs"><b>API docs</b></a> · <a href="https://cli-market-production.up.railway.app/dashboard"><b>Dashboard</b></a></p>

---

## Quick start

```bash
pip install cli-market
export MARKET_API_URL=https://cli-market-production.up.railway.app
market login
market search "leche" --country PE
market compare "aceite"
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

| Method | Countries | Endpoint |
|---|---|---|
| **Yape / Plin** | Peru | `POST /checkout/yape` |
| **Wise** | Global | `POST /checkout/wise` |
| **PayPal** | Global | `POST /checkout/paypal` |
| **Lemon** | Argentina | `POST /checkout/lemon` |
| **Stripe** | Global | `POST /billing/checkout` |

---

## Pricing

| | Free | Pro | Enterprise |
|---|---|---|---|
| **Price** | $0 | $49/mo | Custom |
| **Requests** | 1,000/day | 10,000/day | Unlimited |
| **API keys** | 1 (read) | 10 (read+write) | Unlimited |
| **Checkout** | — | ✅ | ✅ |
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
│   ├── wise_payments.py     → Wise + Pay Me
│   ├── paypal_payments.py   → PayPal checkout
│   ├── lemon_payments.py    → Lemon cash (Argentina)
│   ├── sunat_invoicing.py   → SUNAT + PSE
│   └── minimax.py           → TTS, image, video generation
└── landing/                 → Next.js (Vercel, Wise design)
```

---

**SINAPSIS INNOVADORA S.A.C.** — RUC 20613045563 — Lima, Peru  
Founder: **Antonio Cuba**  
[cli-market.dev](https://cli-market.dev) · [GitHub](https://github.com/Treevu-ai/cli-market-world)
