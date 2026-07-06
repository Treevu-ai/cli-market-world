# PayPal Sandbox — CLI Market (REST, sin Braintree)

Cuenta PayPal **no vinculada a Braintree** → usa solo [PayPal Developer REST](https://developer.paypal.com/dashboard/).

## 1. Credenciales sandbox

1. Entra a [developer.paypal.com/dashboard](https://developer.paypal.com/dashboard/)
2. **Apps & Credentials** → pestaña **Sandbox**
3. **Create App** (o usa una existente) → copia **Client ID** y **Secret**

Cuentas de prueba (comprador/vendedor):
[Dashboard → Testing Tools → Sandbox Accounts](https://developer.paypal.com/dashboard/accounts)

## 2. Variables en Fly.io (sandbox)

En el servicio API de Fly.io, añade:

```bash
PAYPAL_CLIENT_ID=<sandbox client id>
PAYPAL_CLIENT_SECRET=<sandbox secret>
PAYPAL_SANDBOX=true
# Tras los pasos 3 y 4:
PAYPAL_PLAN_ID=P-...
PAYPAL_WEBHOOK_ID=WH-...
```

Redeploy después de guardar.

## 3. Crear plan Pro ($79/mo) — script

Desde tu máquina (con credenciales sandbox en env):

```bash
cd /home/acuba/Proyectos/nuevo
export PAYPAL_CLIENT_ID=...
export PAYPAL_CLIENT_SECRET=...
export PAYPAL_SANDBOX=true

python3 ops/paypal_sandbox_setup.py check
python3 ops/paypal_sandbox_setup.py create-plan
```

Copia el `plan_id` impreso → `PAYPAL_PLAN_ID` en Fly.io.

Alternativa manual: [Subscriptions → Plans](https://developer.paypal.com/dashboard/) en el dashboard (si tu cuenta lo muestra).

## 4. Registrar webhook

PayPal debe poder hacer POST a tu API **pública HTTPS**.

URL de producción (sandbox apunta al mismo host con credenciales sandbox):

```
https://cli-market-api.fly.dev/checkout/paypal-webhook
```

```bash
python3 ops/paypal_sandbox_setup.py register-webhook \
  https://cli-market-api.fly.dev/checkout/paypal-webhook
```

Copia el `webhook_id` → `PAYPAL_WEBHOOK_ID` en Fly.io.

Eventos que registramos automáticamente:

- `BILLING.SUBSCRIPTION.ACTIVATED` / `CANCELLED` / `EXPIRED` / `SUSPENDED`
- `CHECKOUT.ORDER.APPROVED` / `COMPLETED`
- `PAYMENT.CAPTURE.COMPLETED`

Ver webhooks existentes:

```bash
python3 ops/paypal_sandbox_setup.py list-webhooks
```

## 5. Probar flujo completo

### A) Diagnóstico

```bash
curl https://cli-market-api.fly.dev/paypal-status
```

Esperado (sandbox):

```json
{
  "configured": true,
  "sandbox": true,
  "webhook_configured": true,
  "plan_id_configured": true
}
```

### B) Upgrade Pro (CLI)

```bash
export MARKET_API_URL=https://cli-market-api.fly.dev
market login
market upgrade
```

Abre la `approve_url` → inicia sesión con **cuenta sandbox Personal (buyer)** → aprueba suscripción.

### C) Verificar tier Pro

```bash
curl -H "Authorization: Bearer <tu-token>" \
  https://cli-market-api.fly.dev/auth/subscription
```

Debería mostrar `"tier": "pro"` tras el webhook (puede tardar unos segundos).

### D) Script rápido (solo URL de pago)

```bash
python3 ops/paypal_sandbox_setup.py test-upgrade admin
```

### E) Checkout carrito (requiere tier Pro)

```bash
market search "leche" --country PE
market add 1 --store wong
market checkout --payment paypal
```

Aprueba en PayPal sandbox → webhook marca orden `paid`:

```bash
market orders
```

## 6. Sandbox buyer login

En la pantalla de PayPal usa una cuenta **Personal** del sandbox (no Business).

Credenciales en [Sandbox Accounts](https://developer.paypal.com/dashboard/accounts) → ver email/password de la cuenta **Personal**.

## 7. Troubleshooting

| Síntoma | Causa probable | Fix |
|---------|----------------|-----|
| `PayPal no configurado` | Env vars faltan en Fly.io | Añadir CLIENT_ID/SECRET, redeploy |
| `approve_url` OK pero tier sigue `free` | Webhook no llega o ID incorrecto | Verificar `PAYPAL_WEBHOOK_ID`, logs Fly.io en `/checkout/paypal-webhook` |
| Webhook 401 | Firma inválida o sin configurar | `PAYPAL_WEBHOOK_ID` de la misma app; en prod nunca acepta webhooks sin firma |
| Webhook 503 | Live sin `PAYPAL_WEBHOOK_ID` | Registrar webhook y fijar env var antes de `PAYPAL_SANDBOX=false` |
| Sandbox local 401 | Tests sin webhook ID | Solo dev: `PAYPAL_ALLOW_UNVERIFIED_WEBHOOKS=1` (nunca en Fly.io prod) |
| Plan duplicados | Sin `PAYPAL_PLAN_ID` | Ejecutar `create-plan` una vez y fijar env var |
| Checkout 403 | Usuario free | Completar upgrade Pro primero |

## 8. Pasar a Live (después de sandbox OK)

1. App **Live** en developer.paypal.com → nuevas credenciales
2. Nuevo webhook + plan en Live
3. Fly.io:

```bash
PAYPAL_SANDBOX=false
PAYPAL_CLIENT_ID=<live>
PAYPAL_CLIENT_SECRET=<live>
PAYPAL_PLAN_ID=<live plan>
PAYPAL_WEBHOOK_ID=<live webhook>
CHECKOUT_WEBHOOK_SECRET=<random secret for POST /checkout/webhook>
```

4. Probar con monto real pequeño antes de anunciar Alpha.
