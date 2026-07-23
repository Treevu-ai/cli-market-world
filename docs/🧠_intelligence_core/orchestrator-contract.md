# CLI Market — Orchestrator Contract

> Contrato del pipeline: un **orquestador** entiende el request, clasifica **tools MCP/API**, selecciona **sub-agentes** de enriquecimiento y sintetiza la respuesta final.
>
> Implementación de referencia: `ops/market_orchestrator.py`  
> Workflow hermano (fijo, no dinámico): `docs/agents/price-pulse-workflow.md`

---

## 1. Principios

| # | Principio | Implicación |
|---|-----------|-------------|
| 1 | **Un solo orquestador** | Solo él decide tools y sub-agentes. Los sub-agentes no eligen tools por defecto. |
| 2 | **Tools = hechos** | `market_*` aportan precios, señales, carrito, moat. Nunca inventar datos. |
| 3 | **Sub-agentes = juicio** | Interpretan el payload de tools + intent; producen narrativa, tradeoffs, next actions. |
| 4 | **Mínimo viable de tools** | Preferir 1–4 tools. No llamar el catálogo completo. |
| 5 | **Mínimo viable de agentes** | Preferir 1–4 enrichers. Max 6 salvo `mode: deep`. |
| 6 | **Caveats explícitos** | Si el moat no tiene stock/delivery/competitividad, el plan lo declara. |
| 7 | **Idempotencia de plan** | Mismo request + mismos defaults → mismo `plan` (salvo reloj en `meta`). |

---

## 2. Pipeline (orden obligatorio)

```text
Request
  → (1) UNDERSTAND   IntentEnvelope
  → (2) PLAN         OrchestratorPlan  { tools[], agents[], response_spec }
  → (3) EXECUTE      ToolResults[]     (hechos)
  → (4) ENRICH       AgentOutputs[]    (juicio, solo sobre ToolResults + intent)
  → (5) SYNTHESIZE   FinalResponse
```

Dependencias:

- (2) depende de (1)
- (3) depende de (2)
- (4) depende de (2) y (3)
- (5) depende de (1)–(4)

No se enriquece sin resultados de tools. Para `product_help` y `ambiguous`, `tools`/`agents` pueden ser `[]` — SYNTHESIZE responde directo (copy estático o pregunta aclaratoria), sin llamada LLM de enriquecimiento (ver 4.4, roster v2).

---

## 3. Schema — `IntentEnvelope`

Clasificación del request del usuario.

```json
{
  "intent_id": "uuid-or-slug",
  "primary": "basket_optimize",
  "secondary": ["procurement_timing"],
  "language": "es",
  "locale_hint": "PE",
  "entities": {
    "country": "PE",
    "line": "supermercados",
    "store": null,
    "items": [
      { "name": "leche", "qty": 2 },
      { "name": "arroz", "qty": 1 }
    ],
    "product_query": null,
    "product_id": null,
    "barcode": null,
    "ticket_url": null,
    "budget": 800,
    "payment_method": null,
    "segment": "hotelero",
    "use_case": "amenities",
    "days": 30,
    "constraints": {
      "preferred_stores": [],
      "allow_substitutes": true,
      "include_tco": true,
      "max_stores": 2
    }
  },
  "user_tier_hint": "free|starter|pro|unknown",
  "risk_flags": [],
  "confidence": 0.0,
  "raw_request": "texto original del usuario"
}
```

### 3.1 `primary` (enum cerrado)

| primary | Descripción | Usuario típico |
|---------|-------------|----------------|
| `product_search` | Buscar / comparar un producto | Consumer / agente |
| `basket_optimize` | Canasta multi-ítem + TCO | Consumer / hotel / rest. |
| `procurement_timing` | ¿Comprar ahora o esperar? | Procurement |
| `market_intel` | Inflación, scores, affordability, brief | Analista / Sinapsis |
| `retailer_ops` | Scorecard tienda, stats moat | Ops / partner |
| `ticket_audit` | OCR ticket vs moat | Finance / consumer |
| `household_prefs` | Perfil hogar, alertas, favoritos | Consumer |
| `commerce_action` | Add / cart / checkout / orders | Agente autenticado |
| `product_help` | Cómo funciona CLI Market / tiers | Prospect / sales |
| `ambiguous` | No se pudo clasificar con confianza | — |

`secondary` es un array del mismo enum (0–3 valores) para intents compuestos.

### 3.2 Reglas de clasificación (deterministas, prioridad de arriba a abajo)

