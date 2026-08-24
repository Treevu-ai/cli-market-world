---
title: PRD — Góndola Digital v0 (asesor de surtido y precio online)
tags:
  - product
  - prd
  - intelligence
  - category
  - digital-shelf
status: Draft — In Review
owner: Ricardo Cuba
updated: 2026-08-24
repos: cli-market-core, cli-market-world
depends_on:
  - docs/prd-brand-intelligence-v1.md
  - docs/gtm/intelligence-pilot-one-pager.md
  - docs/INDECOPI_ARCHITECTURE_ANALYSIS.md
related_backlog: docs/backlog-digital-gondola.md
---

# PRD: Góndola Digital v0

**Capa comercial:** Intelligence (Puerta C) — *add-on* de categoría, no SKU Nielsen.  
**Duración de build v0:** 2–3 sprints. **Prioridad:** P1 (empaquetar lo que ya existe; no abrir un moat nuevo).

## Press release (antes del PRD)

> CLI Market lanza **Góndola Digital**: un asesor que le dice a trade, category y pricing qué SKU falta en qué cadena, dónde el precio se desvió del PVP y dónde hay un hueco de oferta — con evidencia de góndola formal online, cada pocas horas.
>
> No es NielsenIQ. No mueve caras en el pasillo. Le dice, con dato verificable, **qué listar, qué repriciar y qué no tocar** en el canal digital de supermercados LATAM.

Si esa frase no convence a un gerente de trade en 20 segundos, el producto no está listo. El valor no es “IA de góndola”; es **una lista de acciones con evidencia**.

---

## 1. Problem Statement

Los equipos de **category / trade / pricing** en CPG y en cadenas deciden surtido y precio con tres insumos malos:

1. **Panel Nielsen / auditoría en tienda** — caro ($30–80K/año en Brand Intel PRD), mensual, 3–4 semanas de rezago, fuerte en espacio físico y sell-out, débil en e-commerce LATAM.
2. **Excel del junior + screenshots** — no escala, no comparable, se pudre en 24 h.
3. **Nada** — marcas challenger y agencias de trade no pagan Nielsen y operan a ciegas en góndola digital.

CLI Market **ya observa** esa góndola (catálogos formales, precio, promo, cobertura). Lo que **no entrega** es un producto de decisión: hoy el usuario encadena `market_search` + `market_compare` + `market_coverage_matrix` + skill de reporte y se inventa las acciones.

**Quién lo siente, con qué frecuencia, a qué costo:**

| Persona | Frecuencia | Costo de no resolverlo |
|---------|------------|------------------------|
| Category / trade (marca) | Semanal | SKU no listado en una cadena 2–4 semanas; promo del competidor sin respuesta |
| Pricing | Diario / semanal | PVP violado en digital; guerra de precios invisible |
| Category del retailer | Mensual | Huecos de tier / marca en el propio e-comm vs competencia |
| Agencia de trade | Por pitch / QBR | No tiene insumo propio; re-vende Nielsen o no cierra |

**Evidencia (honestidad):**

- **User research:** n=0 entrevistas específicas de este SKU. Se infiere de ICP de Brand Intel, outreach Intelligence (consultoras / NielsenIQ como competidor de *datos*, no de espacio) y del gap explícito en análisis INDECOPI: *no hay datos de espacio en góndola*.
- **Behavioral:** las tools de cobertura, compare e intel brief existen; no hay endpoint de *recomendación de surtido/precio*. El skill `cli-market-intel-report` ya pide “3–5 bullets accionables” — es un procedimiento de agente, no un producto.
- **Competitive:** NielsenIQ Optimize / Spaceman = POS + planograma + elasticidad de espacio. Ese tablero **no** es el nuestro.
- **Confianza en el problema:** ~65%. El dolor de “no veo la góndola digital” está documentado. El dolor de “quiero que me armen el planograma” es de otro comprador y **no** lo atacamos.

**Costo de no hacer esto:** sales seguirá escuchando “¿son como Nielsen?” y o bien **sobre-promete espacio físico** (riesgo legal/reputacional) o bien **deja el dinero en la mesa** del comprador que sí pagaría $500–800/mes por cobertura + precio + acciones.

---

## 2. Goals & Success Metrics

North star de este SKU: **acciones aceptadas**, no reportes generados.

