# Release dispersion checklist

Ejecutar después de cada release PyPI (core + world + backend pin). Evita drift entre prod, landing, assets y GTM.

## Pre-flight

- [x] `pip index versions cli-market-core` → **1.9.36** (2026-06-13)
- [x] `pip index versions cli-market-world` → **1.9.36**
- [x] Railway `/health` → 200

## Automático (world repo)

> **CI:** El job `release-dispersion` en `publish-pypi.yml` ejecuta los pasos 1 y 4 automáticamente después de cada release (tag `v*`). Solo los pasos 2–3 requieren intervención manual.

```bash
cd cli-market-world

# 1. Stats → landing, README, OG, MCP manifests, content templates  ← CI lo hace
python ops/sync_market_stats.py

# 2. GIFs terminalizer (si cambió versión visible o métricas en hero)  ← manual
python ops/generate_demo_gif.py
python ops/generate_usecase_gifs.py

# 3. README heroes multi-repo (releases mayores)  ← manual, opcional
python ops/sync_readme_heroes.py

# 4. Commit + push → Cloudflare landing deploy  ← CI lo hace
git add landing/ README.md pyproject.toml server.json mcp.json docs/
git commit -m "chore(stats): sync landing and assets after X.Y.Z"
git push origin main
```

## Verificar en landing

- [ ] `MARKET_STATS.packageVersion` = versión PyPI
- [ ] `indicatorsCount` alineado con `INDICATOR_DEFINITIONS` en core
- [ ] Hero / docs / checkout usan `MARKET_STATS.pipInstallCmd` (no hardcoded)
- [ ] `demo.gif` y `use-cases/*.gif` muestran versión actual en frame de install

## GTM (rolling, no big-bang)

- [ ] Templates en `cli-market-content/templates/` — footnote dual-package si aplica
- [ ] Posts **nuevos** salen de `make content` (sync ya parchea templates world)
- [ ] Posts **publicados** — no reescribir; solo pinned/top si crítico
- [ ] `strategy/GTM-Hub.md` pitch intacto: `pip install cli-market-world`

## Backend / ops

- [ ] `requirements.txt` pin `cli-market-core>=X.Y.Z`
- [ ] **Auto-PR:** Actions → `Sync backend core pin` (secret `GH_PAT_BACKEND_WRITE` con Contents write en `cli-market-backend`; `GH_PAT` solo lectura no alcanza)
- [ ] **Fallback manual:** artifact `backend-core-pin-X.Y.Z` del workflow run
- [ ] `CACHE_BUST` en Dockerfiles si hubo race PyPI
- [ ] `contract_parity.py` OK en CI world

## Documentación

- [ ] `docs/PYPI-PACKAGE-MODEL.md` — referencia canónica (sin cambio por release menor)
- [ ] `CHANGELOG.md` — entrada con core + world + indicadores nuevos si aplica

## Timing (lección 1.9.27)

Railway build puede fallar si backend push corre **antes** de que PyPI propague `cli-market-core`. Esperar 2–3 min o verificar con `pip index versions` antes de push backend.
