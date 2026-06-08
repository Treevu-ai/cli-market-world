# CLI Market — Deployment, Monitoring & Daily Ops Runbook

**Generado:** 2026-06-07 (actualizado 2026-06-08 — E2E pagos + pricing ecosistema)

**Pricing (sin canibalización):** `docs/pricing-strategy.md` — CLI Market Pro ($39 builders) · Procure ($29–149 operadores) · Intelligence ($300–500 datos).

## Verificación de Deployments

Todo lo crítico está arriba y respondiendo correctamente:

- Landing (Cloudflare Pages): 200 OK
- API principal (Railway): 200 OK
- Health checks: sanos
- Dashboard: cargando
- PyPI: accesible (versión actual 1.9.5)
- DB: conectada, con ~50k snapshots y todas las tablas esperadas

No vi caídas, errores 5xx ni datos vacíos. El collector parece funcionando (snapshots altos). El landing tiene el contenido actualizado de pricing simplificado.

## Enlaces, Puertos y Puntos de Monitoreo Continuo (Core)

### Producción (monitorea estos diariamente + alerts)
- **Landing principal**: https://cli-market.dev (página completa, hero, pricing, docs teaser)
- **Dashboard / funnel / adopción / KPIs**: https://cli-market-production.up.railway.app/dashboard
- **API raíz + health**:
  - https://cli-market-production.up.railway.app
  - https://cli-market-production.up.railway.app/health → `{"status": "healthy"}`
  - https://cli-market-production.up.railway.app/health/db → (detalle: backend postgresql, snapshots, tablas, pg_error)
- **Docs + Tools (MCP catalog)**: https://cli-market.dev/docs y https://cli-market.dev/tools
- **PyPI (versión, descargas, descripción)**: https://pypi.org/project/cli-market
- **Railway (servicios)**: Dashboard de Railway → servicio `cli-market-production` (API) + servicio collector separado (usa `railway.collector.toml`)
- **Cloudflare Pages (landing)**: Dashboard Cloudflare → proyecto `cli-market-world`
- **GitHub (deploys, CI, issues)**: https://github.com/Treevu-ai/cli-market-world (y el repo de content)
- **MCP / agent entrypoints**: `market-mcp` (instalado vía pip), configurado vía `mcp.json`, smithery.yaml, glama.json
- **Go-live / 3 KPIs + alerts** (interno): ejecuta `python market_golive.py` (o usa el /dashboard)
- **Slack bitácora / publicaciones** (notificaciones de collector, deploys, daily): canales configurados vía `SLACK_*` envs (ver ops/daily_briefing.py)
- **Métricas de contenido / price-pulse**: `content/metrics/price-pulse-*.md` + reportes generados en `ops/daily/` o `content/generated/daily/`
- **Procure Copilot (landing + checkout)**: https://procure-copilot.contacto-8e4.workers.dev/procure

### Local / dev (para debugging)
- Puerto principal del server: **8765** (`python market_server.py` o uvicorn)
- Puerto de tests/e2e: **8767** (en e2e_test.py)
- Health local: `http://127.0.0.1:8765/health` y `/health/db`

### Otros que vale tener en bookmarks/alerts
- Railway logs + metrics del servicio API y collector
- Cloudflare Pages deploys + analytics del proyecto landing
- PyPI stats (descargas semanales)
- GitHub Actions (smoke tests, releases)

## Lista de Comandos Diarios (orden recomendados + justificación)

Basado en `content/Makefile`, `ops/daily_briefing.py`, `AGENTS.md`, `market_golive.py`, `collect_prices.py`, `PYPI_RELEASE.md` y flujos de GTM + ops:

1. **python ops/daily_briefing.py** (o `--product` / `--content` / `--dry-run`)  
   Genera los dos reportes diarios (product KPIs + content calendar + gates). Incluye Slack si está configurado. **Primero del día** — te da el estado del moat, collector y qué publicar.

2. **make today** (o `python scripts/status.py`)  
   Dashboard inmediato: qué toca publicar hoy en todos los canales (LinkedIn personal/empresa, HN, Reddit, DEV, etc.).

