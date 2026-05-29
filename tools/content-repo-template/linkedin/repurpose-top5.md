---
title: Repurpose Top 5 LinkedIn → Multi-channel
tags:
  - linkedin
  - content
  - repurpose
hub: "[[GTM-Hub]]"
date: 2026-05-28
---

# Repurpose — Top 5 LinkedIn Posts

**Agente:** Content Creator · **Fuente:** [[linkedin/00-Index]] semana 1

## Selection criteria

Highest expected reach + technical depth + reusable demos.

| Rank | Day | Título | Canales |
|------|-----|--------|---------|
| 1 | 1 | Agente comparó 30 retailers en 0.8s | DEV Art. 1 hook, Twitter thread, landing hero |
| 2 | 3 | Stripe pagos / nosotros comercio | DEV Art. 1 body, Twitter, outbound email |
| 3 | 5 | Carousel 4 pasos agente compra | DEV Art. 2 tutorial, GitHub README |
| 4 | 6 | Por qué 36 herramientas MCP | `/tools` page intro, DEV MCP post |
| 5 | 25 | pip install CTA | PyPI README, HN, Reddit |

---

## 1. Day 01 → DEV "Commerce Infrastructure" (intro)

**DEV title:** What Happens When an AI Agent Compares 30 Supermarkets in Under a Second

**Opening paragraph (adapt from LI):**

> An AI agent just compared prices across 30 verified retailers in 0.8 seconds. No browser. No scraping. One JSON call.

**Embed:** Terminal GIF + `market search "leche" --country PE --json`

**CTA:** https://cli-market.dev?utm_source=devto&utm_campaign=repurpose-d1

**Twitter thread (5 tweets):**

1. An AI agent compared 30 supermarkets in 0.8s. Here's how 🧵
2. Problem: agents can reason but can't shop — 30 APIs, 30 auths
3. CLI Market = one API, 36 MCP tools, 8 countries
4. `pip install cli-market` + `market search "leche" --country PE`
5. Open source MIT → cli-market.dev

---

## 2. Day 03 → DEV vision section

**Pull quote:** "Stripe turned payments into APIs. We're doing the same for commerce."

**Use in:** Art. 1 section 2, outbound email subject line, landing `#pricing` subhead test.

---

## 3. Day 05 → DEV tutorial (Art. 2)

**Carousel → numbered DEV post:**

1. `pip install cli-market`
2. `market login`
3. `market search "leche" --country PE`
4. `market add` → `market checkout`

**Landing snippet:** Add "4 steps" section below hero (copy from [[Day-05]]).

---

## 4. Day 06 → `/tools` + MCP outreach

**DEV title:** Why 36 MCP Tools Beat One Generic "Shop" Tool

**Bullet list:** search, compare, basket, inflation, ticket OCR, voice, export...

**Outreach email (AI IDE teams):** Link https://cli-market.dev/tools?utm_source=email&utm_campaign=mcp-outreach

---

## 5. Day 25 → HN / Reddit / PyPI

**HN title:** Show HN: CLI Market – commerce infrastructure for AI agents (pip install)

**Reddit r/LocalLLaMA:** Focus on MCP + minified JSON (85% token savings from llms.txt)

**PyPI README:** Add "Try now" block at top:

```bash
pip install cli-market && market search "leche" --country PE
```

---

## UTM template

```
?utm_source={linkedin|devto|twitter|hn|reddit}&utm_medium=social&utm_campaign=repurpose-d{N}
```

Track in [[metrics/README]] weekly.

[[GTM-Hub]] · [[content-strategy]] · [[dev-calendar]]
