---
name: cli-market-basket-optimize
description: Optimiza dónde comprar una lista de varios productos entre retailers de CLI Market, mostrando el split recomendado y el ahorro vs. comprar todo en una sola tienda. Usa esto cuando el usuario pida "optimiza mi compra de X, Y, Z", "arma mi canasta", "dónde compro esto más barato en total", o mencione una lista de productos con presupuesto.
---

# CLI Market — Optimización de Canasta

## Requisitos

Igual que los demás skills de CLI Market: requiere el MCP `cli-market` conectado y un API key válido (`MARKET_API_TOKEN` o pedido explícitamente al usuario si falta). Si una llamada devuelve `401`, pide la key — no hagas fallback a búsqueda web.

## Instrucciones

### Paso 1 — Preferir `market_optimize_purchase`

Es la tool preferida para este caso: hace basket compare + sustitutos + intel en una sola llamada.

**Formato exacto de `items` — es un array de objetos, NO strings tipo `"leche:2"`** (esa sintaxis es de la CLI de terminal `market optimize leche:2`, no del tool MCP):

```json
{
  "items": [{"name": "leche", "qty": 2}, {"name": "arroz", "qty": 1}],
  "country": "PE",
  "constraints": {
    "max_budget": 200,
    "include_tco": true,
    "include_action_links": true
  }
}
```

- Si el usuario quiere links de compra/checkout en la respuesta, **debes pedirlos explícitamente** con `constraints.include_action_links: true` — no vienen por default.
- Si el usuario mencionó un presupuesto, pásalo como `constraints.max_budget`.
- Si el usuario quiere costos de envío/pago incluidos, usa `constraints.include_tco: true`.

### Paso 2 — `market_basket` como alternativa/complemento

Si necesitas el desglose por tienda de forma más directa (sin intel adicional), usa `market_basket` con el mismo formato de `items` (array de objetos `{name, qty}`, nunca strings). Acepta `stores` (filtro opcional), `include_tco`, `include_delivery`, `include_action_links`.

### Paso 3 — Reportar resultado

Estructura el reporte así:
- Tienda(s) recomendada(s) por ítem o split completo.
- Total estimado, y ahorro vs. comprar todo en la tienda más cara / en una sola tienda.
- Si pediste `include_action_links`, incluye los links de compra devueltos.
- Si algún ítem no se encontró, dilo explícitamente — no lo omitas en silencio del total.

### Paso 4 — Ítems no encontrados

Para cualquier ítem que la tool no pudo resolver, llama `market_substitutes` con el nombre del ítem y `country` para ofrecer hasta 3 alternativas, etiquetadas claramente como sustitutos (no como el producto original).

## Reglas

- Nunca uses la sintaxis `"producto:cantidad"` como string al llamar las tools MCP — siempre array de objetos `{name, qty}`.
- Máximo 2 reintentos con nombres más simples por ítem antes de reportarlo como no encontrado.
- No inventes montos de ahorro — calcúlalos solo a partir de lo que devuelven las tools.
