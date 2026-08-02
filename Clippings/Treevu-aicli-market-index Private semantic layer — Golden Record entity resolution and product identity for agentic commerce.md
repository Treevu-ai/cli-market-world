---
title: "Treevu-ai/cli-market-index: Private semantic layer — Golden Record entity resolution and product identity for agentic commerce"
source: "https://github.com/Treevu-ai/cli-market-index"
author:
published:
created: 2026-07-15
description: "Private semantic layer — Golden Record entity resolution and product identity for agentic commerce - Treevu-ai/cli-market-index"
tags:
  - "clippings"
---
[![CLI MARKET INDEX](https://github.com/Treevu-ai/cli-market-index/raw/treevu-ai-main/assets/readme-hero.svg)](https://github.com/Treevu-ai/cli-market-index/blob/treevu-ai-main/assets/readme-hero.svg)

## cli-market-index

> **Private repo** · Treevu-ai org — request access from maintainer.

> **The Semantic Moat** — Entity Resolution & Knowledge Graph for CLI Market

"Stripe apifizó los pagos, CLI Market apifiza los comercios."

---

## What is this?

`cli-market-index` is the semantic brain of the CLI Market ecosystem. It transforms chaotic, inconsistent retailer data from 81+ stores (VTEX, Shopify, Magento, WooCommerce) into a single, canonical, deduplicated **Golden Record** per product.

It is the moat. Once a product enters the Index with a `prod_` ID, that identity is immutable across all downstream consumers: the backend API, MCP tools, and AI agents.

---

## Architecture

```
cli-market-index/
├── src/
│   ├── api/
│   │   └── resources.py        ← Stripe-style objects (prod_, brnd_, cat_, sku_, bskt_)
│   ├── schemas/
│   │   └── canonical.py        ← Golden Record internal storage schema
│   ├── engines/
│   │   └── normalizer/
│   │       ├── unit_normalizer.py   ← ml/L/kg/unit extraction & normalization
│   │       └── brand_normalizer.py  ← 66+ retailer brand → canonical slug
│   ├── core/
│   │   └── resolver.py         ← Entity Resolution Engine (exact + fuzzy + drift)
│   └── services/
│       └── index_service.py    ← Stripe-like facade (resolve, register, enrich)
├── tests/
│   ├── fixtures/
│   │   └── raw_snapshots.py    ← Real retailer snapshot samples
│   └── integration/
│       └── test_resolution.py  ← E2E Golden Record identity tests
├── index_gate.py               ← Drop-in bridge for cli-market-backend
└── pyproject.toml
```

---

## Core Concepts

### The Golden Record (prod\_)

Every unique product — regardless of how many retailers carry it or how differently they name it — resolves to a single canonical `Product` object with a stable, prefixed ID:

```
prod_gloria_lacteos_1l
prod_primor_aceites_1l
prod_sanluis_bebidas_3.75l
```

### Stripe-style Resources

All objects follow Stripe's API design principles:

| Resource | Prefix | Example |
| --- | --- | --- |
| Product | `prod_` | `prod_gloria_lacteos_1l` |
| Brand | `brnd_` | `brnd_gloria` |
| Category | `cat_` | `cat_lacteos` |
| Retailer SKU | `sku_` | `sku_plazavea_12345` |
| Market Basket | `bskt_` | `bskt_user_1234567890` |

### Resolution Pipeline

```
Raw Retailer Data
       ↓
1. Normalize  → unit_normalizer + brand_normalizer
2. Candidate  → build lookup key (prod_<brand>_<cat>_<qty><unit>)
3. Score      → exact (0.98) | fuzzy (0.75) | none (0.0)
4. Audit      → detect semantic drift (price anomaly → confidence penalty)
       ↓
ResolutionResult { product, confidence, match_type }
```

### Canonical Units

| Raw | Canonical |
| --- | --- |
| `ml`, `cc`, `1000ml` | `L` |
| `g`, `gr`, `grs`, `gramos` | `kg` |
| `kg`, `kilos` | `kg` |
| `L`, `lt`, `litro`, `litros` | `L` |
| `un`, `u`, `uds`, `x12` | `unit` |
| `6 x 625ml` | `3.75 L` (total content) |

---

## Usage

### From cli-market-backend (drop-in)

```
from index_gate import enrich_product, enrich_list

# Single product
item = {"name": "Leche Gloria 1L", "price": 4.50, "store": "plazavea_pe"}
enriched = enrich_product(item)
# → item["index"] = {"id": "prod_gloria_lacteos_1l", "confidence": 0.98, ...}

# Batch
enriched_list = enrich_list(products, store_key="metro_pe")
```

### Direct IndexService

```
from services.index_service import IndexService

index = IndexService()
result = index.resolve_snapshot({
    "store":    "plazavea_pe",
    "sku":      "12345",
    "name":     "Leche Gloria Entera Caja 1L",
    "price":    4.50,
    "currency": "PEN",
    "brand":    "Gloria",
})
print(result.product.id)       # prod_gloria_lacteos_1l
print(result.confidence)       # 0.98
print(result.match_type)       # 'exact'
```

---

## Running Tests

```
pip install -e ".[dev]"
pytest

# Or run directly:
python tests/integration/test_resolution.py
```

---

## Ecosystem

Canonical public metrics: `cli-market-world/ops/sync_market_stats.py` → `landing/lib/marketStats.ts`.

| Repo | Role |
| --- | --- |
| `cli-market-backend` | Data ingestion — collector, FastAPI prod API, 81 retailers (41 verified active), 61,000+ verified shelf prices |
| `cli-market-index` | **This repo** — Semantic brain, entity resolution |
| `cli-market-core` | Intelligence — indicators, stats, billing, connectors, MCP SDK |
| `cli-market-world` | Exposure — Next.js landing, docs, mirror API, ops/CI, PyPI `cli-market-world` |

---

## Status

- Stripe-style resource definitions (`prod_`, `brnd_`, `cat_`, `sku_`, `bskt_`)
- Unit normalizer (ml, L, kg, g, packs, countables)
- Brand normalizer (18 canonical brands, 66+ retailer variants)
- Entity Resolver (exact + fuzzy + semantic drift detection)
- IndexService facade (resolve, register, enrich, list)
- Index Gate (drop-in bridge for backend)
- Integration tests (cross-retailer Golden Record identity)
- Vector embeddings for semantic similarity
- Postgres persistence layer (optional `INDEX_DATABASE_URL`; SQLite default)
- REST API exposure via FastAPI (`routers/index_api.py` on backend + world mirror)
- MCP tools `index_resolve`, `index_lookup`, `index_stats` (backend `market_mcp.py`)