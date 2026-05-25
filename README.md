<p align="center"><img src="https://raw.githubusercontent.com/Treevu-ai/cli-market-world/main/social-preview.svg" alt="CLI Market" width="600"/></p>

<p align="center">
  <img src="https://img.shields.io/badge/retailers-30-brightgreen" alt="30 retailers">
  <img src="https://img.shields.io/badge/lines-6-blue" alt="6 lines">
  <img src="https://img.shields.io/badge/countries-8-orange" alt="8 countries">
  <img src="https://img.shields.io/badge/MCP%20tools-30-00d75f" alt="30 MCP tools">
  <img src="https://img.shields.io/badge/dashboard-live-3cffd0" alt="dashboard">
  <img src="https://img.shields.io/badge/python-3.10+-306998" alt="py">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" alt="MIT">
  <img src="https://img.shields.io/badge/build-passing-brightgreen" alt="build">
  <img src="https://img.shields.io/badge/CI-vercel-black" alt="Vercel">
</p>

<p align="center">
  <a href="https://pypi.org/project/cli-market/"><img src="https://img.shields.io/pypi/v/cli-market?color=00FF88" alt="PyPI version"></a>
  <a href="https://pypi.org/project/cli-market/"><img src="https://img.shields.io/pypi/dm/cli-market?color=00FF88" alt="PyPI downloads"></a>
  <a href="https://github.com/Treevu-ai/cli-market-world"><img src="https://img.shields.io/github/stars/Treevu-ai/cli-market-world?style=social" alt="GitHub stars"></a>
  <a href="https://www.producthunt.com/products/cli-market"><img src="https://api.producthunt.com/widgets/embed-image/v1/featured.svg?post_id=1150344&amp;theme=neutral" alt="ProductHunt featured" width="125" height="27"></a>
</p>

<!-- mcp-name: io.github.Treevu-ai/cli-market -->

<h1 align="center">CLI Market</h1>
<p align="center"><b>Your AI agent can search, compare, and buy across 30 retailers in 8 countries.</b><br>One <code>pip install</code>. One API. Zero scraping.</p>

---

## What is CLI Market?

**The problem:** AI agents can't comparison-shop. Carrefour, Wong, Motorola, HEB — 30 retailers across Latin America and Europe share the same e-commerce engine (VTEX). But every retailer requires separate auth, separate search logic, no unified cart. Agents fail before the first query.

**CLI Market fixes this.** One `pip install`. One API call across all 30 retailers. One JSON schema.

- **Search** any product across 30 verified retailers in 8 countries
- **Compare** prices cross-border — ARS, BRL, MXN, PEN, COP, CLP, EUR
- **Basket** — compare your full shopping cart across retailers, find the cheapest
- **Inflation** — track real price changes from supermarket shelves, updated every 4 hours
- **Buy** — autonomous checkout with human approval (30 MCP tools)
- **Build** — data moat with thousands of verified prices, historical snapshots, SKU normalization

> Stripe turned payments into APIs. We turn commerce into APIs.

<p align="center"><a href="https://cli-market.dev"><b>cli-market.dev</b></a></p>

---

## Quick start

```bash
# 1. Install
pip install cli-market

# 2. Point to our cloud API (or run locally: python market_server.py)
export MARKET_API_URL=https://cli-market-api.onrender.com

# 3. Authenticate
market login

# 4. Search
market search "leche" --country AR       # Argentina
market search "leite" --store carrefour_br  # Brazil

# 5. Compare prices
market compare "aceite"

# 6. Add to cart and checkout
market add 3 --qty 2
market cart
market checkout --payment yape

# 7. Agent mode — natural language
market ask "compra arroz al mejor precio"
market ask "compara canasta: leche:2 arroz:1"

# 8. Machine-readable output
market --json
```

---

## What you get

| You | Your AI agent |
|-----|---------------|
| `pip install cli-market` | 30 MCP tools |
| `market search "milk"` | REST API + JSON native |
| Rich terminal tables | Cross-border price intelligence |
| Spanish / English | Inflation tracking |
| Cart, checkout, reorder | Autonomous workflows |

### 30 MCP tools

