# P0 — Bloqueadores de contrato API, canasta GLORIA (PE, enterprise)

**Fecha:** 2026-07-30
**Reportado por:** Ricardo Cuba, tras ejecutar 10 prompts analíticos de procura sobre la
canasta lácteos GLORIA (tier enterprise). Playbook alcanzó la decisión operativa (comprar
en Makro, S/ 958.14) solo con validación manual de SKUs.
**Alcance de la investigación:** verificación directa contra `https://cli-market-api.fly.dev`
en producción (curl + llamadas MCP), y contra el código fuente de `cli-market-core`
(repo local `C:\Users\acuba\cli-market-core`, `main` @ 1.11.91) y `cli-market-world`
(este repo).

---

## Hallazgo 1 (P0) — Tres MCP tools apuntan a endpoints que nunca se implementaron

**Tools afectadas:** `market_basket_stress`, `market_commerce_pulse`, `market_arbitrage`
(y probablemente `market_price_forecast`, ver nota).

**Síntoma:** 404 al invocarlas desde Cursor y desde cualquier cliente MCP.

**Verificación:**
- `curl https://cli-market-api.fly.dev/v1/intel/basket-stress?country=PE` → `404`
- `curl https://cli-market-api.fly.dev/v1/intel/pulse?country=PE` → `404`
- `curl https://cli-market-api.fly.dev/v1/intel/arbitrage?product=leche&countries=PE,MX` → `404`
- `GET /openapi.json` en producción confirma que esas tres rutas no están en el spec activo
  (sí están `/v1/intel/procurement-bulk`, `/procurement-signal`, `/promo-detector`,
  `/retailer-scorecard`, `/inflation-report`, `/informal-signal`, etc.)

