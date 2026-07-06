# PyPI release — cli-market-world + cli-market-core

> Modelo canónico (marca vs paquetes, CTA GTM, versiones visibles): **`docs/PYPI-PACKAGE-MODEL.md`**  
> Post-release landing/GTM/assets: **`ops/RELEASE-DISPERSION.md`**

## Packages

| Package | Repo | Quién instala | Install |
|---------|------|---------------|---------|
| `cli-market-core` | `cli-market-core` | Backend Fly.io, SDK-only | `pip install cli-market-core` |
| `cli-market-world` | `cli-market-world` | Developers, GTM CTA | `pip install cli-market-world` |

`cli-market-world` depende de `cli-market-core` en PyPI. **CTA público siempre world.**

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
4. Verify: `pip install cli-market-world==X.Y.Z && market hello`
5. Dispersion: `python ops/sync_market_stats.py` (+ GIFs si aplica) — ver `RELEASE-DISPERSION.md`

## Version

- Mismo número en core y world (`pyproject.toml` en cada repo).
- Tag: `git tag vX.Y.Z && git push origin vX.Y.Z` (dispara `publish-pypi.yml` en push tag).

## Verify

```bash
pip index versions cli-market-core
pip index versions cli-market-world
pip install -U cli-market-world
market hello
python -c "import market_stats; print(market_stats.PACKAGE_VERSION)"
```