# Diagnostico de desempeno de las tools de CLI Market

Fecha: 29 de julio de 2026. Base: ejecuciones reales de tools MCP en esta sesion, sin ERP, carrito, checkout ni cambios transaccionales.

## Veredicto

CLI Market ya es util como capa de inteligencia exploratoria y de preseleccion con humano en el circuito. Todavia no es confiable para automatizar compras, pricing o recomendaciones finales sin una capa robusta de validacion.

## Lo que funciono bien

### Disponibilidad y superficie MCP

- Las tools estuvieron accesibles y respondieron con datos reales.
- `market_whoami` confirmo sesion enterprise.

### Busqueda y comparacion cuando la identidad es clara

Funcionaron bien en ejemplos concretos:

- Leche evaporada Gloria 390 g: distincion entre lata, pack de 6 y pack de 12.
- Lavavajillas Sapolio Manzana 800 g: Makro S/ 5.50 frente a Plaza Vea S/ 6.20.
- Horno industrial convector Ilumi: escalera coherente de 5, 10 y 12 bandejas.

### Metadatos de calidad

`market_retailer_scorecard`, `source_health`, cobertura, frescura, stock reportado y `confidence` dan al agente evidencia para explicar la fuerza o debilidad de una senal.

### Inteligencia agregada

`market_procurement_signal`, `market_price_risk`, `market_intel_brief` y `market_informal_signal` son utiles para contexto de timing, riesgo, promociones y cobertura, siempre que no se transformen en decisiones automaticas.

### Exploracion fuera de FMCG

La linea `equipos_cocina` permitio descubrir retailers especializados y activos de alto ticket. Es una ruta valida para MRO/CAPEX, aunque con cobertura competitiva aun limitada.

## Problemas criticos observados

### 1. Identidad de producto no suficientemente segura

- `product_id=468` devolvio cafe Cafetal 200 g y aceite de albahaca de otro retailer. `product_id` no puede considerarse llave global.
- Yogurt DANLAC Kefir 900 g mostro el mismo SKU comercial con distintos `canonical_product_id` entre retailers.
- Productos encontrados en busquedas amplias desaparecieron en busquedas exactas.

Correccion requerida: usar llave compuesta de retailer, product_id local, nombre normalizado, marca, presentacion y EAN cuando exista. El Golden Record debe incluir confianza y evidencia de match.

### 2. `market_basket` puede devolver totales peligrosos con resolucion parcial

Se solicito aceite vegetal 900 ml y la tool lo resolvio como un pack de arroz 5 kg mas aceite 900 ml. Solo encontro uno de tres items, pero devolvio total y retailer mas barato.

Un contrato seguro deberia exponer:

```text
status: incomplete | blocked
eligible_for_ranking: false
unresolved_items: [...]
mismatched_items: [...]
```

La tool no deberia seleccionar `cheapest_store` ni calcular ahorro cuando la canasta no esta completa y validada.

### 3. `market_compare` inconsistente frente a busqueda e historial

Funciono para Gloria y Sapolio, pero devolvio cero o cobertura incompleta para productos presentes en busqueda o historial:

- Yogurt DANLAC Kefir 900 g.
- Cafe instantaneo Cafetal 180 g.
- Cafe molido Cafetal 200 g.

Busqueda, comparacion e historial deben usar una logica de matching compatible y reportar por que un producto es excluido.

### 4. Drift entre registro MCP y backend

Dos tools expuestas respondieron 404:

- `market_commerce_pulse`.
- `market_price_forecast`.

Se debe implementar la ruta, retirar la tool o devolver una degradacion explicita. Un agente no puede planificar sobre herramientas anunciadas que fallan por contrato.

### 5. Historial temporal escaso

`market_price_history` y `market_promo_detector` devolvieron repetidamente `insufficient_history`.

Hoy se puede afirmar precio observado, descuento visible o diferencia puntual. No se puede sostener tendencia, autenticidad promocional, elasticidad, presion competitiva persistente ni forecast de compra.

### 6. Semantica de cobertura y frescura ambigua

Hubo casos de cobertura operativa normal/alta junto a confianza agregada `stale`; tambien retailers con alta cobertura semanal y datos no frescos a 24 horas.

Se deben separar en la respuesta:

- Salud del conector.
- Frescura del snapshot.
- Cobertura del retailer.
- Tamano de muestra.
- Calidad de normalizacion.
- Confianza de equivalencia.
- Confianza de precio.

### 7. Rendimiento y tamano de respuesta irregulares

- Busquedas acotadas: respuesta generalmente rapida.
- Consultas agregadas: mas de un minuto en algunos casos.
- Canasta: varios minutos.
- `market_discover`: respuesta muy extensa y truncable aun con filtros.

Se requiere modo compacto, paginacion y un parametro `summary=true` para agentes.

## Priorizacion de correcciones

| Prioridad | Mejora |
|---|---|
| P0 | Bloquear ranking y ahorro para canastas incompletas o ambiguas. |
| P0 | Corregir contrato MCP para tools que devuelven 404. |
| P0 | Corregir identidad: no tratar product_id local como llave global. |
| P1 | Alinear market_search, market_compare e historial. |
| P1 | Uniformar cobertura, frescura, muestra y confianza. |
| P1 | Añadir respuestas compactas y paginadas. |
| P2 | Acumular historia para forecast y autenticidad promocional. |
| P2 | Añadir especificaciones, garantia y postventa para CAPEX/MRO. |

## Que automatizar hoy

- Exploracion de catalogo.
- Briefs de mercado.
- Deteccion de candidatos.
- Clasificacion de evidencia.
- Alertas de producto exacto.
- Borradores de solicitudes de cotizacion.
- Explicacion de riesgos y vacios.

## Que no automatizar todavia

- Seleccion del retailer mas barato para una canasta.
- Cambios de precio.
- Compra, checkout o sustitucion de producto.
- Calculo de ahorro anual.
- Recomendaciones de CAPEX.
- Conclusiones de tendencia o promocion autentica.

## Conclusion

El activo mas valioso de CLI Market es su direccion de producto: datos reproducibles, cobertura por retailer, trazabilidad y tools especializadas. La principal brecha no es cantidad de tools, sino consistencia del contrato de datos e identidad de producto. Corregir esos puntos habilitaria sistemas agenticos mucho mas confiables.