**Causa raíz:** commit `cli-market-core@0f539d3` ("fix(security): SSRF-safe alert webhook
dispatch + 5 new intel MCP tools (v1.11.46)", 2026-07-17) agregó los tool handlers y
entradas de registry en `market_core/market_mcp_registry.py` / `market_mcp.py` para estas
tools, bajo la premisa (declarada en el propio mensaje del commit) de que los endpoints
REST *"ya existían"*. Verificado con `git log --all -S'"/basket-stress"' -- market_core/api_routes.py`
(y lo mismo para `/pulse`, `/arbitrage`, `/forecast`) sobre el historial completo del repo:
**cero commits** — esas rutas nunca se implementaron, ni siquiera transitoriamente. No hay
PR ni rama en progreso que las cubra.

**Impacto:** cualquier agente/cliente que confíe en el registry de tools disponibles
(que sí las declara con schema completo) recibe 404 en tiempo de ejecución. Rompe
`market_ecosystem_radar`/`market_intel_brief`-adyacentes flujos que esperan basket
stress y pulse semanal como señales de apoyo.

**Fix propuesto:**
1. Implementar `GET /v1/intel/basket-stress`, `GET /v1/intel/pulse`, `GET /v1/intel/arbitrage`
   en `cli-market-core/market_core/api_routes.py`. Reutilizar lógica ya existente donde
   aplique — `market_procurement_signal` ya calcula un basket stress index; `market_intel_brief`
   ya agrega inflación + basket stress + actividad de promos, que es justo lo que
   `commerce_pulse` promete sintetizar.
2. Confirmar si `market_price_forecast` (`/v1/intel/forecast`) tiene el mismo problema —
   tampoco apareció en el `openapi.json` de producción revisado en esta investigación.
3. Publicar nueva versión de `cli-market-core`, bump del pin en `cli-market-world`
   (mismo patrón que el bump reciente a 1.11.91).
4. Agregar un check de CI que valide que todo tool en `market_mcp_registry.py` tenga una
   ruta correspondiente resuelta en el `openapi.json` desplegado — para que este tipo de
   contrato roto no vuelva a llegar a producción silenciosamente.

---

## Hallazgo 2 (P0) — `market_procurement_bulk` responde 500 con input malformado en vez de 422

**Síntoma reportado:** 500 al pasar una canasta de SKUs.

**Repro exacto:**
```
lines: ["leche gloria", "yogurt gloria"]   # array de strings, sin envolver en objetos
→ HTTP 500
```
Con el formato correcto documentado en el schema —
`lines: [{"sku_query": "...", "qty": N, "unit": "..."}]` — el endpoint responde 200
consistentemente. Probado con `qty` string, `qty` numérico, sin `unit`, con 1 línea y con
10 líneas: todos OK.

**Causa raíz probable:** el handler de `/v1/intel/procurement-bulk` en `api_routes.py`
probablemente hace `line.get("sku_query")` (o similar) sin validar que cada elemento de
`lines` sea un dict antes de accederlo — un string no tiene `.get()`, lo que produce una
excepción no capturada → 500 en vez de una validación Pydantic normal (422).

**Fix propuesto:** declarar `lines` con un modelo Pydantic tipado
(`list[ProcurementLine]`) en vez de `list[dict]` suelto, para que FastAPI devuelva 422
con el detalle del campo inválido automáticamente.

---

## Hallazgo 3 (P1) — `market_optimize_purchase` resuelve el mismo SKU a productos distintos dentro de la misma respuesta

**Síntoma:** para el ítem `"yogurt gloria"` en una sola llamada, la respuesta contiene
**tres productos GLORIA distintos** en tres secciones distintas:
- `items_resolved`: Yogurt Batido GLORIA Griego Frutos Rojos, S/ 1.79
- `product_links`: Yogurt GLORIA Batishake Vainilla, S/ 2.90
- `sections.compare.breakdown`: Yogurt GLORIA Battimix Vainilla c/ Arroz Crujiente, S/ 2.90

Además, `"leche evaporada gloria"` aparece resuelto en `items_resolved` pero desaparece
de `sections.compare.breakdown` (`items_found: 2` de 3 solicitados).

**Impacto:** el total mostrado (`shelf_total`/`tco_total`) no es reconstruible a partir de
los ítems individuales listados — cada sección "cuenta una historia" distinta de qué se
está comprando. Esto invalida cualquier automatización de compra basada en la respuesta
completa sin re-validación manual SKU por SKU (que es justo el problema original
reportado por el usuario).

**Fix propuesto:** unificar la resolución de producto a una sola pasada — resolver cada
ítem del basket una vez, y que todas las secciones (`items_resolved`, `product_links`,
`compare.breakdown`) referencien el mismo `product_id` resuelto.

---

## Hallazgo 4 (P1) — `market_procurement_bulk`: substitutes cruzan categoría de producto

**Síntoma:** en la misma corrida de 10 SKUs GLORIA:
- `"mantequilla gloria"` → substitute sugerido: **"Queso Crema Sabor a Jamón GLORIA"**
- `"leche condensada gloria"` → substitute sugerido: **"Queso Crema Natural GLORIA"**

Ambos casos marcados con `match_reason: "same_canasta_item+unit_equivalent"` y
`confidence: "ok"` — es decir, el sistema afirma con confianza alta que mantequilla y
queso crema son sustitutos válidos, lo cual es incorrecto.

**Impacto:** más grave que un `best_match: null` (Hallazgo ya conocido, 2/10 SKUs sin
match en la misma corrida) porque esto devuelve una respuesta *confiada pero
incorrecta* — no hay señal de que el resultado necesite revisión manual.

**Fix propuesto:** revisar la lógica de matching de substitutes — el `canonical_product_id`
usado para encontrar sustitutos parece estar agrupando por proximidad de precio/tamaño de
paquete dentro de la categoría "lácteos" en general, sin filtrar por subcategoría real
(mantequilla vs. queso vs. crema son subcategorías distintas dentro de lácteos GLORIA).

---

## Hallazgo 5 (P1) — Historial de precios insuficiente invalida auditoría de promo

**Verificación:** `market_price_history` para "Leche Entera UHT GLORIA Caja 946ml"
(Makro, product_id 358217) devuelve solo **2 snapshots totales** (uno por tienda,
no una serie temporal). `market_promo_detector` sobre el mismo producto responde
`status: "insufficient_history", history_points: 1`.

**Re-diagnosticado 2026-07-30** (el collector lleva ~2 meses corriendo — la hipótesis
original de "cobertura insuficiente" no cuadraba con ese tiempo de operación).
Causa raíz real, confirmada en código (`cli-market-core/market_core/market_core.py:779`,
`append_price_history()`): `price_history` es un changelog append-on-change, no una
serie periódica — se llama en cada ciclo del collector para cada producto
(incondicional, `market_core.py:1122`), pero **solo inserta una fila nueva si `price`
cambió respecto al último punto registrado**, sin importar cuántas veces se haya
scrapeado el producto mientras tanto. No hay job de retención/purga (confirmado por
`grep` de `DELETE FROM price_history`, sin resultados) — las filas no se están
borrando, nunca se crearon. Se descartó además que el `product_id` esté rotando entre
scrapes (lo que resetearía el changelog invisiblemente): Makro es VTEX
(`market_connectors/vtex.py:482`) y su `product_id` viene directo de
`productReference`/`productId` de la propia API de VTEX, estable entre corridas.

**El verdadero bug**, más específico que "pocos snapshots": la condición de dedup
solo comparaba `price`, nunca `list_price`. Eso significa que el patrón exacto que
`promo_detector` existe para atrapar — inflar `list_price` manteniendo el precio
efectivo plano, para luego "descontar" contra ese list_price artificial — era
**invisible para `price_history` sin importar la frecuencia del collector**. El
guardrail de -53.9% RPV línea supermercados reportado como "publicado sin guardrail"
es consistente con esta carencia, pero la recomendación original (aumentar frecuencia
de captura) no la habría resuelto: llamar más seguido a un collector que ya
deduplica por `price` no genera más puntos si el precio no se mueve.

**Fix aplicado** (`cli-market-core` — ver su CHANGELOG.md, entrada 2026-07-30):
`append_price_history()` ahora también compara `list_price`, así que un movimiento de
solo `list_price` sí genera una fila nueva. Tests nuevos:
`cli-market-core/tests/test_append_price_history.py`. Sigue habiendo un componente
de infraestructura fuera de alcance de este fix: si el precio efectivo de un SKU es
genuinamente estable durante meses, `price_history` seguirá teniendo pocos puntos —
eso es correcto por diseño, no un bug — así que aumentar la frecuencia de captura
para SKUs GLORIA de alto volumen en Makro/PlazaVea sigue siendo recomendable antes de
GA de auditoría de promo, pero ya no es la causa principal de este hallazgo.

---

## No reproducido / no es bug

- **`market_export` "no filtra por canasta"**: confirmado como comportamiento esperado,
  no bug — el tool solo acepta `line` (categoría de tienda: supermercados, farmacias,
  etc.), no tiene ni tuvo nunca parámetro de marca/canasta. Es un gap de producto/API
  surface, no un contrato roto. Considerar agregar parámetro `brand` como mejora separada
  (no P0).
- **Hipótesis de "conector desfasado en Cursor"**: descartada. `cli-market-world` instalado
  = 1.11.45 (latest en PyPI). `cli-market-core` instalado = 1.11.89 (latest = 1.11.91,
  irrelevante para estos bugs). El problema es 100% del lado del servidor desplegado.
- **Puente CPI sin mapa nativo**: no investigado en esta pasada — pendiente si se requiere
  para GA.

---

## Prioridad para GA del playbook enterprise

**Bloqueantes de GA (P0):** Hallazgo 1 (tools 404) y Hallazgo 2 (500 sin validar input) —
ambos son contratos de API rotos, no matices de calidad de dato.

**Deben resolverse antes de confiar el playbook a automatización sin supervisión (P1):**
Hallazgo 3 (resolución de SKU inconsistente) y Hallazgo 4 (substitutes cruzando
categoría) — son la causa directa de por qué la decisión operativa solo fue alcanzable
con validación manual.

**Requiere trabajo de infraestructura de datos, no de código (P1, plazo más largo):**
Hallazgo 5 (cobertura de historial de precios).
