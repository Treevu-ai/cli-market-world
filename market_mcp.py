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
import sys
from pathlib import Path

import httpx

API = "http://127.0.0.1:8765"
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
        "name": "market_search",
        "description": "Buscar productos en Wong, Metro y Plaza Vea. Retorna nombre, marca, precio, tienda e ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Término de búsqueda"},
                "store": {"type": "string", "description": "wong, metro, o plazavea (vacío = todas)"},
                "limit": {"type": "integer", "default": 10},
            },
            "required": ["query"],
        },
    },
    {
        "name": "market_compare",
        "description": "Comparar precios entre Wong, Metro y Plaza Vea.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Producto a comparar"},
                "limit": {"type": "integer", "default": 10},
            },
            "required": ["query"],
        },
    },
    {
        "name": "market_add",
        "description": "Agregar producto al carrito.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "string"},
                "name": {"type": "string"},
                "price": {"type": "number"},
                "store": {"type": "string", "description": "wong, metro, o plazavea"},
                "quantity": {"type": "integer", "default": 1},
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
    r = api("POST", "/products/search", {"query": args["query"], "store": args.get("store"), "limit": args.get("limit", 10)})
    if "error" in r: return r
    items = [{"id": p["id"], "name": p["name"], "brand": p["brand"], "price": p["price"], "store": p["store_name"], "url": p["url"]} for p in r.get("results", [])[:args.get("limit", 10)]]
    return {"query": r["query"], "total": r["total"], "products": items}


def handle_compare(args: dict) -> dict:
    r = api("POST", "/products/compare", {"query": args["query"], "limit": args.get("limit", 10)})
    return r if "error" in r else {"query": r["query"], "comparison": r["comparison"][:10]}


def handle_ask(args: dict) -> dict:
    prompt = args["prompt"].lower()
    # "repite última compra" / "lo mismo del mes pasado"
    if any(w in prompt for w in ["repetir", "repite", "mismo", "última compra", "mes pasado"]):
        r = api("POST", "/orders/reorder")
        return {"message": "Última orden restaurada al carrito", "cart": r.get("cart", [])} if "error" not in r else r
    # "compara X" / "X más barato"
    if any(w in prompt for w in ["compar", "más barato", "mas barato"]):
        import re
        q = re.sub(r'(compara[rm]?\s*|m[aá]s barato\s*)', '', prompt).strip().rstrip(".!?")
        return handle_compare({"query": q}) if q else {"message": "¿Qué producto querés comparar?"}
    # "compra X"
    import re
    m = re.search(r'compra\s+(.+)', prompt)
    if m:
        item = m.group(1).strip().rstrip(".!?")
        r = api("POST", "/products/search", {"query": item, "limit": 3})
        if "error" in r: return {"message": f"No encontré '{item}'", "error": r["error"]}
        prods = r.get("results", [])
        if not prods: return {"message": f"No encontré '{item}'"}
        best = min(prods, key=lambda p: p["price"] if p["price"] > 0 else float("inf"))
        add = api("POST", "/cart/add", {"product_id": best["id"], "name": best["name"], "price": best["price"], "store": best["store"], "quantity": 1})
        return {"message": f"Agregué '{best['name']}' de {best['store_name']} a S/ {best['price']}", "product": best, "cart": add.get("cart", [])} if "error" not in add else add
    # default: search
    return handle_search({"query": prompt, "limit": 5})


HANDLERS = {
    "market_login": lambda a: api("POST", "/auth/login", {"username": a.get("username", "admin"), "password": a.get("password", "market")}),
    "market_search": handle_search,
    "market_compare": handle_compare,
    "market_add": lambda a: api("POST", "/cart/add", {"product_id": a["product_id"], "name": a["name"], "price": a["price"], "store": a.get("store","wong"), "quantity": a.get("quantity",1)}),
    "market_cart": lambda a: api("GET", "/cart"),
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
