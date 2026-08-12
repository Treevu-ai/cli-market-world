# n8n Workflows — CLI Market Sales Pipeline

Workflows de n8n para orquestar el pipeline de ventas CLI Market + HubSpot + Slack.

## Arquitectura

```
Landing (Cloudflare) → HubSpot Form → n8n → Slack
CLI Market Billing → n8n → HubSpot Deal Update → Slack
Cron Daily → n8n → CLI Market API + HubSpot → Slack #command-control
```

## Workflows

### 1. Lead to Slack Sync (`01-lead-to-slack-sync.json`)

**Trigger:** Webhook POST `/lead-sync`

**Payload:**
```json
{
  "email": "cliente@example.com",
  "product_line": "Procure Pro",
  "tier_intent": "Pro $79",
  "lead_source": "Landing"
}
```

**Flow:**
1. Recibe webhook del form de landing
2. Crea Deal en HubSpot (Stage: New Lead)
3. Formatea mensaje Slack con emojis por product line
4. Publica en `#outbound`
5. Responde con deal_id

**Slack Output:**
```
🚀 New Lead: Procure Pro
Email: cliente@example.com
Tier Intent: Pro $79
Product Line: Procure Pro
Deal ID: 123456789
[View in HubSpot]
```

---

### 2. Demo Booking (`02-demo-booking.json`)

**Trigger:** Webhook POST `/demo-booking`

**Payload:**
```json
{
  "deal_id": "123456789",
  "email": "cliente@example.com",
  "product_line": "Procure Pro",
  "calendar_link": "https://calendly.com/your-calendar"
}
```

**Flow:**
1. Recibe booking del calendario
2. Chequea product line (Procure vs otros)
3. Genera checklist pre-demo específico
4. Actualiza Deal en HubSpot (Stage: Demo Booked)
5. Publica en `#command-control` con checklist

**Checklist Procure Pro:**
- ✅ Verify moat health (make gate-remote)
- ✅ Prepare approval workflow demo
- ✅ Set up demo environment
- ✅ Prepare checkout demo (optional)

**Slack Output:**
```
📅 Demo Booked
Email: cliente@example.com
Deal ID: 123456789

Pre-demo Checklist:
• ✅ Verify moat health (make gate-remote)
• ✅ Prepare approval workflow demo
• ✅ Set up demo environment
• ✅ Prepare checkout demo (optional)

[Calendar Link] [View in HubSpot]
```

---

### 3. Billing to CRM Sync (`03-billing-to-crm-sync.json`)

**Trigger:** Webhook POST `/billing-webhook`

**Payload (desde CLI Market API):**
```json
{
  "event_type": "subscription_activated",
  "email": "cliente@example.com",
  "username": "cli-username",
  "payment_method": "paypal",
  "reference": "PRO-XXXXXXXX",
  "amount": 39,
  "currency": "USD"
}
```

**Flow:**
1. Parsea evento de billing (PayPal/MP/Yape/Plin)
2. Chequea si es `subscription_activated`
3. Lookup Contact en HubSpot por email
4. Lookup Deals asociados al contact
5. Selecciona deal más reciente que no sea customer
6. Actualiza Deal Stage → Customer
7. Agrega payment_method, activation_reference, amount
8. Publica en `#cli-market-pro`

**Slack Output:**
```
💳 Pro Activated
Email: cliente@example.com
Payment: PAYPAL
Amount: 39 USD
Reference: PRO-XXXXXXXX

Deal: Procure Pro - cliente@example.com
Deal ID: 123456789
[View in HubSpot]
```

---

### 4. Daily Command Control (`04-daily-command-control.json`)

**Trigger:** Cron (diario, configurable)

**Flow:**
1. Trigger cron (ej: 08:00 PET)
2. Fetch CLI Market health endpoint
3. Fetch Observatory metrics (MAA, active agents, retailers)
4. Fetch indicators daily
5. Fetch HubSpot deals por stage (New Lead, Demo Booked, Customer)
6. Agrega métricas (CLI Market + Sales + Revenue)
7. Calcula conversion rates (demo rate, customer rate)
8. Formatea daily briefing
9. Publica en `#command-control`

**Slack Output:**
```
📊 Daily Command Control - 2026-08-04

CLI Market Metrics:
MAA: 1,234
Active Agents: 892
Retailers: 38
Countries: 8

Sales Pipeline:
New Leads: 12
Demo Booked: 5
Customers: 3
Demo Rate: 41.7%

Revenue:
MRR: $117
ARR: $1,404
Customer Rate: 60.0%
Date: 2026-08-04

[View HubSpot Pipeline] [View CLI Market Stats]
```

---

## Configuración

### Credenciales en n8n

1. **HubSpot API**
   - Credential type: HubSpot API
   - API Key: HubSpot Private App Token

2. **Slack API**
   - Credential type: Slack API
   - Bot Token: `xoxb-...`
   - User Token: `xoxp-...` (opcional)

3. **CLI Market API Auth**
   - Credential type: HTTP Header Auth
   - Header Name: `Authorization`
   - Header Value: `Bearer ${MARKET_API_TOKEN}`

