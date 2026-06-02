## 📒 Calidad del Dato

### Funnel de calidad — 2026-06-02 (Semana 23)

| Etapa | Cantidad | % del total |
|-------|----------|-------------|
| Capturados (total_indexed) | 45.422 | 100% |
| Clean (ok) | 38.842 | 85.5% |
| Flagged: descuento >90% | 3.203 | 7.1% |
| Flagged: outlier 5x | 3.377 | 7.4% |
| Flagged: total | 6.580 | 14.5% |
| Citables (marketing-ready) | 3 | 0.007% |
| No normalizables (unidad no parseable) | 20.965 | 46.2% |

**Explicación de filtros:**

1. **Descuento >90%**: No es una promoción genuina en retail formal. Error de scraping (precio de lista mal capturado, producto descontinuado, 2x1 mal interpretado). Se marca suspect (2.186 registros). Excluido de canasta, compare y spreads.

2. **Outlier 5x mediana**: Precio >5x la mediana del grupo (subcategoría + moneda). Captura errores de unidad (caja vs unidad), productos premium mal categorizados, scrapes corruptos.

3. **No normalizables**: 20.965 productos (46.2%) con unidad no convertible a kg/L. Válidos para búsqueda, excluidos de canasta y spreads.

4. **Citables**: Solo 3 productos pasan todos los filtros. Refleja criterios conservadores por diseño — crecerá con historial consistente.

### Health del Collector

| Indicador | Valor |
|-----------|-------|
| Estado | running |
| Último snapshot | 2026-06-02 16:29 UTC |
| Antigüedad del moat | 3.4 horas |
| Collector stale | No |
| Precios último ciclo | 307 |
| Tiendas éxito último ciclo | 31 de 36 |
| Tiendas fresh 24h | 35 de 36 (97.2%) |
| Cobertura 7d | 36 de 36 (100.0%) |
| Tienda stale | whirlpool_ar (24 fallos consecutivos) |

El collector está operativo. 35/36 tiendas con datos <24h. whirlpool_ar dejó de responder en las últimas horas pero mantiene cobertura 7d 100%.

### Juicio del Controller

**APTO para uso en decisiones comerciales.** Cobertura 7d: 100.0% (≥80%). Antigüedad: 3.4h (<24h). Collector operativo. Funnel documentado con trazabilidad.

Salvedad: 20.965 productos (46.2%) no normalizables. Universo efectivo para canasta/spreads: 24.457 (53.8%).

---

✅ CONTROLLER'S SIGN-OFF

Certifico que:
- Datos extraídos de /dashboard/data el 2026-06-02 19:51 UTC.
- Funnel aplicado: descuento >90% → suspect, outlier >5x → flagged, no normalizable → excluido.
- 45.422 precios trazables a price_snapshots.
- Cobertura 7d 100.0% (≥80%), antigüedad 3.4h (<24h). **Apto para decisiones comerciales.**

— Dana, Bookkeeper & Controller

---

## 📋 Metodología y Audit Trail

### Cadena de custodia

| Eslabón | Descripción | Timestamp |
|---------|-------------|-----------|
| 1. Fuente | APIs VTEX/Shopify/Magento | Cada 8h |
| 2. Collector | collect_prices.py (Railway) | 2026-06-02 16:29 UTC |
| 3. DB | price_snapshots (PostgreSQL) | Upsert (product_id, store) |
| 4. Dashboard | GET /dashboard/data | 2026-06-02 19:51 UTC |
| 5. Reporte | Este documento | 2026-06-02 · SHA256: e6f491fe739296f4 |

### Query fuente

GET /dashboard/data → 200 · ~1.3 MB
JSON completo: ops/generated/prompts/dashboard-data.json

### Criterios de inclusión/exclusión

**Incluidos (45.422):** price > 0, price < 999999, en ventana del collector.
**Excluidos de canasta/spreads:** descuento ≥90%, outlier >5x mediana, unidad no parseable.
**Excluidos de marketing:** <6/10 ítems canasta, spreads bajo umbral (2.5x/10x).

### Limitaciones

1. Retail formal urbano solamente. No incluye mercados ni comercio informal.
2. No replica IPC oficial. Canasta CLI Market = 10 productos vs ~500 del IPC.
3. Zonas metropolitanas. No refleja precios en provincias.
4. No todos los productos se re-capturan en cada ciclo de 8h.
5. Conversiones USD usan tasas fijas, no spot.
