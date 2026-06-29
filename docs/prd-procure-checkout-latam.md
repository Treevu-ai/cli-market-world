---
title: PRD — Procure Checkout LATAM (Mercado Pago + onboarding)
tags:
  - product
  - prd
  - procure
  - billing
  - latam
status: Aprobado — Sprint 1 desbloqueado · decisiones cerradas 2026-06-29
author: Alex (PM) / Ricardo Cuba
updated: 2026-06-29
approved: 2026-06-29
version: 1.0
stakeholders: Eng Lead, Design, CS, GTM outbound horeca
repos: cli-market-world, cli-market-backend, cli-market-core, procure-copilot
---

# PRD: Procure Checkout LATAM — Mercado Pago, Yape/Plin y onboarding sin CLI

**Status**: Draft | **Last Updated**: 2026-06-25 | **Version**: 1.0

## 1. Problem Statement

Procure Copilot es el producto para operadores de compras en Perú y LATAM (restaurantes, hoteles, agro, construcción). Hoy la **suscripción mensual** solo acepta **PayPal USD**, mientras que Build Pro ya ofrece **Mercado Pago (soles, Yape, Plin, tarjeta)** con activación automática.

El ICP Procure no es developer: muchos buyers en Perú no tienen PayPal configurado, pero sí Yape/Plin. Además:

- La landing del Worker (`procure-copilot.../procure`) muestra CTAs **"Agendar"** (ventas asistida), no self-serve.
- El marketing promete Yape/MP en el flujo operativo, pero no en la **suscripción SaaS**.
- Post-pago exige `market register` → copiar `sk-` → pegar en dashboard — fricción inaceptable para gerente de compras.

**Costo de no resolverlo**: pérdida de conversión en el plan de entrada Compare ($29), dependencia de founder en cada cierre, y mensaje inconsistente entre Worker y cli-market.dev.

### Evidence

| Fuente | Señal |
|--------|-------|
| Journey audit (2026-06-25) | Procure subscribe = PayPal only; Build Pro = MP default en `America/Lima` |
| Worker live `/procure` | Botones "Agendar Starter/Pro/Builder" — sin checkout |
| `docs/pricing-strategy.md` | Anti-canibalización OK; gap es método de pago local en suscripción |
| `market_golive.py` | `TTC_MEDIAN_HOURS_TARGET = 24h`; `PRO_TO_ACTIVATED_TARGET = 50%` — Procure sin métrica propia |
| GTM outbound horeca | Piloto comercial abierto; self-serve bloqueado por PayPal |

---

## 2. Goals & Success Metrics

### North Star (initiative)

**Procure paid activation rate** = suscripciones Procure activadas ÷ clics "Suscribir" en `#pricing` Procure (rolling 30d).

| Goal | Metric | Baseline (est.) | Target | Window |
|------|--------|-----------------|--------|--------|
| Conversión checkout Procure | Click → subscription request creada | ~15% (PayPal only) | **≥35%** | 60 días post-launch |
| Activación auto (rails automáticos) | % activadas vía webhook (PayPal + MP) | ~70% PayPal | **≥85%** | 60 días |
| Time-to-activate (TTC) — MP/PayPal | Mediana horas: request → `tier: procure_*` | Sin baseline Procure | **≤2 h** mediana | 60 días |
| TTC — Yape/Plin manual (si habilitado) | Mediana horas | 24 h (Build Pro ref) | **≤8 h** | 60 días |
| Onboarding sin CLI | % nuevos Procure que llegan a dashboard con key válida sin `market` CLI | ~0% | **≥70%** | 90 días |
| Starter → Ops upgrade | % `procure_starter` que sube a `procure_pro` en 90d | TBD | **≥20%** | 90 días cohort |
| Worker CTA clarity | % sesiones `/procure` que llegan a checkout self-serve | ~0% | **≥25%** | 60 días |

### Métricas por rail de pago

| Rail | Métrica | Target 60d |
|------|---------|------------|
| PayPal USD | Request → activated (webhook) | ≥80% |
| Mercado Pago PEN | Request → activated (webhook) | ≥85% |
| Yape/Plin manual | Request → activated (ops) | ≥90% en ≤8h hábiles |
| Magic link onboarding | Email post-pago → dashboard con sesión | ≥70% en 24h |

### Guardrails (no regresión)

| Métrica | Umbral |
|---------|--------|
| Error rate checkout Procure | <2% 5xx en `/billing/procure-*` |
| Webhook duplicate activations | 0 |
| Canibalización Build Pro | <5% nuevos `pro` sin `procurementId` en 90d que deberían ser Procure |
| Chargebacks / disputas MP | <1% volumen |

---

## 3. Non-Goals

