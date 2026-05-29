---
title: Day 17
status: ready
day: 17
pillar: build-in-public
lang: es
published_at:
link_comment: https://cli-market.dev
tags:
  - linkedin
---

# Day 17 — Python httpx asyncio

**Calendario:** [[linkedin-calendar]] · **Hub:** [[GTM-Hub]]

## Hooks (elegir 1)

1. **Hook 1:** ¿Por qué Python + httpx + asyncio + FastAPI? Porque fan-out a 30 APIs lo exige.
2. **Hook 2:** Un search en CLI Market dispara N requests paralelos. Así lo construimos.
3. **Hook 3:** FastAPI + asyncio: la stack que eligió un commerce API para agentes.

## Post (copiar a LinkedIn — sin link en cuerpo)

¿Por qué Python para infraestructura de comercio para agentes?

Porque **`httpx` + `asyncio` + `FastAPI`** es imbatible para fan-out:

```python
# Simplificado: buscar en N retailers en paralelo
async with httpx.AsyncClient() as client:
    tasks = [search_store(client, store, query) for store in stores]
    results = await asyncio.gather(*tasks, return_exceptions=True)
```

Un `market search "leche"` dispara requests paralelos a Wong, Metro, Cencosud, Carrefour…

El agente recibe JSON unificado en <2 segundos.

Alternativas que evaluamos:

→ Node: bueno, pero ecosystem PyPI para CLI
→ Go: rápido, pero DX para data scientists peor
→ Sync requests: muerte a los 30 retailers

Python ganó por DX + async + ecosistema IA.

¿Tu agent stack es Python-first también?

## Primer comentario

Quickstart 👇

https://cli-market.dev

```
pip install cli-market
```

## Hashtags

#python #FastAPI #asyncio #AI #developers

## Assets

**Adjuntar en LinkedIn:** `docs/linkedin/assets/day-17/day-17-linkedin.png`
Regenerar: `python3 ops/generate_all_linkedin_assets.py --day 17` · todos: `python3 ops/generate_all_linkedin_assets.py`
## Checklist

- [ ] Mensaje alineado ([[GTM-Hub#Mensaje público acordado]])
- [ ] Datos verificados ([[linkedin/data-gate]] / [[metrics/price-pulse-YYYY-WW]]) si aplica
- [ ] Responder comentarios 60 min post-publicación

## Notas post-publicación

- Impresiones:
- Comentarios clave:
