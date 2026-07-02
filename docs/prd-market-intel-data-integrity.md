---
title: PRD — Market Intel Data Integrity: País Fantasma, CV Inválido de Tienda Única y Confianza sin Ponderar
tags:
  - product
  - prd
  - intelligence
  - data-integrity
status: Draft
owner: Head of Product + Engineering
updated: 2026-07-02
repos: cli-market-core, cli-market-backend, cli-market-world
methodology: docs/methodology.md
related: prd-intelligence-v2-methodology.md
---

# PRD — Market Intel Data Integrity: País Fantasma, CV Inválido de Tienda Única y Confianza sin Ponderar

**Producto:** CLI Market Intel (`market intel brief`, `/v1/intel/brief`, scores compuestos)
**Autor:** Head of Product + Engineering
**Estado:** Draft v1.0
**Fecha:** 2026-07-02
**Origen:** Auditoría manual de `market intel brief` sobre 14 países declarados en catálogo (IT, MX, CL, US, CO, AR, BR, PE, FR, ES, CH, EC, BO, UY) + verificación directa de código fuente.
**Relación con PRD previo:** Complementa [prd-intelligence-v2-methodology.md](prd-intelligence-v2-methodology.md) (P0 shipped 2026-06-29). Ese PRD resolvió nomenclatura, fórmulas y umbrales; este PRD ataca un problema distinto y más grave: **integridad de los datos subyacentes**, no la definición de las métricas.

---

## 1. Problema

De los 14 países que el catálogo declara con cobertura, la auditoría encontró que solo 5–6 (AR, BR, CO, PE, MX, CL) tienen tiendas realmente registradas y activas. Los países sin tiendas registradas (CH, EC, BO, UY, US, y probablemente otros) reciben un **response de `/v1/intel/brief` sin ningún flag de error**, con un conteo de tiendas idéntico entre sí que no corresponde al país consultado.

Por separado, dos defectos metodológicos independientes fueron confirmados en el código:

1. **Price Dispersion (CV) no exige múltiples tiendas distintas** — se calcula igual con 1 tienda que con 10, mezclando varianza temporal intra-tienda con dispersión cross-retailer.
2. **Los scores compuestos no descuentan por frescura o cobertura** — un score de agresividad o riesgo logístico calculado sobre 0% de frescura y 1–2 tiendas se presenta con la misma autoridad visual que uno calculado sobre datos frescos de 8+ tiendas.

**Costo del problema:**

- Un cliente o inversionista que consulte un país sin cobertura real (ej. Bolivia, Ecuador) recibe una respuesta con apariencia de dato real — riesgo de credibilidad si se detecta en demo o due diligence.
- Los scores compuestos (`retail_aggression`, `logistics_risk`, etc.) no son auditables cuando su n real es 1–2 tiendas con 0% frescura — mismo tipo de riesgo que ya motivó el PRD anterior, pero ahora en la capa de scores, no de indicadores individuales.
- Corrección de una nota importante encontrada durante esta auditoría: un hallazgo externo previo interpretó `basket_stress_index = 123.36` (Italia) como "overflow numérico" comparándolo contra la escala 0.95–1.15 de `methodology.md §3`. **Esto es una lectura incorrecta de escala, no un bug numérico** — el código (`market_indicators.py:1380-1383`) documenta y calcula el BSI expuesto en escala ~100 (`>105 elevado`), consistente con un fix previo ya shippeado (`cli-market-backend#127`, ver §4.2). El problema real no es "overflow": es que **`methodology.md §3` sigue documentando la escala vieja (ratio 0.95–1.15) que ya no coincide con lo que el código produce**, lo cual genera exactamente este tipo de mala interpretación en cualquier revisor — humano o agente — que solo lea la documentación pública.

---

## 2. Objetivos

| Objetivo | Métrica de éxito |
|----------|------------------|
| Ningún país sin cobertura real devuelve datos con apariencia de válidos | Response incluye `data_available: false` explícito + cero fallback silencioso a catálogo global |
| CV de price dispersion es auditable | CV solo se computa y publica cuando `n_stores >= 2` distintas en la ventana |
| Scores compuestos reflejan su propia confianza | Cada score expone `confidence` derivado de frescura + n_stores; scores con confianza baja se marcan explícitamente, no se suprimen silenciosamente |
| `methodology.md` es la fuente única de verdad de escala | Escala del BSI (y cualquier otro indicador con reescalado interno) documentada en `methodology.md` coincide exactamente con lo que el código produce |

