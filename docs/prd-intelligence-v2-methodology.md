---
title: PRD — Market Intelligence v2 · Metodología Defensible
tags:
  - product
  - prd
  - intelligence
  - price-pulse
status: Draft v1.0 — P0 shipped
owner: Head of Product + Lead Economist
updated: 2026-06-24
repos: cli-market-core, cli-market-backend, cli-market-world
methodology: docs/methodology.md
---

# PRD — Market Intelligence v2: Metodología Defensible

**Producto:** CLI Market Intelligence Reports  
**Autor:** Head of Product + Lead Economist  
**Estado:** Draft v1.0  
**Fecha:** 2026-06-24  
**Audiencia objetivo del reporte:** Procurement teams, CFOs, prensa económica, inversores

---

## 1. Problema

El reporte de inteligencia actual genera señales valiosas pero contiene métricas mal definidas, comparaciones temporalmente inconsistentes y términos que crean exposición regulatoria y reputacional. No es publicable en canales institucionales ni defendible ante un economista externo sin revisión mayor.

**Costo del problema:**

- Riesgo de cobertura negativa si "inflación de góndola" es citada fuera de contexto
- Credibilidad comprometida ante CFOs y analistas macro en demos enterprise
- BSI y price dispersion no son auditables — bloquean uso en propuestas formales

---

## 2. Objetivos

| Objetivo | Métrica de éxito |
|----------|------------------|
| Métricas públicamente defendibles | Cada indicador tiene fórmula documentada + n explícito |
| Eliminar riesgo regulatorio | Cero uso del término "inflación" sin calificador metodológico |
| Habilitar uso institucional | Reporte aprobado por revisor econométrico externo |
| Mantener valor comercial | Price dispersion y promo intensity como métricas propietarias diferenciadas |

---

## 3. Fuera de scope

- Cambiar la infraestructura de scraping o frecuencia de captura
- Reemplazar el IPC como referencia externa — solo cambiar cómo se comunica la relación
- Rediseño de UI del dashboard

---

## 4. Requerimientos por hallazgo

### 4.1 Renombrar y redefinir "inflación de góndola" — **P0 ✅**

**Problema:** término con definición legal-estadística en Perú. Crea conflicto directo con IPC-INEI.

**Jerarquía de nombres:**

| Contexto | Nombre |
|----------|--------|
| API / base de datos | `shelf_price_momentum_7d` |
| Dashboard / producto | **Retail Price Velocity (RPV)** |
| Newsletter / prensa | Movimiento de precios en góndola |
| Prohibido | "inflación" sin calificador explícito |

**Definición operacional:** ver [methodology.md §1](methodology.md#1-retail-price-velocity-rpv).

**Criterio de aceptación:** el término "inflación" sin calificador no aparece en ninguna superficie pública del producto.

### 4.2 Comparación con IPC — redefinir el benchmark externo — **P0 ✅**

**Problema:** comparación de WSPM semanal vs IPC anual o mensual. Incomparables por período y por metodología de canasta.

**Requerimiento:** eliminar la comparación directa "X puntos por debajo del IPC". Ver reglas en [methodology.md §2](methodology.md#2-comparación-con-ipc-oficial).

**Criterio de aceptación:** ningún reporte publica "brecha de X pp vs IPC" sin las condiciones cumplidas.

### 4.3 Basket Stress Index — fórmula y escala — **P0 ✅**

**Problema:** indicador publicado sin fórmula, sin escala definida, sin referencia histórica.

**Definición:** [methodology.md §3](methodology.md#3-basket-stress-index-bsi).

**Diferencia vs price dispersion:** BSI = volatilidad temporal (mismo retailer, distintos momentos). Price dispersion = variación cross-retailer en un mismo momento. Ortogonales.

**Criterio de aceptación:** BSI publicado siempre con escala, valor histórico de referencia y diferenciación explícita vs price dispersion.

### 4.4 Affordability Ratio — corregir sesgo del precio mínimo — **P1**

Publicar tres variantes (best / promedio / worst). Titular = promedio. Disclaimer obligatorio. Ver [methodology.md §4](methodology.md#4-affordability-ratio).

### 4.5 Price Dispersion — estandarizar definición — **P1**

Adoptar coeficiente de variación (CV) como métrica estándar. Ver [methodology.md §5](methodology.md#5-price-dispersion).

### 4.6 Promo Intensity — definición operacional — **P1**

Umbral mínimo de descuento 3%. Ver [methodology.md §6](methodology.md#6-promo-intensity).

### 4.7 Coverage & Freshness — métricas obligatorias — **P0 ✅**

Tabla de cobertura en cada reporte. Umbral <60% → `[COBERTURA PARCIAL]`. Ver [methodology.md §7](methodology.md#7-coverage--freshness).

### 4.8 Google Trends — declarar estructura causal — **P2**

Comunicar como correlación observada hasta caracterizar lag y dirección causal. Ver [methodology.md §8](methodology.md#8-google-trends).

---

## 5. Priorización

| Requerimiento | Prioridad | Esfuerzo | Bloquea publicación | Estado |
|---------------|-----------|----------|---------------------|--------|
| 4.1 Rename RPV | P0 | Bajo | Sí | ✅ Shipped |
| 4.2 Comparación IPC | P0 | Bajo | Sí | ✅ Shipped |
| 4.3 BSI fórmula + escala | P0 | Medio | Sí | ✅ Shipped |
| 4.4 Affordability ratio promedio | P1 | Bajo | No | 🔲 Pendiente |
| 4.5 Price dispersion CV | P1 | Medio | No | 🔲 Pendiente |
| 4.6 Promo umbral 3% | P1 | Medio | No | 🔲 Pendiente |
| 4.7 Coverage table | P0 | Alto | Sí | ✅ Shipped |
| 4.8 Trends causalidad | P2 | Alto | No | 🔲 Pendiente |

---

## 6. Entregables

| Entregable | Responsable | Fecha | Estado |
|------------|-------------|-------|--------|
| `/docs/methodology.md` — fórmulas completas | Lead Economist | Sprint 1 | ✅ |
| Actualización de nomenclatura en API y dashboard | Engineering | Sprint 1 | ✅ (core) |
| Reporte v2 con coverage table y disclaimers | Product | Sprint 2 | 🔲 |
| Análisis de causalidad Trends-precio | Data Science | Sprint 3 | 🔲 |
| Revisión externa por economista independiente | Head of Product | Pre-launch institucional | 🔲 |

---

## 7. Score objetivo post-implementación

| Dimensión | Actual | Target v2 |
|-----------|--------|-----------|
| Rigor financiero | 6/10 | 8.5/10 |
| Rigor econométrico | 5.5/10 | 8/10 |
| Valor comercial | 8.5/10 | 9/10 |
| Defensibilidad metodológica | 5/10 | 9/10 |

---

## 8. Criterio de lanzamiento

El reporte v2 está listo para uso institucional y prensa cuando:

- [x] P0s implementados y documentados en `/docs/methodology.md`
- [x] Ninguna superficie pública usa "inflación" sin calificador *(core/API/dashboard — sync world pendiente en copy legacy)*
- [x] BSI tiene fórmula, escala y contexto histórico visible
- [x] Coverage table incluida en cada emisión
- [ ] P1s implementados (affordability promedio, CV dispersion, promo 3%)
- [ ] Revisión externa completada

---

## 9. Próximo sprint (P1)

1. **Affordability v2** — titular con canasta promedio ponderada; best/worst en `components`
2. **Price dispersion** — forzar CV en API + reportes; deprecar `(max-min)/min` en copy
3. **Promo intensity** — documentar umbral 3% en `indicator_definitions.formula` y en reporte
4. **World sync** — `price_pulse_client.py`, agent prompts, `market_cli.py` labels → nomenclatura RPV

Ver también: [DATA-MOAT-INDICATORS.md](DATA-MOAT-INDICATORS.md) · [price-pulse-workflow.md](agents/price-pulse-workflow.md)
