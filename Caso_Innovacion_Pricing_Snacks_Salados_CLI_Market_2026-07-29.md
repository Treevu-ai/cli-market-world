# Caso ejecutado: innovación y pricing de snacks salados

**Fecha:** 29 de julio de 2026  
**Mercado y canal:** Perú, supermercados online  
**Ámbito:** desarrollo de producto y estrategia de precios; no procura ni optimización de compras.

## Decisión que se busca habilitar

Definir si conviene probar una nueva línea de **chifles con sabor peruano**, con un formato individual para descubrimiento y uno para compartir, y establecer los precios que deben entrar a prueba. No se propone un PVP definitivo: faltan costos industriales, márgenes por canal, impuestos, inversión promocional y objetivos de contribución.

## Hipótesis de producto

La oportunidad no es lanzar un chifle genérico. La oferta ya incluye variantes tradicional, leche de tigre, acevichado y jalapeño. La hipótesis es una plataforma con un sabor regional reconocible —por ejemplo, ají amarillo y limón— y una arquitectura de formatos con roles distintos:

| Formato propuesto | Rol | Precio experimental |
|---|---|---:|
| 130–150 g | Descubrimiento, prueba de sabor y percepción premium | S/7.90 vs. S/8.90 |
| 250 g | Compartir, valor por porción y repetición | S/9.90 vs. S/11.20 |

Los puntos de prueba se anclan en precios observados. Deben validarse con costo y margen antes de presentarse a un retailer.

## Evidencia observada con CLI Market

### Búsqueda focalizada: `chifles`

| Producto observado | Retailer | Precio | Lectura |
|---|---|---:|---|
| Cuisine & Co Chifles Norteños 100 g | Wong | S/6.80 | Referencia de entrada por formato pequeño |
| Inka Chips Tradicional 135 g | Metro / Wong | S/8.00 | Referencia de chifle de marca y sabor tradicional |
| Inka Chips Leche de Tigre 130 g | Metro | S/8.00 | Evidencia de sabor inspirado en gastronomía peruana |
| Voraz Leche de Tigre 130 g | Plaza Vea / Vivanda | S/8.50–S/9.10 | Banda superior para formato individual saborizado |
| Crickets Salados 250 g | Plaza Vea | S/9.80 | Formato compartir con promoción observada |
| Crickets 250 g | Metro / Wong | S/11.20 | Precio regular comparable para el mismo formato |
| Crickets 500 g | Wong | S/21.90 | Referencia de formato familiar |

### Anclas competitivas adyacentes

La búsqueda de `papas fritas` devolvió referencias comparables y también productos preparados; por esa mezcla no debe utilizarse como un universo limpio de snacks. Como anclas puntuales, Lay’s Clásicas 140 g apareció a S/5.50 en promoción y Tiyapuy Papa Nativa 142 g entre S/6.90 y S/7.60.

### Validación exacta: `Chifles Salados Crickets 250g`

La comparación exacta sí identificó el mismo SKU en tres retailers:

| Retailer | Precio | Precio por 100 g | Interpretación |
|---|---:|---:|---|
| Plaza Vea | S/9.80 | S/3.92 | Precio promocional observado; lista S/11.20 |
| Metro | S/11.20 | S/4.48 | Precio regular observado |
| Wong | S/11.20 | S/4.48 | Precio regular observado |

El formato de 250 g ofrece valor por gramo comparable o inferior al snack masivo promocionado, sin obligar a abandonar una propuesta de sabor diferenciada. La dispersión de 14.3% entre S/9.80 y S/11.20 muestra que el posicionamiento por canal y la promoción son determinantes.

## Lectura de pricing

1. **Formato individual:** el rango observado para chifles de 100–150 g es S/6.80–S/9.10. Un test S/7.90–S/8.90 mantiene coherencia con la categoría y permite medir cuánto valor agrega el sabor.
2. **Formato compartir:** S/9.90 es una entrada cercana al precio promocional observado; S/11.20 prueba la disposición a pagar el precio regular de referencia. El objetivo no es vender barato, sino demostrar que el valor por porción y el sabor pueden sostener rotación.
3. **No depender de descuento:** la línea debe escalar solo si el formato de 250 g mantiene rotación a precio regular. Una alta venta exclusivamente promocional sería una alerta de elasticidad y no una validación de innovación.

## Diseño de piloto

1. Probar un sabor regional reconocible en 130–150 g y 250 g.
2. Asignar los dos precios experimentales por formato en tiendas o audiencias comparables.
3. Alternar el mensaje de exhibición: **“sabor peruano para compartir”** frente a **“snack intenso para picar”**.
4. Medir conversión, recompra a 30 días, mezcla entre formatos, margen neto, tasa de compra con promoción y canibalización de sabores existentes.
5. Decidir expansión por formato, sabor y canal, no por ventas agregadas de una única semana promocional.

## Invocaciones y límites de la evidencia

- `market_search` permitió mapear competidores y presentaciones. La consulta amplia de papas fritas fue ruidosa, por lo que se usó solo como referencia puntual y no como base de cálculo.
- `market_compare` funcionó al acotar la consulta al SKU exacto de Crickets 250 g. Esto confirma que la comparación debe validarse por nombre, gramaje y presentación antes de usarla en pricing.
- `market_price_history` devolvió una sola observación para Plaza Vea; no alcanza para estimar tendencia ni elasticidad temporal.
- `market_promo_detector` reportó historial insuficiente para el SKU exacto, por lo que no permite atribuir la diferencia de precio a una mecánica promocional completa.
- `market_substitutes` no devolvió sustitutos útiles para el producto exacto; la sustitución debe probarse en el experimento comercial.
- `market_price_risk` clasificó el entorno de supermercados PE como moderado, con intensidad promocional alta y dispersión de precios. Es contexto para diseñar el piloto, no una proyección de margen.
- La cobertura de los retailers observados en los últimos siete días fue parcial en Plaza Vea, Metro y Wong. Los resultados reflejan retail online formal y no representan bodegas, mercados ni la totalidad del canal tradicional.

## Recomendación

Avanzar con un piloto acotado de innovación y pricing, no con lanzamiento nacional. La evidencia respalda una línea de chifles saborizados con arquitectura 130–150 g / 250 g; todavía no respalda un PVP final ni una previsión de demanda. El primer criterio de éxito debe ser recompra rentable sin descuento permanente.
