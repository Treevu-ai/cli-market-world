# WhatsApp bot — CLI Market (Twilio)

**Estado (2026-08-05):** funnel conversacional + canasta multi-línea en prod (Fly `cli-market-api` v328+).  
**Código:** `routers/integrations/whatsapp.py`, `whatsapp_conversation.py`, `whatsapp_horeca.py`  
**Tests:** `tests/test_whatsapp_*.py`  
**Deploy:** gated on CI → `Deploy Fly.io`; emergency: `gh workflow run "Deploy Fly.io" --ref main`

---

## 1. Qué es

Bot de precios de góndola LATAM sobre **Twilio WhatsApp Sandbox** (o número de negocio).  
No compra ni paga: solo consulta datos de CLI Market (search, basket, intel).

| Superficie | URL |
|------------|-----|
| Health | `GET https://cli-market-api.fly.dev/v1/integrations/whatsapp/health` |
| Webhook canónico | `POST https://cli-market-api.fly.dev/v1/integrations/whatsapp/webhook` |
| Webhook legacy (alias) | `POST https://cli-market-api.fly.dev/whatsapp/webhook` |
| Verify GET | ambas rutas → `200` + body `ok` |

Twilio debe apuntar al **canónico**. El alias existe porque en prod se observó tráfico a `/whatsapp/webhook` → **404** (mensajes en silencio).

---

## 2. Arquitectura

```text
WhatsApp user
    │
    ▼
Twilio (firma X-Twilio-Signature)
    │
    ▼
POST /v1/integrations/whatsapp/webhook   ← ack TwiML vacío (BackgroundTasks)
    │
    ├─ allowlist? ──no──► mensaje de denegación
    ├─ rate limit
    │
    ▼
_process_and_reply
    │
    ├─ HORECA (si HORECA_ENABLED): solo comandos / onboarding mid-flow
    │     mis ahorros, plantillas, costo menú, cotizar semana, upgrade, registrar…
    │     free-text de producto → NO retiene (fallthrough)
    │
    ▼
handle_standard_turn  (whatsapp_conversation.py)
    │
    ├─ hola / menu / help     → welcome
    ├─ 2–20 líneas / canasta  → POST /v1/basket/compare  (sin LLM)
    ├─ aceite (vago)          → clarify 1 pregunta
    ├─ aceite Primor 1L       → POST /products/search    (sin LLM)
    ├─ pick 1/2/3             → detalle producto o tienda
    └─ compara… / va a subir… → POST /v1/intel/ask       (LLM / Anthropic)
```

**Respuesta al usuario:** siempre vía Twilio REST (`messages.create`), no en el body del webhook (evita timeout Sandbox + error TwiML 12100).

---

## 3. Flujo conversacional estándar

### 3.1 Welcome (`hola`, `menu`, `ayuda`, `help`)

- Ejemplo mal vs bien (`aceite` vs `aceite Primor 1L`)
- Cómo armar canasta multi-línea
- Atajos: `menu`, `atras`, `1/2/3`

### 3.2 Query vaga (familia)

Palabras como `aceite`, `leche`, `limpieza`, `pollo`, …  
→ **No busca todavía.** Una pregunta con opciones numeradas (1–4).  
Estado sesión: `clarify`.

### 3.3 Medio / específico

Ej. `aceite vegetal`, `leche Gloria evaporada 400g`  
→ `POST /products/search` (`country=PE`, `require_all=true`, top 3)  
→ lista numerada; usuario elige `1`/`2`/`3` → ficha.

### 3.4 Canasta multi-línea (P0 de gastos)

**Formato** (2–20 líneas; también `;` si WhatsApp aplana):

```text
12 x leche Gloria 390 g
4 x aceite vegetal 1 L
2 x arroz extra 5 kg
```

O prefijo:

```text
canasta
2 x leche Gloria 390 g
1 x arroz extra 5 kg
```

Solo `canasta` / `cotizar` / `lista` → ayuda con plantilla.

**Backend:** `POST /v1/basket/compare`  
- `enveloped=false`  
- stores default: `wong`, `metro`, `plazavea`, `makro_pe`, `vega_pe`  
- **Requiere tier Pro** en el token del bot (`require_pro`)

**Comportamiento:**

| Resultado | Respuesta |
|-----------|-----------|
| Cobertura incompleta | No total ni “mejor tienda”; pide marca/presentación |
| Tiendas con canasta completa | Lista 1..N con total; pick → desglose línea a línea |
| Confianza baja de identidad | Muestra tiendas con nota de honestidad |
| HTTP 403 | Mensaje: canasta requiere Pro; buscar de a uno |

### 3.5 Intel (LLM)

