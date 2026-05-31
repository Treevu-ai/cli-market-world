# PyPI release — cli-market

## Current target

- Package: `cli-market`
- Version: see `pyproject.toml` / `market_stats.py` (`PACKAGE_VERSION`)
- Tag: `git tag vX.Y.Z && git push origin vX.Y.Z`

## Option A — GitHub Actions (recommended)

1. Configure [PyPI trusted publishing](https://docs.pypi.org/trusted-publishers/) for:
   - Owner: `Treevu-ai`
   - Repo: `cli-market-world`
   - Workflow: `publish-pypi.yml`
   - Environment: `pypi`
2. Create GitHub environment **`pypi`** (Settings → Environments).
3. Push tag `v*` or run workflow **Publish PyPI** manually.

## Option B — Local upload

### Windows (PowerShell)

```powershell
cd C:\Users\acuba\Projects\cli-market-world
py -3 -m pip install -U build twine
Remove-Item -Recurse -Force dist, build, cli_market.egg-info -ErrorAction SilentlyContinue
py -3 ops/sync_market_stats.py
py -3 -m build
py -3 -m twine check dist/cli_market-1.6.1*
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = "pypi-***"
py -3 -m twine upload --verbose dist/cli_market-1.6.1*
```

### WSL / Git Bash / Linux

```bash
cd /mnt/c/Users/acuba/Projects/cli-market-world
python3 -m pip install -U build twine
rm -rf dist build *.egg-info
python3 ops/sync_market_stats.py
python3 -m build
python3 -m twine check dist/cli_market-1.6.1*
export TWINE_USERNAME='__token__'
export TWINE_PASSWORD='pypi-***'
python3 -m twine upload --verbose dist/cli_market-1.6.1*
```

**Auth:** with an API token, username must be literally `__token__` (not your PyPI account name).

## Troubleshooting 400 Bad Request

| Cause | Fix |
|-------|-----|
| Re-uploading an existing version | Remove old wheels from `dist/` or upload `dist/cli_market-X.Y.Z*` only |
| Generic error, no detail | Re-run with `--verbose` |
| Summary too long / multiline | Keep `description` in `pyproject.toml` under 512 chars, single line |
| Stale build cache | `rm -rf dist build *.egg-info` then rebuild |

## Verify

```bash
pip index versions cli-market
pip install -U cli-market
market hello
python -c "import market_stats; print(market_stats.PACKAGE_VERSION)"
```

Also sync `server.json` + `landing/public/server.json` version with `pyproject.toml` (`python ops/sync_market_stats.py`).
