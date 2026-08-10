# Índice Canasta Perú

**Actualizado:** 2026-08-10 13:57 (UTC) · Fuente: [CLI Market dashboard](https://cli-market-api.fly.dev/dashboard/data)

Canasta básica comparable (10 ítems) en cadenas peruanas con cobertura activa. Señal pública del data moat — ver [`docs/gtm/pitch-agentic-protocols.md`](../docs/gtm/pitch-agentic-protocols.md).

## Resumen

- **Cadenas PE en canasta:** 3
- **Freshness:** ver dashboard
- **Cobertura 7d:** 93.2%

## Totales por cadena (PEN)

| Cadena | Ítems | Total canasta |
|--------|------:|--------------:|
| Tambo+ | 5/10 | S/ 57.20 |
| Del Campo a tu Casa | 3/10 | S/ 57.70 |
| AmaGreen Mayorista | 4/10 | S/ 66.60 |

## Spread

- Más barata: **Tambo+** (S/ 57.20)
- Más cara: **AmaGreen Mayorista** (S/ 66.60)
- Ratio max/min: **1.16×**

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