- **Stripe** — no opera en Perú; fuera de scope.
- **Facturación electrónica SUNAT automática** — iniciativa separada (legal/finance).
- **Mercado Pago suscripciones recurrentes nativas (preapproval)** — Fase 2; Fase 1 replica patrón Build Pro (preference + renovación manual/email).
- **Cambiar precios** ($29/$79/$149) — solo rails y UX.
- **Intelligence ($300–500)** — sigue contacto / ventas.
- **Rediseño completo del Worker** — solo paridad de CTA y deep links en Fase 1.

---

## 4. User Personas & Stories

**Primary**: **María** — gerente de compras, restaurante 3 locales, Lima. Usa Yape diario. No tiene CLI ni PayPal business.

**Secondary**: **Carlos** — CFO operativo, constructora mediana. Quiere factura y transferencia; acepta MP con tarjeta corporativa.

### Story 1 — Suscribir Compare con Yape (Perú)

**As a** gerente de compras, **I want** pagar Procure Compare con Yape/soles **so that** puedo empezar sin PayPal ni terminal.

**Acceptance criteria**:

- [ ] Given audiencia `es-PE` o tz `America/Lima`, when abro modal Procure, then **Soles (Mercado Pago)** es método recomendado.
- [ ] Given elijo Compare $29 y MP, when completo email y legal, then recibo `checkout_url` MP en PEN con ref `PCS-xxxxxxxx`.
- [ ] Given pago aprobado en MP, when webhook llega, then `tier: procure_starter` en ≤5 min (p95).
- [ ] Given activación OK, when abro link del email, then llego al dashboard Procure **sin pegar API key manualmente** (magic link).

### Story 2 — Suscribir Ops desde Worker

**As a** usuario que llega por LinkedIn al Worker, **I want** un CTA claro de compra **so that** no tenga que agendar demo para pagar $79.

**Acceptance criteria**:

- [ ] Given estoy en `/procure` plan Pro, when clic "Suscribir" (nuevo CTA), then redirect a `cli-market.dev/?audience=procure&plan=pro#pricing` con modal abierto.
- [ ] Given redirect, when completo checkout, then return URL incluye `audience=procure` y banner post-pago con pasos Procure.

### Story 3 — PayPal internacional (sin regresión)

**As a** hotel con cuenta PayPal USD, **I want** seguir pagando en dólares **so that** mi contabilidad no cambie.

**Acceptance criteria**:

- [ ] PayPal path actual intacto para los 3 planes Procure.
- [ ] Webhook `BILLING.SUBSCRIPTION.ACTIVATED` sigue mapeando `procure_*` tiers.

### Story 4 — Ops activa manual Yape (fallback)

**As a** usuario sin tarjeta en MP, **I want** transferir con ref `PCP-xxx` **so that** puedo pagar como en Build Pro manual.

**Acceptance criteria**:

- [ ] Given `WALLET_MANUAL_FALLBACK=true`, when elijo Yape/Plin manual en modal Procure, then veo número, monto PEN exacto y ref.
- [ ] Given ops confirma pago, when `activate-procure` (Slack/ops), then tier correcto según plan.

---

## 5. Solution Overview

### Fase 1 (MVP — 2–3 sprints eng.)

1. **Extender `POST /billing/procure-subscribe`** con `payment_method`: `paypal` | `mercadopago` | `yape` | `plin` (mismo contrato que `/billing/pro-checkout`).
2. **Nuevo handler MP** `_start_procure_mercadopago_checkout` — preference PEN, refs `PCS`/`PCP`/`PCB`, webhook activa `procure_starter`/`procure_pro`/`procure_builder`.
3. **Landing modal Procure** — selector de pago (espejo Build Pro); copy "PayPal only" eliminado.
4. **Worker CTAs** — "Suscribir" deep link a cli-market.dev; mantener "Agendar" como secundario para enterprise/piloto.
5. **Post-pago magic link** — email con URL firmada al dashboard Procure + API key provisionada server-side.

### Fase 2 (recurrencia + finanzas)

- MP Preapproval / débito automático mensual O job de renovación con email + preference.
- Recordatorio D-3 / D-0 / grace period 7 días antes de downgrade.
- Comprobante / factura SUNAT (integración contable).

### Key design decisions

| Decisión | Elegimos | Trade-off |
|----------|----------|-----------|
| MP Fase 1 = Preference (one-shot) | Igual que Build Pro hoy | Renovación manual hasta Fase 2; documentar en ToS |
| Endpoint único `procure-subscribe` | Menos superficie que nuevo `/procure-checkout` | Handler más grande; tests exhaustivos |
| Onboarding magic link en Fase 1 | Reduce churn post-pago | Requiere JWT/signing + Worker callback |
| Worker no hostea checkout | Billing centralizado Railway | Un salto de dominio (aceptable) |

