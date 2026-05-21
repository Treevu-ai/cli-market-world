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
from pathlib import Path

import httpx

API = os.environ.get("MARKET_API_URL", "http://127.0.0.1:8765")
SESSION_FILE = Path.home() / ".market" / "session.json"


def get_token() -> str:
    if SESSION_FILE.exists():
        return json.loads(SESSION_FILE.read_text()).get("token", "")
    return ""


def api(method: str, path: str, json_data: dict | None = None) -> dict:
    token = get_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        if method == "GET":
            resp = httpx.get(f"{API}{path}", headers=headers, timeout=30)
        elif method == "POST":
            resp = httpx.post(f"{API}{path}", headers=headers, json=json_data, timeout=30)
        elif method == "PUT":
            resp = httpx.put(f"{API}{path}", headers=headers, json=json_data, timeout=30)
        elif method == "DELETE":
            resp = httpx.delete(f"{API}{path}", headers=headers, timeout=30)
        else:
            return {"error": f"Unknown method: {method}"}
        if resp.status_code >= 400:
            return {"error": resp.json().get("detail", resp.text)}
        return resp.json()
    except httpx.ConnectError:
        return {"error": "Server not running. Start: python market_server.py"}


TOOLS = [
    {
        "name": "market_login",
        "description": "Autenticarse en Agentic Market. Requerido antes de otras tools.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "username": {"type": "string", "default": "admin"},
                "password": {"type": "string", "default": "market"},
            },
        },
    },
    {
        "name": "market_lines",
        "description": "Listar las 4 líneas de negocio (supermercados, farmacias, electro, moda, deportes, hogar, financiero, automotriz, libros, viajes, hogar-construcción, educación) con sus retailers VTEX y países.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "market_search",
        "description": "Buscar productos en todos los retailers VTEX (26 retailers en 8 países, 4 líneas). Retorna product_id, name, price, store_key (para usar en market_add), store (nombre legible), line_key y line. Usar 'line' para filtrar por vertical.",
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
]


def handle_search(args: dict) -> dict:
    r = api("POST", "/products/search", {
        "query": args["query"],
        "store": args.get("store"),
        "line": args.get("line"),
        "limit": args.get("limit", 10),
    })
    if "error" in r: return r
    items = []
    for p in r.get("results", [])[:args.get("limit", 10)]:
        items.append({
            "product_id": p["id"],
            "name":       p["name"],
            "brand":      p["brand"],
            "price":      p["price"],
            "store":      p["store_name"],
            "store_key":  p["store"],
            "line":       p.get("line_name", ""),
            "line_key":   p.get("line", ""),
            "url":        p["url"],
        })
    return {"query": r["query"], "total": r["total"], "products": items}


def handle_lines(args: dict) -> dict:
    r = api("GET", "/lines")
    if "error" in r: return r
    return r


def handle_compare(args: dict) -> dict:
    r = api("POST", "/products/compare", {
        "query": args["query"],
        "line": args.get("line"),
        "limit": args.get("limit", 10),
    })
    return r if "error" in r else {"query": r["query"], "comparison": r["comparison"][:10]}


def handle_ask(args: dict) -> dict:
    prompt = args["prompt"].lower().strip()
    import re

    # ── "repite última compra" ──
    if any(w in prompt for w in ["repetir", "repite", "mismo", "última compra", "mes pasado"]):
        r = api("POST", "/orders/reorder")
        return {"message": "Última orden restaurada al carrito", "cart": r.get("cart", [])} if "error" not in r else r

    # ── "compara X" / "X más barato" ──
    if any(w in prompt for w in ["compar", "más barato", "mas barato"]):
        q = re.sub(r'(compara[rm]?\s*|m[aá]s barato\s*)', '', prompt).strip().rstrip(".!?")
        if not q:
            return {"message": "¿Qué producto querés comparar?"}
        # Extraer línea si se menciona
        line = None
        for lk in ["supermercados", "farmacias", "electro", "moda", "deportes", "hogar"]:
            if lk in prompt:
                line = lk
                break
        return handle_compare({"query": q, "line": line})

    # ── "compra 2 leche en farmacias" ──
    m = re.search(r'compra\s+(?:(\d+)\s+)?(.+)', prompt)
    if m:
        qty = int(m.group(1)) if m.group(1) else 1
        item = m.group(2).strip().rstrip(".!?")

        # Extraer línea y tienda del texto
        line = None
        store = None
        for lk in ["supermercados", "farmacias", "electro", "moda", "deportes", "hogar"]:
            if lk in item:
                line = lk
                item = item.replace(lk, "").replace("en", "").strip()
                break

        search_body = {"query": item, "limit": 5}
        if line:
            search_body["line"] = line

        r = api("POST", "/products/search", search_body)
        if "error" in r:
            return {"message": f"No encontré '{item}'", "error": r["error"]}
        prods = r.get("results", [])
        if not prods:
            return {"message": f"No encontré '{item}'", "suggestion": "Probá con un término más general o usá market_search."}

        # Elegir el más barato con precio > 0
        best = min(prods, key=lambda p: p["price"] if p["price"] > 0 else float("inf"))
        add = api("POST", "/cart/add", {
            "product_id": best["id"],
            "name": best["name"],
            "price": best["price"],
            "store": best["store"],
            "quantity": qty,
        })
        if "error" in add:
            return add

        currency = best.get("currency", "")
        return {
            "message": f"Agregué {qty}× '{best['name']}' de {best['store_name']} a {currency} {best['price']}",
            "product": best,
            "quantity": qty,
            "cart": add.get("cart", []),
        }

    # ── "muéstrame X" / "busca X" → search ──
    return handle_search({"query": prompt, "limit": 5})


HANDLERS = {
    "market_login": lambda a: api("POST", "/auth/login", {"username": a.get("username", "admin"), "password": a.get("password", "market")}),
    "market_lines": handle_lines,
    "market_search": handle_search,
    "market_compare": handle_compare,
    "market_add": lambda a: api("POST", "/cart/add", {"product_id": a["product_id"], "name": a["name"], "price": a["price"], "store": a.get("store","wong"), "quantity": a.get("quantity",1)}),
    "market_cart": lambda a: api("GET", "/cart"),
    "market_cart_update": lambda a: api("PUT", "/cart/update", {"product_id": a["product_id"], "quantity": a["quantity"]}),
    "market_cart_remove": lambda a: api("DELETE", f"/cart/{a['product_id']}"),
    "market_checkout": lambda a: api("POST", "/checkout", {"payment_method": a.get("payment_method","yape")}),
    "market_orders": lambda a: api("GET", "/orders"),
    "market_reorder": lambda a: api("POST", "/orders/reorder"),
    "market_ask": handle_ask,
}


def send_rpc(msg: dict) -> None:
    sys.stdout.write(json.dumps(msg, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def run():
    for line in sys.stdin:
        line = line.strip()
        if not line: continue
        try: request = json.loads(line)
        except json.JSONDecodeError: continue
        rid = request.get("id")
        method = request.get("method", "")
        params = request.get("params", {})
        if method == "initialize":
            send_rpc({"jsonrpc":"2.0","id":rid,"result":{"protocolVersion":"2024-11-05","serverInfo":{"name":"agentic-market","version":"1.0.0"},"capabilities":{"tools":{}}}})
        elif method == "tools/list":
            send_rpc({"jsonrpc":"2.0","id":rid,"result":{"tools":TOOLS}})
        elif method == "tools/call":
            name = params.get("name","")
            args = params.get("arguments",{})
            handler = HANDLERS.get(name)
            if handler:
                try:
                    result = handler(args)
                    send_rpc({"jsonrpc":"2.0","id":rid,"result":{"content":[{"type":"text","text":json.dumps(result,indent=2,ensure_ascii=False)}]}})
                except Exception as e:
                    send_rpc({"jsonrpc":"2.0","id":rid,"result":{"content":[{"type":"text","text":str(e)}],"isError":True}})
            else:
                send_rpc({"jsonrpc":"2.0","id":rid,"error":{"code":-32601,"message":f"Tool not found: {name}"}})
        elif method == "notifications/initialized":
            pass
        else:
            send_rpc({"jsonrpc":"2.0","id":rid,"error":{"code":-32601,"message":f"Unknown: {method}"}})


if __name__ == "__main__":
    run()
