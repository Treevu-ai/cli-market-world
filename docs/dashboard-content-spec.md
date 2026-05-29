# Especificación de contenido — Dashboard Data Moat

Documento de producto alineado con la implementación en código. La fuente de verdad en runtime es **`GET /dashboard/data` → `dashboard_view`** (`dashboard_view_model.py`). Este archivo describe copy, reglas de calidad y mapeo de campos.

**Versión de spec:** `dashboard_view.spec_version` (actualmente `1.0`)  
**Idioma:** español (panel público)  
**Glosario técnico:** `metric_glossary` (tooltips extendidos)

---

## Arquitectura

```
GET /dashboard/data
├── kpis, canasta_basica, marketing_spreads, …   ← datos crudos / analíticos
├── metric_glossary                              ← definiciones por métrica
├── moat_guide                                   ← capas inventario/frescura/ops
└── dashboard_view                               ← copy render-ready (6 bloques)
```

**Consumidores:** HTML (`/dashboard`), landing React, agentes MCP, reporting LinkedIn.

**Regla:** el frontend no debe re-derivar copy de producto; debe leer `dashboard_view.blocks.*`.

---

## Matriz de estados

| Estado | Cuándo | Copy / UI |
|--------|--------|-----------|
| `hero.state = ok` | `fresh_24h_pct ≥ 80`, `moat_age_hours < 8`, collector ok, freshness `fresh` | 🟢 Sistema al día |
| `hero.state = partial` | mezcla de señales | 🟡 Actualización parcial |
| `hero.state = stale` | `moat_age_hours ≥ 24` o refresh 24h = 0 con inventario > 0 | 🔴 Datos envejeciendo |
| `canasta.stores[].comparable = false` | `items_found < 6` (60%) | "Comparación parcial — faltan productos"; ocultar total |
| `price_spreads.state = empty` | `marketing_spreads` vacío | empty state en bloque 4 |
| `inflation.state = measuring` | `avg_before = 0` en todas las filas o sin movers | caja "⏳ Midiendo…" |
| `ops.collapsed_default` | siempre | Bloque 6 colapsado en UI futura |

---

## BLOQUE 1 — El titular (`dashboard_view.blocks.hero`)

**Propósito:** entender el producto en 10 segundos.

| Elemento | Copy literal | Origen JSON |
|----------|--------------|-------------|
| H1 | CLI Market · Precios reales, verificados todos los días | fijo |
| Subtítulo | Seguimos los precios de [N] productos en [T] tiendas de [P] países. Último precio capturado: hace [X]. | `kpis.total_indexed`, `kpis.stores_indexed`, `len(by_country)`, `kpis.moat_age_hours` → `_fmt_age_es()` |
| Sello 1 | [N]% de los precios son de hoy | `kpis.fresh_24h_pct` · tooltip: `tooltips.freshness` |
| Sello 2 | El dato más reciente hace [X] | `kpis.moat_age_hours` |
| Sello 3 | 🟢/🟡/🔴 + etiqueta | `_global_system_status()` |

**Implementación:** `sticky: true` en JSON (CSS `.hero-panel` en HTML). No mostrar siglas al usuario en este bloque.

---

## BLOQUE 2 — Por qué esto vale (`blocks.moat_narrative`)

**Propósito:** narrativa defensiva (inversores / prensa).

| Elemento | Copy | Origen |
|----------|------|--------|
| H2 | Por qué estos datos son difíciles de copiar | fijo |
| Intro | 3 frases (prosa en spec original) | fijo en `intro` |
| Pilar volumen | [N] precios ya guardados | `kpis.total_indexed` |
| Pilar cobertura | [T] tiendas en [P] países | `kpis.stores_indexed` + `by_country` |
| Pilar frescura | [N]% renovado en 24h | `kpis.fresh_24h_pct` |
| Gráfico crecimiento | "El foso se hace más profundo cada día" | `growth_chart.state = placeholder` — **fase 2** (`inventory_daily[]`) |

---

## BLOQUE 3 — Canasta básica (`blocks.canasta`)

**Propósito:** sección más humana; alta jerarquía visual.

| Elemento | Copy | Origen |
|----------|------|--------|
| H2 | La canasta básica, tienda por tienda | fijo |
| Subtítulo | Cuánto costaría una lista de 10 productos esenciales… | fijo |
| Regla calidad | Solo comparamos totales entre tiendas con completitud similar… | `quality_note` |
| Fila tienda | [8] de 10 productos · total [MONEDA X] | `canasta_basica` → enriquecido en view model |
| Advertencia | Comparación parcial — faltan productos | si `items < 6` |
| Dónde conviene | Supermercados → más barato en Metro | `cheapest_by_line` |

**Orden:** completitud desc → total asc (solo si `comparable`).

