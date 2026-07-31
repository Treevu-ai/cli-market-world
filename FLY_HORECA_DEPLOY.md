# Deploy HORECA Piloto a Fly.io

## 1. Configurar Secrets de Fly.io

Necesitas configurar las siguientes variables de entorno en Fly.io para el piloto HORECA:

### Secrets Twilio (requerido para Twilio WhatsApp)
```bash
fly secrets set TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
fly secrets set TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
fly secrets set TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
fly secrets set WHATSAPP_ALLOWED_NUMBERS=
fly secrets set WHATSAPP_ADMIN_NUMBERS=whatsapp:+519xxxxxxxx
```

### Secrets Telegram (opcional para bot Telegram)
```bash
fly secrets set TELEGRAM_BOT_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
fly secrets set TELEGRAM_WEBHOOK_SECRET=your_random_secret_here
fly secrets set TELEGRAM_ALLOWED_CHAT_IDS=
fly secrets set TELEGRAM_ADMIN_CHAT_IDS=123456789
```

### Secrets API (requerido para funcionar)
```bash
fly secrets set MARKET_API_TOKEN=your_market_api_token
fly secrets set MARKET_BOT_API_TOKEN=your_bot_scoped_token
fly secrets set OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Configuración HORECA (habilitar piloto)
```bash
fly secrets set HORECA_ENABLED=true
fly secrets set HORECA_FREE_SEARCHES_DAILY=5
fly secrets set HORECA_COOLDOWN_HOURS=4
fly secrets set HORECA_MAX_CONCURRENT_SEARCHES=3
fly secrets set HORECA_PRIORITY_CATEGORIES=aceites,limpieza,papel,bebidas,electrodomesticos
fly secrets set HORECA_SAVINGS_NOTIFICATION_THRESHOLD=50.0
```

## 2. Deploy a Fly.io

```bash
# Configurar la app Fly.io
fly launch

# Si ya existe la app
fly deploy

# Verificar que el servidor esté corriendo
fly logs
```

## 3. Configurar Webhook Twilio

1. Obtener la URL pública de tu app Fly.io:
```bash
fly info
```

2. Configurar el webhook en Twilio Console:
- URL: `https://tu-app.fly.dev/v1/integrations/whatsapp/webhook`
- Method: POST

## 4. Configurar Webhook Telegram (opcional)

```bash
# Set webhook para Telegram bot
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://tu-app.fly.dev/v1/integrations/telegram/webhook",
    "secret_token": "tu_secret_token"
  }'
```

## 5. Verificar Deploy

```bash
# Health check WhatsApp
curl https://tu-app.fly.dev/v1/integrations/whatsapp/health

# Health check Telegram
curl https://tu-app.fly.dev/v1/integrations/telegram/health
```

## 6. Testing del Piloto HORECA

### Onboarding flow
1. Enviar "hola" al número Twilio
2. El bot pedirá nombre del negocio
3. Luego pedirá tipo de negocio (1-4)
4. Se creará perfil HORECA con templates de ejemplo

### Comandos HORECA
- `mis ahorros` - Ver resumen de ahorros
- `mis plantillas` - Ver búsquedas guardadas
- `upgrade` - Ver planes HORECA

### Búsqueda normal
- Cualquier otra búsqueda usará lógica HORECA si está habilitada
- Incluirá cálculo de ahorro y notificaciones de hitos

## 7. Monitoring

```bash
# Ver logs en tiempo real
fly logs --tail

# Ver métricas
fly monitor
```

## Troubleshooting

### HORECA no funciona
- Verificar que `HORECA_ENABLED=true` esté configurado
- Verificar logs: `fly logs --tail | grep HORECA`

### Twilio webhook falla
- Verificar que TWILIO_ACCOUNT_SID y TWILIO_AUTH_TOKEN estén configurados
- Verificar que la URL webhook sea correcta y pública
- Verificar logs: `fly logs --tail | grep Twilio`

### DB migration falló
- Ejecutar manualmente: `python migrations/run_migration.py`
- Verificar que las tablas HORECA existan en la DB