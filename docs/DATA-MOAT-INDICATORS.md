# Data Moat — Indicadores con API pública

Documento de referencia para el esquema de indicadores en CLI Market. Complementa [[data-moat-strategy]].

## Tablas

### `indicator_definitions`

Catálogo estático de indicadores (**21** en total).

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `key` | TEXT PK | Identificador estable (`promo_intensity`, `fx_usd_local`, …) |
| `name` | TEXT | Nombre legible |
| `category` | TEXT | `retail`, `macro`, `demand`, `quality`, `affordability`, `composite`, `product`, `logistics` |
| `source` | TEXT | `internal:*`, `external:*`, `computed` |
| `unit` | TEXT | `pct`, `index`, `rate`, `count`, `ratio`, `pp` |
| `refresh_hours` | INT | Frecuencia recomendada de refresh |
| `description` | TEXT | Qué mide |
| `formula` | TEXT | Fórmula o endpoint |

### `indicator_values`

Serie temporal append-only.

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `id` | PK | Autoincrement |
| `indicator_key` | TEXT | FK lógica a `indicator_definitions.key` |
| `scope` | TEXT | Ej. `PE:supermercados`, `PE:macro`, `global:all` |
| `country` | TEXT | Código ISO (vacío = global) |
| `line` | TEXT | Línea de negocio (vacío = todas) |
| `value` | REAL | Valor numérico |
| `metadata_json` | TEXT | Contexto (moneda, inputs, etc.) |
| `recorded_at` | TIMESTAMP | Momento del cálculo/fetch |

### `price_history`

Historial append-only por cambio de precio (hook en `save_price_snapshot`).

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `product_id`, `store` | TEXT | Clave del SKU |
| `price`, `list_price`, `discount` | | Estado en el momento |
| `recorded_at` | TIMESTAMP | Solo se inserta si `price` cambió vs último punto |

> **Importante:** `price_snapshots` sigue siendo upsert por `(product_id, store)`. No se altera su semántica.

---

### `enrichment_cache`

Cache de respuestas Open Food Facts (barcode/search) para no repetir llamadas.

| Columna | Descripción |
|---------|-------------|
| `cache_key` | PK — `off:barcode:{ean}` o `off:search:{term}` |
| `source` | `openfoodfacts` |
| `payload_json` | Producto normalizado (nutriscore, nova, brand) |
| `recorded_at` | TTL default 168h |

---

## Indicadores (34)

### Core moat + macro (10)

