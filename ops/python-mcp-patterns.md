# Patrones MCP en Python — `market-mcp`

> Traducción de los conceptos del skill `mcp-server-patterns` (que asume el SDK
> Node/TypeScript) al servidor real de CLI Market, que es Python puro sin SDK — solo
> `json`/`sys.stdin`/`sys.stdout`. Referencia para futuro trabajo en el servidor (nuevas
> tools, soporte HTTP, resources/prompts reales).

## Dónde vive

- `cli-market-core/market_core/market_mcp.py` — loop JSON-RPC, dispatch de métodos.
- `cli-market-core/market_core/market_mcp_registry.py` — registro canónico de tools,
  perfiles, alias.

## Los 3 conceptos del skill, mapeados

| Concepto MCP | En `market-mcp` hoy |
|---|---|
| **Tools** | `TOOLS: list[dict]` en `market_mcp_registry.py` (`_TOOL_SPECS`) — cada uno `{name, description, inputSchema}` en JSON Schema plano, sin Zod (es Python). `handle_tool(name, args)` en `market_mcp.py` despacha a la función real. |
| **Resources** | **No implementado.** `resources/list` y `resources/templates/list` devuelven `{"resources": []}` siempre (línea 461-462 de `market_mcp.py`). Si se necesita exponer datos de solo lectura (ej. el catálogo de tiendas) como resource en vez de tool, es trabajo nuevo. |
| **Prompts** | **No implementado.** `prompts/list` devuelve `{"prompts": []}` siempre (línea 463-464). |
| **Transport** | **Solo stdio.** `main()` (línea 475) es un `for line in sys.stdin` — no hay Streamable HTTP ni SSE. Todos los clientes (Claude Code, Cursor, Codex, etc.) lo invocan como proceso hijo vía `command`/`args`, nunca por URL. |

## El loop real (no un SDK — JSON-RPC a mano)

```python
def main():
    profile = get_profile()          # MCP_TOOL_PROFILE env var
    for line in sys.stdin:
        request = json.loads(line.strip())
        response = handle_rpc_request(request, profile)
        if response is not None:     # None = notification, no reply
            _write_rpc(response)      # print + flush a stdout
```

`handle_rpc_request()` es un despachador manual por `method`:

- `initialize` → negocia versión de protocolo (`_negotiate_protocol_version`, soporta
  `2025-03-26` y `2024-11-05`), devuelve `capabilities: {tools: {listChanged: false}}`.
- `ping` → `{}` vacío.
- `tools/list` → `list_tools(profile)` (filtra por perfil, ver abajo).
- `tools/call` → `handle_tool(name, args)`, envuelve el resultado en
  `{"content": [{"type": "text", "text": ...}]}` — **siempre texto**, nunca contenido
  estructurado/imagen.
- `resources/*`, `prompts/list` → listas vacías (no implementado).
- `notifications/*` → `None` (sin respuesta, correcto para notificaciones JSON-RPC).
- Método desconocido → error JSON-RPC `-32601`.

## Detalle no obvio: notificaciones con `id: null`

```python
def _is_jsonrpc_notification(request: dict) -> bool:
    return request.get("id") is None
```

Cursor manda frames internos (ej. reconnect probes) con `id: null`, no solo `id`
ausente. Responder con `{"id": null, "error": ...}` rompe el validador Zod de Cursor y
mata la conexión — por eso se trata `null` igual que "sin id". Si se porta este patrón
a otro lenguaje/SDK, no asumir que "notification" == "sin campo id".

## Perfiles de tools (`MCP_TOOL_PROFILE`)

`market_mcp_registry.py` filtra qué tools expone `tools/list` según un env var, no según
el cliente:

- `default` (35 tools) — curado, oculta `_ADVANCED_NAMES` + `_ADMIN_NAMES` + `_DEFAULT_HIDDEN`.
- `legacy` (60 tools) — todo, incluye alias deprecados.
- `full` (57) / `admin` (60 + scan/refresh).

`ALIASES: dict[str, str]` mapea nombres viejos a su handler canónico (ej.
`market_lines` → `market_discover`) — así un cliente con config vieja sigue funcionando
sin romper, aunque el tool ya no aparezca listado en `default`.

## Si se agrega soporte HTTP (Streamable) más adelante

Hoy no existe. El punto de entrada sería envolver `handle_rpc_request()` (que ya es puro:
recibe un dict, devuelve un dict o `None`) detrás de un servidor HTTP (FastAPI, ya usado
en `cli-market-backend`) en vez de reemplazar el loop de stdio — `handle_rpc_request` no
depende de `sys.stdin`/`sys.stdout`, así que es reusable tal cual.

## Si se agregan resources/prompts reales

`resources/list`/`prompts/list` hoy son placeholders vacíos, no "no soportado" a nivel de
protocolo (`initialize` ya no anuncia `resources`/`prompts` en `capabilities`, solo
`tools`). Para implementarlos de verdad: (1) agregar las keys correspondientes a
`capabilities` en la respuesta de `initialize`, (2) poblar las listas con datos reales,
(3) manejar `resources/read` / `prompts/get` (no existen todavía en el despachador).
