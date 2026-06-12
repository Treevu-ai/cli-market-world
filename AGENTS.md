# AGENTS.md — CLI Market

Instrucciones para agentes (Cursor, Cloud Agent, CI). Este archivo es la entrada única para cualquier agente que opere en el ecosistema CLI Market.

## Repos del producto (4 repos + GTM)

| Repo | Propósito | Path local | Deploy / distribución |
|------|-----------|------------|------------------------|
| `cli-market-index` | Golden Records, entity resolution | `../cli-market-index` | Pin git en backend `requirements-private.txt` |
| `cli-market-core` | Intelligence SDK — MCP, billing, indicators | `../cli-market-core` | PyPI `cli-market-core` |
| `cli-market-backend` | **API producción** — collector, FastAPI, telemetría prod | `../cli-market-backend` | Railway |
| `cli-market-world` | PyPI `cli-market-world`, landing, ops/CI, mirror API dev | `.` | PyPI + Cloudflare landing |

**Orden de release** (cualquier feature cross-repo): **core → backend → world → index** (index solo si aplica). Checklists: `ops/PRICING-CHANGE-CHECKLIST.md`, `ops/OBSERVATORY-CHANGE-CHECKLIST.md`, `ops/RELEASE-DISPERSION.md`.

**PyPI (dos paquetes, una marca):** CTA GTM = `pip install cli-market-world` (incluye `cli-market-core`). Railway pin = solo `cli-market-core`. Doc canónica: `docs/PYPI-PACKAGE-MODEL.md`.

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

## Slack

Canales (un propósito por canal):

| Canal | Env | Qué va |
|-------|-----|--------|
| **command-control** | `SLACK_CHANNEL_COMMAND_CONTROL` | Panel founder 1×/día (KPIs + checklist) |
| **suscripciones-cli-pro** | `SLACK_CHANNEL_CLI_MARKET_PRO` | Solo `[REVENUE]`: pending / activated / cancelled |
| **funnel-cli-market** | `SLACK_CHANNEL_FUNNEL` | `[FUNNEL DIGEST]` adopción (registro, checkout) |
| **publicaciones** | `SLACK_CHANNEL_PUBLICACIONES` | Índice diario GTM (gate + checklist) |
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

Ritual diario (automático vía GitHub Actions, sin terminal):
- **07:30 PET** — `command-control-morning.yml` → `#command-control`
- **08:00 PET (13:00 UTC)** — `daily-briefing.yml` → índice en `#publicaciones` + copy por red en cada `SLACK_CHANNEL_*` GTM
- **tarde** — `funnel-digest-evening.yml` → `#funnel-cli-market`

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

Estrategia canónica: `docs/pricing-strategy.md`

| Capa | Producto | ICP | Precio |
|------|----------|-----|--------|
| Infra | CLI Market Pro | Agent builders (código) | $39/mes |
| App | Procure Copilot | Operadores de compras | $29–149/mes (API incluida en Pro+) |
| Datos | Intelligence / Price Pulse | Analistas, fintech | $300–500/mes |

**GTM:** no mezclar `pip install` con Procure en el mismo post. Outbound compras → solo Procure.

## Observatory (P0 — MCP Telemetry)

PRD: `docs/prd-observatory-p0.md` · Checklist 4 repos: `ops/OBSERVATORY-CHANGE-CHECKLIST.md`

| Capa | Repo |
|------|------|
| Primitivas (`market_observatory`, identity, DDL) | `cli-market-core` → PyPI |
| Middleware + routers prod | `cli-market-backend` → Railway |
| Mirror API + ops + landing `/stats` | `cli-market-world` |
| Golden Records | `cli-market-index` — sin cambios P0 |

- North Star: **MAA** (Monthly Active Agents)
- Prod telemetría: solo cuenta en **backend** desplegado; world mantiene mirror paridad
- Jobs (world): `ops/adoption_index.py`, `ops/observatory_daily.py`, `ops/indicators_daily.py`, workflows `observatory-nightly.yml`, `indicators-nightly.yml`

## Identidad visual

- Tokens y modos Terminal/Operations: `docs/BRAND.md`
- Métricas en creative: solo data-gate; neón &lt;15% del layout

## Reglas de contenido

- Español: castellano neutro LATAM (Perú). Ver `../cli-market-content/linkedin/STYLE-es.md`
- Claims: solo los del GTM Hub (`docs/gtm/README.md`). No inventar métricas.
- Data-gate: verificar antes de publicar posts data-gated. `make gate` en content repo.
- Imágenes: regenerar con `python3 ops/generate_all_linkedin_assets.py --patch`

## Cursor Cloud — Railway deploy

Prod API (`cli-market-production.up.railway.app`) **no** se actualiza solo con push a `main`. Requiere:

1. **Secret `RAILWAY_API_TOKEN`** — account token de https://railway.com/account/tokens (no project token)
2. En **GitHub Actions secrets** y/o **Cursor Cloud secrets**
3. Disparar: `python3 ops/railway_deploy.py --target both` o workflow **Deploy Railway**

Runbook: `ops/RAILWAY_DEPLOY.md`

## Cuándo usar cada agente

| Necesidad | Agente | Contexto |
|-----------|--------|----------|
| Generar reporte financiero semanal | 5 agentes finance | `docs/agents/price-pulse-workflow.md` |
| Escribir posts, tweets, artículos | content-creator | `../cli-market-content/AGENTS.md` |
| Responder DMs, comentarios, emails | support-responder | `docs/agents/contexts/support-responder-context.md` |
| Outbound a retailers | outbound-strategist | `../cli-market-content/outbound/` |
| Demo técnica a retailer | sales-engineer | `docs/agents/contexts/sales-engineer-context.md` |
| Demo / outbound Procure Copilot | sales-engineer + outbound-strategist | `docs/agents/contexts/sales-engineer-context.md` · `../cli-market-content/outbound/procure-sequences.md` |
