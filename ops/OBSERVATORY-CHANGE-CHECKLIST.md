# Observatory Change Checklist — 4 repos

Cada entrega de Observatory (P0) debe dejar **verde** esta lista antes de considerar el release cerrado.

PRD: `docs/prd-observatory-p0.md` §0

---

## Orden de ejecución

```
cli-market-core  →  PyPI
cli-market-backend  →  Railway
cli-market-world  →  PyPI tag + landing
cli-market-index  →  (sin cambio P0)
```

---

## 1. cli-market-core (primero)

- [ ] Nuevo paquete/módulo `market_observatory/` (o `market_core/market_observatory.py`)
  - [ ] `ensure_observatory_schema()` — DDL `agent_events`, `agents`, `daily_observatory_metrics`
  - [ ] `resolve_agent_id(request, auth)` — prioridad `X-Agent-ID` → API key → username → session → fingerprint
  - [ ] `record_agent_event(...)` — fail-open, metadata allowlist
  - [ ] Re-export noise filter (`is_noise_username` o equivalente)
- [ ] `market_core/market_mcp_registry.py` — lista canónica de `tool_name` instrumentados
- [ ] `market_core/market_stats.py` — `PACKAGE_VERSION` bump
- [ ] `pyproject.toml` — `version` bump + `packages` si aplica
- [ ] `tests/test_observatory_core.py` — identity + schema
- [ ] CI verde
- [ ] Tag + publish PyPI `cli-market-core`

**Versión anotar aquí:** `core ___.___.___`

---

## 2. cli-market-backend (producción)

- [ ] `requirements.txt` — `cli-market-core>=<versión publicada>`
- [ ] `market_observatory.py` — thin shim: import desde `cli-market-core`
- [ ] `market_server.py` — `ObservatoryMiddleware` (fail-open, async batch)
- [ ] `routers/observatory.py` — `/analytics/observatory`, `/dashboard/observatory`
- [ ] `routers/__init__.py` / `market_server.py` — registrar router
- [ ] Lifespan startup — `ensure_observatory_schema()`
- [ ] `server_deps.py` — solo si cambia extracción auth para agent_id
- [ ] `tests/test_observatory.py` — integration contra DB aislada
- [ ] CI verde (`pytest`)
- [ ] Railway deploy prod
- [ ] Smoke: `curl $API/analytics/observatory` responde 200

---

## 3. cli-market-world (mirror + ops + landing)

### 3a. Paridad API (mirror backend)

Diff cero en paths relativos:

- [ ] `market_observatory.py`
- [ ] `market_server.py` (middleware)
- [ ] `routers/observatory.py`
- [ ] `server_deps.py` (si cambió en backend)

```powershell
# Verificación rápida (ajustar rutas locales)
fc ..\cli-market-backend\market_observatory.py .\market_observatory.py
fc ..\cli-market-backend\routers\observatory.py .\routers\observatory.py
```

### 3b. Dependencias PyPI

- [ ] `pyproject.toml` — `version` bump
- [ ] `pyproject.toml` — `cli-market-core>=<versión publicada>`
- [ ] `[tool.setuptools] py-modules` — incluir `market_observatory` si es shim local

### 3c. Ops y Adoption Index (solo world)

- [ ] `market_adoption_index.py` — `real_usage` desde MAA (`agent_events`)
- [ ] `ops/observatory_daily.py` — job agregación diaria
- [ ] `.github/workflows/observatory-nightly.yml` — schedule
- [ ] `ops/command_control_daily.py` — bloque MAA / mcp_retention_7d
- [ ] `ops/adoption_index.py` — sin regresión

### 3d. Landing

- [ ] `landing/app/stats/page.tsx` — consume `/analytics/observatory`
- [ ] `landing/app/legal/privacy/page.tsx` — telemetría agregada (si aplica)
- [ ] `ops/sync_market_stats.py` — solo si `/stats` expone cifras en `MARKET_STATS`

### 3e. Release

- [ ] Tests `tests/test_observatory*.py` verdes
- [ ] `CHANGELOG.md` — entrada world + core
- [ ] Tag `v*` → workflow Publish PyPI

**Versión anotar aquí:** `world ___.___.___`

---

## 4. cli-market-index

- [ ] Sin cambios de código P0
- [ ] (Opcional) README ecosystem — una línea si se documenta que index no participa en telemetry

---

## 5. Post-release verificación

- [ ] `python ops/observatory_daily.py --dry-run` — agregados coherentes
- [ ] `python ops/adoption_index.py` — `agent_usage_proxy` reemplazado por MAA
- [ ] `python ops/command_control_daily.py --remote` — MAA visible
- [ ] Adoption Index nightly CI — verde 24h post-deploy
- [ ] `GET /analytics/observatory?days=30` prod — 7 preguntas del PRD §1
- [ ] Landing `/stats` — data-gate OK (`make gate` en content repo si cifra en creative)

---

## 6. Versiones alineadas (plantilla release)

| Artefacto | Versión |
|-----------|---------|
| cli-market-core PyPI | |
| cli-market-world PyPI | |
| cli-market-backend deploy SHA | |
| cli-market-index pin (sin cambio) | `2bfa6d2…` |

---

## Anti-patrones (no hacer)

- Implementar solo en world y olvidar backend (prod no registra eventos)
- Bump world sin publicar core primero (import falla en CI/PyPI)
- Duplicar lógica de identidad en world y backend (debe vivir en core)
- Crear `daily_metrics` paralelo a `daily_observatory_metrics` + `adoption_index_snapshots`
- Publicar MAA en landing sin data-gate
