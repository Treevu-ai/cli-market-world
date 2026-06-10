# Estrategia de pricing — ecosistema CLI Market

**Última actualización:** 2026-06-08

Tres capas complementarias. Cada capa tiene un comprador, un job-to-be-done y un precio. No compiten en el mismo presupuesto.

## Regla de oro

| Si el buyer… | Vende | No vender |
|--------------|-------|-----------|
| Construye agentes o productos con API/MCP | **CLI Market Build** (Free / Starter $24 / Pro $39 / Pro Founding $29) | Procure |
| Opera compras (gerente, comprador, CFO) | **Procure Copilot** ($29–149/mes) | CLI Market Pro por separado |
| Analiza inflación, spreads, canasta (sin ejecutar compra) | **Intelligence** ($300–500/mes) | Procure Starter ni CLI Market Pro |

**Procure incluye infraestructura CLI Market** — el operador de compras no necesita suscripción API adicional.

---

## Capa 1 — CLI Market (infraestructura)

**ICP:** AI Agent Builders, developers, integradores.

| Plan | Precio | Job | Incluye | No incluye |
|------|--------|-----|---------|------------|
| Free | $0 | Probar API | Search, compare, 1k req/día, MCP default | Checkout, export, alertas |
| Starter | **$24/mes** | Export y alertas sin checkout | 5k req/día, 3 claves API, export CSV, 3 alertas | Checkout retail |
| Pro | **$39/mes** | Embeber comercio en *tu* agente/producto | MCP completo, checkout, alertas, export | UI procurement, aprobaciones, auditoría D1 |
| Pro Founding | **$29/mes** (100 plazas) | Mismo que Pro con precio bloqueado | Igual que Pro · promo `founding100` | — |
| Enterprise | A medida | Plataformas, alto volumen | SLA, feeds, white-label | — |

**Checkout Pro** = para quien integra `market_checkout` en software propio, no para equipos de compras que deberían usar Procure.

---

## Capa 2 — Procure Copilot (aplicación)

**ICP:** Restaurantes, hoteles, agro, constructoras — equipos que compran, no que programan.

| Plan | Precio | Job | Incluye | No incluye |
|------|--------|-----|---------|------------|
| Starter | **$29/mes** | Dejar WhatsApp/Excel — comparar y decidir | 20 procurement/mes, compare 3 retailers | **Checkout**, aprobaciones, stock, delivery |
| Pro | **$79/mes** | Gobernar compra con trazabilidad | Aprobaciones, stock, delivery, **checkout**, alertas | Integraciones custom |
| Builder | **$149/mes** | Multi-país, alto volumen | 1k procurement/mes, integraciones | — |
| Enterprise | A medida | Corporativo LATAM | Ilimitado, SLA 99.9% | — |

**Anti-canibalización técnica:** checkout bloqueado en API y UI para Starter/Free. Solo Pro+ ejecuta pago.

**Anti-canibalización comercial:** copy explícito “infra CLI Market incluida” — no sumar $39 + $79.

---

## Capa 3 — Intelligence / Price Pulse (datos)

**ICP:** Pricing, trade marketing, fintech, consultoras.

| Tier | Precio | Entrega |
|------|--------|---------|
| Pilot S | $300/mes | Export semanal, 1 país |
| Pilot M | $400/mes | API + export, 1–2 países |
| Pilot L | $500/mes | Multi-país, SLA 48h |

No compite con Procure (ejecución) ni con CLI Market Pro (API self-serve). Upsell natural: Intelligence → Procure cuando el cliente quiera *actuar* sobre los datos.

---

## Matriz de decisión (ventas)

```
¿Escribe código o configura MCP?
  Sí → CLI Market Build (Free · Starter $24 · Pro $39 · Pro Founding $29)
  No → ¿Ejecuta compras con aprobación gerente?
         Sí → Procure Pro $79+
         No → ¿Solo quiere comparar precios sin pagar?
                Sí → Procure Starter $29
                No → ¿Solo quiere datos para modelos/reportes?
                       Sí → Intelligence $300+
```

---

## Mensajes por canal GTM

| Canal | Producto | CTA | Evitar |
|-------|----------|-----|--------|
| PyPI, HN, DEV, MCP | CLI Market | `pip install` · Pro $39 | Procure, restaurantes |
| LinkedIn empresa, outbound compras | Procure | Demo · Starter $29 / Pro $79 | `pip install` en mismo post |
| Fintech, consultoras | Intelligence | Piloto $300 | Checkout, dashboard |

---

## Métricas de canibalización

Monitorear mensualmente:

1. **Pro CLI Market con checkout** sin `procurementId` / webhook Procure (builders legítimos vs operadores mal segmentados).
2. **Leads Procure** que preguntan por API key separada (fricción de messaging).
3. **Starter Procure → Pro** upgrade rate (debe ser el funnel principal en horeca).

---

## Superficie comercial unificada (Fase A)

- **Pricing Procure:** `https://cli-market.dev/#procure` — misma landing que Build e Intelligence.
- **App Procure:** Worker en `/dashboard` — sin landing de marketing propia (`/procure` redirige a `#procure`).
- **Checkout Procure:** `POST /billing/procure-subscribe` en Railway; activación vía webhook PayPal (`procure_starter` / `procure_pro` / `procure_builder`).

## Referencias

- Planes Procure (código): `../procure-copilot/lib/plans.ts`, `landing/lib/procurePlans.ts`
- Planes CLI Market: `README.md`, `landing/public/llms.txt`
- Intelligence: `landing/public/intelligence-pilot-es.md`
- Demo SE: `docs/agents/contexts/sales-engineer-context.md`