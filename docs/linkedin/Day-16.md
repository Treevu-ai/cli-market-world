---
title: Day 16
status: ready
day: 16
pillar: build-in-public
lang: es
published_at:
link_comment: https://cli-market.dev
tags:
  - linkedin
---

# Day 16 — 30 APIs sincronizadas

**Calendario:** [[linkedin-calendar]] · **Hub:** [[GTM-Hub]]

## Hooks (elegir 1)

1. **Hook 1:** El mayor desafío no fue el código. Fue mantener 30 APIs externas sincronizadas.
2. **Hook 2:** 30 retailers = 30 formas distintas de fallar. Así lo manejamos.
3. **Hook 3:** Async fan-out a 30 APIs: lo que nadie te cuenta del agent commerce.

## Post (copiar a LinkedIn — sin link en cuerpo)

El mayor desafío técnico de CLI Market no fue escribir Python.

Fue mantener **30 APIs externas sincronizadas**.

Cada retailer VTEX o Magento tiene:

→ Rate limits distintos
→ Schemas que cambian sin aviso
→ Tokens que expiran
→ Catálogos de 10K+ SKUs

Nuestra respuesta:

→ `httpx` + `asyncio` para fan-out paralelo
→ Health checks por tienda (dashboard en vivo)
→ Collector cada 8h con retry y alertas
→ Desactivar tiendas rotas — calidad > cantidad

Hoy: 31 en catálogo, 16 saludables, 51% success rate.

No es 100%. Pero es honesto — y mejora cada semana.

Los agentes merecen datos reales, no promesas.

¿Qué stack usarías para fan-out a N APIs?

## Primer comentario

Arquitectura 👇

https://github.com/Treevu-ai/cli-market-world

## Hashtags

#python #asyncio #buildinpublic #ecommerce #AI

## Assets

**Adjuntar en LinkedIn:** `docs/linkedin/assets/day-16/day-16-linkedin.png`
Regenerar: `python3 ops/generate_all_linkedin_assets.py --day 16` · todos: `python3 ops/generate_all_linkedin_assets.py`
## Checklist

- [ ] Mensaje alineado ([[GTM-Hub#Mensaje público acordado]])
- [ ] Datos verificados ([[linkedin/data-gate]] / [[metrics/price-pulse-YYYY-WW]]) si aplica
- [ ] Responder comentarios 60 min post-publicación

## Notas post-publicación

- Impresiones:
- Comentarios clave:
