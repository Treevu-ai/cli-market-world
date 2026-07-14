# CLI Market en Mistral (API / Le Chat)

Guía para conectar las MCP tools de CLI Market a un agente construido con el SDK oficial de Mistral (`mistralai` 2.6.0).

## Diferencia clave vs. LangChain / Open WebUI

LangChain y Open WebUI se conectan **directo** al endpoint Streamable HTTP de CLI Market (`POST /mcp?token=...`) en cada llamada. Mistral usa un modelo distinto: primero hay que **registrar el servidor MCP como "connector"** en la plataforma de Mistral (una sola vez), y luego referenciarlo por `connector_id` en cada conversación. No hay forma de pasar la URL del MCP directamente en el request de chat.

Esto se confirmó inspeccionando el código fuente instalado de `mistralai==2.6.0` (`site-packages/mistralai/client/`), no la documentación pública — la guía oficial en la web puede describir una versión distinta del SDK.

## Instalación

```bash
pip install mistralai
```

Importante: en la versión 2.6.0 el paquete no expone nada en `mistralai/__init__.py` — todo el SDK vive bajo `mistralai.client`. El import correcto es:

```python
from mistralai.client import Mistral
```

(`from mistralai import Mistral`, que es lo que muestran la mayoría de ejemplos online, falla con `ImportError` en esta versión.)

## Paso 1: registrar CLI Market como connector (una sola vez)

```python
from mistralai.client import Mistral

client = Mistral(api_key="tu-mistral-api-key")

connector = client.beta.connectors.create(
    name="cli_market",
    description="Precios y análisis de retail en LATAM (CLI Market)",
    server="https://cli-market-api.fly.dev/mcp",
    headers={"Authorization": "Bearer sk-..."},  # tu API key de CLI Market
)
print(connector.id)  # guardar este id, se usa en cada conversación
```

`server` es la URL del servidor MCP (`connectors.py:create`, parámetro `server: str`). `headers` son headers a nivel organización que Mistral reenvía en cada llamada al servidor — ahí va el token de CLI Market, no en la URL como en LangChain/Open WebUI.

## Paso 2: usar el connector en una conversación

```python
from mistralai.client.models import CustomConnector

response = client.beta.conversations.start(
    model="mistral-large-latest",
    inputs="¿Cómo está posicionado un serum a S/45 en Lima?",
    tools=[
        CustomConnector(connector_id=connector.id),
    ],
)
print(response.outputs)
```

`tools` en `conversations.start()` acepta un `Union` discriminado por `type` (`FunctionTool`, `WebSearchTool`, `CodeInterpreterTool`, `CustomConnector`, etc. — ver `models/conversationrequest.py`). Las tools de un servidor MCP externo entran como `CustomConnector`, no como una entrada de tools individual por cada `market_*` — Mistral las descubre automáticamente vía el `server` registrado.

## Qué se verificó y qué no

- **Verificado por inspección de código fuente**: ruta de import real (`mistralai.client`), firma de `Connectors.create()`, firma de `Conversations.start()`, forma del modelo `CustomConnector`. Todo esto se confirmó leyendo directamente los archivos instalados en `site-packages/mistralai/client/`, no la documentación pública.
- **No verificado end-to-end**: no se ejecutó una llamada real a la API de Mistral (no hay una API key de Mistral disponible en este entorno) — a diferencia de la integración de LangChain, que sí se probó en vivo contra el endpoint de CLI Market. El flujo de registro de connector y el uso de `CustomConnector` en `tools` son correctos según el SDK instalado, pero no se confirmó que el servidor de Mistral efectivamente llame de vuelta a `cli-market-api.fly.dev/mcp` y obtenga resultados reales.

## Limitaciones conocidas

- El registro del connector (Paso 1) es a nivel de cuenta/organización de Mistral, no por request — hacerlo una vez y reusar el `connector_id`.
- El header con el token de CLI Market se guarda del lado de Mistral al crear el connector; si el token rota, hay que actualizar el connector (`client.beta.connectors.update(...)`, no cubierto en detalle aquí).
- Igual que en las otras integraciones: tools `[Pro]` devuelven mensaje de upgrade si el token es tier Free, no fallan en silencio.

## Verificación rápida

```bash
curl -s -X POST "https://cli-market-api.fly.dev/mcp?token=<tu-token>" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-03-26","capabilities":{},"clientInfo":{"name":"mistral","version":"0.0.1"}}}'
```

Debe responder con `serverInfo` — confirma que el endpoint está en línea antes de registrar el connector en Mistral.
