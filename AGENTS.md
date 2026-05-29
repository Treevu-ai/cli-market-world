# AGENTS.md — CLI Market

Instrucciones para agentes (Cursor, Cloud Agent, CI).

## Slack

Cuando el usuario pida apoyo en Slack, briefings, o publicar en bitácora/publicaciones:

1. Configuración / migración: `docs/ops/slack-setup.md`
2. Uso con Cursor: `docs/ops/cursor-slack.md`
2. Usar `python3 ops/slack_cli.py` (nunca commitear tokens)
3. Canales: **bitácora** `C0B6V3Y9ZSP` · **publicaciones** `C0B6ZJ1B9B8` · **revisiones-cursor** `C0B723TQS78`

Comandos rápidos:

```bash
python3 ops/slack_cli.py briefing
python3 ops/slack_cli.py post --bitacora "mensaje"
python3 ops/slack_cli.py post --publicaciones --file ops/daily/YYYY-MM-DD-content.md
python3 ops/slack_cli.py post --revisiones-cursor "resumen de revisión"
python3 ops/slack_cli.py verify --send-test
```

Regla detallada: `.cursor/rules/slack-ops.mdc`

## Ops diario

- `python3 ops/daily_briefing.py` — reportes producto + contenido
- `docs/ops/daily-briefing.md`
- Campaña LinkedIn desde Día 1 (2026-05-29): `docs/linkedin/catch-up-plan.md`
- `python3 ops/slack_cli.py campaign status` · `campaign sync` · `campaign assets`
- Contenido GTM: repo privado **`cli-market-content`** — ver `docs/CONTENT.md`
- `python3 ops/init_content_repo.py` · `CLI_MARKET_CONTENT_DIR=../cli-market-content`
- `python3 ops/generate_all_linkedin_assets.py` — regenera PNG en content repo

**Slack no ejecuta órdenes** escritas en el canal del bot; solo envía. Pedir cambios en Cursor o terminal.

## Español en copy

Castellano estándar (Perú / LATAM): `docs/linkedin/STYLE-es.md`
