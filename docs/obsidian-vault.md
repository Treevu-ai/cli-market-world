---
title: Obsidian Vault — CLI Market
tags:
  - obsidian
  - gtm
---

# Obsidian Vault Setup

**Vault root:** `/home/acuba/Proyectos/nuevo` (WSL: `\\wsl.localhost\Ubuntu\home\acuba\Proyectos\nuevo`)

## Config shipped

| File | Purpose |
|------|---------|
| `.obsidian/app.json` | Editor defaults, new files → `docs/linkedin/` |
| `.obsidian/core-plugins.json` | Daily notes, templates, graph |
| `.obsidian/templates.json` | Template folder → `docs/Templates/` |
| `.obsidian/graph.json` | Graph colors for GTM tags |
| `.obsidian/workspace.json` | Default layout: GTM-Hub pinned |

## Recommended folders to collapse

- `landing/.next/`, `landing/out/`
- `node_modules/`, `__pycache__/`
- `.cursor/rules/` (184 agency agents)

## Entry points

1. [[GTM-Hub]] — MOC principal
2. [[linkedin/00-Index]] — calendario 30d
3. [[cli-market-prd-v2]] — north star producto
4. [[metrics/README]] — KPIs semanales

## Frontmatter convention

Todos los docs GTM usan:

```yaml
---
title: ...
tags: [gtm, ...]
hub: "[[GTM-Hub]]"
---
```

LinkedIn days: `status: ready | idea`, `pillar`, `lang`, `day`.

[[GTM-Hub]]
