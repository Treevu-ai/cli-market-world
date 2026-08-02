# Casos de uso: CLI Market + ERP + sistemas agenticos

## Marco comun: ERP transaccional + CLI Market como inteligencia externa

En los cinco casos, el ERP conserva la verdad operativa: maestro de items, inventario, contratos, costos, ventas, presupuestos, aprobaciones y contabilidad. CLI Market aporta observacion externa de precios, surtido, riesgo, promociones y senales de compra. El sistema agentico conecta ambos y produce propuestas, nunca cambios comerciales criticos automaticos.

```text
ERP/POS/PMS -> contexto interno y restricciones
Agente -> valida identidad y presentacion -> consulta CLI Market
Agente -> calcula impacto con reglas internas
ERP -> recibe propuesta, evidencia y workflow de aprobacion
Responsable -> aprueba/rechaza -> ERP ejecuta y registra resultado
```

La base funcional es un catalogo de equivalencias:

- SKU ERP, EAN/UPC, marca, presentacion y unidad de medida.
- `canonical_id` o producto identificado en CLI Market.
- Nivel de confianza del match.
- Regla de comparacion: precio por unidad, no solo precio por empaque.
- Fecha, retailer, pais, cobertura y evidencia de cada observacion.

## 1. Hotel: agente de abastecimiento segun ocupacion, eventos y riesgo de precios

### Objetivo

Reducir quiebres y compras urgentes sin sobreinventario, cuidando el costo por habitacion ocupada.

### Disparador

Cada manana, o cuando un articulo critico cae bajo el umbral de cobertura definido en ERP: por ejemplo, menos de siete dias para leche, azucar, detergente, amenities o papel.

### Datos que recibe desde ERP/PMS

- Ocupacion real y proyectada.
- Eventos, banquetes, desayunos previstos y calendario de alta demanda.
- Inventario por almacen y area.
- Consumo historico por habitacion ocupada.
- Requisiciones pendientes, ordenes abiertas y lead time.
- Proveedores homologados, contratos, precios negociados y presupuesto.

### Flujo del agente

1. Calcula demanda esperada por area: desayuno, housekeeping, lavanderia, amenities y mantenimiento.
2. Identifica el faltante proyectado y verifica si un contrato vigente lo cubre.
3. Si se requiere inteligencia externa, consulta `market_search` para validar productos equivalentes y presentacion.
4. Construye la canasta con `market_basket` o `market_optimize_purchase`.
5. Consulta `market_procurement_signal`, `market_price_risk` y, para items criticos, `market_price_history` o `market_price_forecast`.
6. Clasifica la accion: comprar bajo contrato, adelantar compra, monitorear, sustituir con aprobacion o escalar a compras por riesgo de quiebre.

### Salida hacia ERP

Una propuesta de abastecimiento por centro de costo con:

- SKU interno y equivalencia externa validada.
- Cantidad sugerida y dias de cobertura resultante.
- Comparacion contra presupuesto, ultimo precio pagado y contrato.
- Alternativas solo para productos previamente habilitados.
- Evidencia de mercado, nivel de confianza y fecha.
- Recomendacion: crear solicitud de compra, revisar contrato o no actuar.

### Aprobador y KPIs

Jefe de compras u operaciones. El hotel nunca permite que el agente emita una orden de compra o cambie proveedor sin aprobacion.

- Costo de abastecimiento por habitacion ocupada.
- Tasa de quiebres por area.
- Compras urgentes versus planificadas.
- Ahorro validado contra la linea base del ERP.
- Dias de inventario y merma.

### Limite

Un precio observado en retail digital es una senal de mercado, no un reemplazo del precio B2B, flete, credito, impuestos ni disponibilidad contractual.

## 2. Restaurante: agente de proteccion de margen por plato

### Objetivo

Detectar que ingredientes estan erosionando el margen de carta antes de que el problema aparezca en el cierre mensual.

### Disparador

Revision semanal; tambien se activa si el food cost real de un plato supera su banda objetivo o si un insumo critico aumenta de precio.

### Datos que recibe desde ERP/POS

- Recetas, gramajes, mermas y rendimientos.
- Ventas por plato, mix de carta y margen objetivo.
- Costo teorico versus costo real.
- Inventario de cocina, ordenes abiertas y proveedores.
- Reglas culinarias: alergenos, origen, calidad y sustitutos aprobados.

