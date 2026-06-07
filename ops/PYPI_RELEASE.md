# PyPI release — cli-market-world + cli-market-core

## Packages (new PyPI account)

| Package | Repo | Install |
|---------|------|---------|
| `cli-market-core` | `cli-market-core` | `pip install cli-market-core` |
| `cli-market-world` | `cli-market-world` | `pip install cli-market-world` |

Legacy `cli-market` on the old account (`Ricardo_Cuba`) is frozen at 1.9.5.

## Auth

1. Create a **new** PyPI account (verified email).
2. API token scope: **Entire account** (required for first upload of each project).
3. Store in both repos:

```powershell
gh secret set PYPI_API_TOKEN -R Treevu-ai/cli-market-core
gh secret set PYPI_API_TOKEN -R Treevu-ai/cli-market-world
```

Or configure [Trusted Publishers](https://docs.pypi.org/trusted-publishers/) per repo (`publish-pypi.yml`, environment `pypi`).

## Publish order

1. **core** first: `gh workflow run publish-pypi.yml -R Treevu-ai/cli-market-core --ref main`
2. Verify: `pip index versions cli-market-core`
3. **world**: `gh workflow run publish-pypi.yml -R Treevu-ai/cli-market-world --ref main`
4. Verify: `pip install cli-market-world==1.9.5 && market hello`

## Version

- See `pyproject.toml` in each repo (`1.9.5` target).
- Tag optional: `git tag vX.Y.Z && git push origin vX.Y.Z` (workflow also supports `workflow_dispatch` on `main`).

## Verify

```bash
pip index versions cli-market-core
pip index versions cli-market-world
pip install -U cli-market-world
market hello
python -c "import market_stats; print(market_stats.PACKAGE_VERSION)"
```