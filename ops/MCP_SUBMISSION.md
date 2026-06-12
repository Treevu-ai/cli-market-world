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

Tag `v*` → workflow **Publish PyPI** publica a PyPI y luego al MCP Registry (`github-oidc`, sin secret extra).

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
