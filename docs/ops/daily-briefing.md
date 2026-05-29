# Daily Briefing — automatización

Dos reportes markdown por día, generados desde producción y el calendario GTM en el repo.

## Qué genera

| Archivo | Contenido |
|---------|-----------|
| `ops/daily/YYYY-MM-DD-product.md` | KPIs collector, inflación, movers, store health, frescura, outreach (misma fuente que `ops/monday.py`) |
| `ops/daily/YYYY-MM-DD-content.md` | Post LinkedIn del día N, hooks, comentario, checklist, preview mañana, backlog sin `published_at`, gates |

Además actualiza `docs/metrics/price-pulse-YYYY-WW.md` cuando corre el bloque de producto.

## Ejecución local

```bash
pip install httpx
python3 ops/daily_briefing.py           # ambos reportes
python3 ops/daily_briefing.py --product # solo producto
python3 ops/daily_briefing.py --content # solo contenido / LinkedIn
python3 ops/daily_briefing.py --dry-run # sin Slack
```

## Variables de entorno

| Variable | Default | Uso |
|----------|---------|-----|
| `DASHBOARD_DATA_URL` | Railway prod `/dashboard/data` | Métricas producto |
| `SLACK_WEBHOOK_URL` | — | Resumen corto a Slack |
| `LINKEDIN_CAMPAIGN_START` | `2026-05-01` | Día 1 del calendario 30d |
| `LINKEDIN_POST_UTC_HOUR` | `13` | Hora sugerida de publicación |

## Automatización (GitHub Actions)

Workflow: [`.github/workflows/daily-briefing.yml`](../../.github/workflows/daily-briefing.yml)

- **Cron:** `0 13 * * *` (todos los días 13:00 UTC)
- **Manual:** Actions → Daily Briefing → Run workflow
- **Commit automático** de `ops/daily/*.md` y price pulse semanal

Secret opcional en el repo: `SLACK_WEBHOOK_URL` (mismo que Monday Ops).

## Flujo operativo recomendado

```mermaid
flowchart LR
  A[13:00 UTC cron] --> B[daily_briefing.py]
  B --> C[product.md]
  B --> D[content.md]
  B --> E[Slack opcional]
  C --> F[Revisar tiendas críticas]
  D --> G[Publicar LinkedIn]
  G --> H[published_at en Day-XX.md]
```

1. Leer `*-product.md` → priorizar tiendas 🔴 y WARN.
2. Leer `*-content.md` → copiar post + comentario.
3. Tras publicar, editar frontmatter: `published_at: 2026-05-29`.

## Relación con Monday Ops

| Script | Frecuencia | Salida principal |
|--------|------------|------------------|
| `ops/monday.py` | Lunes (GH Action) | `ops/reports/YYYY-MM-DD.md` |
| `ops/daily_briefing.py` | Diario | `ops/daily/YYYY-MM-DD-{product,content}.md` |

Ambos usan el mismo endpoint de dashboard. El reporte diario de producto es el playbook ops con título "Daily Product Status".

## Extender

- **Nuevo calendario** (DEV.to, Reddit): añadir parser en `build_content_report()` leyendo `docs/dev-calendar.md`.
- **Marcar publicado vía CLI:** futuro `python3 ops/daily_briefing.py --mark-published`.
- **Email:** enviar `*-content.md` con SendGrid/Resend en el workflow.

[[linkedin-calendar]] · [[linkedin/00-Index]] · [[linkedin/data-gate]]
