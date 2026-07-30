# PIT ↔ CLI Market — límites de producto y Market Evidence Package

**Estado:** contrato de producto + mocks e integración delgada (fases 0–2)  
**Fecha:** 2026-07-29  
**PIT API (referencia):** `https://cli-market-pit-backend.fly.dev` — OpenAPI en `/docs`  
**CLI Market API (prod):** `https://cli-market-api.fly.dev`  
**Implementación delgada:** `ops/market_evidence_package.py` · fixtures en `ops/pit_integration/`

## 1. Principio

| Producto | Dominio | No es |
|----------|---------|--------|
| **PIT** (*PIT Research API*) | Corridas de *technology intelligence* trazables: query científica/aplicada, enrich por dominio, report/PDF, ficha de oportunidad tech | Motor de precios de góndola |
| **CLI Market** | Evidencia de retail formal online: surtido, precios, inflación de estantería, affordability, scores, export citables | Scouting de papers, patentes ni HS como eje de research |

**Regla de oro para backlog**

- Papers, HS scouting, research-run, PDF tech, enrich domain científico → **PIT**
- Precio, surtido, shelf inflation, affordability, methods export → **CLI Market**
- Ficha unificada ciencia + mercado / demo de innovación → **orquestación**, no duplicar tools en ambos lados

Integración por **contrato de datos** (Market Evidence Package), no por reimplementar el stack del otro producto.

```
┌─────────────────────────────────────────────────────────┐
│  Orquestación (agente innovación / glue)                │
│  Une report PIT + Market Evidence Package → ficha final │
└───────────────────────┬─────────────────────────────────┘
                        │
          ┌─────────────┴─────────────┐
          ▼                           ▼
┌──────────────────┐        ┌──────────────────────┐
│ PIT              │        │ CLI Market           │
│ research runs    │        │ search/compare/intel │
│ enrich / report  │        │ affordability/scores │
│ ficha (estructura)│       │ export / methods     │
│ HS / tech domains│        │ nowcast / CPI bridge │
└──────────────────┘        └──────────────────────┘
```

## 2. Matriz de endpoints PIT → CLI Market

Fuente de paths: OpenAPI PIT Research API v0.1.0 (*Traceable technology-intelligence research runs*).

| Endpoint PIT | Qué aporta | Capacidad CLI Market | Gap | Owner |
|--------------|------------|----------------------|-----|--------|
| `POST /v1/research-runs` | Crear corrida (`query`, `target_market`, `application`, fechas, `limit`) | No hay research-run de literatura | No cubrir | **PIT** |
| `POST /v1/research-runs/full` | Corrida + `hs_code` | No hay scouting por HS | No cubrir | **PIT** |
| `GET /v1/research-runs/{run_id}` | Estado / artefacto de corrida | — | — | **PIT** |
| `POST .../enrich/{domain}` | Enrich multi-dominio (literatura, trade, etc.) | Enrich de intel de precios vía brief/scores (otro dominio) | No clonar domains de PIT | **PIT** |
| `GET .../report` y `.../report.pdf` | Informe tech-intel | Price Pulse / intel brief ≠ report de papers | No cubrir | **PIT** |
| `POST .../ficha` | Ficha de oportunidad (`segment`, `stage`, `market_label`) | Flujo innovación con search/compare/intel (docs ERP/agentes) | Falta bloque estandarizado **evidencia de mercado** | **PIT orquesta** + **CLI Market provee datos** |
| Auth (signup / login / tiers free·pro·enterprise) | Cuenta PIT | Auth propia (API key, billing) | Identidad unificada opcional | **Producto/ops** |
| `GET /v1/agents/status` | Disponibilidad de agentes PIT | Market Orchestrator (otro runtime) | No unificar runtimes | Cada producto |
| `GET /v1/connectors/status` | Salud de conectores científicos | Cobertura/freshness vía stats | Separados | Cada producto |
| `GET /v1/health`, `/metrics` | Ops | Ops world/Fly | Separados | Cada producto |

**Nota operativa (probe 2026-07-29):** en el deploy público de PIT, el módulo de agentes puede no estar instalado (`ficha_available: false`). Eso no cambia el contrato de producto; solo el readiness de demo.

## 3. Bloques de la ficha de oportunidad

| Bloque | Fuente ideal | Estado |
|--------|--------------|--------|
| Hipótesis / query tecnológica | PIT research run | PIT |
| Evidencia científica (papers, tech) | PIT enrich + report | PIT |
| País / application / HS | Inputs PIT | PIT |
| Surtido y precios observables | `market_search`, `market_compare`, `market_discover` | CLI Market listo |
| Señal macro de góndola | `market_intel_brief`, `market_inflation`, `market_scores` | CLI Market listo |
| Asequibilidad / presión | `market_affordability` | CLI Market listo |
| Ruido vs oportunidad | `market_trending`, `market_price_risk` (+ promo si aplica) | CLI Market listo |
| Exploratorio cross-border | Compare multi-país / arbitrage (con caveats) | CLI Market parcial |
| Bundle citable / metodología | Methods export + `market_export` | CLI Market listo (skill; API formal opcional) |
| Nowcast / gap vs CPI | Skills nowcast + cpi-bridge | CLI Market listo (no es core de PIT) |
| Stage / segment / go-no-go | PIT ficha + juicio humano/ERP | PIT + cliente |
| PDF unificado ciencia + mercado | Un solo artefacto unificado | Orquestador (fase 2) |

Referencia de flujo solo-CLI-Market (sin papers): `Casos_de_uso_CLI_Market_ERP_agentes.md` (innovación / ficha con evidencia de góndola).

## 4. Market Evidence Package (contrato)

Paquete JSON que **CLI Market produce** (vía API/MCP/orquestador) y **PIT (o un agente) consume** al armar la ficha o el anexo de mercado.

### 4.1 Propósito

- Anclar una hipótesis tech/aplicada a **precios y surtido reales** de retail formal online.
- Ser **trazable** (`as_of`, tools usadas, product_ids) sin pretender ser IPC oficial ni mercado informal.
- Evitar que PIT reimplemente collector, search o indicators.

### 4.2 Mapping típico desde un research run PIT

| Campo PIT (run) | Uso en CLI Market |
|-----------------|-------------------|
| `query` | Semilla de búsqueda / categoría (puede requerir normalización a términos de góndola) |
| `target_market` (ISO-2) | `country` en search/compare/intel |
| `application` | Contexto narrativo; opcionalmente `line` (default `supermercados` si es alimentos/funcionales) |
| `hs_code` | No se usa en collector de góndola; queda en lado PIT. Opcional en metadata del package solo como ref |
| `run_id` | Se copia a `consumer_ref` / `pit_run_id` para trazabilidad cruzada |
| `from_publication_date`, `limit` | No aplican a góndola | 

### 4.3 Schema (v0.1 — contrato, no endpoint obligatorio)

```json
{
  "schema_version": "0.1",
  "package_id": "mep_<ulid_or_uuid>",
  "as_of": "2026-07-29T18:00:00Z",
  "generated_by": {
    "system": "cli-market",
    "api_base": "https://cli-market-api.fly.dev",
    "tools_used": [
      "market_discover",
      "market_search",
      "market_compare",
      "market_intel_brief",
      "market_inflation",
      "market_scores",
      "market_affordability",
      "market_stats"
    ]
  },
  "consumer_ref": {
    "pit_run_id": "optional-run-id-from-pit",
    "request_id": "optional-caller-id"
  },
  "request": {
    "query": "blueberry functional beverage",
    "country": "PE",
    "line": "supermercados",
    "application": "functional foods and beverages",
    "hs_code": null,
    "max_items": 25
  },
  "coverage": {
    "retailers_with_price": 0,
    "items_returned": 0,
    "freshness_pct_under_24h": null,
    "data_confidence": null,
    "notes": []
  },
  "assortment": [
    {
      "product_id": "string",
      "name": "string",
      "brand": "string|null",
      "store": "string",
      "country": "PE",
      "price": 0,
      "currency": "PEN",
      "unit": "string|null",
      "url": "string|null",
      "observed_at": "ISO-8601|null"
    }
  ],
  "price_summary": {
    "currency": "PEN",
    "min": null,
    "max": null,
    "median": null,
    "n": 0,
    "method": "simple_on_returned_items"
  },
  "signals": {
    "intel_brief_headline": "string|null",
    "inflation": {},
    "scores": {},
    "affordability": {},
    "price_risk": {},
    "trending": {}
  },
  "quality": {
    "layer": "clean|flagged|mixed|unknown",
    "caveats": [
      "Retail formal online only; not national CPI.",
      "Not informal market coverage."
    ]
  },
  "citations": {
    "methodology_ref": "docs/methodology.md | GTM methodology-shelf-inflation",
    "cite_snippet": "CLI Market. Shelf prices / shelf inflation — retail formal online. Corte: [as_of], país: [CC]."
  },
  "disclaimers": [
    "Inflación y precios observados desde góndola online (retail formal). No reemplaza IPC oficial (INEI, DANE, INDEC, IBGE, etc.).",
    "Este paquete no constituye scouting tecnológico ni revisión de literatura."
  ]
}
```

