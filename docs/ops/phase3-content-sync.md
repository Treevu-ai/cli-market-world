# Fase 3 — Consistencia de copy y sync de contenido

**Fecha:** 2026-05-30 · **Rama:** `cursor/phase3-content-sync-f414`

Continúa `docs/ops/phase2-db-split.md`. Alinea el copy de marketing al mensaje canónico y documenta el sync al repo de contenido privado.

---

## Mensaje canónico (fuente única)

Generado por `python3 ops/sync_market_stats.py` → `landing/lib/marketStats.ts`:

| Concepto | Valor |
|----------|-------|
| Retailers | **60 en catálogo · 30 verificados activos** |
| Plataformas | **3** (VTEX · Shopify · Magento) |
| Países | **8** (PE, AR, BR, MX, CO, CL, IT, FR) |
| MCP tools | **36** |
| Precios | **43,000+** (refresh 8h) |

Frase corta: *60 retailers (30 verificados) · 8 países · 3 plataformas · 36 herramientas MCP · 43,000+ precios.*

---

## Completado en esta fase

| # | Tarea | Archivos |
|---|-------|----------|
| 1 | GTM-Hub: tabla "Mensaje acordado" → canónico | `strategy/GTM-Hub.md` (era "36 verificados") |
| 2 | Calendario: 12,000 → 43,000+; stats recap | `calendar/linkedin-calendar.md` |
| 3 | Stat lines posts → "60 retailers (30 verificados)" | Day-01/04/09/13/15, repurpose-top5 |
| 4 | Outbound + strategy stat claims | `outbound/` y `strategy/outbound-sequences.md`, content/reddit |

Las menciones **narrativas** (p. ej. "comparó 30 retailers en 0.8s", "de 1 conector VTEX a 30 retailers") se mantienen: reflejan el set verificado usado en demos y la historia build-in-public.

---

## Dos sistemas de métricas — no confundir

1. **Product stats** (retailers, países, plataformas, label de precios): estables, vienen de `marketStats.ts`. Se editan a mano y se alinean al canónico.
2. **Price-pulse semanal** (`metrics/price-pulse-YYYY-WW.md`, cifras tipo 41,856 / 36,935): snapshot fechado, **regenerado por el pipeline**, no editar a mano.

> Los posts data-brag (Day-07/08/09/10/14, `data-gate.md`) usan cifras price-pulse. **Antes de publicar**, regenerar con el pipeline de métricas y no publicar cifras de >48h sin sincronizar (ver `linkedin/catch-up-plan.md`). El snapshot W22 (41K) queda como registro histórico.

---

## Sync al repo de contenido privado

El contenido GTM vive en el repo privado **`cli-market-content`** (no en este monorepo). El template fuente es `tools/content-repo-template/`.

Tras mergear esta fase, propagar al repo privado (acción local — requiere el repo presente):

```bash
# Inicializar / actualizar desde el template
CLI_MARKET_CONTENT_DIR=../cli-market-content python3 ops/init_content_repo.py --force

# Regenerar assets PNG de LinkedIn en el content repo
python3 ops/generate_all_linkedin_assets.py

# Estado / sync de campaña
python3 ops/slack_cli.py campaign status
python3 ops/slack_cli.py campaign sync
```

No se puede ejecutar desde el Cloud Agent (el repo privado no está montado aquí).

---

## Verificación

```bash
rg -n "13K|13,000|12,000" tools/content-repo-template/   # sin resultados de producto
rg -n "36 verificados" tools/content-repo-template/       # sin resultados
```

---

## Pendiente Fase 4+

| Item | Notas |
|------|-------|
| PayPal «Agotado» / live | Panel PayPal Business: pasar de sandbox a live + inventario (externo) |
| Regenerar price-pulse | Pipeline de métricas para data-brags (Day-07/08/09/10/14) |
| i18n landing | Unificar copy inline vs `translations.ts` |
| Checkout autónomo | Roadmap Build |
