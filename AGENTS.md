# AGENTS.md — CLI Market

Instrucciones para agentes (Cursor, Cloud Agent, CI).

## Slack

Cuando el usuario pida apoyo en Slack, briefings, o publicar en bitácora/publicaciones:

1. Leer `docs/ops/cursor-slack.md`
2. Usar `python3 ops/slack_cli.py` (nunca commitear tokens)
3. Canales: **bitácora** `C0B6V3Y9ZSP` · **publicaciones** `C0B6ZJ1B9B8`

Comandos rápidos:

```bash
python3 ops/slack_cli.py briefing
python3 ops/slack_cli.py post --bitacora "mensaje"
python3 ops/slack_cli.py post --publicaciones --file ops/daily/YYYY-MM-DD-content.md
python3 ops/slack_cli.py verify --send-test
```

Regla detallada: `.cursor/rules/slack-ops.mdc`

## Ops diario

- `python3 ops/daily_briefing.py` — reportes producto + contenido
- `docs/ops/daily-briefing.md`
- Campaña LinkedIn desde Día 1 (2026-05-29): `docs/linkedin/catch-up-plan.md`
- `python3 ops/slack_cli.py campaign status` · `campaign sync` — métricas + día N

**Slack no ejecuta órdenes** escritas en el canal del bot; solo envía. Pedir cambios en Cursor o terminal.

## Español en copy

Castellano estándar (Perú / LATAM): `docs/linkedin/STYLE-es.md`
