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

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from market_core import (
    STORES, LINES, COUNTRIES, API, SESSION_FILE, LANG_FILE, LAST_SEARCH_FILE,
    get_token, api,
    CURRENCY_SYMBOLS, fmt_price, store_color, store_emoji,
    save_last_search, load_last_search,
)

console = Console()

# ── i18n ────────────────────────────────────────────────────────────────────
_ = lambda x: x

T = {
    "es": {
        "desc": "Agentic Market CLI — compras desde la terminal.",
        "usage": "market <comando> [opciones]",
        "login": "Autenticarse", "search": "Buscar productos", "compare": "Comparar precios entre tiendas",
        "add": "Agregar al carrito (usa # de tabla o product_id)", "cart": "Ver carrito",
        "cart_remove": "Eliminar un producto del carrito", "cart_update": "Cambiar cantidad de un producto en el carrito",
        "cart_clear": "Vaciar el carrito por completo", "checkout": "Finalizar compra",
        "orders": "Historial de órdenes", "reorder": "Repetir una orden (última si no se especifica ID)",
        "ask": "Compra por lenguaje natural", "preferences": "Ver perfil y preferencias de compra",
        "countries": "Ver países y tiendas disponibles", "lines": "Ver líneas de negocio y sus retailers",
        "about": "Modelo de negocio", "whoami": "Ver sesión activa", "lang": "Cambiar idioma (es/en)",
        "categories": "Explorar categorías de una tienda", "barcode": "Buscar producto por código de barras",
        "enrich": "Buscar con datos de Open Food Facts",
        "query": "Buscar productos", "store": "Tienda específica", "country": "Filtrar por país",
        "line": "Filtrar por línea de negocio", "limit": "Cantidad de resultados", "page": "Página de resultados",
        "product_id": "Número de la tabla de búsqueda (#) o ID de producto",
        "product_name_help": "Nombre del producto (auto-fill si se usa #)",
        "price_help": "Precio (auto-fill si se usa #)", "qty": "Cantidad",
        "payment": "Método de pago", "order_id_help": "ID de la orden a repetir",
        "prompt": "Ej: 'compra leche', 'repite la última', 'compara arroz'",
        "barcode_help": "Código de barras EAN/UPC",
        "lang_code_help": "Código de idioma: es o en",
        "json_help": "Salida machine-readable para agentes IA",
        "username": "Usuario", "password": "Contraseña",
        "product_remove_help": "ID del producto a eliminar del carrito",
        "product_update_help": "ID del producto",
        "quantity_help": "Nueva cantidad (0 = eliminar)",
    },
    "en": {
        "desc": "Agentic Market CLI — purchases from the terminal.",
        "usage": "market <command> [options]",
        "login": "Authenticate", "search": "Search products", "compare": "Compare prices across stores",
        "add": "Add to cart (use table # or product_id)", "cart": "View cart",
        "cart_remove": "Remove product from cart", "cart_update": "Change product quantity in cart",
        "cart_clear": "Clear entire cart", "checkout": "Complete purchase",
        "orders": "Order history", "reorder": "Repeat last order",
        "ask": "Natural language purchase", "preferences": "View profile and preferences",
        "countries": "View countries and stores", "lines": "View business lines and retailers",
        "about": "Business model", "whoami": "View active session", "lang": "Change language (es/en)",
        "categories": "Explore store categories", "barcode": "Search product by barcode",
        "enrich": "Search with Open Food Facts data",
        "query": "Search products", "store": "Specific store", "country": "Filter by country",
        "line": "Filter by business line", "limit": "Number of results", "page": "Results page",
        "product_id": "Table # from search or product ID",
        "product_name_help": "Product name (auto-fill if using #)",
        "price_help": "Price (auto-fill if using #)", "qty": "Quantity",
        "payment": "Payment method", "order_id_help": "Order ID to repeat",
        "prompt": "E.g. 'buy milk', 'repeat last', 'compare rice'",
        "barcode_help": "EAN/UPC barcode",
        "lang_code_help": "Language code: es or en",
        "json_help": "Machine-readable output for AI agents",
        "username": "Username", "password": "Password",
        "product_remove_help": "Product ID to remove from cart",
        "product_update_help": "Product ID",
        "quantity_help": "New quantity (0 = remove)",
    },
}

def get_lang() -> str:
    if LANG_FILE.exists():
        return LANG_FILE.read_text().strip()
    return "es"

def set_lang(code: str) -> None:
    LANG_FILE.parent.mkdir(parents=True, exist_ok=True)
    LANG_FILE.write_text(code)

def t(key: str) -> str:
    lang = get_lang()
    return T.get(lang, {}).get(key, key)

# ── Welcome banner ───────────────────────────────────────────────────────────

WELCOME_BANNER = """\n[#00FF88]  ╭───────────────────────────────────────────────────────────────╮
  │                                                               │
     [#FFFFFF bold] C L I   M A R K E T[/]
     [#888888]infraestructura de comercio para humanos y agentes ia[/]

     [#00FF88]●[/] 27 retailers    [#00FF88]●[/] 11 países       [#00FF88]●[/] 4 líneas
     [#00FF88]●[/] 15 mcp tools       [#00FF88]●[/] api rest        [#00FF88]●[/] json nativo
     [#00FF88]●[/] cross-border       [#00FF88]●[/] autónomo         [#00FF88]●[/] open source

     [#555555]pip install cli-market[/]
     [#555555]github.com/treevu-ai/cli-market-world[/]

     [#00FF88]market login[/]        [#888888]autentícate[/]
     [#00FF88]market search[/]       [#888888]busca en todos los retailers[/]
     [#00FF88]market compare[/]      [#888888]compara precios entre países[/]
     [#00FF88]market ask[/]          [#888888]modo agente: lenguaje natural[/]
     [#00FF88]market checkout[/]     [#888888]completa la compra[/]
     [#00FF88]market --json[/]       [#888888]salida estructurada para agentes[/]

  ╰───────────────────────────────────────────────────────────────╯[/]
"""

WELCOME_BANNER_EN = """\n[#00FF88]  ╭───────────────────────────────────────────────────────────────╮
  │                                                               │
     [#FFFFFF bold] C L I   M A R K E T[/]
     [#888888]commerce infrastructure for humans and ai agents[/]

     [#00FF88]●[/] 27 retailers    [#00FF88]●[/] 11 countries    [#00FF88]●[/] 4 lines
     [#00FF88]●[/] 15 mcp tools       [#00FF88]●[/] api rest        [#00FF88]●[/] json native
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
    return Panel(banner.strip(), border_style="#00FF88", padding=(1, 2))

# ── Helpers ─────────────────────────────────────────────────────────────────

def get_token_with_prompt() -> str:
    token = get_token()
    if not token:
        console.print(Panel.fit(
            "[bold #FFD600]No estás autenticado aún.[/]\n\n"
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
    return token

def cli_api(method: str, path: str, json_data: dict | None = None) -> dict:
    result = api(method, path, json_data)
    if isinstance(result, dict) and "error" in result:
        if result.get("status") == 401:
            console.print(f"[red]Sesión expirada. Ejecutá: market login[/]")
            console.print("[dim]Si usás MARK_API_URL, asegurate de haber hecho login contra ese servidor.[/]")
        else:
            console.print(f"[red]Error: {result['error']}[/]")
        sys.exit(1)
    return result

# ── Commands ─────────────────────────────────────────────────────────────────

def cmd_login(args):
    data = cli_api("POST", "/auth/login", {"username": args.username, "password": args.password})
    console.print(f"[#00FF88]✓ {data.get('message', 'OK')}[/]")
    console.print(f"[dim]Usuario: {data.get('username')}[/]")

def cmd_search(args):
    if not args.query.strip():
        console.print(welcome_banner())
        return
    params = {"query": args.query, "limit": args.limit, "page": args.page}
    if args.store: params["store"] = args.store
    if args.country:
        params["store"] = [k for k, v in STORES.items() if v["country"] == args.country][0] if [k for k, v in STORES.items() if v["country"] == args.country] else None
    if args.line: params["line"] = args.line
    with console.status(f"[cyan]Buscando '{args.query}'..."):
        data = cli_api("POST", "/products/search", params)
    results = data.get("results", [])
    if getattr(args, "json", False):
        console.print(json.dumps(data, indent=2, ensure_ascii=False))
        return
    save_last_search(results)
    if not results:
        console.print(f"\n[yellow]Sin resultados para '{args.query}'[/]")
        return
    table = Table(title=f'[bold white]Resultados: "{args.query}" ({data["total"]})[/]', border_style="dim blue")
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Producto", style="white", max_width=36, no_wrap=False)
    table.add_column("Marca", style="blue", max_width=12)
    table.add_column("Tienda", max_width=12)
    table.add_column("Precio", style="yellow", justify="right")
    table.add_column("Desc.", justify="center", width=6)
    table.add_column("ID", style="dim", max_width=14)
    for i, p in enumerate(results, 1):
        color = store_color(p.get("store", ""))
        disc = p.get("discount")
        price_str = fmt_price(p.get("price", 0), p.get("currency", "PEN"))
        if disc:
            price_str = f"[bold yellow]{price_str}[/]"
            disc_str = f"[#3cffd0]{disc}%[/]"
        else:
            disc_str = "—"
        table.add_row(
            str(i), p["name"], p.get("brand", "—"),
            f"[{color}]{p.get('store_name', p.get('store', '?'))}[/]",
            price_str, disc_str,
            p.get("id", p.get("product_id", "")),
        )
    console.print()
    console.print(table)
    console.print(f"\n[dim]Para agregar al carrito: market add [bold]#[/] [--qty N][/]")
    console.print(f"[dim]Ej: market add 3 --qty 2  (el #3 de la tabla)[/]")

def cmd_compare(args):
    with console.status(f"[cyan]Comparando '{args.query}'..."):
        data = cli_api("POST", "/products/compare", {"query": args.query, "line": args.line, "limit": args.limit})
    comp = data.get("comparison", [])
    if getattr(args, "json", False):
        console.print(json.dumps(data, indent=2, ensure_ascii=False))
        return
    if not comp:
        console.print(f"\n[yellow]Sin resultados para '{args.query}'[/]")
        return
    all_stores: list[str] = []
    seen = set()
    for item in comp:
        for sk in item.get("prices", {}):
            if sk not in seen:
                all_stores.append(sk)
                seen.add(sk)
    display_stores = all_stores[:6]
    table = Table(title=f'[bold white]Comparativa: "{args.query}"[/]', border_style="dim blue")
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Producto", style="white", max_width=30, no_wrap=False)
    table.add_column("Marca", style="blue", max_width=12)
    for sk in display_stores:
        store_name = STORES.get(sk, {}).get("name", sk)
        table.add_column(store_name, justify="right", width=11)
    table.add_column("Mejor", justify="center", width=10)
    for i, item in enumerate(comp, 1):
        prices = item.get("prices", {})
        best = item.get("best_store", "")
        best_color = store_color(best) if best else "dim"
        def pcell(sk):
            if sk in prices:
                currency = STORES.get(sk, {}).get("currency", "PEN")
                return f"[{store_color(sk)}]{fmt_price(prices[sk], currency)}[/]"
            return "[dim]—[/]"
        row = [str(i), item.get("name", ""), item.get("brand", "")]
        for sk in display_stores:
            row.append(pcell(sk))
        row.append(f"[bold {best_color}]{STORES.get(best, {}).get('name', best)}[/]" if best else "—")
        table.add_row(*row)
    console.print()
    console.print(table)

def cmd_add(args):
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
    data = cli_api("POST", "/cart/add", {
        "product_id": pid, "name": name or pid,
        "price": price or 0, "store": store or "wong",
        "quantity": args.qty,
    })
    cart = data.get("cart", [])
    total = sum(i["price"] * i["quantity"] for i in cart)
    console.print(f"[#3cffd0]✓ Agregado al carrito[/] ({len(cart)} items, total: {fmt_price(total)})")

def cmd_cart(args):
    data = cli_api("GET", "/cart")
    if getattr(args, "json", False):
        console.print(json.dumps(data, indent=2, ensure_ascii=False))
        return
    cart = data.get("cart", [])
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
            str(i), item["name"],
            f"[{color}]{item.get('store_name', '?')}[/]",
            fmt_price(item["price"]), str(item["quantity"]), fmt_price(sub),
        )
    console.print()
    console.print(table)
    total = data.get("total", 0)
    console.print(f"\n[bold]Total: [bold yellow]{fmt_price(total)}[/] — {data.get('items', 0)} items[/]")
    console.print("[dim]market checkout → finalizar compra[/]")

def cmd_cart_remove(args):
    data = cli_api("DELETE", f"/cart/{args.product_id}")
    console.print(f"[#3cffd0]✓ {data.get('message', 'Eliminado')}[/]")

def cmd_cart_update(args):
    data = cli_api("PUT", "/cart/update", {"product_id": args.product_id, "quantity": args.quantity})
    console.print(f"[#3cffd0]✓ {data.get('message', 'Actualizado')}[/]")

def cmd_cart_clear(args):
    data = cli_api("GET", "/cart")
    cart = data.get("cart", [])
    if not cart:
        console.print("[yellow]Carrito ya está vacío[/]")
        return
    for item in cart:
        cli_api("DELETE", f"/cart/{item['product_id']}")
    console.print("[#3cffd0]✓ Carrito vaciado[/]")

def cmd_checkout(args):
    data = cli_api("POST", "/checkout", {"payment_method": args.payment})
    order = data.get("order", {})
    console.print(f"[#00FF88]✓ {data.get('message', 'Compra completada')}[/]")
    console.print(f"[bold]Orden: {order.get('order_id', '?')}[/] — Total: {fmt_price(order.get('total', 0))}")

def cmd_orders(args):
    data = cli_api("GET", "/orders")
    orders = data.get("orders", [])
    if not orders:
        console.print("[yellow]Sin órdenes previas[/]")
        return
    table = Table(title="[bold white]Historial de órdenes[/]", border_style="dim blue")
    table.add_column("ID", style="bold")
    table.add_column("Fecha", style="dim", max_width=20)
    table.add_column("Items", max_width=40)
    table.add_column("Total", style="bold yellow", justify="right")
    table.add_column("Pago", style="dim")
    for o in reversed(orders):
        items_str = ", ".join(f"{i['quantity']}x {i['name'][:15]}" for i in o.get("items", [])[:3])
        table.add_row(o.get("order_id", "?"), o.get("created_at", "")[:19], items_str,
                       fmt_price(o.get("total", 0)), o.get("payment_method", "?"))
    console.print(table)

def cmd_reorder(args):
    data = cli_api("POST", "/orders/reorder")
    console.print(f"[#3cffd0]✓ {data.get('message', 'OK')}[/]")

def cmd_ask(args):
    data = cli_api("POST", "/agent/ask", {"prompt": args.prompt})
    console.print(f"[#3cffd0]✓ {data.get('message', 'OK')}[/]")

def cmd_preferences(args):
    data = cli_api("GET", "/agent/preferences")
    console.print(f"[bold]Total gastado:[/] {fmt_price(data.get('total_spent', 0))}")
    console.print(f"[bold]Órdenes:[/] {data.get('total_orders', 0)}")

def cmd_countries(args):
    data = cli_api("GET", "/countries")
    countries = data.get("countries", {})
    table = Table(title="[bold #3cffd0]Países[/]", border_style="dim blue")
    table.add_column("País", style="bold")
    table.add_column("Tiendas")
    table.add_column("Cant.", justify="center")
    for code, info in sorted(countries.items()):
        table.add_row(info["name"], ", ".join(info["stores"]), str(info["count"]))
    console.print()
    console.print(table)
    console.print(f"\n[dim]market search --country PE[/] [dim]para buscar en un solo país[/]")

def cmd_lines(args):
    data = cli_api("GET", "/lines")
    lines = data.get("lines", {})
    table = Table(title="[bold #3cffd0]Líneas de negocio[/]", border_style="dim blue")
    table.add_column("Línea", style="bold")
    table.add_column("Retailers")
    table.add_column("Cant.", justify="center")
    for line_id, info in lines.items():
        stores_str = ", ".join(s["name"] for s in info["stores"].values())
        table.add_row(f"{info['emoji']} {info['name']}", stores_str, str(info["total_stores"]))
    console.print()
    console.print(table)

def cmd_categories(args):
    with console.status(f"[cyan]Cargando categorías de {STORES[args.store]['name']}..."):
        data = cli_api("GET", f"/categories/{args.store}")
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
    with console.status(f"[cyan]Buscando código {args.code}..."):
        data = cli_api("GET", f"/products/barcode/{args.code}")
    table = Table(title=f"[bold #3cffd0]Código: {args.code}[/]", border_style="dim blue")
    for k, v in data.items():
        if v:
            table.add_row(k, str(v)[:100])
    console.print(table)

def cmd_enrich(args):
    with console.status(f"[cyan]Buscando '{args.query}' en Open Food Facts..."):
        data = cli_api("GET", f"/products/enrich?query={args.query}&limit={args.limit}")
    results = data.get("results", [])
    table = Table(title=f"[bold #3cffd0]Open Food Facts: {args.query} ({data.get('total', 0):,} total)[/]", border_style="dim blue")
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

def cmd_basket(args):
    items = []
    for arg in args.items:
        if ":" in arg:
            name, qty = arg.split(":", 1)
            items.append({"name": name, "qty": int(qty)})
        else:
            items.append({"name": arg, "qty": 1})
    stores = []
    if args.country:
        stores = [k for k, v in STORES.items() if v["country"] == args.country]
    with console.status("[cyan]Comparando canasta..."):
        data = cli_api("POST", "/v1/basket/compare", {"items": items, "stores": stores or None})
    if getattr(args, "json", False):
        console.print(json.dumps(data, indent=2, ensure_ascii=False))
        return
    comp = data.get("comparison", {})
    if not comp:
        console.print("[yellow]No se encontraron productos en ninguna tienda[/]")
        return
    table = Table(title="[bold white]Comparativa de canasta[/]", border_style="dim blue")
    table.add_column("Tienda", style="bold")
    table.add_column("Productos", max_width=50)
    table.add_column("Total", style="bold yellow", justify="right")
    for store_key, info in sorted(comp.items(), key=lambda x: x[1]["total"]):
        items_str = ", ".join(f"{i['qty']}x {i['name'][:15]}" for i in info["items"][:3])
        table.add_row(info["store_name"], items_str, f"{info['currency']} {info['total']:.2f}")
    console.print(table)
    best = data.get("best_store")
    if best:
        console.print(f"\n[#00FF88]✓ Mejor opción: {comp[best]['store_name']} — {comp[best]['currency']} {comp[best]['total']:.2f}[/]")

def cmd_inflation(args):
    params = []
    if args.country: params.append(f"country={args.country}")
    if args.line: params.append(f"line={args.line}")
    qs = "&".join(params)
    with console.status("[cyan]Calculando inflación..."):
        data = cli_api("GET", f"/v1/intel/inflation?{qs}" if qs else "/v1/intel/inflation")
    if getattr(args, "json", False):
        console.print(json.dumps(data, indent=2, ensure_ascii=False))
        return
    items = data.get("items", [])
    avg = data.get("avg_inflation_pct", 0)
    color = "#FF6B35" if avg > 0 else "#00FF88"
    console.print(f"\n[bold]Inflación promedio: [{color}]{avg:+.1f}%[/] ({len(items)} productos rastreados)[/]")
    if items:
        table = Table(title="[bold white]Variación de precios[/]", border_style="dim blue")
        table.add_column("Producto", max_width=35)
        table.add_column("Desde", style="dim")
        table.add_column("Hasta", style="dim")
        table.add_column("Δ %", justify="right")
        for i in items[:15]:
            c = "#FF6B35" if i["delta_pct"] > 0 else "#00FF88"
            table.add_row(i["product"][:35], f"{i['currency']} {i['first_price']:.2f}", f"{i['currency']} {i['last_price']:.2f}", f"[{c}]{i['delta_pct']:+.1f}%[/]")
        console.print(table)

def cmd_alerts(args):
    if args.action == "list":
        data = cli_api("POST", "/v1/alerts", {"product": "", "action": "list"})
        alerts_list = data.get("alerts", [])
        if not alerts_list:
            console.print("[yellow]No hay alertas configuradas.[/]")
            return
        for a in alerts_list:
            console.print(f"  🔔 {a['product']} | threshold: {a['threshold_pct']}%")
    else:
        data = cli_api("POST", "/v1/alerts", {"product": args.product, "threshold_pct": args.threshold, "action": "create"})
        console.print(f"[#3cffd0]✓ Alerta creada para {args.product}[/]")

def cmd_about(args):
    console.print(Panel.fit(
        "[bold #00FF88]CLI Market[/] — Infraestructura de comercio para agentes IA.\n\n"
        "[#888888]Un solo pip install. Una API. 27 retailers en 11 países.[/]\n"
        "[#888888]Comparación de precios cross-border. Data moat con precios reales.[/]\n"
        "[#888888]Open source (MIT). Gratis para developers.[/]\n\n"
        "[dim]github.com/Treevu-ai/cli-market-world[/]",
        border_style="#00FF88"
    ))

def cmd_whoami(args):
    data = cli_api("GET", "/auth/whoami")
    console.print(f"[#3cffd0]✓ {data.get('username', '?')}[/]")

def cmd_lang(args):
    if args.lang_code:
        set_lang(args.lang_code)
        console.print(f"[#3cffd0]Idioma cambiado a {args.lang_code}[/]")
    else:
        current = get_lang()
        console.print(f"[dim]Idioma actual: {current}. Usá market lang en para inglés.[/]")

# ── Main ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description=t("desc"), usage=t("usage"))
    parser.add_argument("--json", action="store_true", help=t("json_help"))
    sub = parser.add_subparsers(dest="command")

    # login
    p = sub.add_parser("login", help=t("login"))
    p.add_argument("--username", default="admin", help=t("username"))
    p.add_argument("--password", default="market", help=t("password"))

    # search
    p = sub.add_parser("search", help=t("search"))
    p.add_argument("query", nargs="?", default="")
    p.add_argument("--store", "-s", choices=list(STORES.keys()), default=None)
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default=None)
    p.add_argument("--line", choices=list(LINES.keys()), default=None)
    p.add_argument("--limit", "-l", type=int, default=10)
    p.add_argument("--page", "-p", type=int, default=1)

    # compare
    p = sub.add_parser("compare", help=t("compare"))
    p.add_argument("query", nargs="?", default="")
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default=None)
    p.add_argument("--line", choices=list(LINES.keys()), default=None)
    p.add_argument("--limit", "-l", type=int, default=10)

    # add
    p = sub.add_parser("add", help=t("add"))
    p.add_argument("product_id")
    p.add_argument("--name")
    p.add_argument("--price", type=float, default=None)
    p.add_argument("--store", "-s", choices=list(STORES.keys()), default=None)
    p.add_argument("--qty", type=int, default=1)

    # cart
    sub.add_parser("cart", help=t("cart"))

    # cart-remove
    p = sub.add_parser("cart-remove", help=t("cart_remove"))
    p.add_argument("product_id")

    # cart-update
    p = sub.add_parser("cart-update", help=t("cart_update"))
    p.add_argument("product_id")
    p.add_argument("quantity", type=int)

    # cart-clear
    sub.add_parser("cart-clear", help=t("cart_clear"))

    # checkout
    p = sub.add_parser("checkout", help=t("checkout"))
    p.add_argument("--payment", choices=["yape", "plin", "tarjeta"], default="yape")

    # orders
    sub.add_parser("orders", help=t("orders"))

    # reorder
    p = sub.add_parser("reorder", help=t("reorder"))
    p.add_argument("order_id", nargs="?", default=None)

    # ask
    p = sub.add_parser("ask", help=t("ask"))
    p.add_argument("prompt")

    # preferences
    sub.add_parser("preferences", help=t("preferences"))

    # categories
    p = sub.add_parser("categories", help=t("categories"))
    p.add_argument("store", choices=list(STORES.keys()))

    # barcode
    p = sub.add_parser("barcode", help=t("barcode"))
    p.add_argument("code")

    # enrich
    p = sub.add_parser("enrich", help=t("enrich"))
    p.add_argument("query")
    p.add_argument("--limit", "-l", type=int, default=5)

    # countries
    sub.add_parser("countries", help=t("countries"))

    # lines
    sub.add_parser("lines", help=t("lines"))

    # about
    sub.add_parser("about", help=t("about"))

    # whoami
    sub.add_parser("whoami", help=t("whoami"))

    # lang
    p_lang = sub.add_parser("lang", help=t("lang"))
    p_lang.add_argument("lang_code", nargs="?")

    # basket
    p = sub.add_parser("basket", help="Comparar canasta completa entre retailers")
    p.add_argument("items", nargs="+", help="Productos con cantidad, ej: leche:2 arroz:1")
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default=None)

    # inflation
    p = sub.add_parser("inflation", help="Ver inflación desde el data moat")
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default=None)
    p.add_argument("--line", choices=list(LINES.keys()), default=None)

    # alerts
    p = sub.add_parser("alerts", help="Gestionar alertas de precios")
    p.add_argument("action", nargs="?", default="list", choices=["list", "create"])
    p.add_argument("--product")
    p.add_argument("--threshold", type=float, default=5.0)

    args = parser.parse_args()
    if not args.command:
        console.print(welcome_banner())
        return

    handlers = {
        "login": cmd_login, "search": cmd_search, "compare": cmd_compare,
        "add": cmd_add, "cart": cmd_cart,
        "cart-remove": cmd_cart_remove, "cart-update": cmd_cart_update,
        "cart-clear": cmd_cart_clear, "checkout": cmd_checkout,
        "orders": cmd_orders, "reorder": cmd_reorder,
        "ask": cmd_ask, "preferences": cmd_preferences,
        "countries": cmd_countries, "lines": cmd_lines,
        "categories": cmd_categories, "barcode": cmd_barcode,
        "enrich": cmd_enrich, "basket": cmd_basket,
        "inflation": cmd_inflation, "alerts": cmd_alerts,
        "about": cmd_about, "whoami": cmd_whoami, "lang": cmd_lang,
    }
    handler = handlers.get(args.command)
    if handler:
        handler(args)

if __name__ == "__main__":
    main()
