---
title: Day 08
status: ready
day: 8
pillar: data-stories
lang: es
published_at:
link_comment: https://cli-market.dev
tags:
  - linkedin
---

# Day 08 — Arroz Lima — variación entre supermercados

**Calendario:** [[linkedin-calendar]] · **Hub:** [[GTM-Hub]]

> ⚠️ Verificar datos en [[linkedin/data-gate]] antes de publicar.

## Hooks (elegir 1)

1. **Hook 1:** Data shock: el precio del arroz no es uno solo en Lima — varía fuerte entre cadenas esta semana.
2. **Hook 2:** Mismo producto, distinto supermercado, distinto precio. Nuestro collector lo ve cada 8 horas.
3. **Hook 3:** ¿Tu agente sabe comparar arroz en PE? El nuestro sí — con APIs reales, no scraping.

## Post (copiar a LinkedIn — sin link en cuerpo)

El precio del arroz no es un solo número en Lima.

Esta semana nuestro collector indexó miles de precios reales de góndola en supermercados peruanos — actualizados cada 8 horas vía APIs VTEX, sin scraping.

Lo que vemos en PE (arroz 750g, esta semana):

→ Desde **S/ 2.90** (Metro / Plaza Vea) hasta **S/ 4.40+** según marca
→ Wong y Metro compiten en el mismo SKU — el agente elige en <1s
→ No es índice INEI — es señal de góndola actualizada cada pocas horas

**36,935** precios en refresh 24h · **41,856** indexados · **35** retailers fresh · **8** países.

Si construyes agentes que toman decisiones de compra, necesitan esta capa de infraestructura.

¿Qué producto te gustaría ver comparado en PE la próxima semana?

## Primer comentario

Dashboard + comparar en terminal 👇

https://cli-market.dev

```
pip install cli-market
market compare "arroz" --country PE
```

Datos: [[metrics/price-pulse-2026-W22]]

## Hashtags

#AI #ecommerce #data #retail #Peru

## Assets

**Adjuntar en LinkedIn:** `docs/linkedin/assets/day-08/day-08-linkedin.png`
Regenerar: `python3 ops/generate_all_linkedin_assets.py --day 8` · todos: `python3 ops/generate_all_linkedin_assets.py`
## Checklist

- [ ] Mensaje alineado ([[GTM-Hub#Mensaje público acordado]])
- [ ] Datos verificados ([[linkedin/data-gate]] / [[metrics/price-pulse-YYYY-WW]]) si aplica
- [ ] Responder comentarios 60 min post-publicación

## Notas post-publicación

- Impresiones:
- Comentarios clave:
