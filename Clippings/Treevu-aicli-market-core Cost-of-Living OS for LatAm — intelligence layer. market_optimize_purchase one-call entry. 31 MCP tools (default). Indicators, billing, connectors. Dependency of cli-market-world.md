---
title: "Treevu-ai/cli-market-core: Cost-of-Living OS for LatAm — intelligence layer. market_optimize_purchase one-call entry. 31 MCP tools (default). Indicators, billing, connectors. Dependency of cli-market-world."
source: "https://github.com/Treevu-ai/cli-market-core"
author:
published:
created: 2026-07-15
description: "Cost-of-Living OS for LatAm — intelligence layer. market_optimize_purchase one-call entry. 31 MCP tools (default). Indicators, billing, connectors. Dependency of cli-market-world. - Treevu-ai/cli-market-core"
tags:
  - "clippings"
---
[![CLI MARKET CORE](https://camo.githubusercontent.com/b84359d33b8118128abcccfeee6c626c9689996d1b24399665da99434108b549/68747470733a2f2f636c692d6d61726b65742e6465762f64656d6f2e676966)](https://camo.githubusercontent.com/b84359d33b8118128abcccfeee6c626c9689996d1b24399665da99434108b549/68747470733a2f2f636c692d6d61726b65742e6465762f64656d6f2e676966)

## cli-market-core

> **Intelligence Layer** — Indicators, billing, connectors, and MCP tools for CLI Market

```
pip install cli-market-world
```

Install **`cli-market-world`** for the full CLI + MCP experience. This package is the intelligence dependency pulled in automatically.

---

## What is this?

`cli-market-core` is the intelligence engine of the CLI Market ecosystem: price indicators, spread analysis, billing/payments, retailer connectors, and MCP tool definitions.

---

## Links

- 🌐 [cli-market.dev](https://cli-market.dev/)
- 📚 [Docs](https://cli-market.dev/docs)
- 🔧 [MCP /tools](https://cli-market.dev/tools)
- 📦 [PyPI — cli-market-world](https://pypi.org/project/cli-market-world/)

---

## Ecosystem

```
cli-market-backend  →  Data ingestion (scrapers, FastAPI)
cli-market-index    →  Semantic refinery (Golden Records)
cli-market-core     →  Intelligence (THIS PACKAGE)
cli-market-world    →  CLI + MCP exposure (pip install target)
```

---

## Modules

| Module | Role |
| --- | --- |
| `market_core` | Core service orchestrator |
| `market_indicators` | 46 market indicators from shelf data |
| `market_spread` | Cross-retailer price spreads |
| `market_mcp` | MCP tool definitions |
| `market_basket` | Basket comparison logic |
| `market_billing` | Subscription and billing |
| `market_connectors/` | PayPal, Mercado Pago, VTEX, Shopify, etc. |

Canonical stats: run `python ops/sync_market_stats.py` in **cli-market-world**.

---

MIT License · [SINAPSIS INNOVADORA S.A.C.](https://cli-market.dev/) · Lima, Peru