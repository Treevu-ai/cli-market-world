# AGENTS.md — CLI Market

Instrucciones para agentes (Cursor, Cloud Agent, CI). Este archivo es la entrada única para cualquier agente que opere en el ecosistema CLI Market.

## Repos del producto (4 repos + GTM)

| Repo | Propósito | Path local | Deploy / distribución |
|------|-----------|------------|------------------------|
| `cli-market-index` | Golden Records, entity resolution | `../cli-market-index` | Pin git en backend `requirements-private.txt` |
| `cli-market-core` | Intelligence SDK — MCP, billing, indicators | `../cli-market-core` | PyPI `cli-market-core` |
| `cli-market-backend` | Mirror API — paridad con prod; pin `cli-market-core` | `../cli-market-backend` | Sin deploy directo (sync manual / auto-PR) |
| `cli-market-world` | **Fly.io prod** (`cli-market-api.fly.dev`) + PyPI `cli-market-world`, landing, ops/CI | `.` | Fly.io + PyPI + Cloudflare landing |

**Orden de release** (cualquier feature cross-repo): **core → backend → world → index** (index solo si aplica). Checklists: `ops/PRICING-CHANGE-CHECKLIST.md`, `ops/OBSERVATORY-CHANGE-CHECKLIST.md`, `ops/RELEASE-DISPERSION.md`.

**PyPI (dos paquetes, una marca):** CTA GTM = `pip install cli-market-world` (incluye `cli-market-core`). Pin de prod (Fly.io) = solo `cli-market-core`. Doc canónica: `docs/PYPI-PACKAGE-MODEL.md`.

| Repo auxiliar | Propósito | Path local |
|---------------|-----------|------------|
| `cli-market-content` | GTM autónomo — 10 canales, calendario | `../cli-market-content` |
| `agency-agents` | Librería de definiciones de agentes | `../agency-agents` |

## Content repo (cli-market-content)

El content repo es autónomo. Tiene su propio `AGENTS.md`, scripts, y Makefile. Para operar contenido:

```bash
cd ../cli-market-content
make today       # dashboard: qué publicar hoy
make content     # copy listo para pegar
make brief       # briefing detallado LinkedIn
make gate        # verificar data-gate
make publish day=N  # marcar día como publicado
```

**Configuración de campaña:**
- Inicio oficial: **2026-06-01 = Día 1**
- Offsets: `PERSONAL=+2` (archivo Day-03 = Día 1), `COMPANY=-1` (Company-Day-01 = Día 2)
- Soft-launch previo: Day-01 y Day-02 publicados 2026-05-29 y 2026-05-30
- Estos defaults ya están en los scripts y Makefile del content repo

**Canales activos y sus drafts:**
10 canales con contenido listo — ver `../cli-market-content/calendar/master-calendar.md`

## Agentes financieros (Price Pulse)

Workflow documentado en `docs/agents/price-pulse-workflow.md`.
5 agentes de `agency-agents/finance/` con contextos en `docs/agents/contexts/`.

```bash
python3 ops/price_pulse_agents.py --prepare
python3 ops/price_pulse_agents.py --assemble
python3 ops/price_pulse_agents.py --run
```

Output: PDF de 10 secciones, 3 tiers comerciales ($300-500/mes).

## Market Orchestrator

Router por request (distinto de Price Pulse, que es un plan congelado semanal): entiende el pedido en lenguaje natural, clasifica intent, arma un plan de tools + sub-agentes, ejecuta contra la API real, enriquece con LLM y sintetiza una respuesta con grounding (FactIndex) contra los datos reales.

- Contrato: `docs/agents/orchestrator-contract.md` (v0.2.0, roster v2 — 6 agentes)
- System prompt: `docs/agents/contexts/orchestrator-context.md`
- Runtime: `ops/market_orchestrator.py` (v0.2.1)

```bash
python ops/market_orchestrator.py --plan "optimiza leche, arroz PE budget 200"
python ops/market_orchestrator.py --run --mode fast --synthesize "inflación supermercados PE"
```

