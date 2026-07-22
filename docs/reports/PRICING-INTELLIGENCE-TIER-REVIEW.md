# Revisión de pricing: Inteligencia de Mercado (Inflación y Costo de Vida)

**Para:** Producto / Pricing  
**De:** Análisis estratégico (Data/AI + Negocio + Revenue)  
**Fecha:** 2026-07-21  
**Estrategia canónica:** `docs/🚀_growth_engine/pricing-strategy.md` (capas Build · Procure · Intelligence)  
**Decisión de marco:** *Value-Metric Realignment con fence de capas* — no “subir 9 tools de Base a Pro”.

---

## 1. Insight

El catálogo de CLI Market está monetizado al revés: la inteligencia de mayor valor (inflación, costo de vida, scores de mercado, dashboard de confiabilidad — 9 tools) es tier Base/gratis, mientras que Pro (17 tools) es casi puro transaccional de consumidor (carrito, checkout, alertas, favoritos). Solo 1 de 54 tools es Enterprise (`procurement_bulk`).

**Se está cobrando por lo commoditizado y regalando lo diferenciado.**

Eso choca con la propia estrategia de producto: Intelligence / Price Pulse ya está valuado a **$300–500/mes**. Si el fence manda todo el pack de datos a **Pro $39**, se **infravalora el moat** y se **canibaliza** el SKU de data.

---

## 2. Palanca

No es “mover de Base a Pro”. Es **asignar cada tool a la capa de ingreso del job-to-be-done**:

| Capa | Precio | Job | Qué debe vivir ahí |
|------|--------|-----|--------------------|
| **Free teaser** | $0 | “¿Existe la data?” | 1 país, headline limitado, sin export/dashboard |
| **Build Pro** | $39/mes | Agente en producción | Cart, checkout, alerts; señales *operativas* livianas |
| **Intelligence** | $300–500/mes | Visibilidad / estrategia / desk | Inflación, scores, dashboard, scorecard, brief completo, export |
| **Enterprise** | A medida | Feeds, bulk, SLA | `procurement_bulk`, volúmenes, multi-tenant |

El comprador B2B/procurement (segundo perfil por superficie de tools) hoy consume **gratis** lo que más le sirve para decidir. El ARPU no despega porque **no hay fence en el valor de decisión**, no porque falte un skill de carrito.

---

## 3. Decisión propuesta

**Congelar** skills de consumidor — ya sobre-cubierto (≈27/54 tools, 50%, bajo ticket, alta comoditización frente a apps de super).

**Sí:**

1. **Empaquetar** las tools de inflación/costo de vida como **un producto Market Intelligence** (composite), vendido en la capa **Intelligence $300–500**, no como 6 endpoints sueltos en Base ni como “todo en Pro $39”.
2. **Cercar** scores / dashboard / scorecard fuera de Base; destino de **pago de data** (Intelligence), no de carrito.
3. **Wirear** `market_whoami` como chequeo de sesión/tier al inicio de flujos Pro / Intelligence / Enterprise (hoy huérfano; “HTTP errors / tool not found” en skills suelen ser 401/403 disfrazados).
4. **Dejar Free real pero angosto** (1 país, sin export, sin dashboard) para no matar el funnel.

**No:**

- Subir el pack completo de inteligencia a Pro $39 como fin de juego.
- Seguir construyendo API sin dueño de caso de uso.

---

## 4. Matriz de tools — capa destino

Fila filtrada (categoría inflación / costo de vida + trust de mercado).  
**Tier propuesto en código** se alinea a la **capa de producto**, no a un único flag “Pro”.

