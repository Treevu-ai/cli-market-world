---
title: Day 04
status: ready
day: 4
pillar: commerce-ai
lang: es
published_at:
link_comment: https://cli-market.dev
tags:
  - linkedin
---

# Day 04 — 5 agentes, leche Wong vs Metro

**Calendario:** [[linkedin-calendar]] · **Hub:** [[GTM-Hub]]

## Hooks (elegir 1)

1. **Personal story:** Probé 5 agentes de IA. Ninguno podía decirme cuánto cuesta la leche en Wong vs Metro.
2. **Frustration:** Le pedí a ChatGPT el precio de la leche en Lima. Me dio una respuesta genérica de 2023.
3. **Specific:** 5 agentes. 1 pregunta simple. 0 precios reales de góndola.

## Post (copiar a LinkedIn — sin link en cuerpo)

Probé 5 agentes de IA distintos.

Les hice la misma pregunta:

"¿Cuánto cuesta la leche en Wong vs Metro en Lima?"

Respuestas que obtuve:

→ Estimaciones genéricas
→ "Los precios varían, consulta la web"
→ Links a páginas que el agente no puede leer bien
→ Alucinaciones con números inventados

Ninguno pudo darme precios reales de góndola. Hoy. En Lima. En dos retailers concretos.

El problema no es la inteligencia del modelo.

Es que no tienen infraestructura de comercio.

Los agentes pueden razonar, escribir código, analizar documentos…

Pero no pueden comprar ni comparar precios reales porque cada retailer es un mundo aparte: auth distinta, búsqueda distinta, carrito distinto, checkout distinto.

Por eso construimos CLI Market:

→ 60 retailers (30 verificados) en 8 países
→ Precios reales, refresh cada 8 horas
→ Una API, un schema, `pip install cli-market`

La próxima vez que le preguntes a tu agente por la leche, que te responda con datos — no con suposiciones.

¿Qué producto probarías primero con un agente?

## Primer comentario

Probé la misma búsqueda con CLI Market 👇

https://cli-market.dev

```
pip install cli-market
market search "leche" --country PE --store wong
market compare "leche entera" --country PE
```

MCP configs: https://cli-market.dev/tools

## Hashtags

#AI #ecommerce #MCP #agents #Peru

## Assets

**Adjuntar en LinkedIn:** `docs/linkedin/assets/day-04/day-04-linkedin.png`
Regenerar: `python3 ops/generate_all_linkedin_assets.py --day 4` · todos: `python3 ops/generate_all_linkedin_assets.py`
## Checklist

- [x] Mensaje alineado ([[GTM-Hub#Mensaje público acordado]])
- [ ] No incluir precios específicos de leche (varían; usar screenshot en asset)
- [ ] Responder comentarios 60 min post-publicación

## Notas post-publicación

- Impresiones:
- Comentarios clave:
