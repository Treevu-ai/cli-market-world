---
title: Day 21
status: ready
day: 21
pillar: build-in-public
lang: es
published_at:
link_comment: https://cli-market.dev
tags:
  - linkedin
---

# Day 21 — Error APIs VTEX inestables

**Calendario:** [[linkedin-calendar]] · **Hub:** [[GTM-Hub]]

## Hooks (elegir 1)

1. **Hook 1:** Mi error más grande: asumir que las APIs VTEX eran estables. Spoiler: no lo son.
2. **Hook 2:** 10 retailers desactivados. Lección aprendida en build in public.
3. **Hook 3:** La integración feliz en demo ≠ producción con 30 APIs.

## Post (copiar a LinkedIn — sin link en cuerpo)

Mi error más grande construyendo CLI Market:

Asumir que las APIs VTEX eran estables.

Spoiler: **no lo son**.

→ Tokens que expiran sin aviso
→ Endpoints que devuelven HTML en vez de JSON
→ Rate limits opacos
→ Catálogos que cambian de schema

Resultado: desactivamos 10 tiendas del catálogo. Mejor 31 que funcionan parcialmente que 41 en paper.

Dashboard en vivo muestra health por store — sin maquillaje.

Lección: **agent commerce necesita observabilidad por retailer**, no un boolean "integrado".

¿Le ha pasado que una API de terceros rompa producción un domingo?

## Primer comentario

Store health 👇

https://cli-market-production.up.railway.app/dashboard

## Hashtags

#buildinpublic #VTEX #ecommerce #failures #AI

## Assets

- [ ] GIF terminal / screenshot (si aplica)
- [ ] Carousel Canva (días 5, 12)

## Checklist

- [ ] Mensaje alineado ([[GTM-Hub#Mensaje público acordado]])
- [ ] Datos verificados ([[linkedin/data-gate]] / [[metrics/price-pulse-YYYY-WW]]) si aplica
- [ ] Responder comentarios 60 min post-publicación

## Notas post-publicación

- Impresiones:
- Comentarios clave:
