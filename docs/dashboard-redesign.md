# Dashboard Data Moat — Rediseño por capas

Plan operativo alineado con `docs/dashboard-content-spec.md`. La fuente de verdad en runtime sigue siendo **`GET /dashboard/data` → `dashboard_view`**.

**Principio rector:** confianza verificable + acceso programático, estética terminal (sin marketing ni emojis en el panel).

---

## Diagnóstico (sin cambios)

- Buen inventario mal presentado (~43k precios, ~97% frescura).
- ~20 secciones del mismo peso, duplicados (canasta ×3, scraping ×2).
- Datos sucios al mismo nivel que insights verificados.
- El filtrado estricto no se visualiza como embudo.

---

## Arquitectura — 4 capas + fase 0

### Fase 0 · Confianza base ✅

| Tarea | Estado |
|-------|--------|
| `collector.status`: `healthy` → `ok` | ✅ `routers/dashboard.py`, `routers/health.py` |
| Dejar de renderizar tablas duplicadas | ✅ `dashboard_renderer.py` (un solo renderer) |
| Consumir `dashboard_view` + `metric_glossary` | ✅ |
| `ops.collapsed_default`, `hero.sticky` | ✅ `<details>` + CSS sticky |

### Capa 0 · Barra global (sticky) ✅

`COLLECTOR ok | FRESH 97.2% <24h | UTC HH:MM | [?] glosario`

- Bloque: `dashboard_view.blocks.global_bar`
- Sin emojis; estados `ok / partial / stale / dead / running / unknown`

### Capa 1 · Portada ✅

Tres tarjetas + bloque ACCESO con curls existentes.

- Bloque: `dashboard_view.blocks.portada`

### Capa 2 · Calidad y confianza ✅ (parcial)

Embudo `captured → flagged → clean → citable` + salud scraping unificada.

- JSON: `quality_funnel` en `/dashboard/data`
- Bloque: `dashboard_view.blocks.quality_funnel`
- **Pendiente Fase 4:** contadores de outlier a nivel DB (hoy: discount SQL + muestra outliers)

### Capa 3 · Exploración filtrable ✅ (parcial)

- Toggle **solo dato limpio** (default ON) — oculta `.dirty-section`
- Insights verificados arriba (`price_spreads` antes de canasta)
- Canasta unificada (una sección)
- Precios por categoría con moneda
- Brechas sospechosas colapsadas en `<details>`

- Bloque: `dashboard_view.blocks.exploration`

### Capa 4 · Activo temporal + ops

| Sección | Estado |
|---------|--------|
| Inflación medida en tienda | Bloqueado — `measuring` hasta 2ª captura |
| API `/v1/*` granular | Fase 3 |
| Mapa cobertura país × categoría | Fase 3–4 |
| Ops del collector | Colapsado en `blocks.ops` |

---

## Fases pendientes

### Fase 3 · API granular

- `GET /v1/quality/flagged`
- `GET /v1/sources/health`
- `GET /v1/prices?clean=1`
- `GET /v1/dispersion?clean=1`
- `GET /v1/basket` (snapshot-based, alineado con dashboard)

### Fase 4 · Activo temporal

- Gráfica inflación por tienda/país (post 2ª captura)
- `inventory_daily[]`
- Columna `confidence` en DB (opcional)

---

## Criterios de éxito

1. Visitante técnico entiende volumen, frescura y rigor en ~10 s (portada + embudo).
2. Embudo visible explica por qué se filtró.
3. Toggle ON → cero dispersion/sospechosos en viewport principal.
4. `curl` de ACCESO devuelve datos coherentes con pantalla.
5. Contadores auditables sin acceso a ops.

---

## Archivos

| Archivo | Rol |
|---------|-----|
| `dashboard_view_model.py` | Genera bloques render-ready (spec 1.1) |
| `dashboard_renderer.py` | HTML único desde view + glossary |
| `dashboard_quality.py` | `quality_funnel` counters |
| `routers/dashboard.py` | `/dashboard`, `/dashboard/data` |
| `tests/test_dashboard_*.py` | View model + funnel + regresión HTML |

---

## Riesgos

| Riesgo | Mitigación |
|--------|------------|
| Payload monolítico | Fase 3: endpoints paginados |
| Toggle sin flags DB | Suficiente Fase 2; Fase 4 confidence |
| Dos verdades canasta (DB vs live) | Etiquetar fuente / unificar Fase 3 |
| Drift spec ↔ HTML | Un solo renderer (`dashboard_renderer.py`) |
