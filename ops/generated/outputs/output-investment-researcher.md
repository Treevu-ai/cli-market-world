## 🔬 Dispersión de Precios — Análisis Contextual

### Tabla de Spreads Detectados (Marketing-Ready)

Productos con spread ≥2.5×, unidad normalizable por kg/L, ≥3 tiendas:

| Producto | País | Línea | Moneda | Tiendas | Spread | Status |
|----------|------|-------|--------|---------|--------|--------|
| Queso (Port Salut) | AR | Supermercados | ARS | 3 | 2.93× | ⚠️ warn |
| Pollo (bocaditos) | AR | Supermercados | ARS | 3 | 2.67× | ⚠️ warn |
| Aceite de Girasol | AR | Supermercados | ARS | 3 | 2.65× | ⚠️ warn |

Los 3 spreads detectados están en Argentina (ARS). No se detectaron spreads >2.5× en Perú (PEN), México (MXN), Brasil (BRL), Colombia (COP) ni Chile (CLP) en esta ventana.

### Interpretación por país

**Argentina (ARS) — spreads 2.6×–2.9×**: La dispersión de precios en Argentina es estructuralmente más alta que en otros mercados LATAM. Tres factores convergen:

1. **Inflación residual**: aunque la desinflación está en curso (IPC mensual ~2-3% en mayo 2026, desde picos >25% en 2023), los precios relativos todavía se están reacomodando. Distintos retailers ajustan a distinta velocidad.

2. **Controles de precios sectoriales**: Precios Justos y acuerdos sectoriales generan distorsiones donde un mismo producto puede tener precio regulado en una cadena y precio libre en otra.

3. **Fragmentación del retail**: Vea, Jumbo y Carrefour AR compiten en segmentos distintos (económico, medio, premium). La canasta en Vea (10/10, ARS 10.287) cuesta 31% menos que en Jumbo (10/10, ARS 14.936). Este spread es consistente con el posicionamiento de mercado.

**Perú (PEN) — sin spreads >2.5×**: La canasta entre Plaza Vea (PEN 64.39), Metro (PEN 76.39) y Wong (PEN 88.75) muestra spreads de 1.18×–1.38×. Es un mercado más concentrado (3 grandes cadenas controlan ~70% del retail formal) y con menor inflación (IPC ~2.4%), lo que reduce la dispersión.

### Implicancias para el cliente

- **Fintech / credit scoring**: spreads en ARS de 2.6×–2.9× en productos de canasta básica son relevantes para modelos de riesgo. Un hogar que compra en la tienda más cara gasta 31% más en los mismos 10 productos. Incorporar el spread intra-canasta como variable en scoring de crédito puede mejorar la precisión del modelo.

- **CPG / trade marketing**: el aceite de girasol en ARS con spread de 2.65× (min ARS 143, max ARS 3.353) sugiere que el precio sugerido por el fabricante no se está respetando uniformemente en góndola. Es una señal para revisar la ejecución de la estrategia de pricing en el canal retail.

---

## 🌎 Contexto Macro — LATAM, Junio 2026

### Inflación regional

América Latina entra al segundo semestre de 2026 con una inflación en descenso generalizado pero heterogéneo:

- **Argentina**: desinflación en curso. IPC mensual estimado en 2-3%, anualizado ~30-40% (desde >200% en 2023). El programa de estabilización muestra resultados pero la inflación inercial persiste en alimentos.
- **Perú**: inflación controlada dentro del rango meta del BCRP (1-3%). IPC ~2.4% anual. La economía crece ~3.2%, impulsada por minería y consumo privado. Año electoral 2026 con riesgo de volatilidad post-elecciones.
- **Brasil**: IPCA ~4-5%, por encima de la meta de 3%. El BCB mantiene la Selic elevada. Presión en alimentos por factores climáticos y tipo de cambio.
- **México**: inflación ~4%, dentro de un proceso de convergencia lenta hacia la meta de 3%. Presión salarial por política de salario mínimo.
- **Colombia**: IPC ~5-6%, todavía por encima de la meta de 3%. La reforma tributaria y el ajuste de combustibles presionan precios.

### Tipo de cambio

El BRL, MXN y COP se apreciaron frente al USD en lo que va de 2026, impulsados por carry trade y precios de commodities. El ARS oficial mantiene un crawling peg administrado. El PEN se mantiene estable, respaldado por un BCRP con alta credibilidad y reservas récord. Las diferencias cambiarias explican parte de los spreads cross-border observados en el collector.

### Consumo y retail

El consumo privado en LATAM muestra recuperación desigual. Perú lidera con crecimiento de ~3%, impulsado por empleo formal y remesas. Argentina muestra signos de estabilización del consumo después de la contracción de 2023-2024. Brasil y México crecen a ritmo moderado (~2%). El canal online (VTEX, Shopify) sigue ganando participación — el collector captura este shift estructural hacia retail digital.

### Conexión con los datos

La ausencia de inflación 7d en el collector (serie <7 días) es esperable para un piloto en su primera semana. La canasta muestra precios consistentes con el posicionamiento de cada retailer y la realidad macroeconómica de cada país. Los spreads detectados exclusivamente en ARS son consistentes con un mercado en proceso de estabilización post-crisis inflacionaria.

---

## 🏢 Competitive Landscape

| Fuente | Tipo | Cobertura | Frecuencia | Precio estimado | Ventaja CLI Market |
|--------|------|-----------|------------|-----------------|-------------------|
| **NielsenIQ** | Panel / scanner | Global, débil LATAM | Mensual | USD 5K–20K/mes | 8h vs 30d, USD 300 vs USD 5K+, granularidad SKU, LATAM-first |
| **INDEC / INEI / IBGE** | Gubernamental | Nacional | Mensual (rezago 30-45d) | Gratis | Frecuencia 8h vs 45d, datos de góndola real, no encuestas |
| **Kantar / Worldpanel** | Panel de hogares | LATAM selectivo | Trimestral | USD 10K+/informe | Granularidad diaria, multi-retailer, API programática |
| **Keepa / CamelCamelCamel** | Scraping | Amazon solamente | Horaria | EUR 19/mes | Multi-retailer físico, LATAM, canasta cross-tienda |
| **Consultoras boutique** | Fieldwork manual | Por proyecto | A demanda | USD 5K–50K/proyecto | Automatizado, recurrente, verificable |

CLI Market Intelligence ocupa un espacio no cubierto: **datos de góndola LATAM de alta frecuencia a precio de suscripción accesible**. Las alternativas son o globales-caros (Nielsen), o gratuitos-lentos (INEI), o limitados a e-commerce puro (Keepa).

---

*Investment Researcher: Quinn · Fuentes: datos del collector CLI Market, contexto macro de fuentes públicas (BCRP, INDEC, IBGE, Banxico, Banco de la República).*
