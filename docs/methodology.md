---
title: CLI Market Intelligence — Metodología de Indicadores v2
tags:
  - intelligence
  - methodology
  - price-pulse
status: active
updated: 2026-06-24
version: 2.0
supersedes: narrativa informal "inflación de góndola" en reportes pre-v2
---

# Metodología CLI Market Intelligence v2

Documento canónico de fórmulas, nomenclatura y reglas de publicación para **Price Pulse**, **Intelligence API** y copy público.

**Principio rector:** CLI Market mide precios observados en retail online indexado. No produce índices oficiales de inflación ni replica el IPC/INEI, INDEC, IBGE, DANE o INEGI.

---

## 1. Retail Price Velocity (RPV)

| Capa | Identificador |
|------|---------------|
| API / DB | `shelf_price_momentum_7d` |
| Producto / dashboard | **Retail Price Velocity (RPV)** |
| Prensa / newsletter | Movimiento de precios en góndola |

### Fórmula

Para cada par `(línea, moneda)`:

```
RPV_7d = mean_over_SKUs( (avg_price_7d − avg_price_prev_7d) / avg_price_prev_7d ) × 100
```

Donde:

- `avg_price_7d` = media aritmética simple de precios capturados en los últimos 7 días
- `avg_price_prev_7d` = media de los 7 días inmediatamente anteriores
- Solo entran SKUs con ≥2 observaciones en cada ventana (n reportado por línea)

### Qué NO es

- No es inflación oficial ni sustituto del IPC
- No incorpora ponderadores de gasto de hogares
- No incluye canales no digitales ni servicios

### Copy permitido

> "Movimiento de precios observado en góndola online (RPV 7d: +X.X% en supermercados PEN)."

### Copy prohibido

> "Inflación de góndola" · "Inflación del X%" *(sin calificador metodológico)*

---

## 2. Comparación con IPC oficial

### Reglas

1. **Nunca** publicar "brecha de X pp vs IPC general" como titular.
2. Comparación permitida solo si:
   - Período alineado (ambos mensuales **o** ambos anuales)
   - Benchmark = sub-índice **alimentos y bebidas**, no IPC headline
   - Nota metodológica visible en el mismo bloque (no solo pie de página)
3. Si no se cumplen las condiciones → omitir comparación numérica; usar texto cualitativo.

### Copy estándar (cuando no hay alineación)

> "RPV mide alta frecuencia en retail online indexado. El IPC INEI usa metodología distinta, canasta ampliada y canales mixtos. No son directamente comparables."

### Campo API legacy

`collector_vs_official_gap` / `vs_official_cpi_gap_pp` — solo para uso interno o anexo metodológico con las condiciones anteriores. No en headlines públicos.

---

## 3. Basket Stress Index (BSI)

### Fórmula

```
BSI = canasta_total_hoy / median(canasta_total, últimos 30 días)
```

- `canasta_total` = suma de precios unitarios de los 10 ítems de referencia CLI Market (canasta básica), por país/moneda
- Escala: **índice 1.0 = sin estrés** (nivel histórico mediano)
  - `< 0.95` — aliviado
  - `0.95 – 1.05` — estable
  - `1.05 – 1.15` — presión moderada
  - `> 1.15` — estrés elevado

### Publicación obligatoria

Cada emisión incluye: valor actual, banda interpretativa, mediana 30d de referencia, n de tiendas en la canasta.

### Diferencia vs Price Dispersion

| | BSI | Price Dispersion |
|---|-----|------------------|
| Dimensión | Temporal (mismo retailer, distintos momentos) | Cross-sectional (distintos retailers, mismo momento) |
| Pregunta | ¿La canasta subió vs su propio histórico? | ¿Cuánto divergen precios entre cadenas hoy? |
| Ortogonalidad | Sí — pueden moverse en direcciones opuestas | |

---

## 4. Affordability Ratio

### Variantes (v2)

