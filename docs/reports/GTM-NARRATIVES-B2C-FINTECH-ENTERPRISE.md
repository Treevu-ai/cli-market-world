# Narrativas GTM — B2C, Fintech, Enterprise

**Fecha:** 2026-07-21
**Estado de tiers verificado contra:** `routers/mcp_http.py` (`_PRO_TOOLS`, commit `defbef22`)

---

## 1. B2C / Usuario Final — "Tu Copiloto de Ahorro e Inteligencia de Compra"

**Posicionamiento correcto: Pro ($39/mes), no free.** Casi todas las tools del pitch son `[Pro]`.

| Tool en el pitch | Tier real |
|---|---|
| `market_promo_detector` | **[Pro]** (recién tagueado — antes devolvía error crudo en vez de upgrade prompt) |
| `market_optimize_purchase` | **[Pro]** |
| `market_basket` | **[Pro]** |
| `market_alert_create` | **[Pro]** |
| `market_household_update` | **[Pro]** |
| `market_household_get` | [Starter] — único accesible en trial de 7 días |

Problema → Solución → Enganche/Optimización/Alertas/Personalización se mantiene como estructura de pitch, pero el CTA debe ser "empieza tu trial de 7 días / Pro $39", no "gratis".

## 2. Fintech / Neobancos — "Affordability & Smart Shopping Engine"

B2B, asume acceso pagado — coherente en general. Ojo con:

| Tool | Riesgo |
|---|---|
| `market_inflation`, `market_affordability` | Documentadas sin tag `[Pro]` en la capa MCP, pero el backend (`routers/intel.py`) ya exige `require_pro()`. Mismatch aún sin resolver — avisar al equipo de integración del partner para que no pruebe con key Starter. |
| `market_checkout` | [Pro] — para integración B2B real, evaluar si el modelo de tier individual ($39) aplica o si esto debería ir a un acuerdo Enterprise/revenue-share. |
| `market_substitutes` | Accesible con cualquier API key (Starter+), sin sorpresas. |

## 3. Enterprise / Retail Analytics — "Matriz de Market Intelligence LATAM"

La más limpia. `market_search`, `market_exchange`, `market_price_history` son genuinamente Free/Starter, sin fricción.

- `market_macro` — mismo mismatch que `inflation`/`affordability`: sin tag en MCP pero `require_pro()` en backend.

## Guion de demo recomendado (del pitch original)

1. **Enganche:** `market_promo_detector`
2. **Ahorro masivo:** `market_optimize_purchase`
3. **Cierre:** `market_checkout`

Los 3 pasos son Pro. Correr la demo con una cuenta Pro real, no con una key Starter/trial — de lo contrario el Paso 2 y 3 ya devolvían upgrade prompt (correcto, no error), pero antes del fix de hoy el Paso 1 rompía con un HTTP error crudo justo en el momento diseñado para enganchar al prospecto.

## Deuda pendiente (no resuelta hoy)

`market_inflation`, `market_affordability`, `market_macro`, `market_scores`, `market_intel_brief`, `market_indicators`, `market_dashboard` — documentados como Free en la capa MCP (`routers/mcp_http.py`) pero gateados como Pro en el backend real (`routers/intel.py`, `require_pro()`). Mismo bug de fondo que motivó todo este documento, todavía sin cerrar en el proxy MCP. Ver `docs/reports/PRICING-INTELLIGENCE-TIER-REVIEW.md` para el análisis completo de repricing de esa capa.
