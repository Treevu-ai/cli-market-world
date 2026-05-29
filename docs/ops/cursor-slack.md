# Cursor + Slack — cómo trabajar juntos

CLI Market ya envía **briefings diarios** a Slack. Esta guía explica cómo pedirle a **Cursor** que te ayude en los mismos canales sin pegar tokens en el chat.

## Canales

| Canal | ID | Contenido |
|-------|-----|-----------|
| Bitácora (producto) | `C0B6V3Y9ZSP` | KPIs, tiendas críticas, collector |
| Publicaciones (redes) | `C0B6ZJ1B9B8` | Post LinkedIn del día, hooks, checklist |

Bot: `cli_market_dev_bot` — debe estar invitado: `/invite @cli_market_dev_bot`

## 1. Token en tu máquina (para Cursor local)

Crea `.env` en la raíz del repo (no se sube a git):

```bash
SLACK_BOT_TOKEN=xoxb-tu-token
SLACK_CHANNEL_BITACORA=C0B6V3Y9ZSP
SLACK_CHANNEL_PUBLICACIONES=C0B6ZJ1B9B8
```

En **PowerShell**:

```powershell
$env:SLACK_BOT_TOKEN = "xoxb-..."
```

En **bash / WSL**:

```bash
export SLACK_BOT_TOKEN=xoxb-...
```

## 2. Qué pedirle a Cursor en el chat

Ejemplos de instrucciones:

- «Ejecutá el briefing diario y envialo a Slack»
- «Publicá en bitácora un resumen de las tiendas críticas de hoy»
- «Mandá a publicaciones el post del Day 29»
- «Verificá que Slack siga funcionando»

Cursor usará la regla `.cursor/rules/slack-ops.mdc` y estos comandos:

| Pedido | Comando |
|--------|---------|
| Briefing completo | `python3 ops/slack_cli.py briefing` |
| Solo archivos, sin Slack | `python3 ops/slack_cli.py briefing --dry-run` |
| Mensaje corto bitácora | `python3 ops/slack_cli.py post --bitacora "..."` |
| Archivo a publicaciones | `python3 ops/slack_cli.py post --publicaciones --file ops/daily/YYYY-MM-DD-content.md` |
| Test de token | `python3 ops/slack_cli.py verify --send-test` |

## 3. Automático sin Cursor (GitHub Actions)

- Workflow: `.github/workflows/daily-briefing.yml`
- Cron: **13:00 UTC** todos los días
- Secret en repo: `SLACK_BOT_TOKEN`
- Manual: Actions → **Daily Briefing** → Run workflow

## 4. Cursor Cloud Agent (background)

El agente en la nube **no** lee tu `.env` local. Para que postee a Slack:

1. `SLACK_BOT_TOKEN` debe estar en **GitHub Secrets** del repo.
2. El workflow `daily-briefing` (o uno que dispares) hace el envío.
3. Pedí al agente: «al terminar, asegurate de que el workflow Daily Briefing pueda correr» o «commitea los reportes en ops/daily».

## 5. Escribir órdenes en el canal del bot — ¿funciona?

**No.** Si escribís en bitácora o publicaciones «empezá desde día 1» o «reestructurá los scripts», el bot **no** ejecuta nada.

| Lo que parece | Lo que hace el bot hoy |
|---------------|-------------------------|
| Chat con el bot en Slack | Solo **envía** textos que genera el repo (briefing, posts manuales vía CLI) |
| Pedir a Cursor en el canal | **No** hay Events API ni slash commands — nadie lee tus mensajes |
| Pedir en **Cursor IDE** o Cloud Agent | Sí: corre `ops/slack_cli.py`, `daily_briefing.py`, `sync_linkedin_metrics.py` |

Para publicar desde Día 1 con el producto actual: ver [[linkedin/catch-up-plan]] y `LINKEDIN_CAMPAIGN_START=2026-05-29`.

## 6. Qué Cursor no hace solo

