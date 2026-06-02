# CLI Market Price Pulse
**Semana 2026-W23 · 2026-06-02**

*Reporte generado automáticamente desde datos de góndola verificados.*
*CLI Market Intelligence — Piloto comercial · Confidencial*

---

## 1. Resumen Ejecutivo

- **45.422** precios indexados en el data moat
- **3.138** precios actualizados en las últimas 24 horas
- **36** tiendas con datos activos
- **100.0%** de cobertura del catálogo activo (7 días)
- **97.2%** de precios con menos de 24 horas de antigüedad
- Antigüedad del último snapshot: **3 horas**
- Estado del collector: 🔄 **running**

---

## 2. Inflación Observada (7 días)

_Serie histórica insuficiente (se requieren ≥7 días de datos). El piloto incluye acumulación progresiva._

---

## 3. Canasta Básica

| Tienda | Ítems | Total | Moneda |
|--------|-------|-------|--------|
| Plaza Vea | 10/10 | 64.39 | PEN |
| Mambo BR | 6/10 | 65.82 | BRL |
| Metro | 10/10 | 76.39 | PEN |
| Wong | 10/10 | 88.75 | PEN |
| Sam's Club BR | 6/10 | 95.19 | BRL |
| Chedraui | 10/10 | 207.00 | MXN |
| HEB | 10/10 | 319.20 | MXN |
| Carrefour BR | 9/10 | 589.73 | BRL |
| Vea AR | 10/10 | 10286.90 | ARS |
| Jumbo AR | 10/10 | 14936.19 | ARS |

### Trazabilidad metodológica — Categorías IPC (INEI, base 2021=100)

| Ítem canasta | División IPC | Subclase IPC | Ponderación INEI |
|-------------|-------------|-------------|------------------|
| leche | Alimentos y Bebidas No Alcohólicas | Leche, queso y huevos | 5.03% |
| arroz | Alimentos y Bebidas No Alcohólicas | Pan y cereales | 4.82% |
| aceite | Alimentos y Bebidas No Alcohólicas | Aceites y grasas | 3.41% |
| azucar | Alimentos y Bebidas No Alcohólicas | Azúcar, mermelada, chocolate | 2.78% |
| huevos | Alimentos y Bebidas No Alcohólicas | Leche, queso y huevos | 0.91% |
| pan | Alimentos y Bebidas No Alcohólicas | Pan y cereales | 3.52% |
| cafe | Alimentos y Bebidas No Alcohólicas | Café, té y cacao | 0.88% |
| pollo | Alimentos y Bebidas No Alcohólicas | Carne | 7.12% |
| queso | Alimentos y Bebidas No Alcohólicas | Leche, queso y huevos | 1.45% |
| jabon | Bienes y Servicios Diversos | Cuidado personal | 2.91% |

*Ponderaciones referenciales INEI (base 2021=100). La canasta de CLI Market cubre productos de consumo diario en retail formal urbano. No pretende replicar la canasta completa del IPC nacional.*

---

## 4. Dispersión de Precios (Spreads)

- **queso** (Supermercados, ARS): spread **2.9x** entre 3 tiendas — min ARS 6.97 / max ARS 931.03 (promedio: 314.99)
- **pollo** (Supermercados, ARS): spread **2.7x** entre 3 tiendas — min ARS 21.10 / max ARS 20135.45 (promedio: 7533.48)
- **aceite** (Supermercados, ARS): spread **2.6x** entre 3 tiendas — min ARS 143.00 / max ARS 3352.67 (promedio: 1212.89)

---

## 5. Calidad del Dato

- **Capturados**: 45.422 precios
- **Flagged (descuentos >90%)**: 3.203
- **Flagged (outliers 5x)**: 3.377
- **Citables (marketing-ready)**: 3

*El funnel clean → flagged → citable documenta cada paso de filtrado. Solo se entregan datos 'citables' en exports y reportes B2B.*

---

## 6. Metodología

- **Fuente**: APIs públicas de retailers VTEX/Shopify/Magento (sin scraping de páginas web).
- **Frecuencia**: Collector programado cada 8 horas.
- **Cobertura geográfica**: Perú, Colombia, Argentina, Brasil, México, Chile + Europa.
- **Normalización**: Precios por kg/L cuando la unidad es parseable (ej. 900ml → normalizado a 1L).
- **Filtros de calidad**: Descuentos >90% marcados como 'suspect'. Outliers de precio >5x la mediana del grupo excluidos de canasta.
- **Disclaimer**: Los datos provienen de góndola online en retail formal urbano. No reemplazan IPC oficial (INEI, INDEC, IBGE). Señal de alta frecuencia, no índice nacional.

---

*Generado el 2026-06-02 · CLI Market Intelligence · hello@cli-market.dev*
*Dashboard público: https://cli-market-production.up.railway.app/dashboard*
