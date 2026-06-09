# Command & Control — Founder Ops

Canal Slack: **#command-control-cli-market**

Panel diario para el founder: checklist de comandos + KPIs con tendencia visual (sparklines).

## Publicar panel

```bash
# KPIs locales + post Slack
python ops/slack_cli.py command-control

# KPIs desde producción (recomendado)
python ops/slack_cli.py command-control --remote

# Solo ver sin guardar histórico ni Slack
python ops/command_control_daily.py --dry-run --remote
```

## Configuración Slack

1. Invita al bot al canal: `/invite @CLI Market` (o el nombre del bot).
2. Opción A — auto-resolve (requiere scope `channels:read` en la app Slack).
3. Opción B — fija el ID del canal:
   ```bash
   export SLACK_CHANNEL_COMMAND_CONTROL=C0XXXXXXXX
   ```

Verificar:

```bash
python ops/verify_slack.py --send-test
```

## Histórico de métricas

Cada ejecución (sin `--dry-run`) appendea una línea JSON en:

`ops/metrics/command-control/history.jsonl`

Campos trackeados para sparklines:

- `moat.total_indexed`, `moat.snapshots_24h`, `moat.coverage_7d_pct`
- `index.registry_size`, `index.linkage_pct`
- `golive.overall`, `pam.pass/fail/skip`

## Diferencia con bitácora

| Canal | Propósito |
|-------|-----------|
| **bitácora** | Narrativa producto + contenido (daily_briefing) |
| **command-control** | Checklist founder + métricas ops + tendencias |

## Comandos del checklist (resumen)

Ver `ops/DEPLOYMENT_MONITORING_DAILY_COMMANDS.md` para el runbook completo.

Orden sugerido cada mañana:

1. `python ops/command_control_daily.py --slack --remote`
2. `python ops/daily_briefing.py`
3. `python ops/go_live_check.py --remote`
4. `python ops/production_acceptance.py --phase user --tier 2`
5. Content repo: `make today` → `make gate` → `make content`

Tarde (~18:00): `python ops/funnel_digest_daily.py --slack` → `#funnel-cli-market` (adopción; dinero sigue en `#suscripciones-cli-pro`).

## Index API (Golden Records)

Montado en la API world:

- `GET /index/stats` — `registry_size`, `linkage_pct`
- `POST /index/resolve` — entity resolution
- `POST /index/backfill` — admin batch link

PAM ya no hace SKIP en `user.index_stats` / `user.index_resolve`.