| Goal | Metric | Baseline | Target | Window |
|------|--------|----------|--------|--------|
| Valor percibido en piloto | % de recomendaciones v0 marcadas “útil / la vamos a ejecutar” por el cliente | 0 | ≥40% de las acciones mostradas | 30 días, n≥3 pilotos |
| Tiempo a insight | Minutos desde “categoría + país + portafolio” hasta 5 acciones con evidencia | Manual 45–90 min (skill) | ≤3 min p50; ≤8 min p95 | launch |
| Honestidad | Payloads / PDFs con disclaimer de góndola digital y **cero** claims de facings / share of shelf / planograma | n/a | 100% (lint + review) | launch y continuo |
| Pipeline | Pilotos Intelligence/Brand que incluyen Góndola Digital | 0 | ≥3 conversaciones con SOW firmado o piloto activo | 60 días |
| Calidad de dato | % de acciones `LIST`/`PRICE` con ≥1 snapshot citables (store, price, queried_at) | n/a | 100% | launch |
| No canibalizar | Mix de mensaje: este SKU no se vende con `pip install` ni con Procure en el mismo pitch | n/a | 0 piezas mezcladas | continuo |

**No es éxito:** “nos parece tan completo como Nielsen”. Eso es un fail de posicionamiento.

---

## 3. Non-Goals (v0 y v1)

**v0 no es y no será:**

- Planograma, facings, share of shelf físico, adyacencias, altura de góndola.
- Elasticidad de espacio (“si quito 2 caras, vendo −X%”).
- Market share / sell-out / paneles de hogares.
- Garantía legal tipo Nielsen o “medición auditada de mercado”.
- Auto-ejecutar cambios en el surtido del retailer.
- Canal tradicional, ferias, mayorista informal (fuera del moat).
- Forecast de demanda.
- UI consumer / Procure Copilot.

**v1 tampoco** abre POS ni planograma. Eso es **Later**, y solo con dato del cliente o alianza con cadena.

**Kill list (no entra al backlog disfrazado):**

- Inferir share of shelf desde conteo de SKUs en el crawler.
- Llamar “optimización de góndola” en copy público sin el calificativo **digital / online**.
- Precio tipo Nielsen ($30K+) para un producto que no entrega POS.

---

## 4. Personas & stories

**Primaria — Elena, Gerente de Trade / Category (marca CPG, PE o CO)**  
Presupuesto insuficiente para Nielsen. Cada lunes arma un Excel de “estoy en Wong/Metro/Vea”. Quiere 5 acciones, no un dashboard de 40 charts.

**Secundaria — Diego, analista de pricing**  
Le importa PVP vs góndola digital y promo del competidor. Brand Intel cubre *su marca*; Góndola Digital cubre *la categoría* (huecos de listado y de tier).

**Terciaria — Agencia de trade**  
Quiere un one-pager para el QBR del cliente. Ciclo de venta más corto que una multinacional (misma puerta de entrada que Brand Intel).

### Story 1 — Matriz de cobertura de portafolio

Como Elena, quiero ver mis SKUs × retailers digitales del país, con estado listado / ausente / stale, para saber dónde empujar al Key Account.

**Acceptance:**
- [ ] Given país + lista de SKUs o queries de marca, when corre Góndola Digital, then cada celda es `listed` | `missing` | `stale` | `insufficient_data` con `queried_at`.
- [ ] Given un retailer en catálogo sin snapshot &lt; SLA de frescura, when se muestra, then es `stale` o `insufficient_data`, nunca `missing` silencioso.
- [ ] Given copy/UI, when se renderiza, then no aparece “share of shelf” ni “facings”.

### Story 2 — Acciones de precio y promo

Como Diego, quiero ver desvío vs PVP (si lo cargué) y promo relativa vs competidores declarados, para decidir si repricio o no.

**Acceptance:**
- [ ] Given PVP por SKU, when precio observado &gt; PVP×1.05 o &lt; PVP×0.85 (mismos umbrales que Brand Intel), then acción `PRICE` con evidencia.
- [ ] Given sin PVP, when hay spread cross-retailer, then se reporta landscape; no se inventa un PVP.
- [ ] Given promo en competidor y no en el SKU propio en el mismo store, then acción `PROMO` marcada hipótesis, no hecho de sell-out.

### Story 3 — Whitespace de oferta (categoría)

Como Elena, quiero huecos de **tier de precio** y de **listado** en la categoría (no solo mis SKUs), para proponer un SKU o un precio de entrada.

**Acceptance:**
- [ ] Given categoría + país, when hay un gap entre p20 y p80 de precio normalizado sin SKU propio, then acción `LIST` o `HOLD` con atractivo alto/medio/bajo **solo** si hay evidencia de cobertura.
- [ ] Given &lt;N retailers o &lt;M SKUs en la subcategoría, when se evalúa whitespace, then atractivo = bajo o `insufficient_data` — no “oportunidad enorme”.
- [ ] Given canal informal, when el usuario lo pide, then se niega tamaño de mercado; se puede apuntar a `market_informal_signal` como honestidad de cobertura.

### Story 4 — Contrato de recomendación (anti-alucinación)

Como un agente MCP o un analista, quiero que cada acción cite snapshots, para no llevar un invento al comité.

