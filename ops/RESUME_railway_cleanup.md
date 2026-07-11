# Resume: limpieza Railway → Fly.io/Cloudflare

**Estado:** Nada commiteado todavía en ninguno de los 3 repos. Todo el trabajo está en el
working tree (`git status --short` en cada repo para ver el detalle completo).

## Repos tocados

| Repo | Estado |
|---|---|
| `procure-copilot` | ✅ Completo — 0 referencias a Railway/vestigios restantes |
| `cli-market-world` | ✅ Completo (2 rondas) — solo quedan docs históricas fechadas (changelogs, PRDs con `[x]`, posts de LinkedIn ya publicados) |
| `cli-market-backend` | ✅ Completo — solo queda `ops/FLY-MIGRATION.md` (runbook histórico de la migración, correcto que mencione Railway) |
| `cli-market-core` | Sin cambios — solo tenía menciones cosméticas de alias de nombres, no vestigios reales |

## Qué se hizo (resumen)

- Borrados: `railway.toml`, `railway.collector.toml`, `deploy-railway.yml`, `requirements-railway.txt`
  (renombrado a `requirements.txt` en world), y ~10 scripts `ops/*railway*` ya muertos.
- Convertidos a Fly.io: fallbacks de URL hardcodeados en ~20 scripts Python/TS, `market_security.py`
  (detección de prod), `routers/checkout/routes.py` + `routers/mercadopago.py` (env flags),
  `ops/contract_parity.py` (pin de versión), `ops/reset_store_health.py`, hotpatch SSH
  (`railway ssh` → `fly ssh console`), y ~16 scripts que seteaban secrets vía `railway variables --set`
  → `fly secrets set --app cli-market-api`.
- Página legal de privacidad (`landing/app/legal/privacy/page.tsx`, ES+EN) corregida — decía
  "Railway" como proveedor de infra en una página pública real.
- Docs operativos y CI actualizados en los 3 repos (READMEs, AGENTS.md, runbooks de ops, workflows).
- Dejado intacto a propósito: changelogs, PRDs con checklists `[x]` ya cerrados, scripts de release
  fechados, reportes generados, posts de LinkedIn ya publicados, y `ops/FLY-MIGRATION.md` (backend) —
  son registro histórico, no vestigios.

## 🔴 Pendientes que requieren tu acción (no resueltos por mí)

1. **Credencial expuesta**: `ops/_check_db.py` (world, ya borrado) tenía una contraseña de Postgres
   de Railway en texto plano, commiteada en el historial de git. **Rotar esa contraseña** si se
   reutilizó en algo (incluida la DB de Fly).

2. **Confirmar arquitectura real de deploy**: verifiqué con `fly status` + `openapi.json` en vivo que
   `cli-market-api.fly.dev` corre el código de **`cli-market-world`** (no el de `cli-market-backend`,
   pese a que backend tiene su propio `fly.toml`/`fly.collector.toml` con el mismo nombre de app).
   No quedó claro si el `fly.toml` de backend sigue en uso para algo o es remanente de un plan de
   migración que terminó ejecutándose desde world en su lugar. Ver nota en `AGENTS.md` (world),
   sección "Deploy prod — Fly.io".

3. **Secret nuevo requerido**: `.github/workflows/ops-check-pro-request.yml` (world) ahora necesita
   un secret `DATABASE_URL` en GitHub — antes lo sacaba dinámicamente vía `railway variables --json`
   con `RAILWAY_TOKEN`, y Fly no permite leer secrets de vuelta por CLI (a diferencia de Railway),
   así que no hay forma mecánica de replicar ese paso. **Crear el secret en GitHub antes de que este
   workflow se dispare.**

## Cómo retomar

```bash
# Revisar el diff completo antes de commitear, repo por repo:
cd procure-copilot && git status --short && git diff
cd cli-market-world && git status --short && git diff
cd cli-market-backend && git status --short && git diff
```

No se ha pedido commit todavía — cuando confirmes que el diff se ve bien, avisame y armo los
commits (probablemente uno por repo, mensaje tipo `chore: retire Railway, migrate to Fly.io`).

Después de commitear, atacar los 3 pendientes de arriba, en ese orden de prioridad
(credencial expuesta > confirmar arquitectura > secret de GitHub).
