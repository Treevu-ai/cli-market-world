## §1 — Resumen Ejecutivo

- **Inflación 7d no determinable.** La totalidad de las líneas registra `avg_before = 0.0` y `delta_pct = 0`, lo que indica que esta es la primera ventana de recolección del piloto. No existe aún una serie histórica que permita calcular variación semanal. El sistema acumulará historia en los próximos ciclos de 8 horas.
- **Canasta básica CLI Market: PEN 64.39 en la tienda más barata, ARS 14,936.19 en la más cara.** Dentro de una misma moneda, el spread es moderado: 1.38× en PEN (Plaza Vea vs. Wong), 1.45× en ARS (Vea AR vs. Jumbo AR) y 1.54× en MXN (Chedraui vs. HEB). En BRL la comparación no es homogénea porque las tiendas tienen distinto número de ítems capturados.
- **No se detectan spreads anómalos (>5×) ni movimientos extremos (>20%).** El spread máximo observado es 3.0× en jabón (ARS). Los arrays `top_risers` y `top_fallers` están vacíos, consistente con la ausencia de historia comparativa.
- **Cobertura del collector:** ~45,400 precios activos en 6 líneas de negocio (departamentales, electro, farmacias, hogar, moda, supermercados) y 6 monedas (ARS, BRL, CLP, COP, EUR, MXN, PEN). La línea Supermercados concentra la mayor profundidad con 23,980 SKUs.
- **Primera fotografía, no tendencia.** Sin ventana previa no es posible afirmar dirección inflacionaria ni cambio de régimen. Se recomienda al cliente monitorear la evolución en las próximas 2–3 semanas para obtener la primera señal direccional.

---

## §2 — Inflación Observada 7d

### ⚠️ Serie histórica insuficiente

Todos los registros del array `inflation` presentan `avg_before = 0.0` y `delta_pct = 0`. Esto indica que el collector no cuenta aún con una ventana de comparación de al menos 7 días. La tabla siguiente expone lo disponible — exclusivamente el precio promedio actual por línea y moneda, sin variación calculable.

| Línea | Moneda | Precio Prom. Actual | Precio Prom. Anterior | Δ% 7d | Señal |
|---|---|---|---|---|---|
| Tiendas Departamentales | ARS | 147,787.20 | — | — | ⏳ |
| Tiendas Departamentales | BRL | 222.18 | — | — | ⏳ |
| Electro y Tecnología | ARS | 193,756.67 | — | — | ⏳ |
| Electro y Tecnología | BRL | 1,082.23 | — | — | ⏳ |
| Electro y Tecnología | CLP | 122,172.62 | — | — | ⏳ |
| Electro y Tecnología | EUR | 574.19 | — | — | ⏳ |
| Electro y Tecnología | MXN | 6,160.78 | — | — | ⏳ |
| Farmacias y Salud | BRL | 72.47 | — | — | ⏳ |
| Farmacias y Salud | MXN | 564.82 | — | — | ⏳ |
| Hogar y Construcción | ARS | 101,878.80 | — | — | ⏳ |
| Hogar y Construcción | PEN | 342.14 | — | — | ⏳ |
| Moda y Vestimenta | BRL | 192.31 | — | — | ⏳ |
| Supermercados | ARS | 6,281.16 | — | — | ⏳ |
| Supermercados | BRL | 116.02 | — | — | ⏳ |
| Supermercados | COP | 28,331.15 | — | — | ⏳ |
| Supermercados | MXN | 191.50 | — | — | ⏳ |
| Supermercados | PEN | 33.31 | — | — | ⏳ |

### Narrativa

No es posible identificar líneas líderes en inflación ni deflación. La señal agregada del collector **no puede calcularse** porque ninguna línea dispone de una ventana histórica de comparación. Este es el estado esperable para un piloto en su primera ejecución: los promedios actuales (`avg_now`) constituyen la línea de base contra la cual se computarán las variaciones en los próximos ciclos de recolección (cada 8 horas).

**Se recomienda** que el cliente evalúe estos datos como fotografía de nivel de precios — no como tendencia. La interpretación de "inflación observada desde góndola" será viable a partir del séptimo día de operación continua del collector.

> **Disclaimer:** Inflación observada desde góndola online. No reemplaza el IPC oficial (INEI, INDEC, IBGE, DANE, INEGI). Los promedios son aritméticos simples sobre SKUs capturados; no incorporan ponderadores de gasto de los hogares.

---

## §3 — Canasta Básica

### Tabla de canasta por tienda

| Tienda | País inferido | Ítems / 10 | Total | Moneda |
|---|---|---|---|---|
| Plaza Vea | Perú | 10 | 64.39 | PEN |
| Metro | Perú | 10 | 76.39 | PEN |
| Wong | Perú | 10 | 88.75 | PEN |
| Vea AR | Argentina | 10 | 10,286.90 | ARS |
| Jumbo AR | Argentina | 10 | 14,936.19 | ARS |
| Chedraui | México | 10 | 207.00 | MXN |
| HEB | México | 10 | 319.20 | MXN |
| Mambo BR | Brasil | 6 | 65.82 | BRL |
| Sam's Club BR | Brasil | 6 | 95.19 | BRL |
| Carrefour BR | Brasil | 9 | 589.73 | BRL |

> **Nota sobre USD:** Los totales en dólares no están disponibles en este corte de datos. La conversión a USD que aparece en el array `inflation` utiliza FX estático y es aproximada. Para la canasta básica, los valores en moneda local son la referencia primaria.