- No reemplaza la **app de Slack** para conversar con el equipo.
- No lee mensajes entrantes (solo envía) — para eso haría falta Events API + servidor.
- No guarda el token: vos lo configurás en `.env` o GitHub Secrets.

## Diagrama

```mermaid
flowchart TB
  subgraph local [Cursor IDE en tu PC]
    U[Tú en chat]
    C[Agente Cursor]
    CLI[ops/slack_cli.py]
    U --> C --> CLI
  end
  subgraph cloud [Cursor Cloud / GitHub]
    GH[daily-briefing.yml]
  end
  CLI --> S[Slack API]
  GH --> S
  S --> B[Bitácora]
  S --> P[Publicaciones]
```

## Cambiar de cuenta o workspace

Hay **tres** cosas distintas; confundirlas hace que “vaya a otra cuenta”:

| Capa | Qué controla | Dónde se cambia |
|------|----------------|-----------------|
| **Cursor MCP Slack** | Con qué usuario lee/busca Cursor en Slack | Cursor → Settings → MCP → **Slack** → desconectar y volver a autorizar con la cuenta correcta |
| **`SLACK_BOT_TOKEN`** | Quién **publica** briefings (`ops/slack_cli.py`, GitHub Actions) | [api.slack.com/apps](https://api.slack.com/apps) → tu app → **Install to Workspace** en el workspace correcto → copiar `xoxb-...` |
| **IDs de canal** | A qué `#canal` llegan los posts | `.env` o secrets: `SLACK_CHANNEL_BITACORA`, `SLACK_CHANNEL_PUBLICACIONES` |

### Pasos recomendados

1. **Confirmar workspace del bot** (local, sin commitear el token):

   ```bash
   export SLACK_BOT_TOKEN=xoxb-tu-token-del-workspace-correcto
   python3 ops/verify_slack.py
   ```

   Debe mostrar el nombre del workspace y la URL (`https://tu-workspace.slack.com/`). Si no coincide, reinstalá la app en el workspace correcto y repetí.

2. **Actualizar token en todos los sitios** donde corre el envío:
   - `.env` en la raíz del repo (Cursor local)
   - GitHub → repo → Settings → Secrets → `SLACK_BOT_TOKEN`
   - Opcional: `SLACK_WEBHOOK_*` si usás webhooks en lugar del bot

3. **Canales en el workspace nuevo**
   - Creá `#bitácora` y `#publicaciones` (o los nombres que uses).
   - `/invite @cli_market_dev_bot` en cada uno.
   - Copiá el ID del canal (clic derecho → copiar enlace → el segmento `C...` de la URL).
   - En `.env`:

     ```bash
     SLACK_CHANNEL_BITACORA=C0XXXXXXXX
     SLACK_CHANNEL_PUBLICACIONES=C0YYYYYYYY
     ```

4. **Probar envío**

   ```bash
   python3 ops/verify_slack.py --send-test
   ```

5. **Cursor MCP** (solo para leer/escribir desde el chat del agente con herramientas Slack): si Cursor “ve” otro workspace, desconectá Slack en MCP y autorizá de nuevo con el usuario del workspace que querés.

Los IDs por defecto en el repo (`C0B6V3Y9ZSP`, `C0B6ZJ1B9B8`) son del workspace **climarketworspace**. Si movés todo a otro workspace, **hay que cambiar esos IDs**; no se transfieren entre workspaces.

## Troubleshooting

| Error | Solución |
|-------|----------|
| `invalid_auth` | Token `xoxb-...` válido; Reinstall app en Slack |
| `not_in_channel` | `/invite @cli_market_dev_bot` en el canal |
| `missing_scope` | Scope `chat:write` + Reinstall |
| `channel_not_found` | Token de un workspace y canal ID de otro → alinear token + `SLACK_CHANNEL_*` |
| Cursor no envía | ¿`SLACK_BOT_TOKEN` exportado en esa terminal? |
| MCP ve otro Slack | Reautorizar Slack en Cursor MCP (no usa `SLACK_BOT_TOKEN` del repo) |

[[daily-briefing]] · [[linkedin/STYLE-es]]
