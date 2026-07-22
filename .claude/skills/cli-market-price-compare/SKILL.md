---
name: cli-market-price-compare
description: Compara el precio de un producto entre retailers verificados de CLI Market y consulta su historial de precios. Usa esto cuando el usuario pregunte "cuánto cuesta X", "compara precios de X", "dónde está más barato X", o "cómo ha variado el precio de X".
---

# CLI Market — Comparación y Monitoreo de Precios

## Requisitos

Este skill depende del servidor MCP `cli-market` (tools `market_search`, `market_compare`, `market_price_history`, `market_substitutes`) ya conectado. Cada llamada requiere autenticación:

- Si el usuario ya proporcionó un API key (`sk-...`) en la conversación o está configurado como `MARKET_API_TOKEN`, úsalo automáticamente sin pedirlo de nuevo.
- Si no hay key disponible y una tool responde `401`/`Unauthorized`, dile al usuario explícitamente que necesitas su API key de CLI Market (sk-...) para continuar. **No hagas fallback a búsqueda web.**

## Instrucciones

### Paso 1 — Encontrar el producto real

Llama `market_search` con el término del usuario y `country` si se conoce (PE, AR, MX, BR, CO, CL, ES, US). No asumas ID de producto — siempre viene del resultado real de `market_search` (campo `id` + `store`), nunca lo inventes.

Si hay más de un resultado plausible, muestra los 3-5 más relevantes y pídele al usuario que confirme cuál es, salvo que uno sea claramente el mejor match.

Si no hay resultados: reintenta una vez con un término más amplio (quita marca, tamaño, adjetivos). Si tras ese reintento sigue sin resultados, repórtalo honestamente: qué buscaste, qué intentaste, y sugiere reformular.

### Paso 2 — Comparar entre retailers

Llama `market_compare` con el mismo query (y `country`/`line` si aplica). Reporta cada tienda con precio, y **normaliza a precio por kg/L/unidad** cuando los tamaños de envase difieran — nunca compares precio total de presentaciones distintas sin normalizar.

Destaca la opción más barata y la brecha (%) contra la más cara.

### Paso 3 — Historial de precio (si el usuario lo pide)

`market_price_history` requiere `product_id` (el campo `id` del resultado real de `market_search`, NO un ID inventado tipo `prod_algo`) **y** `store` — el historial está atado a producto+tienda, no solo al producto.

Si no tienes ambos valores todavía, corre `market_search` primero para conseguirlos.

Reporta tendencia (subiendo/bajando/estable), min/max del período, y la frescura del dato (el campo de fecha/timestamp que devuelva la tool).

### Paso 4 — Sustitutos (si no se encuentra o el usuario los pide)

Llama `market_substitutes` con el nombre **casi exacto** del catálogo (no una descripción libre — usa el `name` que devolvió `market_search`) y `country`. Es normal que devuelva una lista vacía para productos de nicho — repórtalo como resultado válido, no como error.

## Reglas

- Nunca inventes nombres de tienda, `product_id`, ni datos de precio — todo sale de las tools.
- Máximo 2 reintentos por búsqueda antes de reportar "no encontrado" con honestidad.
- Si el usuario pide un país sin especificar, pregúntale o usa el país de su contexto de conversación si ya se mencionó antes.
- `line` filtra por **rubro de tienda** (`supermercados`, `farmacias`, `hogar`, `electro`, `moda`, `departamentales`, `automotriz`, `industrial`) — no es una categoría de producto libre.
