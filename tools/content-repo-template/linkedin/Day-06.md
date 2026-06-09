---
title: Day 06
status: ready
day: 6
pillar: commerce-ai
lang: es
published_at:
link_comment: https://cli-market.dev/tools
tags:
  - linkedin
---

# Day 06 — Por qué 22 herramientas MCP

**Calendario:** [[linkedin-calendar]] · **Hub:** [[GTM-Hub]]

## Hooks (elegir 1)

1. **Behind the scenes:** ¿Por qué 22 herramientas MCP? Porque un agente necesita buscar, comparar, añadir al carrito Y pagar.
2. **Design:** No basta con un endpoint `/search`. El comercio para agentes es un workflow completo.
3. **Specific:** 36 tools. 6 categorías. Un agente que solo busca no compra.

## Post (copiar a LinkedIn — sin link en cuerpo)

¿Por qué 22 herramientas MCP?

Porque un agente que solo puede "buscar productos" no compra nada.

Cuando diseñamos CLI Market, la tentación fue publicar 3 tools y listo: search, compare, done.

Pero el comercio real es un workflow:

**Buscar** → market_search, market_categories, market_barcode, market_brands

**Comparar** → market_compare, market_basket, market_intel, market_trending

**Decidir** → market_inflation, market_price_history, market_stats

**Actuar** → market_add, market_cart, market_checkout, market_stock

**Operar** → market_orders, market_reorder, market_ticket, market_alerts

**Descubrir** → market_stores, market_countries, market_lines, market_ask

36 herramientas porque cada paso reduce alucinaciones.

Un agente con tools mal definidas inventa precios.

Un agente con primitives claras devuelve JSON verificable.

Eso es lo que publicamos en MCP: schemas estrictos, descripciones accionables, respuestas minificadas (85% menos tokens vs HTML crudo).

68 retailers (38 verified). 8 países. 43K+ precios reales.

Un `pip install`. Un servidor MCP. Listo para Cursor, Claude Desktop, o tu propio runtime.

¿Cuántas tools usa tu agente hoy para interactuar con comercio?

## Primer comentario

Copia-pega configs MCP para Cursor y Claude 👇

https://cli-market.dev/tools

```
pip install cli-market-world
market-mcp
```

Lista completa: https://cli-market.dev/llms.txt

## Hashtags

#MCP #AI #ecommerce #agents #opensource

## Assets

**Adjuntar en LinkedIn:** `docs/linkedin/assets/day-06/day-06-linkedin.png`
Regenerar: `python3 ops/generate_all_linkedin_assets.py --day 6` · todos: `python3 ops/generate_all_linkedin_assets.py`
## Checklist

- [x] Mensaje alineado ([[GTM-Hub#Mensaje público acordado]]) — 36 MCP, 30 retailers
- [ ] Responder comentarios 60 min post-publicación

## Notas post-publicación

- Impresiones:
- Comentarios clave:
