# CLI Market — MCP Registry

Canonical server: **`io.github.Treevu-ai/cli-market-world`** · PyPI **`cli-market-world`** · vía `server.json` en repo root.

## Publish (manual)

```bash
# From cli-market-world repo root (after PyPI release)
mcp-publisher validate
mcp-publisher login github          # device flow, or: login github --token "$GITHUB_TOKEN"
mcp-publisher publish
```

## Publish (CI)

Tag `v*` → workflow **Publish PyPI** publica a PyPI y luego al MCP Registry (`github-oidc`, sin secret extra). El job MCP espera hasta 6 min a que PyPI propague el paquete antes de publicar.

## Re-publish (MCP only)

Si PyPI OK pero MCP falló con `PyPI package 'cli-market-world' not found (status: 404)`:

1. **GitHub Actions** → **Publish MCP Registry** → Run workflow (version = la ya publicada en PyPI, ej. `1.9.36`)
2. O manual local (después de confirmar `curl -fsSL https://pypi.org/pypi/cli-market-world/VERSION/json`):

```bash
# Sync version in server.json first, then:
mcp-publisher validate
mcp-publisher login github
mcp-publisher publish
```

## Deprecate legacy entry

La entrada **`io.github.Treevu-ai/cli-market`** (PyPI `cli-market` congelado) debe quedar deprecated:

```bash
mcp-publisher login github
bash ops/deprecate_legacy_mcp_registry.sh
```

## Manifest rules

| Campo | Valor |
|-------|--------|
| `name` | `io.github.Treevu-ai/cli-market-world` |
| `packages[0].identifier` | `cli-market-world` |
| `repository.url` | `https://github.com/Treevu-ai/cli-market-world` |
| `repository.source` | `github` |
| PyPI README | línea `mcp-name: io.github.Treevu-ai/cli-market-world` |

`ops/sync_market_stats.py` mantiene `server.json` + `landing/public/server.json` en cada release.

## After publishing

Searchable at [registry.modelcontextprotocol.io](https://registry.modelcontextprotocol.io) · keywords: commerce, shopping, prices, retail.