Triggers: `compara`, `cuánto`, `va a subir`, `inflación`, `historial`, …  
→ `/v1/intel/ask` con guardrails (no inventar ahorro / mejor tienda).  
**Depende de créditos del proveedor LLM (Anthropic en prod).**

### 3.6 Sesión

Tabla `messenger_sessions` (`platform_id` = `whatsapp:+51…`):

| Campo | Uso |
|-------|-----|
| `last_context` | JSON `{"type":"wa_flow","state":...,"candidates":...,"stores":...}` |
| `last_query` | última consulta |
| `last_country` | default `PE` |

Estados: `idle` · `clarify` · `await_free_text` · `candidates` · `detail` · `basket_stores` · `basket_detail`

---

## 4. HORECA

Con `HORECA_ENABLED=true`:

| Retiene HORECA | Fallthrough al estándar |
|----------------|-------------------------|
| Onboarding a mitad (nombre ya set) | `hola`, productos, canasta |
| `horeca` / `registrar` / `mi negocio` | — |
| `mis ahorros`, `mis plantillas` | — |
| `costo menú`, `cotizar semana` | — |
| `upgrade` | — |
| Auto-seed Estación 90 (número configurado) | — |

No interpretar el primer mensaje free-text como nombre de negocio (bug histórico).

Detalle piloto: `FLY_HORECA_DEPLOY.md`.

---

## 5. Seguridad y límites

| Control | Detalle |
|---------|---------|
| Firma Twilio | Obligatoria; sin firma → 403 |
| Allowlist | `WHATSAPP_ALLOWED_NUMBERS` (prod: 2 números). Vacío = abierto (sandbox legacy) |
| Admin numbers | `WHATSAPP_ADMIN_NUMBERS` → pueden usar `MARKET_API_TOKEN` |
| Token público | `MARKET_BOT_API_TOKEN` (nunca admin para senders normales) |
| Rate limit | default 20/min, 300/día por sender (`whatsapp:{from}`) |
| Audio | Whisper + OpenAI; solo tras firma válida |

---

## 6. Secrets / env (Fly.io)

```bash
# Twilio
fly secrets set TWILIO_ACCOUNT_SID=AC...
fly secrets set TWILIO_AUTH_TOKEN=...
fly secrets set TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

# Access
fly secrets set WHATSAPP_ALLOWED_NUMBERS=whatsapp:+51...,whatsapp:+51...
fly secrets set WHATSAPP_ADMIN_NUMBERS=whatsapp:+51...

# API
fly secrets set MARKET_BOT_API_TOKEN=...   # bot-scoped; Pro si se usa canasta
fly secrets set MARKET_API_TOKEN=...       # solo admins allowlisted
fly secrets set MARKET_API_URL=https://cli-market-api.fly.dev

# LLM (intel path + audio)
# Anthropic (intel agent) — debe tener crédito
# OPENAI_API_KEY — Whisper

# HORECA
fly secrets set HORECA_ENABLED=true
# … ver FLY_HORECA_DEPLOY.md
```

Inventario: `ops/SECRETS_INVENTORY.md`.

### Health esperado

```json
{
  "status": "ok",
  "twilio_configured": true,
  "twilio_number_set": true,
  "bot_token_set": true,
  "allowlist_size": 2,
  "admin_list_size": 1,
  "horeca_enabled": true,
  "horeca_available": true,
  "webhook_path": "/v1/integrations/whatsapp/webhook",
  "webhook_path_legacy": "/whatsapp/webhook"
}
```

---

## 7. Configurar Twilio Console

1. **Messaging → Try it out → Send a WhatsApp message** (Sandbox)  
2. **When a message comes in:**  
   `https://cli-market-api.fly.dev/v1/integrations/whatsapp/webhook`  
   Method: **HTTP POST**  
3. Join sandbox: al `+1 415 523 8886` enviar `join <palabra-palabra>`  
   (el código de join **no** está en el repo; solo en Twilio Console)  
4. El número del usuario debe estar en `WHATSAPP_ALLOWED_NUMBERS` si la lista no está vacía  

### Error histórico: URL corta

```text
POST /whatsapp/webhook → 404
```

Síntoma: usuario escribe, bot no responde, logs solo 404.  
Fix: URL canónica + alias montado en `market_server.py` (`legacy_router`).

---

## 8. Operación y troubleshooting

### Comandos útiles

```bash
# Health
curl -sS https://cli-market-api.fly.dev/v1/integrations/whatsapp/health

# Logs
fly logs --app cli-market-api

# Filtrar WhatsApp
fly logs --app cli-market-api --no-tail | findstr /i "WhatsApp intel basket 403 503"

# Deploy de emergencia (si CI rojo por tests ajenos)
gh workflow run "Deploy Fly.io" --ref main
```

### Mensajes de error al usuario → causa

| Usuario ve | Causa típica | Acción |
|------------|--------------|--------|
| *No pude consultar los precios ahora* | `/v1/intel/ask` 503 o excepción en flujo | Logs: crédito Anthropic, token, exception |
| *No pude consultar el catálogo* | `/products/search` falló o sin token | Token bot, API down |
| *No pude verificar la canasta* | `basket/compare` error | Pro tier, stores, API |
| *requiere acceso Pro* | `require_pro` en basket | Subir tier de `MARKET_BOT_API_TOKEN` |
| *no está autorizado* | Fuera de allowlist | Agregar a `WHATSAPP_ALLOWED_NUMBERS` |
| Silencio total | Webhook mal URL / 404 / no join sandbox | Twilio URL + `join` |
| Menú Sandbox “You said :X…” | TwiML inválido o timeout (histórico) | Ack vacío + BackgroundTasks |

### Incidente 2026-08-05 (documentado)

1. Webhook en Twilio apuntaba a `/whatsapp/webhook` → 404.  
2. CI `test-pg` falló (tests async + `test_auth` ajeno) → **Deploy Fly skipped**.  
3. Prod seguía en código viejo (todo a intel).  
4. Anthropic: *credit balance too low* → 503 en `/v1/intel/ask`.  
5. Mitigación: deploy manual workflow_dispatch → **v328** con funnel + canasta + alias.  

**Lección:** canasta y search **no** deben depender del LLM; intel sí. Monitorear créditos del provider por separado del deploy del bot.

---

## 9. Deploy

| Mecanismo | Cuándo |
|-----------|--------|
| Push a `main` + CI verde | Normal (`workflow_run` de CI success) |
| `gh workflow run "Deploy Fly.io" --ref main` | Emergency / CI rojo por flaky ajeno |

Archivos que disparan imagen: `.py`, `requirements.txt`, `Dockerfile`, `fly.toml` (ver workflow).

Verificar post-deploy:

```bash
curl -sS https://cli-market-api.fly.dev/v1/integrations/whatsapp/health | jq .
fly releases --app cli-market-api
```

Presencia de `webhook_path_legacy` confirma build con funnel actual.

---

## 10. Tests

```bash
python -m pytest \
  tests/test_whatsapp_conversation.py \
  tests/test_whatsapp_allowlist.py \
  tests/test_whatsapp_webhook_signature.py \
  tests/test_whatsapp_webhook_latency.py \
  tests/test_whatsapp_rate_limit.py \
  tests/test_whatsapp_markdown_formatting.py \
  tests/test_whatsapp_legacy_webhook_path.py \
  -q
```

**Importante CI:** no usar `@pytest.mark.asyncio` en este suite si `test-pg` no carga el plugin de forma confiable. Usar `asyncio.run(...)` (como Telegram).

---

## 11. Roadmap documentado (no implementado)

| Fase | Qué | Notas |
|------|-----|--------|
| Hecho | Funnel vago → candidatos; canasta multi-línea | 2026-08-05 |
| Hecho | Alias `/whatsapp/webhook` | anti-404 |
| P1 | PDF texto nativo (export limpio) | parse + confirmación |
| P2 | PDF/scan OCR | caro; privacidad |
| — | Uno-por-uno rígido | **No** como default; lista multi-línea es el default |

Decisión de producto: lista en un mensaje > PDF como default; PDF opcional con confirmación humana del extracto.

---

## 12. Archivos clave

| Path | Rol |
|------|-----|
| `routers/integrations/whatsapp.py` | Webhook, Twilio, HORECA gate, envío |
| `routers/integrations/whatsapp_conversation.py` | Funnel + canasta + classify |
| `routers/integrations/whatsapp_horeca.py` | Comandos HORECA / Estación 90 |
| `market_server.py` | Monta `router` + `legacy_router` |
| `server_deps.py` | `get/update_messenger_session` |
| `FLY_HORECA_DEPLOY.md` | Secrets y piloto HORECA |
| `ops/SECRETS_INVENTORY.md` | Inventario de secrets |

---

## 13. Checklist go-live / smoke

- [ ] Health `ok`, `bot_token_set`, `twilio_configured`
- [ ] Twilio webhook = URL **canónica**
- [ ] Número de prueba en allowlist + `join` sandbox
- [ ] `hola` → welcome con canasta
- [ ] `aceite` → clarify (no monólogo LLM)
- [ ] 2 líneas producto → respuesta basket o gap (no “crédito Anthropic”)
- [ ] `compara leche…` → solo si hay crédito LLM / provider OK
- [ ] Número no allowlisted → denegación en lenguaje natural
- [ ] Firma inválida → 403 (no procesa)

---

*Última actualización: 2026-08-05 — funnel + canasta + alias + incidente Anthropic/deploy.*