**Acceptance:**
- [ ] Cada acción tiene `type`, `sku`/`query`, `retailers[]`, `evidence[]` (`store`, `price`, `queried_at`, `url` si existe), `rationale`, `confidence`.
- [ ] El payload top-level incluye `scope: digital_shelf_formal` y `not_included: [physical_space, pos, planogram, market_share]`.
- [ ] Tests de contrato fallan si una rec se emite sin `evidence` (excepto `HOLD`/`insufficient_data`).

---

## 5. Solution Overview

**Góndola Digital v0** es un *composer* sobre el moat actual. No scrapeamos pasillos. No compramos paneles.

```
Input: country, category/line, portfolio (SKUs o brand+queries), optional PVP, optional competitors
        ↓
Reuse: search, compare, coverage_matrix, price history, promo flags, intel brief
        ↓
Engine: DigitalShelfAdvisor (reglas determinísticas; LLM solo para redactar rationale grounded)
        ↓
Output: coverage grid + price landscape + 3–7 action cards + disclaimer
Surfaces: REST + MCP + PDF one-pager (v0.1) + dashboard Intelligence (v0.2)
```

**Decisiones de diseño:**

1. **Reglas primero, LLM segundo.** El tipo de acción y la evidencia se calculan en código. El modelo **no** puede inventar un `LIST` sin celda `missing`. Trade-off: copy menos “brillante”; cero alucinación de espacio físico.
2. **Add-on de Intelligence, no producto Nielsen.** Mismo comprador que el piloto $300–500/mes; ticket sugerido de add-on **$200–400/mes** extra o paquete categoría **$500–800/mes** (1 país × 1 categoría). Trade-off: no perseguimos el budget de space management del retailer en v0.
3. **Reutilizar Brand Intel para “mis SKUs”.** Góndola Digital aporta *categoría + cobertura + acciones*. No duplicar el dashboard de desvío PVP. Trade-off: v0 puede vivir sin Brand Intel shipped si el PVP se pasa en el request.
4. **Una categoría, un país, ≤8 subcategorías** (misma disciplina que el skill de intel report). Trade-off: no “snacks LATAM” en una corrida.

### Output canónico (v0)

```json
{
  "scope": "digital_shelf_formal",
  "country": "PE",
  "category": "leche_evaporada",
  "freshness_hours": 8,
  "not_included": ["physical_space", "facings", "planogram", "pos_share", "market_share"],
  "coverage": { "rows": ["sku:..."], "cols": ["wong", "metro"], "cells": [] },
  "landscape": { "unit": "PEN_per_L", "p20": 0, "p50": 0, "p80": 0 },
  "actions": [
    {
      "id": "act_01",
      "type": "LIST|PRICE|PROMO|HOLD",
      "priority": 1,
      "confidence": "ok|low|insufficient_data",
      "evidence": [],
      "rationale": "1-3 oraciones, solo hechos del evidence[]"
    }
  ]
}
```

Tipos de acción:

| Tipo | Significa | Nunca significa |
|------|-----------|-----------------|
| `LIST` | Empujar listado digital en retailer X | Poner 4 facings en el pasillo |
| `PRICE` | Revisar PVP / precio observado | Que el sell-out va a subir |
| `PROMO` | Hay asimetría promocional observada | Que la promo es efectiva |
| `HOLD` | Dato insuficiente o no hay gap material | “Todo está perfecto” |

### Superficies

| Superficie | v0 | Nota |
|------------|----|------|
| `GET/POST /v1/intel/gondola-advise` | Sí | World router; lógica en core si es pura sobre snapshots |
| MCP `market_gondola_advise` | Sí | **stdio + HTTP** (dos listas independientes) |
| CLI `market gondola` | Opcional v0.1 | Solo si reutiliza el mismo contrato JSON |
| PDF one-pager (email) | v0.1 | Máx. 2 páginas; mismo disclaimer |
| Dashboard `/intelligence/gondola` | v0.2 | No bloquear el contrato API |

### Pricing y anti-canibalización

| SKU | Promesa | Precio (piloto) |
|-----|---------|-----------------|
| Intelligence | Spreads, inflación, canasta, calidad | $300–500/mes |
| Brand Intel | Mis SKUs + competidores declarados + PVP | $500/mes por marca (PRD existente) |
| **Góndola Digital** | Cobertura × retailer + whitespace + acciones | **$500–800/mes** 1 país × 1 categoría, o +$200–400 sobre Intelligence |

No vender los tres como “el Nielsen completo”. Pitch: *Nielsen (si lo tienen) para espacio y sell-out; CLI Market para góndola digital cada pocas horas.*

---

## 6. Technical Considerations

**Build order:** core (contrato + engine + tests) → world (router, MCP HTTP, dashboard) → index no aplica.

**Reuse (no reinventar):**

