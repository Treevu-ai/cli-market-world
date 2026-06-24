# CLI Market Intelligence — Metodología Defensible

**Versión:** 2.0 · **Fecha:** 2026-06-24  
**Fuente canónica:** `market_core/market_indicators_catalog.py` + `market_core/market_indicators.py`

---

## Principio rector

Los indicadores de CLI Market miden **velocidad de precios en góndola online** — no inflación oficial. Cada métrica tiene un nombre, escala, fórmula y nota metodológica explícita para evitar comparaciones incorrectas contra indicadores oficiales (IPC, CPI, INEI, INDEC, etc.).

---

## P0 — Indicadores núcleo

### 1. Retail Price Velocity (RPV) — `staple_price_momentum`

| Campo | Valor |
|-------|-------|
| **Nombre display** | Retail Price Velocity (RPV) |
| **Clave interna** | `staple_price_momentum` |
| **Ventana** | 7 días rolling |
| **Unidad** | % (delta porcentual) |

**Qué mide:** Cambio porcentual promedio de precios de SKUs de canasta básica (arroz, leche, aceite, azúcar, harina…) en el canal online en los últimos 7 días. Solo incluye retailers con ≥3 snapshots en el período.

**Fórmula:**
```
RPV = mean((price_last - price_first) / price_first × 100)
      para SKUs de canasta básica con ≥2 observaciones en la ventana
```

**Nota metodológica crítica:**
- CLI Market RPV ≠ CPI oficial. El RPV captura velocidad de precio en canal online.
- El IPC oficial (INEI, INDEC, DANE, INEGI, etc.) usa encuesta de hogares, canasta mensual o anual, precios en tienda física y online.
- **No anualizar RPV** ni comparar directamente contra cifras de IPC.
- El RPV es útil para procurement e inteligencia de mercado, no para análisis macroeconómico.

---

### 2. Basket Stress Index (BSI) — `basket_stress_index`

| Campo | Valor |
|-------|-------|
| **Nombre display** | Basket Stress Index (BSI) |
| **Clave interna** | `basket_stress_index` |
| **Ventana** | 30 días (baseline rolling) |
| **Escala** | 0–1+ (normalizado) |

**Qué mide:** Presión sobre la canasta básica. Compara el total mínimo de la canasta (10 staples en los retailers más baratos del país) contra el baseline de 30 días.

**Fórmula raw:**
```
BSI_raw = (current_min_basket / baseline_min_basket) × 100
          donde baseline = promedio rolling 30d
```

**Escala normalizada (0–1+):**
| Rango | Interpretación |
|-------|----------------|
| < 0.15 | Estable — sin presión significativa |
| 0.15 – 0.50 | Presión moderada — monitorear |
| > 0.50 | Crítico — canasta básica bajo estrés severo |

**Raw index ~100 = paridad con baseline. >105 = presión creciente.**

**Nota:** La escala normalizada y el raw index son representaciones distintas del mismo cálculo. El API de `/v1/intel/brief` expone ambas: `basket_stress_index` (raw) y `basket_stress_index_scale` (leyenda).

---

### 3. Shelf Signal vs Official CPI Gap — `collector_vs_official_gap`

| Campo | Valor |
|-------|-------|
| **Nombre display** | Shelf Signal vs Official CPI Gap |
| **Clave interna** | `collector_vs_official_gap` |
| **Unidad** | puntos porcentuales (pp) |
| **Fuente externa** | Banco Mundial `FP.CPI.TOTL.ZG` (YoY anual) |

**Qué mide:** Diferencia en pp entre la señal de precio de góndola CLI Market (rolling 30d) y el CPI oficial del Banco Mundial (YoY anual) para el mismo país.

**Fórmula:**
```
gap_pp = internal_inflation_avg_30d_pct - cpi_official_yoy_annual
```

**Caveat temporal — CRÍTICO:**

> La señal interna es un promedio rolling de **30 días de precios online**. El CPI oficial es **YoY anual** basado en encuesta de hogares. Son **metodológicamente distintos**: distinto canal, distinta canasta, distinta frecuencia, distinto año base.

