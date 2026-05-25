#!/usr/bin/env python3
"""
market-mcp — MCP server para Agentic Market.

Expone búsqueda, carrito y checkout como tools MCP (JSON-RPC sobre stdio)
para que cualquier agente IA (DeepSeek TUI, Claude, etc.) pueda operar
el supermercado.

Uso:
    python market_mcp.py
    → se conecta vía stdio, listo para MCP
"""

import json
import os
import sys

import httpx

from market_core import API, SESSION_FILE, get_token, api

TOOLS = [
    {
        "name": "market_login",
        "description": "Autenticarse en Agentic Market. Requerido antes de otras tools.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "username": {"type": "string"},
                "password": {"type": "string"},
            },
        },
    },
    {
        "name": "market_lines",
        "description": "Listar las 6 líneas de negocio verificadas (supermercados, farmacias, electro, hogar, departamentales, moda) con sus retailers VTEX, países y monedas.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "market_search",
        "description": "Buscar productos en 30 retailers VTEX verificados (8 países, 6 líneas). Cada retailer tiene API real comprobada. Retorna product_id, name, price, store_key (para usar en market_add), store (nombre legible), line_key y line. Usar 'line' para filtrar por vertical.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Término de búsqueda"},
                "store": {"type": "string", "description": "ID de tienda específica (vacío = todas). Usar market_lines para ver IDs válidos."},
                "line": {"type": "string", "description": "Línea de negocio: supermercados, farmacias, electro, moda, deportes, hogar"},
                "limit": {"type": "integer", "default": 10},
            },
            "required": ["query"],
        },
    },
    {
        "name": "market_compare",
        "description": "Comparar precios entre todos los retailers VTEX. Usar 'line' para filtrar por vertical.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Producto a comparar"},
                "line": {"type": "string", "description": "Línea de negocio: supermercados, farmacias, electro, moda, deportes, hogar"},
                "limit": {"type": "integer", "default": 10},
            },
            "required": ["query"],
        },
    },
    {
        "name": "market_add",
        "description": "Agregar producto al carrito. Usar product_id y store_key del resultado de market_search. Usar market_lines para ver IDs de tienda válidos.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "string", "description": "Copiar del campo 'product_id' en market_search"},
                "name":       {"type": "string", "description": "Copiar del campo 'name' en market_search"},
                "price":      {"type": "number", "description": "Copiar del campo 'price' en market_search"},
                "store":      {"type": "string", "description": "Copiar del campo 'store_key' en market_search"},
                "quantity":   {"type": "integer", "default": 1},
            },
            "required": ["product_id", "name", "price", "store"],
        },
    },
    {
        "name": "market_cart",
        "description": "Ver carrito actual con productos, cantidades, precios y total.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "market_cart_update",
        "description": "Cambiar la cantidad de un producto en el carrito. Usar quantity=0 para eliminar.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "string", "description": "ID del producto en el carrito (campo 'product_id')"},
                "quantity":   {"type": "integer", "description": "Nueva cantidad (0 = eliminar)"},
            },
            "required": ["product_id", "quantity"],
        },
    },
    {
        "name": "market_cart_remove",
        "description": "Eliminar un producto del carrito por su ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "string", "description": "ID del producto a eliminar del carrito"},
            },
            "required": ["product_id"],
        },
    },
    {
        "name": "market_checkout",
        "description": "Finalizar compra con método de pago.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "payment_method": {"type": "string", "default": "yape"},
            },
        },
    },
    {
        "name": "market_orders",
        "description": "Ver historial de órdenes.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "market_reorder",
        "description": "Repetir la última orden.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "market_ask",
        "description": "Compra por lenguaje natural. 'compra leche', 'repite la última compra', 'compara arroz'.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "prompt": {"type": "string", "description": "Instrucción en lenguaje natural"},
            },
            "required": ["prompt"],
        },
    },
    {
        "name": "market_basket",
        "description": "Comparar el costo total de una canasta de productos entre retailers. Pasa una lista de items con nombre y cantidad. Retorna el total por tienda y cuál es la más barata.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "items": {"type": "array", "description": "Lista de productos, ej: [{\"name\":\"leche\",\"qty\":2},{\"name\":\"arroz\",\"qty\":1}]"},
                "stores": {"type": "array", "description": "Lista opcional de stores. Vacío = todos los retailers."},
            },
            "required": ["items"],
        },
    },
    {
        "name": "market_inflation",
        "description": "Consultar la variación de precios (inflación) desde el data moat. Retorna productos con su delta de precio y un promedio de inflación. Filtrar por país o línea.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "description": "Código de país: AR, BR, MX, CO, PE, CL, IT, FR"},
                "line": {"type": "string", "description": "Línea de negocio: supermercados, farmacias, electro, hogar"},
                "days": {"type": "integer", "description": "Ventana de días para el análisis (default 30)"},
            },
        },
    },
    {
        "name": "market_categories",
        "description": "Explorar el árbol de categorías de un retailer VTEX. Retorna la jerarquía completa de categorías y subcategorías.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "store": {"type": "string", "description": "ID de la tienda (usar market_lines para ver IDs válidos)"},
            },
            "required": ["store"],
        },
    },
    {
        "name": "market_barcode",
        "description": "Buscar producto por código de barras EAN/UPC.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {"type": "string", "description": "Código de barras EAN/UPC"},
            },
            "required": ["code"],
        },
    },
    {
        "name": "market_enrich",
        "description": "Buscar productos en Open Food Facts para enriquecer con datos nutricionales.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Producto a buscar"},
                "limit": {"type": "integer", "default": 5},
            },
            "required": ["query"],
        },
    },
    {
        "name": "market_stores",
        "description": "Listar todos los 30 retailers VTEX verificados con país, moneda, línea de negocio y emoji. Usar para descubrir qué tiendas están disponibles.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "market_countries",
        "description": "Listar los 8 países disponibles con sus retailers y conteo de tiendas por país.",
        "inputSchema": {"type": "object", "properties": {}},
    },
]


