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
PROCURE_MP_CHECKOUT=0          # 1 = habilita MP/Yape/Plin en procure-subscribe (dark launch default off)
PROCURE_PEN_PER_USD=3.75       # opcional; fallback PRO_PEN_PER_USD
PROCURE_MP_SUCCESS_URL=https://cli-market.dev/?mp=success&audience=procure&ref={ref}#procure

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

## Email en checkout (quién lo genera)

`POST /billing/pro-checkout` **no inventa** el email del cliente: guarda `body.email` tal como lo envía el modal, curl o script (normalizado a minúsculas). El backend solo lo usa para la solicitud `PRO-` y, tras activación, para el correo de bienvenida Pro (contraseña CLI — **no** la `sk-`).

### Plus-addressing en `@cli-market.dev`

Google Workspace entrega todo `*@cli-market.dev` al buzón principal (`hello@cli-market.dev`). Los prefijos ayudan a filtrar en Gmail y a distinguir origen del pago en ops.

| Prefijo | Quién lo genera | Uso |
|---------|-----------------|-----|
| `e2e+{método}+{run_id}@…` | `ops/payments_e2e.py` | E2E automatizado (PayPal, MP, Yape, Plin, Procure) |
| `pam+{método}+{{run_id}}@…` | `ops/pam_matrix.yaml` | Matriz PAM / regresión manual |
| `pago-real+{método}+{id}@…` | **Manual** (modal, curl, script local) | Pago real en prod con etiqueta legible; `{id}` suele ser 8 hex del run o del usuario |

Ejemplos reales:

```
e2e+mp+a1b2c3d4@cli-market.dev      # E2E Mercado Pago
pam+mp+{{run_id}}@cli-market.dev    # PAM (plantilla)
pago-real+mp+8a3ea8af@cli-market.dev # Pago real MP — ref PRO-D2CF329D
```

`pago-real+…` **no está hardcodeado** en el repo: es convención ops para pagos reales que quieres rastrear sin mezclarlos con `e2e+` o `pam+`. El segmento `{método}` es informativo (`mp`, `pp`, `yape`, `plin`); la activación depende del webhook o de ops, no del local-part del email.

### Copia ops del correo de activación

No hay BCC al cliente. Tras enviar el email al cliente con éxito, el backend manda un borrador separado `[Pro activado — borrador]` a `BILLING_NOTIFY_EMAIL` (`hello@cli-market.dev`). Si SMTP falla al cliente, **no** se envía el borrador ops.

Tokens en logs Railway / webhook `actions`:

- `activation_email:…` — enviado al cliente
- `activation_email_skipped:…` — omitido (SMTP deshabilitado o duplicado reciente)
- `activation_draft_notify:…` — borrador ops enviado
- `activation_email_failed` — fallo SMTP

Rails con logging unificado: PayPal Pro webhook, Mercado Pago, Yape/Plin manual, admin resend, **`ops/activate_pro.py`** (vía `_activate_pro_from_request` / `_append_pro_activation_email_actions`).

## Reenviar correo de activación Pro

Solo para solicitudes **ya activadas** (`tier=pro`) con ref `PRO-`. Genera **nueva contraseña CLI** y reenvía el mismo template de bienvenida.

```bash
# CLI (requiere MARKET_API_TOKEN)
python3 ops/resend_pro_activation_email.py PRO-D2CF329D
python3 ops/resend_pro_activation_email.py PRO-D2CF329D --email otro@ejemplo.com

# API directa
curl -X POST https://cli-market-production.up.railway.app/admin/resend-pro-activation-email \
  -H "Authorization: Bearer $MARKET_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"request_id":"PRO-D2CF329D"}'
```

GitHub Actions: workflow `ops-resend-pro-email.yml` (disparador en `ops/triggers/resend-pro-email.trigger`).

## Endpoints

| Endpoint | Uso |
|----------|-----|
| `POST /billing/pro-checkout` | Landing modal — PayPal, MP, Yape, Plin |
| `POST /billing/paypal` | CLI autenticado — PayPal REST |
| `POST /billing/procure-subscribe` | Tab Procure — PayPal REST; MP/Yape/Plin si `PROCURE_MP_CHECKOUT=1` |
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