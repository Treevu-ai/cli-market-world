# AGENTS.md — CLI Market

Instrucciones para agentes (Cursor, Cloud Agent, CI). Este archivo es la entrada única para cualquier agente que opere en el ecosistema CLI Market.

## Repos del producto

| Repo | Propósito | Path local |
|------|-----------|------------|
| `cli-market-world` | Producto principal, API, ops, Slack, docs | `.` |
| `cli-market-backend` | Collector, normalizador, billing, dashboard | `../cli-market-backend` |
| `cli-market-content` | Contenido GTM, 10 canales, calendario, plantillas | `../cli-market-content` |
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

Canales: **bitácora** `C0B6V3Y9ZSP` · **publicaciones** `C0B6ZJ1B9B8` · **revisiones-cursor** `C0B723TQS78` · **command-control** `#command-control-cli-market` (env `SLACK_CHANNEL_COMMAND_CONTROL`)

```bash
python3 ops/slack_cli.py command-control --remote   # panel founder (checklist + KPIs + tendencias)
python3 ops/slack_cli.py briefing
python3 ops/slack_cli.py post --bitacora "mensaje"
python3 ops/slack_cli.py post --publicaciones --file ops/daily/YYYY-MM-DD-content.md
python3 ops/slack_cli.py verify --send-test
```

Runbook founder: `ops/COMMAND_CONTROL.md` · `ops/DEPLOYMENT_MONITORING_DAILY_COMMANDS.md`

**Slack no ejecuta órdenes** escritas en el canal del bot; solo envía. Pedir cambios en Cursor o terminal.

## Reglas de contenido

- Español: castellano neutro LATAM (Perú). Ver `../cli-market-content/linkedin/STYLE-es.md`
- Claims: solo los del GTM Hub (`docs/gtm/README.md`). No inventar métricas.
- Data-gate: verificar antes de publicar posts data-gated. `make gate` en content repo.
- Imágenes: regenerar con `python3 ops/generate_all_linkedin_assets.py --patch`

## Cuándo usar cada agente

| Necesidad | Agente | Contexto |
|-----------|--------|----------|
| Generar reporte financiero semanal | 5 agentes finance | `docs/agents/price-pulse-workflow.md` |
| Escribir posts, tweets, artículos | content-creator | `../cli-market-content/AGENTS.md` |
| Responder DMs, comentarios, emails | support-responder | `docs/agents/contexts/support-responder-context.md` |
| Outbound a retailers | outbound-strategist | `../cli-market-content/outbound/` |
| Demo técnica a retailer | sales-engineer | `docs/agents/contexts/sales-engineer-context.md` |
