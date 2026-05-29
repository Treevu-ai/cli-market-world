# Contenido GTM / LinkedIn

Posts e imágenes **no están en este repo**. Repo privado aparte.

## Ruta raíz (Ricardo / WSL)

```text
/home/acuba/Proyectos/cli-market-content
```

## Setup automático

Desde el repo de producto (`/home/acuba/Proyectos/nuevo`):

```bash
bash ops/setup_content_repo_acuba.sh
```

O manual:

```bash
cd /home/acuba/Proyectos/nuevo
python3 ops/init_content_repo.py --target /home/acuba/Proyectos/cli-market-content
export CLI_MARKET_CONTENT_DIR=/home/acuba/Proyectos/cli-market-content
python3 ops/generate_all_linkedin_assets.py --patch
```

## Publicar hoy (día 1)

| Qué | Ruta absoluta |
|-----|----------------|
| Texto | `/home/acuba/Proyectos/cli-market-content/linkedin/Day-01.md` |
| Imagen | `/home/acuba/Proyectos/cli-market-content/linkedin/assets/day-01/day-01-linkedin.png` |

Guía: `cli-market-content/linkedin/PUBLISH.md`

## Repo GitHub privado

```bash
cd /home/acuba/Proyectos/cli-market-content
git remote add origin git@github.com:Treevu-ai/cli-market-content.git
git push -u origin main
```

(Crear el repo vacío en GitHub antes del push.)
