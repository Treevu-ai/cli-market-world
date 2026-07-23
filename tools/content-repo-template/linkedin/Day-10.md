---
title: Day 10
status: ready
day: 10
pillar: data-stories
lang: es
published_at:
link_comment: https://cli-market.dev
tags:
  - linkedin
---

# Day 10 — Inflación — señal cada 8 horas

**Calendario:** [[linkedin-calendar]] · **Hub:** [[GTM-Hub]]

## Hooks (elegir 1)

1. **Hook 1:** ¿Inflación real? Nuestro collector corre cada 8 horas. Esto es lo que vemos.
2. **Hook 2:** No reemplazamos al INEI. Pero sí damos señal de mercado a agentes cada 8h.
3. **Hook 3:** 36K+ precios frescos. Un snapshot cada 8 horas. Así se ve el retail desde IA.

## Post (copiar a LinkedIn — sin link en cuerpo)

¿Inflación real?

No somos el INEI ni el INDEC. No publicamos un índice oficial.

Pero sí tenemos algo que casi nadie tiene para agentes de IA: **37,731 precios de góndola en las últimas 24 horas** y **43,415 indexados** en 13 países.

Nuestro collector:

→ Corre automático en Railway + PostgreSQL
→ Cero intervención humana
→ APIs reales (VTEX + Magento), cero scraping
→ Snapshots históricos para ver variación

Herramienta MCP `market_inflation` devuelve delta de precios por país y línea.

Para un agente, eso es oro: señal de mercado accionable, no un PDF trimestral.

Para un retailer, es presión: ahora compites también en búsquedas de IA.

Stripe convirtió pagos en APIs.

Nosotros convertimos precios de góndola en APIs.

¿Qué país te interesa monitorear primero?

## Primer comentario

Stats en vivo 👇

https://cli-market.dev

```
market stats
```

## Hashtags

#AI #data #ecommerce #inflation #buildinpublic

## Assets

**Adjuntar en LinkedIn:** `docs/linkedin/assets/day-10/day-10-linkedin.png`
Regenerar: `python3 ops/generate_all_linkedin_assets.py --day 10` · todos: `python3 ops/generate_all_linkedin_assets.py`
## Checklist

- [ ] Mensaje alineado ([[GTM-Hub#Mensaje público acordado]])
- [ ] Datos verificados ([[linkedin/data-gate]] / [[metrics/price-pulse-YYYY-WW]]) si aplica
- [ ] Responder comentarios 60 min post-publicación

## Notas post-publicación

- Impresiones:
- Comentarios clave:
