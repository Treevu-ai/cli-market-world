# Command & Control — Founder Ops

Canal Slack: **#command-control-cli-market**

Panel diario para el founder: checklist de comandos + KPIs con tendencia visual (sparklines).

## GTM CLI Market–first — qué va en este canal (2026-07-16)

**Este canal = salud del hub CLI Market**, no war room de Procure/hoteles.

| Va en command-control | No va aquí |
|----------------------|------------|
| Moat, coverage, index linkage, go-live, PAM | Copy de secuencia outbound hotel |
| Adoption / first search / MAA proxies | “Cerrar 2 Procure Pro” como único KPI |
| Checklist deploy y ops API | Target lists Trujillo / WhatsApp first-touch |
| Tendencias de KPIs producto | Briefing de copy GTM (eso es `#publicaciones`) |

| Ritual | Canal | Propósito |
|--------|--------|-----------|
| **Command-control** | este | Salud hub CLI Market |
| **Publicaciones** | `#publicaciones` + GTM `SLACK_CHANNEL_*` | Serie del día (mix 40/25/25/10) |
| **Outbound Procure** | `#outbound` | Solo compras / Secuencia B |
| **Funnel** | `#funnel-cli-market` | Registro / checkout API |
| **Revenue Pro API** | `#suscripciones-cli-pro` | Pro/cancelaciones API (no confundir con solo Procure) |
| **Bitácora** | `#bitácora` | Deploys / incidentes |

Canónico content: `cli-market-content/strategy/gtm-cli-market-first.md`.

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
- `index.registry_size`, `index.linkage_pct`, `index.linkage_level`, `index.linkage_alerts`
- `golive.overall`, `pam.pass/fail/skip`
- `adoption_index.score`, `adoption_index.grade`, `adoption_index.first_search`

## Diferencia con bitácora / GTM / outbound

| Canal | Propósito |
|-------|-----------|
| **command-control** | Checklist founder + métricas ops + tendencias (**hub CLI Market**) |
| **bitácora** | Narrativa producto (deploys, go-live) |
| **GTM / publicaciones** | Copy del día por serie (tools / data / agents) → `SLACK_CHANNEL_*` (08:00 PET) |
| **outbound** | Solo Procure / compras — no mezclar con tools MCP |

## Comandos del checklist (resumen)

Ver `ops/DEPLOYMENT_MONITORING_DAILY_COMMANDS.md` para el runbook completo.

Orden sugerido cada mañana (automático vía `morning-ops-chain.yml` @ 08:00 PET):

1. Revisar Actions → **Morning Ops Chain** (9 jobs verdes)
2. Publicar en redes el copy que ya está en Slack GTM
3. Content repo: `make publish date=YYYY-MM-DD`

Manual si la cadena falló: `gtm-preflight` + `daily-briefing` (bump `ops/gtm-ci-run.trigger`).

**Hoy (post-briefing):** copy en `#publicaciones` y `#linkedin-personal` → publicar LI → `cd cli-market-content && make publish date=2026-06-12`

Funnel digest: mismo bloque matutino (chain) → `#funnel-cli-market`. Revenue sigue en `#suscripciones-cli-pro`.

## Index API (Golden Records)

Montado en la API world:

- `GET /index/stats` — `registry_size`, `linkage_pct`
- Alertas linkage en panel C&C cuando `< 85%` meta, `< 70%` crítico, o caída `≥ 2pp` vs ayer
- `POST /index/resolve` — entity resolution
- `POST /index/backfill` — admin batch link

PAM ya no hace SKIP en `user.index_stats` / `user.index_resolve`.