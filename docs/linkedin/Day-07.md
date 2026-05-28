---
title: Day 07
status: ready
day: 7
pillar: commerce-ai
lang: es
published_at:
link_comment: https://cli-market.dev
tags:
  - linkedin
---

# Day 07 — Data brag semana 1

**Calendario:** [[linkedin-calendar]] · **Hub:** [[GTM-Hub]]

> ⚠️ **Antes de publicar:** reemplazar `[N]` con cifra verificada de [[metrics/price-pulse-YYYY-WW]]. No publicar si el collector <80% success esa semana.

## Hooks (elegir 1)

1. **Data brag:** Esta semana: [N] precios frescos. 30 retailers. 8 países. Un solo `pip install`.
2. **Numbers:** 13K+ precios indexados. Refresh cada 8 horas. Cero scraping.
3. **Build in public:** Semana 1 de CLI Market en público — esto es lo que el collector vio.

## Post (copiar a LinkedIn — sin link en cuerpo)

Semana 1 construyendo infraestructura de comercio para agentes de IA.

Los números de esta semana:

→ **[N] precios indexados** (actualizar desde price-pulse)
→ **30 retailers** verificados
→ **8 países** — PE, AR, BR, MX, CO, CL, IT, FR
→ **36 herramientas MCP**
→ **Refresh cada 8 horas** — precios reales de góndola, no estimaciones

Cada precio viene de APIs de retailers reales (VTEX + Magento).

No scraping. No HTML parsing. No alucinaciones.

Un agente hace `market search "arroz" --country PE` y obtiene respuesta en menos de un segundo.

Eso es lo que estamos construyendo: la capa de infraestructura que falta entre los LLM y el comercio real.

Stripe convirtió pagos en APIs.

Nosotros convertimos comercio en APIs.

Open source. MIT. Free para developers.

Si eres retailer y quieres que los agentes te encuentren: la puerta está abierta.

## Primer comentario

Dashboard + quickstart 👇

https://cli-market.dev

```
pip install cli-market
market hello
market stats
```

Retailers: https://cli-market.dev/retailers

## Hashtags

#AI #ecommerce #data #MCP #buildinpublic

## Assets

- [ ] Screenshot dashboard KPIs o terminal `market stats`
- [ ] Gráfico simple: precios por país (si disponible en price-pulse)

## Checklist

- [ ] **[N] verificado** en [[metrics/price-pulse-YYYY-WW]] antes de publicar
- [x] Mensaje base alineado ([[GTM-Hub#Mensaje público acordado]])
- [ ] Collector ≥80% success esa semana
- [ ] Responder comentarios 60 min post-publicación

## Placeholder hasta export metrics

Si aún no hay price-pulse exportado, usar mensaje acordado **~13K precios** solo si el dashboard lo confirma el día de publicación.

## Notas post-publicación

- Impresiones:
- Comentarios clave:
