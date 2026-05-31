# CLI Market — Estrategia de Producto y Plan de Actualización

> **Documento de decisión consolidado** · v1.0 · Mayo 2026
> Autor: Ricardo Cuba (Sinapsis Innovadora) · Estado: propuesta para revisión
> Alcance: posicionamiento, modelo de negocio calibrado a Perú, decisión sobre protocolos de comercio agéntico (UCP/ACP), y MVP del Índice de Canasta.

---

## TL;DR

1. **El producto no es "un CLI para comprar". Es una capa de agregación y normalización de datos de comercio LatAm con interfaz agente-nativa.** El moat es la data normalizada, el rail Yape/Plin y el histórico de precios — no el protocolo ni la interfaz.
2. **Acción inmediata:** unificar el mensaje público en **41 retailers verificados / 36 MCP tools**. El "3,760" es el universo VTEX teórico, no cobertura real, y la inconsistencia quema credibilidad técnica.
3. **UCP (Google) no es una decisión arquitectónica hoy.** Es un connector futuro, igual que VTEX/Shopify/Magento. Cero urgencia (26 implementaciones reales a mayo 2026). Apuesta: MCP-native + agregación horizontal LatAm.
4. **El cash está en la línea de Data de Inflación, no en el API metering.** Modelo calibrado a Perú: caja acumulada 3 años ≈ **USD 392K (Base)**, con USD 40K no dilutivo de ProInnóvate en Año 1.
5. **MVP del Índice de Canasta construido y demostrable.** El gancho de venta: la señal de alta frecuencia anualiza ~15.8% vs. meta oficial 2.4% — gap relevante para research/medios/banca en año electoral.

---

## 1. Estado actual del proyecto (línea base)

| Dimensión | Realidad (mayo 2026) |
|-----------|----------------------|
| Cobertura | 41 retailers verificados · 8 países (PE, AR, BR, MX, CO, CL, US, +) |
| Datos | ~13K precios reales · refresh cada 8h · objetivo 200K+ |
| Interfaz | API REST + CLI + 36 herramientas MCP |
| Conectores | VTEX + Shopify + Magento |
| Checkout | PayPal (API) + QR Yape/Plin |
| Licencia | MIT (open source) |
| Repo | `github.com/Treevu-ai/cli-market-world` |
| Demo | `cli-market.dev` |
| En desarrollo | Archivo histórico de precios 90 días (tracking de inflación) |

**Insight fundacional (correcto):** *el cuello de botella de los agentes de compra no es el LLM, es la capa de datos de comercio.* Eso define el producto.

---

## 2. Acción inmediata — Unificar narrativa

La historia pública evolucionó en tres saltos inconsistentes:

- "VTEX API es igual para 3,760 retailers" (acceso teórico)
- "Registré MCP server para 3,760 retailers"
- "41 retailers verificados, 13K precios reales" (28 may)

**Problema:** Product Hunt aún dice *3,760 + 12 MCP tools*; el post de DEV dice *41 + 36 tools*. Un dev técnico que verifica encuentra el desfase y pierde confianza.

**Acción:**
- [ ] Unificar todo el material en **41 verificados / 36 MCP tools**.
- [ ] Añadir `as-of timestamp` visible en cada respuesta de precio (honestidad de data = confianza técnica).
- [ ] Reservar "3,760" solo como TAM teórico, etiquetado como tal.

---

## 3. Tesis de producto

CLI Market opera en una capa distinta a la de los protocolos de comercio agéntico:

- **Protocolos (UCP, ACP):** merchant ↔ agente, relación 1:1, vertical.
- **CLI Market:** agregador multi-merchant con datos normalizados, relación N:1, horizontal.

El valor está en tres activos defendibles:

1. **Normalización cross-retailer** — mismo SKU, IDs distintos entre retailers → canonical price set (ya implementado parcialmente en `market_compare`).
2. **Rail de pago LatAm** — Yape/Plin funcionando hoy, mientras las big tech aún resuelven settlement (Google Wallet→AP2 sin cerrar).
3. **Histórico de precios** — el activo más infravalorado: serie timestamped, granular, multi-país.

---

## 4. Posición competitiva y decisión sobre protocolos

### Cuatro frentes

| Frente | Naturaleza | Lectura |
|--------|-----------|---------|
| **VTEX Developer MCP** (abr 2026, 42 skills) | Para desarrollar *sobre* VTEX | No agrega cross-retailer. No compite directo; podrían construir tu capa, pero no agregarán a Shopify/Magento. |
| **UCP** (Google + Shopify) | Protocolo merchant↔agente vertical | No agrega ni normaliza. Consumible como connector. 26 implementaciones reales = irrelevante operativamente hoy. |
| **ACP** (OpenAI + Stripe) | Checkout dentro de ChatGPT | Canal de distribución potencial, no competidor. |
| **Scrapers / status quo** | "Cada quien scrapea solo" | **El competidor real.** Ganas si `pip install` es más barato que mantener 41 scrapers. |

### Decisión: UCP

**No adoptar como decisión arquitectónica. Tratar como connector futuro.**

- Cuando un retailer exponga UCP, se consume igual que VTEX/Shopify/Magento.
- Mantener **MCP-native** como core (alineado con el stack y con Anthropic; UCP además incluye soporte MCP).
- Abstraer payment handlers (VTEX/Yape hoy; UCP/AP2 cuando settle).

**Disparadores para revisar (cualquiera):**
1. >500 implementaciones UCP detectadas (vs 26 hoy).
2. Gemini agent checkout con UCP en producción ≥5% conversión.
3. Top-5 retailers de tu base lo piden.
4. Settlement AP2 estabilizado (Mastercard/Visa/Stripe acuerdan handler).

---

## 5. Modelo de negocio — calibrado a Perú

> Detalle numérico editable en `CLI_Market_Modelo_v2_Peru.xlsx` (3 escenarios, supuestos transparentes).

### Contexto que justifica la calibración

- Inflación oficial 2026: **2.4%** (BCRP), con riesgo de cierre **>3%** por alimentos/combustibles (analistas).
- PBI 2026: **3.2%**; elecciones presidenciales abril 2026 → volatilidad.
- Ecosistema startup PE: USD ~60M en 2025 (+28%), fintech ~85%; detrás de MX/CO/CL en capital, pero costo operativo menor.
- Capital no dilutivo disponible: **ProInnóvate hasta S/150K (~USD 40K)**, requiere PMV.
- Benchmark tracción B2B local: Khipu, 40 clientes en año 1.

### Tres líneas + financiamiento

| Línea | Cliente | ACV/ARPU (Base) | Rol |
|-------|---------|-----------------|-----|
| **L1 · API Metering** | Devs/agentes globales | $29/mes | Top-of-funnel, credibilidad |
| **L2 · Data Inflación local** | Research/medios/retail PE | $6K/año | Volumen local |
| **L3 · Data Inflación internacional** | Multilaterales/research/banca | $25K/año | **Activo premium (LTV $170K)** |
| **+ ProInnóvate** | Estado (no dilutivo) | $40K Año 1 | Runway sin diluir equity |

### Resultados (escenario Base)

| Métrica | 2026 | 2027 | 2028 |
|---------|------|------|------|
| Revenue total | $40.5K | $123K | $253K |
| EBITDA operativo | $35.7K | $104K | $213K |
| Caja neta del año | $75.7K | $104K | $213K |

**Caja acumulada 3 años:** Conservador **$54.7K** · Base **$392K** · Optimista **$1.53M**.

### Lecturas honestas

- **El negocio lo carga Data, no API.** En Base 2028, L2+L3 ≫ L1.
- **Márgenes altos (84-88%) = bootstrap sin salario de founder.** Bajan al pagarse o levantar.
- **Unit economics "demasiado buenos" (LTV/CAC 25-68x):** reales en early-stage orgánico, **bajarán con GTM pagado**. No usar sin asterisco en pitch.
- **El conservador sobrevive sin depender del fondo público.** La estructura liviana protege el piso.

**Supuestos a validar primero (amarillos en el modelo):** ACV local, ACV internacional, # clientes Data Año 1, churn, margen bruto.

---

## 6. Producto: Índice de Data de Inflación

### Tesis
El daemon ya genera, como subproducto, lo que research/bancos pagan por construir: serie de precios reales, granular por SKU, timestamped, multi-país, casi en tiempo real.

### Capas
| Capa | Contenido |
|------|-----------|
| Dato base | Precio × SKU × retailer × país × timestamp (8h) |
| Derivado 1 | Índice de canasta (SKU → categorías) |
| Derivado 2 | Serie histórica → variación % (inflación observada) |
| Derivado 3 | Comparativa cross-retailer y cross-país |

### Por qué es defensible
- Granularidad que el dato oficial (IPC mensual agregado) no tiene.
- Velocidad: 8h vs. semanas de rezago oficial.
- Nadie agrega cross-retailer en LatAm. UCP/VTEX-MCP/ACP no producen series históricas.

### Formatos (incremental)
1. **v0** — Dataset por suscripción (CSV/Parquet o API histórica). Más rápido de vender.
2. **v1** — Dashboard "Canasta LatAm" (marketing + lead-gen). → *entregado como MVP, ver §7*.
3. **v2** — API de nowcasting (señales derivadas). Premium banca/research.

### Gaps técnicos (de mock a real)
1. Fijar taxonomía de canasta estable (mapear SKUs a categorías comparables tipo IPC).
2. Persistencia histórica robusta (no perder data al refrescar).
3. Capa de agregación/ponderación.

### Riesgos específicos
- **Sesgo de muestra:** 41 retailers ≠ IPC nacional. Vender como *señal de alta frecuencia*, no "inflación oficial".
- **Continuidad de serie:** perder cobertura rompe el índice. Persistencia = no-negociable.
- **Legal:** publicar índice agregado es más defendible que reexponer catálogos crudos. El producto-índice aleja del riesgo ToS.

---

## 7. MVP entregado — Índice de Canasta Perú

**Archivo:** `CLI_Market_Indice_Canasta_MVP.html` (self-contained, abre en navegador).

- Canasta peruana real: 12 SKUs (leche Gloria, arroz, aceite, etc.) × Metro/Wong/Plaza Vea/Tottus.
- Componentes: índice base 100, serie 90d, desglose por categoría, comparación cross-retailer, tabla SKU, metodología.
- **Gancho de venta:** señal anualizada ~15.8% vs. meta oficial 2.4% → el *gap observado* es la conversación que abre puertas.
- Marcado como demo; datos de muestra; metodología honesta (retail formal urbano, no IPC).

**Pendiente para producción:** conectar a la serie real del daemon (ver gaps §6).

---

## 8. Roadmap priorizado

### Esta semana
- [ ] Unificar narrativa pública en 41 verificados / 36 MCP tools.
- [ ] `as-of timestamp` en cada respuesta de precio.

### 2–4 semanas
- [ ] Definir modelo de negocio explícito (API metering + Data B2B). Documentar v0.
- [ ] Onboarding "retailer lista gratis con token read-only" como camino default (blinda flanco legal).
- [ ] Máquina de estados de checkout (QR → webhook → reconciliación → fallback).
- [ ] Llevar el MVP del índice a 3 contactos (research/medios/banca) → calibrar ACV real.

### 2–3 meses
- [ ] Productizar dataset de inflación: taxonomía de canasta + persistencia histórica + agregación.
- [ ] Postular a ProInnóvate con el MVP como evidencia de PMV (= los $40K del modelo).
- [ ] Foco en tracción > features: 5 devs construyendo agentes sobre CLI Market.

---

## 9. Riesgos transversales

| Riesgo | Mitigación |
|--------|-----------|
| Frescura 8h → disputa de checkout | SLA de frescura por categoría; timestamp explícito |
| Legal/ToS (polling no autorizado a escala) | Empujar onboarding por token; producto-índice agregado |
| Concentración de plataforma (VTEX) | Diversificar mix Shopify/Magento activamente |
| Sin moat de demanda (producto sin tracción) | Distribución > features; casos de uso reales |
| Identidad de marca difusa (`Treevu-ai/`) | Decidir: ¿producto independiente o spin-off de Sinapsis? |

---

## 10. Entregables de esta iteración

| Archivo | Contenido |
|---------|-----------|
| `CLI_Market_Modelo_v2_Peru.xlsx` | Modelo financiero, 3 escenarios, calibrado a Perú |
| `CLI_Market_Indice_Canasta_MVP.html` | Dashboard demostrable del Índice de Canasta |
| `STRATEGY.md` (este documento) | Decisión consolidada para el repo |

---

## Apéndice — Fuentes macro (mayo 2026)

- BCRP, *Reporte de Inflación marzo 2026*: PBI 3.2%, inflación 2.4%, tasa 4.25%.
- Infobae / Macroconsult: riesgo de inflación >3% por alimentos/combustibles.
- PECAP: inversión startups PE +28% en 2025 (~USD 60M), fintech ~85%.
- ProInnóvate / Startup Perú 2026: capital semilla no reembolsable hasta S/150K.
- Gestión: benchmark tracción B2B (Khipu, 40 clientes año 1).
- McKinsey / Morgan Stanley / Bain / Gartner: comercio agéntico 2030 (contexto global del sector).

---

*Documento vivo. Próxima revisión sugerida: tras validación de ACV con 3 contactos y/o resultado de postulación ProInnóvate.*
