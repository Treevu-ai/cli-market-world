# Índice Canasta Perú

**Actualizado:** 2026-08-03 14:14 (UTC) · Fuente: [CLI Market dashboard](https://cli-market-api.fly.dev/dashboard/data)

Canasta básica comparable (10 ítems) en cadenas peruanas con cobertura activa. Señal pública del data moat — ver [`docs/gtm/pitch-agentic-protocols.md`](../docs/gtm/pitch-agentic-protocols.md).

## Resumen

- **Cadenas PE en canasta:** 2
- **Freshness:** ver dashboard
- **Cobertura 7d:** 93.8%

## Totales por cadena (PEN)

| Cadena | Ítems | Total canasta |
|--------|------:|--------------:|
| Del Campo a tu Casa | 3/10 | S/ 58.00 |
| AmaGreen Mayorista | 4/10 | S/ 66.60 |

## Spread

- Más barata: **Del Campo a tu Casa** (S/ 58.00)
- Más cara: **AmaGreen Mayorista** (S/ 66.60)
- Ratio max/min: **1.15×**

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