1. Contiene URL de imagen / “ticket” / “boleta” / “recibo” → `ticket_audit`
2. Lista de ítems (comas o “y”) + (presupuesto|optimiz|canasta|compra semanal) → `basket_optimize`
3. “¿compro ya?” / “esperar” / “procurement” / “forward buy” → `procurement_timing`
4. “inflación” / “affordability” / “intel” / “scores” / “riesgo de precio” → `market_intel`
5. “scorecard” / “cobertura de tienda” / “frescura del moat” → `retailer_ops`
6. “alerta” / “favoritos” / “hogar” / “household” / “presupuesto mensual” (sin canasta) → `household_prefs`
7. “agregar al carrito” / “checkout” / “pedidos” / “reordenar” → `commerce_action`
8. “cómo funciona” / “API” / “MCP” / “plan Pro” / “demo” → `product_help`
9. Query de un solo producto / “compara X” / barcode → `product_search`
10. Si confidence < 0.55 → `ambiguous` (repreguntar; no ejecutar tools de pago)

---

## 4. Schema — `OrchestratorPlan`

Salida del paso PLAN. Es el contrato ejecutable.

```json
{
  "plan_id": "plan_...",
  "intent": { "$ref": "IntentEnvelope" },
  "mode": "fast|standard|deep",
  "tools": [
    {
      "tool": "market_optimize_purchase",
      "args": {},
      "required": true,
      "on_error": "abort|continue|fallback",
      "fallback_tool": null,
      "why": "TCO multi-ítem con segment hotelero"
    }
  ],
  "agents": [
    {
      "id": "pricing-analyst",
      "role_path": "specialized/specialized-pricing-analyst.md",
      "context_path": "docs/agents/contexts/pricing-analyst-context.md",
      "depends_on_tools": ["market_optimize_purchase"],
      "input_slice": ["optimization", "substitutes", "stores"],
      "output_section": "ranking_and_unit_value",
      "parallel_group": 1
    }
  ],
  "response_spec": {
    "format": "markdown",
    "sections": [
      "summary",
      "facts",
      "enrichment",
      "recommendation",
      "caveats",
      "next_actions"
    ],
    "max_bullets_summary": 5,
    "language": "es",
    "audience": "consumer|procurement|executive|developer"
  },
  "guards": {
    "max_tools": 4,
    "max_agents": 4,
    "forbid_checkout_without_confirm": true,
    "require_country": true
  },
  "meta": {
    "created_at": "ISO-8601",
    "orchestrator_version": "0.1.0"
  }
}
```

### 4.1 Catálogo de tools permitidas (default profile)

Solo estas keys en `tools[].tool` (perfil MCP default / alias estables):

| tool | Familia |
|------|---------|
| `market_discover` | coverage |
| `market_search` | shop |
| `market_compare` | shop |
| `market_substitutes` | shop |
| `market_optimize_purchase` | shop |
| `market_ask` | shop |
| `market_add` | commerce |
| `market_cart` | commerce |
| `market_cart_update` | commerce |
| `market_checkout` | commerce |
| `market_orders` | commerce |
| `market_barcode` | shop |
| `market_ticket` | audit |
| `market_intel_brief` | intel |
| `market_inflation` | intel |
| `market_inflation_report` | intel |
| `market_scores` | intel |
| `market_affordability` | intel |
| `market_price_risk` | intel |
| `market_procurement_signal` | intel |
| `market_trending` | intel |
| `market_price_history` | intel |
| `market_price_alerts` | account |
| `market_favorites` | account |
| `market_household_get` | account |
| `market_household_update` | account |
| `market_retailer_scorecard` | ops |
| `market_informal_signal` | ops (honestidad de cobertura formal — nunca % de informal) |
| `market_promo_detector` | ops (autenticidad de descuento, opcional en modo deep para product_search) |
| `market_stats` | ops |
| `market_export` | ops |
| `market_whoami` | account |
| `market_subscription` | account |

### 4.2 Matriz intent → tools (default)

| primary | tools (orden) | on_error |
|---------|---------------|----------|
| `product_search` | `market_compare` o `market_search`; opcional `market_substitutes` | fallback search↔compare |
| `basket_optimize` | opcional `market_household_get` → `market_optimize_purchase`; opcional `market_procurement_signal` | abort si optimize falla |
| `procurement_timing` | `market_procurement_signal` + `market_price_risk` + opcional `market_intel_brief` | continue parcial |
| `market_intel` | `market_intel_brief` + opcional `market_inflation_report` + `market_scores` | continue parcial |
| `retailer_ops` | `market_discover` → `market_retailer_scorecard` + `market_stats` | abort sin store |
| `ticket_audit` | `market_ticket`; opcional `market_compare` por ítems caros | abort sin url |
| `household_prefs` | `market_household_get` / `update`; opcional `market_price_alerts` | continue |
| `commerce_action` | `market_whoami` → `market_cart` / `add` / `checkout` / `orders` | abort si 401 |
| `product_help` | `market_discover` + `market_subscription` (opc.) | continue sin auth |
| `ambiguous` | `[]` | no ejecutar |

