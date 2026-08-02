# Caso de uso: innovación y pricing de alcachofa lista para cocinar de La Libertad

**Fecha:** 29 de julio de 2026  
**Ubicación económica:** La Libertad, Perú  
**Ámbito:** desarrollo de producto, inteligencia comercial y pricing; no procura.

## Oportunidad

La propuesta es crear una línea de **alcachofa práctica para consumo doméstico**, transformando una materia prima asociada a la agroindustria regional en una solución de conveniencia: corazones de alcachofa grillados en frasco, alcachofa marinada refrigerada o una base lista para pizza, pasta y ensalada.

La agroexportación de La Libertad ya incluye alcachofa dentro de su canasta relevante. La oportunidad no es replicar el negocio de exportación en fresco, sino desarrollar transformación local, empaque, marca regional y consumo interno.

Fuente de contexto: [Gobierno Regional de La Libertad: agroexportaciones de Chavimochic 2024](https://www.gob.pe/institucion/regionlalibertad/noticias/1105392-agroexportaciones-desde-los-campos-de-chavimochic-se-incrementaron-un-23-en-2024)

## Decisión que habilita

Determinar qué formato de alcachofa debe lanzar una empresa de Virú, Chao o Trujillo para consumo local, en qué gramaje, con qué precio y en qué canal debe iniciar.

| Línea | Uso | Formato inicial |
|---|---|---|
| Alcachofa grillada y marinada | Ensaladas, piqueos y sándwiches | Frasco de 190–280 g |
| Corazones listos para cocinar | Pizza, pasta, arroz y guisos | Bolsa o frasco de 250–400 g |
| Antipasto norteño | Regalo, reunión y consumo premium | Frasco con alcachofa, ají y hierbas |

La innovación no debe basarse solo en “alcachofa gourmet”. Debe resolver fricción para el usuario: evitar limpieza, cocción y preparación lenta.

## Sistema agéntico apoyado en CLI Market

| Agente | Función | Herramientas y salida |
|---|---|---|
| Explorador de categoría | Construye el universo competitivo | `market_discover` y `market_search` con “alcachofa en conserva”, “corazones de alcachofa”, “antipasto” y “vegetales grillados” |
| Normalizador | Elimina comparaciones falsas | Valida peso drenado, ingredientes, gramaje, presentación, marca y `canonical_product_id`; calcula precio por 100 g |
| Arquitecto de precios | Define bandas de precio | `market_compare` para referencias exactamente equivalentes; separa precio de entrada, core y premium |
| Detector de espacio | Formula hipótesis de producto | Identifica formatos, ocasiones de consumo y precios con oferta relativa limitada |
| Diseñador de experimento | Convierte hipótesis en piloto | Propone dos formatos, dos precios, mensajes y umbrales de escala |
| Reality checker | Controla evidencia y riesgos | Revisa cobertura, frescura, equivalencia de producto, promociones e historial antes de recomendar |

## Flujo de trabajo

1. **Mapear oferta.** Consultar surtido en supermercados peruanos y tiendas especializadas. El resultado sirve para observar surtido y presentaciones, no para declarar tamaño de mercado.
2. **Normalizar.** Agrupar solo productos equivalentes en tipo, peso drenado e ingredientes. Un frasco de 190 g no es comparable de forma directa con una bolsa de 400 g.
3. **Construir arquitectura de precios.** Calcular precio por 100 g y separar precio regular de precio promocional. Definir bandas accesible, core y premium.
4. **Diseñar producto.** Priorizar, por ejemplo, un corazón de alcachofa grillado de 220–250 g y una alcachofa marinada con ají amarillo y hierbas de 190–220 g.
5. **Pilotear.** Probar dos precios por SKU y dos mensajes: “lista en minutos para pasta, pizza y ensalada” frente a “antipasto peruano para compartir”.
6. **Decidir.** Escalar, reformular, reposicionar el precio o descartar según recompra rentable, no solo ventas de una semana promocional.

## Diseño de piloto

| Variable | Propuesta |
|---|---|
| SKU A | Corazones de alcachofa grillados, frasco 220–250 g |
| SKU B | Alcachofa marinada con ají amarillo y hierbas, frasco 190–220 g |
| Canales | Retail digital, tiendas gourmet y puntos físicos seleccionados en Trujillo y Lima |
| Precios | Dos puntos por SKU, derivados de sustitutos comparables por precio por 100 g |
| Mensajes | Funcional/conveniencia frente a gastronómico/para compartir |
| Métricas | Conversión, recompra a 30 días, margen neto, ventas sin promoción y canibalización |

## Criterio de éxito

Escalar solo si el producto alcanza recompra rentable sin descuento permanente. Una venta inicial alta por novedad o por promoción no valida por sí sola la innovación.

## Límites y controles

- CLI Market aporta observación de surtido, precios y promociones de retail formal digital; no sustituye estudios de disponibilidad de materia prima, costo industrial, vida útil, permisos sanitarios, prueba sensorial ni demanda del canal tradicional.
- El sistema debe conservar fuente, fecha, retailer, producto, peso drenado, método de coincidencia y confianza de cada dato.
- Toda comparación requiere equivalencia explícita de producto y presentación. Si la cobertura es parcial, la recomendación debe mostrarse como hipótesis de piloto, no como una verdad de mercado.
- No deben realizarse claims nutricionales, regulatorios o de salud sin evidencia y validación humana especializada.

## Recomendación

Implementar primero un radar de categoría y un piloto controlado. El objetivo es aprender qué combinación de formato, receta, precio y canal consigue recompra rentable, antes de decidir una expansión regional o nacional.