### 4.4 Campos mínimos para una ficha usable (MVP)

Obligatorios en la primera integración:

| Campo | Obligatorio MVP |
|-------|-----------------|
| `schema_version`, `as_of`, `request.country`, `request.query` | Sí |
| `assortment[]` con al menos `name`, `store`, `price`, `currency` | Sí (puede ser `[]` si no hay cobertura; documentar en `coverage.notes`) |
| `price_summary` | Sí (nulls permitidos si `n=0`) |
| `quality.caveats` + `disclaimers` | Sí |
| `signals.*` | Recomendado; omitir clave si la tool falló o el tier no alcanza |
| `consumer_ref.pit_run_id` | Sí cuando el caller es PIT |
| `package_id`, `generated_by.tools_used` | Sí para trazabilidad |

### 4.5 Cómo armarlo hoy (sin endpoint dedicado)

Orquestación manual o agent skill, en este orden (reutilizar resultados; no duplicar calls idénticas):

1. `market_discover` — acotar `line` / retailers del `country`
2. `market_search` / `market_compare` — surtido y precios (query normalizada a términos de góndola)
3. `market_intel_brief` + `market_inflation` + `market_scores` — señales agregadas
4. `market_affordability` — si el caso es alimentos / canasta / pricing al consumidor
5. `market_stats` — freshness / cobertura cuando exista
6. Opcional: `market_price_risk`, `market_trending` si hay que separar promo de señal
7. Opcional: `market_export` / methods export skill si el consumidor es data room o academic

Skills de apoyo en el ecosistema: nowcast, cpi-bridge, methods-export, affordability (no sustituyen el package; lo enriquecen en workflows largos).

### 4.5.1 Mocks e integración delgada (implementado)

| Pieza | Path |
|-------|------|
| Builder + CLI | `ops/market_evidence_package.py` |
| Fixture package | `ops/pit_integration/mocks/market_evidence_package.example.json` |
| Stub ficha PIT | `ops/pit_integration/mocks/pit_ficha_stub.example.json` |
| Ejemplo merge | `ops/pit_integration/mocks/ficha_merged.example.json` |
| Runbook corto | `ops/pit_integration/README.md` |
| Tests | `tests/test_market_evidence_package.py` |
| Salidas locales | `ops/generated/pit/last-*.json` / `.md` |

**Mock (sin red):**

```bash
python ops/market_evidence_package.py --mode mock --merge-ficha
python -m pytest tests/test_market_evidence_package.py -q
```

**Live (API CLI Market → package + ficha merge):**

```bash
export MARKET_API_URL=https://cli-market-api.fly.dev
export MARKET_API_TOKEN=...   # recomendado para /v1/intel/*

python ops/market_evidence_package.py --mode live \
  --query "arandanos" --country PE \
  --pit-run-id demo-run-1 --merge-ficha
```

Qué hace el merge delgado:

1. Construye el Market Evidence Package (mock o live).
2. Carga un stub de ficha estilo PIT (`segment`, `stage`, `science_summary`, …).
3. Adjunta `market_evidence` + `market_headline` + `market_evidence_package_id`.
4. Emite JSON y markdown para demo / enganche a PDF de PIT.

No llama a PIT todavía: cuando `POST .../ficha` o el report estén disponibles con auth, el consumidor solo debe inyectar el bloque `market_evidence` (o el `package_id` + snapshot).

