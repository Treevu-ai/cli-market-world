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

### Piloto Estación 90 (Surco)
```bash
# Número WhatsApp del encargado de compras/cocina
fly secrets set HORECA_ESTACION90_WHATSAPP=whatsapp:+51XXXXXXXXX
fly secrets set HORECA_ESTACION90_AUTO_SEED=true
fly secrets set HORECA_ESTACION90_BUSINESS_NAME="Estación 90"
fly secrets set HORECA_ESTACION90_STORES=wong,metro,plazavea
fly secrets set HORECA_ESTACION90_MENU_URL=https://estacion90.pe/api/menu.json
```

O ejecutar el script: `bash ops/horeca/estacion90_fly_secrets.sh`

**Hostinger:** Estación 90 es un cliente potencial — la integración de subida
está lista pero **inactiva** hasta que comparta credenciales FTP de su
hosting. `hostinger/estacion90/api/menu.json` se sube automáticamente a
`public_html/api/menu.json` en estacion90.pe cada vez que cambia en `main`
(workflow `.github/workflows/sync-estacion90-menu.yml`, vía FTPS con
`ops/horeca/sync_estacion90_menu.py`) — pero solo si los 3 secrets de abajo
están configurados; si no, el workflow valida el JSON y omite la subida sin
fallar (no rompe CI). Cuando Estación 90 entregue las credenciales, agregar
estos secrets en GitHub (Settings → Secrets and variables → Actions):

```
HOSTINGER_ESTACION90_FTP_HOST
HOSTINGER_ESTACION90_FTP_USER
HOSTINGER_ESTACION90_FTP_PASSWORD
```

Para subir manualmente (o probar credenciales) sin esperar un push a `main`:

```bash
# Valida el JSON sin subir nada
python ops/horeca/sync_estacion90_menu.py --dry-run

# Sube y verifica que la URL pública quedó igual al archivo local
HOSTINGER_ESTACION90_FTP_HOST=... \
HOSTINGER_ESTACION90_FTP_USER=... \
HOSTINGER_ESTACION90_FTP_PASSWORD=... \
python ops/horeca/sync_estacion90_menu.py
```

También se puede disparar el workflow a mano desde GitHub Actions
("Run workflow" en `sync-estacion90-menu.yml`).

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

**Doc canónica del bot (funnel, canasta multi-línea, ops, incidentes):**  
[`docs/integrations/whatsapp-bot.md`](docs/integrations/whatsapp-bot.md)

1. Twilio Console → Messaging → Try it out → Send a WhatsApp message (Sandbox)
2. **When a message comes in:**
   - URL: `https://cli-market-api.fly.dev/v1/integrations/whatsapp/webhook` (canónica)
   - Method: **HTTP POST**
3. No depender de `/whatsapp/webhook` sola (histórico 404). Hay alias de compatibilidad, pero usá la canónica.
4. Join: `join <código>` al `+1 415 523 8886` (código solo en Twilio Console).
5. Allowlist: números de prueba en `WHATSAPP_ALLOWED_NUMBERS`.

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

### Flujo estándar (default para free-text)
1. `hola` → welcome con ejemplos + canasta
2. `aceite` → clarify (no LLM)
3. Lista multi-línea → `basket/compare` (requiere Pro en `MARKET_BOT_API_TOKEN`)
4. `compara…` → intel (requiere crédito LLM / Anthropic)

Ver checklist completo: `docs/integrations/whatsapp-bot.md` §13.

### Onboarding HORECA (explícito)
1. Enviar `registrar` / `horeca` / `mi negocio` (no el primer free-text genérico)
2. El bot pedirá nombre del negocio y tipo (1–4)
3. Perfil HORECA + templates de ejemplo

### Comandos HORECA
- `mis ahorros` - Ver resumen de ahorros
- `mis plantillas` - Ver búsquedas guardadas
- `costo menú` / `menú del día` - Costo estimado de insumos (Estación 90)
- `cotizar semana` - Insumos semanales (Estación 90 + Procure)
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