---
title: Day 09 AR — Canasta básica Argentina
status: draft
day: 9
pillar: data-stories
lang: es
market: AR
published_at:
link_comment: https://cli-market.dev
tags:
  - linkedin
  - argentina
---

# Day 09 AR — Canasta básica Argentina — Carrefour vs Jumbo vs Vea

**Calendario:** [[linkedin-calendar]] · **Hub:** [[GTM-Hub]] · **Gate:** [[linkedin/data-gate#Gate AR — canasta (bloque cero)]]

> ⛔ **No publicar** hasta que el gate AR pase. Placeholders `[ ]` = datos verificados en dashboard post-bloque cero.

## Hooks (elegir 1)

1. **Hook 1:** La misma canasta básica cuesta `[X]`% más en una cadena argentina que en otra. Esta semana.
2. **Hook 2:** Arroz, aceite, leche, huevos. Mismos productos, distinto supermercado, distinto precio.
3. **Hook 3:** La inflación no es un número abstracto del INDEC. Es JSON de góndola, comparado en tiempo real.

## Post (copiar a LinkedIn — sin link en cuerpo)

¿Cuánto cuesta llenar la canasta básica en Argentina?

Depende de a qué supermercado entres.

Tomamos `[10]` productos esenciales —arroz, aceite, leche, huevos, pan— y comparamos el total entre Carrefour, Jumbo y Vea.

La diferencia entre la más cara y la más barata: `[X]`%.

No es una estimación. No es el promedio de un instituto. Son precios de góndola, leídos de las webs de cada cadena, normalizados por kilo y por litro para que la comparación sea justa.

→ Mismo producto, empaque equivalente (1 kg / 1 L)
→ `[3]` cadenas argentinas comparadas
→ Datos refrescados cada 8 horas

Los comparadores de precios para humanos existen hace años.

Los comparadores que un agente de IA puede consultar por API casi no existen.

Esa capa es la que estamos construyendo.

¿Qué producto sumarías a la canasta de prueba?

## Primer comentario

Probar la canasta 👇

https://cli-market.dev

## Hashtags

#AI #ecommerce #Argentina #data #MCP #inflación

## Datos a verificar antes de publicar

Fuente: `GET /dashboard/data` → `canasta_basica`, `marketing_spreads`, `suspect_discounts`.

| Campo | Regla | Valor verificado |
|-------|--------|------------------|
| `[X]`% brecha canasta | `(total_max − total_min) / total_min × 100` solo si las 3 cadenas tienen **≥6/10 ítems** y totales comparables | ⏳ pendiente |
| `[10]` productos | `len(CANASTA_ITEMS)` | 10 |
| `[3]` cadenas | Carrefour AR, Jumbo AR, Vea AR en `canasta_basica` | ⏳ pendiente |
| Brecha alternativa (copy secundario) | `marketing_spreads` ARS con `spread_ratio ≥ 2.5` — **por ítem**, no canasta total | ver gate |
| Outliers | `suspect_discounts` vacío o solo en bloque ops | ⏳ verificar |
| Moneda | Solo ARS en la comparación | ⏳ verificar |

**No usar** `canasta_spreads` crudo ni `dispersion` para el titular. **No inflar:** si la brecha real es ~1.5x (50%), decir 50%, no 150%.

## Checklist

- [ ] Bloque cero mergeado y deploy Railway activo
- [ ] Trío ARS ≥6/10 ítems cada uno ([[linkedin/data-gate#Gate AR — canasta (bloque cero)]])
- [ ] `[X]`% calculado y pegado en esta nota + [[metrics/price-pulse-YYYY-WW]]
- [ ] Post cualitativo descartado si gate no pasa — posponer

## Notas post-publicación

- Impresiones:
- Comentarios clave:
