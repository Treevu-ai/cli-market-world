---
title: Alpha Gates — Jun 1 2026
tags:
  - gtm
  - prd
  - alpha
hub: "[[GTM-Hub]]"
date: 2026-05-28
---

# Alpha Gates — 2026-06-01

Ejecución de gates del [[cli-market-prd-v2#4. Launch Plan]].

## Resumen

| Gate | Target PRD | Estado 2026-05-28 | Bloquea Alpha? |
|------|------------|-------------------|----------------|
| Billing Pro live | PayPal live + revenue loop | ✅ **Manual Pro** (email + PayPal Hosted Button) | No |
| Self-serve retailers | Form en `/retailers` | ✅ Form + `POST /v1/retailers/apply` | No |
| Collector reliability | 41/41 stores >80% | ❌ **31 activos, 51.6% healthy** | **Sí** (marketing data claims) |
| SEO críticos | Schema, sitemap, meta | ✅ Shipped 2026-05-28 | No |
| PyPI activation | `market hello` | ✅ Shipped | No |
| Admin security | Token on `/admin/*` | ✅ `MARKET_API_TOKEN` | No |

**Veredicto Alpha producto:** ✅ **GO** para launch comercial (billing + self-serve).

**Veredicto Alpha data marketing:** ⚠️ **CONDITIONAL** — LinkedIn sem 2 requiere [[linkedin/data-gate]].

## Gate 1: Billing Pro

| Check | Result |
|-------|--------|
| `POST /billing/request-pro` | ✅ 200 + email |
| SMTP Railway configured | ✅ |
| PayPal Hosted Button link in email | ✅ |
| Manual activation script | ✅ `ops/activate_pro.py` |
| E2E smoke | ✅ `ops/e2e_smoke.sh` |

**Nota:** PayPal REST webhook automation es opcional post-Alpha; flujo manual es el default operativo.

## Gate 2: Self-serve retailers

| Check | Result |
|-------|--------|
| Landing `/retailers` | ✅ Live |
| Apply API | ✅ |
| Confirmation UX | ✅ Application ID + email |

## Gate 3: Collector

| Check | Target | Actual |
|-------|--------|--------|
| Active stores in catalog | 41 | **31** (10 disabled — broken APIs) |
| Store success rate | >80% | **51.6%** |
| Healthy stores | 33+ | **16** |
| Prices indexed (24h) | 12K+ | **8,064** |

**Acciones post-Alpha:**

1. Continuar `ops/store_probe.py` semanal
2. Re-habilitar stores solo tras probe OK
3. No reactivar claims "41 retailers" en marketing hasta gate cumplido

## Gate 4: GTM pack

| Deliverable | Status |
|-------------|--------|
| GTM-Hub MOC | ✅ |
| LinkedIn D1–7 ready | ✅ |
| LinkedIn D8–30 drafts | ✅ 2026-05-28 |
| SEO week 1 | ✅ |
| DX audit | ✅ [[dx-audit]] |
| AEO baseline | ✅ [[aeo-citation-baseline]] |
| Agency Cursor rules | ✅ 184 rules installed |

## Go / No-Go decision

| Área | Decision |
|------|----------|
| **Alpha launch Jun 1** | **GO** — billing + self-serve + LinkedIn W1 |
| **Data-heavy LinkedIn W2** | **HOLD** until collector ≥80% OR use aggregate-only copy |
| **Beta Jun 8** | **GO** if 3+ self-serve retailer applications received |

[[GTM-Hub]] · [[cli-market-prd-v2]]