### Flujo del agente

1. Explota el recetario: plato -> ingrediente -> cantidad -> costo actual.
2. Prioriza ingredientes segun impacto en margen y rotacion del plato.
3. Usa `market_search` y `market_compare` para verificar referencias comparables.
4. Usa `market_basket` para ver el efecto de una compra consolidada de ingredientes.
5. Consulta `market_price_risk`, `market_procurement_signal` y `market_promo_detector`.
6. Calcula escenarios dentro del ERP: mantener receta y comprar anticipadamente; cambiar de proveedor; usar sustituto aprobado; ajustar porcion; elevar precio de carta; o retirar temporalmente el plato.

### Salida hacia ERP

Una alerta de margen que vincula:

```text
Plato -> insumo -> riesgo de precio -> impacto estimado -> accion propuesta
```

Ademas, crea borradores de requisicion para compras y casos de revision para el comite de menu.

### Aprobador y KPIs

Chef ejecutivo aprueba cambios de receta; compras aprueba abastecimiento; revenue o gerencia aprueba cambios de carta.

- Food cost por plato.
- Margen bruto y contribucion por plato.
- Diferencia entre costo teorico y real.
- Porcentaje de ingredientes criticos con monitoreo.
- Merma y compras de emergencia.

### Limite

CLI Market puede aportar senales externas de precio y promociones; la decision culinaria debe respetar la ficha tecnica y la calidad del plato.

## 3. Cafeterias: agente de reposicion y rentabilidad por local

### Objetivo

Controlar la canasta de alta rotacion —cafe, leche, azucar, jarabes, vasos, panaderia y limpieza— y proteger el margen por bebida en cada tipo de tienda.

### Disparador

Revision de reposicion por tienda, antes del corte de compra; alertas adicionales si el inventario baja de cobertura minima o cambia el costo de un insumo critico.

### Datos que recibe desde ERP/POS

- Ventas y consumo por local.
- Tipo de tienda: express, premium, universidad, mall o corporativa.
- Inventario, minimos, maximos y lead time.
- Surtido autorizado por local.
- Costo por bebida, margen objetivo y presupuesto.

### Flujo del agente

1. Agrupa locales por comportamiento de demanda, no solo por geografia.
2. Calcula necesidades de reposicion por cluster y tienda.
3. Ejecuta `market_basket` para evaluar la canasta de reposicion.
4. Usa `market_search` para validar marcas y formatos; usa `market_substitutes` solo cuando la politica de calidad lo permite.
5. Activa `market_price_alerts` para insumos de alta incidencia.
6. Usa `market_trending`, `market_price_forecast` y `market_retailer_scorecard` para anticipar cambios y evaluar la calidad de la evidencia.
7. Si hay nueva categoria —por ejemplo, bebida vegetal o snack— propone un piloto de surtido, no un alta automatica.

### Salida hacia ERP

- Propuesta de reposicion por local.
- Clasificacion de items: no sustituible, sustituible con prueba o sustituible libremente.
- Riesgo de impacto por bebida.
- Caso de piloto de surtido con tiendas sugeridas, hipotesis y metricas.
- Alerta si un insumo amenaza el margen de una bebida estrategica.

### Aprobador y KPIs

Compras aprueba la reposicion; category manager aprueba el surtido; operaciones valida la viabilidad por tienda.

- Margen por bebida.
- Quiebres de stock.
- Costo de canasta por tienda.
- Diferencia entre compra presupuestada y ejecutada.
- Tasa de exito de pilotos de surtido.

### Limite

La alternativa de menor precio no gana automaticamente: una cafeteria premium debe incorporar estandares de marca, consistencia y experiencia del cliente.

## 4. Innovacion: agente de oportunidades y experimentos comerciales

### Objetivo

Convertir senales externas de categorias, precios y surtido en un pipeline priorizado de pilotos comerciales.

### Disparador

Ciclo mensual de innovacion, propuesta de una nueva categoria o solicitud de analisis de expansion a un pais o canal.

### Datos que recibe desde ERP y gestion de portafolio