### 4.3 Catálogo de sub-agentes (roster v2 — consolidado 2026-07-16, 14 → 6)

Recorte tras auditoría: de 14 agentes v1 quedan 4 indispensables (transversales, con grounding concreto contra ToolResults) + 2 condicionales (solo se seleccionan para su intent/segmento). Los 8 restantes se cortaron — ver justificación en `AGENT_CATALOG` de `ops/market_orchestrator.py`. No se borraron sus archivos de contexto donde servían a otro propósito (`financial-analyst`, `fpa-analyst`, `bookkeeper` siguen existiendo para Price Pulse, sin tocar).

| id | role_path (agency-agents) | Cuándo seleccionarlo |
|----|---------------------------|----------------------|
| `pricing-analyst` | `specialized/specialized-pricing-analyst.md` | search, basket, ticket, household — el más transversal |
| `supply-chain` | `specialized/supply-chain-strategist.md` | procurement_timing, basket B2B |
| `operations` | `specialized/operations-manager.md` | basket multi-tienda, segment ops |
| `reality-checker` | `testing/testing-reality-checker.md` | siempre presente en standard/deep — backstop anti-alucinación |
| `analytics-reporter` | `support/support-analytics-reporter.md` | retailer_ops, market_intel, export, stats |
| `hospitality` | `specialized/hospitality-guest-services.md` | segment hotelero (condicional) |

**Cortados (no forman parte del roster activo del orquestador):** `financial-analyst`, `fpa-analyst`, `bookkeeper` (contexto shape-eado para el JSON semanal de Price Pulse, no para `ToolResult`/`FactIndex` de este contrato), `executive-summary`, `document-generator` (redundantes con el paso SYNTHESIZE — el modo `deep` ya cubre resumen ejecutivo y deliverable sin una llamada LLM aparte), `support-responder` (copy de error/ambigüedad es texto determinista, no necesita LLM con grounding), `sales-engineer` (no hay ToolResult que enriquecer — es contenido de soporte/ventas, categoría de request distinta), `behavioral-nudge` (genérico, se pliega dentro de `pricing-analyst` para `household_prefs`).

### 4.4 Matriz intent → agents (default, roster v2)

| primary | agents (parallel_group) |
|---------|-------------------------|
| `product_search` | pricing-analyst(1), reality-checker(2) — + `market_promo_detector` opcional en modo deep |
| `basket_optimize` | pricing-analyst(1), operations(1), hospitality(1 si segment=hotelero), supply-chain(1 si segment/deep), reality-checker(2) |
| `procurement_timing` | supply-chain(1), reality-checker(2) |
| `market_intel` | analytics-reporter(1) (incluye `market_informal_signal` como honestidad de cobertura, nunca como % de informal), reality-checker(2) |
| `retailer_ops` | analytics-reporter(1), reality-checker(1) |
| `ticket_audit` | pricing-analyst(1), reality-checker(2) |
| `household_prefs` | pricing-analyst(1), reality-checker(2) |
| `commerce_action` | reality-checker(1) — sin LLM de UX, SYNTHESIZE confirma con ToolResults directo |
| `product_help` | `[]` — sin LLM, SYNTHESIZE responde con `market_discover` crudo + copy estático |
| `ambiguous` | `[]` — sin LLM, SYNTHESIZE arma la pregunta aclaratoria del intent directo |

`mode: deep` ya no agrega agentes nuevos — el detalle extra vive en el modo deep del paso SYNTHESIZE, no en una llamada de enriquecimiento aparte.

---

## 5. Schema — `ToolResult`

```json
{
  "tool": "market_optimize_purchase",
  "ok": true,
  "status_code": 200,
  "latency_ms": 0,
  "args": {},
  "data": {},
  "error": null,
  "truncated": false,
  "confidence_notes": []
}
```

Reglas:

- El orquestador **no muta** `data` de la tool salvo truncado documentado (`truncated: true`).
- Errores 401/403 en commerce → no reintentar checkout; pedir login/tier.
- Timeouts: marcar `ok: false` y aplicar `on_error` del plan.

---

## 6. Schema — `AgentOutput`

