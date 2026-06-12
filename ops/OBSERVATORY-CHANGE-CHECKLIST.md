# Observatory Change Checklist — 4 repos

Cada entrega de Observatory (P0) debe dejar **verde** esta lista antes de considerar el release cerrado.

PRD: `docs/prd-observatory-p0.md` §0 · Criterios §13 actualizados 2026-06-12

---

## Orden de ejecución

**Prod actual:** Railway despliega desde **cli-market-world** (`Dockerfile` + `requirements-railway.txt`). Mirror backend = paridad documentada; prod = world.

```
cli-market-world  →  Railway (mirror-first: telemetría P0 aquí) ✅
cli-market-core   →  PyPI 1.9.34 ✅
cli-market-index  →  (sin cambio P0) ✅
```

---

## 1. cli-market-core (primero)

- [x] Nuevo paquete/módulo `market_observatory/` (o `market_core/market_observatory.py`)
  - [x] `ensure_observatory_schema()` — DDL `agent_events`, `agents`, `daily_observatory_metrics`
  - [x] `resolve_agent_id(request, auth)` — prioridad `X-Agent-ID` → API key → username → session → fingerprint
  - [x] `record_agent_event(...)` — fail-open, metadata allowlist
  - [x] Re-export noise filter (`is_noise_username` o equivalente)
- [x] `market_core/market_mcp_registry.py` — lista canónica de `tool_name` instrumentados
- [x] `market_core/market_stats.py` — `PACKAGE_VERSION` bump
- [x] `pyproject.toml` — `version` bump + `packages` si aplica
- [x] `tests/test_observatory_core.py` — identity + schema
- [x] CI verde
- [x] Tag + publish PyPI `cli-market-core`

**Versión anotar aquí:** `core 1.9.34`

---

## 2. cli-market-backend (producción / paridad)

> Prod corre en world; backend repo mantiene paridad y pin de dependencias.

- [x] `requirements.txt` — `cli-market-core>=1.9.34` (sync workflow 2026-06-12)
- [x] `market_observatory.py` — thin shim: import desde `cli-market-core`
- [x] `market_server.py` — `ObservatoryMiddleware` (fail-open, async batch)
- [x] `routers/observatory.py` — `/analytics/observatory`, `/dashboard/observatory`
- [x] `routers/__init__.py` / `market_server.py` — registrar router
- [x] Lifespan startup — `ensure_observatory_schema()`
- [x] `server_deps.py` — solo si cambia extracción auth para agent_id
- [x] `tests/test_observatory.py` — integration contra DB aislada
- [ ] CI verde (`pytest`) — no verificado en este workspace
- [x] Railway deploy prod — world deploy 2026-06-12
- [x] Smoke: `curl $API/analytics/observatory` responde 200 — MAA=30 prod

---

## 3. cli-market-world (mirror + ops + landing)

### 3a. Paridad API (mirror backend)

Diff cero en paths relativos (verificar con checkout local de backend):

- [x] `market_observatory.py`
- [x] `market_server.py` (middleware)
- [x] `routers/observatory.py`
- [x] `server_deps.py` (si cambió en backend)
- [ ] Diff `fc` backend ↔ world — pendiente checkout local

### 3b. Dependencias PyPI

- [x] `pyproject.toml` — `version` bump → **1.9.34**
- [x] `pyproject.toml` — `cli-market-core>=1.9.34`
- [x] `[tool.setuptools] py-modules` — incluir `market_observatory` si es shim local

### 3c. Ops y Adoption Index (solo world)

- [x] `market_adoption_index.py` — `real_usage` desde MAA (`agent_events`)
- [x] `ops/observatory_daily.py` — job agregación diaria
- [x] `.github/workflows/observatory-nightly.yml` — schedule (también en `morning-ops-chain`)
- [x] `ops/command_control_daily.py` — bloque MAA / mcp_retention_7d
- [x] `ops/adoption_index.py` — sin regresión

### 3d. Landing

- [x] `landing/app/stats/page.tsx` — consume `/analytics/observatory`
- [x] `landing/app/legal/privacy/page.tsx` — telemetría agregada MCP (2026-06-12)
- [x] `ops/sync_market_stats.py` — ejecutado 2026-06-12 (PyPI 27k, linkage 84.4%, v1.9.34)

### 3e. Release

- [x] Tests `tests/test_observatory*.py` verdes
- [x] `CHANGELOG.md` — entrada world + core
- [x] Tag `v*` → workflow Publish PyPI → **1.9.34**

**Versión anotar aquí:** `world 1.9.34`

---

## 4. cli-market-index

- [x] Sin cambios de código P0
- [ ] (Opcional) README ecosystem — una línea si se documenta que index no participa en telemetry

---

## 5. Post-release verificación

- [ ] `python ops/observatory_daily.py --dry-run` — agregados coherentes (requiere `DATABASE_URL`)
- [x] `python ops/adoption_index.py` — `agent_usage_proxy` reemplazado por MAA cuando telemetry madura
- [x] `python ops/command_control_daily.py --remote` — MAA visible
- [ ] Adoption Index nightly CI — verde 7 días consecutivos post-deploy (validar 2026-06-19)
- [x] Streak monitor — `GET /admin/observatory/streak` + `ops/observatory_streak.py --remote`
- [x] `GET /analytics/observatory?days=30` prod — 7 preguntas del PRD §1
- [ ] Landing `/stats` — data-gate OK (`make gate` en content repo si cifra en creative)
- [x] PAM — casos `public.observatory`, `admin.observatory_*` en `ops/pam_matrix.yaml`

---

## 6. Versiones alineadas (release 2026-06-12)

| Artefacto | Versión |
|-----------|---------|
| cli-market-core PyPI | **1.9.34** |
| cli-market-world PyPI | **1.9.34** |
| Railway prod (world deploy) | OpenAPI **1.9.34** · deploy verde 2026-06-12 |
| cli-market-backend pin | **1.9.34** — sync workflow 2026-06-12 (`GH_PAT_BACKEND_WRITE`) |
| cli-market-index pin (sin cambio) | `9d050131e9e5b16381581d1916e386f34d319ca6` |

---

## Anti-patrones (no hacer)

- Implementar solo en world y olvidar backend (prod no registra eventos)
- Bump world sin publicar core primero (import falla en CI/PyPI)
- Duplicar lógica de identidad en world y backend (debe vivir en core)
- Crear `daily_metrics` paralelo a `daily_observatory_metrics` + `adoption_index_snapshots`
- Publicar MAA en landing sin data-gate