Auth: `CLI_MARKET_API_KEY` / `MARKET_API_KEY`, o `~/.market/session.json`. LLM: `ORCHESTRATOR_LLM_PROVIDER` (openai default) + `OPENAI_API_KEY`. Artefactos en `ops/generated/orchestrator/`.

**Roster activo (6 de 14 agentes v1, consolidado 2026-07-16):** `pricing-analyst`, `supply-chain`, `operations`, `reality-checker` (siempre presente — backstop anti-alucinación), `analytics-reporter`, `hospitality` (condicional, segment=hotelero). El resto del roster v1 se cortó por redundante con SYNTHESIZE, genérico sin grounding real, o incompatible con el contrato de datos de este pipeline — detalle en `docs/agents/orchestrator-contract.md` §4.3.

## Slack

Canales (un propósito por canal):

| Canal | Env | Qué va |
|-------|-----|--------|
| **command-control** | `SLACK_CHANNEL_COMMAND_CONTROL` | Panel founder 1×/día — **salud hub CLI Market** (KPIs + checklist); no outbound hotel |
| **suscripciones-cli-pro** | `SLACK_CHANNEL_CLI_MARKET_PRO` | Solo `[REVENUE]`: pending / activated / cancelled |
| **funnel-cli-market** | `SLACK_CHANNEL_FUNNEL` | `[FUNNEL DIGEST]` adopción (registro, checkout) |
| **publicaciones** | `SLACK_CHANNEL_PUBLICACIONES` | Índice diario GTM por **serie del día** + mix 40/25/25/10 (gate + checklist) |
| **outbound** | `SLACK_CHANNEL_OUTBOUND` | Solo Procure / compras — sin pip/MCP |
| **linkedin-personal** | `SLACK_CHANNEL_LINKEDIN_PERSONAL` | Copy LI founder |
| **linkedin-empresa** | `SLACK_CHANNEL_LINKEDIN_COMPANY` | Copy LI página |
| **twitter-x** | `SLACK_CHANNEL_TWITTER` | Tweets / threads |
| **devto** | `SLACK_CHANNEL_DEVTO` | Artículos DEV.to |
| **reddit** | `SLACK_CHANNEL_REDDIT` | Posts Reddit |
| **hn** | `SLACK_CHANNEL_HN` | Show HN |
| **threads** | `SLACK_CHANNEL_THREADS` | Threads (opcional: `SLACK_MIRROR_TWITTER_TO_THREADS=1`) |
| **instagram** | `SLACK_CHANNEL_INSTAGRAM` | Grid IG (desde Jul) |
| **whatsapp** | `SLACK_CHANNEL_WHATSAPP` | Canal WA (desde Jul) |
| **newsletter** | `SLACK_CHANNEL_NEWSLETTER` | Price Pulse / Beehiiv |
| **outbound** | `SLACK_CHANNEL_OUTBOUND` | Secuencias DM retailers |
| **bitácora** | `SLACK_CHANNEL_BITACORA` | Salud producto, deploys, go-live |
| **revisiones-cursor** | `SLACK_CHANNEL_REVISIONES_CURSOR` | PRs / agentes |

Ritual diario (automático vía **`morning-ops-chain.yml`**, **08:00 PET = 13:00 UTC** — jobs encadenados, sin carreras):

1. adoption-index → indicators → observatory snapshot
2. PAM tier1 → tier2
3. command-control → `#command-control`
4. gtm-preflight → gate + content `check-gate.py` / `status.py`
5. daily-briefing → `#publicaciones` + copy por red en cada `SLACK_CHANNEL_*` GTM
6. funnel-digest → `#funnel-cli-market`

Ad-hoc (sin cadena): `workflow_dispatch` en cada workflow individual, o bump `ops/gtm-ci-run.trigger` en `main` (solo GTM preflight + briefing).

**No usar "Re-run all jobs"** en runs fallidos viejos — reutilizan YAML antiguo. Usar **Run workflow** o bump del trigger.

Manual si hace falta: `python3 ops/slack_cli.py briefing`. Funnel en tiempo real solo con `SLACK_FUNNEL_REALTIME=1`.