`market_login` `market_lines` `market_search` `market_compare` `market_add` `market_cart` `market_cart_update` `market_cart_remove` `market_checkout` `market_orders` `market_reorder` `market_ask` `market_basket` `market_inflation` `market_categories` `market_barcode` `market_enrich` `market_stores` `market_countries` `market_ticket` `market_voice` `market_price_history` `market_stats` `market_alerts` `market_whoami` `market_preferences` `market_subscription` `market_export` `market_trending` `market_scan`

Compatible with **DeepSeek TUI, Claude, Cursor, Windsurf, Continue, and any MCP client.** [Registered on the MCP Registry.](https://registry.modelcontextprotocol.io)

---

## Coverage

Every retailer below has been verified. The VTEX API responds. No dead URLs.

| Retailer | Country | Line | Currency |
|----------|---------|------|----------|
| **Carrefour** | AR, BR | Supermarkets | ARS, BRL |
| **Wong, Metro, Plaza Vea** | PE | Supermarkets | PEN |
| **Exito, Carulla, Olimpica** | CO | Supermarkets | COP |
| **Chedraui, HEB** | MX | Supermarkets | MXN |
| **Vea, Jumbo, Easy** | AR | Supermarkets, Home | ARS |
| **Farmatodo** | MX | Pharmacies | MXN |
| **Drogaria Pacheco** | BR | Pharmacies | BRL |
| **Motorola** | AR, BR, MX, CL | Electronics | ARS, BRL, MXN, CLP |
| **Electrolux** | AR, CL | Electronics | ARS, CLP |
| **Whirlpool** | AR, IT, FR | Electronics | ARS, EUR |
| **Sam's Club, Mambo** | BR | Supermarkets | BRL |

**8 countries. 30 retailers. 6 lines.** All verified. Growing.

---

## MCP Server

```bash
python market_mcp.py
```

30 tools ready for your AI agent.

---

## API

```
Base: https://cli-market-api.onrender.com
Docs: /docs
```

```bash
GET  /
POST /products/search   {"query":"cafe","store":"wong"}
POST /products/compare  {"query":"aceite"}
POST /v1/basket/compare {"items":[{"name":"leche","qty":2},{"name":"arroz","qty":1}]}
GET  /v1/intel/inflation?country=AR
GET  /v1/intel/competitor?product=leche&store_a=wong&store_b=plazavea
GET  /categories/{store}
```

| Tier | Requests/min | Requests/day | API Keys | Checkout | Price |
|------|-------------|-------------|----------|----------|-------|
| Free | 60 | 1,000 | 1 (read) | — | $0 |
| Pro | 300 | 10,000 | 10 (read+write) | ✓ | $49/mo |
| Enterprise | Custom | Custom | Unlimited | ✓ | [Contact](mailto:hello@cli-market.dev) |

---

## Architecture

```
AI Agent
   │
CLI Market API
   │
30 verified VTEX retailers
   │
Data moat — prices every 4h, deduplicated, historical
```

---

## Data Moat

Price collector runs every 8 hours with 228 seed queries expanded to ~900 via line-specific modifiers and a feedback loop from the data moat itself. Thousands of verified prices across 30 retailers.

```bash
python collect_prices.py              # run once
python collect_prices.py --daemon     # continuous
python collect_prices.py --status     # stats
python collect_prices.py --report     # latest prices
```

**Live dashboard:** [cli-market-api.onrender.com/dashboard](https://cli-market-api.onrender.com/dashboard) — KPIs, price trends by line and country, top products.

PostgreSQL in production. SQLite for local dev. Circuit breaker. Parallel.

---

## Links

- Landing: [cli-market.dev](https://cli-market.dev)
- API: [cli-market-api.onrender.com](https://cli-market-api.onrender.com)
- MCP Registry: `io.github.Treevu-ai/cli-market`
- Telegram: [@climarketbot](https://t.me/climarketbot)

---

## Legal

**Software:** MIT License. **Data:** Proprietary — [Data License Agreement](legal/Data_License_Agreement.md).

- [ToS](legal/ToS.md) · [Privacy](legal/Privacy.md) · [DLA](legal/Data_License_Agreement.md) · [AUP](legal/AUP.md) · [SLA](legal/SLA.md)

<p align="center">MIT © 2026 CLI Market · Treevu AI</p>