| Tool | Tier actual | Capa destino | Acceso recomendado | Notas |
|------|-------------|--------------|--------------------|--------|
| `market_intel_brief` | Base | **Free teaser + Intelligence** | Free: recorte (1 país, sin series largas). Full → Intelligence | Composite preferido: un outcome “estado del mercado” |
| `market_inflation` | Base | **Intelligence** (teaser Free opcional) | Free: delta 7d 1 país. Full multi-ventana/export → Intelligence | No va a Pro $39 como pack completo |
| `market_inflation_report` | Base | **Intelligence** | Solo Intelligence+ | Decisión de mesa / desk |
| `market_affordability` | Base | **Intelligence** | Solo Intelligence+ | Costo de vida / presión social |
| `market_informal_signal` | Base | **Intelligence** | Solo Intelligence+ | Señal diferenciada, no commodity |
| `market_indicators` | Base (legacy) | **Intelligence** / deprecar hacia brief | Preferir `intel_brief` compuesto | Catálogo ya marca deprecados hacia brief |
| `market_scores` | Base | **Intelligence** | Solo Intelligence+ | Insumo de decisión mayorista; no gratis |
| `market_dashboard` | Base | **Intelligence** | Solo Intelligence+ | Sin dashboard en Free |
| `market_retailer_scorecard` | Base | **Intelligence** | Solo Intelligence+ | Confianza/cobertura de retailer |
| `market_procurement_signal` | (según catálogo) | **Build Pro** (light) / **Intelligence** (full) | Pro: timing acotado a flujo de compra. Full hist/export → Intelligence | Evita regalar desk en Free |
| `market_procurement_bulk` | Enterprise | **Enterprise** | Enterprise | Mantener; único Enterprise claro |
| `market_whoami` | Base (huérfano) | **Todas las capas (gate)** | Siempre disponible | Chequeo obligatorio pre-tools de pago |

### Bundles de venta (antes de vender endpoints)

| Bundle SKU | Incluye (lógica de valor) | Capa |
|------------|---------------------------|------|
| **Market Intelligence Core** | Composite: inflación + affordability + informal + indicators + brief | Intelligence Pilot S–L |
| **Market Trust / Coverage** | scores + dashboard + retailer_scorecard | Intelligence |
| **Enterprise Bulk** | procurement_bulk + límites/feeds/SLA | Enterprise |

**Producto antes de precio:** una llamada compuesta que responda “¿cómo está el mercado?” — hoy 6 formas distintas son fricción, no profundidad.

---

## 5. Plan de migración 30–60 días (sin canibalizar Pilot $300–500)

### Fase 0 — Ahora (días 0–7): hygiene + baseline

| Acción | Dueño | Output |
|--------|--------|--------|
| Baseline 14–30d: calls por tool × cuenta × tier × país | Data / Observatory | ¿Demanda latente o dead inventory? |
| Wire `market_whoami` + mensajes de upgrade (no 404 genérico) en skills Pro/Ent/Intel | Eng skills | Auth legible; cohortes medibles |
| Anunciar internamente fence de capa (no “todo a Pro”) | Producto / Pricing | Alineación GTM + eng |
| Congelar roadmap de skills consumidor | Producto | Capacidad a composite Intelligence |

**Go/no-go de reprice:** si las 9 tools no se usan ni gratis → el problema es descubrimiento/producto, no tier. No cerrar el fence a ciegas.

### Fase 1 — Días 7–30: teaser Free + soft fence

| Acción | Dueño | Output |
|--------|--------|--------|
| Spec Free teaser: 1 país, headline/`intel_brief` recortado, sin export/dashboard/scorecard | Producto | Spec implementable |
| Soft fence en API/MCP: tools de decisión devuelven upgrade CTA hacia **Intelligence** (no solo “pasa a Pro $39”) | Core / billing | Copy de capa correcto |
| Grandfather 30–60d cuentas con uso real de intel en Base | Revenue | Menos shock; lista de upgrade a Pilot S |
| Composite v1 (`market_intel_brief` o wrapper skill) como **única** superficie de marketing del pack | Producto + eng | 1 outcome vendible |

### Fase 2 — Días 30–60: hard fence + GTM

| Acción | Dueño | Output |
|--------|--------|--------|
| Hard fence: scores, dashboard, scorecard, report completo, affordability, informal → capa Intelligence | Core | Alineado a $300–500 |
| Build Pro retiene transaccional + señales operativas light | Core | Pro sigue siendo job de agente |
| GTM: canal fintech/comercio exterior → Pilot $300; PyPI/MCP → Pro $39 sin prometer Bloomberg | Content / GTM | Sin canibalización de mensaje |
| Revisar KPIs (abajo); ajustar fence si DAU teaser cae sin conversion | Pricing | Iteración data-driven |

