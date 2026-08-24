---
title: Backlog — Góndola Digital
status: Draft
updated: 2026-08-24
prd: docs/prd-digital-gondola-v0.md
owner: Ricardo Cuba
---

# Backlog: Góndola Digital

Prioridad = impacto en el piloto de Intelligence / trade, no “completitud vs Nielsen”.  
Toda historia hereda los **non-goals** del PRD: cero facings, planograma, POS share, market share.

**Leyenda:** `P0` bloquea piloto · `P1` cierra el paquete comercial · `P2` no entra al primer SOW.

---

## Now — v0 (contrato + motor + API/MCP)

Objetivo: un cliente pega categoría + país + portafolio y recibe **3–7 acciones con evidencia** en &lt;8 min, con disclaimer de góndola digital.

### DG-01 — Schema del consejo (`gondola-advise`)
**P0 · core**  
Como plataforma, quiero un contrato JSON versionado (`scope`, `not_included`, `coverage`, `landscape`, `actions[]`) para que REST, MCP y PDF no diverjan.

**AC:**
- [ ] Schema publicado (OpenAPI o JSON Schema) en repo; `type` enum cerrado: `LIST|PRICE|PROMO|HOLD`.
- [ ] `not_included` siempre presente con physical_space, facings, planogram, pos_share, market_share.
- [ ] Test: payload sin `evidence` en `LIST|PRICE|PROMO` falla.
- [ ] Test: rationale con palabra denylist (`facing`, `planograma`, `share of shelf`, `espacio lineal`) falla.

**No hacer:** campos `facings`, `linear_cm`, `share_of_shelf`.

### DG-02 — Cobertura SKU × store
**P0 · core**  
Como Elena (trade), quiero celdas `listed|missing|stale|insufficient_data` para mi portafolio × retailers del país.

**AC:**
- [ ] Input: `country`, `line`/`category`, lista de queries o `product_id`s.
- [ ] Frescura: si el store no tiene snapshot reciente (mismo SLA que el resto de intel), celda `stale` — **no** `missing`.
- [ ] Reutilizar snapshots; no nuevo crawl ad hoc.
- [ ] Extiende o envuelve `build_coverage_matrix` (hoy línea×país); no reemplazar esa API pública sin deprecación.

**Esfuerzo:** M — es el hueco real vs la matriz actual.

### DG-03 — Landscape de precio normalizado
**P0 · core**  
Como Diego (pricing), quiero p20/p50/p80 y spread de la subcategoría en unidad comparable (kg/L/unidad).

**AC:**
- [ ] Misma normalización que compare/intel (no mezclar pack 400g con 1L sin convertir).
- [ ] Si no hay unidad comparable, `landscape.status = insufficient_data`.
- [ ] No inventar PVP.

### DG-04 — Motor de acciones (reglas)
**P0 · core**  
Como Elena, quiero acciones priorizadas 1–N derivadas de cobertura + landscape + PVP opcional.

**Reglas mínimas v0:**

| Si | Entonces |
|----|----------|
| Portafolio `missing` en store fresco | `LIST` |
| Store `stale` | no `LIST`; `HOLD` o omitir |
| PVP cargado y desvío &gt; +5% o &lt; −15% | `PRICE` (umbrales Brand Intel) |
| Competidor con discount&gt;0 y propio sin discount, mismo store, SKU comparable | `PROMO` (hipótesis) |
| Gap de tier (hueco p20–p80) + cobertura suficiente | `LIST` o `HOLD` con atractivo acotado |
| Poca cobertura de categoría | `HOLD` + `insufficient_data` |

**AC:**
- [ ] LLM opcional **solo** reescribe `rationale` a partir de `evidence`; no elige `type`.
- [ ] Máximo 7 acciones; orden por (tipo LIST/PRICE antes que vanity, luego spread, luego frescura).
- [ ] Tests unitarios por regla con fixtures de snapshots, sin red.

### DG-05 — REST `/v1/intel/gondola-advise`
**P0 · world + core**  
Como analista o integración, quiero POST con API key Intelligence/Pro.

**AC:**
- [ ] Auth igual que otros intel; 403 si el tier no alcanza (gate en world; core no tiene billing).
- [ ] 422 si falta country o category.
- [ ] Idempotencia no requerida v0; sí `run_id` en respuesta.
- [ ] Persistencia opcional `gondola_advice_run` para reconstruir el one-pager del piloto.

### DG-06 — MCP `market_gondola_advise`
**P0 · core stdio + world HTTP**  
Como agente, quiero la misma tool en las **dos** superficies MCP.

**AC:**
- [ ] Registrada en `market_mcp_registry.py` **y** `routers/mcp_http.py` (`_TOOLS` + `_call_tool` + `_PRE_CHECK_TIER` si aplica).
- [ ] Test de paridad HTTP: toda tool en lista tiene branch de dispatch (patrón existente).
- [ ] Descripción de la tool dice explícitamente “digital shelf / góndola formal online; not planogram”.

### DG-07 — Denylist + copy GTM mínimo
**P0 · world docs + tests**  
Como GTM, quiero que el producto no se pueda describir como Nielsen espacio.

**AC:**
- [ ] One-pager Intelligence actualizado: “no incluye espacio físico / planograma”.
- [ ] README GTM enlaza PRD + backlog.
- [ ] Script de objeción Nielsen en el PRD (ya escrito) — no hace falta landing nueva en v0.