---

## 3. Fuera de scope

- Agregar cobertura real (tiendas) a los países sin datos — eso es un problema de scraping/GTM, no de este PRD
- Rediseñar el schema de scores por país (ej. por qué US/UY tienen menos scores que AR/CO) — documentar la razón es P1 aquí, pero unificar el schema no
- Cambiar la fórmula del BSI o del CV — ya están definidas en `methodology.md §3/§5`; este PRD corrige la propagación de esas fórmulas a casos límite (n=0, n=1) y la sincronización de escala en la documentación

---

## 4. Requerimientos por hallazgo

### 4.1 País sin tiendas registradas devuelve datos de fallback sin flag — **P0**

**Problema confirmado:** en `market_core/market_indicators.py`, `confidence["stores_active"]` (consumido por el headline `"Moat activo — N tiendas monitoreadas"` en `cli-market-backend/routers/intel.py:379-381`) cae a `len(get_default_stores())` — el catálogo **global** de tiendas — cuando el valor de `store_coverage` país-específico es `None`:

```python
# market_core/market_indicators.py:1438-1447
stores = _val("store_coverage")
if stores is not None:
    confidence["stores_active"] = int(stores)
else:
    from .store_credentials import get_default_stores
    confidence["stores_active"] = len(get_default_stores())
```

Esto explica el número constante "38 tiendas" (o 37, según el momento) que aparece idéntico para CH, EC, BO, UY, US — países sin tiendas propias en `STORES` (`market_stores.py`). El headline (`intel.py:379-381`) ni siquiera incluye el nombre del país, agravando la confusión.

**Spike requerido (antes de implementar el fix):** confirmar si los *valores* de los scores compuestos (`retail_aggression=68`, `price_fairness=91`, etc. — idénticos entre ES/CH/EC/BO en la auditoría) provienen del mismo mecanismo de fallback, o de otro código no identificado aún. Se verificó directamente que `compute_basket_stress` y `compute_price_dispersion` **sí** retornan `None` correctamente cuando `_stores_for_country()` es vacío (guard en `market_indicators.py:216-218` y equivalentes) — por lo que el fallback de scores compuestos, si existe, está en otro punto del pipeline (probablemente en la capa que arma `latest` a partir de valores cacheados/demo). No asumir el mecanismo sin verificarlo.

**Requerimiento:**
- `stores_active` nunca cae al catálogo global cuando el país no tiene tiendas — debe ser `0`.
- Cuando `stores_active == 0` para un país solicitado explícitamente, el response de `/v1/intel/brief` incluye `"data_available": false` y un mensaje explícito (`"Sin cobertura de tiendas para {país}. Ver /v1/coverage/matrix."`), no un brief con apariencia de dato real.
- El CLI (`market_cli.py`) refleja esto con un mensaje de error/advertencia, no con la tabla de scores normal.

**Criterio de aceptación:** ningún país sin tiendas en `STORES` devuelve un `stores_active` > 0 ni scores compuestos sin el flag `data_available: false`.

### 4.2 Sincronizar la escala documentada del BSI con la escala real del código — **P0**

**Problema confirmado:** `methodology.md §3` documenta el BSI como ratio (`1.0 = sin estrés`, banda `0.95–1.15`). El código (`market_indicators.py:212-257`) retorna `round(current / baseline * 100, 2)` — escala ~100, no ~1.0 — y lo documenta correctamente en el campo expuesto (`market_indicators.py:1380-1383`: `"100 = same canasta total as 30 days ago · >105 elevated · 95-105 normal · <95 eased"`). El score compuesto `basket_stress` (`market_indicators.py:1122-1138`) ya fue corregido para esta escala tras un bug previo (`cli-market-backend#127`, comentario in-line lo documenta), pero **`methodology.md` nunca se actualizó** y sigue mostrando la escala vieja.

**Nota de corrección:** el valor `basket_stress_index = 123.36` reportado para Italia **no es un overflow**. En la escala real (~100 baseline), 123.36 es "elevado" (>105), consistente y dentro de rango — el problema de fondo es que Italia tiene 1 tienda y 0% frescura, por lo que ese "elevado" no es estadísticamente confiable (ver §4.3), no que el número esté matemáticamente mal.

**Requerimiento:** actualizar `methodology.md §3` para documentar la escala ~100 (`>105 elevado · 95–105 estable · <95 aliviado`) exactamente como la produce el código, eliminando la referencia a la banda `0.95–1.15`. Añadir nota explícita de historial: "escala corregida 2026-07 — ver `cli-market-backend#127`".

**Criterio de aceptación:** `methodology.md §3` y `market_indicators.py:1380-1383` documentan literalmente la misma escala y los mismos umbrales.

### 4.3 CV de price dispersion no exige múltiples tiendas distintas — **P0**

**Problema confirmado:** `compute_price_dispersion` (`market_indicators.py:134-160`) vía `canonical_price_buckets` (`golden_taxonomy.py`) agrupa por producto y calcula CV sobre cualquier bucket con `len(prices) >= 2`, sin exigir que esas ≥2 observaciones vengan de tiendas distintas:

```python
# market_indicators.py:150-157
for prices in buckets.values():
    if len(prices) < 2:
        continue
    mean = sum(prices) / len(prices)
    ...
    cvs.append(math.sqrt(var) / mean * 100)
```

Con 1 sola tienda activa (Francia: `whirlpool_fr`), snapshots repetidos del mismo producto en momentos distintos llenan el bucket y producen un CV que el sistema publica como "dispersión cross-retailer" (`methodology.md §5`) cuando en realidad es varianza temporal intra-tienda — metodológicamente inválido por definición (`methodology.md §5` define CV explícitamente como dispersión "entre retailers").

**Requerimiento:**
- `canonical_price_buckets` / `compute_price_dispersion` deben contar **tiendas distintas** por bucket, no observaciones de precio totales.
- CV solo se computa y publica cuando `n_stores_distintas >= 2` en el bucket.
- Cuando el país tiene <2 tiendas activas, `price_dispersion` retorna `None` y el brief lo indica explícitamente (`"Dispersión no aplicable — requiere ≥2 tiendas activas"`), no omite el campo silenciosamente.

**Criterio de aceptación:** ningún país con <2 tiendas activas publica un valor de `price_dispersion` / CV.

### 4.4 Scores compuestos sin ponderación por frescura o cobertura — **P1**

**Problema confirmado:** `_scores_from_latest` (`market_indicators.py:1080-1273`) calcula `retail_aggression`, `logistics_risk`, `price_fairness`, `commodity_pressure`, etc. directamente de los valores crudos. `freshness` se lee (línea 1084) pero solo alimenta el score separado `data_confidence` (líneas ~1141-1146) — nunca descuenta ni marca a los demás scores. El CLI (`market_cli.py:1766-1795`) muestra freshness como texto pequeño al pie de la tabla, sin ninguna advertencia visual cuando es bajo.

Esto reproduce, en la capa de scores compuestos, el mismo problema que el PRD anterior (`prd-intelligence-v2-methodology.md §4.7`) ya resolvió para indicadores individuales vía la tabla de Coverage & Freshness con umbral `<60% → [COBERTURA PARCIAL]`.

**Requerimiento:**
- Cada score compuesto expone un campo `confidence` (alto/medio/bajo) derivado de `freshness` y `n_stores` del país, usando el mismo umbral 60% ya establecido en `methodology.md §7`.
- Scores con `confidence: bajo` se renderizan en el CLI con marca visual explícita (ej. `⚠`), no con el mismo estilo que scores de alta confianza.
- El JSON de `/v1/intel/brief` incluye `confidence` a nivel de cada score individual, no solo un `data_confidence` global desacoplado.

**Criterio de aceptación:** ningún score compuesto con `freshness < 60%` o `n_stores < 3` se muestra sin marca de confianza baja, en CLI ni en API.

### 4.5 Documentar el schema reducido de scores para US/UY — **P2**

**Problema:** US y UY muestran 4 scores (`retail_aggression`, `price_fairness`, `data_confidence`, `commodity_pressure`) frente a los 13 de AR/CO. Puede ser intencional (modelo de referencia distinto) pero no está documentado en ningún lado.

**Requerimiento:** documentar en `methodology.md` (nueva sección o nota en §7) qué determina qué subconjunto de scores se calcula por país, y por qué.

**Criterio de aceptación:** existe una referencia pública explicando la variación de schema por país.

---

## 5. Priorización

| Requerimiento | Prioridad | Esfuerzo | Bloquea publicación/demo | Estado |
|---------------|-----------|----------|---------------------------|--------|
| 4.1 País sin cobertura → flag explícito | P0 | Medio (+ spike) | Sí | ✅ Shipped ([cli-market-core#137](https://github.com/Treevu-ai/cli-market-core/pull/137)) |
| 4.2 Sincronizar escala BSI en methodology.md | P0 | Bajo | Sí | ✅ Shipped ([cli-market-world#484](https://github.com/Treevu-ai/cli-market-world/pull/484)) |
| 4.3 CV exige ≥2 tiendas distintas | P0 | Medio | Sí | ✅ Shipped ([cli-market-core#137](https://github.com/Treevu-ai/cli-market-core/pull/137)) |
| 4.4 Confidence por score compuesto | P1 | Medio | No | ✅ Shipped ([cli-market-core#137](https://github.com/Treevu-ai/cli-market-core/pull/137), [cli-market-world#484](https://github.com/Treevu-ai/cli-market-world/pull/484)) |
| 4.5 Documentar schema reducido US/UY | P2 | Bajo | No | ✅ Shipped ([cli-market-world#484](https://github.com/Treevu-ai/cli-market-world/pull/484)) |

---

## 6. Entregables

| Entregable | Responsable | Repo | Estado |
|------------|-------------|------|--------|
| Spike: trazar origen de scores idénticos ES/CH/EC/BO | Engineering | cli-market-core | ✅ Resuelto — el mecanismo es `get_latest_values()` sirviendo filas de scope global (`country=''`) cuando no hay filas propias del país; confirmado con `compute_basket_stress`/`compute_price_dispersion` retornando `None` correctamente para países sin tiendas |
| Fix: `stores_active` no cae a catálogo global | Engineering | cli-market-core | ✅ |
| Fix: `data_available: false` en brief sin cobertura | Engineering | cli-market-core | ✅ (implementado en `cli-market-core`, no en backend/world — `build_intel_brief` vive ahí) |
| Fix: CV exige n_stores distintas ≥2 | Engineering | cli-market-core | ✅ |
| Update: `methodology.md §3` escala BSI sincronizada | Lead Economist | cli-market-world | ✅ |
| Fix: `confidence` por score compuesto + render CLI | Engineering | cli-market-core, cli-market-world | ✅ |
| Doc: schema de scores por país | Product | cli-market-world | ✅ |

---

## 7. Criterio de lanzamiento

Este PRD se considera resuelto cuando:

- [ ] Ningún país sin tiendas registradas devuelve `stores_active > 0` ni scores sin `data_available: false`
- [ ] `methodology.md §3` coincide exactamente con la escala que produce el código
- [ ] Ningún `price_dispersion`/CV se publica con <2 tiendas distintas en el bucket
- [ ] Todo score compuesto expone `confidence` y se marca visualmente cuando es bajo
- [ ] Spike de §4.1 documentado con hallazgo concreto (mecanismo confirmado, no solo "38 tiendas" como síntoma)

---

## 8. Notas de auditoría (contexto, no normativo)

Tabla de cobertura real observada el 2026-07-01 (antes de cualquier fix de este PRD):

| País | Tiendas reales en `STORES` | Freshness observado | Estado |
|------|------------------------------|---------------------|--------|
| AR | 8 | 62% | Datos reales, parcial |
| BR | 13 | 0% | Datos reales, pipeline RPV con anomalías (fuera de scope, ver PRD anterior) |
| CO | 2 | 100% | Datos reales, cobertura mínima |
| PE | 5 | 0% | Datos reales, pipeline RPV con anomalías |
| MX | 4 | 0% | Datos reales, stale |
| CL | 2 | 0% | Datos reales, stale, n muy bajo |
| IT | 1 | 0% | Datos reales, n=1 (ver §4.3/§4.4) |
| FR | 1 | 0% | Datos reales, n=1 (ver §4.3/§4.4) |
| ES, CH, EC, BO, UY, US | 0 (o schema reducido) | — | Fallback sin flag (§4.1) o schema no documentado (§4.5) |

Ver también: [methodology.md](methodology.md) · [prd-intelligence-v2-methodology.md](prd-intelligence-v2-methodology.md) · [DATA-MOAT-INDICATORS.md](DATA-MOAT-INDICATORS.md)
