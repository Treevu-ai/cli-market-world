mcp-name: io.github.Treevu-ai/cli-market-world

# 🛒 CLI Market

**🌐 [Español](#-español) · [English](#-english)**

---

## 🇪🇸 Español

### Infraestructura de comercio para agentes de IA — un solo `pip install`, una API, cero scraping.

> **Stripe convirtió los pagos en APIs. CLI Market convierte el comercio en una.**

Los agentes de IA todavía no pueden comprar en el mundo real. Cada retailer exige su propia autenticación, su propia lógica de búsqueda y no comparten carrito — así que los agentes fallan antes de la primera consulta.

**CLI Market lo resuelve.** Un solo `pip install`. Una llamada a la API que cubre **66 retailers (66 verificados)** en **11 países**. Un único esquema JSON.

- 🌍 **66 retailers (66 verificados) · 11 países · 3 plataformas · 43 herramientas MCP · 0 indicadores**
- 💰 **Más de 45,000+ precios de góndola verificados**, normalizados por kg/L, actualizados cada 4 horas
- 💳 **Pago con PayPal + QR (Yape / Plin)** integrado

#### ✨ ¿Por qué CLI Market?

- 🔎 **Busca** cualquier producto en 66 retailers (66 verificados) de 11 países
- 📊 **Compara** precios transfronterizos — PEN, ARS, BRL, MXN, COP, CLP, EUR, USD — normalizados por kg/L cuando es posible
- 🧺 **Canasta** — compara tu carrito completo entre retailers (p. ej. Carrefour vs Jumbo vs Vea en AR)
- 📈 **Inflación** — sigue cambios reales de precios desde la góndola, actualizados cada 4 horas
- 🧠 **Enriquecimiento** — 34 indicadores de mercado a partir de datos de góndola + APIs públicas (OFF, Wikimedia, IMF, Eurostat, BCB, Banco Mundial)
- 🛍️ **Compra** — checkout con PayPal o QR (Yape / Plin)
- 🏗️ **Construye** — foso de datos con spreads filtrados por calidad, matching de canasta y dashboard en vivo

🌐 [cli-market.dev](https://cli-market.dev) · 📚 [Docs de API](https://cli-market-production.up.railway.app/docs) · 📊 [Dashboard](https://cli-market-production.up.railway.app/dashboard)

#### 🚀 Inicio rápido

```bash
pip install cli-market
market hello   # post-instalación: estadísticas + próximos pasos

export MARKET_API_URL=https://cli-market-production.up.railway.app
market login
market search "leche" --country PE
market compare "aceite de girasol 900ml" --country AR
market basket "arroz:1 aceite:1 leche:1" --country AR
market checkout --payment yape
market ask "compra arroz al mejor precio"
market indicators --country PE
market enrichment --refresh -c PE
```

#### 💵 Planes

| | Free | Pro | Enterprise |
| --- | --- | --- | --- |
| **Precio** | $0 | $49/mes | A medida |
| **Solicitudes** | 1 000/día | 10 000/día | Ilimitadas |
| **API keys** | 1 (lectura) | 10 (lectura+escritura) | Ilimitadas |
| **Checkout** | — | ✅ (tras activación por email) | ✅ |
| **Exportar datos** | — | JSON/CSV | ✅ |
| **Soporte** | Comunidad | Email | 24/7 + onboarding |

> 📄 Posicionamiento en español (API / landing / ventas): [`docs/api-positioning-es.md`](docs/api-positioning-es.md)

---

## 🇬🇧 English

### Commerce infrastructure for AI agents — one `pip install`, one API, zero scraping.

> **Stripe turned payments into APIs. CLI Market turns commerce into one.**

AI agents still can't shop in the real world. Every retailer means separate auth, separate search logic, no shared cart — so agents fail before the first query.

**CLI Market fixes that.** One `pip install`. One API call across **66 retailers (66 verified)** in **11 countries**. One JSON schema.

- 🌍 **66 retailers (66 verified) · 11 countries · 3 platforms · 43 MCP tools · 0 indicators**
- 💰 **45,000+ verified shelf prices**, normalized per kg/L, refreshed every 4 hours
- 💳 **PayPal + QR (Yape / Plin)** checkout built in

#### ✨ Why CLI Market?

- 🔎 **Search** any product across 66 retailers (66 verified) in 11 countries
- 📊 **Compare** cross-border prices — PEN, ARS, BRL, MXN, COP, CLP, EUR, USD — normalized per kg/L where parseable
- 🧺 **Basket** — compare your full cart across retailers (e.g. Carrefour vs Jumbo vs Vea in AR)
- 📈 **Inflation** — track real shelf-price changes, updated every 4 hours
- 🧠 **Enrichment** — 34 market indicators from shelf data + public APIs (OFF, Wikimedia, IMF, Eurostat, BCB, World Bank)
- 🛍️ **Buy** — checkout with PayPal or QR (Yape / Plin)
- 🏗️ **Build** — data moat with quality-filtered spreads, basket matching, and live dashboard

🌐 [cli-market.dev](https://cli-market.dev) · 📚 [API docs](https://cli-market-production.up.railway.app/docs) · 📊 [Dashboard](https://cli-market-production.up.railway.app/dashboard)

#### 🚀 Quick start

```bash
pip install cli-market
market hello   # post-install: stats + next steps

export MARKET_API_URL=https://cli-market-production.up.railway.app
market login
market search "leche" --country PE
market compare "aceite de girasol 900ml" --country AR
market basket "arroz:1 aceite:1 leche:1" --country AR
market checkout --payment yape
market ask "buy rice at the best price"
market indicators --country PE
market enrichment --refresh -c PE
```

#### 💵 Pricing

| | Free | Pro | Enterprise |
| --- | --- | --- | --- |
| **Price** | $0 | $49/mo | Custom |
| **Requests** | 1,000/day | 10,000/day | Unlimited |
| **API keys** | 1 (read) | 10 (read+write) | Unlimited |
| **Checkout** | — | ✅ (after email activation) | ✅ |
| **Data export** | — | JSON/CSV | ✅ |
| **Support** | Community | Email | 24/7 + onboarding |

---

## 📊 Dashboard auditability

Every price in CLI Market is traceable and verifiable. The [live dashboard](https://cli-market-production.up.railway.app/dashboard) exposes:

- **Cobertura 7 días** — `coverage_7d_pct` per retailer: what % of each store's catalog refreshed in the last week
- **Normalización por kg/L** — unit price visible next to shelf price (e.g. `PEN 4.20/kg`), with counter of non-parseable names
- **Confianza por snapshot** — `ok` vs `suspect` distribution from scrape-quality heuristics
- **Percentiles P25/P50/P75** — median replaces mean in category comparisons; eliminates outlier distortion (e.g. ARS 230K in departamentales)
- **Trazabilidad de outliers** — group size, band (`median ± k·IQR`), acceptable bounds, scraper health state, capture timestamp
- **Foso de datos** — `inventory_daily[]` time series + growth stats (total snapshots, daily avg, days tracked)

All six capabilities are backed by the same 43,000+ verified shelf prices, refreshed every 4 hours by the collector daemon.

---

## 🔧 43 MCP tools · 0 indicators

`market_login` `market_lines` `market_search` `market_compare` `market_add` `market_cart` `market_cart_update` `market_cart_remove` `market_checkout` `market_orders` `market_reorder` `market_ask` `market_basket` `market_inflation` `market_indicators` `market_scores` `market_intel_refresh` `market_enrichment` `market_enrichment_subcategories` `market_enrichment_refresh` `market_analytics_indicators` `market_categories` `market_barcode` `market_enrich` `market_stores` `market_countries` `market_ticket` `market_voice` `market_price_history` `market_stats` `market_alerts` `market_whoami` `market_preferences` `market_subscription` `market_export` `market_trending` `market_scan` `market_stock` `market_notify` `market_brands` `market_favorites` `market_exchange` `market_delivery`

Docs: [`docs/DATA-MOAT-INDICATORS.md`](docs/DATA-MOAT-INDICATORS.md) · GitHub: [Treevu-ai/cli-market-world](https://github.com/Treevu-ai/cli-market-world)

---

**SINAPSIS INNOVADORA S.A.C.** — RUC 20613045563 — Lima, Peru  
MIT License · [cli-market.dev](https://cli-market.dev)
