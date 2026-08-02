# Ejercicio MRO/CAPEX: equipos de cocina con CLI Market

Fecha de ejecución: 29 de julio de 2026 (America/Lima). Consultas de solo lectura, sin ERP ni compra.

## Alcance

Exploración de renovación de activos operativos no masivos para negocios: equipos de cocina comercial. La hipótesis es que CLI Market puede servir como primera capa de catálogo, precio observable y calidad de señal para un agente de preselección técnica y económica.

## Cobertura encontrada

`market_discover` identificó la línea **Equipos de Cocina** en Perú, con dos retailers especializados:

- Ilumiperú.
- Grupo Nova.

La búsqueda de `licuadora industrial` no devolvió productos, aunque ambos retailers respondieron correctamente. Esto se registra como brecha de catálogo o recuperación, no como evidencia de inexistencia de oferta.

## Caso ejecutado: horno industrial convector a gas

La búsqueda de `horno convector` identificó los siguientes activos de Ilumiperú:

| Activo | Precio observado |
|---|---:|
| Horno industrial convector a gas, 5 bandejas | S/ 10,199 |
| Horno industrial convector a gas, 10 bandejas | S/ 15,999 |
| Horno industrial convector a gas, 12 bandejas | S/ 18,799 |
| Horno industrial convector a gas, 12 bandejas + trolley | S/ 28,590 |

### Lectura capacidad/precio

- El salto de 5 a 10 bandejas cuesta 56.9% más y duplica la capacidad nominal de bandejas.
- El salto de 10 a 12 bandejas cuesta 17.5% más.
- Añadir trolley al modelo de 12 bandejas eleva el precio 52.1% respecto del modelo de 12 bandejas sin trolley.

Esto habilita una hipótesis de evaluación: si la restricción operativa es capacidad, el salto de 5 a 10 bandejas es un primer punto de análisis. No permite todavía seleccionar el mejor activo ni el mejor proveedor.

## Calidad de señal y ocurrencias

### `market_compare`

Para el horno de 5 bandejas, la comparación devolvió un solo retailer: Ilumiperú, a S/ 10,199. No existe benchmark competitivo cross-retailer.

### `market_price_history`

El modelo de 5 bandejas tuvo un solo snapshot registrado. No hay serie suficiente para inferir tendencia de precio.

### `market_promo_detector`

Reportó `insufficient_history`; no es posible determinar autenticidad ni recurrencia de promociones.

### `market_retailer_scorecard`

Ilumiperú reportó:

- Cobertura de siete días: 100%.
- Éxito del conector: 97.1%.
- Normalización de catálogo: 57.5%.
- Disponibilidad observada: 57.5%.
- Competitividad cross-retailer: datos insuficientes.

La disponibilidad refleja el último scrape de catálogo; no equivale a stock en tiempo real.

### `market_price_risk`

La línea `equipos_cocina` devolvió riesgo de precio bajo. La señal debe tratarse con cautela: la herramienta reportó solo tres productos seguidos y no mostró dispersión de precios.

## Resultado del ejercicio

La exploración es útil para un agente de **preselección técnica y económica**, con el siguiente flujo:

```text
Necesidad operativa -> capacidad requerida -> activos candidatos
-> precio de lista observable -> evidencia y cobertura
-> datos técnicos pendientes -> solicitud de cotización técnica
```

CLI Market aporta catálogo y precio observable. Para pasar a una recomendación de compra se debe validar, fuera de esta señal:

- Consumo de gas o energía.
- Dimensiones e instalación.
- Producción por hora y compatibilidad con operación.
- Garantía, mantenimiento y repuestos.
- Certificaciones, seguridad y servicio postventa.
- Cotización B2B, flete, impuestos y plazo de entrega.

## Conclusión

El caso prueba que la perspectiva MRO/CAPEX es viable como exploración inicial: permite detectar una escalera de activos y precios. Sin embargo, la cobertura actual no soporta una comparación competitiva ni una decisión de renovación automática. El agente debe emitir una preselección y escalar a validación técnica y cotización humana.
