# PyPI release — cli-market

## Current target

- Package: `cli-market`
- Version: see `pyproject.toml`
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

```bash
python3 -m venv .venv && .venv/bin/pip install build twine
rm -rf dist && .venv/bin/python -m build
TWINE_USERNAME=__token__ TWINE_PASSWORD=pypi-*** .venv/bin/twine upload dist/*
```

## Verify

```bash
pip index versions cli-market
pip install -U cli-market
market hello
```

Also sync `server.json` + `landing/public/server.json` version with `pyproject.toml`.
