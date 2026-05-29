# Day 01 — assets LinkedIn

**Publicar:** adjuntar `day-01-linkedin.png` al post (recomendado).

| Archivo | Dimensiones | Notas |
|---------|-------------|--------|
| `day-01-linkedin.png` | 1200×1500 | Imagen única: comando + comparación + JSON |
| `day-01-terminal.png` | 1200×720 | Recorte terminal |
| `day-01-terminal.gif` | animado | Variante motion |
| `day-01-compare-json.png` | 1200×900 | Solo respuesta API |

## Regenerar

```bash
curl -sS -X POST https://cli-market-production.up.railway.app/products/compare \
  -H 'Content-Type: application/json' \
  -d '{"query":"leche","country":"PE","limit":6}' \
  > docs/metrics/query-leche-pe.json

python3 ops/generate_linkedin_asset.py --day 1
```

Datos en vivo · fuente: producción Railway.
