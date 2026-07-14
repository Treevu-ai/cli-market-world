# CLI Market en LangChain / LangGraph

Guía para usar las MCP tools de CLI Market desde un agente LangChain o LangGraph — sin servidor intermedio, directo al endpoint Streamable HTTP de producción.

## Instalación

```bash
pip install langchain-mcp-adapters langgraph
```

## Cargar las tools (verificado funcionando)

```python
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient

TOKEN = "sk-..."  # tu API key de CLI Market

async def main():
    client = MultiServerMCPClient({
        "cli-market": {
            "transport": "streamable_http",
            "url": f"https://cli-market-api.fly.dev/mcp?token={TOKEN}",
        }
    })
    tools = await client.get_tools()
    print(f"{len(tools)} tools cargadas")  # 35 (perfil default)

    search_tool = next(t for t in tools if t.name == "market_search")
    result = await search_tool.ainvoke({"query": "leche", "limit": 3})
    print(result)

asyncio.run(main())
```

Esto se probó en vivo contra `https://cli-market-api.fly.dev/mcp`: carga las 35 tools del perfil `default` y `market_search` devuelve resultados reales de retailers verificados.

## Agente completo (LangGraph)

Patrón estándar `create_react_agent` — no reemplaza la prueba anterior, es la forma habitual de conectar las tools a un LLM:

```python
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic  # o el proveedor que uses

TOKEN = "sk-..."

async def main():
    client = MultiServerMCPClient({
        "cli-market": {
            "transport": "streamable_http",
            "url": f"https://cli-market-api.fly.dev/mcp?token={TOKEN}",
        }
    })
    tools = await client.get_tools()

    agent = create_react_agent(ChatAnthropic(model="claude-sonnet-5"), tools)
    response = await agent.ainvoke({
        "messages": [{"role": "user", "content": "¿Cómo está posicionado un serum a S/45 en Lima?"}]
    })
    print(response["messages"][-1].content)

asyncio.run(main())
```

## Autenticación

El token va en el query param (`?token=<tu-api-key>`), igual que en la integración de Open WebUI — no hace falta OAuth ni un header especial. Consíguelo con `market register` o desde `cli-market.dev/account`.

## Limitaciones conocidas

- Perfil `default` (35 tools) por defecto. Para el catálogo completo con alias legacy, no hay forma de pasar `MCP_TOOL_PROFILE` vía HTTP — ese env var solo aplica al transporte stdio local (`market-mcp`). El servidor remoto siempre sirve `default`.
- Igual que en Open WebUI: tools marcadas `[Pro]` devuelven mensaje de upgrade si el token es tier Free, no fallan en silencio.
- `market_search` y otras tools que consultan retailers en vivo pueden tardar 10-15s — si envuelves esto en un timeout corto (ej. un nodo de otra plataforma con timeout de 5-10s), súbelo.

## Verificación rápida

```bash
curl -s -X POST "https://cli-market-api.fly.dev/mcp?token=<tu-token>" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"langchain","version":"0.0.1"}}}'
```

Debe responder con `serverInfo` — confirma que el endpoint está en línea antes de correr el script.