---

## 6. Technical Considerations

Ver plan detallado: [`docs/plan-procure-mercadopago-subscribe.md`](./plan-procure-mercadopago-subscribe.md).

**Dependencies**:

| Sistema | Necesidad | Owner | Riesgo |
|---------|-----------|-------|--------|
| `market_connectors.mercadopago_payments` | `create_preference` | core | Bajo |
| Railway webhooks MP | Extender parser refs PCS/PCP/PCB | world/backend | Medio |
| Procure Worker | Recibir magic link / auto-bind key | procure-copilot | Medio |
| PayPal plans | Sin cambio Fase 1 | ops | Bajo |
| FX PEN | `PRO_PEN_PER_USD` o `PROCURE_PEN_PER_USD` | ops | Bajo |

**Known risks**:

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| MP one-shot ≠ suscripción recurrente | Alta | Medio | Email renovación mes 2; Fase 2 preapproval |
| Usuario paga plan equivocado (monto PEN) | Media | Alto | Título preference con plan slug; monto por tier |
| Webhook MP activa tier incorrecto | Baja | Alto | Tests + idempotency + prefix regex |
| Magic link abuse | Baja | Alto | TTL 15 min, single-use, HMAC |

**Open questions** (resolver antes de dev):

- [x] ¿Mismo tipo de cambio `PRO_PEN_PER_USD` para Procure o tabla por tier? → **`PRO_PEN_PER_USD` compartido** (2026-06-29)
- [x] ¿Yape manual en Procure desde día 1 o solo MP hosted? → **Solo MP hosted Fase 1** (2026-06-29)
- [x] ¿Grace period si no renueva mes 2? → **7 días** con emails D-3/D-0/D+3/D+7 (2026-06-29)

---

## 7. Launch Plan

| Phase | Audience | Success gate |
|-------|----------|--------------|
| Internal alpha | Team + 2 design partners horeca | MP sandbox PCS/PCP activan tier; magic link OK |
| Closed beta | 10 clientes Perú (lista outbound) | TTC mediana MP <4h; 0 activaciones duplicadas |
| GA 20% | Tráfico `#pricing` Procure | Conversión click→request +10pp vs control PayPal-only |
| GA 100% | Todos | Métricas tabla §2 en verde o plan de rollback |

**Rollback criteria**: error rate >5% en `procure-subscribe` o activaciones incorrectas >2 en 24h → flag `PROCURE_MP_CHECKOUT=0`.

---

## 8. Appendix

- Journey audit: conversación producto 2026-06-25
- Código: `routers/billing/routes.py`, `procure_billing.py`, `landing/components/BillingCheckoutModal.tsx`
- Ops: `ops/CLIENT_PAYMENT_JOURNEY.md`, `ops/BILLING_MANUAL.md`, `ops/payments_e2e.py`
- Pricing: `docs/pricing-strategy.md`
- Implementación: `docs/plan-procure-mercadopago-subscribe.md`

---

## Aprobación v1.0 — 2026-06-29

**Aprobado para Sprint 1:**
- Mercado Pago Fase 1 (Preference one-shot) en suscripción Procure
- Paridad CTA Worker: reemplazar "Agendar" por self-serve + deep link a checkout
- Magic link onboarding post-pago (JWT + Worker callback)
- Yape/Plin como método de pago en plan Compare ($29)

**Decisiones cerradas 2026-06-29:**

| # | Decisión | Elegida | Detalle |
|---|----------|---------|---------|
| 1 | FX PEN | **A — Mismo `PRO_PEN_PER_USD`** | Un solo env var compartido con Build Pro |
| 2 | Yape/Plin manual | **A — Solo MP hosted día 1** | Manual diferido a Fase 2 si hay demanda |
| 3 | Grace period | **A — 7 días** | Emails D-3, D-0, D+3, D+7 → downgrade |
| 4 | Return URL post-pago | **B — Landing bienvenida** | `procurecopilot.com/welcome?plan=X` (dominio propio, no Worker) |
| 5 | CTA Worker/landing | **B — Dos botones** | "Suscribir ahora" (primario) + "Agendar demo" (secundario) en todos los planes |

**Nota dominio:** ya no se usa `procure-copilot.workers.dev` — dominio propio es `procurecopilot.com`.

**Bloqueantes resueltos — sprint puede arrancar.**

**Fase 2 post-Sprint 1:**
- MP preapproval (suscripción recurrente nativa)
- Renovación automática + emails D-3/D-0/grace
- Yape/Plin manual si hay demanda post-Fase 1
