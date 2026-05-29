---
title: LinkedIn Data Gate — Semana 2
tags:
  - linkedin
  - metrics
  - gate
hub: "[[GTM-Hub]]"
date: 2026-05-29
status: active
---

# LinkedIn Data Gate — Antes de publicar días 8–14

**Regla:** No publicar posts de "data stories" sin cifras verificables en esta nota o en [[metrics/price-pulse-YYYY-WW]].

## Fuente de verdad

```bash
curl -sS https://cli-market-production.up.railway.app/dashboard/data | python3 -m json.tool
curl -sS https://cli-market-production.up.railway.app/health/db | python3 -m json.tool
```

Export semanal: `python3 ops/monday.py` → `docs/metrics/price-pulse-YYYY-WW.md`

## Snapshot verificado — 2026-05-29 ✅ GATE PASSED

| Métrica | Valor | OK para LI? |
|---------|-------|-------------|
| Precios indexados (moat) | **19,452** | ✅ |
| Refresh 24h | **8,392** | ✅ |
| Tiendas fresh 24h | **30** | ✅ |
| Tiendas con datos | **34** | ✅ |
| **coverage_7d_pct** | **94.4%** | ✅ gate semana 2 |
| Collector last run | **1,441** precios · 30/36 tiendas | ✅ |
| `price_snapshots_upsert_ready` | **true** | ✅ |
| Store success % (lifetime) | 55.6% | ❌ solo ops |
| Moat stale | **false** | ✅ |

### Por país (indexado)

| País | Precios | Tiendas |
|------|---------|---------|
| AR | 6,106 | 8 |
| BR | 4,979 | 11 |
| MX | 3,927 | 4 |
| PE | 3,157 | 4 |
| CO | 1,103 | 3 |

## Gate checklist (semana 2)

- [x] **Moat coverage 7d** ≥ **80%** — **94.4%**
- [x] Upsert Postgres operativo (`price_snapshots_upsert_ready: true`)
- [x] Refresh 24h > 0
- [ ] Cifra `[N]` en Day 07 → usar **8,392** (24h) o **19,452** (indexado)
- [x] Claims agregados 8K+ / 19K+ — OK
- [ ] Claims de inflación % por producto — posponer (sin serie 7–14d aún)
- [ ] No implicar INEI/INDEC — usar "según nuestro collector"

## Posts — estado de publicación

| Día | Tema | Estado | Cifras a usar |
|-----|------|--------|---------------|
| 7 | Semana 1 wrap | ✅ publicar | 8,392 fresh · 19,452 indexados · 30 fresh |
| 8 | Arroz PE variación | ✅ publicar | S/ 2.90–4.40+ · 8K+ fresh · ver [[metrics/query-arroz-pe.json]] |
| 9 | Canasta PE | ✅ cualitativo | multi-tienda · evitar S/147–182 |
| 10 | Collector 8h | ✅ publicar | 8,392 snapshots 24h · Railway + PG |
| 11 | Electro/hogar | ✅ publicar | 591 electro · 11 países/líneas |
| 12 | Top 10 carousel | ⚠️ | armar desde dashboard top_discounts |
| 13 | Retailers EN | ✅ | sin cifras duras |
| 14 | 3 insights | ✅ publicar | 19K+ indexados · 8K+ fresh |

## Query reproducible

```bash
# Day 8 — guardado en repo
curl -sS -X POST https://cli-market-production.up.railway.app/products/compare \
  -H 'Content-Type: application/json' \
  -d '{"query":"arroz","country":"PE","limit":20}' \
  > docs/metrics/query-arroz-pe.json
```

## Decisión 2026-05-29

**Semana 2 desbloqueada.** Publicar días 7–14 con cifras agregadas verificadas. Day 8: variación arroz PE con rango real, sin % inflación inventado. Day 9: cualitativo + demo basket, sin totales ficticios.

[[GTM-Hub]] · [[metrics/price-pulse-2026-W22]] · [[linkedin/00-Index]]