Secrets requeridos en GitHub: `SLACK_BOT_TOKEN`, `GH_PAT` (checkout cli-market-content). El bot debe estar invitado a todos los canales GTM.

```bash
python3 ops/slack_cli.py command-control --remote   # panel founder (checklist + KPIs + tendencias)
python3 ops/slack_cli.py briefing
python3 ops/slack_cli.py funnel-digest              # digest adopción → #funnel-cli-market
python3 ops/slack_cli.py post --bitacora "mensaje"
python3 ops/slack_cli.py post --publicaciones --file ops/daily/YYYY-MM-DD-content.md
python3 ops/slack_cli.py verify --send-test
```

Runbook founder: `ops/COMMAND_CONTROL.md` · `ops/DEPLOYMENT_MONITORING_DAILY_COMMANDS.md`

**Slack no ejecuta órdenes** escritas en el canal del bot; solo envía. Pedir cambios en Cursor o terminal.

## Pricing (ecosistema — sin canibalización)

Estrategia canónica: `docs/pricing-strategy.md` · GTM CLI Market–first: `../cli-market-content/strategy/gtm-cli-market-first.md`

| Capa | Producto | ICP | Precio |
|------|----------|-----|--------|
| Infra | CLI Market Pro | Agent builders (código) | $39/mes |
| App | Procure Copilot | Operadores de compras | $29–149/mes (API incluida en Pro+) |
| Datos | Intelligence / Price Pulse | Analistas, fintech | $300–500/mes |

**Promesas:** CLI Market = datos/tools góndola LATAM (API/CLI/MCP). Procure = app de compras encima de CLI Market (sin código).  
**GTM:** hub = CLI Market; spoke = Procure. No mezclar `pip install` con Procure en el mismo post. Outbound compras → solo Procure.  
**Mix content:** 40% tools/MCP · 25% data · 25% Procure · 10% retailers (`cli-market-content/strategy/content-strategy.md`).

## Observatory (P0 — MCP Telemetry)

PRD: `docs/prd-observatory-p0.md` · Checklist 4 repos: `ops/OBSERVATORY-CHANGE-CHECKLIST.md`

| Capa | Repo |
|------|------|
| Primitivas (`market_observatory`, identity, DDL) | `cli-market-core` → PyPI |
| Middleware + routers prod | `cli-market-world` → Fly.io |
| Mirror sin deploy (paridad vía `sync-backend-observatory-mirror.yml`) | `cli-market-backend` |
| Ops + landing `/stats` | `cli-market-world` |
| Golden Records | `cli-market-index` — sin cambios P0 |

- North Star: **MAA** (Monthly Active Agents)
- Prod telemetría: cuenta en **world** desplegado (Fly.io); backend recibe mirror de paridad, sin deploy propio
- Jobs (world): `ops/adoption_index.py`, `ops/observatory_daily.py`, `ops/indicators_daily.py`, `ops/canasta_pe_index.py`, workflows `observatory-nightly.yml`, `indicators-nightly.yml`, `canasta-pe-weekly.yml` (lunes 08:00 PET)

## Identidad visual

- Tokens y modos Terminal/Operations: `docs/BRAND.md`
- Métricas en creative: solo data-gate; neón &lt;15% del layout

## Reglas de contenido

- Español: castellano neutro LATAM (Perú). Ver `../cli-market-content/linkedin/STYLE-es.md`
- Claims: solo los del GTM Hub (`docs/gtm/README.md`). No inventar métricas.
- Data-gate: verificar antes de publicar posts data-gated. `make gate` en content repo.
- Imágenes: regenerar con `python3 ops/generate_all_linkedin_assets.py --patch`

## Deploy prod — Fly.io

Prod API (`cli-market-api.fly.dev`) se despliega **desde este repo** (`cli-market-world`),
**automáticamente** vía `.github/workflows/deploy-fly.yml`: cualquier push a `main` que toque
`**.py`, `requirements.txt`, `Dockerfile` o `fly.toml` dispara `flyctl deploy --app
cli-market-api --config fly.toml`. `fly.toml`/`fly.collector.toml` están commiteados en este
repo (commit `f76dca8`, 2026-07-06).

