# Ejercicio: construccion y continuidad operativa con CLI Market

Fecha: 29 de julio de 2026. Ejecucion de solo lectura, sin ERP, carrito, checkout ni compra.

## Perspectiva explorada

Industria: construccion y mantenimiento de obra.

Beneficio analizado: continuidad operativa de la cuadrilla. El objetivo no es comprar la herramienta mas barata, sino estandarizar herramientas, baterias y repuestos para reducir paradas, incompatibilidades y reemplazos improvisados.

## Oferta encontrada

La linea `hogar` devolvio una oferta relevante: 61 taladros percutores, con marcas Bosch, DeWalt, Makita, Einhell, Stanley y otras.

La busqueda de `generador electrico` no devolvio resultados, aunque ambos retailers de la linea respondieron. Esto se interpreta como una brecha de catalogo o recuperacion, no como inexistencia de oferta.

## Caso ejecutado

Producto de referencia: **Taladro Percutor Bosch GSB 18V 50 + bateria 2 Ah**.

- Precio observado en Promart: S/ 499.
- Precio de lista observado: S/ 649.
- Descuento visible: 23%.
- Stock reportado en catalogo: 63 unidades.
- Canonical product ID: `prod_bosch_general_1unit`.

## Beneficio operativo esperado

La recomendacion que un agente debe evaluar no es: "comprar Bosch porque tiene 23% de descuento".

La pregunta correcta es:

> Conviene estandarizar la flota en una misma plataforma de bateria para reducir tiempo muerto, duplicidad de cargadores, incompatibilidad de repuestos y reemplazo improvisado?

CLI Market puede aportar el primer filtro:

- Modelo, marca, voltaje y accesorios observables.
- Precio de referencia.
- Stock visible.
- Deteccion de promociones.
- Oferta de herramientas relacionadas.

Para tomar una decision se deben anadir fuera de CLI Market:

- Compatibilidad entre baterias, cargadores y otras herramientas.
- Torque, ciclo de trabajo y exigencia de uso.
- Garantia, servicio tecnico y repuestos.
- Tiempo y costo de una cuadrilla detenida.
- Disponibilidad del proveedor local y SLA de reposicion.

## Desempeno de tools observado

### `market_search`

Funciono bien para descubrir oferta y especificaciones basicas. Recupero una gama amplia de taladros y datos de precio, descuento y stock.

### `market_compare`

Devolvio cero comparables, aunque el producto aparecia en catalogo. No permite establecer benchmark competitivo para el modelo evaluado.

### `market_substitutes`

No encontro candidatos. En este caso no reemplaza una matriz tecnica de equivalencias.

### `market_price_history`

Devolvio un unico snapshot, fechado el 19 de junio. No hay base para inferir tendencia de precio.

### `market_retailer_scorecard`

Promart reporto:

- Salud de conector: buena.
- Cobertura semanal: 26.5%.
- Normalizacion de catalogo: 22.5%.
- Stock reportado del catalogo: 95.0%.
- Competitividad cross-retailer: datos insuficientes.

La cobertura y normalizacion reducen la confianza de cualquier conclusion amplia. El stock observado no equivale a inventario en tiempo real.

### `market_price_risk`

La linea `hogar` devolvio riesgo moderado, con intensidad promocional de 42.72%. Es una senal de toda la linea, no una afirmacion especifica para taladros.

## Conclusion

La industria es viable para CLI Market, pero el beneficio mas potente no es price shopping: es gestion de disponibilidad y estandarizacion de activos de obra.

En el estado actual, un agente puede hacer preseleccion y abrir una solicitud de cotizacion tecnica. No puede decidir que herramienta comprar ni asegurar continuidad operativa sin fichas tecnicas, garantia, repuestos y condiciones de servicio.
