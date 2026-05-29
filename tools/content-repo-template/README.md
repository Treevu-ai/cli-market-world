# cli-market-content (plantilla)

Copia inicial para el **repo privado de contenido** GTM / LinkedIn de CLI Market.

El repo de producto (`cli-market-world`) no incluye posts ni imágenes; solo esta plantilla y los scripts generadores.

## Crear tu repo local

Desde la raíz de `cli-market-world`:

```bash
python3 ops/init_content_repo.py --target ../cli-market-content
export CLI_MARKET_CONTENT_DIR=../cli-market-content
pip install pillow httpx
python3 ops/sync_linkedin_metrics.py
python3 ops/generate_all_linkedin_assets.py --patch
```

Luego en `../cli-market-content`:

```bash
git init
git add .
git commit -m "Initial GTM content"
# git remote add origin git@github.com:Treevu-ai/cli-market-content.git
```

## Estructura

| Carpeta | Contenido |
|---------|-----------|
| `linkedin/` | Day-01…30, calendario, data-gate, PUBLISH |
| `linkedin/assets/` | PNG/GIF (generados, no en plantilla) |
| `metrics/` | price-pulse, queries JSON |
| `strategy/` | GTM-Hub, content-strategy, growth-channels… |
| `calendar/` | linkedin-calendar, dev-calendar |
| `outbound/` | secuencias outbound |
| `templates/` | plantillas Obsidian |
| `generated/` | briefings y reportes (opcional) |

## Publicar cada día

Ver `linkedin/PUBLISH.md`.