| Variante | Fórmula | Uso |
|----------|---------|-----|
| **Best case** | `salario_mínimo / precio_canasta_retailer_más_barato` | Oportunidad máxima si el hogar optimiza |
| **Promedio** *(titular)* | `salario_mínimo / precio_canasta_promedio_ponderado` | Indicador principal |
| **Worst case** | `salario_mínimo / precio_canasta_retailer_más_caro` | Costo de no comparar |

Ponderación promedio: por participación de tiendas con datos en el país (peso = 1/n tiendas si no hay volumen de ventas).

### Disclaimer obligatorio

> La canasta CLI Market es un benchmark referencial de productos esenciales en canales digitales verificados. No representa el gasto mensual total de un hogar peruano, que incluye canales no digitales, servicios y mayor variedad de categorías.

---

## 5. Price Dispersion

### Métrica estándar: coeficiente de variación (CV)

Para cada grupo de productos comparables (misma línea + moneda + match semántico):

```
CV = σ(precios) / μ(precios) × 100
```

- `σ` = desviación estándar muestral entre retailers
- `μ` = media aritmética de precios observados
- Reporte agregado = media de CV por grupo, ponderada por n de retailers

### Por qué CV y no (max−min)/min

- Robusto a un outlier extremo de un solo retailer
- Comparable entre categorías con distintos niveles de precio
- Estándar en literatura de price dispersion

### Deprecado

`(max − min) / min` — no usar en publicaciones v2 salvo nota de transición.

---

## 6. Promo Intensity

### Definición operacional

```
Promo Intensity = (SKUs con descuento ≥ 3%) / SKUs totales observados × 100
```

**Promoción activa** = `list_price` presente y `(list_price − price) / list_price ≥ 0.03`

### Publicación

Siempre citar: umbral 3%, n SKUs, ventana de captura (refresh 4–8h), retailers incluidos.

### Exploración v2 (no bloqueante)

- Promo por categoría (lácteos, aceites, granos)
- Promo por retailer
- Promo velocity (entrada/salida de promociones)

---

## 7. Coverage & Freshness

### Tabla obligatoria en cada reporte

| Retailer | País | SKUs indexados | % catálogo activo | Último snapshot | Refresh SLA |
|----------|------|----------------|-------------------|-----------------|-------------|
| … | … | n | % | ISO timestamp | 4h / 8h |

Totales: SKUs únicos, retailers activos, cobertura agregada %, fecha de corte UTC.

### Umbral de publicación

| Cobertura agregada | Etiqueta | Uso público |
|--------------------|----------|---------------|
| ≥ 60% | Normal | Claims en GTM, prensa, LinkedIn data-gated |
| < 60% | `[COBERTURA PARCIAL]` | Solo clientes con disclaimer; sin claims agregados |

Fuente: `GET /v1/coverage/matrix` + `store_health` en `/dashboard/data`.

---

## 8. Google Trends

### Estado actual (P2)

CLI Market observa **correlación** entre volúmenes de búsqueda (`gtrends_search_momentum`) y movimientos de precio (RPV). La dirección causal y el lag óptimo están en proceso de caracterización.

### Comunicación permitida

> "CLI Market observa correlación entre volúmenes de búsqueda y movimientos de precio. La dirección causal y el lag óptimo están en proceso de caracterización."

### Comunicación prohibida

Implicar que Trends **causa** o **predice** precios sin análisis de Granger/lag documentado.

---

## Referencias

- [DATA-MOAT-INDICATORS.md](DATA-MOAT-INDICATORS.md) — catálogo API `indicator_definitions`
- [prd-intelligence-v2-methodology.md](prd-intelligence-v2-methodology.md) — PRD y priorización
- [price-pulse-workflow.md](agents/price-pulse-workflow.md) — pipeline de reportes
- [linkedin/data-gate.md](../tools/content-repo-template/linkedin/data-gate.md) — gate GTM para cifras agregadas
