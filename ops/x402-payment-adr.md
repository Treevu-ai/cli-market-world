# ADR: ¿Encaja x402 en el checkout de Procure Copilot?

> **Estado: investigación únicamente. Cero código de pagos tocado.** Cualquier
> implementación real es un plan separado, que pasa primero por el agente
> `security-reviewer` antes de tocar `procure-copilot/lib/procurement-*.ts`.

## Contexto

El skill `agent-payment-x402` (ECC) agrega pagos agente-a-agente vía protocolo x402
(HTTP 402 + wallets no-custodiales + límites de gasto por tarea). CLI Market se
posiciona como "commerce infrastructure for AI agents" — vale evaluar si x402 encaja en
el flujo de compra real, no en abstracto.

## El flujo real hoy (`procure-copilot/lib/`)

```
run (missions/optimize-purchase)
  → status: pending_approval | checkout_ready | rejected
  → [humano aprueba]  (approvalThreshold en el request)
  → prepareProcurementCheckout()          [procurement-checkout.ts]
      requiere options.buyerConfirmed === true, si no: HTTP 428
      bloquea si classifyProductConfidence(item).tier === "C"  (electro/tecnología)
      checkBudget(budgetId, total) — ya existe, ver abajo
      addToCart() × N → checkoutCart({payment: "yape"|"paypal"|...})
  → status: checkout_ready → confirmProcurementPayment()        [procurement-payment.ts]
      captura PayPal / confirma yape-plin → status: "ordered"
```

Todo el flujo es **humano-en-el-loop por diseño**: `buyerConfirmed` es un flag explícito
que el caller debe pasar, no algo que se infiere. No hay ningún punto de "el agente paga
solo" hoy.

## Lo que YA existe y es directamente reusable

1. **Límite de gasto por presupuesto** (`checkBudget(budgetId, total)` /
   `recordSpend(budgetId, items, total)`, en `lib/budget.ts`, usado en
   `prepareProcurementCheckout` línea 110-120). Si el gasto excede lo que queda del
   presupuesto, el resultado pasa a `pending_human` — **esto es conceptualmente lo mismo
   que "per-task spending limits" de x402**, solo que hoy el límite es un presupuesto
   humano configurado, no un tope on-chain.
2. **Clasificación de confianza por ítem** (`classifyProductConfidence` →
   `checkoutAllowed`, Tier A/B/C en `category-tier.ts`). Tier C (electro/tecnología)
   bloquea checkout siempre; Tier A ("canasta homogénea") es el único caso hoy
   considerado seguro para avanzar sin fricción extra. **Este es el criterio natural
   para acotar qué compras podrían calificar para un piloto autónomo**: solo Tier A,
   nunca C.
3. **Persistencia con estado explícito** (`procurement-store.ts`, D1 + memoria) — cada
   procurement tiene `status` (`pending_approval` / `checkout_ready` / `approved` /
   `ordered` / `rejected` / `pending_human`). Un path x402 necesitaría un estado nuevo
   (ej. `"auto_paid"`), no reinventar la máquina de estados.

## Dónde x402 podría encajar — como alternativa acotada, no reemplazo

Un piloto de bajo riesgo sería: para ítems **Tier A únicamente**, con
`spendCheck.allowed === true` Y el monto por debajo de un tope duro separado (ej.
$10-20), permitir que `prepareProcurementCheckout` se dispare sin
`options.buyerConfirmed`, **si y solo si** el caller es un agente con wallet x402
verificada y el pago se liquida vía x402 en vez de PayPal/yape. Todo lo demás (stock
check, resolución de producto, budget check) se queda exactamente igual — x402
reemplazaría únicamente el paso de `checkoutCart({payment: ...})` por un rail de pago
adicional, no el resto de la lógica de validación.

**Explícitamente NO se propone**: tocar `procurement-payment.ts` (captura PayPal real),
ni bajar el nivel de scrutinio de Tier B/C, ni saltar `checkBudget`.

## Preguntas abiertas (sin resolver, necesitan decisión humana)

1. **Red soportada**: `agentwallet-sdk` (Base) vs. OKX Agent Payments Protocol (X Layer,
   `eip155:196`, USDT0) — ¿cuál tiene mejor soporte real en LATAM/PE hoy? No investigado
   a fondo en esta pasada.
2. **Custodia de wallet**: ¿quién es dueño de la wallet que paga — CLI Market, el
   operador de compras, o el agente mismo? Implicancias legales/contables distintas.
3. **Tope de gasto duro**: ¿un monto fijo en USD, o basado en `budgetId` existente?
4. **Reversibilidad**: PayPal/MercadoPago tienen disputa/reembolso; ¿qué pasa si un pago
   x402 en un rail cripto sale mal? No hay equivalente hoy.
5. **Sandbox primero**: cualquier prueba real debería correr contra testnet (Base
   Sepolia, según la doc del skill) antes de considerar producción.

## Piloto de simulación — ejecutado (2026-07-12, solo lectura)

Se corrió la simulación recomendada arriba contra los datos reales de producción
(`procure-copilot-usage` D1, tabla `procurements`, vía `wrangler d1 execute --remote`,
consulta `SELECT` pura, cero escritura). Se reusó `classifyProductConfidence` /
`worstConfidenceTier` de `lib/category-tier.ts` tal cual, sin reimplementar la lógica.

**Resultado:**

| Métrica | Valor |
|---|---|
| Procurements totales en D1 | 92 |
| Tier A (sin electro/tecnología) | 91 (98.9%) |
| Tier A **y** bajo el tope propuesto de $20 | 63 (68.5%) |

**Lectura:** la canasta real de Procure Copilot es abrumadoramente FMCG (Tier A) — el
riesgo de "producto mal clasificado que no debería calificar para autónomo" es bajo en
la práctica, no solo en teoría. El techo de $20 es lo que más recorta el pool elegible
(91% → 68.5%), no la clasificación por tier. Si se buscara cubrir más volumen, subir el
tope a ~$56 (el monto más alto observado, canastas de 2-3 ítems) capturaría casi el 99%
de los procurements históricos — a costa de un tope de gasto más laxo por transacción
autónoma.

Esto no cambia la recomendación: sigue sin implementarse nada de pagos reales. Pero
ahora hay una cifra concreta para decidir si vale la pena, en vez de una suposición.

## Decisión (2026-07-12)

**Tope de gasto: $20 por transacción autónoma.** Cubre el 68.5% del volumen histórico
manteniendo el margen conservador — no se sube a ~$56 por ahora.

## Recomendación

No implementar todavía. Sigue pendiente resolver las preguntas abiertas de red
soportada y custodia de wallet antes de escribir código de pagos real; el tope de gasto
ya está decidido arriba.
