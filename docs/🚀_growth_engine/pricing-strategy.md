# Estrategia de pricing — ecosistema CLI Market

**Última actualización:** 2026-07-18

Tres capas complementarias. Cada capa tiene un comprador, un job-to-be-done y un precio. No compiten en el mismo presupuesto. En una economía de baja digitalización, CLI Market no se vende como una app de ahorro (B2C), sino como **infraestructura de arbitraje y formalización (B2B/Agents)**.

## Promesas de marca (GTM CLI Market–first)

| Capa | Una línea | Positioning (Anti-B2C) |
|------|-----------|-------------------------|
| **CLI Market (hub)** | Datos y tools de góndola formal LATAM para agentes y equipos. | **Infrastructure.** El usuario final es un agente de IA o un builder. |
| **Procure (spoke)** | La app de compras que corre encima de CLI Market. | **Operations.** Para humanos que gestionan abastecimiento. |
| **Intelligence** | El "Bloomberg" de la góndola LATAM. | **Data.** Para profesionales de Revenue, Growth y Comercio Exterior. |

**Puente:** «Procure es cómo un operador de compras usa CLI Market sin programar.»  
Canónico GTM: `cli-market-content/strategy/gtm-cli-market-first.md`.

## Regla de oro

| Si el buyer… | Vende | Por qué |
|--------------|-------|---------|
| Construye agentes o productos con API/MCP | **CLI Market Build** (Pro $39) | El valor está en la integración, no en el ahorro personal. |
| Opera compras (gerente, comprador, CFO) | **Procure Copilot** ($29–149/mes) | Necesita gobernanza y UI, no una terminal. |
| Analiza inflación, spreads, export/import | **Intelligence** ($300–500/mes) | Compra "visibilidad" y "Golden Records" sobre el caos del mercado. |

**Procure incluye infraestructura CLI Market** — el operador de compras no necesita suscripción API adicional.

---

## Capa 1 — CLI Market (infraestructura)

**ICP:** AI Agent Builders, developers, integradores de última milla.

| Plan | Precio | Job | Realidad en Economía Informal |
|------|--------|-----|------------------------------|
| Free | **$0** | Experimentación | Para devs validando que la data existe. |
| Starter | **$9/mes** | Micro-agentes | *Deprecated* o solo para tareas de discovery puntual. |
| Pro | **$39/mes** | Agente de Producción | El estándar para integrar checkout y arbitrage real. |
| Enterprise | A medida | Plataformas | Feeds masivos para retail-tech. |

**Nota sobre el B2C:** En una economía informal, el costo de oportunidad de usar una CLI es infinito para un consumidor. CLI Market Pro solo tiene sentido para quien **vende una solución** encima (ej. un bot de WhatsApp para bodegas).

---

## Capa 2 — Procure Copilot (aplicación)

**ICP:** Restaurantes, hoteles, agro, constructoras — equipos que compran, no que programan. Es el puente de formalización para negocios que operan en la informalidad.

| Plan | Precio | Job | Incluye | No incluye |
|------|--------|-----|---------|------------|
| Starter | **$29/mes** | Dejar WhatsApp/Excel — comparar y decidir | 20 procurement/mes, compare 3 retailers | **Checkout**, aprobaciones, stock, delivery |
| Pro | **$79/mes** | Gobernar compra con trazabilidad | Aprobaciones, stock, delivery, **checkout**, alertas | Integraciones custom |
| Builder | **$149/mes** | Multi-país, alto volumen | 1k procurement/mes, integraciones | — |
| Enterprise | A medida | Corporativo LATAM | Ilimitado, SLA 99.9% | — |

---

## Capa 3 — Intelligence / Price Pulse (datos)

**ICP:** Estrategas de Revenue, Growth, Innovación, Marketing, Exportadores e Importadores.

| Tier | Precio | Job-to-be-Done |
|------|--------|----------------|
| Pilot S | $300/mes | **Visibilidad.** Entender el mercado real fuera de los reportes oficiales. |
| Pilot M | $400/mes | **Estrategia.** Benchmarking dinámico para pricing y lanzamientos. |
| Pilot L | $500/mes | **Operación Global.** Arbitraje de precios transfronterizo (import/export). |

**Activos Críticos:**
- **Golden Records:** +70,000 entidades normalizadas (Entity Resolution propia).
- **Cobertura:** 82 retailers en 9 países (37 verificados activos).
- **Update:** Refresco cada 4 horas desde la góndola digital.

**Valor para Exportadores:** Saber el precio real de góndola de su competencia en Lima, Buenos Aires o Madrid cada 4 horas, mapeando SKUs específicos mediante Golden Records para comparativas exactas de competitividad en destino.

---

## Matriz de decisión (ventas)

```
¿Escribe código o configura MCP?
  Sí → CLI Market Build (Free · Pro $39)
  No → ¿Ejecuta compras con aprobación gerente?
         Sí → Procure Pro $79+
         No → ¿Solo quiere comparar precios sin pagar?
                Sí → Procure Starter $29
                No → ¿Solo quiere datos para modelos/reportes/export?
                       Sí → Intelligence $300+
```

---

## Mensajes por canal GTM

| Canal | Producto | CTA | Evitar |
|-------|----------|-----|--------|
| PyPI, HN, DEV, MCP | CLI Market | `pip install` · Pro $39 | Procure, "ahorro personal" |
| LinkedIn empresa, outbound compras | Procure | Demo · Starter $29 / Pro $79 | `pip install` en mismo post |
| Comercio Exterior, Fintech | Intelligence | Piloto $300 | Checkout, dashboard operativo |

---

## Referencias

- Planes Procure (código): `../procure-copilot/lib/plans.ts`
- Planes CLI Market: `README.md`
- Intelligence: `landing/public/intelligence-pilot-es.md`