- Secrets ya deben estar seteados con `fly secrets set` (no se pueden leer de vuelta vía CLI).
- Deploy manual (solo si hace falta forzar fuera del flujo de CI):
  `fly deploy --app cli-market-api --dockerfile Dockerfile`.

`cli-market-backend` **ya no tiene** `fly.toml`/`fly.collector.toml` (se borraron en su commit
`57b01ef`, *"world owns the deploy"*) — antes ambos repos apuntaban a la misma app
`cli-market-api`, con riesgo de que un deploy accidental desde backend sobrescribiera prod con
el código equivocado. Hoy `cli-market-backend` no despliega nada: solo recibe sync
unidireccional de `world` (paridad de CI vía `sync-backend-ci.yml`, rutas de Observatory vía
`sync-backend-observatory-mirror.yml`). Ver tabla de repos arriba.

## MCP server de CLI Market en agentes (Devin / Cursor / Claude)

El MCP server (`market-mcp`) expone las tools de CLI Market a agentes locales. La API de producción vive en `https://cli-market-api.fly.dev`.

### Workaround conocido: encoding en Windows

Si `mcp_list_tools` o tools como `market_search`/`market_discover` devuelven `Failed to connect to MCP server 'cli-market'`, el problema puede ser un `UnicodeEncodeError` en el stdio del servidor cuando la consola de Windows usa `cp1252` en lugar de UTF-8.

**Fix local:** agregar `PYTHONIOENCODING=utf-8` al env del servidor MCP:

```json
{
  "mcpServers": {
    "cli-market": {
      "command": "market-mcp",
      "args": [],
      "env": {
        "MARKET_API_URL": "https://cli-market-api.fly.dev",
        "MARKET_API_TOKEN": "${MARKET_API_TOKEN}",
        "MCP_TOOL_PROFILE": "default",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

Ubicación típica en Devin for Terminal: `~/.claude/settings.json`.

También se commiteó un fix defensivo en `market_mcp.py` del repo para forzar UTF-8 en `stdout`/`stderr` en Windows.

### Troubleshooting adicional

Ver `docs/TROUBLESHOOTING-MCP.md` para casos de timeouts de API, `market_optimize_purchase` que no resuelve items, y retailers catalogados sin datos.

## Cuándo usar cada agente

| Necesidad | Agente | Contexto |
|-----------|--------|----------|
| Generar reporte financiero semanal | 5 agentes finance | `docs/agents/price-pulse-workflow.md` |
| Escribir posts, tweets, artículos | content-creator | `../cli-market-content/AGENTS.md` |
| Responder DMs, comentarios, emails | support-responder | `docs/agents/contexts/support-responder-context.md` |
| Outbound a retailers | outbound-strategist | `../cli-market-content/outbound/` |
| Demo técnica a retailer | sales-engineer | `docs/agents/contexts/sales-engineer-context.md` |
| Demo / outbound Procure Copilot | sales-engineer + outbound-strategist | `docs/agents/contexts/sales-engineer-context.md` · `../cli-market-content/outbound/procure-sequences.md` |

## graphify (memoria + tokens)

Antes de explorar a ciegas o hacer grep multi-archivo:

1. L0: `%USERPROFILE%\.graphify\cli-market\CLI-MARKET-MEMORY.md`
2. Grafo producto: `%USERPROFILE%\.graphify\cli-market\product-graph.json` (o local `graphify-out/graph.json`)
3. `graphify query|path|explain --graph <G> --budget 800-1500` → abrir solo 1–3 `source_file`
4. No volcar vault Obsidian al prompt (~20k notas)

Refresh producto:

```powershell
pwsh $env:USERPROFILE\.graphify\cli-market\refresh-product-graph.ps1
```

Reglas completas: `%USERPROFILE%\.graphify\cli-market\GRAPHIFY-AGENT-RULES.md`

Tras cambios de código en este repo: `graphify update .`
