---
title: Day 05
status: ready
day: 5
pillar: commerce-ai
lang: es
published_at:
link_comment: https://cli-market.dev
tags:
  - linkedin
---

# Day 05 — Carousel: 4 pasos para que tu agente compre solo

**Calendario:** [[linkedin-calendar]] · **Hub:** [[GTM-Hub]]

## Hooks (elegir 1)

1. **Educational:** 4 pasos para que tu agente de IA compre solo (sin scraping).
2. **How-to:** Tu agente puede buscar. ¿Puede pagar? Este es el flujo completo.
3. **Listicle:** De `pip install` a checkout en 4 pasos.

## Post (copiar a LinkedIn — sin link en cuerpo; adjuntar carousel)

Tu agente puede escribir código.

¿Puede comprar?

La mayoría se queda en el paso 1: buscar en Google y adivinar precios.

Este es el flujo que usamos en CLI Market para que un agente compre solo — sin scraping, sin 30 integraciones manuales.

**Slide 1 — Instala**
`pip install cli-market-world-world`
Una dependencia. CLI + API + 22 herramientas MCP.

**Slide 2 — Autentica**
`market login`
Acceso free tier. Token listo para API y MCP.

**Slide 3 — Busca y compara**
`market search "arroz" --country PE`
`market compare "aceite de oliva"`
30 retailers. 8 países. JSON plano. Precios reales cada 8h.

**Slide 4 — Checkout**
`market checkout --payment yape`
PayPal, Yape/Plin QR, Wise, Lemon.
El agente cierra la compra — no solo recomienda.

Infraestructura de comercio para agentes.

Stripe convirtió pagos en APIs. Nosotros convertimos comercio en APIs.

Guarda el carousel si estás construyendo agentes con capacidad de compra real.

¿En qué paso se detuvo su agente?

## Carousel — copy por slide

| Slide | Título | Body |
|-------|--------|------|
| 1 | Instala | `pip install cli-market-world-world` · CLI + API + MCP |
| 2 | Autentica | `market login` · Free tier |
| 3 | Busca | `market search` / `market compare` · 30 retailers · 8 países |
| 4 | Compra | `market checkout` · PayPal · Yape/Plin QR |

## Primer comentario

Guía completa + configs MCP 👇

https://cli-market.dev

```
pip install cli-market-world-world
market hello
```

Tools: https://cli-market.dev/tools · Docs agentes: https://cli-market.dev/llms.txt

## Hashtags

#AI #ecommerce #MCP #agents #tutorial

## Assets

**Adjuntar en LinkedIn:** `docs/linkedin/assets/day-05/day-05-linkedin.png`
**Carousel (4 imágenes):** subir en orden `day-05-slide-01.png` … `04.png` en la misma carpeta.

Regenerar: `python3 ops/generate_all_linkedin_assets.py --day 5` · todos: `python3 ops/generate_all_linkedin_assets.py`
## Checklist

- [x] Mensaje alineado ([[GTM-Hub#Mensaje público acordado]])
- [ ] Carousel diseñado antes de publicar
- [ ] Responder comentarios 60 min post-publicación

## Notas post-publicación

- Impresiones:
- Comentarios clave:
