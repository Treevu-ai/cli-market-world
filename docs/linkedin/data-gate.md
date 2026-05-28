---
title: LinkedIn Data Gate — Semana 2
tags:
  - linkedin
  - metrics
  - gate
hub: "[[GTM-Hub]]"
date: 2026-05-28
status: active
---

# LinkedIn Data Gate — Antes de publicar días 8–14

**Regla:** No publicar posts de "data stories" sin cifras verificables en esta nota o en [[metrics/price-pulse-YYYY-WW]].

## Fuente de verdad

```bash
curl -sS https://cli-market-production.up.railway.app/dashboard/data | python3 -m json.tool
```

Export semanal: `python3 ops/monday.py` → `docs/metrics/price-pulse-YYYY-WW.md`

## Snapshot verificado — 2026-05-28

| Métrica | Valor | OK para LI? |
|---------|-------|-------------|
| Total snapshots (24h) | **8,064** | ✅ |
| Precios indexados (price-pulse) | **8,231** | ✅ |
| Active stores (24h) | **28** | ✅ (no decir 30 sin aclarar) |
| Total catalog stores | **30** | ✅ (falabella_co off hasta token Magento) |
| Healthy stores (lifetime) | **16** | ⚠️ solo ops — ver [[data-moat-strategy]] |
| Store success % (lifetime) | **51.6%** | ❌ no usar en marketing |
| **coverage_7d_pct** (post-deploy) | ver `moat_summary` | ✅ gate semana 2 |
| Collector runs | **173** | ✅ interno |

### Por país (snapshots 24h)

| País | Precios | Tiendas |
|------|---------|---------|
| AR | 3,809 | 8 |
| PE | 3,138 | 4 |
| BR | 3,029 | 7 |
| MX | (ver API) | — |

### Por línea

| Línea | Precios | Avg price |
|-------|---------|-----------|
| supermercados | 8,572 | — |
| farmacias | 763 | — |
| electro | 589 | — |

## Gate checklist (semana 2)

- [ ] **Moat coverage 7d** ≥ **80%** (`moat_summary.coverage_7d_pct`) — gate principal
- [ ] Lifetime `store_success_pct` — solo ops, **no marketing**
- [ ] Cifra `[N]` en Day 07 reemplazada con snapshot del día
- [ ] Claims de inflación (% arroz, canasta) respaldados por query exportable
- [ ] No implicar índice oficial INEI/INDEC — usar "según nuestro collector"
- [ ] Legal review en días 8–10 (variación de precios)

Ver estrategia completa: [[data-moat-strategy]]

## Posts bloqueados / condicionales

| Día | Claim del calendario | Estado | Acción |
|-----|---------------------|--------|--------|
| 8 | Arroz +34% Lima | ⚠️ ILUSTRATIVO | Publicar solo tras query `market_compare "arroz" --country PE` exportada |
| 9 | Canasta S/147–182 | ⚠️ ILUSTRATIVO | Usar `market_basket` con items verificados |
| 10 | Inflación real 8h | ✅ OK | Usar 8,064 snapshots + refresh 8h |
| 11 | Motorola/Electrolux counts | ⚠️ | Verificar por tienda en dashboard |
| 14 | 12K precios insights | ✅ OK | Usar ~8K+ con fecha |

## Query reproducible (guardar output en metrics/)

```bash
# Comparar arroz PE — guardar JSON para Day 8
market login
market compare "arroz" --country PE --json > docs/metrics/query-arroz-pe.json

# Canasta básica — Day 9
market basket --items '[{"name":"arroz","qty":1},{"name":"leche","qty":2}]' --json
```

## Decisión 2026-05-28

**Semana 2 LinkedIn:** publicar días 8–14 con copy **qualitativo** + cifras agregadas verificadas (8K+ precios, 28 retailers activos, refresh 8h). **Posponer** claims de % específicos por producto hasta collector ≥80%.

[[GTM-Hub]] · [[metrics/price-pulse-2026-W22]] · [[linkedin/00-Index]]
