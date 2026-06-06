# Production Acceptance Matrix (PAM)

Certificación integral del producto CLI Market: API pública, touchpoints privados, landing y checklist manual CLI/MCP.

## Archivos

| Archivo | Rol |
|---------|-----|
| `ops/pam_matrix.yaml` | **Matriz editable** — casos, tiers, fases, checklist manual |
| `ops/pam_matrix.json` | Copia JSON (generada; el runner la prefiere si existe) |
| `ops/production_acceptance.py` | Runner automatizado |
| `ops/reports/pam-*.json` | Reportes de cada corrida |
| `ops/smoke_e2e.sh` | Smoke rápido legacy (4 checks) |
| `ops/E2E_CLIENT_JOURNEY.md` | Journey comercial Pro |

## Fases

| Fase | Qué cubre | Auth |
|------|-----------|------|
| `public` | Health, catálogo, dashboard data, billing funnel, OpenAPI | Ninguna |
| `landing` | cli-market.dev, llms.txt, mcp.json | Ninguna |
| `user` | search, index, intel, cart, analytics | `sk-` (auto-register o `MARKET_USER_TOKEN`) |
| `admin` | contacts, retailer apps, scan-stores, destructive smoke | `MARKET_API_TOKEN` |
| `post` | **Auto con tier≥2** — validación estricta batch 38/38 al final | Ninguna |
| `manual` | pip install, MCP, PayPal/MP — solo checklist impresa | Humano |

**Collector y destructive:** `admin.collect_smoke` pisa el último run a 2/2. Con tier≥2 (fase `post` auto):
- `public.health_collector` — solo liveness (`status`, `stores_total`).
- `admin.collector_trigger` y `admin.collect_smoke` — **SKIP** si `post` está en la corrida.
- `post.health_collector_batch` — poll hasta 180s si el daemon está `in_progress`; validación 38/38.

Para probar smoke aislado: `--phase admin --tier 2 --include-destructive` (sin `post`).

## Tiers

- **Tier 1** — Core del producto; debe estar 100% PASS antes de release.
- **Tier 2** — Importante pero no bloqueante (alerts, export, retailer apply, destructive admin).

## Uso rápido

```bash
cd cli-market-world

# Generar JSON desde YAML (requiere: pip install pyyaml)
python ops/production_acceptance.py --sync-json

# Ver matriz sin ejecutar
python ops/production_acceptance.py --dry-run --phase all --tier 2

# Core público + landing (sin secretos)
python ops/production_acceptance.py --phase public,landing --tier 1

# + usuario (auto-registra API key en prod)
python ops/production_acceptance.py --phase public,landing,user --tier 1

# + admin (necesita token)
export MARKET_API_TOKEN="..."
python ops/production_acceptance.py --phase public,landing,user,admin --tier 1

# Admin con side-effects (collector trigger, collect, backfill)
python ops/production_acceptance.py --phase admin --tier 2 --include-destructive

# Solo checklist manual CLI/MCP/billing
python ops/production_acceptance.py --phase manual
```

## Variables de entorno

| Variable | Uso |
|----------|-----|
| `MARKET_API_URL` | Default: prod Railway |
| `MARKET_API_TOKEN` | Admin Bearer (local: `$env:…`; GH: Secret o Variable de repo) |
| `MARKET_USER_TOKEN` | Opcional `sk-…`; si falta, usa `/auth/register` |
| `PAM_LANDING_URL` | Default: `https://cli-market.dev` |
| `PAM_REPORT_DIR` | Default: `ops/reports/` |

## Criterio de “listo para release”

1. **Tier 1** automatizado: 0 FAIL (SKIP admin ok si no hay token en CI).
2. **Manual tier 1**: los 4 ítems del checklist ejecutados una vez y anotados.
3. Reporte archivado en `ops/reports/`.

## Cobertura actual (~50 casos automatizados)

### Cubierto
- Health + collector + dashboard KPIs
- Catálogo `/lines`, `/stores`, `/countries`
- OpenAPI, FX, PayPal/MP status, request-pro, contact
- Landing llms.txt + mcp.json
- User: search, compare, index, intel v1, cart add chain
- Admin read-only: contacts, retailer applications

### Tier 2 / manual (documentado, no todos automatizados)
- Checkout real (Yape, PayPal capture, Mercado Pago)
- Media (ticket/voice), Telegram webhook
- MCP 43 tools individuales
- Journey Pro completo (`E2E_CLIENT_JOURNEY.md`)

## CI

Workflow: `.github/workflows/pam-nightly.yml`

| Job | Cuándo | Qué corre |
|-----|--------|-----------|
| `pam-tier1` | Diario 06:00 UTC | `public,landing,user` tier 1 — sin secretos |
| `pam-tier2` | Tras tier 1 | + `admin,post` tier 2 — `MARKET_API_TOKEN` en **Secrets** (o variable de repo) |

Destructive (`--include-destructive`) solo vía `workflow_dispatch` manual.

## Editar la matriz

1. Modificar `pam_matrix.yaml`
2. `python ops/production_acceptance.py --sync-json`
3. `--dry-run` para revisar
4. Correr contra prod y revisar `ops/reports/pam-*.json`