```json
{
  "agent_id": "pricing-analyst",
  "section": "ranking_and_unit_value",
  "ok": true,
  "markdown": "...",
  "structured": {
    "top_picks": [],
    "tradeoffs": [],
    "warnings": []
  },
  "citations_to_tools": ["market_optimize_purchase"],
  "confidence": 0.0
}
```

Reglas del sub-agente:

1. Solo razona sobre `IntentEnvelope` + `ToolResult[]` asignados + **FactIndex** + su role/context.
2. **Prohibido** inventar precios, tiendas, canastas, IPC, stock o señales no presentes en `ToolResult` / FactIndex.
3. Si falta dato: escribirlo en `warnings`, no rellenar.
4. Toda afirmación cuantitativa debe poder anclarse a un `citations_to_tools[]` y a un literal en FactIndex.
5. Runtime (`ops/market_orchestrator.py` ≥0.2.1): construye FactIndex, valida números post-LLM, y corre `reality-checker` al final con drafts de peers.

---

## 7. Schema — `FinalResponse`

```json
{
  "response_id": "resp_...",
  "plan_id": "plan_...",
  "intent_primary": "basket_optimize",
  "language": "es",
  "summary": ["..."],
  "facts": {
    "tools_used": ["market_optimize_purchase"],
    "highlights": []
  },
  "enrichment": {
    "sections": [
      { "agent_id": "pricing-analyst", "title": "...", "markdown": "..." }
    ]
  },
  "recommendation": {
    "action": "buy_now|split_stores|wait|monitor|login_required|clarify",
    "rationale": "...",
    "confidence": 0.0
  },
  "caveats": [
    "El scorecard de retailer no incluye competitividad cross-store ni stock."
  ],
  "next_actions": [
    { "type": "tool|user|agent", "label": "Confirmar checkout", "payload": {} }
  ],
  "raw": {
    "intent": {},
    "plan": {},
    "tool_results": [],
    "agent_outputs": []
  }
}
```

### 7.1 Secciones de respuesta al usuario (markdown)

Orden fijo para UX:

1. **Resumen** (≤5 bullets)
2. **Hechos del moat** (tablas/números de tools)
3. **Análisis** (sub-agentes)
4. **Recomendación** (una acción principal)
5. **Caveats**
6. **Siguientes pasos**

---

## 8. Guards y políticas

| Guard | Comportamiento |
|-------|----------------|
| `forbid_checkout_without_confirm` | `market_checkout` solo si el request lo pide explícitamente o hay `confirm: true` en entities |
| `require_country` | Default `PE` si falta; anunciar default en caveats |
| No inventar stock/delivery | Reality-checker + plantilla de caveat |
| Tier | Si tool requiere Pro y falla, next_action = upgrade/login |
| PII | No loguear passwords; tokens solo en session store del CLI |

---

## 9. Prompt del orquestador (system, resumen)

El orquestador de runtime (LLM o reglas) debe:

1. Emitir **solo** JSON válido `OrchestratorPlan` en el paso PLAN (o usar el planner determinista).
2. Ejecutar tools en orden; respetar `required` / `on_error`.
3. Despachar sub-agentes por `parallel_group` (menor número primero; mismo grupo = paralelo).
4. Sintetizar `FinalResponse` sin contradecir `ToolResult`.
5. Si `primary=ambiguous`, una sola pregunta de clarificación; no ejecutar commerce.

Plantilla completa: ver `docs/agents/contexts/orchestrator-context.md`.

---

## 10. Versionado

| Campo | Valor |
|-------|-------|
| `orchestrator_version` | `0.2.0` |
| Schema status | ejecutable (tools HTTP alineados a OpenAPI + LLM enrichers) |
| Compatible con | MCP profile default (~31 tools), agency-agents roster v1 |
| Runtime | `ops/market_orchestrator.py` — auth via session/API key; LLM via OpenAI/Anthropic/xAI/Ollama |

Cambios breaking (renombrar `primary`, quitar tools del catálogo) → bump minor/major y actualizar `ops/market_orchestrator.py`.

---

## 11. Relación con Price Pulse

| | Price Pulse | Market Orchestrator |
|--|-------------|---------------------|
| Trigger | Semanal / dashboard | Request del usuario en tiempo real |
| Tools | `/dashboard/data` fijo | Set dinámico `market_*` |
| Agents | 5 finance fijos | Subset dinámico del roster v1 |
| Output | PDF multi-sección | `FinalResponse` + markdown |

Price Pulse es un **plan congelado** de este contrato (`primary=market_intel`, agents finance-only, tool=dashboard slice).
