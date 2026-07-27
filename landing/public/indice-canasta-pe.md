# Índice Canasta Perú

**Actualizado:** 2026-07-27 15:41 (UTC) · Fuente: [CLI Market dashboard](https://cli-market-api.fly.dev/dashboard/data)

Canasta básica comparable (10 ítems) en cadenas peruanas con cobertura activa. Señal pública del data moat — ver [`docs/gtm/pitch-agentic-protocols.md`](../docs/gtm/pitch-agentic-protocols.md).

## Resumen

- **Cadenas PE en canasta:** 7
- **Freshness:** ver dashboard
- **Cobertura 7d:** 32.9%

## Totales por cadena (PEN)

| Cadena | Ítems | Total canasta |
|--------|------:|--------------:|
| Datilera Biomarket | 6/10 | S/ 63.00 |
| Vega | 10/10 | S/ 65.70 |
| AmaGreen Mayorista | 4/10 | S/ 66.60 |
| Plaza Vea | 11/10 | S/ 67.19 |
| Metro | 11/10 | S/ 78.99 |
| Wong | 11/10 | S/ 83.39 |
| Makro Online | 11/10 | S/ 90.59 |

## Spread

- Más barata: **Datilera Biomarket** (S/ 63.00)
- Más cara: **Makro Online** (S/ 90.59)
- Ratio max/min: **1.44×**

## Metodología

- Ítems: leche, arroz, aceite, azúcar, huevos, pan, café, pollo, queso, jabón (canasta CLI Market)
- Precios de góndola online, normalizados cuando aplica; actualización collector cada **4 h**
- Solo cadenas con ≥60% ítems encontrados en el snapshot

## API

```bash
pip install cli-market-world
market basket "arroz:1 aceite:1 leche:1" --country PE
```

*CLI Market · datos verificables · [cli-market.dev](https://cli-market.dev)*