### Variables de entorno

Configurar en n8n (Settings → Variables):

```
HUBSPOT_PORTAL_ID=YOUR_PORTAL_ID
HUBSPOT_PIPELINE_ID=cli_market_procure
SLACK_CHANNEL_OUTBOUND=outbound
SLACK_CHANNEL_COMMAND_CONTROL=command-control
SLACK_CHANNEL_CLI_MARKET_PRO=cli-market-pro
CLI_MARKET_API_URL=https://cli-market-api.fly.dev
```

### Importación de workflows

1. Abrir n8n UI
2. Settings → Import from File
3. Seleccionar cada JSON
4. Actualizar credenciales en cada nodo
5. Activar workflows

---

## Integración con CLI Market API

### Nuevo endpoint en CLI Market

Agregar en `routers/billing.py`:

```python
@router.post("/billing/hubspot-webhook")
async def billing_hubspot_webhook(request: Request):
    """Trigger n8n workflow → HubSpot deal update"""
    event = await request.json()
    
    # Trigger n8n workflow
    n8n_webhook_url = os.getenv("N8N_BILLING_WEBHOOK_URL")
    if n8n_webhook_url:
        async with httpx.AsyncClient() as client:
            await client.post(n8n_webhook_url, json=event)
    
    return {"status": "ok"}
```

### Environment variables en Fly.io

```bash
N8N_BILLING_WEBHOOK_URL=https://your-n8n-instance.com/webhook/billing-webhook
N8N_LEAD_SYNC_WEBHOOK_URL=https://your-n8n-instance.com/webhook/lead-sync
N8N_DEMO_BOOKING_WEBHOOK_URL=https://your-n8n-instance.com/webhook/demo-booking
```

---

## Integración con Landing (Cloudflare Pages)

### Componente HubSpotLeadForm

Se creó el componente `landing/components/HubSpotLeadForm.tsx` que:

1. Envía datos a HubSpot Form API
2. Dispara webhook n8n para Slack sync
3. Maneja estados de loading, error y éxito
4. Soporta múltiples product lines y tier intents

### Uso en Pricing

En `landing/components/Pricing.tsx` se agregó la prop `useHubSpotForms`:

```jsx
// En /build page
<Pricing spoke="build" useHubSpotForms={true} />
```

### Configuración environment variables

En `landing/.env.example`:

```bash
# HubSpot Configuration
NEXT_PUBLIC_HUBSPOT_PORTAL_ID=YOUR_HUBSPOT_PORTAL_ID
NEXT_PUBLIC_HUBSPOT_FORM_ID=YOUR_HUBSPOT_FORM_ID

# n8n Webhook URLs
NEXT_PUBLIC_N8N_LEAD_SYNC_WEBHOOK_URL=https://your-n8n-instance.com/webhook/lead-sync
NEXT_PUBLIC_N8N_DEMO_BOOKING_WEBHOOK_URL=https://your-n8n-instance.com/webhook/demo-booking
NEXT_PUBLIC_N8N_BILLING_WEBHOOK_URL=https://your-n8n-instance.com/webhook/billing-webhook
```

### Pasos para activar

1. Crear form en HubSpot con campos: `email`, `product_line`, `tier_intent`, `lead_source`
2. Configurar `NEXT_PUBLIC_HUBSPOT_PORTAL_ID` y `NEXT_PUBLIC_HUBSPOT_FORM_ID` en Cloudflare Pages
3. Configurar `NEXT_PUBLIC_N8N_LEAD_SYNC_WEBHOOK_URL` con URL del workflow n8n
4. Agregar `useHubSpotForms={true}` en `<Pricing />` donde se quiera activar
5. Deploy landing a Cloudflare Pages

---

## Troubleshooting

### Webhook no responde

- Verificar que el workflow esté activo en n8n
- Chequear logs de ejecución en n8n
- Verificar credenciales (HubSpot, Slack)

### Deal no se crea en HubSpot

- Verificar HubSpot API Key
- Chequear que el pipeline `cli_market_procure` exista
- Verificar que las custom properties estén configuradas

### Slack notificación no llega

- Verificar Slack Bot Token
- Chequear que el bot esté invitado a los canales
- Verificar permisos del bot (chat:write, channels:join)

### Daily briefing no se ejecuta

- Verificar configuración de cron
- Chequear credenciales CLI Market API
- Verificar que CLI Market API esté respondiendo

---

## Próximos pasos

1. ✅ Crear workflows n8n
2. ⏳ Configurar HubSpot (properties, pipelines)
3. ⏳ Modificar landing con HubSpot form
4. ⏳ Agregar endpoint webhook en CLI Market API
5. ⏳ Test E2E: landing → HubSpot → n8n → Slack

---

## Documentación relacionada

- HubSpot setup: Configurar propiedades personalizadas y pipelines
- CLI Market billing: `ops/BILLING_MANUAL.md`
- Slack integration: `ops/slack_cli.py`
- E2E journey: `ops/E2E_CLIENT_JOURNEY.md`
