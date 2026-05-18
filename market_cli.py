#!/usr/bin/env python3
"""
market — Agentic Market CLI.

Sistema operativo de compras desde la terminal.
Busca productos reales en Wong, Metro y Plaza Vea,
agrega al carrito y hace checkout.

Uso:
    market login
    market search "leche sin lactosa"
    market compare "aceite"
    market add 560748 --qty 2
    market cart
    market checkout
    market orders
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

API = os.environ.get("MARKET_API_URL", "http://127.0.0.1:8765")
SESSION_FILE = Path.home() / ".market" / "session.json"
LANG_FILE = Path.home() / ".market" / "lang"
console = Console()

def get_lang() -> str:
    try: return LANG_FILE.read_text().strip()[:2]
    except Exception: return "es"

def set_lang(code: str) -> None:
    LANG_FILE.parent.mkdir(parents=True, exist_ok=True)
    LANG_FILE.write_text(code)

LANG = get_lang()

# ── JSON-able business model (agent-friendly) ──────────────────────

BUSINESS_MODEL_JSON = {
    "company": "CLI Market LATAM",
    "version": "1.0.0",
    "positioning": "Infrastructure layer that transforms traditional LATAM supermarkets into AI-agent compatible commerce systems.",
    "solution": {
        "agent_layer": True,
        "mcp_compatible": True,
        "semantic_search": True,
        "autonomous_checkout": True,
        "multi_retailer_support": True,
        "integrated_stores": ["wong", "metro", "plazavea"],
    },
    "business_model": {
        "saas_b2b": {"starter": "$499/mo", "growth": "$1,999/mo", "enterprise": "custom"},
        "api_usage": {"metrics": ["search_requests", "checkout_executions", "agent_actions"]},
        "transaction_fee": "1-5% per order",
        "white_label": "Retailers deploy infrastructure under their own brand",
    },
    "latam_expansion": {
        "phase_1": ["Peru", "Chile", "Colombia"],
        "phase_2": ["Mexico", "Brazil", "Argentina"],
    },
    "pitch": "Stripe transformed payments into APIs. CLI Market LATAM transforms supermarkets into APIs for AI agents.",
}

WELCOME_BANNER = """\
[#00FF88]  ─────────────────────────────────────────────────────────────
                                                                   
     [#FFFFFF bold] C L I   M A R K E T[/]                                   
     [#888888]infraestructura de comercio para humanos y agentes IA[/]                       
                                                                   
     [#00FF88]●[/] 3,603 retailers    [#00FF88]●[/] 67 paises       [#00FF88]●[/] 12 lineas        
     [#00FF88]●[/] 12 herramientas    [#00FF88]●[/] api rest        [#00FF88]●[/] json nativo      
     [#00FF88]●[/] cross-border       [#00FF88]●[/] autonomo         [#00FF88]●[/] open source      
                                                                   
     [#555555]pip install cli-market[/]                                    
     [#555555]github.com/treevu-ai/cli-market-world[/]                     
                                                                   
     [#00FF88]market login[/]        [#888888]autenticate[/]                       
     [#00FF88]market search[/]       [#888888]busca en todos los retailers[/]           
     [#00FF88]market compare[/]      [#888888]compara precios entre paises[/]            
     [#00FF88]market ask[/]          [#888888]modo agente: lenguaje natural[/]           
     [#00FF88]market checkout[/]     [#888888]completa la compra[/]                  
     [#00FF88]market --json[/]       [#888888]salida estructurada para agentes[/]        
                                                                   
  ─────────────────────────────────────────────────────────────[/]

"""


WELCOME_BANNER_EN = """\n[#00FF88]  ╭───────────────────────────────────────────────────────────────╮
  │                                                               │
     [#FFFFFF bold] C L I   M A R K E T[/]                                   
     [#888888]commerce infrastructure for humans and ai agents[/]             
                                                                   
     [#00FF88]●[/] 3,603 retailers    [#00FF88]●[/] 67 countries    [#00FF88]●[/] 12 lines         
     [#00FF88]●[/] 12 mcp tools       [#00FF88]●[/] api rest        [#00FF88]●[/] json native      
     [#00FF88]●[/] cross-border       [#00FF88]●[/] autonomous       [#00FF88]●[/] open source      
                                                                   
     [#555555]pip install cli-market[/]                                    
     [#555555]github.com/treevu-ai/cli-market-world[/]                     
                                                                   
     [#00FF88]market login[/]        [#888888]authenticate[/]                     
     [#00FF88]market search[/]       [#888888]search across all retailers[/]        
     [#00FF88]market compare[/]      [#888888]cross-country price comparison[/]      
     [#00FF88]market ask[/]          [#888888]agent mode: natural language[/]         
     [#00FF88]market checkout[/]     [#888888]complete purchase[/]                 
     [#00FF88]market --json[/]       [#888888]structured output for agents[/]         
                                                                   
  ╰───────────────────────────────────────────────────────────────╯[/]
"""

def welcome_banner():
    banner = WELCOME_BANNER_EN if get_lang() == "en" else WELCOME_BANNER
    from rich.panel import Panel
    return Panel(banner.strip(), border_style="#00FF88", padding=(1, 2))

# ── Helpers ─────────────────────────────────────────────────────────────────

def get_token() -> str:
    if not SESSION_FILE.exists():
        console.print(Panel.fit(
            "[bold #FFD600]No estas autenticado aun.[/]\n\n"
            "[#888888]Para usar CLI Market necesitas un token de acceso.[/]\n"
            "[#888888]Es gratis. Toma 5 segundos:[/]\n\n"
            "  [#00FF88 bold]1.[/] Ejecuta:  [#00FF88]market login[/]\n"
            "  [#00FF88 bold]2.[/] Usuario: [#FFFFFF bold]admin[/]\n"
            "  [#00FF88 bold]3.[/] Password: [#FFFFFF bold]market[/]\n\n"
            "[dim]El servidor genera tu token automaticamente.[/]\n"
            "[dim]Si eres un agente IA: usa market --json para integrarte.[/]",
            title="CLI Market",
            border_style="#FFD600"
        ))
        sys.exit(1)
    data = json.loads(SESSION_FILE.read_text())
    return data["token"]


def api(method: str, path: str, json_data: dict | None = None) -> dict:
    token = None
    if path not in ("/auth/login", "/"):
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
            raise ValueError(f"Unknown method: {method}")
        if resp.status_code >= 400:
            detail = resp.json().get("detail", resp.text)
            console.print(f"[red]Error: {detail}[/]")
            sys.exit(1)
        return resp.json()
    except httpx.ConnectError:
        console.print("[red]Error: No se pudo conectar al servidor. Ejecuta primero: python market_server.py[/]")
        sys.exit(1)


# ── Currency symbols ─────────────────────────────────────────────────────────

CURRENCY_SYMBOLS = {
    "PEN": "S/", "ARS": "ARS", "BRL": "R$", "MXN": "MXN", "COP": "COP",
    "CLP": "CLP", "EUR": "€", "GBP": "£",
}


def fmt_price(price: float, currency: str = "PEN") -> str:
    symbol = CURRENCY_SYMBOLS.get(currency, currency)
    return f"{symbol} {price:,.2f}"


def store_color(store: str) -> str:
    colors = {
        "wong": "#3cffd0", "metro": "#5200ff", "plazavea": "#ffe600",
        "carrefour": "#3cffd0", "jumbo_ar": "#00FF88", "carrefour_br": "#3cffd0",
        "chedraui": "#FF6B35", "heb": "#FF6B35",
        "olimpica": "#60A5FA", "exito": "#60A5FA",
        "drogaraia": "#FF6B35", "drogasil": "#FF6B35",
        "magazineluiza": "#A78BFA", "motorola_br": "#A78BFA",
        "renner": "#FFD600", "centauro": "#4ADE80", "homecenter": "#F5F5F0",
        "carrefour_es": "#FFD600", "decathlon_fr": "#4ADE80",
    }
    return colors.get(store, "#e9e9e9")


def store_emoji(store: str) -> str:
    if store in STORES:
        return STORES[store].get("emoji", "📦")
    return "📦"


# ── Last-search cache (for market add auto-fill) ─────────────────────────────

LAST_SEARCH_FILE = Path.home() / ".market" / "last_search.json"


def save_last_search(results: list[dict]) -> None:
    slim = []
    for p in results[:50]:
        slim.append({
            "product_id": p.get("id", p.get("product_id", "")),
            "name": p.get("name", ""),
            "price": p.get("price", 0),
            "store": p.get("store", ""),
            "store_name": p.get("store_name", ""),
            "currency": p.get("currency", "PEN"),
            "brand": p.get("brand", ""),
        })
    LAST_SEARCH_FILE.parent.mkdir(parents=True, exist_ok=True)
    LAST_SEARCH_FILE.write_text(json.dumps(slim, ensure_ascii=False))


def load_last_search() -> list[dict]:
    if LAST_SEARCH_FILE.exists():
        try:
            return json.loads(LAST_SEARCH_FILE.read_text())
        except (json.JSONDecodeError, KeyError):
            pass
    return []


# ── Comandos ───────────────────────────────────────────────────────────────

def cmd_lang(args):
    if not args.lang_code:
        from rich.panel import Panel
        g=get_lang()
        msg = f"Idioma actual: [#00FF88]{g}[/]\n\n"
        msg += "[#888888]Idiomas disponibles:[/]\n"
        msg += "  [#00FF88]es[/] espanol\n"
        msg += "  [#00FF88]en[/] english\n\n"
        msg += "[dim]Usa: market lang es  o  market lang en[/]"
        console.print(Panel.fit(msg, border_style="#00FF88"))
        return
    code=args.lang_code.strip()[:2]
    if code not in ("es","en"):
        console.print("[red]Idioma no valido. Usa es o en.[/]")
        return
    set_lang(code)
    global LANG
    LANG=code
    console.print(f"[#00FF88]Idioma cambiado a {code}[/]")

def cmd_login(args):
    """Autentica al usuario contra el servidor."""
    username = args.username
    password = args.password

    # Interactive mode — guide the newbie
    if not username:
        console.print(Panel.fit(
            "[bold #00FF88]Bienvenido a CLI Market[/]\n\n"
            "[#888888]Vas a crear tu token de acceso.[/]\n"
            "[#888888]Es un solo paso y queda guardado en tu equipo.[/]\n\n"
            "[#888888]Si eres un agente IA: este token activa 12 herramientas MCP.[/]\n\n"
            "[dim]Credenciales por defecto:[/]\n"
            "  Usuario: [#FFFFFF bold]admin[/]\n"
            "  Password: [#FFFFFF bold]market[/]",
            border_style="#00FF88"
        ))
        username = console.input("[#00FF88]Usuario:[/] ")
        if not username:
            console.print("[red]Cancelado.[/]")
            return

    if not password:
        password = console.input("[#00FF88]Password:[/] ", password=True)
        if not password:
            console.print("[red]Cancelado.[/]")
            return

    data = api("POST", "/auth/login", {"username": username, "password": password})
    console.print(f"\n[#00FF88]✓ Autenticado como [bold]{data['username']}[/][/]")
    console.print(f"[dim]Token guardado en {SESSION_FILE}[/]")
    console.print(f"\n[#888888]Ahora puedes buscar productos:[/]")
    console.print(f"  [#00FF88]market search[/] [dim]\"leche\" --country PE[/]")
    console.print(f"\n[dim]Tip para agentes:[/] [#00FF88]market --json[/] [dim]te da salida estructurada[/]")


def cmd_search(args):
    """Busca productos. Soporta --country, --line, --store, --page."""
    if not args.query:
        console.print("[yellow]USO: market search <término> [--line LINEA] [--country PAIS] [--store TIENDA] [--limit N] [--page N][/]")
        console.print("[dim]Ej: market search \"leche\" --line supermercados --country PE[/]")
        return

    stores_to_search = [args.store] if args.store else None
    if args.country and not args.store:
        country_stores = [k for k, v in STORES.items() if v["country"] == args.country]
        stores_to_search = country_stores

    label = args.store or args.country or args.line or "todas"
    if args.line:
        label = LINES[args.line]["name"]
    with console.status(f"[cyan]Buscando '{args.query}' en {label}..."):
        data = api("POST", "/products/search", {
            "query": args.query,
            "store": args.store,
            "line": args.line,
            "limit": args.limit,
            "page": getattr(args, "page", 1),
        })
        if args.country and not args.store:
            data["results"] = [p for p in data["results"] if p["store"] in stores_to_search]
            data["total"] = len(data["results"])

    results = data["results"]
    if not results:
        console.print(f"\n[yellow]Sin resultados para '{args.query}'[/]")
        return

    # Cache results for market add auto-fill
    save_last_search(results)

    table = Table(
        title=f'[bold white]"{args.query}" — {len(results)} resultados[/]',
        border_style="dim blue",
        show_lines=False,
    )
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Producto", style="white", max_width=38, no_wrap=False)
    table.add_column("Marca", style="blue", max_width=14)
    table.add_column("Tienda", max_width=12)
    table.add_column("Precio", style="bold yellow", justify="right", width=12)
    table.add_column("Desc.", justify="center", width=7)
    table.add_column("ID", style="dim", max_width=20)

    for i, p in enumerate(results, 1):
        color = store_color(p["store"])
        disc = p.get("discount")
        currency = p.get("currency", "PEN")
        price_str = fmt_price(p["price"], currency)
        if disc:
            price_str = f"[bold yellow]{price_str}[/]"
            disc_str = f"[#3cffd0]{disc}%[/]"
        else:
            disc_str = "—"

        table.add_row(
            str(i),
            p["name"],
            p["brand"],
            f"[{color}]{p['store_name']}[/]",
            price_str,
            disc_str,
            p.get("id", p.get("product_id", "")),
        )

    console.print()
    console.print(table)
    console.print(f"\n[dim]Para agregar al carrito: market add [bold]#[/] [--qty N][/]")
    console.print(f"[dim]Ej: market add 3 --qty 2  (el #3 de la tabla)[/]")


def cmd_compare(args):
    """Compara precios. Columnas dinámicas según los stores en los resultados."""
    with console.status(f"[cyan]Comparando '{args.query}'..."):
        data = api("POST", "/products/compare", {"query": args.query, "line": args.line, "limit": args.limit})

    comp = data["comparison"]
    if not comp:
        console.print(f"\n[yellow]Sin resultados para '{args.query}'[/]")
        return

    # Extraer todas las tiendas que aparecen en los resultados (columnas dinámicas)
    all_stores: list[str] = []
    seen = set()
    for item in comp:
        for sk in item.get("prices", {}):
            if sk not in seen:
                all_stores.append(sk)
                seen.add(sk)

    # Limitar a 6 columnas máximo en pantalla
    display_stores = all_stores[:6]
    if len(all_stores) > 6:
        console.print(f"[dim]Mostrando {len(display_stores)} de {len(all_stores)} tiendas.[/]")

    table = Table(
        title=f'[bold white]Comparativa: "{args.query}"[/]',
        border_style="dim blue",
    )
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Producto", style="white", max_width=30, no_wrap=False)
    table.add_column("Marca", style="blue", max_width=12)
    for sk in display_stores:
        store_name = STORES.get(sk, {}).get("name", sk)
        table.add_column(store_name, justify="right", width=11)
    table.add_column("Mejor", justify="center", width=10)

    for i, item in enumerate(comp, 1):
        prices = item["prices"]
        best = item["best_store"]
        best_color = store_color(best) if best else "dim"

        def pcell(sk):
            if sk in prices:
                currency = STORES.get(sk, {}).get("currency", "PEN")
                return f"[{store_color(sk)}]{fmt_price(prices[sk], currency)}[/]"
            return "[dim]—[/]"

        row = [str(i), item["name"], item["brand"]]
        for sk in display_stores:
            row.append(pcell(sk))
        row.append(f"[bold {best_color}]{STORES[best]['name']}[/]" if best else "—")
        table.add_row(*row)

    console.print()
    console.print(table)


def cmd_add(args):
    """Agrega un producto al carrito. Auto-fill desde último search si se usa # de tabla."""
    # Si el product_id es un número de tabla (1-based), buscar en cache
    pid = args.product_id
    name = args.name
    price = args.price
    store = args.store

    if pid.isdigit() and not name and not price:
        idx = int(pid) - 1
        cache = load_last_search()
        if 0 <= idx < len(cache):
            p = cache[idx]
            pid = p["product_id"]
            name = name or p["name"]
            price = price if price else p["price"]
            store = store or p["store"]

    data = api("POST", "/cart/add", {
        "product_id": pid,
        "name": name or pid,
        "price": price or 0,
        "store": store or "wong",
        "quantity": args.qty,
    })
    cart = data["cart"]
    total = sum(i["price"] * i["quantity"] for i in cart)
    console.print(f"[#3cffd0]✓ Agregado al carrito[/] ({len(cart)} items, total: {fmt_price(total)})")


def cmd_cart(args):
    """Muestra el carrito actual."""
    data = api("GET", "/cart")
    cart = data["cart"]
    if not cart:
        console.print("[yellow]Carrito vacío[/]")
        console.print("[dim]market search <término> → market add <ID>[/]")
        return

    table = Table(title="[bold white]Carrito[/]", border_style="dim blue")
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Producto", style="white", max_width=36, no_wrap=False)
    table.add_column("Tienda", max_width=10)
    table.add_column("Precio", style="yellow", justify="right")
    table.add_column("Cant.", justify="center", width=5)
    table.add_column("Subtotal", style="bold yellow", justify="right")

    for i, item in enumerate(cart, 1):
        color = store_color(item.get("store", ""))
        sub = item["price"] * item["quantity"]
        table.add_row(
            str(i),
            item["name"],
            f"[{color}]{item.get('store_name', '?')}[/]",
            fmt_price(item["price"]),
            str(item["quantity"]),
            fmt_price(sub),
        )

    console.print()
    console.print(table)

    total = data["total"]
    console.print(f"\n[bold]Total: [bold yellow]{fmt_price(total)}[/] — {data['items']} items[/]")
    console.print("[dim]market checkout → finalizar compra[/]")


def cmd_cart_remove(args):
    """Elimina un producto del carrito."""
    data = api("DELETE", f"/cart/{args.product_id}")
    console.print(f"[#3cffd0]✓ {data.get('message', 'Eliminado')}[/]")
    if "cart" in data:
        console.print(f"[dim]Carrito: {data.get('items', 0)} items, total: {fmt_price(data.get('total', 0))}[/]")


def cmd_cart_update(args):
    """Cambia la cantidad de un producto del carrito."""
    data = api("PUT", "/cart/update", {"product_id": args.product_id, "quantity": args.quantity})
    console.print(f"[#3cffd0]✓ {data.get('message', 'Actualizado')}[/]")
    if "cart" in data:
        total = sum(i["price"] * i["quantity"] for i in data["cart"])
        console.print(f"[dim]Carrito: {len(data['cart'])} items, total: {fmt_price(total)}[/]")


def cmd_cart_clear(args):
    """Vacía el carrito completo."""
    data = api("GET", "/cart")
    cart = data.get("cart", [])
    if not cart:
        console.print("[yellow]Carrito ya está vacío[/]")
        return
    for item in cart:
        api("DELETE", f"/cart/{item.get('cart_id', item.get('product_id', ''))}")
    console.print(f"[#3cffd0]✓ Carrito vaciado ({len(cart)} items eliminados)[/]")


def cmd_checkout(args):
    """Finaliza la compra."""
    payment = args.payment or "yape"
    data = api("POST", "/checkout", {"payment_method": payment})
    order = data["order"]
    console.print(Panel.fit(
        f"[bold #3cffd0]✓ Compra completada[/]\n\n"
        f"Orden: [bold]{order['order_id']}[/]\n"
        f"Total: [bold yellow]{fmt_price(order['total'])}[/]\n"
        f"Pago: {order['payment_method']}\n"
        f"Items: {len(order['items'])}",
        title="Checkout",
        border_style="green",
    ))


def cmd_orders(args):
    """Historial de órdenes con detalle de ítems."""
    data = api("GET", "/orders")
    orders = data["orders"]
    if not orders:
        console.print("[yellow]Sin órdenes previas[/]")
        return

    table = Table(title="[bold white]Historial de órdenes[/]", border_style="dim blue")
    table.add_column("Orden", style="bold", width=10)
    table.add_column("Fecha", style="dim", width=12)
    table.add_column("Ítems", style="white", max_width=45, no_wrap=False)
    table.add_column("Total", style="bold yellow", justify="right")
    table.add_column("Pago", width=10)

    for o in reversed(orders):
        date = o["created_at"][:10] if "created_at" in o else "?"
        item_names = ", ".join(f"{i.get('quantity',1)}× {i.get('name','?')[:20]}" for i in o.get("items", [])[:4])
        if len(o.get("items", [])) > 4:
            item_names += f" +{len(o['items']) - 4} más"
        table.add_row(
            o["order_id"],
            date,
            item_names,
            fmt_price(o["total"]),
            o.get("payment_method", "?"),
        )

    console.print()
    console.print(table)
    console.print(f"\n[dim]{len(orders)} órdenes — market reorder [orden_id] para repetir una específica[/]")


def cmd_reorder(args):
    """Repite una orden. Si se pasa ID, repite esa; si no, la última."""
    if getattr(args, "order_id", None):
        # Buscar la orden específica y restaurar sus ítems al carrito
        data = api("GET", "/orders")
        orders = data.get("orders", [])
        target = next((o for o in orders if o["order_id"] == args.order_id), None)
        if not target:
            console.print(f"[yellow]Orden '{args.order_id}' no encontrada[/]")
            return
        # Limpiar carrito y agregar los ítems de la orden
        current = api("GET", "/cart")
        for item in current.get("cart", []):
            api("DELETE", f"/cart/{item.get('cart_id', item.get('product_id', ''))}")
        for item in target.get("items", []):
            api("POST", "/cart/add", {
                "product_id": item["product_id"],
                "name": item["name"],
                "price": item["price"],
                "store": item.get("store", "wong"),
                "quantity": item.get("quantity", 1),
            })
        cart = api("GET", "/cart")
        total = sum(i["price"] * i["quantity"] for i in cart.get("cart", []))
        console.print(f"[#3cffd0]✓ Orden {args.order_id} restaurada al carrito[/] ({len(cart.get('cart', []))} items, {fmt_price(total)})")
    else:
        data = api("POST", "/orders/reorder")
        cart = data["cart"]
        total = sum(i["price"] * i["quantity"] for i in cart)
        console.print(f"[#3cffd0]✓ Última orden restaurada al carrito[/] ({len(cart)} items, {fmt_price(total)})")
    console.print("[dim]market cart → market checkout[/]")


def cmd_ask(args):
    """Compra por lenguaje natural."""
    with console.status("[cyan]Pensando..."):
        data = api("POST", "/agent/ask", {"prompt": args.prompt})
    if "message" in data:
        console.print(f"[#3cffd0]{data['message']}[/]")
    if "cart" in data:
        cart = data["cart"]
        total = sum(i["price"] * i["quantity"] for i in cart)
        console.print(f"[dim]Carrito: {len(cart)} items, {fmt_price(total)}[/]")
    if "comparison" in data:
        comp = data["comparison"][:5]
        for c in comp:
            stores = ", ".join(f"{s}: {fmt_price(p)}" for s, p in c["prices"].items())
            console.print(f"  {c['name'][:50]} | {stores}")
    if "results" in data:
        for p in data["results"][:5]:
            console.print(f"  {p['name'][:50]} | {p['store_name']} | {fmt_price(p['price'])}")


def cmd_preferences(args):
    """Muestra preferencias inferidas del historial."""
    data = api("GET", "/agent/preferences")
    console.print(f"[bold]Perfil de compra:[/] {data['username']}")
    console.print(f"  Órdenes: {data['total_orders']}")
    console.print(f"  Total gastado: {fmt_price(data['total_spent'])}")
    if data.get("favorite_store"):
        console.print(f"  Tienda favorita: [bold]{data['favorite_store']}[/]")
    if data.get("last_order_date"):
        console.print(f"  Última compra: {data['last_order_date'][:10]}")


def cmd_countries(args):
    """Lista países y tiendas disponibles."""
    data = api("GET", "/countries")
    countries = data.get("countries", {})
    table = Table(title="[bold #3cffd0]Países y supermercados[/]", border_style="dim blue")
    table.add_column("País", style="bold", width=14)
    table.add_column("Tiendas", style="white", width=50)
    table.add_column("Cant.", justify="center", width=6)

    for code, info in countries.items():
        stores_list = ", ".join(STORES[s]["name"] for s in info["stores"] if s in STORES)
        emoji = STORES.get(info["stores"][0], {}).get("emoji", "")
        table.add_row(f"{emoji} {info['name']}", stores_list, str(info["count"]))

    console.print()
    console.print(table)
    console.print(f"\n[dim]market search --country PE[/] [dim]para buscar en un solo país[/]")


def cmd_lines(args):
    """Lista líneas de negocio con sus retailers."""
    data = api("GET", "/lines")
    lines = data.get("lines", {})

    table = Table(title="[bold #3cffd0]Líneas de negocio[/]", border_style="dim blue")
    table.add_column("Línea", style="bold", width=22)
    table.add_column("Retailers", width=45)
    table.add_column("Cant.", justify="center", width=6)

    for line_id, info in lines.items():
        stores_str = ", ".join(s["name"] for s in info["stores"].values())
        table.add_row(f"{info['emoji']} {info['name']}", stores_str, str(info["total_stores"]))

    console.print()
    console.print(table)
    console.print(f"\n[dim]market search --line farmacias \"paracetamol\"[/] [dim]para buscar en una línea[/]")


def cmd_categories(args):
    """Muestra el árbol de categorías de una tienda."""
    with console.status(f"[cyan]Cargando categorías de {STORES[args.store]['name']}..."):
        data = api("GET", f"/categories/{args.store}")
    if isinstance(data, list):
        _print_cat_tree(data, indent=0)
    else:
        console.print(f"[yellow]Sin categorías para {args.store}[/]")


def _print_cat_tree(cats, indent):
    for c in cats[:15]:
        name = c.get("name", "?")
        children = c.get("children", [])
        prefix = "  " * indent + ("▸ " if indent > 0 else "● ")
        console.print(f"{prefix}[bold]{name}[/] [dim]({len(children)} subcats)[/]")
        if children and indent < 1:
            _print_cat_tree(children, indent + 1)


def cmd_barcode(args):
    """Busca un producto por código de barras."""
    with console.status(f"[cyan]Buscando código {args.code}..."):
        data = api("GET", f"/products/barcode/{args.code}")
    table = Table(title=f"[bold #3cffd0]Código: {args.code}[/]", border_style="dim blue")
    for k, v in data.items():
        if v:
            table.add_row(k, str(v)[:100])
    console.print(table)


def cmd_enrich(args):
    """Busca productos en Open Food Facts."""
    with console.status(f"[cyan]Buscando '{args.query}' en Open Food Facts..."):
        data = api("GET", f"/products/enrich?query={args.query}&limit={args.limit}")
    results = data.get("results", [])
    table = Table(title=f"[bold #3cffd0]Open Food Facts: {args.query} ({data['total']:,} total)[/]", border_style="dim blue")
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Producto", style="white", max_width=35, no_wrap=False)
    table.add_column("Marca", style="blue", max_width=15)
    table.add_column("Nutri", justify="center", width=6)
    table.add_column("Barcode", style="dim", width=15)
    for i, p in enumerate(results, 1):
        ns = p.get("nutriscore", "?")
        ns_color = {"A": "green", "B": "green", "C": "yellow", "D": "red", "E": "red"}.get(ns, "dim")
        table.add_row(str(i), p.get("name", "?")[:35], p.get("brand", "?")[:15], f"[{ns_color}]{ns}[/]", p.get("barcode", ""))
    console.print()
    console.print(table)


def cmd_whoami(args):
    """Muestra el usuario autenticado."""
    try:
        data = api("GET", "/auth/whoami")
        console.print(f"[#3cffd0]Sesión activa: [bold]{data['username']}[/][/]")
    except SystemExit:
        pass


# ── Store config (duplicated for CLI standalone use) ───────────────────────

STORES = {
    "wong":      {"name": "Wong",       "country": "PE", "currency": "PEN", "emoji": "🇵🇪", "line": "supermercados"},
    "metro":     {"name": "Metro",      "country": "PE", "currency": "PEN", "emoji": "🇵🇪", "line": "supermercados"},
    "plazavea":  {"name": "Plaza Vea",  "country": "PE", "currency": "PEN", "emoji": "🇵🇪", "line": "supermercados"},
    "carrefour": {"name": "Carrefour",  "country": "AR", "currency": "ARS", "emoji": "🇦🇷", "line": "supermercados"},
    "jumbo_ar":  {"name": "Jumbo",      "country": "AR", "currency": "ARS", "emoji": "🇦🇷", "line": "supermercados"},
    "carrefour_br": {"name": "Carrefour", "country": "BR", "currency": "BRL", "emoji": "🇧🇷", "line": "supermercados"},
    "chedraui":  {"name": "Chedraui",   "country": "MX", "currency": "MXN", "emoji": "🇲🇽", "line": "supermercados"},
    "heb":       {"name": "HEB",        "country": "MX", "currency": "MXN", "emoji": "🇲🇽", "line": "supermercados"},
    "olimpica":  {"name": "Olímpica",   "country": "CO", "currency": "COP", "emoji": "🇨🇴", "line": "supermercados"},
    "exito":     {"name": "Éxito",      "country": "CO", "currency": "COP", "emoji": "🇨🇴", "line": "supermercados"},
    "drogaraia": {"name": "Droga Raia",  "country": "BR", "currency": "BRL", "emoji": "🇧🇷", "line": "farmacias"},
    "drogasil":  {"name": "Drogasil",    "country": "BR", "currency": "BRL", "emoji": "🇧🇷", "line": "farmacias"},
    "magazineluiza": {"name": "Magazine Luiza", "country": "BR", "currency": "BRL", "emoji": "🇧🇷", "line": "electro"},
    "motorola_br":   {"name": "Motorola",       "country": "BR", "currency": "BRL", "emoji": "🇧🇷", "line": "electro"},
    "renner":    {"name": "Lojas Renner", "country": "BR", "currency": "BRL", "emoji": "🇧🇷", "line": "moda"},
    "centauro":  {"name": "Centauro",     "country": "BR", "currency": "BRL", "emoji": "🇧🇷", "line": "deportes"},
    "homecenter":{"name": "Homecenter",   "country": "CO", "currency": "COP", "emoji": "🇨🇴", "line": "hogar"},
    "carrefour_es": {"name": "Carrefour España", "country": "ES", "currency": "EUR", "emoji": "🇪🇸", "line": "supermercados"},
    "decathlon_fr":  {"name": "Decathlon",       "country": "FR", "currency": "EUR", "emoji": "🇫🇷", "line": "deportes"},
}

LINES = {
    "supermercados": {"name": "Supermercados",       "emoji": "🛒"},
    "farmacias":     {"name": "Farmacias y Salud",   "emoji": "💊"},
    "electro":       {"name": "Electro y Tecnología","emoji": "📱"},
    "moda":          {"name": "Moda y Calzado",       "emoji": "👕"},
    "deportes":      {"name": "Deportes y Fitness",   "emoji": "⚽"},
    "hogar":         {"name": "Hogar y Construcción", "emoji": "🏠"},
}

COUNTRIES = {
    "PE": "Perú",
    "AR": "Argentina",
    "BR": "Brasil",
    "MX": "México",
    "CO": "Colombia",
    "CL": "Chile",
    "ES": "España",
    "FR": "Francia",
    "IT": "Italia",
    "GB": "Reino Unido",
}


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Agentic Market CLI — compras desde la terminal.",
        usage="market <comando> [opciones]",
    )
    sub = parser.add_subparsers(dest="command")

    # login
    p = sub.add_parser("login", help="Autenticarse")
    p.add_argument("--username", default="admin")
    p.add_argument("--password", default="market")

    # search
    p = sub.add_parser("search", help="Buscar productos")
    p.add_argument("query", nargs="?", default="")
    p.add_argument("--store", "-s", choices=list(STORES.keys()), default=None)
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default=None)
    p.add_argument("--line", choices=list(LINES.keys()), default=None, help="Filtrar por línea de negocio")
    p.add_argument("--limit", "-l", type=int, default=10)
    p.add_argument("--page", "-p", type=int, default=1, help="Página de resultados")

    # compare
    p = sub.add_parser("compare", help="Comparar precios entre tiendas")
    p.add_argument("query", nargs="?", default="")
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default=None, help="Filtrar por país")
    p.add_argument("--line", choices=list(LINES.keys()), default=None, help="Filtrar por línea de negocio")
    p.add_argument("--limit", "-l", type=int, default=10)

    # add
    p = sub.add_parser("add", help="Agregar al carrito (usa # de tabla o product_id)")
    p.add_argument("product_id", help="Número de la tabla de búsqueda (#) o ID de producto")
    p.add_argument("--name", help="Nombre del producto (auto-fill si se usa #)")
    p.add_argument("--price", type=float, default=None, help="Precio (auto-fill si se usa #)")
    p.add_argument("--store", "-s", choices=list(STORES.keys()), default=None)
    p.add_argument("--qty", type=int, default=1)

    # cart
    sub.add_parser("cart", help="Ver carrito")

    # cart-remove
    p = sub.add_parser("cart-remove", help="Eliminar un producto del carrito")
    p.add_argument("product_id", help="ID del producto a eliminar")

    # cart-update
    p = sub.add_parser("cart-update", help="Cambiar cantidad de un producto en el carrito")
    p.add_argument("product_id", help="ID del producto")
    p.add_argument("quantity", type=int, help="Nueva cantidad (0 = eliminar)")

    # cart-clear
    sub.add_parser("cart-clear", help="Vaciar el carrito por completo")

    # checkout
    p = sub.add_parser("checkout", help="Finalizar compra")
    p.add_argument("--payment", choices=["yape", "plin", "tarjeta"], default="yape")

    # orders
    sub.add_parser("orders", help="Historial de órdenes")

    # reorder
    p = sub.add_parser("reorder", help="Repetir una orden (última si no se especifica ID)")
    p.add_argument("order_id", nargs="?", default=None, help="ID de la orden a repetir")

    # ask
    p = sub.add_parser("ask", help="Compra por lenguaje natural")
    p.add_argument("prompt", help="Ej: 'compra leche', 'repite la última', 'compara arroz'")

    # preferences
    sub.add_parser("preferences", help="Ver perfil y preferencias de compra")

    # categories
    p = sub.add_parser("categories", help="Explorar categorías de una tienda")
    p.add_argument("store", choices=list(STORES.keys()), help="Tienda")

    # barcode
    p = sub.add_parser("barcode", help="Buscar producto por código de barras")
    p.add_argument("code", help="Código de barras EAN/UPC")

    # enrich
    p = sub.add_parser("enrich", help="Buscar con datos de Open Food Facts")
    p.add_argument("query", help="Término de búsqueda")
    p.add_argument("--limit", "-l", type=int, default=5)

    # countries
    sub.add_parser("countries", help="Ver países y tiendas disponibles")

    # lines
    sub.add_parser("lines", help="Ver líneas de negocio y sus retailers")

    # about
    sub.add_parser("about", help="Modelo de negocio")

    # whoami
    sub.add_parser("whoami", help="Ver sesión activa")
    p_lang=sub.add_parser("lang", help="Cambiar idioma (es/en)")
    p_lang.add_argument("lang_code", nargs="?", help="Codigo de idioma: es o en")

    parser.add_argument("--json", action="store_true", help="Salida machine-readable para agentes IA")

    args = parser.parse_args()

    if args.command is None:
        if args.json:
            import json as _json
            console.print(_json.dumps(BUSINESS_MODEL_JSON, indent=2, ensure_ascii=False))
        else:
            console.print(welcome_banner())
            console.print(Panel.fit(
                "[#888888]¿Es tu primera vez?[/] [#00FF88]market login[/] [#888888]→ autentificate (usuario: admin, password: market)[/]\n"
                "[#888888]¿Quieres buscar algo?[/] [#00FF88]market search[/] [#888888]\"producto\" --country PE[/]\n"
                "[#888888]¿Eres un agente IA?[/] [#00FF88]market --json[/] [#888888]→ salida estructurada MCP para LLMs[/]\n"
                "[#888888]¿No sabes por donde empezar?[/] [#00FF88]market --help[/] [#888888]→ todos los comandos[/]",
                border_style="#1A1A1A"
            ))
        return

    if args.json and args.command == "about":
        import json as _json
        console.print(_json.dumps(BUSINESS_MODEL_JSON, indent=2, ensure_ascii=False))
        return

    commands = {
        "login":    cmd_login,
        "search":   cmd_search,
        "compare":  cmd_compare,
        "add":      cmd_add,
        "cart":     cmd_cart,
        "cart-remove": cmd_cart_remove,
        "cart-update": cmd_cart_update,
        "cart-clear":  cmd_cart_clear,
        "checkout": cmd_checkout,
        "orders":   cmd_orders,
        "reorder":  cmd_reorder,
        "ask":      cmd_ask,
        "preferences": cmd_preferences,
        "countries": cmd_countries,
        "lines":     cmd_lines,
        "categories": cmd_categories,
        "barcode":  cmd_barcode,
        "enrich":   cmd_enrich,
        "about":    lambda a: console.print(BUSINESS_MODEL_BANNER),
        "lang":     cmd_lang,
        "whoami":   cmd_whoami,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
