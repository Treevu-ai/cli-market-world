mcp-name: io.github.Treevu-ai/cli-market-world

<!-- readme-hero -->
<div align="center">

<img src="https://cli-market.dev/demo.gif" alt="CLI MARKET — terminal demo" width="100%" />

</div>

# 🛒 CLI Market

[![PyPI Downloads](https://img.shields.io/badge/PyPI%20downloads-45k-00d75f?logo=pypi)](https://pepy.tech/projects/cli-market-world)
[![PyPI](https://img.shields.io/pypi/v/cli-market-world.svg)](https://pypi.org/project/cli-market-world/)

**🌐 [Español](#-español) · [English](#-english)**

---

## 🇪🇸 Español

### Cost-of-Living OS para LatAm — optimiza tu compra en una llamada.

> **Stripe convirtió los pagos en APIs. CLI Market convierte el costo de vida en una.**

`market optimize "leche, arroz, aceite" --country PE` — una llamada compara toda la canasta entre 41 retailers, calcula TCO, sugiere sustitutos y genera links de acción. Falabella, Ripley, Wong, Metro no van a exponer APIs de comercio por su cuenta. CLI Market es el puente.

**CLI Market lo resuelve.** Un solo `pip install`. Una llamada a la API que cubre **80 retailers (40 verificados activos)** en **8 países**. Un único esquema JSON listo para integrar.

- 🌍 **80 retailers (40 verificados activos) · 8 países · 4 plataformas**
- 💰 **Más de 64,000+ precios de góndola verificados**, normalizados por kg/L, actualizados cada 4 horas
- 💳 **Pago con PayPal + Mercado Pago + QR (Yape/Plin)** integrado

#### ✨ ¿Por qué CLI Market?

- 🔎 **Busca** cualquier producto en 80 retailers (40 verificados activos) de 8 países
- 📊 **Compara** precios transfronterizos — PEN, ARS, BRL, MXN, COP, CLP, EUR, USD — normalizados por kg/L cuando es posible
- 🧺 **Canasta** — compara tu carrito completo entre retailers (p. ej. Carrefour vs Jumbo vs Vea en AR)
- 📈 **Inflación** — sigue cambios reales de precios desde la góndola, actualizados cada 4 horas; historial de hasta 12 meses para señales de *cuándo* comprar, no solo *qué*
- 🧠 **Enriquecimiento** — datos de mercado a partir de góndola + APIs públicas (OFF, Wikimedia, IMF, Eurostat, BCB, Banco Mundial)
- 🛍️ **Compra** — orden interna CLI Market + pago LATAM (PayPal / Yape / Plin); no checkout en sitio del retailer
- 🏗️ **Construye** — foso de datos con spreads filtrados por calidad, matching de canasta y dashboard en vivo
- 🔗 **API-first** — schema JSON normalizado, listo para integrar; el retailer LATAM no expone APIs por su cuenta

🌐 [cli-market.dev](https://cli-market.dev) · 📚 [Docs](https://cli-market.dev/docs) · 🔧 [Tools](https://cli-market.dev/tools) · 📊 [Stats](https://cli-market.dev/stats) · [API](https://cli-market-production.up.railway.app/docs) · [Dashboard](https://cli-market-production.up.railway.app/dashboard)

#### 🚀 Inicio rápido

```bash
pip install cli-market-world
market hello   # post-instalación: estadísticas + próximos pasos
market init    # cuenta + primera búsqueda (recomendado)

# Cost-of-Living OS — una llamada optimiza toda la canasta
market optimize "leche evaporada, arroz 5kg, aceite" --country PE

# Flujo granular (opcional)
market search "leche" --country PE
market compare "aceite de girasol 900ml" --country AR
market basket "arroz:1 aceite:1 leche:1" --country AR
market checkout --payment yape
market intel brief --country PE
```

**¿Qué hace `market optimize`?** Compara toda la canasta entre retailers, calcula TCO, sugiere sustitutos con ahorro y genera links de acción — una sola llamada. **`market checkout`** crea una orden interna CLI Market con pago vía Yape/Plin/PayPal; **no** completa compras en Wong, Rappi ni Mercado Libre.

#### 💵 Planes

| Plan | Starter | Pro | Enterprise |
|------|---------|-----|------------|
| **Precio** | $9/mes | $49/mes · Anual $490 | A medida |
| **Solicitudes/día** | 1,000 | 10,000 | Ilimitadas (negociado) |
| **Solicitudes/min** | 60 | 300 | Ilimitadas |
| **API keys** | 1 | 10 | Ilimitadas |
| **Intel** | — | Ilimitado | Ilimitado + white-label |
| **Alertas de precio** | — | ✅ Hasta 10 (email) | Ilimitadas (email + webhook) |
| **Historial de precios** | 7 días | 12 meses | Completo |
| **Exportar datos** | — | CSV ilimitado + cron | Feed directo S3/webhook |
| **Checkout** | — | ✅ PayPal / Yape / Plin | ✅ |
| **Soporte** | Comunidad | Email 4h | 24/7 + SLA escrito |
| **Anual** | — | $490/año | — |

#### ¿Quién compra qué? (ecosistema)

| Buyer | Producto | Precio |
|-------|----------|--------|
| Developer / agent builder que **integra** comercio en su software | **CLI Market Pro** | $49/mes |
| Equipo de **compras** (restaurante, hotel, agro) — sin código | **Procure Copilot** | $29–149/mes (infra CLI Market incluida en Pro+) |
| Analista / fintech que necesita **datos**, no checkout | **Intelligence** | $300–500/mes |

Equipos de procurement **no** necesitan CLI Market Pro por separado. Ver [planes y pricing](https://cli-market.dev/#pricing).

---

## 🇬🇧 English

### Cost-of-Living OS for LatAm — optimize your purchase in one call.

> **Stripe turned payments into APIs. CLI Market turns cost of living into one.**

`market optimize "milk, rice, oil" --country PE` — one call compares your full basket across 41 retailers, calculates TCO, suggests substitutes, and generates action links. Falabella, Ripley, Wong, Metro won't expose commerce APIs on their own. CLI Market is the bridge.

**CLI Market fixes that.** One `pip install`. One API call across **80 retailers (40 verified active)** in **8 countries**. One JSON schema ready to integrate.

- 🌍 **80 retailers (40 verified active) · 8 countries · 4 platforms**
- 💰 **64,000+ verified shelf prices**, normalized per kg/L, refreshed every 4 hours
- 💳 **PayPal + Mercado Pago + QR (Yape/Plin)** checkout built in

#### ✨ Why CLI Market?

- 🔎 **Search** any product across 80 retailers (40 verified active) in 8 countries
- 📊 **Compare** cross-border prices — PEN, ARS, BRL, MXN, COP, CLP, EUR, USD — normalized per kg/L where parseable
- 🧺 **Basket** — compare your full cart across retailers (e.g. Carrefour vs Jumbo vs Vea in AR)
- 📈 **Inflation** — track real shelf-price changes, updated every 4 hours; up to 12-month history for *when-to-buy* signals, not just *what-to-buy*
- 🧠 **Enrichment** — market data from shelf data + public APIs (OFF, Wikimedia, IMF, Eurostat, BCB, World Bank)
- 🛍️ **Buy** — internal CLI Market order + LATAM payment (PayPal / Yape / Plin); not retailer-site checkout
- 🏗️ **Build** — data moat with quality-filtered spreads, basket matching, and live dashboard
- 🔗 **API-first** — normalized JSON schema, ready to integrate; LATAM retailers don't expose APIs themselves

🌐 [cli-market.dev](https://cli-market.dev) · 📚 [Docs](https://cli-market.dev/docs) · 🔧 [Tools](https://cli-market.dev/tools) · 📊 [Stats](https://cli-market.dev/stats) · [API](https://cli-market-production.up.railway.app/docs) · [Dashboard](https://cli-market-production.up.railway.app/dashboard)

#### 🚀 Quick start

```bash
pip install cli-market-world
market hello   # post-install: stats + next steps
market init    # account + first search (recommended)

# Cost-of-Living OS — one call optimizes your full basket
market optimize "evaporated milk, 5kg rice, cooking oil" --country PE

# Granular flow (optional)
market search "leche" --country PE
market compare "aceite de girasol 900ml" --country AR
market basket "arroz:1 aceite:1 leche:1" --country AR
market checkout --payment yape
market intel brief --country PE
```

**What does `market optimize` do?** Compares your full basket across retailers, calculates TCO, suggests substitutes with savings, and generates action links — one call. **`market checkout`** creates an internal CLI Market order with payment via Yape/Plin/PayPal; it does **not** complete purchases on Wong, Rappi, or Mercado Libre.

#### 💵 Pricing

| Plan | Starter | Pro | Enterprise |
|------|---------|-----|------------|
| **Price** | $9/mo | $49/mo · Annual $490 | Custom |
| **Requests/day** | 1,000 | 10,000 | Unlimited (negotiated) |
| **Requests/min** | 60 | 300 | Unlimited |
| **API keys** | 1 | 10 | Unlimited |
| **Intel** | — | Unlimited | Unlimited + white-label |
| **Price alerts** | — | ✅ Up to 10 (email) | Unlimited (email + webhook) |
| **Price history** | 7 days | 12 months | Full dataset |
| **Export** | — | CSV unlimited + cron | Direct S3/webhook feed |
| **Checkout** | — | ✅ PayPal / Yape / Plin | ✅ |
| **Support** | Community | Email 4h | 24/7 + written SLA |
| **Annual** | — | $490/yr | — |

#### Who buys what (ecosystem)

| Buyer | Product | Price |
|-------|---------|-------|
| Developer / agent builder **embedding** commerce in their software | **CLI Market Pro** | $49/mo |
| **Procurement** team (no code) | **Procure Copilot** | $29–149/mo (CLI Market infra bundled on Pro+) |
| Analyst / fintech needing **data**, not checkout | **Intelligence** | $300–500/mo |

Procurement teams do **not** need a separate CLI Market Pro subscription. See [pricing](https://cli-market.dev/#pricing).

---

## 📖 Learn more

- **[Docs — quick start](https://cli-market.dev/docs)** — install, auth, compare, basket, intel, setup
- **[Use cases & pricing](https://cli-market.dev/#pricing)** — developers, procurement, intelligence
- **[Public stats / data-gate](https://cli-market.dev/stats)** — live data metrics; **MAA** (Monthly Active Agents) is the north star

---

## 🏗️ Ecosystem architecture

CLI Market is composed of 4 product repos + 1 GTM repo:

```
cli-market-backend   Mirror API — paridad con prod, FastAPI server, 81 retailers, 63,000+ prices
       |
       v  raw snapshots
cli-market-index     Semantic Refinery — entity resolution, Golden Records (prod_ IDs)
       |
       v  canonical identities
cli-market-core      Intelligence SDK — MCP tools, billing, indicators (PyPI public)
       |
       v  structured intelligence
cli-market-world     Exposure — landing, docs, ops/CI, Railway prod + PyPI (THIS REPO)
```

| Repo | Visibility | Role |
|---|---|---|
| `cli-market-backend` | Private | Mirror API + FastAPI server |
| `cli-market-index` | Private | Entity resolution engine |
| `cli-market-core` | Public | Intelligence SDK + MCP tools |
| `cli-market-world` | Public | Landing + docs + Railway prod |
| `cli-market-content` | Private | GTM + content calendar |

---

## 📊 Dashboard auditability

Every price in CLI Market is traceable. The [live dashboard](https://cli-market-production.up.railway.app/dashboard) exposes:

- **Cobertura 7 días** — `coverage_7d_pct` per retailer: what % of each store's catalog refreshed in the last week
- **Normalización por kg/L** — unit price visible next to shelf price (e.g. `PEN 4.20/kg`), with counter of non-parseable names
- **Confianza por snapshot** — `ok` vs `suspect` distribution from scrape-quality heuristics
- **Percentiles P25/P50/P75** — median replaces mean in category comparisons; eliminates outlier distortion (e.g. ARS 230K in departamentales)
- **Trazabilidad de outliers** — group size, band (`median ± k·IQR`), acceptable bounds, scraper health state, capture timestamp
- **Foso de datos** — `inventory_daily[]` time series + growth stats (total snapshots, daily avg, days tracked)

All six capabilities are backed by the same **63,000+** shelf prices, refreshed every 4 hours by the collector daemon.

---

## 🔧 API tools (Shop · Intel · Account)

**32 MCP tools** (default profile) across Shop, Intel, and Account bundles. Full catalog at [cli-market.dev/tools](https://cli-market.dev/tools) · [mcp.json](mcp.json).

The canonical entry point is **`market_optimize_purchase`** — one call covers basket compare, TCO, substitutes, intel, and action links. The legacy search → compare → basket flow remains available for granular use.

---

**SINAPSIS INNOVADORA S.A.C.** — RUC 20613045563 — Lima, Peru  
MIT License · [cli-market.dev](https://cli-market.dev)