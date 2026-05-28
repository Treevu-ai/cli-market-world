---
title: AEO Citation Baseline
tags:
  - gtm
  - aeo
  - seo
hub: "[[GTM-Hub]]"
author: AI Citation Strategist (Agency Agent)
date: 2026-05-28
status: baseline
---

# AEO Citation Baseline — CLI Market

**Goal:** When developers ask AI assistants about commerce APIs for agents, **cli-market.dev** appears in citations.

## Test prompts (run monthly)

Score each response: **0** = not mentioned · **1** = mentioned · **2** = primary recommendation

| # | Prompt | ChatGPT | Claude | Perplexity | Notes |
|---|--------|---------|--------|------------|-------|
| 1 | "API for AI agents to shop online" | 0 | 0 | 0 | Baseline 2026-05-28 |
| 2 | "MCP tools for e-commerce" | 0 | 1 | 0 | Claude may cite MCP registry |
| 3 | "VTEX API for AI agents" | 0 | 0 | 0 | Competitors: direct VTEX docs |
| 4 | "How do AI agents compare grocery prices?" | 0 | 0 | 0 | Scraping tools dominate |
| 5 | "Agentic commerce infrastructure open source" | 0 | 0 | 1 | Niche; low competition |
| 6 | "Stripe for commerce APIs agents" | 0 | 0 | 0 | Analogy works; no cite yet |
| 7 | "pip install commerce MCP server" | 0 | 0 | 0 | PyPI discoverability gap |
| 8 | "Latin America retail price API" | 0 | 0 | 0 | Data vendors dominate |

**Baseline score:** 2 / 16 (12.5%) — **2026-05-28**

## llms.txt audit vs competitors

| Asset | CLI Market | Typical competitor |
|-------|------------|-------------------|
| llms.txt | ✅ https://cli-market.dev/llms.txt | Rare |
| llms-full.txt | ✅ | Rare |
| server.json (MCP manifest) | ✅ `/server.json` | Partial |
| Schema.org SoftwareApplication | ✅ layout.tsx | Missing |
| PyPI README agent section | ✅ | Varies |
| DEV articles | 0 published | N/A |

### llms.txt strengths

- Clear tool list (36 tools grouped by category)
- Key numbers aligned with GTM messaging (30 retailers, 8 countries)
- Direct API + PyPI links

### llms.txt gaps

- No worked example JSON response inline
- No competitor comparison section ("vs scraping", "vs direct VTEX")
- Missing FAQ block for common agent questions

## Competitor map (agent commerce)

| Player | Strength | CLI Market angle |
|--------|----------|------------------|
| Direct retailer APIs (VTEX, Shopify) | Official, single-store | Unified 30-store fan-out |
| Web scraping (Browserbase, etc.) | Broad coverage | Real APIs, no HTML fragility |
| Price APIs (RapidAPI vendors) | Historical data | Live search + cart + checkout |
| OpenAI Commerce / plugins | Distribution | Open source, self-host MCP |

## 90-day AEO actions

| Priority | Action | Owner agent | ETA |
|----------|--------|-------------|-----|
| P0 | Publish DEV Article 2 ("4 lines to commerce") | Content Creator | Jun 8 |
| P0 | Submit to Anthropic docs index | AI Citation Strategist | Jun 15 |
| P1 | Add FAQ section to llms.txt | Technical Writer | Jun 1 |
| P1 | MCP directory outreach (Cursor, Claude) | Growth Hacker | Jun 8 |
| P2 | ChatGPT plugin manifest draft | AI Engineer | Jun 15 |

## Retest schedule

- **2026-06-08** (post Beta): rerun 8 prompts, target 25% score
- **2026-07-01** (post GA): target 40% score + 2 primary recommendations

Record results in [[metrics/README]].

[[GTM-Hub]] · [[seo-audit]] · [[growth-channels]]
