# Informe de ejercicios CLI Market sin ERP

Fecha de ejecucion: 29 de julio de 2026 (America/Lima). Algunas respuestas de API se registran en UTC del 30 de julio.

## Alcance y criterio

Se ejecutaron ejercicios de solo lectura para los cinco casos planteados: hotel, restaurante, cafeterias, innovacion de producto, y trade marketing/revenue & pricing. No se uso ERP, carrito, checkout ni se escribio informacion en CLI Market.

CLI Market se uso como fuente de senales de gondola digital: productos, precios observados, promociones, riesgo y cobertura. No se interpretan estos resultados como cotizaciones B2B, demanda, ventas, margenes, inventario contractual ni IPC oficial.

Regla aplicada: un resultado solo se convierte en recomendacion cuando marca, presentacion, unidad y comparabilidad estan validadas. Un match parcial, una respuesta vacia, historial insuficiente o error de endpoint se registra como una ocurrencia y bloquea una conclusion fuerte.

## Resumen ejecutivo

1. La senal agregada para supermercados de Peru fue `buy_now`, pero con riesgo moderado por intensidad promocional alta. Es un indicador de timing, no una orden de compra.
2. Hubo comparables validos para leche evaporada Gloria 390 g, lavavajillas Sapolio Manzana 800 g, y cafe instantaneo Cafetal 180 g. Sin embargo, varios tienen historial insuficiente para inferir tendencia o autenticidad promocional.
3. La canasta HORECA no fue utilizable porque resolvio un aceite solicitado como un pack de arroz mas aceite. Se rechazo el total calculado.
4. Las busquedas y comparaciones mostraron discrepancias: productos recuperados en busquedas amplias no siempre aparecen en una busqueda exacta; algunos `market_compare` devolvieron cero aun cuando `market_search` o `market_price_history` mostraban observaciones.
5. Para innovacion, el yogurt funcional estilo kefir es una hipotesis de piloto, no una oportunidad confirmada. El rango observado es util para disenar pruebas, pero no para definir un PVP definitivo.

## Contexto agregado: hotel, restaurante y compras

Tools: `market_intel_brief`, `market_procurement_signal`, `market_price_risk`, `market_informal_signal`.

- Senal de procurement: `buy_now`; motivo reportado: canasta bajo baseline.
- Riesgo de precios: `moderate`; motivo reportado: actividad promocional alta.
- Intensidad promocional: entre 35.83% y 43.16%, segun la herramienta y corte utilizado.
- Dispersion de precios: entre 9.49% y 11.01%.
- Momentum de precios de basicos a 7 dias: -1.4% en la consulta agregada.
- Cobertura formal de supermercados: 64.7%, confianza `warn`. La herramienta aclara que no cubre ferias, mercados de abastos ni venta ambulante.

Decision sin ERP: cotizar y monitorear compras cercanas; no adelantar compras masivas ni presentar esta senal como inflacion oficial o evidencia de costos B2B.

## Ejercicio 1: hotel/HORECA - validacion de leche evaporada

Producto: Leche evaporada Gloria lata 390 g.

| Presentacion observada | Retailer | Precio | Precio unitario estimado |
|---|---:|---:|---:|
| Lata individual 390 g | Metro | S/ 4.20 | S/ 4.20 por lata |
| Pack de 6 latas | Makro / Plaza Vea | S/ 23.30 | S/ 3.88 por lata |
| Pack de 12 latas | Vega | S/ 45.60 | S/ 3.80 por lata |

Hallazgo: los packs parecen mas eficientes por lata si el contenido declarado es correcto. Esto habilita una hipotesis de compra por volumen, pero exige validar necesidad, almacenamiento, minimos de compra, flete y condiciones comerciales.

Ocurrencia: una busqueda estricta de `Leche Gloria UHT 1L` devolvio un pack de tres unidades de leche para ninos, no una unidad individual equivalente. Se excluyo de cualquier comparacion.

## Ejercicio 2: canasta HORECA - resultado rechazado

Items enviados: leche evaporada Gloria 390 g, arroz superior 750 g y aceite vegetal 900 ml.

Resultado de `market_basket`: solo encontro un item y resolvio el aceite como `Pack Cuisine & Co: Arroz Extra Anejo 5kg + Aceite Vegetal 900ml`. El total devuelto fue S/ 200.40 para seis unidades, en Wong.

Decision: resultado rechazado. El producto resuelto no es una botella de aceite equivalente y la canasta estaba incompleta. No se usa para ahorro, comparacion de retailer ni recomendacion de compra.

Leccion para el agente: exigir completitud de canasta y validacion de cada `resolved_name` antes de calcular ranking, ahorro o TCO.

## Ejercicio 3: hotel - insumo de limpieza profesional

Producto explorado: Lavavajillas Sapolio Limon Botella 4L Paquete 4 unidades.

Ocurrencia: el producto aparecio en una busqueda amplia de Sapolio a S/ 39.50 en Makro, con 16 litros totales declarados; una busqueda exacta posterior devolvio cero resultados.

Decision: no se usa como benchmark ni recomendacion hotelera. Se registra como inconsistencia de recuperacion y se requiere revalidar por URL, EAN o snapshot antes de usarlo como sustituto o referencia por litro.

## Ejercicio 4: restaurante - costo de cafe molido como insumo

Producto: Cafe tostado y molido Cafetal Selecto, bolsa 200 g.

- `market_compare` solo devolvio Plaza Vea a S/ 15.00.
- El detector de promociones tambien encontro Vega a S/ 12.90 para `200gr`, pero sin historial suficiente.
- La consulta de historial mediante `product_id=468` devolvio correctamente el cafe de Plaza Vea y, ademas, un aceite de albahaca no relacionado en otro retailer con el mismo identificador local.

Decision: no calcular margen ni ahorro para restaurante con este resultado. La identidad del producto debe combinar retailer, ID, nombre, marca, presentacion y, cuando exista, canonical record; el `product_id` aislado no es una llave global confiable.

## Ejercicio 5: cafeterias - cafe instantaneo como insumo de alta rotacion

Producto: Cafe instantaneo Cafetal Clasico 180 g.

- Wong: S/ 17.50, precio de lista S/ 23.50, descuento reportado 26%.
- Metro: S/ 17.50, precio de lista S/ 23.50, descuento reportado 26%.
- Ambos snapshots tienen `canonical_product_id` consistente: `prod_cafetal_bebidas_0.18kg`.
- `market_compare` devolvio cero comparables, pese a que el historial mostro ambas observaciones.
- El detector de promociones reporto historial insuficiente para validar autenticidad de la promocion.

Decision sin ERP: monitorear, no anticipar compra ni fijar costo estandar. La paridad observada de Wong y Metro es una referencia puntual; el descuento no debe tratarse como precio estable ni como promocion validada.

## Ejercicio 6: trade marketing y pricing - lavavajillas Sapolio 800 g

Producto validado: Lavavajillas Sapolio Manzana Pote 800 g.

| Retailer | Precio observado | Lectura |
|---|---:|---|
| Makro Online | S/ 5.50 | Referencia mas baja observada |
| Plaza Vea | S/ 6.20 | 12.7% por encima de Makro |

El mismo producto fue identificado con `canonical_product_id` `prod_sapolio_general_0.8kg`. El scorecard de Makro reporto cobertura de siete dias de 100%, normalizacion de catalogo de 91.5% y disponibilidad reportada de 99.5% en el ultimo scrape.

Ocurrencia promocional: un pack de lavavajillas 800 g mas lejia 4.8 kg aparecio con 34% de descuento. Fue excluido del benchmark del producto individual.

Ocurrencia de historial: para el SKU exacto, habia solo un snapshot en Makro y el detector marco historial insuficiente en todos los retailers. No se puede inferir tendencia ni autenticidad de promociones.

Decision: `monitorear y validar`. No bajar precio ni lanzar promocion defensiva solo por una diferencia puntual de S/ 0.70.

## Ejercicio 7: innovacion de producto y pricing - yogurt funcional estilo kefir

Producto de referencia: Yogurt Funcional DANLAC Estilo Kefir Botella 900 g.

