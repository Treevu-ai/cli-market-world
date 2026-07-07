---
title: PRD — Brand Intelligence v1
tags:
  - product
  - prd
  - brand-intelligence
  - trade-marketing
status: v1.0 — backend/frontend/tests/email-alert/NDA/metodología construidos; falta subdominio + onboardear primera agencia piloto
owner: Ricardo Cuba
created: 2026-07-07
repos: cli-market-world, cli-market-core, cli-market-backend
related:
  - docs/pricing-strategy.md
  - docs/DATA-MOAT-INDICATORS.md
  - docs/methodology.md
  - docs/BRAND.md
  - routers/analytics.py
  - routers/data_v1.py
---

# PRD — Brand Intelligence v1

## TL;DR

Las marcas CPG en Perú (Gloria, Alicorp, Laive, San Fernando, Backus) hoy no saben si sus SKUs
están al precio sugerido en góndola digital, ni cuándo los retailers o competidores activan promos
que los desplazan. Nielsen cobra $30K–$80K/año con datos mensuales y rezago de 3-4 semanas.

CLI Market ya tiene los datos: 50K+ precios, refresh 8h, 41 retailers verificados, `brand` y
`category` indexados en `price_snapshots`. El activo existe. Brand Intelligence es empaquetarlo
para el comprador correcto: el equipo de trade marketing o pricing de una marca CPG.

**Propuesta de valor en una línea:**
> Inteligencia de precios de tus SKUs y tus competidores en góndola digital peruana — en tiempo
> real, sin paneles de Nielsen, desde $500/mes.

---

## 1. Problema

### 1.1 El dolor del comprador

| Persona | Empresa | Pain point específico |
|---------|---------|----------------------|
| Gerente de Trade Marketing | Alicorp, Gloria, San Fernando | No sabe si sus SKUs están al PVP sugerido en cada cadena esta semana |
| Analista de Pricing | Unilever PE, P&G PE | No detecta en tiempo real cuándo un competidor baja precio o activa promo |
| Brand Manager | Laive, Backus, Nestlé PE | No puede cuantificar la "dispersión de marca" (cuánto varía su propio precio entre cadenas) |
| Agencia de Trade Marketing | Pragma, Neo Consulting, Summa | No tiene insumo de datos propio para diferenciarse de otras agencias en pitches |
| Category Manager | Cencosud (Wong/Metro), Intercorp (PV) | No tiene vista rápida de qué marcas tienen pricing agresivo esta semana en su propia categoría |

### 1.2 Por qué las alternativas no resuelven

| Alternativa | Problema |
|-------------|----------|
| Nielsen Retail Measurement | $30-80K/año, datos mensuales, latencia 3-4 semanas, solo cadenas en el panel |
| Kantar Worldpanel | Panel de hogares — mide compra, no precio de góndola |
| Scraping interno | Requiere equipo técnico, mantenimiento constante, no normalizado |
| Monitoreo manual (promotoras en tienda) | No escala, no cubre digital, no comparable cross-cadena |
| Google Shopping | No cubre retailers VTEX peruanos, sin historial, sin normalización por kg/L |

### 1.3 El gap de mercado

Existe un gap nítido entre:
- **Datos oficiales de panel** (caros, lentos, retrospectivos)
- **Nada** (la mayoría de marcas medianas no tienen ningún dato de precios de competidores)

Brand Intelligence v1 vive en ese gap: datos verificados, frecuencia alta, precio accesible para
marcas que no tienen presupuesto Nielsen pero sí necesitan la señal.

---

## 2. Activos técnicos disponibles (sin build nuevo)

Todo lo siguiente ya existe en producción:

| Activo | Endpoint / tabla | Relevancia para Brand Intel |
|--------|-----------------|----------------------------|
| Precios por marca | `GET /analytics/brands?line=supermercados&country=PE` | Top marcas por volumen de snapshots |
| Historial de precios | `GET /analytics/price-history?product_id=X` | Serie temporal por SKU |
| Dispersión cross-tienda | `GET /v1/dispersion` | Spread entre retailers para mismo producto |
| Promo intensity | `indicator_values WHERE key='promo_intensity'` | % SKUs con descuento activo, por línea |
| Price dispersion | `indicator_values WHERE key='price_dispersion'` | CV medio cross-tienda |
| Trending (movers) | `GET /analytics/trending?country=PE&line=supermercados` | SKUs con mayor variación 7d |
| Búsqueda semántica | `market_search` MCP / `POST /v1/search` | Encontrar SKUs de una marca |
| Price snapshots | tabla `price_snapshots` con columnas `brand`, `category`, `store`, `price`, `discount` | Fuente de todo |

**Lo que NO existe y debe construirse para v1:**
1. Endpoint `/v1/brand-monitor` — vista por marca: SKUs propios + competidores en misma categoría
2. UI de Brand Monitor dashboard (Next.js, estilo terminal)
3. Lógica de "alerta de desvío vs PVP sugerido" (requiere que la marca ingrese su PVP)
4. Exportación CSV de brand report
5. Contrato / NDA template (no-cross-sharing entre marcas competidoras)

---

## 3. Producto — Tres SKUs

### SKU A — Brand Monitor Dashboard ($500/mes por marca)

**Job-to-be-done:** el analista de pricing entra cada lunes y en 5 minutos sabe qué pasó con sus
SKUs y sus competidores la semana pasada.

**Tres vistas en el dashboard:**

#### Vista 1 — Mis SKUs (`/brand/[slug]/my-skus`)

| Columna | Dato | Fuente |
|---------|------|--------|
| Producto | Nombre normalizado | `price_snapshots.name` |
| Cadena | Plaza Vea / Metro / Wong | `price_snapshots.store` |
| Precio actual | S/ X.XX | `price_snapshots.price` |
| PVP sugerido | S/ X.XX | Ingresado por la marca (campo editable) |
| Desvío vs PVP | +X% / −X% / ✓ | Calculado |
| Promo activa | Sí / No (% descuento) | `price_snapshots.discount > 0` |
| Última actualización | hace N horas | `price_snapshots.queried_at` |

**Alerta de desvío:** badge rojo si `precio_actual > PVP_sugerido × 1.05` (precio por encima del
sugerido — problema de imagen de marca) o `precio_actual < PVP_sugerido × 0.85` (precio muy bajo
— posible guerra de precios que erosiona margen del canal).

#### Vista 2 — Competidores (`/brand/[slug]/competitors`)

Comparación dentro de la misma categoría (ej: "leche evaporada 410g" de Gloria vs Ideal vs
Nestlé):

| Métrica | Descripción |
|---------|-------------|
| Precio relativo | Mi precio / precio competidor (ratio) — si >1 soy más caro |
| Gap en S/ | Diferencia absoluta en el SKU más comparable |
| Promo frequency | % de los últimos 30 días en que el competidor tuvo descuento activo |
| Price trend | ↑ / ↓ / → en 7d y 30d |

**Regla de no-cross-sharing:** los datos de la marca A no son visibles para la marca B aunque
ambas sean clientes. El query filtra por `brand IN (mi_marca, competidores_declarados)`. Las
marcas competidoras son declaradas por el cliente en onboarding; no se cruzan automáticamente.

#### Vista 3 — Promo Tracker (`/brand/[slug]/promos`)

Historial de activaciones promocionales de mis SKUs y competidores:

- Línea de tiempo: cuándo y dónde se activó descuento
- Intensidad: % de descuento, duración estimada (desde primera hasta última observación con
  `discount > 0` en el mismo `product_id + store`)
- Retail aggression score por cadena: qué tan agresiva es cada cadena con promos en mi categoría

**Datos base:** `price_history` tabla + `promo_intensity` indicator.

---

### SKU B — Category Report mensual ($1.5K/mes)

**Job-to-be-done:** el Gerente de Trade Marketing necesita un PDF de 8 páginas para presentar a
su Gerente Comercial o a la agencia. No tiene tiempo de operar el dashboard.

**Estructura del reporte (8 páginas):**

| Página | Contenido |
|--------|-----------|
| 1 | Portada + resumen ejecutivo (3 bullets: qué subió, qué bajó, qué alerta) |
| 2 | Mis SKUs: precios por cadena, desvío vs PVP sugerido, semáforo |
| 3 | Mapa de competidores: precio relativo, ranking de precio en categoría |
| 4 | Promo tracker: historial de activaciones del mes, duración, cadena |
| 5 | Price dispersion de mi marca vs industria: ¿soy más o menos consistente? |
| 6 | Top movers de la categoría (qué SKUs cambiaron más precio en el mes) |
| 7 | Contexto macro (RPV de la línea, BSI, presión de canasta) |
| 8 | Recomendaciones de acción (3 bullets generados por plantilla) |

**Entrega:** PDF generado automáticamente cada primer lunes del mes, enviado por email.
**Generación:** extensión de `price_pulse_agents.py` con contexto de marca.

---

### SKU C — API de Brand Intel ($800/mes, add-on Pro)

**Job-to-be-done:** la agencia o el equipo técnico de la marca quiere integrar los datos en su
propio dashboard o modelo.

**Endpoint nuevo:** `GET /v1/brand-monitor`

```
Parámetros:
  brand       string   required  Marca a monitorear (ej: "Gloria")
  country     string   required  PE / AR / BR
  competitors string[] optional  Marcas competidoras a incluir
  line        string   optional  supermercados / farmacias / etc.
  days        int      optional  Ventana histórica (default 30, max 90)

Respuesta:
  my_skus[]          Lista de SKUs propios con precio por tienda + desvío
  competitor_skus[]  SKUs de competidores (solo los declarados en onboarding)
  promo_events[]     Activaciones de descuento en el período
  dispersion_score   CV de precio cross-tienda para la marca
  category_rank      Posición de precio relativo en la categoría (1 = más barato)
```

**Autenticación:** API key Pro existente + flag `brand_intel: true` en el perfil del key.
**Rate limit:** 100 req/día (suficiente para polling diario por SKU).

---

## 4. Pricing y anti-canibalización

| SKU | Precio | Ciclo | Entrega |
|-----|--------|-------|---------|
| Brand Monitor Dashboard | $500/mes por marca | Mensual | Self-serve dashboard |
| Category Report PDF | $1.5K/mes | Mensual | Email automático |
| Brand Intel API | $800/mes (add-on) | Mensual | Integración técnica |
| **Piloto de validación** | **$0 por 30 días** | Único | Dashboard + 1 reporte |

**Regla de no-canibalización con Intelligence ($300-500/mes):**
- Intelligence → macro, multi-país, analistas fintech/research, canasta agregada
- Brand Intelligence → micro, por marca, trade marketing, SKU-level
- No mezclar en el mismo post ni en el mismo pitch

**Comparación con Nielsen** (argumento de ventas):
| | Nielsen | Brand Intel CLI Market |
|---|---|---|
| Precio | $30-80K/año | $6K-18K/año |
| Frecuencia | Mensual | Cada 8 horas |
| Latencia | 3-4 semanas | < 24 horas |
| Cobertura retail digital PE | Limitada al panel | 41 retailers VTEX |
| Competidores comparables | Según panel contratado | Cualquier marca indexada |
| Implementación | 3-6 meses | 1 semana (piloto) |

---

## 5. ICP y segmentación de entrada

### Segmento 1 — Entrada más rápida: Agencias de Trade Marketing

**Por qué entrar por agencias primero:**
- Una agencia firma un contrato y activa 3-5 marcas
- El ciclo de venta es 3-6 semanas (vs 3-6 meses para una multinacional)
- La agencia tiene incentivo propio: diferenciarse con datos en el pitch a sus clientes
- No necesitan aprobación de procurement corporativo

**Target en Perú:**
- Pragma (Lima) — trade marketing y shopper marketing
- Neo Consulting (Lima) — retail consulting y category management
- Summa (Lima) — brand y trade marketing
- Brandovation — digital + trade
- Cualquier agencia que haga "shopper insights" o "category management" como servicio

**Mensaje para agencia:**
> "Ofrece inteligencia de precios de góndola a tus clientes de marca como parte de tu
> servicio — sin construir nada. Tú te llevas el margen, nosotros ponemos los datos."

### Segmento 2 — Mayor ticket: Marcas challenger medianas

No las líderes (Alicorp, Gloria — procurement largo). Las que atacan al líder y necesitan
inteligencia para competir:

| Marca | Categoría | Por qué necesita Brand Intel |
|-------|-----------|------------------------------|
| Laive | Lácteos | Compite contra Gloria — necesita ver si está siempre más caro en góndola |
| San Fernando | Aves/procesados | Múltiples SKUs en múltiples cadenas, promos frecuentes |
| Molitalia | Pastas/harinas | Compite con Don Vittorio (Alicorp) — precio relativo crítico |
| Pastificio | Pastas | Challenger vs líderes, presupuesto ajustado |
| Florida (conservas) | Conservas | Ya indexado — atún Florida está en nuestra DB |

**Mensaje para marca challenger:**
> "¿Sabes si Don Vittorio está haciendo promo en Metro esta semana mientras tus productos
> están al precio regular? Ahora puedes saberlo antes de que te afecte el sell-out."

### Segmento 3 — Upsell natural: Category Managers de retail

Los propios retailers (Wong, Metro, Plaza Vea) son potenciales clientes para la vista de
categoría: ¿qué marcas están siendo más agresivas esta semana en mi propia góndola?

Este segmento requiere un producto ligeramente diferente (sin el "mis SKUs" — solo vista de
categoría completa). Lo dejamos para v2.

---

## 6. Plan de build — 4 sprints de 1 semana

### Sprint 1 — Backend: endpoint `/v1/brand-monitor`

**Objetivo:** query funcional que devuelva mis SKUs + competidores desde `price_snapshots`.

```python
# Lógica core del endpoint
GET /v1/brand-monitor?brand=Gloria&country=PE&competitors=Laive,Nestlé&line=supermercados&days=30

# Query base
SELECT name, brand, store, price, list_price, discount, queried_at
FROM price_snapshots
WHERE brand IN ('Gloria', 'Laive', 'Nestlé')
  AND line = 'supermercados'
  AND store IN (pe_stores)
ORDER BY brand, name, store, queried_at DESC
```

**Entregables Sprint 1:**
- [x] `routers/brand_intel.py` con endpoint `/v1/brand-monitor`
- [x] Lógica de normalización: agrupar variantes del mismo producto (400ml vs 410ml vs "grande")
- [x] Cálculo de `dispersion_score` (CV de precio cross-tienda por SKU)
- [x] Cálculo de `promo_events` (activaciones detectadas en el período)
- [x] Tests unitarios básicos — `tests/test_brand_intel.py` (12 tests, los 4 endpoints)

### Sprint 2 — Backend: alertas y PVP sugerido

**Objetivo:** la marca puede ingresar su PVP sugerido y el sistema detecta desvíos.

