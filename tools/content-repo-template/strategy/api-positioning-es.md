---
title: Posicionamiento API — ES
tags:
  - api
  - gtm
  - copy
date: 2026-06-12
---

# CLI Market — copy API / landing / docs (ES)

> **Honestidad técnica:** claims de *flag de confianza* y filtro de outliers aplican desde bloque cero (PR #16–#18). Verificar en prod antes de campaña pública.

## Tagline

**El middleware LATAM entre los protocolos agénticos y los retailers que aún no están listos.**

## Momento (Jun 2026)

El mercado está construyendo dos capas que definen el comercio de los próximos 5 años:

1. **Riel de pagos agénticos** — Visa+OpenAI, Mastercard Agent Pay, PayPal ACS estandarizan el checkout sin fricción humana. El pago deja de ser el cuello de botella.
2. **Guerra de protocolos de descubrimiento** — ACP (OpenAI/Stripe) vs UCP (Google/Shopify/Visa/Walmart) deciden cómo los agentes *encuentran* y *evalúan* productos.

Con checkout resuelto, el cuello de botella se mueve al **descubrimiento y comparación** — exactamente donde vive CLI Market.

**Validación (intel de mercado):** OpenAI Instant Checkout muestra adopción limitada (decenas de comercios, no cientos) — la fricción de integración es el problema real. CLI Market es el anti-fricción. *[Fuente pendiente antes de post público]*

## Bloque de valor

Los retailers de LATAM no van a implementar UCP o ACP por su cuenta. Falabella, Ripley, Wong, Metro, Plaza Vea no tienen equipos de protocolo agéntico. Cuando los agentes empiecen a comprar masivamente, estos retailers serán invisibles para el ecosistema agéntico — a menos que alguien los conecte.

**CLI Market es ese puente.**

Tu retailer peruano/LATAM disponible en cualquier agente que use UCP o ACP, sin tocar su backend. Una sola API con precios reales de góndola — normalizados, verificados, con historial — lista para ser consumida por agentes que operan sobre cualquier protocolo agéntico.

```bash
market search "leche" --country PE
# → precios de Metro, Wong, Plaza Vea en <2s · schema único · mapeable a UCP/ACP

market basket "arroz:1 aceite:1 leche:1" --country AR
# → compara el total de la canasta entre Carrefour, Jumbo y Vea
# → precios verificados · normalizado por kg/L · historial de hasta 12 meses
```

## Por qué el historial importa más ahora

Los agentes no solo necesitan saber *qué* comprar — necesitan saber *cuándo* comprar. El archivo histórico de precios de CLI Market + los rieles locales (Yape/Plin) = señales de timing únicos para agentes que operan en Perú.

Nadie puede replicar esto en 6 meses.

## Por qué confiar en el dato

- Precios de góndola reales, actualizados cada **4 horas**
- Normalización por kg/L para comparaciones justas entre cadenas
- Historial de hasta **12 meses** (Pro) / completo (Enterprise)
- Filtro de outliers y descuentos sospechosos documentado en dashboard
- **38 retailers verificados activos · 13 países · schema único**

## Pitch ventas / inversión (una línea)

Stripe convirtió los pagos en una API. CLI Market convierte el comercio LATAM en una — middleware LATAM preparado para integración UCP y ACP cuando el comercio agéntico llegue a la región.

## Para conversaciones con PSPs (Culqi/BCP/Niubiz)

Cuando Visa o Mastercard agéntico llegue a Perú, el PSP que lo adopte primero necesitará dos cosas:
1. **Riel de pago** — lo tiene el PSP
2. **Datos de retailers normalizados** — los tiene CLI Market

La pregunta no es "¿necesitamos una API de precios?" Es: **¿tu PSP quiere ser el puente entre el ecosistema agéntico global y el retail peruano, o prefiere que Amazon sea ese puente?**

El timing es crítico: esta conversación hay que tenerla *antes* de que Visa/Mastercard lleguen con su propio partner de datos.

---

[[GTM-Hub]] · [[docs/gtm/pitch-agentic-protocols]] · [[linkedin/Day-09-AR]] · [[linkedin/data-gate]]
