# Índice Canasta Perú

**Actualizado:** 2026-07-01 15:31 (UTC) · Fuente: [CLI Market dashboard](https://cli-market-api.fly.dev/dashboard/data)

Canasta básica comparable (10 ítems) en cadenas peruanas con cobertura activa. Señal pública del data moat — ver [`docs/gtm/pitch-agentic-protocols.md`](../docs/gtm/pitch-agentic-protocols.md).

## Resumen

- **Cadenas PE en canasta:** 4
- **Freshness:** ver dashboard
- **Cobertura 7d:** 92.5%

## Totales por cadena (PEN)

| Cadena | Ítems | Total canasta |
|--------|------:|--------------:|
| Plaza Vea | 10/10 | S/ 65.70 |
| Metro | 10/10 | S/ 70.09 |
| Wong | 10/10 | S/ 77.99 |
| Nuna Orgánica | 9/10 | S/ 149.72 |

## Spread

- Más barata: **Plaza Vea** (S/ 65.70)
- Más cara: **Nuna Orgánica** (S/ 149.72)
- Ratio max/min: **2.28×**

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