**Tabla nueva:** `brand_intel_config`
```sql
CREATE TABLE brand_intel_config (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  brand_slug TEXT NOT NULL,         -- 'gloria', 'laive'
  api_key    TEXT NOT NULL,         -- FK a api_keys
  sku_pvps   TEXT,                  -- JSON: {"prod_gloria_leche_0.4kg": 3.50, ...}
  competitors TEXT,                 -- JSON array: ["Laive", "Nestlé"]
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**Entregables Sprint 2:**
- [x] `POST /v1/brand-monitor/config` — onboarding: declara marca, competidores, PVPs
- [x] `GET /v1/brand-monitor/alerts` — desvíos activos vs PVP sugerido
- [x] Lógica de alerta: `precio > PVP × 1.05` o `precio < PVP × 0.85`
- [x] Email de alerta automático cuando se detecta desvío significativo (>10%) — `ops/brand_alert_email.py` + `.github/workflows/brand-alert-email.yml` (cron diario 08:00 PET)

### Sprint 3 — Frontend: Brand Monitor Dashboard

**Objetivo:** dashboard usable por un analista no técnico. Estilo terminal (alineado con
`docs/BRAND.md` — no e-commerce, Bloomberg density).

**Stack:** Next.js (ya existe en `landing/`), componentes de la design system existente.

**Páginas nuevas:**
```
/brand/[slug]/                → resumen (cards: mis SKUs, alertas activas, promo tracker)
/brand/[slug]/my-skus         → tabla completa de mis SKUs
/brand/[slug]/competitors     → tabla de competidores + precio relativo
/brand/[slug]/promos          → historial de promos
/brand/[slug]/settings        → configuración: PVPs, competidores declarados
```

**Componentes nuevos:**
- `BrandMetricCard` — card con métrica principal + tendencia (reutiliza tokens `--cm-data`,
  `--cm-signal`)
- `PriceComparisonTable` — tabla de precios cross-tienda con semáforo de desvío
- `PromoTimeline` — línea de tiempo de activaciones de descuento
- `CompetitorRankChart` — ranking de precio relativo en categoría

**Auth:** misma API key del plan Pro. El slug de marca se registra en `brand_intel_config`.

**Estado:** construido — `BrandMonitorDashboard`, `BrandCompetitorTable`, `BrandPromoTimeline`,
`BrandSkuTable` y ruta `/brand/[slug]` ya existen en `landing/`, con un `/brand/demo` de referencia.

### Sprint 4 — PDF mensual + piloto

**Objetivo:** primer cliente piloto recibe su primer reporte.

**Entregables Sprint 4:**
- [x] Generador PDF `ops/brand_report.py` — extiende `price_pulse_agents.py`
- [x] Template de 8 páginas — primer reporte ya generado: `ops/generated/reports/brand-report-gloria-2026-07.pdf`
- [ ] Onboarding manual del primer cliente (30 días gratis) — pendiente: aún no hay primer cliente piloto
- [x] Documento metodológico público de 1 página — `docs/methodology-brand-intelligence.md`
- [x] NDA template con cláusula de no-cross-sharing — `docs/legal/nda-brand-intelligence-template.md` (borrador, requiere revisión legal antes de usar)

---

## 7. Métricas de éxito — Piloto (días 0-30)

| Métrica | Target piloto | Target mes 3 |
|---------|--------------|--------------|
| Clientes pagos | 0 (piloto gratis) | 3 marcas o agencias |
| MRR Brand Intel | $0 | $1.5K–$4.5K |
| Reportes generados | 1 (al final del piloto) | 3/mes automáticos |
| Alertas de desvío detectadas | Al menos 5 reales | — |
| NPS piloto | ≥ 8/10 | — |
| Tiempo de onboarding | < 30 min | < 15 min |

---

## 8. Riesgos y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|------------|
| Cobertura de SKUs de una marca es parcial | Alta | Alto | Comunicar al cliente qué % de su catálogo está indexado antes de firmar |
| Marca no quiere que competidor sepa que usa el servicio | Media | Alto | NDA con cláusula no-cross-sharing; no publicar lista de clientes |
| Nielsen baja precios en respuesta | Baja | Medio | Nuestro diferenciador es frecuencia + precio, no solo precio |
| Retailer bloquea scraping de sus datos | Media | Alto | Diversificar fuentes; VTEX API pública es más estable que scraping |
| Marca pide cobertura offline (tiendas físicas) | Alta | Medio | Scope explícito: solo retail digital indexado; offline = v2 con datos de Nielsen |
| Datos de historial insuficientes (<30 días) | Alta ahora | Alto | Arrancar piloto hoy para acumular historia; ofrecer piloto gratis durante acumulación |

---

## 9. Lo que este PRD NO incluye (fuera de scope v1)

- Cobertura de retail offline (tiendas físicas, promotoras en punto de venta)
- Integración con sistemas de la marca (ERP, SAP Trade Promotion)
- Datos de sell-out o volumen de ventas (solo precios, no cantidades vendidas)
- Cobertura de canales informales (mayoristas, distribuidores)
- Módulo de recomendación de precio sugerido (pricing optimization — v2)
- Segmento de Category Manager de retail (distinto producto — v2)

---

## 10. Decisiones — tomadas 2026-07-06

| Decisión | Opciones | Resuelto |
|----------|---------|---------------|
| ¿Nuevo dominio o subdominio? | `brand.cli-market.dev` vs `climarket.dev/brand` | **Subdominio** `brand.cli-market.dev` — menor fricción técnica, misma identidad |
| ¿Precio piloto? | $0 / $99 / $199 por 30 días | **$0** — elimina fricción para el primer caso; convierte por valor demostrado |
| ¿Primer cliente: agencia o marca directa? | Agencia (3-5 marcas de golpe) vs marca directa (ciclo más corto) | **Agencia** primero — mayor leverage por contrato |
| ¿Normalización de SKU competidor? | Automática (semántica) vs manual (el cliente declara) | **Automática** con revisión manual en onboarding |
| ¿Acceso API para competidores en la misma agencia? | Compartido con NDA vs silos separados | **Silos separados** por brand_slug + api_key |

Con esto resuelto, y con tests/email/NDA/metodología ya construidos (ver checklist de Sprint 4
arriba), lo único que falta para arrancar el piloto real es: setup del subdominio y
conseguir/onboardear la primera agencia piloto.
