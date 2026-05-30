# CLI Market Intelligence — Piloto comercial

**Versión:** 2026-05-30 · **Confidencial — uso en propuestas B2B**

---

## 1. Resumen ejecutivo

CLI Market Intelligence entrega **precios de góndola verificables** de retailers en LATAM: spreads, inflación por línea, canasta básica comparable y capa de calidad (clean / flagged / citable). Actualización cada **8 horas** sobre **30 retailers verificados** en **8 países**.

**Piloto recomendado:** 30–90 días · **USD 300–500/mes** según país, categorías y profundidad histórica.

**Ancla de valor:** bureaus y herramientas legacy suelen cobrar **USD 500+/mes** (o contratos anuales de cinco cifras) por menos cobertura regional, datos con retraso institucional y sin filtros de calidad explícitos.

---

## 2. Problema que resolvemos

| Dolor | Situación típica | Con Intelligence |
|-------|------------------|------------------|
| Datos tardíos | INEI / DANE / fuentes oficiales con 30–45 días de retraso | Snapshots cada 8 h desde góndola online |
| Costo alto | Nielsen, panel propio, scraping manual | Piloto desde USD 300/mes |
| Comparabilidad | Precios por unidad distinta (kg/L/pack) | Normalización por kg/L + canasta con reglas explícitas |
| Confianza | Outliers y promos distorsionan decisiones | Funnel clean → flagged → citable documentado |
| Cobertura LATAM | Proveedores globales débiles en PE/CO/CL secundario | 8 países, 6 líneas, VTEX + Shopify + Magento |

---

## 3. Qué incluye el piloto

### Datos y métricas

- **Spreads** — mismo SKU / seed comparable entre tiendas (ratio min–max documentado)
- **Inflación** — variación por línea y país (ventana configurable, ej. 7 / 30 días)
- **Canasta básica** — total comparable cuando ≥60% ítems encontrados por tienda
- **Inventario indexado** — 43.000+ precios verificados (crece con collector)
- **Freshness** — % precios &lt;24 h y antigüedad del último snapshot

### Capa de calidad

- **Clean** — apto para comparación automatizada
- **Flagged** — descuentos sospechosos, outliers, reglas documentadas
- **Citable** — subset publicable con trazabilidad

### Entrega

- Export **CSV / JSON** (series históricas según alcance del piloto)
- Acceso **API dedicada** (lectura; límites acordados en SOW)
- **Onboarding en 48 h** — país, categorías, tiendas objetivo
- Revisión quincenal de cobertura y calidad durante el piloto

### Alcance geográfico inicial (piloto)

Perú y/o Colombia prioritarios; otros países LATAM bajo demanda (AR, MX, CL, BR).

---

## 4. Qué NO incluye (este trimestre)

| Excluido | Alternativa |
|----------|-------------|
| Checkout autónomo para agentes | Producto **Build** (Pro) — roadmap, no foco comercial Q2 |
| Listado de tienda para GEO | **Puerta B** — gratis, separado de Intelligence |
| Scraping ad hoc / fuentes no acordadas | Solo catálogo activo + reglas del collector |
| Garantía legal tipo Nielsen | Piloto con métricas de freshness/cobertura verificables en dashboard |

---

## 5. Tres productos (sin mezclar mensajes)

| Puerta | Audiencia | Precio | Promesa |
|--------|-----------|--------|---------|
| **A · Build** | Devs, agentes IA | Free / Pro USD 49 | API, MCP, export técnico |
| **B · Retailer listing** | E-commerce VTEX/Shopify/Magento | Gratis | Aparecer en búsquedas de agentes |
| **C · Intelligence** | Pricing, trade, fintech, consultoras | Piloto USD 300–500/mes | Datos comerciales con calidad |

---

## 6. Estructura del piloto (30–90 días)

### Semana 0 — Kickoff (48 h)

1. Definir país, líneas (super, farmacia, electro…), tiendas competidoras
2. Entregar credenciales API + muestra CSV (7 días histórico si aplica)
3. Alinear KPIs: freshness mínima, ítems canasta, spreads de interés

### Semanas 1–4 — Validación

- Entregas semanales de export o acceso batch
- Revisión de flagged vs clean con su equipo
- Ajuste de seeds / categorías si hay gaps de cobertura

### Semanas 5–12 — Escala o cierre

- Decisión: contrato Intelligence mensual, Enterprise a medida, o fin de piloto
- Documento de resultados: cobertura alcanzada, freshness media, casos de uso validados

---

## 7. Pricing piloto

| Tier | Precio | Perfil |
|------|--------|--------|
| **Pilot S** | USD 300/mes | 1 país · 1–2 líneas · 30 d histórico · export semanal |
| **Pilot M** | USD 400/mes | 1–2 países · 3 líneas · 60 d histórico · API + export |
| **Pilot L** | USD 500/mes | Multi-país LATAM · canasta + spreads + 90 d · SLA email 48 h |

Precio final según volumen de SKUs/seeds, frecuencia de export y requisitos de SLA. Enterprise a medida post-piloto.

---

## 8. Prueba social (formato case study)

**Fintech — credit scoring (Perú)**  
Necesidad: canasta básica en tiempo útil vs INEI (45 d).  
Resultado referencial: 13.000+ precios indexados · time-to-data 1 día vs 45 · costo orden de magnitud menor vs alternativas anuales.  
*(Detalle completo: `landing/public/case-studies.md`)*

---

## 9. Stack y confianza

- Collector programado cada **8 h** contra APIs públicas / acordadas
- Dashboard de moat (freshness, cobertura, salud por tienda) — demo en vivo bajo NDA si aplica
- Licencia de datos: ver `legal/Data_License_Agreement.md`
- Sin acceso a PII de clientes finales de retailers

---

## 10. Próximo paso

1. Complete el formulario en [cli-market.dev/#contact-intelligence](https://cli-market.dev/#contact-intelligence)  
   **o** escriba a **hello@cli-market.dev** con asunto `Intelligence Pilot`
2. Indique: país · categorías · equipo (pricing / trade / data) · ventana histórica deseada
3. Propuesta de piloto en **48 h hábiles**

**One-pager público:** [intelligence-pilot-es.md](https://cli-market.dev/intelligence-pilot-es.md)

---

*CLI Market · Infraestructura de comercio y precios para LATAM · MIT (Build) · Data License (Intelligence)*
