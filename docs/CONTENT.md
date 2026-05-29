# Contenido GTM / LinkedIn

Posts, imágenes y estrategia de marketing **no viven en este repo**.

## Repo privado

**`cli-market-content`** (plantilla en `tools/content-repo-template/`).

## Setup local

```bash
python3 ops/init_content_repo.py --target ../cli-market-content
export CLI_MARKET_CONTENT_DIR=../cli-market-content
python3 ops/generate_all_linkedin_assets.py --patch
```

Publicar: `../cli-market-content/linkedin/PUBLISH.md`