| Retailer | Precio observado | Estado |
|---|---:|---|
| Plaza Vea | S/ 17.30 | Descuento visible de 13.1% sobre S/ 19.90 |
| Makro Online | S/ 19.90 | Sin descuento visible |

La diferencia puntual es S/ 2.60, aproximadamente 15.0% frente a Plaza Vea. La exploracion de categoria tambien encontro variantes funcionales con proposiciones de defensas, fibra, colageno y kefir, pero no permite concluir demanda o tamano de mercado.

Ocurrencias:

- `market_compare` devolvio cero comparables aunque el historial devolvio los dos snapshots.
- Los snapshots entregaron `canonical_product_id` distintos para el mismo SKU comercial; se requiere validar variante, sabor, imagen y atributos antes de usarlo como benchmark definitivo.
- `market_promo_detector` reporto historial insuficiente.
- `market_price_forecast` respondio 404.

Decision: hipotesis apta para piloto, no para escalamiento. El rango S/ 17.30-S/ 19.90 sirve para disenar dos o tres tests de precio tras validar costo, propuesta de valor, claims permitidos y repeticion de compra.

## Registro de tools invocadas y ocurrencias

| Tool | Invocaciones | Resultado principal | Ocurrencias relevantes |
|---|---:|---|---|
| `market_intel_brief` | 1 | Senal agregada de gondola y cobertura | Datos de gondola digital; no IPC ni costo B2B |
| `market_procurement_signal` | 1 | `buy_now` | Senal de timing, no orden de compra |
| `market_price_risk` | 1 | Riesgo `moderate` | Promocion alta como principal factor |
| `market_informal_signal` | 1 | Cobertura formal 64.7%, `warn` | No representa canal informal |
| `market_search` | 8 | Identidades, precios y candidatos | Busquedas exactas vacias para productos vistos en consultas amplias; busqueda semantica ruidosa |
| `market_basket` | 1 | Canasta parcial | Match incorrecto de aceite como pack arroz + aceite; resultado rechazado |
| `market_compare` | 5 | Comparables utiles en leche y Sapolio | Ceros o cobertura incompleta para kefir y cafes pese a snapshots existentes |
| `market_price_history` | 4 | Snapshots por retailer | Historial escaso; colision de `product_id=468` con producto no relacionado |
| `market_promo_detector` | 5 | Promociones visibles y estados de historial | Historial insuficiente para validar autenticidad en todos los casos relevantes |
| `market_retailer_scorecard` | 1 | Salud de Makro | Disponibilidad es ultimo scrape, no stock en tiempo real |
| `market_trending` | 1 | Catalogo mixto de novedades | No apto para inferir demanda de una categoria sin validacion adicional |
| `market_commerce_pulse` | 1 | Sin resultado | Error 404 |
| `market_price_forecast` | 1 | Sin resultado | Error 404 |

## Reglas operativas para un sistema agentico posterior

1. Consultar primero senales agregadas; despues buscar productos con pais, linea y presentacion acotados.
2. No sumar ni comparar precios hasta validar nombre, marca, formato, cantidad, retailer y confianza del match.
3. Rechazar canastas parciales o productos resueltos a bundles no equivalentes.
4. Tratar `product_id` como identificador local, no global, salvo que se demuestre lo contrario; preferir canonical record y atributos completos.
5. Diferenciar precio actual, precio de lista, descuento visible, historial y autenticidad promocional. Un descuento con historial insuficiente no debe impulsar una decision.
6. Registrar 404, cero resultados y discrepancias entre tools como evidencia operativa. El agente debe abstenerse o escalar a revision humana, nunca completar los vacios con inferencias.
7. Separar observacion, normalizacion, inferencia y recomendacion; cada salida debe mostrar fecha, fuentes, cobertura, confianza y limitaciones.

## Conclusion

Las tools permiten construir ejercicios utiles de procurement, pricing e innovacion, pero el valor real surge de un orquestador que privilegie identidad de producto, completitud de canasta y trazabilidad sobre respuestas plausibles. Hoy la evidencia soporta monitoreo y diseno de pilotos; no soporta cambios automaticos de compra, precio, surtido o promocion.
