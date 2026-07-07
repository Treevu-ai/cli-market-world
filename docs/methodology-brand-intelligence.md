---
title: CLI Market Brand Intelligence — Metodología (dispersion_score y desvío de PVP)
tags:
  - intelligence
  - methodology
  - brand-intelligence
status: active
updated: 2026-07-06
version: 1.0
related:
  - docs/methodology.md
  - docs/prd-brand-intelligence-v1.md
---

# Metodología CLI Market Brand Intelligence

Documento público de 1 página, citable por el analista que reciba el reporte mensual PDF de
Brand Intelligence. Complementa la metodología general de indicadores
(`docs/methodology.md`), específico a las dos métricas propias de este producto:
`dispersion_score` y desvío vs. PVP sugerido.

**Principio rector:** CLI Market mide precios observados en retail online indexado, con
frecuencia de refresh de horas (no semanas). No mide ventas, volumen, ni cobertura offline.

---

## 1. `dispersion_score` — coeficiente de variación cross-tienda

Para cada SKU (identificado por `product_id`), sobre el conjunto de precios vigentes
observados en las tiendas indexadas de un país:

```
dispersion_score = σ(precios) / μ(precios)
```

- `σ` = desviación estándar poblacional de los precios observados para ese SKU
- `μ` = media aritmética de esos mismos precios
- Expresado como razón (p. ej. `0.08` = 8% de dispersión), no como porcentaje ×100 —
  a diferencia de la métrica general de "Price Dispersion" en `docs/methodology.md` §5, que sí
  multiplica por 100. Al leer el campo `dispersion_score` en la API, multiplicar por 100 para
  obtener el porcentaje equivalente.
- Requiere al menos 2 tiendas con precio vigente para ese SKU; si hay menos, el campo es `null`.

## 2. Desvío vs. PVP sugerido

El PVP (precio de venta al público) sugerido **no lo calcula CLI Market** — es un dato
declarado por la marca al registrar su configuración (`POST /v1/brand-monitor/config`,
campo `sku_pvps`). Sobre ese valor declarado:

```
desvío_pct = (precio_observado − PVP_sugerido) / PVP_sugerido × 100
```

Umbrales de alerta:

| Umbral | Etiqueta | Lectura |
|---|---|---|
| `desvío_pct > +5%` | `above_pvp` | Precio por encima del sugerido — riesgo de imagen de marca |
| `desvío_pct < −15%` | `far_below_pvp` | Precio muy por debajo — posible guerra de precios que erosiona margen de canal |
| Email automático | — | Se dispara cuando `\|desvío_pct\| > 10%` (umbral distinto y más estricto que el de la UI/API, pensado para no saturar la bandeja con desvíos leves que ya se ven en el dashboard) |

## 3. Qué NO mide este producto

- No reemplaza una auditoría de campo en punto de venta físico — solo cubre retail digital
  indexado por CLI Market.
- No incluye canal offline (tiendas físicas, promotoras) ni datos de sell-out/volumen vendido.
- El PVP es un insumo declarado por la marca, no un cálculo propio — su precisión depende de
  que la marca lo mantenga actualizado.
- `dispersion_score` no distingue causa (promo legítima vs. desvío no autorizado) — es un
  indicador de atención, no un veredicto.

## Referencias

- Metodología general de indicadores: `docs/methodology.md` (RPV, IPC, BSI, Price Dispersion
  general, Promo Intensity, Coverage & Freshness).
- PRD del producto: `docs/prd-brand-intelligence-v1.md`.
