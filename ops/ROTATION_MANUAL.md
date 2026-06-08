# Rotación manual de secretos (post-privatización)

> Generado tras exponer repos públicos. Los marcados ✅ ya se rotaron automáticamente.

## ✅ Rotados automáticamente

| Secreto | Dónde actualizado |
|---------|-------------------|
| `MARKET_API_TOKEN` | Railway production + GitHub Secret + `ops/.rotation-local.txt` |
| `CHECKOUT_WEBHOOK_SECRET` | Railway production + `ops/.rotation-local.txt` |
| `GH_PAT` | GitHub Secret (CI checkout de repos privados) |

## ⏳ Rotar manualmente (consolas externas)

### 1. Pepy (`PEPY_API_KEY`)
1. Ir a https://pepy.tech/user
2. Revocar la key antigua
3. Crear key nueva (máx. 3 activas)
4. Actualizar:
   ```bash
   railway variables --set "PEPY_API_KEY=nueva_key"
   gh secret set PEPY_API_KEY -R Treevu-ai/cli-market-world
   ```

### 2. Slack (`SLACK_BOT_TOKEN`)
1. https://api.slack.com/apps → tu app CLI Market
2. **OAuth & Permissions** → **Rotate** token (o reinstall app)
3. ```bash
   gh secret set SLACK_BOT_TOKEN -R Treevu-ai/cli-market-world
   ```
4. Si usas webhooks: regenerar en Slack → actualizar `SLACK_WEBHOOK_BITACORA` / `SLACK_WEBHOOK_PUBLICACIONES` en GitHub Secrets

### 3. Cloudflare (`CLOUDFLARE_API_TOKEN`)
1. https://dash.cloudflare.com/profile/api-tokens
2. Revocar token antiguo → crear nuevo (**Account · Cloudflare Pages · Edit**)
3. ```bash
   gh secret set CLOUDFLARE_API_TOKEN -R Treevu-ai/cli-market-world
   # opcional si CI no resuelve solo:
   gh secret set CLOUDFLARE_ACCOUNT_ID -R Treevu-ai/cli-market-world
   ```
4. Push a `main` con cambios en `landing/` dispara el workflow **Deploy Landing (Cloudflare Pages)** (build + `wrangler pages deploy`). Manual: `.\ops\deploy_landing.ps1`.

### 4. PayPal (Railway)
- https://developer.paypal.com/dashboard/applications
- Rotar **Client Secret** en la app Live
- Actualizar en Railway: `PAYPAL_CLIENT_SECRET`
- Verificar webhook en `PAYPAL_WEBHOOK_ID` sigue activo

### 5. Mercado Pago (Railway)
- https://www.mercadopago.com.pe/developers/panel/app
- Rotar credenciales de producción
- Actualizar: `MERCADOPAGO_ACCES_TOKEN_PRODUCTION`, `MERCADO_PAGO_CLIENT_SECRET_PRODUCTION`
- **No rotar** `MERCADOPAGO_WEBHOOK_SECRET` sin actualizar también el panel MP

### 6. SMTP Gmail (`SMTP_PASSWORD`)
- https://myaccount.google.com/apppasswords
- Revocar app password antigua → crear nueva
- `railway variables --set "SMTP_PASSWORD=nueva"`

### 7. Anthropic (`ANTHROPIC_API_KEY`)
- https://console.anthropic.com/settings/keys
- Revocar → crear nueva → Railway

### 8. PostgreSQL (`DATABASE_URL`)
- Railway dashboard → servicio Postgres → **Reset password**
- Railway actualiza `DATABASE_URL` automáticamente si está linked
- Verificar API: `curl https://cli-market-production.up.railway.app/health/db`

## Verificación post-rotación

```powershell
$env:MARKET_API_TOKEN = (Get-Content ops/.rotation-local.txt | Where-Object { $_ -match '^MARKET_API_TOKEN=' }) -replace '^MARKET_API_TOKEN=',''
curl -s "$env:MARKET_API_URL/dashboard/funnel?days=7" -H "Authorization: Bearer $env:MARKET_API_TOKEN"
python ops/go_live_check.py --remote
```

## Local founder

Nuevo admin token guardado en **`ops/.rotation-local.txt`** (gitignored). Cargar en cada terminal nueva:

```powershell
$env:MARKET_API_TOKEN = (Get-Content ops/.rotation-local.txt | Where-Object { $_ -match '^MARKET_API_TOKEN=' }) -replace '^MARKET_API_TOKEN=',''
```