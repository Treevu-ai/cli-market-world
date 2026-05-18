<p align="center">
  <img src="https://img.shields.io/badge/retailers-3600+-brightgreen" alt="3600 retailers">
  <img src="https://img.shields.io/badge/lines-12-blue" alt="12 lines">
  <img src="https://img.shields.io/badge/countries-67-orange" alt="67 countries">
  <img src="https://img.shields.io/badge/MCP%20tools-12-00d75f" alt="MCP">
  <img src="https://img.shields.io/badge/python-3.10+-306998" alt="py">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" alt="MIT">
  <img src="https://img.shields.io/badge/build-passing-brightgreen" alt="build">
  <img src="https://img.shields.io/badge/CI-vercel-black" alt="Vercel">
</p>

<h1 align="center">CLI Market</h1>
<p align="center"><b>Commerce infrastructure for AI agents.</b><br>3,600+ retailers · 12 lines · 67 countries · 1 API.</p>

---

## What is CLI Market?

CLI Market is the middleware between VTEX and AI agents. One API call searches, compares, and purchases across 3,600+ retailers in 67 countries. Human-friendly CLI. Agent-friendly MCP tools. JSON-parseable output.

> Stripe turned payments into APIs. We turn commerce into APIs.

## Quick start

### Linux / macOS / WSL

```bash
# 1. Install
pip install cli-market

# 2. Start backend
market-server &

# 3. Use the CLI
market login
market search "leche" --country PE
market compare "aceite"
market add 3 --qty 2
market checkout --payment yape

# 4. Agent mode
market ask "compra arroz"
market --json
```

### Windows (PowerShell)

```powershell
# 1. Install
pip install cli-market

# 2. Start backend (in a separate terminal)
Start-Process -NoNewWindow python -ArgumentList "-m", "market_server"

# 3. Use the CLI
market login
market search "leche" --country PE
market compare "aceite"
market add 3 --qty 2
market checkout --payment yape

# 4. Agent mode
market ask "compra arroz"
market --json
```

### Windows (CMD)

```cmd
:: 1. Install
pip install cli-market

:: 2. Start backend (in a separate terminal)
start python -m market_server

:: 3. Use the CLI
market login
market search "leche" --country PE
market compare "aceite"
market add 3 --qty 2
market checkout --payment yape

:: 4. Agent mode
market ask "compra arroz"
market --json
```

## Features

| For humans | For AI agents |
|---|---|
| Terminal CLI | REST API + JSON |
| Rich tables | 12 MCP Tools |
| Spanish / English | CSV export |
| `market search "milk"` | Autonomous workflows |

### Commands

`login` `lines` `search` `compare` `add` `cart` `cart-update` `cart-remove` `cart-clear` `checkout` `orders` `reorder` `ask` `--json`

### MCP Server

```bash
python market_mcp.py
```

12 tools: `market_login` `market_lines` `market_search` `market_compare` `market_add` `market_cart` `market_cart_update` `market_cart_remove` `market_checkout` `market_orders` `market_reorder` `market_ask`

Compatible with DeepSeek TUI, Claude, Cursor, and any MCP client.

## Coverage

3,600+ retailers across 12 business lines in 67 countries.

| Line | Count | Key retailers |
|------|-------|--------------|
| 👕 Moda | 1,560 | Louis Vuitton · Gucci · Prada · Chanel · Dior · Zara · H&M · Levi's · Nike · Adidas · Renner · Lamborghini · Ferrari |
| 📱 Electro | 571 | Samsung · Apple · Sony · LG · Panasonic · Dell · HP · Lenovo · Yamaha · Dyson |
| 🏠 Hogar | 314 | IKEA · Homecenter · Sodimac · Miele · Bosch · Smeg · Tefal · KitchenAid |
| ⚽ Deportes | 306 | Nike · Adidas · Reebok · Puma · Under Armour · Decathlon · Foot Locker · Patagonia |
| 🛒 Supermercados | 252 | Wong · Carrefour · Jumbo · Coto · Costco · Sainsbury's · Edeka · Albert Heijn |
| 🍔 Alimentos | 176 | Nestle · Unilever · Coca-Cola · Pepsi · Lindt · Heineken · Nespresso |
| 💄 Belleza | 170 | Sephora · MAC · Clinique · Estee Lauder · Lancome · Lush · Yves Rocher |
| 🏬 Departamentales | 136 | Mercado Libre · El Corte Ingles · Otto · Miniso · Lego · Americanas |
| 💊 Farmacias | 51 | Droga Raia · Drogasil · Boots · DM · Rossmann |
| 🔧 Autopartes | 50 | BMW · Mercedes-Benz · Audi · Tesla · Harley Davidson · Ducati |
| 📚 Librería | 11 | Staples · Office Depot |


**Countries:** 67 países en LATAM, Europa y global

## API

```
Base URL: https://cli-market-api-production.up.railway.app
Swagger:  /docs
llms.txt: https://cli-market.dev/llms.txt
```

### Endpoints

```bash
# Status
GET /

# Data Feed
GET /v1/feed/prices?query=cafe&country=PE&format=csv
GET /v1/feed/stats?period=7d

# Competitive Intelligence (CIaaS)
GET /v1/intel/competitor?product=leche&store_a=wong&store_b=plazavea
GET /v1/intel/delta?product=cafe&country_a=PE&country_b=CO
GET /v1/intel/alerts?product=arroz&threshold_pct=5

# Pricing
GET /v1/pricing
```

### Rate limits

| Tier | Requests/min | Requests/day | CIaaS |
|------|-------------|-------------|-------|
| Free | 10 | 100 | No |
| Paid | Contact | Contact | Yes |

## Architecture

```
AI Agents (Claude, DeepSeek, GPT)
        |
   CLI Market API    ← You are here
        |
   3,600+ VTEX retailers across 67 countries
        |
  SQLite data moat — price snapshots, search history
```

## Why this exists

E-commerce is optimized for clicks, not agents. VTEX powers 3,600+ retailers with the same public API — yet no one has built a unified agentic layer on top. CLI Market is that layer.

## Links

- Landing: [cli-market.dev](https://cli-market.dev)
- API: [cli-market-api-production.up.railway.app](https://cli-market-api-production.up.railway.app)
- Telegram: [@climarketbot](https://t.me/climarketbot)
- llms.txt: [cli-market.dev/llms.txt](https://cli-market.dev/llms.txt)

## License

MIT © 2026 CLI Market · Sinapsis Innovadora
