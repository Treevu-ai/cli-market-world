---
title: "Treevu-ai/procure-copilot: Procurement control plane for LatAm teams — approval workflows, budget control, checkout on CLI Market infra. Powered by market_optimize_purchase."
source: "https://github.com/Treevu-ai/procure-copilot"
author:
published:
created: 2026-07-15
description: "Procurement control plane for LatAm teams — approval workflows, budget control, checkout on CLI Market infra. Powered by market_optimize_purchase. - Treevu-ai/procure-copilot"
tags:
  - "clippings"
---
[![PROCURE COPILOT](https://github.com/Treevu-ai/procure-copilot/raw/main/assets/readme-hero.gif)](https://github.com/Treevu-ai/procure-copilot/blob/main/assets/readme-hero.gif)

## Procure Copilot

**Procurement inteligente para empresas en América Latina**

Procure Copilot es el control plane de compras sobre [CLI Market](https://cli-market.dev/): busca, compara y optimiza compras empresariales en **40 retailers verificados** (80 en catálogo) en **8 países**, con flujo de aprobación, data-gate y checkout integrado.

**Prod:** [https://procure-copilot.contacto-8e4.workers.dev](https://procure-copilot.contacto-8e4.workers.dev/)

---

## Qué resuelve

| Sin Procure | Con Procure |
| --- | --- |
| Cotizar por WhatsApp/email | Agente compara en segundos |
| Transcribir precios a Excel | Precios normalizados por kg/L |
| Sin verificación de stock | Stock y delivery antes de recomendar |
| Compras sin auditoría | run → approve → checkout trazable |
| Datos desactualizados | Data-gate bloquea si el moat está stale |

## Capacidades

- Búsqueda y comparación multi-retailer vía CLI Market API
- Optimización de canasta (`POST /v1/basket/compare`)
- Flujo de aprobación interno (planes Pro+)
- Verificación de stock y estimación de delivery
- Alertas de precio, historial y reporte de ahorro
- Checkout PayPal / Yape tras aprobación explícita
- Dashboard de procurement y analytics de uso (D1)

## Planes

| Plan | Precio | Ideal para |
| --- | --- | --- |
| **Starter** | $29/mes | Restaurantes, un local, 20 procurement/mes |
| **Pro** | $79/mes | Hoteles, constructoras — aprobaciones + stock + 12m historial |
| **Builder** | $149/mes | Multi-país, alto volumen, integraciones |
| **Enterprise** | A medida | SLA, soporte dedicado, cobertura completa |

Detalle en `lib/procure-content.ts` y `lib/plans.ts`.

## Flujo de compra

```
POST /api/procurement/run     → canasta + quotes + ahorro
        ↓ (si monto > umbral y plan Pro+)
POST /api/procurement/approve → gerente aprueba/rechaza
        ↓
POST /api/procurement/checkout → carrito CLI Market + URL de pago
```

Ver `AGENTS.md` para headers (`x-plan`, `x-budget-id`, `x-approver-id`) y reglas de data-gate.

## Tech stack

- **App:** Next.js 16 + TypeScript + Tailwind 4
- **Deploy:** Cloudflare Workers (OpenNext)
- **Persistencia:** Cloudflare D1 — procurements, approvals, budgets
- **Datos retail:** CLI Market REST (`lib/cli-market.ts`)

## Getting started

### Prerequisites

- Node.js 18+
- API key CLI Market (`POST /auth/register`)

### Installation

```
git clone https://github.com/Treevu-ai/procure-copilot.git
cd procure-copilot
npm install
cp .env.example .env.local
```

`.env.local`:

```
CLI_MARKET_API_URL=https://cli-market-api.fly.dev
CLI_MARKET_API_KEY=sk-your-api-key-here
DEMO_MODE=false
```

### Development

```
npm run dev          # http://localhost:3000
npm run build        # producción (--webpack requerido para CF)
npm run lint
```

### Deploy y verificación

```
npm run db:migrate:remote   # primera vez con tablas nuevas
npm run cf-deploy           # Cloudflare Workers
npm run smoke               # run → approve → checkout en prod — ver ops/SMOKE-SETUP.md
npm run smoke:hotel         # alias — canasta ICP B hotel
npm run demo:gif            # regenerar demo animada
npm run procure-daily       # resumen Slack (requiere PROCUREMENT_WEBHOOK_SECRET)
```

## Scripts

| Command | Description |
| --- | --- |
| `npm run dev` | Servidor de desarrollo |
| `npm run build` | Build producción |
| `npm run cf-deploy` | Deploy a Cloudflare Workers |
| `npm run smoke` | Smoke E2E prod — **requires** `PROCURE_E2E_SECRET` ([setup](https://github.com/Treevu-ai/procure-copilot/blob/main/ops/SMOKE-SETUP.md)) |
| `npm run smoke:doctor` | Diagnose local + Workers E2E secret (run this first) |
| `npm run smoke:hotel` | Igual que smoke — canasta hotel Tier A/B |
| `npm run demo:gif` | Genera `public/demo.gif` |
| `npm run procure-daily` | Trigger daily summary Slack |

## API Procure

| Endpoint | Uso |
| --- | --- |
| `POST /api/procurement/run` | Ejecutar agente de procurement |
| `POST /api/procurement/approve` | Aprobar/rechazar pending |
| `GET /api/procurement/approve?id=` | Estado de aprobación |
| `POST /api/procurement/checkout` | Checkout CLI Market |
| `POST /api/procurement/alert` | Alertas de precio |

## Integración CLI Market

- `POST /products/search` — búsqueda multi-tienda
- `POST /products/compare` — comparación unitaria
- `POST /v1/basket/compare` — canasta optimizada
- `GET /dashboard/data` — data-gate / moat health
- `POST /v1/alerts` — alertas Pro

Docs: [https://cli-market-api.fly.dev/docs](https://cli-market-api.fly.dev/docs)

## Agentes y GTM

- `AGENTS.md` — stack, endpoints, tabla de agentes para cierre comercial
- `.cursor/skills/procure-with-cli-market/SKILL.md` — workflow MCP + API
- Outbound: `cli-market-content/outbound/procure-sequences.md`
- Demo script: `cli-market-world/docs/agents/contexts/sales-engineer-context.md`

## Ecosistema

| Repo | Rol |
| --- | --- |
| [cli-market-world](https://github.com/Treevu-ai/cli-market-world) | API, moat, ops |
| [cli-market-content](https://github.com/Treevu-ai/cli-market-content) | GTM, outbound, Price Pulse |
| [cli-market-core](https://github.com/Treevu-ai/cli-market-core) | SDK `pip install cli-market` |

## License

---

**Built by Treevu-ai** — procurement con datos de góndola reales en LATAM