# CLI Market LATAM · v1.0

<p align="center">
  <img src="https://img.shields.io/badge/stores-8-green" alt="8">
  <img src="https://img.shields.io/badge/countries-5-blue" alt="5">
  <img src="https://img.shields.io/badge/MCP-compatible-00d75f" alt="MCP">
  <img src="https://img.shields.io/badge/python-3.10+-306998" alt="py">
  <img src="https://img.shields.io/badge/license-MIT-lightgrey" alt="MIT">
</p>

> Infrastructure layer that transforms LATAM supermarkets into AI-agent compatible commerce systems.
>
> Stripe transformed payments into APIs. We transform supermarkets into APIs for AI agents.

## The problem

E-commerce is optimized for **clicks**, not **agents**. Retailers in LATAM are not ready for autonomous commerce. No standardized AI-native supermarket layer exists. APIs are fragmented or nonexistent.

## The solution

| Human-friendly | Agent-friendly |
|---|---|
| Terminal CLI | REST API |
| Rich tables | MCP Tools |
| Spanish commands | JSON parseable |
| Purchase flow | Autonomous workflows |

## Quick start

```bash
pip install git+https://github.com/Treevu-ai/cli-market-latam.git

# Terminal 1 — backend
market-server

# Terminal 2 — CLI
market login
market search "leche"
market compare "aceite de oliva"
market add 5834 --price 45.50 --store metro --name "Tollo de Leche" --qty 2
market cart
market checkout --payment yape
market orders
```

## Agent mode

```bash
market ask "compra arroz"
market ask "compara aceite"
market ask "repite la ultima compra"
market --json                    # Machine-readable for LLMs
```

## Supported supermarkets

| Country | Stores | Platform |
|---------|--------|----------|
| 🇵🇪 Peru | Wong, Metro, Plaza Vea | VTEX |
| 🇦🇷 Argentina | Carrefour, Jumbo | VTEX |
| 🇧🇷 Brazil | Carrefour | VTEX |
| 🇲🇽 Mexico | Chedraui, HEB | VTEX |
| 🇨🇴 Colombia | Olimpica | VTEX |
| 🌐 Global | Open Food Facts (3M+ products) | Public API |

## Commands

```bash
market login              # Authenticate
market search "leche"     # Search across 8 stores
market compare "aceite"   # Price comparison
market add <id> --qty 2   # Add to cart
market cart               # View cart
market checkout           # Complete purchase
market orders             # Order history
market reorder            # Repeat last order
market ask "compra X"     # Natural language
market categories wong    # Browse categories
market barcode <ean>      # Lookup by barcode
market enrich "cafe"      # Open Food Facts search
market preferences        # Purchase profile
market countries          # List countries
market about              # Business model
market --json             # Agent-readable
```

## Architecture

```
Retailers LATAM (VTEX APIs)
        │
CLI Market LATAM
        │
APIs + MCP + Agent Layer
        │
LLMs / AI Agents / Assistants
```

## MCP Server

```bash
python market_mcp.py
```

9 tools: `market_login`, `market_search`, `market_compare`, `market_add`, `market_cart`, `market_checkout`, `market_orders`, `market_reorder`, `market_ask`.

Compatible with DeepSeek TUI, Claude, and any MCP client.

## Business model

**SaaS B2B:** Starter $499/mo · Growth $1,999/mo · Enterprise custom  
**API usage:** Per-request pricing for AI agents  
**Transaction fee:** 1-5% per completed order  
**White-label:** Retailers deploy under their own brand

## LATAM expansion

- **Phase 1:** Peru · Chile · Colombia
- **Phase 2:** Mexico · Brazil · Argentina

## Demo

```bash
asciinema rec demo.cast --command "bash demo.sh"
```

---

**"Estamos convirtiendo supermercados en infraestructura consumible por inteligencia artificial."**

🌎 [cli-market-latam.vercel.app](https://cli-market-latam.vercel.app)
