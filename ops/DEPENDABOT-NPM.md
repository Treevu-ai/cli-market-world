# Dependabot npm (landing)

## Error `private_registry_config_not_found` / `npm.pkg.github.com`

Org-level npm may point scopes at GitHub Packages. This repo overrides to **public npm only**:

- `landing/.npmrc` — `registry=https://registry.npmjs.org/`
- `.github/dependabot.yml` — `npmjs` registry with `replaces-base: true`

No Dependabot secrets required for landing updates.

## If you add private `@Treevu-ai/*` npm deps later

1. Grant repo read access on the package (Manage Actions access).
2. Add Dependabot secret `GH_PAT` (PAT with `read:packages` + repo admin for secrets API).
3. Restore `github-npm` registry block in `.github/dependabot.yml`.

## Verify

```bash
cd landing && npm audit && npm run build
```
