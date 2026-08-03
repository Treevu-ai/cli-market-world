# CLI Market en Claude Desktop (Connector remoto)

Guía para conectar las MCP tools de CLI Market a Claude Desktop vía **Settings → Connectors**, sin editar `claude_desktop_config.json`.

## Por qué vía Connectors y no vía JSON

`claude_desktop_config.json` solo soporta servidores **locales (stdio)** — el paquete `cli-market-world` de PyPI (`market-mcp`, ver `mcp.json` / `server.json`). Ese modo requiere tener el paquete instalado localmente.

CLI Market también expone el transporte **Streamable HTTP** (MCP `2025-03-26`) directamente en producción:

```
POST https://cli-market-api.fly.dev/mcp
```

(ver `routers/mcp_http.py`). Ese transporte es el que consume la UI de Connectors — sin instalar nada localmente, sin tocar el JSON.

## Configuración

1. Conseguir un token de API en [cli-market.dev](https://cli-market.dev) (`market_login`, o revisar el tier actual con `market_subscription` / `market_whoami`).
2. Claude Desktop → avatar/perfil → **Settings → Connectors**.
3. **Add custom connector**.
4. Completar:
   - **Name:** `CLI Market`
   - **URL:** `https://cli-market-api.fly.dev/mcp`
5. En **Advanced settings** (headers custom), agregar:
   - **Key:** `Authorization`
   - **Value:** `Bearer <tu-token>`
6. Guardar. Claude Desktop hace `initialize` automáticamente; el connector debe quedar en estado **Connected**.
7. Probar en un chat nuevo, con el connector activado en el selector de herramientas: pedir algo como *"busca precios de arroz en Perú"* debe invocar `market_search` sin error.

## Comportamiento de auth (importante)

- `tools/list` **no requiere token** — el catálogo completo (69 tools) se lista igual con o sin auth.
- **Cualquier `tools/call` sí requiere token** — incluso tools sin marca `[Pro]`/`[Starter]` como `market_search` devuelven `401 Auth required: Authorization header with a Bearer token` si no hay header. Sin el header configurado en el paso 5, las tools aparecerán disponibles en el connector pero fallarán al ejecutarse.
- El filtrado por tier (`[Pro]`, `[Starter]`, `[Enterprise]`, `[Admin]`) ocurre dentro del `tools/call`, no en el listado — con un token de tier bajo verás las 69 tools igual, pero las restringidas devuelven un mensaje de upgrade en vez de fallar en silencio.

## Verificación rápida

Sin auth (debe responder `200` con `serverInfo`, pero cualquier `tools/call` da `401`):

```bash
curl -s -X POST https://cli-market-api.fly.dev/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"verify","version":"1.0"}}}'
```

Con auth (debe responder `market_whoami` con username/tier):

```bash
curl -s -X POST https://cli-market-api.fly.dev/mcp \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <tu-token>" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"market_whoami","arguments":{}}}'
```

## Seguridad del token

No pegar el token de producción en chats, issues o commits — queda en el historial. Si un token quedó expuesto accidentalmente en una conversación (ej. con un asistente de IA), rotarlo desde cli-market.dev antes de usarlo en el connector definitivo.

## Limitaciones conocidas

- Solo Streamable HTTP en este canal — el modo stdio (`market-mcp` vía PyPI) sigue siendo la única opción si se necesita ejecución 100% local sin llamadas de red del cliente MCP.
- Mismo endpoint que usan Open WebUI, Cursor, VS Code, etc. (ver `docs/OPENWEBUI-INTEGRATION.md`) — el comportamiento de auth y tiers es idéntico en todos los clientes.