| Key | Categoría | Fuente | Refresh | Fórmula resumida |
|-----|-----------|--------|---------|------------------|
| `promo_intensity` | retail | internal | 8h | % SKUs con descuento activo |
| `price_dispersion` | retail | internal | 8h | CV medio entre tiendas por producto |
| `basket_stress_index` | affordability | internal | 8h | Canasta mínima / baseline 30d |
| `search_momentum` | demand | internal | 24h | Búsquedas 7d / 7d previos |
| `moat_freshness` | quality | internal | 8h | % snapshots < 24h |
| `store_coverage` | quality | internal | 8h | Tiendas distintas con precio |
| `fx_usd_local` | macro | [open.er-api.com](https://open.er-api.com) | 24h | USD → moneda local |
| `cpi_official_yoy` | macro | [World Bank](https://data.worldbank.org/indicator/FP.CPI.TOTL.ZG) | 7d | IPC oficial anual |
| `food_price_index` | macro | World Bank `AG.PRD.FOOD.XD` | 7d | Índice precios alimentos |
| `collector_vs_official_gap` | composite | computed | 24h | Inflación collector − CPI oficial |

### Enriquecimiento público (11)

| Key | Categoría | Fuente | Refresh | Fórmula resumida |
|-----|-----------|--------|---------|------------------|
| `off_match_rate` | product | [Open Food Facts](https://world.openfoodfacts.org) | 7d | % SKUs supermercado matcheados (sample) |
| `off_nutriscore_ab_pct` | product | Open Food Facts | 7d | % Nutri-Score A/B en matches |
| `off_nova_avg` | product | Open Food Facts | 7d | NOVA promedio (1–4) |
| `off_ultra_processed_pct` | product | Open Food Facts | 7d | % NOVA 4 (ultra-procesados) |
| `off_ecoscore_avg` | product | Open Food Facts | 7d | Eco-Score promedio (A=5 … E=1) |
| `wiki_demand_momentum` | demand | [Wikimedia Pageviews](https://wikimedia.org/api/rest_v1/) | 24h | Pageviews 7d / 7d previos (canasta) |
| `wiki_staple_momentum` | demand | Wikimedia | 24h | Momentum leche / arroz / aceite |
| `staple_price_momentum` | affordability | internal:price_history | 8h | Δ% precio canasta 7d |
| `weather_logistics_stress` | logistics | [Open-Meteo](https://open-meteo.com) | 12h | Lluvia + calor → estrés logístico 0–100 |
| `food_cpi_yoy` | macro | World Bank `FP.CPI.FOOD.ZG` | 7d | Inflación alimentaria oficial |
| `food_inflation_spread` | composite | computed | 7d | Food CPI YoY − headline CPI YoY |

### Tier 2 — fuentes públicas secundarias (10)

| Key | Categoría | Fuente | Refresh | Fórmula resumida |
|-----|-----------|--------|---------|------------------|
| `imf_inflation_yoy` | macro | [IMF DataMapper](https://www.imf.org/external/datamapper/) | 7d | PCPIPCH — validación cruzada CPI |
| `imf_gdp_growth_yoy` | macro | IMF DataMapper | 7d | NGDP_RPCH — crecimiento PIB |
| `imf_epi_inflation_yoy` | macro | IMF DataMapper | 7d | PCPIEPCH — inflación fin de período |
| `eurostat_food_hicp_yoy` | macro | [Eurostat](https://ec.europa.eu/eurostat) | 7d | Food HICP (IT, FR) |
| `eurostat_headline_hicp_yoy` | macro | Eurostat | 7d | Headline HICP CP00 (IT, FR) |
| `bcb_food_inflation_mom` | macro | [BCB](https://api.bcb.gov.br) | 7d | IPCA alimentos MoM (BR) |
| `bcb_headline_inflation_mom` | macro | BCB | 7d | IPCA general MoM (BR) |
| `macro_unemployment_rate` | macro | World Bank `SL.UEM.TOTL.ZS` | 7d | Desempleo % |
| `wb_gdp_growth_yoy` | macro | World Bank `NY.GDP.MKTP.KD.ZG` | 7d | Crecimiento PIB |
| `imf_wb_cpi_gap` | composite | computed | 7d | IMF CPI − World Bank CPI |

### Por subcategoría (3 tipos × 10 básicos)

Scope: `{CC}:subcat:{item}` — items: canasta completa (`leche`, `arroz`, `aceite`, `azucar`, `huevos`, `pan`, `cafe`, `pollo`, `queso`, `jabon`)

| Key | Fuente | Qué mide |
|-----|--------|----------|
| `subcat_price_momentum` | internal:price_history | Δ% precio 7d del básico |
| `subcat_wiki_momentum` | Wikimedia | Pageviews del artículo wiki del básico |
| `subcat_min_price` | internal:price_snapshots | Precio mínimo indexado en el país |

---

## Scores compuestos (`GET /v1/intel/scores`)

| Score | Inputs | Interpretación |
|-------|--------|----------------|
| `retail_aggression` | `promo_intensity` | Alta promo → score alto |
| `price_fairness` | `price_dispersion` | Alta dispersión → score bajo (menos “justo”) |
| `basket_stress` | `basket_stress_index` | >105 elevado, <95 aliviado |
| `data_confidence` | `moat_freshness` | ≥80 fresh |
| `macro_alignment` | `collector_vs_official_gap` | Gap pequeño → alineado con CPI |
| `product_intelligence` | `off_match_rate`, `off_nova_avg` | Cobertura OFF − penalización NOVA alta |
| `demand_outlook` | `wiki_demand_momentum` | >1.1 rising, <0.9 cooling |
| `logistics_risk` | `weather_logistics_stress` | >40 elevated (lluvia/calor) |
| `food_premium` | `food_inflation_spread` | Spread food vs headline CPI |
| `nutrition_quality` | `off_nutriscore_ab_pct`, `off_ultra_processed_pct`, `off_ecoscore_avg` | Calidad nutricional + ambiental |
| `staple_demand` | `wiki_staple_momentum` | Demanda Wikipedia en básicos |
| `macro_validation` | `imf_wb_cpi_gap` | Consistencia IMF vs World Bank |
| `labor_stress` | `macro_unemployment_rate` | Presión laboral / desempleo |
| `growth_outlook` | `imf_gdp_growth_yoy` | Expansión vs desaceleración PIB |

---

## Endpoints API

```bash
# Catálogo
curl "http://127.0.0.1:8765/v1/intel/indicators"

# Un indicador
curl "http://127.0.0.1:8765/v1/intel/indicators/promo_intensity?country=PE&line=supermercados"

# Scores compuestos
curl "http://127.0.0.1:8765/v1/intel/scores?country=PE"

# Canasta
curl "http://127.0.0.1:8765/v1/intel/basket-stress?country=PE"

# Refresh (internal + APIs públicas + enriquecimiento)
curl -X POST "http://127.0.0.1:8765/v1/intel/refresh?country=PE"

# Solo indicadores de enriquecimiento
curl "http://127.0.0.1:8765/v1/intel/enrichment?country=PE"

curl "http://127.0.0.1:8765/v1/intel/enrichment/subcategories?country=PE"

# Refresh solo enriquecimiento (sin recalcular todo el moat)
curl -X POST "http://127.0.0.1:8765/v1/intel/enrichment/refresh?country=PE"
```

Endpoints existentes **sin cambios de contrato**:

- `GET /v1/intel/inflation`
- `GET /v1/intel/alerts` — ahora usa `price_history` cuando hay datos

---

## Overlap retailer + cobertura macro

| País | Retailers CLI (ej.) | FX | CPI World Bank | QR/pagos locales |
|------|---------------------|----|----------------|------------------|
| PE | Wong, Metro, Plaza Vea | PEN | Sí | Yape/Plin + MP limitado |
| AR | Carrefour, Jumbo, Vea | ARS | Sí | MP QR híbrido fuerte |
| MX | Carrefour, Chedraui | MXN | Sí | MP QR híbrido |
| BR | Carrefour, C&A, Hering | BRL | Sí | MP + Pix |
| CL | Falabella, Ripley | CLP | Sí | MP |
| CO | Falabella, Farmatodo | COP | Sí | MP |

**Decisión de diseño:** MP-first para pagos phygital; indicadores macro agnósticos vía World Bank + FX público.

---

## Operación

| Acción | Cuándo |
|--------|--------|
| Collector cada 8h | Alimenta `price_snapshots` + `price_history` + **refresh automático de indicadores** |
| `POST /v1/intel/refresh` | Tras collector o cron diario para macro |
| **Auto** — `collect_prices.py` | Tras cada corrida (daemon o once), `INDICATOR_AUTO_REFRESH=1` (default) |

### CLI

```bash
market intel indicators              # catálogo de 34 indicadores
market intel indicators -c PE        # catálogo + scores PE
market intel enrichment -c PE        # señales OFF / Wiki / clima / food CPI
market intel scores -c PE            # scores compuestos
market intel inflation -c PE         # variación por línea (7d)

# Legacy (shim): market indicators … → market intel indicators …
# Ops refresh: POST /v1/intel/refresh (no expuesto en --help público)
```
| `GET /v1/intel/scores` | Agentes MCP / dashboard |

---

## Disclaimer comercial

Todos los indicadores macro llevan disclaimer: **no reemplazan INEI, INDEC, IBGE ni índices oficiales**. El moat aporta señales operativas de góndola + contexto macro público.