---

## Next — v0.1 / v0.2 (paquete vendible)

### DG-08 — PDF one-pager (2 páginas)
**P1 · world**  
Como agencia, quiero un PDF del `run_id` para el QBR.

**AC:**
- [ ] Portada: país, categoría, freshness, disclaimer.
- [ ] Pág. 2: grid resumido + 5 acciones.
- [ ] Mismos claims que el JSON; generación sin LLM o LLM grounded.
- [ ] No es el Category Report de 8 páginas de Brand Intel.

### DG-09 — CLI `market gondola`
**P1 · world/core**  
Como usuario Pro, quiero un comando que imprima el JSON/tabla.

**AC:**
- [ ] Reusa el endpoint; no segunda implementación.
- [ ] `--json` obligatorio para agentes.

### DG-10 — Dashboard `/intelligence/gondola`
**P1 · world landing**  
Como piloto, quiero pegar el resultado sin Postman.

**AC:**
- [ ] Una pantalla: inputs + grid + cards.
- [ ] Banner permanente de alcance (digital, no físico).
- [ ] No mezclar CTA Procure.

### DG-11 — PVP y competidores = Brand Intel
**P1**  
Como Diego, quiero cargar PVP una vez y reusarlos.

**AC:**
- [ ] Si Brand Monitor existe, leer PVP/competidores declarados.
- [ ] Si no, el request acepta `pvp[]` y `competitors[]`.
- [ ] No cross-sharing entre marcas (misma regla Brand Intel).

### DG-12 — Alerta de delistado
**P1**  
Como Elena, quiero saber si un SKU listado pasó a `missing`/`stale` vs el run anterior.

**AC:**
- [ ] Diff entre `run_id` N y N−1.
- [ ] Canal: email o Slack bitácora interno del piloto — no spam WhatsApp.
- [ ] No alertar `missing` cuando el store está `stale`.

### DG-13 — Promo authenticity
**P2 · next**  
Reusar `market_promo_detector` para no tratar todo discount crawleado como promo real.

**AC:**
- [ ] Acciones `PROMO` bajan a `low` si el detector flaggea.
- [ ] No bloquear v0.

### DG-14 — Multi-categoría en un SOW
**P2**  
Hasta 3 categorías / país en un job batch, misma disciplina de ≤8 subcats cada una.

---

## Later — solo con dato que no tenemos

Estas ítems **no se estiman ni se “preparan” en v0**. Se reabren con evidencia: POS del retailer, auditoría, o partnership.

| ID | Ítem | Señal para abrir |
|----|------|------------------|
| DG-20 | Ingestión POS / sell-out del cliente | Un piloto trae sell-out bajo NDA y pide cruzar con listado digital |
| DG-21 | Planograma / facings | Cadena entrega planograma o auditoría; no inferir del HTML |
| DG-22 | Elasticidad de espacio | Requiere DG-20+DG-21; no es CLI Market solo |
| DG-23 | Share of shelf físico | Auditoría en tienda o imagen; fuera de alcance orgánico |
| DG-24 | Store clustering (express vs hipermercado) | Útil para retailer; necesita maestro de locales del cliente |
| DG-25 | Auto-push al PIM/ERP del retailer | Solo después de que LIST/PRICE se acepten a mano en n≥3 clientes |

---

## Explicitly not doing

| Pedido típico | Respuesta |
|---------------|-----------|
| “Optimicen la góndola como Nielsen” | Góndola **digital**; Nielsen/POS para espacio |
| “Digan nuestro market share” | No. Conteo de SKUs ≠ share |
| “Cuánto espacio lineal tenemos vs competencia” | No hay dato |
| “Que el agente recategorice la tienda sola” | Acciones son propuestas; humano aprueba |
| “Incluyan feria / bodega” | Fuera de moat; informal_signal es honestidad, no medición |
| Landing “Nielsen killer” | Prohibido |

---

## Sprint slices (sugeridos)

| Sprint | Entregar | Demo |
|--------|----------|------|
| 1 | DG-01, DG-02, DG-03, tests denylist | JSON de lácteos PE con grid honesto (stale≠missing) |
| 2 | DG-04, DG-05, DG-06, DG-07 | MCP + REST; objeción Nielsen en el payload |
| 3 (v0.1) | DG-08, DG-09 | PDF de 2 páginas a una agencia |
| 4 (v0.2) | DG-10, DG-11 | Dashboard + PVP |

Si el sprint 1 demuestra que SKU×store es basura por entity resolution, **parar** y no inventar acciones `LIST`. El producto no se lanza con missing falsos.

---

## Owners (mientras no haya equipo formal)

| Área | DRI |
|------|-----|
| PRD / alcance / no-goals | Producto (este doc) |
| Engine + schema + tests | core |
| Router, MCP HTTP, billing gate, PDF, dashboard | world |
| Copy claims / outreach | content + GTM Hub |
| Index / golden records | solo si DG-02 falla por matching |

---

## Tracking

- Cada run de piloto: `run_id`, categoría, #acciones, #marcadas útiles (planilla; no hace falta producto de feedback en v0).
- Kill criterion: 3 pilotos con &lt;20% acciones útiles **o** 1 incidente de overclaim Nielsen en material enviado a cliente.
- Ampliar a Later (POS) solo con dato del cliente, no con más crawlers.
