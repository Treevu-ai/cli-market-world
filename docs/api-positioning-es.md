---
title: Posicionamiento API — ES
tags:
  - api
  - gtm
  - copy
---

# CLI Market — copy API / landing / docs (ES)

> **Honestidad técnica:** claims de *flag de confianza* y filtro de outliers aplican desde bloque cero (PR #16–#18). Verificar en prod antes de campaña pública.

## Tagline

**Precios de retail reales, listos para agentes. Una llamada. Datos verificados, con flag de confianza.**

## Bloque de valor

Los agentes de IA no pueden comparar precios en retail físico. Cada cadena tiene su propia autenticación, su propia búsqueda, ningún esquema común. CLI Market resuelve eso: una sola API con precios reales de góndola, normalizados y comparables entre cadenas.

**Qué nos hace distintos:** cada precio pasa por un control de calidad antes de llegarte. Normalizamos por unidad (precio por kilo, por litro), filtramos descuentos imposibles y brechas anómalas, y cada dato viaja con un nivel de confianza. Tu agente no recibe un -99% mal leído como si fuera una oferta real.

## Snippet de uso

```bash
market basket "arroz:1 aceite:1 leche:1 huevos:1" --country AR
# Compara el total de la canasta entre Carrefour, Jumbo y Vea
# Respuesta: total por cadena + la más barata (precios verificados)

market compare "aceite de girasol 900ml" --country AR
# Mismo producto, varias cadenas, precio normalizado por litro
```

## Por qué confiar en el dato

- Precios de góndola reales, no estimados
- Normalización por kilo/litro para comparaciones justas
- Filtro de outliers y descuentos sospechosos en dashboard y spreads de marketing
- Refresco cada 8 horas
- Cobertura multi-cadena, no una sola tienda

## Pitch ventas / inversión (una línea)

Stripe convirtió los pagos en una API. Nosotros convertimos el comercio en una API — con un foso de datos que se hace más profundo cada día.

---

[[GTM-Hub]] · [[linkedin/Day-09-AR]] · [[linkedin/data-gate]]