### Análisis de spreads por moneda homogénea

| Moneda | Tienda más barata | Tienda más cara | Spread (×) | Diferencia absoluta |
|---|---|---|---|---|
| PEN | Plaza Vea (64.39) | Wong (88.75) | 1.38 | 24.36 PEN |
| ARS | Vea AR (10,286.90) | Jumbo AR (14,936.19) | 1.45 | 4,649.29 ARS |
| MXN | Chedraui (207.00) | HEB (319.20) | 1.54 | 112.20 MXN |

Los spreads dentro de una misma moneda se mantienen en el rango de 1.38× a 1.54×, lo cual es consistente con mercados de retail formal urbano con competencia efectiva. No se observan divergencias que sugieran segmentación extrema ni fallas de arbitraje entre cadenas. Las tiendas brasileñas no se incluyen en la comparación directa porque difieren en el número de ítems capturados (6 vs. 9), lo que distorsiona el total.

### Spreads a nivel de producto individual

El análisis fino producto por producto (`canasta_spreads`) revela que los spreads más amplios se concentran en Argentina, donde 6 de los 10 ítems presentan razones superiores a 2.0× (todos con status `warn`):

| Producto | Moneda | Spread (×) | Avg Price | Min–Max |
|---|---|---|---|---|
| Jabón | ARS | 3.00 | 1,635.90 | 1.35 – 4,905.00 |
| Queso | ARS | 2.93 | 314.99 | 6.97 – 931.03 |
| Pan | ARS | 2.91 | 853.95 | 2.19 – 2,486.40 |
| Pollo | ARS | 2.67 | 7,533.48 | 21.10 – 20,135.45 |
| Aceite | ARS | 2.65 | 1,212.89 | 143.00 – 3,352.67 |
| Jabón | PEN | 2.47 | 44.35 | 2.63 – 112.00 |
| Jabón | COP | 2.44 | 68,916.67 | 12,500.00 – 181,000.00 |
| Huevos | ARS | 2.22 | 93.77 | 23.62 – 232.19 |

En el resto de los ítems y monedas, los spreads son inferiores a 2.0×, con varios productos por debajo de 0.20× indicando una convergencia casi total de precios entre tiendas (arroz PEN 0.10×, azúcar PEN 0.05×, leche PEN 0.05×).

**Interpretación:** los spreads elevados en ARS son consistentes con un entorno inflacionario que genera dispersión de precios entre cadenas con distinta velocidad de ajuste. No obstante, ningún spread supera el umbral de anomalía (5×), por lo que no se activan alertas de dislocación de mercado.

### Comparación con referencias externas

No se incluyen en este corte referencias externas (salario mínimo, canasta oficial) que permitan contextualizar los valores absolutos. Esta funcionalidad está prevista para iteraciones posteriores del reporte.

### Trazabilidad IPC — CANASTA_IPC_MAP

Cada producto de la canasta CLI Market se mapea a su división y subclase oficial del IPC (referencia metodológica INEI). Las ponderaciones corresponden a la estructura de la canasta del IPC de Perú y se incluyen únicamente como guía de relevancia relativa.

| Producto CLI | División IPC | Subclase IPC | Ponderación |
|---|---|---|---|
| Leche | Alimentos y Bebidas No Alcohólicas | Leche, queso y huevos | 5.03% |
| Arroz | Alimentos y Bebidas No Alcohólicas | Pan y cereales | 4.82% |
| Aceite | Alimentos y Bebidas No Alcohólicas | Aceites y grasas | 3.41% |
| Azúcar | Alimentos y Bebidas No Alcohólicas | Azúcar, mermelada, chocolate | 2.78% |
| Huevos | Alimentos y Bebidas No Alcohólicas | Leche, queso y huevos | 0.91% |
| Pan | Alimentos y Bebidas No Alcohólicas | Pan y cereales | 3.52% |
| Café | Alimentos y Bebidas No Alcohólicas | Café, té y cacao | 0.88% |
| Pollo | Alimentos y Bebidas No Alcohólicas | Carne | 7.12% |
| Queso | Alimentos y Bebidas No Alcohólicas | Leche, queso y huevos | 1.45% |
| Jabón | Bienes y Servicios Diversos | Cuidado personal | 2.91% |

**Ponderación total capturada:** 32.83% de la canasta del IPC de referencia, concentrada principalmente en la división Alimentos y Bebidas No Alcohólicas (29.92%) más una fracción de Bienes y Servicios Diversos (2.91%). La división Alimentos representa el núcleo de la canasta CLI Market, lo cual es apropiado para un indicador de alta frecuencia basado en precios de góndola.

### Nota metodológica

> La canasta CLI Market consiste en 10 productos de consumo diario (leche, arroz, aceite, azúcar, huevos, pan, café, pollo, queso, jabón). Los precios corresponden a retail formal urbano y se recolectan cada 8 horas desde plataformas VTEX, Shopify y Magento. No replica la canasta completa del IPC nacional. Los totales por tienda representan una suma simple de los precios unitarios promedio por ítem; no están ponderados por participación en el gasto de los hogares. Las comparaciones entre monedas son indicativas y no implican paridad de poder adquisitivo.

---

*Fuente: CLI Market Price Pulse — corte generado 2026-06-02T19:51:34 UTC. Datos crudos en `ops/generated/prompts/prompt-financial-analyst.md`. CANASTA_IPC_MAP extraído de `market_spread.py:19-30`.*
