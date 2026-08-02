# CLI Market — Brief institucional
## Señales de consumo minorista para pilotos de scoring alternativo (contexto SBS Sandbox)

**SINAPSIS INNOVADORA S.A.C.** · Lima, Perú  
**API producción:** https://cli-market-api.fly.dev  
**Sitio:** https://cli-market.dev  
**Snapshot de datos:** 2026-07-14T16:04 UTC (fuente: `/dashboard/data`, `/health`, `/health/db`)

---

## 1. Quiénes somos

**CLI Market** es infraestructura de datos de mercado minorista para integración vía **API REST**, **CLI** (`pip install cli-market-world`) y **MCP** (herramientas para agentes de IA).

Recopilamos precios de góndola de retailers en Latinoamérica, los normalizamos (marca, unidad, subcategoría) y exponemos señales agregadas de **inflación minorista**, **canasta**, **dispersión de precios** e **indicadores compuestos** — sin procesar datos personales del deudor.

**Empresa:** SINAPSIS INNOVADORA S.A.C. (Lima, Perú).

---

## 2. Contexto regulatorio (Perú) — sin sobreprometer

La **SBS** amplió el **sandbox regulatorio** mediante la **Resolución SBS N° 04142-2025** (nov. 2025), publicada en medios oficiales y analizada por firmas locales (p. ej. Revoredo, Infobae):

| Hecho verificable | Detalle |
|-------------------|---------|
| Alcance ampliado | Pueden postular **fintechs**, **empresas no supervisadas** y **cooperativas** (entre otros actores antes excluidos). |
| Duración | Pruebas piloto hasta **30 meses** (extensión respecto al marco anterior). |
| Objetivo declarado | Experimentar productos/servicios financieros en entorno controlado y supervisado. |
| Ejemplos citados en análisis legal | Incluyen soluciones de **análisis de riesgo** e **IA** aplicadas al sistema financiero. |

**Importante:** CLI Market **no afirma** estar inscrito hoy en el sandbox SBS ni sustituir modelos de scoring aprobados por una entidad supervisada. Ofrecemos **datos y señales de mercado** que una entidad supervisada (o su fintech asociada) puede evaluar **dentro de un piloto sandbox** como variables complementarias al buró y al ingreso declarado.

Referencias públicas:
- [Infobae — Sandbox SBS, Res. 04142-2025](https://www.infobae.com/peru/2025/11/24/sandbox-regulatorio-sbs-permitira-que-fintechs-y-cooperativas-experimenten-con-nuevos-productos-financieros-durante-30-meses/)
- [Revoredo — Análisis Res. 04142-2025](https://revoredo.pe/el-nuevo-sandbox-regulatorio-de-la-sbs-un-cambio-de-paradigma-para-la-innovacion-financiera-en-el-peru/)

---

## 3. Perfil de uso: economía peruana, consumidor formal

Este brief se orienta al **hogar o trabajador formal** cuyo gasto discrecional depende del **costo observable en retail** — el que compra en cadenas indexadas en Perú (supermercados y líneas afines), no al segmento informal sin precios de góndola trazables.

**Cobertura retail Perú en catálogo API** (9 retailers, verificado `/stores?country=PE`):

| Retailer | Línea |
|----------|-------|
| Wong, Metro, Plaza Vea, MiMercado Delivery, Nuna Orgánica | Supermercados |
| Promart, Sodimac PE | Hogar y construcción |
| Ripley PE, Falabella PE | Departamentales |

**Precios indexados con datos activos en el agregado país** (snapshot dashboard): **14.971** observaciones PE en **6** tiendas con volumen en el moat agregado (el catálogo declara 9; la cobertura operativa varía por tienda — ver §4).

---

## 4. Data moat — métricas en tiempo real (verificables)

Fuente única: `GET https://cli-market-api.fly.dev/dashboard/data` y `/health/db` al **2026-07-14T16:04 UTC**.

### 4.1 Salud del sistema

| Métrica | Valor |
|---------|-------|
| API `/health` | `healthy` |
| Base de datos | PostgreSQL |
| `price_snapshots` en DB | 74.249 |
| Upsert Postgres | `price_snapshots_upsert_ready: true` |

### 4.2 Moat global (todas las geografías)

| Métrica | Valor |
|---------|-------|
| Precios indexados (`total_indexed`) | **73.740** |
| Productos únicos | 74.060 |
| Tiendas con índice activo | 40 |
| Snapshots últimas 24h | **32.257** |
| Cobertura 7 días | **97,3%** |
| Tiendas fresh 24h | 36 / 37 catálogo activo |
| Última recolección | 2026-07-14 15:35 UTC |
| Edad del moat | 0,5 h |
| Collector | `status: ok` · último ciclo 2026-07-14 14:56 UTC · 2.249 precios en ciclo |
| Intervalo declarado en dashboard | 8 h |
| Golden records (linkage semántico) | 99,2% snapshots vinculados |

### 4.3 Perú — frescura por tienda (supermercados)

| Tienda | Cobertura 7d | Último éxito collector |
|--------|--------------|------------------------|
| Wong | 66,0% | 2026-07-14 14:56 UTC |
| Metro | 67,3% | 2026-07-14 14:56 UTC |
| Plaza Vea | 60,2% | 2026-07-14 14:56 UTC |
| Nuna Orgánica | 79,9% | 2026-07-14 14:56 UTC |
| Promart | 34,8% | 2026-07-14 14:56 UTC |

*Nota honesta:* la cobertura por tienda en PE es **heterogénea** (60–80% en supermercados principales; Promart más bajo). Cualquier piloto de scoring debe acotarse a subcategorías y tiendas con cobertura suficiente.

---

## 5. Señales Perú relevantes para scoring alternativo

Todas las cifras siguientes provienen del bloque `indicators` y `canasta_basica` del dashboard — **no son índices INEI ni IPC oficial**.

### 5.1 Indicadores agregados PE (2026-07-14)

| Indicador | Valor | Lectura técnica |
|-----------|-------|-----------------|
| **Retail Price Velocity (RPV)** — staples 7d | **−3,52%** | Momentum de precio en góndola (leche, arroz, aceite, azúcar, huevos), modo shelf. |
| **RPV list price** (promo-adjusted) | **+0,88%** | Misma canasta, precios lista sin distorsión promocional extrema. |
| **Promo intensity** | **42,32%** | Alta intensidad promocional en PE — relevante al interpretar precios shelf vs. lista. |
| **Price dispersion** (agregado PE) | **8,42%** | Dispersión media entre retailers indexados. |
| **Shelf vs official CPI gap** | **−4,1 pp** | Señal interna −2,57% vs. CPI oficial referenciado 1,531% (metadato API). |
| **Store coverage** | **5** tiendas | Tiendas PE con datos en el cómputo del indicador. |
| **Weather logistics stress** | **0,8** | Índice logístico externo (Open-Meteo). |

### 5.2 Canasta básica comparativa (matched items, PEN)

Cómputo interno CLI Market — **no es canasta INEI**:

| Retailer | Ítems emparejados | Total PEN |
|----------|-------------------|-----------|
| Plaza Vea | 11 | **S/ 67,59** |
| Metro | 11 | **S/ 77,84** |
| Wong | 11 | **S/ 83,22** |
| Nuna Orgánica | 10 | **S/ 174,80** |

Brecha entre Plaza Vea y Wong en la misma canasta indexada: **~23%** (S/ 15,63 sobre base S/ 67,59).

### 5.3 Dispersión por subcategoría — aceite (pack estándar 1 kg / 1 L)

| Campo | Valor |
|-------|-------|
| Tiendas comparables | 4 |
| Productos en muestra | 89 |
| Precio mínimo | S/ 5,78 / L |
| Precio máximo | S/ 52,75 / L |
| Spread ratio | **2,6×** (umbral marketing interno: 2,5) |

---

## 6. Qué ofrecemos (propuesta de valor técnica)

### 6.1 Producto

| Capa | Entrega |
|------|---------|
| **Datos** | Precios de góndola, historial, canasta matched, dispersión por subcategoría |
| **Indicadores** | RPV staples, promo intensity, gap vs. CPI referencia, logistics stress |
| **Alertas** | Motor post-collector con condiciones `price_jump`, `price_drop`, `price_min_30d`, `dispersion_anomaly` y cooldown configurable (1–720 h) |
| **Integración** | REST (`/docs`), webhooks Enterprise, jobs asíncronos (`/v1/intel/price-pulse`) |
| **Agentes** | MCP profile default (31 herramientas documentadas en repo público cli-market-world) |

### 6.2 Uso en scoring alternativo (piloto sandbox)

Variables **candidatas** — a validar estadísticamente por la entidad supervisada:

1. **RPV staples 7d** → presión de costo de vida del hogar formal.
2. **Canasta mínima indexada** → regla de affordability (cuota / costo canasta).
3. **Promo intensity** → ajuste por distorsión promocional en precios observados.
4. **Shelf vs CPI gap** → desalineación señal minorista vs. macro oficial.
5. **Dispersión subcategoría** → costo efectivo según capacidad de arbitrar entre cadenas.
6. **Alertas** → monitoreo en vida del crédito (no solo originación).

**Arquitectura típica de piloto:**

```
CLI Market API  →  cache institucional  →  motor scoring (entidad supervisada)
                         ↑
              sin PII — solo señales agregadas de mercado
```

El cruce con datos del solicitante (ingreso, buró Sentinel/Experian, comportamiento interno) ocurre **en infraestructura de la entidad supervisada**, no en CLI Market.

### 6.3 Lo que no somos

- No somos buró de crédito ni originador.
- No emitimos score de crédito ni decisión automatizada de concessión.
- No publicamos índices oficiales de inflación (INEI).
- No garantizamos que un piloto sandbox sea aprobado por la SBS; eso depende del expediente de la entidad solicitante.

**Disclaimer API (texto en endpoints intel):** *"Internal collector signal — not an official inflation index."*

---

## 7. Encaje con sandbox SBS (propuesta concreta y acotada)

Un expediente sandbox razonable podría plantearse así:

| Elemento | Propuesta |
|----------|-----------|
| **Sujeto supervisado** | Entidad financiera o caja autorizada (originador del crédito). |
| **Rol CLI Market** | Proveedor de **datos alternativos de mercado** (señales de consumo agregadas). |
| **Hipótesis a probar** | Variables de costo de vida minorista mejoran explicación de mora temprana vs. modelo solo buró+ingreso, en segmento formal urbano PE. |
| **Duración sugerida** | Alineada al marco SBS (hasta 30 meses); piloto técnico inicial 90 días con backtest. |
| **Gobernanza** | Definición de variables en catálogo API, `recorded_at` por indicador, export CSV para auditoría de modelos. |
| **Datos personales** | Fase 1 sin PII en CLI Market; cruce on-premise en originador. |

---

## 8. Evidencia reproducible (para el equipo técnico del receptor)

```bash
# Salud y moat (sin autenticación)
curl -sS https://cli-market-api.fly.dev/health
curl -sS https://cli-market-api.fly.dev/health/db
curl -sS https://cli-market-api.fly.dev/dashboard/data | jq '.moat_summary, .by_country, .canasta_basica, .indicators.latest'

# Catálogo Perú
curl -sS "https://cli-market-api.fly.dev/stores?country=PE"

# OpenAPI
open https://cli-market-api.fly.dev/docs
```

Indicadores avanzados (`/v1/intel/scores`, `/v1/intel/basket-stress`, etc.) requieren **API key** (registro en cli-market.dev). Disponibles bajo planes documentados en producción.

---

## 9. Contacto y siguiente paso

**Propuesta de primer contacto:** reunión técnica de 45 min con demo en vivo del dashboard + un endpoint de canasta PE + revisión de catálogo de indicadores.

**SINAPSIS INNOVADORA S.A.C.**  
https://cli-market.dev · https://cli-market-api.fly.dev/docs

---

*Documento preparado con datos live del datamoat. Cifras sujetas a cambio en cada ciclo del collector. No constituye oferta vinculante ni asesoría regulatoria.*