def handle_tool(name: str, args: dict) -> str:
    """Dispatch MCP tool calls to the API."""
    tool_map = {
        "market_login":      lambda a: api("POST", "/auth/login", {"username": a["username"], "password": a["password"]}),
        "market_lines":      lambda a: api("GET", "/lines"),
        "market_search":     lambda a: api("POST", "/products/search", {"query": a["query"], "store": a.get("store"), "line": a.get("line"), "limit": a.get("limit", 10)}),
        "market_compare":    lambda a: api("POST", "/products/compare", {"query": a["query"], "line": a.get("line"), "limit": a.get("limit", 10)}),
        "market_add":        lambda a: api("POST", "/cart/add", {"product_id": a["product_id"], "name": a["name"], "price": a["price"], "store": a["store"], "quantity": a.get("quantity", 1)}),
        "market_cart":       lambda a: api("GET", "/cart"),
        "market_cart_update": lambda a: api("PUT", "/cart/update", {"product_id": a["product_id"], "quantity": a["quantity"]}),
        "market_cart_remove": lambda a: api("DELETE", f"/cart/{a['product_id']}"),
        "market_checkout":   lambda a: api("POST", "/checkout", {"payment_method": a.get("payment_method", "yape")}),
        "market_orders":     lambda a: api("GET", "/orders"),
        "market_reorder":    lambda a: api("POST", "/orders/reorder"),
        "market_ask":        lambda a: api("POST", "/agent/ask", {"prompt": a["prompt"]}),
        "market_basket":     lambda a: api("POST", "/v1/basket/compare", {"items": a["items"], "stores": a.get("stores")}),
        "market_inflation":  lambda a: api("GET", f"/v1/intel/inflation?country={a.get('country', '')}&line={a.get('line', '')}"),
        "market_categories": lambda a: api("GET", f"/categories/{a['store']}"),
        "market_barcode":    lambda a: api("GET", f"/products/barcode/{a['code']}"),
        "market_enrich":     lambda a: api("GET", f"/products/enrich?query={a['query']}&limit={a.get('limit', 5)}"),
        "market_stores":     lambda a: api("GET", "/stores"),
        "market_countries":  lambda a: api("GET", "/countries"),
    }
    handler = tool_map.get(name)
    if not handler:
        return json.dumps({"error": f"Unknown tool: {name}"})
    try:
        result = handler(args)
        return json.dumps(result, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)})


def main():
    """MCP JSON-RPC loop over stdio."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            continue

        method = request.get("method", "")
        req_id = request.get("id")

        if method == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {"name": "cli-market", "version": "1.0.0"},
                },
            }
        elif method == "tools/list":
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"tools": TOOLS},
            }
        elif method == "tools/call":
            tool_name = request["params"]["name"]
            tool_args = request["params"].get("arguments", {})
            content = handle_tool(tool_name, tool_args)
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": content}]},
            }
        else:
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Method not found: {method}"},
            }

        sys.stdout.write(json.dumps(response, ensure_ascii=False) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