| Pieza | Dónde |
|-------|--------|
| Snapshots, brand, category, store, discount | `price_snapshots` |
| Matriz de cobertura | `build_coverage_matrix` / `market_coverage_matrix` (hoy es línea×país; v0 necesita **SKU×store**) |
| Compare / search | APIs v1 existentes |
| Umbrales PVP | Brand Intel PRD (1.05 / 0.85) |
| Honestidad informal | `market_informal_signal` + skill intel-report |
| Capa clean/flagged/citable | piloto Intelligence |

**Nuevo:**

- Tabla o vista `gondola_advice_run` (run_id, inputs, payload, created_at) para que el piloto pueda decir “esta acción salió el lunes”.
- Engine `DigitalShelfAdvisor` con reglas + schema.
- Lint de copy: denylist `facing`, `facings`, `planograma`, `share of shelf`, `espacio lineal` en rationale generado.

**Dependencies:**

| Dep | Para qué | Riesgo |
|-----|----------|--------|
| Frescura del collector | Acciones `LIST` falsas si el crawler falló | Alto — mitigar con `stale` ≠ `missing` |
| Resolución de entidad (index) | Mismo SKU entre tiendas | Medio — degradar a query comparable, marcar `low` |
| Billing Intelligence | Gate Pro/Intelligence; core no enforza tier | Medio — `_pre_check_tier` en MCP HTTP |

**Riesgos:**

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Sales vende espacio físico | Alto | Alto | Disclaimer en payload, one-pager GTM, denylist |
| `missing` por crawler caído | Medio | Alto | SLA de frescura por store; no recomendar LIST si stale |
| LLM inventa atractivo de mercado | Medio | Alto | LLM no elige `type`; no cifras de TAM |
| Canibaliza Brand Intel | Medio | Medio | Góndola = categoría + cobertura; Brand = marca + PVP |
| Cliente pide POS “para que sea Nielsen” | Alto | — | Later explícito; no absorber scope en el piloto |

**Open questions (antes de dev, no bloquean el draft del PRD):**

- [ ] ¿El portafolio de v0 es lista de `product_id` internos o queries de marca? **Default:** queries + match a golden records; `product_id` opcional. Owner: producto + core. 
- [ ] ¿Quién paga el primer piloto: agencia de trade o marca challenger? **Default:** misma puerta que Brand Intel (agencia). Owner: GTM.
- [ ] ¿Dashboard en v0 o solo API+PDF? **Default:** API+MCP+PDF; dashboard v0.2. Owner: producto.

---

## 7. Launch Plan

| Phase | Audience | Success gate |
|-------|----------|----------------|
| Alpha interno | Equipo + 1 categoría PE (lácteos o arroz — alta cobertura del moat) | Contrato JSON estable; 0 claims físicos; p95 &lt; 8 min |
| Piloto cerrado | 2–3 agencias o marcas (mismo ICP Brand Intel) | ≥40% acciones “útiles”; 0 reclamos de “esto no es Nielsen” mal manejados (script de objeción listo) |
| GA | Add-on en landing Intelligence + SOW | Métricas de §2 en camino; copy GTM actualizado |

**Rollback:** feature flag `gondola_advise_enabled`; si freshness de la categoría piloto &lt; umbral o error rate &gt; 5%, apagar superficie pública y dejar API interna.

**GTM (objeción canónica):**

> “¿Optimizan la góndola como NielsenIQ?”  
> “Optimizamos **surtido y precio en góndola formal online**. Facings, planograma y sell-out siguen siendo Nielsen o el POS de la cadena. Somos el complemento de alta frecuencia, no el reemplazo.”

**Claims públicos:** solo data-gate + este PRD. No citar “share of shelf CLI Market”.

---

## 8. Appendix

- Brand Intel: `docs/prd-brand-intelligence-v1.md`
- Intelligence piloto: `docs/gtm/intelligence-pilot-one-pager.md`
- Gap espacio góndola: `docs/INDECOPI_ARCHITECTURE_ANALYSIS.md` §3.3
- Skill categoría: `.claude/skills/cli-market-intel-report/SKILL.md`
- Backlog: `docs/backlog-digital-gondola.md`
- GTM Hub: `docs/gtm/README.md`

**RICE (juicio, no analogía de usage):**

| Factor | Value | Notes |
|--------|-------|-------|
| Reach | ~ decenas de cuentas Intelligence/Brand en 2 trimestres, no miles de MAA | Comprador B2B, no PyPI |
| Impact | 2 | Desbloquea un no-compra (“¿son Nielsen?”) y un yes de categoría |
| Confidence | 50% | Sin entrevistas de este SKU |
| Effort | M (2–3 sprints) | Composer + SKU×store coverage + 2 superficies MCP |
| **RICE** | Medio — **build v0 scoped**, no platform |

**Recomendación:** **Build v0** como add-on Intelligence. **No** abrir POS/planograma. **No** esperar a Brand Intel GA para el contrato API (PVP opcional en el request).