### 4.6 Endpoint futuro (opcional — fase 4)

Solo si hay demanda medible de fichas/data rooms:

- Nombre tentativo: `POST /v1/intel/market-evidence` o tool MCP `market_category_evidence`
- Body ≈ `request` del schema
- Response ≈ package completo
- **No** incluye literature, HS enrich ni PDF de PIT

Hasta entonces el schema de esta sección es la fuente de verdad para mocks e integración.

## 5. Gaps y no-gaps

| ID | Gap | ¿Tool MCP nueva en CLI Market? | Acción |
|----|-----|--------------------------------|--------|
| G1 | PIT no tiene contrato fijo para “pedir góndola” | No prioritario | Usar este schema; mock o skill primero |
| G2 | Ficha PIT sin precios reales | No | PIT/agente llama CLI Market al generar ficha |
| G3 | Trazabilidad `run_id` ↔ snapshot de precios | Opcional | `consumer_ref.pit_run_id` + `as_of` en package |
| G4 | Auth dual | No | SSO/keys documentadas; tiers independientes al inicio |
| G5 | “Una tool papers + precios” | **Evitar** | Orquestación, no primitiva única en MCP commerce |

**No son gaps de CLI Market:** literature search, HS scouting, enrich domains científicos, PDF tech-intel, lifecycle de research-run.

## 6. Ownership

| Decisión | Owner |
|----------|--------|
| Primitivas de papers / tech | PIT |
| Primitivas de góndola / precios | CLI Market |
| Schema del Market Evidence Package | Contrato compartido (este doc); implementación de proveedor → CLI Market |
| Ficha final al usuario | PIT (o app encima), consumiendo el package |
| GTM / claims | No mezclar `pip install` commerce con scouting científico en el mismo post sin dejar claro el spoke (hub CLI Market / spoke research) |

## 7. Roadmap de producto

| Fase | Qué | Criterio de done |
|------|-----|------------------|
| **0** | Límites de dominio alineados (este doc) | Equipos usan la matriz para triage de tickets — **hecho** |
| **1** | Schema v0.1 del package + mapping query PIT → params CLI Market | Mock fixture + `validate_package` — **hecho** (`ops/pit_integration/`) |
| **2** | Integración delgada: ficha stub + bloque mercado (live opcional) | `ops/market_evidence_package.py --merge-ficha` — **hecho** (PIT ficha real = siguiente cuando API agents esté up) |
| **3** | Trazabilidad: `as_of` + `pit_run_id` en metadata del run | Auditoría “este precio salió de este corte” en el lado PIT |
| **4** | Solo con demanda: tool/API `market_category_evidence` o methods en API formal | Usos reales en fichas / data rooms |

## 8. Disclaimers canónicos (copiar en package y ficha)

1. Precios e inflación observados desde **góndola online (retail formal)**. No reemplazan el IPC oficial del instituto nacional.
2. El Market Evidence Package **no** es scouting tecnológico ni revisión de literatura; eso es dominio PIT.
3. Cobertura incompleta o `assortment: []` debe reportarse como gap de datos, no como “precio cero” ni “sin mercado”.

## 9. Referencias

| Recurso | Ubicación |
|---------|-----------|
| PIT OpenAPI / Swagger | `https://cli-market-pit-backend.fly.dev/docs` |
| CLI Market prod API | `https://cli-market-api.fly.dev/docs` |
| Metodología shelf / indicadores | `docs/methodology.md` |
| Casos ERP / ficha innovación (solo góndola) | `Casos_de_uso_CLI_Market_ERP_agentes.md` |
| Orchestrator | `docs/🧠_intelligence_core/orchestrator-contract.md` |
| Tools catalog (snapshot) | `docs/reports/TOOLS_CATALOG_COMPLETO.txt` |
| Academic / methods (skill) | ecosystem skill `cli-market-methods-export` |

---

**Changelog**

| Fecha | Cambio |
|-------|--------|
| 2026-07-29 | v0.1 — matriz PIT↔CLI Market, ownership, schema Market Evidence Package, roadmap |
| 2026-07-29 | v0.2 — mocks, CLI `market_evidence_package.py`, merge ficha, tests, runbook `ops/pit_integration/` |
