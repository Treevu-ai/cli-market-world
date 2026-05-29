---
title: Publicar LinkedIn — solo copiar y pegar
tags:
  - linkedin
  - gtm
---

# Publicar LinkedIn (30 días)

## Cada día

1. Abrí **`docs/linkedin/Day-NN.md`** (hoy = día de campaña desde `LINKEDIN_CAMPAIGN_START`).
2. Copiá la sección **Post (copiar a LinkedIn — sin link en cuerpo)** → pegá en LinkedIn.
3. Adjuntá **`docs/linkedin/assets/day-NN/day-NN-linkedin.png`**.
4. Publicá. En el **primer comentario**, pegá la sección **Primer comentario** del mismo archivo.
5. Marcá `published_at: YYYY-MM-DD` en el frontmatter del `Day-NN.md`.

## Días carousel (5 y 12)

Subí **todas** las imágenes `day-NN-slide-01.png` … en orden, en un solo post carousel.

## Regenerar imágenes (semanal o tras salto de métricas)

```bash
python3 ops/sync_linkedin_metrics.py
python3 ops/generate_all_linkedin_assets.py --patch
```

Índice visual: [[linkedin/assets/README]]

## Briefing automático

```bash
python3 ops/slack_cli.py briefing --dry-run
# → ops/daily/YYYY-MM-DD-content.md incluye post + ruta de imagen
```
