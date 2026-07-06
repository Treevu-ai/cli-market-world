# Sprint N-1 — Split `routers/payments.py`

**Status:** Ready to start · **Owner:** eng + PM  
**Repo:** `cli-market-world` → mirror `cli-market-backend`  
**Sprint goal:** Partir el monolito de pagos sin cambiar contratos HTTP ni romper revenue paths.

---

## 1. Problem

`routers/payments.py` tiene **~2,350 LOC** y mezcla tres dominios:

| Dominio | Rutas | Riesgo si se toca a ciegas |
|---------|-------|----------------------------|
| **Cart checkout** | `/checkout/*` (yape, paypal, MP, wise, validate, rates) | Órdenes + idempotency |
| **Webhooks** | `/checkout/*-webhook`, `_handle_paypal_event` | Doble activación / revenue |
| **Pro billing** | `/billing/*`, activación Pro/Starter/Procure/Build | Funnel + email + Slack |

**Importadores internos** (no pueden romperse):

- `market_server.py` → `payments_router`
- `routers/admin.py`, `routers/slack_ops.py` → `_activate_pro_from_request`, `resend_pro_activation_email`
- `routers/retailers.py` → `process_pro_subscription_request`
- `ops/activate_pro.py` → helpers de activación/email

Ya existe `routers/billing/pro_helpers.py` — el patrón de extracción está probado.

---

## 2. Success metrics

| Métrica | Target |
|---------|--------|
| `payments.py` LOC | **< 80** (facade + re-exports) |
| OpenAPI `/checkout/*` + `/billing/*` | **0 diff** vs pre-split (`contract_parity.py`) |
| `pytest tests/test_checkout_payments.py` | **100% green** |
| `pytest tests/test_pro_payment_guard.py tests/test_billing_slack.py` | green |
| Backend mirror | Auto-PR o parity manual post-merge world |

---

## 3. Non-goals (este sprint)

- Stripe `/billing/checkout` (sigue disabled)
- Checkout autónomo Fase 8
- Cambios de pricing o nuevos gateways
- Refactor de `market_connectors/*`

---

## 4. Target architecture

```
routers/
  payments.py              # FACADE: include_router + re-exports públicos
  billing/
    __init__.py
    pro_helpers.py         # (ya existe)
    activation.py          # NEW: _activate_pro_from_request, process_*_subscription_request
    notifications.py       # NEW: Slack, email activation, resend
    routes.py              # NEW: POST /billing/*
  checkout/
    __init__.py
    routes.py              # NEW: POST/GET /checkout/* (except webhooks)
    webhooks.py            # NEW: paypal-webhook, mercadopago-webhook, generic webhook
    paypal_handler.py      # NEW: _handle_paypal_event, _parse_*_ref (testable unit)
```

**Regla de oro:** `market_server.py` sigue con una sola línea:

```python
from routers.payments import router as payments_router
```

Los importadores legacy (`from routers.payments import _activate_pro_from_request`) se mantienen vía **re-exports** en `payments.py` hasta un cleanup opcional en N-3.

---

## 5. Phased delivery (3 PRs)

### PR-N1a — Helpers only (bajo riesgo)

**Scope:** Mover funciones sin `@router` a `billing/activation.py` y `billing/notifications.py`.  
**Sin mover rutas.** `payments.py` importa y re-exporta.

| Check |
|-------|
| `test_checkout_payments.py` |
| `test_pro_payment_guard.py` |
| `ruff check` |

**ETA técnico:** ~1 PR reviewable.

---

### PR-N1b — Checkout + webhooks

**Scope:**

- `checkout/routes.py` — yape, lemon, paypal, wise, mercadopago, validate, rates, status endpoints
- `checkout/webhooks.py` — webhooks + `paypal_handler.py`
- `payments.py` hace `include_router` de ambos

| Check |
|-------|
| Idempotency y webhook dedup (`test_checkout_payments.py`) |
| `contract_parity` checkout paths |

---

### PR-N1c — Billing routes + facade final

**Scope:**

- `billing/routes.py` — todos los `/billing/*`
- `payments.py` queda facade (< 80 LOC)
- Bump `ops/backend-payments-mirror.trigger` (nuevo) o sync manual backend

| Check |
|-------|
| Full test suite payments/billing |
| `python ops/contract_parity.py` |
| Smoke manual: `POST /billing/pro-checkout` (mock/skip live) |

---

## 6. Test gates (CI — no negociar)

```bash
pytest tests/test_checkout_payments.py tests/test_pro_payment_guard.py \
  tests/test_billing_slack.py tests/test_contract_parity.py -q
python ops/contract_parity.py   # si GH_PAT lee backend
ruff check --config ruff.toml . # backend; world usa pyproject.toml
```

Añadir en N-1b si falta cobertura:

- `tests/test_payments_webhooks.py` — mock `_handle_paypal_event` (duplicate event ignored)
- Smoke `GET /mercadopago-status` + `GET /paypal-status` (200, no live call)

---

## 7. Backend mirror

Orden release: **world → backend** (igual que Observatory T-178).

1. Merge PRs N-1a→c en `cli-market-world`
2. Copiar árbol `routers/payments.py`, `routers/billing/`, `routers/checkout/` al backend
3. Verificar `contract_parity` checkout + billing paths
4. Fly.io deploy backend

Si `GH_PAT_BACKEND_WRITE` tiene Workflows scope: workflow futuro `sync-backend-payments-mirror.yml` (opcional — no bloquea N-1).

---

## 8. Rollback

Cada PR es revertible de forma independiente. Si webhook regression en prod:

1. Revert PR-N1b en world + backend
2. Confirmar `webhook_events_processed` dedup sigue activo
3. Post-mortem antes de re-intentar split webhooks

---

## 9. Sprint checklist (founder / eng)

| # | Acción | Owner |
|---|--------|-------|
| 1 | Abrir PR-N1a (helpers) | eng |
| 2 | No mezclar posts GTM de Procure con cambios de pagos | GTM |
| 3 | Tras N-1c: re-run backend CI + contract parity | eng |
| 4 | Actualizar `TECH-DEBT-BACKLOG.md` — N-1 → ✅ | PM |

---

## 10. RICE (por qué N-1 primero)

| Factor | Nota |
|--------|------|
| **Reach** | Todo revenue Pro + cart checkout pasa por este archivo |
| **Impact** | Alto — reduce riesgo de regresión en cada cambio de billing |
| **Confidence** | Media-alta — tests P0 checkout existen; patrón `billing/pro_helpers` probado |
| **Effort** | L (3 PRs, ~2,350 LOC) |

**Recomendación PM:** Empezar **PR-N1a hoy**. No abrir N-2 (GTM chain) en paralelo en el mismo dev — payments es revenue-critical.
