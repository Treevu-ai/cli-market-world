# Billing manual — Pro via email (default)

Sin integración PayPal directa. Flujo:

1. Usuario solicita Pro (`market upgrade --email`, landing pricing, o `/v1/contact` plan=pro)
2. API guarda `subscription_requests` y envía email desde **hello@cli-market.dev**
3. Usuario paga link configurado (`PRO_PAYMENT_URL`)
4. Usuario responde al email con su username CLI
5. Tú activas Pro manualmente

## Variables Railway

```bash
# Link de pago — PayPal Hosted Button (recomendado)
PRO_PAYMENT_URL=https://www.paypal.com/ncp/payment/B6YVFTG4MA73J
PRO_PRICE_LABEL=$49/month

# Email saliente
BILLING_FROM_EMAIL=hello@cli-market.dev
BILLING_NOTIFY_EMAIL=hello@cli-market.dev

# SMTP (ej. Google Workspace, Zoho, SendGrid SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=hello@cli-market.dev
SMTP_PASSWORD=app-password-here
SMTP_USE_TLS=true
```

Sin SMTP: el endpoint devuelve el `payment_link` en JSON/CLI pero no envía email.

## PayPal Hosted Button — «Agotado» en landing

Si el widget embebido muestra **Sold out / Agotado**:

1. PayPal Business → **Payment links & buttons** → botón `B6YVFTG4MA73J`
2. Verificar que el producto/plan Pro tenga **inventario ilimitado** o stock > 0
3. Mientras tanto, el CTA principal en landing es el link directo `PRO_PAYMENT_URL` (botón verde post-solicitud)

## Probar

```bash
curl -X POST https://cli-market-production.up.railway.app/billing/request-pro \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","lang":"es"}'
```

CLI:

```bash
market login
market upgrade --email tu@email.com
```

## Activar Pro tras pago confirmado

```bash
cd /home/acuba/Proyectos/nuevo
python3 ops/activate_pro.py admin
```

O en Python:

```python
from market_core import ensure_db_initialized, db_set_subscription
ensure_db_initialized()
db_set_subscription("admin", "pro")
```

## PayPal REST (opcional, más adelante)

Endpoints `/billing/paypal` y webhooks siguen en el código por si vuelves a automatizar.
Ver `ops/PAYPAL_SANDBOX.md`.
