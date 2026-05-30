# E2E client journey — CLI Market Pro

Checklist para el **primer cliente** de punta a punta, sin fricción.

## Journey del cliente

```mermaid
flowchart LR
  A[cli-market.dev] --> B[Email + ref PRO-xxx]
  B --> C[PayPal Hosted Button]
  C --> D[hello@cli-market.dev reply]
  D --> E[ops activate_pro]
  E --> F[market whoami = pro]
  F --> G[market checkout]
```

### 1. Descubrimiento
- Landing: [cli-market.dev/#pricing](https://cli-market.dev/#pricing)
- O contacto: [cli-market.dev/#contact](https://cli-market.dev/#contact)
- O CLI: `pip install cli-market && market hello`

### 2. Cuenta free (recomendado antes de pagar)
```bash
pip install cli-market
export MARKET_API_URL=https://cli-market-production.up.railway.app
market login          # elige username — úsalo al activar Pro
market search "leche" --country PE
market whoami         # tier: free
```

### 3. Solicitar Pro
**Web:** email (+ usuario CLI opcional) → ref `PRO-XXXXXXXX` + botón PayPal  
**CLI:**
```bash
market upgrade --email tu@email.com
```

### 4. Pagar
- Botón PayPal embebido (Hosted Button `B6YVFTG4MA73J`)
- O link: `https://www.paypal.com/ncp/payment/B6YVFTG4MA73J`
- Incluir ref `PRO-xxx` en nota PayPal si es posible

### 5. Confirmación (ops — tú)
1. Email de notify en `hello@cli-market.dev` con ref + email + use case
2. Verificar pago en PayPal dashboard
3. **SLA:** activar Pro en ≤24 h hábiles (`docs/ops/phase0-mitigation.md`)
4. Activar:
```bash
python3 ops/activate_pro.py USERNAME --request-id PRO-XXXXXXXX
# o
python3 ops/activate_pro.py USERNAME --email cliente@example.com
```

### 6. Cliente verifica
```bash
market whoami              # tier: pro
market checkout --payment yape   # ya no 403
```

---

## Pre-flight (antes del primer cliente)

### Railway (API)
- [ ] `SMTP_*` configurado — ver `.env.example`
- [ ] `PRO_PAYMENT_URL=https://www.paypal.com/ncp/payment/B6YVFTG4MA73J`
- [ ] `BILLING_FROM_EMAIL=hello@cli-market.dev`
- [ ] Test: `curl -X POST .../billing/request-pro -d '{"email":"test@you.com"}'`

### Cloudflare Pages (landing)
- [ ] `NEXT_PUBLIC_API_URL` apunta a Railway
- [ ] PayPal client-id + hosted button id (ver `landing/.env.example`)
- [ ] Deploy landing tras cambios

### Smoke test (5 min)
```bash
# API
curl -s https://cli-market-production.up.railway.app/ | jq .status

# Pro request (mock email si SMTP off — debe devolver payment_link)
curl -s -X POST https://cli-market-production.up.railway.app/billing/request-pro \
  -H "Content-Type: application/json" \
  -d '{"email":"smoke@test.com","lang":"es"}' | jq .

# CLI
market login && market whoami
```

---

## Troubleshooting

| Síntoma | Causa | Fix |
|---------|-------|-----|
| "Revisa email" pero no llega | SMTP no configurado | Railway env SMTP_* o muestra link en UI (ya implementado) |
| Pro no activa tras pago | Username incorrecto | Cliente debe `market login` y responder con ese username + ref |
| `checkout` 403 | Sigue en free | `ops/activate_pro.py` con username correcto |
| Rate limit 429 en pricing | Muchos requests mismo día | Rare; reenviar con `resend: true` desde CLI |

---

Ver también: [BILLING_MANUAL.md](./BILLING_MANUAL.md)
