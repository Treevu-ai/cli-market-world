# CLI Market en Open WebUI

Guía para conectar las MCP tools de CLI Market a una instancia de [Open WebUI](https://openwebui.com) — sin código nuevo, sin `mcpo`.

## Por qué no hace falta `mcpo`

`mcpo` es un proxy que traduce servidores MCP en **stdio** o **SSE** a endpoints OpenAPI, para que Open WebUI (que solo habla HTTP) pueda usarlos. Desde Open WebUI **v0.6.31** existe soporte nativo para MCP, pero únicamente sobre transporte **Streamable HTTP**.

CLI Market ya expone ese transporte directamente en producción:

```
POST https://cli-market-api.fly.dev/mcp
```

(ver `routers/mcp_http.py`). Por eso, para este caso puntual, Open WebUI puede conectarse **directo**, sin capa intermedia.

## Configuración (5 minutos)

1. Conseguir un token de API en [cli-market.dev/login](https://cli-market.dev) (tier Free alcanza para probar).
2. En Open WebUI: **Admin Settings → External Tools → Add Server (+)**.
3. Completar:
   - **Type:** `MCP (Streamable HTTP)`
   - **Server URL:** `https://cli-market-api.fly.dev/mcp?token=<tu-token>`
   - Auth: no requiere OAuth — el token va en el query param (los clientes tipo claude.ai/Open WebUI no siempre soportan Bearer header en este flujo).
4. Guardar. Open WebUI hace `initialize` y `tools/list` automáticamente y las tools quedan disponibles para cualquier modelo conectado.

## Qué se obtiene

Las ~50 tools del perfil desplegado (`market_search`, `market_compare`, `market_basket`, `market_optimize_purchase`, `market_affordability`, etc.), con el mismo esquema que usan Claude, Cursor o VS Code vía MCP.

El límite por tier ya viene resuelto del lado del servidor: las tools marcadas `[Pro]` devuelven un mensaje de upgrade si el token es de tier Free, en vez de fallar en silencio. No hay que replicar esa lógica en Open WebUI.

## Limitaciones conocidas

- Solo Streamable HTTP — si en el futuro se agrega un transporte SSE o stdio-only, ahí sí haría falta `mcpo` como puente.
- No probado con `market_ask` (LLM interno del lado del servidor) dentro de un flujo Open WebUI con su propio modelo — puede haber redundancia si el usuario ya le pregunta directo al modelo de Open WebUI.
- Procure Copilot no tiene (todavía) un endpoint MCP HTTP equivalente — este canal por ahora es solo para CLI Market (Build / Intelligence / Cost of Living).

## Verificación rápida

```bash
curl -s -X POST "https://cli-market-api.fly.dev/mcp" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"openwebui","version":"0.0.1"}}}'
```

Debe responder con `serverInfo` (nombre, versión, descripción) — confirma que el endpoint está en línea antes de configurar Open WebUI.