### Checklist anti-canibalización

- [ ] Ningún CTA de tool intel dice solo “upgrade to Pro $39” si el valor es desk/datos  
- [ ] Landing Intelligence lista el pack (Core + Trust); Pro no lista dashboard/scores completos  
- [ ] Free mantiene un teaser usable (funnel vivo)  
- [ ] Grandfather documentado antes del hard fence  
- [ ] Skills devuelven upgrade path a **Intelligence** cuando el token es Free/Pro sin entitlement de data  

Referencia de release multi-repo si hay cambio de billing/tiers: `ops/PRICING-CHANGE-CHECKLIST.md` · orden **core → backend → world**.

---

## 6. KPIs

| KPI | Para qué | Señal |
|-----|----------|--------|
| % llamadas tools paid (Pro **+** Intelligence **+** Ent) / total | ¿El fence mueve tráfico a paid? | Debe subir post-fence si hay demanda |
| Uso de las 9 tools **antes** del fence (baseline) | ¿Hay demanda latente? | Si ≈0, no repricear a ciegas |
| Conversion Free → Intelligence en cuentas con ≥N calls intel/mes | ¿El teaser convierte? | Meta de negocio del fence |
| ARPU y mix por cohorte (builder / procure / intel) | ¿Sube B2B data o solo fricción? | ARPU intel es el norte |
| Attach rate Intelligence en cuentas con `procurement_*` | ¿El buyer B2B paga data? | Cierre del gap de ARPU B2B |
| Churn / drop de DAU en tools teaser post-fence | ¿Matamos el funnel? | Si cae sin paid ↑, fence agresivo |
| Upgrade CTA hit-rate post-403 de tool intel | ¿whoami/gate monetiza? | Hygiene de revenue |

**Interpretación:**

- Sube % paid **y** ARPU intel → el problema era el tier/fence.  
- No sube uso ni paid → no era pricing; era product-market / GTM / wiring.  
- Cae uso free y no sube paid → free demasiado muerto o hard fence prematuro.

---

## 7. Trade-off

Subir de capa lo que hoy es gratis frena a PyMEs/devs que prueban sin pagar.

**Mitigación:** Free **real pero angosto** (1 país, sin export, sin dashboard/scorecard). Pro $39 no sustituye Intelligence: es infra de agente, no Bloomberg de góndola.

---

## 8. Riesgo estructural (gobierno de tools)

7 de 54 tools (≈13%) sin skill que las dispare. 3 admin (OK). 4 (`ask`, `enrich`, `stores`, `whoami`) señalan **API-first sin caso de uso**.

**Regla de gobierno:** ningún tool sale a prod sin:

1. Dueño de caso de uso  
2. Skill o flujo documentado que lo dispare  
3. Métrica de uso o deprecation plan  

Sin esa regla, el backlog de tools huérfanos crece cada release. Mitigación = la regla, no más parches reactivos.

---

## 9. Insumo para la conversación de producto/pricing

**Frase de cierre:**

> El ARPU B2B no despega porque el catálogo vende checkout a $39 y regala la capa que el documento de pricing ya valora a $300–500. No hacen falta más tools de consumidor: hacen falta **fence de Intelligence**, **un SKU compuesto**, y **auth de tier** para que el pago siga al valor de decisión, no al carrito.

**Próximos 48 h:**

1. Aprobar esta matriz de **capa destino** (no la lista Base→Pro del borrador previo).  
2. Correr baseline de uso de las 9 tools.  
3. Patch `whoami` + upgrade path en skills.  
4. Spec del Free teaser + composite Intelligence v1.

---

## Referencias

- Estrategia de capas: `docs/🚀_growth_engine/pricing-strategy.md`  
- Catálogo tools: `docs/reports/TOOLS_CATALOG_COMPLETO.txt`  
- Checklist de cambio de pricing: `ops/PRICING-CHANGE-CHECKLIST.md`  
- Intelligence GTM: landing `intelligence-pilot` / canal Comercio Exterior · Fintech → Pilot $300  