- La comparación es **direccional**, no equivalente.
- Un gap de +5pp no significa que "la inflación real es 5pp más alta que la oficial" — puede reflejar diferencias de canal, composición de canasta o rezago temporal.
- En el API, este indicador siempre incluye `period_caveat` en la respuesta para evitar interpretaciones incorrectas.
- En reportes públicos, etiquetar como "señal de góndola vs referencia macro" — nunca como "inflación real vs inflación oficial".

**Uso legítimo:**
- Señal anticipatoria de presión de precios en canal moderno
- Divergencia sectorial (supermercados vs canasta IPC)
- Análisis de procurement para compras de corto plazo

---

### 4. Coverage Table — `coverage_matrix`

| Campo | Valor |
|-------|-------|
| **Endpoint** | `GET /v1/coverage/matrix` |
| **Umbral mínimo** | 60% cobertura para publicar datos del país |

**Qué mide:** Cobertura del collector por país y línea de producto — % de retailers activos con datos frescos en las últimas 24h.

**Campos en la respuesta del brief:**
```json
{
  "coverage": {
    "PE": { "pct": 87, "active_stores": 18, "total_stores": 21, "stale_stores": [] },
    "AR": { "pct": 61, "active_stores": 13, "total_stores": 21, "stale_stores": ["wong_ar"] }
  },
  "coverage_threshold_pct": 60,
  "coverage_warning": null
}
```

**Regla de publicación:** Si cobertura < 60% para un país, no publicar datos de ese país en reportes externos. El data-gate (`collector_stale`) bloquea el brief completo si la cobertura global está degradada.

---

## Indicadores de soporte

### `promo_intensity`
% de SKUs con `price < list_price` en el período. Mide agresividad promocional en góndola.

### `price_dispersion`
Desviación estándar relativa de precios para el mismo producto entre retailers. Alta dispersión = oportunidad de arbitraje para procurement.

### `food_inflation_spread`
Spread entre la señal de inflación de alimentos (línea supermercados) y la señal promedio global. Indicador sectorial — no equivale al índice de alimentos del IPC oficial.

---

## Fuentes externas

| Fuente | Indicador | Latencia | Uso |
|--------|-----------|----------|-----|
| Banco Mundial (`FP.CPI.TOTL.ZG`) | CPI YoY anual | 1–2 años | `collector_vs_official_gap` |
| FMI | Inflation YoY | 1 año | `macro_validation` |
| Wikipedia Pageviews | Momentum por categoría | Diario | `demand_outlook`, `staple_demand` |
| Open Food Facts | Match rate / NOVA score | Semanal | Product intelligence |
| Open-Meteo | Weather alerts | Horario | `logistics_risk` |
| CEPAL | Salario mínimo real | Anual | `labor_stress` / `wage_affordability` |

**Nota sobre latencia macro:** Los datos del Banco Mundial y FMI tienen latencia de 1–2 años. Se usan como referencia histórica de dirección, no como dato en tiempo real. Siempre mostrar el año de referencia junto al valor.

---

## Disclaimers estándar

### Para reportes externos (PIR, posts, decks):
> "Los datos de CLI Market miden velocidad de precios en góndola online (canal moderno). No reemplazan indicadores oficiales de inflación (INEI, INDEC, DANE, INEGI, INE, INEC, BCCh, INE-UY)."

### Para el gap CPI:
> "Comparación direccional entre señal de góndola rolling 30d y CPI oficial YoY anual. Metodologías distintas — no reportar como equivalentes."

### Para RPV en encabezados:
> "Retail Price Velocity (RPV): cambio de precio en góndola online en {N} días. ≠ IPC oficial."

---

## Historial de cambios

| Fecha | Cambio | Motivo |
|-------|--------|--------|
| 2026-06-24 | `staple_price_momentum` renombrado a RPV en display | Evitar confusión con CPI |
| 2026-06-24 | BSI escala explícita 0–1+ documentada | Ambigüedad entre raw index y normalizado |
| 2026-06-24 | `collector_vs_official_gap` añade `period_caveat` en API | Mismatch temporal 30d vs YoY |
| 2026-06-24 | Coverage table añadida al brief | P0.4 PRD — umbral 60% |
