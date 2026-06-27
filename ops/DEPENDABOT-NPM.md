# Dependabot npm (landing)

## Error `private_registry_config_not_found` / `npm.pkg.github.com`

Org-level npm config may point `@Treevu-ai` scopes at GitHub Packages. Dependabot needs matching registry auth in `.github/dependabot.yml`.

This repo uses:

- `landing/.npmrc` — public npm for install/build
- `.github/dependabot.yml` — `npmjs` + `github-npm` registries
- Dependabot secret **`GH_PAT`** — same PAT as Actions `GH_PAT` (`read:packages` minimum)

## One-time / after PAT rotation

1. Ensure **Actions** secret `GH_PAT` exists (already used by CI checkout).
2. Run workflow **Sync Dependabot secrets** (Actions → Sync Dependabot secrets → Run workflow).
3. Re-run failed Dependabot job or wait for next weekly schedule.

## Verify locally

```bash
cd landing && npm audit && npm run build
npm run qa:spoke
```