3. **make gate** (local) + **make gate-remote** (vs API live)  
   Verifica data-gate (cobertura ≥80%). Crítico antes de posts data-gated. El remote usa la Railway real.

4. **make content** (o `python scripts/content.py`)  
   Copia lista para pegar en todos los canales activos del día.

5. **make brief** (o `python scripts/briefing.py`)  
   Briefing detallado de LinkedIn (personal + empresa) con hooks y CTAs.

6. **python collect_prices.py --report** (o `--status`)  
   KPIs del collector (precios por línea, tiendas frescas, health). Parte del daily briefing pero ejecútalo explícitamente si quieres ver crudo.

7. **python ops/payments_e2e.py**  
   E2E de rieles de pago — **retail/logístico** (carrito CLI Market Pro) y **Procure** (run → approve → checkout). Valida PayPal, Mercado Pago, Yape y Plin sin cobro real (solo forma de respuesta: `qr_url`, `approve_url`, `checkout_url`).  
   ```bash
   cd cli-market-world
   python ops/payments_e2e.py
   ```
   Env opcional:
   - `MARKET_API_URL` — API Railway (default prod)
   - `MARKET_API_TOKEN` — admin; gates free→403 y billing legacy
   - `MARKET_PRO_API_KEY` — `sk-…` Pro para checkout retail (si falta, intenta `../Projects/procure-copilot/.env.local` → `CLI_MARKET_API_KEY`)
   - `PROCURE_PUBLIC_URL` — Worker Procure (default prod)  
   **Exit 0** = PASS en retail + procure. SKIP esperado si `/billing/pro-checkout` o `/v1/admin/set-tier` no están desplegados en Railway.  
   Solo Procure (mismo cuatro canales):
   ```bash
   cd ../Projects/procure-copilot
   npm run payments:e2e
   ```

8. **python market_golive.py** (o `ops/go_live_check.py`)  
   Las 3 north-star KPIs + founder alerts:
   - `SEARCH_PER_REGISTER_TARGET = 0.40`
   - `COVERAGE_7D_TARGET = 80.0`
   - `WEEKLY_ACTIVATED_GOAL = 1`
   + alerts accionables (stores críticas, collector stale, etc.). **Imprescindible para founder ops**.

9. **make fresh** (`python scripts/check-freshness.py`)  
   Diagnóstico de frescura del moat (cuánto tiempo desde último snapshot por retailer).

10. **make publish day=N** (`python scripts/mark-published.py --day N`)  
   Marca el día de campaña como publicado (actualiza calendario y evita repeticiones).

**Flujos semanales / spike (cuando aplique):**
- `make week2`, `make week2-copy`, `make week2-bundle` (monetización activa).
- `make spike` + `make spike-copy` (D-Day HN/DEV/Reddit/Twitter).

**Después de cambios de código (CLI / landing):**
- Landing (si tocaste UI): `$env:CLOUDFLARE_API_TOKEN=... ; .\ops\deploy_landing.ps1`
- CLI package (si tocaste `market_cli.py` / `market_ui.py`): sigue `PYPI_RELEASE.md` (bump versión, `python -m build`, `twine upload`, sync README vía patch script). PyPI actual está en 1.9.5 — tus últimos cambios de JSON estandarizado están en el repo pero **aún no en PyPI** (hay que publicar).

## Qué Entendí del Contexto

Estás operando un sistema multi-repo (content para GTM + world para producto/landing/CLI/server). El foco es **agent-native commerce infra** (pip + MCP + 43 tools + data moat real). Hay dos flujos paralelos que mantener vivos:
- **GTM/content** (calendario, posts, gates de datos, monetización semana 2, spikes).
- **Producto/ops** (collector, API Railway, landing Cloudflare, KPIs go-live, daily briefings, deploys manuales).

Todo debe ser monitoreable por founder (tú) con un set pequeño de enlaces + comandos diarios que cierren el loop de "data moat fresco + contenido publicable + revenue gates + alerts".

Si los tests de flujo que corrimos antes (JSON en hello/init/tools/etc.) y los pings live de ahora están bien, el sistema está "deployado" en el sentido operativo. El CLI en PyPI todavía necesita un release manual para que los usuarios vean los últimos cambios.
