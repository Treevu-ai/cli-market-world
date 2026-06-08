# Billing manual — CLI Market Pro

Flujo principal: **PayPal REST** + modal en landing (`/billing/pro-checkout`). Activación automática vía webhook.

Fallback manual (hosted button, Yape/Plin): activación ops ≤24 h.

## Flujo web (recomendado)

1. Usuario abre [cli-market.dev/#pricing](https://cli-market.dev/#pricing) → **Configurar Pro**
2. Modal paso 1: método + legal · paso 2: email + username CLI
3. API: `POST /billing/pro-checkout` → `approve_url` PayPal o QR Yape/Plin
4. PayPal confirmado → webhook activa tier `pro` en segundos
5. Usuario: `market whoami` → `market checkout`

## Flujo CLI (con sesión)

```bash
market login
market upgrade    # POST /billing/paypal — PayPal REST, mismo webhook
```

## Flujo manual (fallback)

1. PayPal REST no disponible → `process_pro_subscription_request` + `PRO_PAYMENT_URL`
2. O Yape/Plin → QR + ref `PRO-xxx` → ops activa manualmente
3. `python3 ops/activate_pro.py USERNAME --request-id PRO-XXXXXXXX`

## Variables Railway

```bash
# PayPal REST (primario)
PAYPAL_CLIENT_ID=...
PAYPAL_CLIENT_SECRET=...
PAYPAL_PLAN_ID_PRO=...
PAYPAL_SANDBOX=false   # Live en producción

# Return URLs post-PayPal (opcional)
PRO_SUBSCRIBE_RETURN_URL=https://cli-market.dev/?sub=success#pricing
PRO_SUBSCRIBE_CANCEL_URL=https://cli-market.dev/?sub=cancelled#pricing
PROCURE_SUBSCRIBE_RETURN_URL=https://cli-market.dev/?sub=success&audience=procure#procure

# Fallback hosted button
PRO_PAYMENT_URL=https://www.paypal.com/ncp/payment/PLB-K47XCNUKG24P
PRO_PRICE_USD=39

# Yape/Plin — transferencia manual en app (no QR web)
YAPE_PLIN_NUMBER=9XXXXXXXX
PRO_PEN_PER_USD=3.7

# Email saliente
BILLING_FROM_EMAIL=hello@cli-market.dev
BILLING_NOTIFY_EMAIL=hello@cli-market.dev
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=hello@cli-market.dev
SMTP_PASSWORD=app-password-here
SMTP_USE_TLS=true
```

Sin SMTP: el endpoint devuelve `approve_url` en JSON/modal pero no envía email.

## Endpoints

| Endpoint | Uso |
|----------|-----|
| `POST /billing/pro-checkout` | Landing modal — PayPal, MP, Yape, Plin |
| `POST /billing/paypal` | CLI autenticado — PayPal REST |
| `POST /billing/procure-subscribe` | Tab Procure — PayPal REST |
| `POST /billing/request-pro` | Legacy email + hosted button |

## Probar

```bash
curl -X POST https://cli-market-production.up.railway.app/billing/pro-checkout \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","lang":"es","payment_method":"paypal","username":"miuser"}'
```

Reenviar si duplicado:
```bash
curl -X POST .../billing/pro-checkout \
  -d '{"email":"test@example.com","payment_method":"paypal","resend":true}'
```

## PayPal Hosted Button — «Agotado» en landing

Si el widget embebido muestra **Sold out / Agotado**:

1. PayPal Business → **Payment links & buttons** → link `PLB-K47XCNUKG24P`
2. Verificar inventario ilimitado en el plan
3. El modal usa REST primero; hosted button solo en `<details>` de respaldo

## Activar Pro tras pago manual

**SLA:** ≤24 h hábiles para Yape/Plin y fallback hosted (`docs/ops/phase0-mitigation.md`).

Atajo (recomendado tras confirmar Yape/Plin):

```bash
python3 ops/slack_cli.py activate-pro PRO-XXXXXXXX
# → activa tier · email al cliente · borrador de respuesta en hello@cli-market.dev · #cli-market-pro
```

Equivalente directo:

```bash
python3 ops/activate_pro.py USERNAME --request-id PRO-XXXXXXXX
python3 ops/activate_pro.py USERNAME --request-id PRO-XXXXXXXX --display-name "Nombre Cliente"
python3 ops/activate_pro.py --email cliente@example.com
python3 ops/slack_cli.py activate-pro --email cliente@example.com --bitacora
```

Journey completo: `ops/E2E_CLIENT_JOURNEY.md` · Sandbox: `ops/PAYPAL_SANDBOX.md`