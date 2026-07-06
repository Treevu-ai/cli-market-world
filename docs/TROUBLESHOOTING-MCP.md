# Troubleshooting — MCP server de CLI Market

Guía de diagnóstico para el MCP server `cli-market` (`market-mcp`) usado por agentes locales (Devin for Terminal, Cursor, Claude Code, etc.).

## Arquitectura rápida

- **MCP server local:** `market-mcp` (stdio JSON-RPC) → expone tools como `market_search`, `market_compare`, `market_basket`, etc.
- **API productiva:** `https://cli-market-api.fly.dev` (Fly.io).
- **Autenticación:** token `MARKET_API_TOKEN` guardado como variable de entorno del usuario.
- **Configuración típica en Devin:** `~/.claude/settings.json` bajo `mcpServers.cli-market`.

---

## Problema 1: `mcp_list_tools` falla o tools devuelven "Failed to connect"

### Síntoma

- `mcp_list_tools` para `cli-market` devuelve error.
- `market_whoami` a veces funciona, pero `market_search`/`market_discover` desconectan.
- En logs aparece:

```python
UnicodeEncodeError: 'charmap' codec can't encode character '\u2192' in position ...
```

### Causa

En Windows, Python usa la codificación de consola (`cp1252` por defecto) para `stdout`. Las descripciones de tools contienen caracteres Unicode (`→`, `·`, emojis), y al responder `tools/list` el servidor `market-mcp` se rompe.

### Fix

1. Abrir `~/.claude/settings.json` (Devin) o el archivo MCP equivalente.
2. Agregar `PYTHONIOENCODING=utf-8` al env del servidor `cli-market`:

```json
{
  "mcpServers": {
    "cli-market": {
      "command": "market-mcp",
      "args": [],
      "env": {
        "MARKET_API_URL": "https://cli-market-api.fly.dev",
        "MARKET_API_TOKEN": "${MARKET_API_TOKEN}",
        "MCP_TOOL_PROFILE": "default",
        "PYTHONIOENCODING": "utf-8"
      }
    }
  }
}
```

3. Reiniciar el agente / Devin for Terminal.

### Fix en código (defensivo)

El repo `cli-market-world` incluye un shim en `market_mcp.py` que fuerza UTF-8 en `stdout`/`stderr` cuando corre en Windows. El fix upstream definitivo debe aplicarse en `market_core/market_mcp.py` del paquete `cli-market-core`.

---

## Problema 2: `ReadTimeout` desde `cli-market-api.fly.dev`

### Síntoma

- `market_ask` o `market_optimize_purchase` devuelven:

```json
{"error": "Cannot reach API at https://cli-market-api.fly.dev (ReadTimeout)."}
```

### Causa

La API productiva en Fly.io tarda más de lo esperado en consultas complejas (comparaciones de canasta, misiones de optimización, búsquedas con muchos resultados).

### Workarounds

1. **Dividir la consulta** en partes más pequeñas:
   - En lugar de `market_optimize_purchase` con 8 items, usar `market_basket` con 2-3 items.
   - En lugar de `market_ask` con prompts complejos, usar `market_search` o `market_compare` directos.
2. **Usar `market_search` con scope reducido**: siempre pasar `store` o `line` + `country`.
3. **Reintentar**: los timeouts son intermitentes; una segunda llamada puede funcionar.

### Ejemplo de fallback

```bash
# Si esto falla:
market ask "compara precios de arroz costeño en supermercados de Perú"

# Usar esto:
market search "arroz costeño" --line supermercados --country PE
market compare "arroz costeño" --line supermercados --country PE
```

---

## Problema 3: `market_optimize_purchase` no resuelve items

### Síntoma

```json
{
  "error": "no stores with prices for items",
  "items_resolved": [
    {"requested": "arroz costeño 5kg", "resolved_product_id": null, ...}
  ]
}
```

### Causa

La tool de optimización usa el golden taxonomy para resolver items. Nombres muy específicos o formatos de granel (5kg, 5L) a veces no resuelven.

### Workarounds

1. **Usar `market_basket`** en su lugar:

```json
{
  "items": [
    {"name": "arroz costeño", "qty": 4},
    {"name": "aceite vegetal", "qty": 2},
    {"name": "azucar rubia", "qty": 2}
  ],
  "country": "PE",
  "include_tco": true
}
```

2. **Quitar el tamaño del nombre**: `arroz costeño` en lugar de `arroz costeño 5kg`.
3. **Dividir en grupos**: granos, proteínas, vegetales, condimentos.

### Limitación conocida

`market_basket` resuelve a unidades pequeñas (750g, 900ml) y no siempre a granel (5kg, 5L). Para compras reales de restaurante, complementar con `market_search` directo.

---

## Problema 4: Retailer catalogado pero sin datos

### Síntoma

- `market_discover` muestra el retailer (ej. `ripley_pe`).
- `market_search` con `store=ripley_pe` devuelve 0 resultados.
- `source_health` indica `state: dead` o `coverage_7d_pct: 0`.

### Causa

El retailer está en el catálogo pero el scraper no está extrayendo datos (fallas consecutivas, cambios en el sitio, etc.).

### Ejemplo

```json
{
  "store": "ripley_pe",
  "store_name": "Ripley PE",
  "state": "dead",
  "consecutive_failures": 9899,
  "coverage_7d_pct": 0.0
}
```

### Workaround

Usar retailers alternativos en la misma línea. Para departamentales en Perú, Ripley está catalogado pero sin datos; Coppel AR y Ri Happy BR sí tienen datos.

---

## Problema 5: Productos no encontrados

### Síntoma

- Búsqueda de `pollo fresco` o `ají panca` no devuelve resultados.

### Causa

1. **Productos perecibles frescos**: pollo fresco, leche líquida, pescado fresco suelen no estar en el moat de datos (se enfoca en productos envasados/secos).
2. **Gaps del catálogo**: algunos productos locales (ají panca, ají amarillo) no están indexados.

### Workaround

- Para pollo: buscar `pollo congelado`, `muslo pollo`, `pollo rostizado`.
- Para ají: buscar `pasta aji`, `aji molido`, `salsa aji`.
- Usar términos más genéricos y verificar alternativas.

---

## Verificación rápida

```bash
# 1. Verificar que el CLI funciona
market hello

# 2. Verificar que el MCP server responde
mcp__cli-market__market_whoami

# 3. Verificar tools list
mcp__cli-market__market_discover

# 4. Verificar una búsqueda
mcp__cli-market__market_search {"query": "arroz", "country": "PE", "store": "wong"}
```

---

## Referencias

- `market_mcp.py` — shim local con fix UTF-8.
- `AGENTS.md` — sección "MCP server de CLI Market en agentes".
- `docs/PYPI-PACKAGE-MODEL.md` — modelo de paquetes PyPI.
- API productiva: `https://cli-market-api.fly.dev`
