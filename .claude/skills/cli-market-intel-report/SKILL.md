---
name: cli-market-intel-report
description: Genera un reporte profundo de inteligencia de mercado para una categoría o línea de producto en CLI Market — panorama de precios, mapa de marcas, cobertura de retailers, tendencias y oportunidades. Usa esto cuando el usuario pida un "análisis de categoría", "estudio de mercado", "reporte de inteligencia" o "dónde hay oportunidad" para una línea de producto completa (no un solo SKU).
---

# CLI Market — Reporte de Inteligencia de Mercado (Deep-Dive)

Este skill orquesta múltiples tools de CLI Market para producir un reporte estructurado sobre una categoría completa. Es más lento que una consulta simple (puede tomar varios minutos con muchas sub-categorías) — avisa al usuario antes de empezar si el alcance es amplio.

## Requisitos

MCP `cli-market` conectado + API key válido (mismo manejo de auth/401 que los otros skills de CLI Market: pedir la key explícitamente si falta, nunca fallback a búsqueda web).

## Instrucciones

### Paso 1 — Acotar el alcance con el usuario

Antes de disparar múltiples llamadas, confirma: país, línea/categoría objetivo, y si hay sub-categorías específicas en mente (si no las da, tú las derivas de la categoría, ej. "snacks" → papas fritas, chips, palitos, etc. — no más de 5-8 sub-categorías por corrida para no disparar decenas de llamadas innecesarias).

### Paso 2 — Cobertura de retailers (`market_discover`)

Llama `market_discover` con `country` (y `line` si aplica) — reemplaza y consolida lo que antes eran `market_stores` + `market_lines` + `market_countries` en una sola llamada. Úsalo para mapear qué retailers están activos en el país/línea antes de buscar productos.

**Verificado hoy: el parámetro `country` no siempre filtra la lista de tiendas** — puede devolver retailers de todos los países bajo esa línea. No asumas que la respuesta ya viene filtrada: revisa el campo `country` de cada store en el resultado y filtra tú mismo por el país objetivo antes de usar esa lista en los pasos siguientes.

### Paso 3 — Barrido de catálogo (`market_search`)

Para cada sub-categoría acotada en el Paso 1, llama `market_search` con `country`/`line`. Junta los SKUs, marcas y tiendas encontradas. No repitas una llamada idéntica dos veces.

### Paso 4 — Panorama de precios (`market_compare`)

Para los SKUs/queries más relevantes del barrido, llama `market_compare` para precios cross-retailer actuales. Normaliza todo a precio por kg/L/unidad antes de comparar.

### Paso 5 — Tendencias de precio (`market_price_history`)

Para los 3-5 SKUs más indexados (mayor cobertura de tiendas), llama `market_price_history` con `product_id` real (el campo `id` devuelto por `market_search`) **y** `store`. Identifica dirección de tendencia (subiendo/bajando/estable) y min/max del período.

### Paso 6 — Señales macro e intel (opcional, según profundidad pedida)

- `market_scores` — competitividad comparativa.
- `market_trending` — qué se mueve más en precio recientemente.
- `market_price_risk` — volatilidad de la categoría.
- `market_procurement_signal` — señal de comprar ahora vs. esperar.
- `market_inflation_report` — presión de precios macro de la línea/país.
- `market_promo_detector` — autenticidad de descuentos activos (requiere `product`, opcionalmente `store`).
- `market_retailer_scorecard` — salud de catálogo/cobertura de un retailer específico (requiere `store` exacto — usa las claves reales que devuelve `market_discover`, ej. `wong`, `plazavea`; nunca un nombre comercial libre que no esté confirmado en el catálogo).

### Paso 7 — Compilar el reporte

Estructura fija:
1. **Category overview** — SKUs indexados, sub-categorías cubiertas, retailers activos.
2. **Price landscape** — por sub-categoría: min/max/avg normalizado, spread %, # SKUs.
3. **Brand map** — marcas rankeadas por profundidad de SKU; marca "dominante" si ≥30% share, "subrepresentada" si tiene muy pocos SKUs.
4. **Retailer coverage** — qué sub-categorías cubre cada retailer (completa/parcial/ninguna).
5. **Price trends** — dirección + min/max/avg de los SKUs con historial.
6. **Opportunity matrix** — gaps de distribución, de tier de precio, whitespace de cobertura, tendencias al alza — cada uno con atractivo estimado (alto/medio/bajo) basado en spread y cobertura real, nunca inventado.
7. **Recomendaciones** — 3-5 bullets accionables, atados a datos concretos del reporte (no genéricos).

### Paso 8 — Honestidad de cobertura (regla no negociable)

CLI Market indexa **retailers formales** (VTEX, Shopify, Magento, WooCommerce) — no cubre ferias, mercados de abastos ni venta ambulante. **Nunca** uses este reporte para afirmar un porcentaje de "mercado informal" o de "mercado total" de un país — eso no existe en los datos. Si el usuario pregunta por eso, usa `market_informal_signal` y repórtalo como lo que es: honestidad de cobertura del canal formal, no una medición del canal informal.

Si la cobertura de alguna sub-categoría es baja (pocos SKUs, pocos retailers), dilo explícitamente en el reporte en vez de generalizar con pocos datos.

## Reglas

- No dispares más de ~5-8 sub-categorías de búsqueda por corrida sin confirmar con el usuario si quiere ampliar — cada una implica varias llamadas encadenadas.
- Nunca repitas una llamada idéntica (mismos parámetros) — si necesitas el mismo dato dos veces, reutiliza el resultado ya obtenido en la conversación.
- Máximo 2 reintentos por sub-categoría con términos más amplios antes de reportarla como "sin cobertura suficiente".
- Todo número en el reporte final debe trazarse a una tool call real de esta conversación — no rellenes con estimaciones propias.