**Nota backend:** hoy `canasta_basica` solo incluye tiendas con ≥3 ítems; ampliar a todas las tiendas es mejora futura.

---

## BLOQUE 4 — Diferencias verificadas (`blocks.price_spreads`)

**Propósito:** ahorro entendible sin jerga.

| Elemento | Copy | Origen |
|----------|------|--------|
| H2 | El mismo producto, precios muy distintos | fijo |
| Fila ítem | [Producto] cuesta hasta [2.6] veces más… | **`marketing_spreads` ONLY** |
| Cobertura | comparado en [3] tiendas | `marketing_spreads[].stores` |
| Regla | Excluimos automáticamente precios sospechosos… | `quality_note` |

**NO usar:** `dispersion`, `canasta_spreads` para copy público.

**Umbral actual:** canasta ≥ `analytics_meta.marketing_canasta_min_spread` (2.5x) · farmacia ≥10x.

---

## BLOQUE 5 — Inflación (`blocks.inflation`)

| Estado | UI |
|--------|-----|
| `measuring: true` | Caja "⏳ Midiendo. Necesitamos una segunda captura…" + ETA |
| `measuring: false` | Filas `{line} ({currency}): +X% esta semana` desde `inflation` |

**Detección measuring:** todos `avg_before = 0` o sin `top_risers`/`top_fallers`.

**Nunca** mostrar 0% como dato real.

---

## BLOQUE 6 — Ops (`blocks.ops`)

Colapsado por defecto (`collapsed_default: true`).

| Subsección | Origen crudo |
|------------|--------------|
| Estado de tiendas | `store_health` |
| Fiabilidad del collector | `collector`, `collector_history` |
| Frescura por tienda | `freshness` |
| Alertas de calidad | `top_discounts` donde `discount_pct ≥ 90` |
| Valores atípicos | `outliers` |
| Brechas de cobertura | gaps derivados de `line_country_matrix` |

Tablas analíticas crudas (`dispersion`, `canasta_spreads`) viven en `ops.raw_analytics` para el equipo.

---

## Reglas transversales

**Tooltips (`dashboard_view.tooltips`):**

- Frescura → `tooltips.freshness`
- Cobertura → ver `metric_glossary.sections.coverage`
- Spread → `tooltips.spread`
- Snapshot → `tooltips.snapshot`

**Reemplazos de idioma (UI):**

| Inglés (legacy) | Español |
|-----------------|---------|
| market compare | Comparar precios |
| market basket | Canasta básica |
| Price Movers | Qué subió y qué bajó |
| Store Reliability | Fiabilidad de tiendas |
| Line × Country | Cobertura por país |

**Pie de página:** `dashboard_view.footer_stamp`

**Jerarquía lectura (escritorio):** bloques 1–3 sin scroll · 4–5 un scroll · 6 colapsado.

---

## Ejemplo JSON (recortado)

```json
{
  "dashboard_view": {
    "spec_version": "1.0",
    "locale": "es",
    "footer_stamp": "Actualizado el 2026-05-29 a las 12:00 UTC · Frescura 97%",
    "blocks": {
      "hero": {
        "title": "CLI Market · Precios reales, verificados todos los días",
        "subtitle": "Seguimos los precios de 38.464 productos…",
        "trust_badges": […],
        "system_status": { "state": "ok", "icon": "🟢", "label": "Sistema al día" }
      },
      "canasta": {
        "stores": [
          {
            "store_name": "Wong",
            "completeness_label": "8 de 10 productos",
            "comparable": true,
            "total_label": "PEN 435.20"
          }
        ]
      },
      "price_spreads": {
        "data_rule": "marketing_spreads ONLY (not dispersion)",
        "items": [{ "copy": "Aceite… cuesta hasta 2.6 veces más…" }]
      },
      "inflation": { "state": "measuring", "measuring_copy": "⏳ Midiendo…" }
    },
    "reading_order": ["hero", "moat_narrative", "canasta", "price_spreads", "inflation", "ops"]
  }
}
```

---

## Archivos relacionados

| Archivo | Rol |
|---------|-----|
| `dashboard_view_model.py` | Genera `dashboard_view` |
| `dashboard_glossary.py` | Tooltips y definiciones por métrica |
| `routers/dashboard.py` | Expone JSON + HTML público |
| `docs/data-moat-reporting.md` | Gates LinkedIn / reporting externo |
| `tests/test_dashboard_view_model.py` | Tests del view model |

---

## Fase 2 (pendiente)

- [ ] Serie `inventory_daily[]` para gráfico de crecimiento del moat
- [ ] Canasta: incluir tiendas con &lt;3 ítems con badge parcial
- [ ] Bloque 6 colapsable en React con `<details>`
- [ ] Insignia "precio excluido" enlazando alertas → bloques 3–4