- Portafolio actual, ventas, margen, rotacion y productos descontinuados.
- Costos estimados, capacidad productiva y proveedores.
- Presupuesto de innovacion.
- Proyectos y pilotos anteriores, con resultados.
- Mercados, canales y segmentos objetivo.

### Flujo del agente

1. Convierte una tesis en hipotesis comprobables: categoria, formato, pais, rango de precio y canal.
2. Parte de `market_intel_brief`, `market_scores` y `market_affordability`.
3. Consulta `market_discover`, `market_search` y `market_compare` para mapear surtido y precio observable.
4. Evalua `market_trending`, `market_price_risk` y `market_promo_detector` para diferenciar oportunidad estructural de ruido promocional.
5. Usa `market_arbitrage` como senal exploratoria internacional, sin tratarlo como margen de importacion.
6. Consulta `market_informal_signal` para mostrar que parte del mercado no esta observada.
7. Puntua la oportunidad con evidencia externa mas factibilidad interna.

### Salida hacia ERP/PPM

Una ficha de oportunidad con:

- Hipotesis de negocio.
- Evidencia observada y fecha.
- Datos internos empleados.
- Riesgos y vacios de informacion.
- Pais, canal y formato sugeridos.
- Presupuesto preliminar.
- Diseno de piloto, metrica de exito y condicion de descarte.
- Recomendacion: explorar, validar, pilotear o descartar.

### Aprobador y KPIs

Comite de innovacion, estrategia y finanzas.

- Tiempo desde hipotesis hasta piloto.
- Porcentaje de proyectos descartados temprano con evidencia suficiente.
- Tasa de aprendizaje por piloto.
- Porcentaje de pilotos que escalan.
- Precision de la priorizacion inicial.

### Limite

Cobertura de catalogo o precio de gondola no equivalen a tamano de mercado, demanda comprobada ni disposicion a pagar.

## 5. Trade marketing y revenue & pricing: agente de respuesta competitiva rentable

### Objetivo

Unificar precio externo, promociones, margen interno, inventario y objetivos comerciales para decidir cuando actuar y cuando no reaccionar.

### Disparador

Monitoreo semanal por SKU-retailer; alertas si existe una variacion relevante de precio, promocion, riesgo de margen o desviacion frente al rango competitivo definido.

### Datos que recibe desde ERP, CRM y BI

- Lista de precios, costo neto, margen minimo y politicas de descuento.
- Ventas, inventario, presupuesto de trade y calendario promocional.
- Rentabilidad por SKU, canal, cliente y region.
- SKUs estrategicos, equivalencias competitivas y retailers prioritarios.
- Sell-in, sell-out y elasticidades propias cuando esten disponibles.

### Flujo del agente

1. Selecciona SKUs estrategicos y los vincula con productos comparables, cuidando presentacion y unidad.
2. Usa `market_search` para confirmar la identidad del producto.
3. Ejecuta `market_compare` por pais, retailer y linea.
4. Analiza tendencia con `market_price_history`, `market_price_forecast` y `market_price_risk`.
5. Consulta `market_promo_detector` para no sobrerreaccionar a descuentos poco confiables.
6. Usa `market_retailer_scorecard` para ponderar la confianza de cada observacion.
7. Cruza la senal con costo, margen, stock, objetivos y presupuesto del ERP.
8. Recomienda una accion: sostener precio, ajustar precio, responder con promocion, proteger margen y no responder, o investigar por falta de comparabilidad o evidencia.

### Salida hacia ERP

Una matriz `SKU x retailer x semana` con:

- Precio observado, presentacion y evidencia.
- Estado promocional, frescura y confianza.
- Indice competitivo.
- Impacto estimado sobre margen.
- Accion recomendada y responsable.
- Borrador de cambio comercial sujeto a aprobacion.

### Aprobador y KPIs

Pricing, trade marketing y direccion comercial, segun el umbral de impacto.

- Indice competitivo de precio.
- Margen neto por SKU/canal.
- ROI de promociones.
- Tiempo desde deteccion hasta decision.
- Porcentaje de alertas correctas versus falsas alarmas.
- Cumplimiento de bandas de precio y presupuesto trade.

### Limite

CLI Market aporta la senal de mercado; el ERP aporta rentabilidad y capacidad interna. Ninguno por separado debe definir un cambio de precio o promocion.

