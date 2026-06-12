# PyPI package model — CLI Market

Documento canónico: qué paquete instala quién, qué versión muestra cada superficie, y cómo evitar drift entre deploy, landing y GTM.

## Marca vs paquetes

| Concepto | Nombre | Uso |
|--------|--------|-----|
| **Marca / producto** | CLI Market | Web, redes, pitch, `cli-market.dev` |
| **Paquete developer** | `cli-market-world` | CTA público: `pip install cli-market-world` |
| **Paquete intelligence SDK** | `cli-market-core` | Librería `market_core.*`; pin directo en backend/collector |
| **Legacy (congelado)** | `cli-market` | Cuenta PyPI antigua, frozen 1.9.5 |

**Regla GTM:** en marketing, docs públicos y onboarding siempre **`pip install cli-market-world`**. No cambiar el CTA a `cli-market-core` salvo documentación SDK-only.

## Quién depende de qué

```
Developer / agent builder
  pip install cli-market-world
    └── instala cli-market-core (transitivo)
    └── expone: market, market-server, market-mcp

Railway (cli-market-backend + collector)
  requirements.txt → cli-market-core>=X.Y.Z
    └── sin CLI ni landing; solo market_core

Mirror dev (cli-market-world)
  pyproject.toml → cli-market-core>=X.Y.Z + entrypoints locales
```

## Versiones visibles

| Superficie | Versión mostrada | Fuente |
|------------|------------------|--------|
| `market --version` | `PACKAGE_VERSION` de **core** | `market_core.market_stats` |
| PyPI `cli-market-world` | `pyproject.toml` version | Mismo número que core en release |
| PyPI `cli-market-core` | `pyproject.toml` + tag | Publicado primero |
| Landing / README | `MARKET_STATS.packageVersion` | `ops/sync_market_stats.py` |
| `landing/lib/marketStats.ts` | Auto-generado | No editar a mano |

Tras split PyPI, **core y world comparten número de release** (ej. 1.9.28) pero son artefactos distintos.

## Orden de release

1. **cli-market-core** — commit → tag `vX.Y.Z` → PyPI (workflow `publish-pypi.yml`)
2. Esperar ~2 min → `pip index versions cli-market-core`
3. **cli-market-backend** — pin `>=X.Y.Z`, CACHE_BUST Docker, push Railway
4. **cli-market-world** — pin core, bump version, tag → PyPI
5. **Dispersión** — ver `ops/RELEASE-DISPERSION.md`

## Downloads (Pepy / badges)

- URL primaria funnel: `pepy.tech/projects/cli-market-world`
- Badge consolidado en landing: legacy `cli-market` + `cli-market-core` + `cli-market-world` (ver `market_pepy.pepy_multi_summary`)

## MCP registry

- Identificador MCP: `io.github.Treevu-ai/cli-market-world` — **no cambiar** al renombrar paquetes internos.

## Footnote para copy (templates GTM)

> `cli-market-world` incluye el intelligence SDK (`cli-market-core`) automáticamente. Un solo `pip install` para CLI, API local y MCP.

## Anti-patterns

| ❌ No hacer | ✅ Hacer |
|------------|---------|
| Cambiar CTA global a `pip install cli-market-core` | Mantener `cli-market-world` en web/redes |
| Editar `marketStats.ts` a mano | `python ops/sync_market_stats.py` |
| Push backend antes de PyPI core | Verificar `pip index versions` primero |
| Mezclar versión world en pin de Railway | Backend pin solo `cli-market-core` |

## Referencias

- `ops/PYPI_RELEASE.md` — auth y workflows PyPI
- `ops/RELEASE-DISPERSION.md` — checklist post-release landing/GTM
- `AGENTS.md` — orden cross-repo
