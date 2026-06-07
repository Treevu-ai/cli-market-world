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

from rich.console import Console
from rich.panel import Panel
from rich import box
from rich.align import Align
from rich.text import Text
from rich.columns import Columns
from rich.table import Table

from market_core import (
    STORES, LINES, COUNTRIES, LANG_FILE, SESSION_FILE, get_token, api, API,
    fmt_price, store_color, save_last_search, load_last_search,
)
import market_ui as ui
from market_stats import (
    COUNTRIES as MS_COUNTRIES, MCP_TOOLS, RETAILERS_VERIFIED,
    PRICES_VERIFIED_LABEL, INDICATORS_COUNT, PLATFORM_LIST_ES, PLATFORM_LIST_EN,
    PRICES_REFRESH_HOURS, PACKAGE_VERSION,
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
        "about": "Modelo de negocio", "whoami": "Ver sesión activa", "account": "Dashboard tier, uso y upgrade", "lang": "Cambiar idioma (es/en)",
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
        "hello": "Onboarding post-install y próximos pasos",
        "register": "Crear cuenta free y API key (sk-)",
        "share": "Link de referido para compartir CLI Market",
        "upgrade": "Solicitar Pro — email con link de pago",
        "doctor": "Diagnóstico: API, auth, tier y MCP",
        "init": "Onboarding completo: API, cuenta, MCP",
        "shell": "Sesión interactiva tipo agente (REPL)",
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
        "about": "Business model", "whoami": "View active session", "account": "Account dashboard: tier, usage, upgrade", "lang": "Change language (es/en)",
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
        "hello": "Post-install onboarding and next steps",
        "register": "Create free account and API key (sk-)",
        "share": "Referral link to share CLI Market",
        "upgrade": "Request Pro — email with payment link",
        "doctor": "Diagnostics: API, auth, tier, and MCP",
        "init": "Full onboarding: API, account, MCP",
        "shell": "Interactive agent-style session (REPL)",
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

     [#00FF88]>[/] 30 retailers    [#00FF88]>[/] 8 países       [#00FF88]>[/] 36 mcp tools
     [#00FF88]>[/] cross-border       [#00FF88]>[/] autónomo         [#00FF88]>[/] open source

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

     [#00FF88]>[/] 30 retailers    [#00FF88]>[/] 8 countries    [#00FF88]>[/] 36 mcp tools
     [#00FF88]>[/] cross-border       [#00FF88]>[/] autonomous       [#00FF88]>[/] open source

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
    is_en = get_lang() == "en"
    n_countries = len(MS_COUNTRIES)
    stats = (
        f"[#00FF88]>[/] {RETAILERS_VERIFIED} retailers    "
        f"[#00FF88]>[/] {n_countries} {'countries' if is_en else 'países'}    "
        f"[#00FF88]>[/] {MCP_TOOLS} mcp tools"
    )
    if is_en:
        body = WELCOME_BANNER_EN.replace(
            "[#00FF88]>[/] 30 retailers    [#00FF88]>[/] 8 countries    [#00FF88]>[/] 36 mcp tools",
            stats,
        ).replace(
            "[#00FF88]market login[/]        [#888888]authenticate[/]",
            "[#00FF88]market register[/]     [#888888]free API key[/]\n"
            "     [#00FF88]market login[/]        [#888888]existing account[/]",
        )
    else:
        body = WELCOME_BANNER.replace(
            "[#00FF88]>[/] 30 retailers    [#00FF88]>[/] 8 países       [#00FF88]>[/] 36 mcp tools",
            stats,
        ).replace(
            "[#00FF88]market login[/]        [#888888]autentícate[/]",
            "[#00FF88]market register[/]     [#888888]API key gratis[/]\n"
            "     [#00FF88]market login[/]        [#888888]cuenta existente[/]",
        )
    return Panel(body.strip(), border_style="#00FF88", padding=(1, 2))

# ── Helpers ─────────────────────────────────────────────────────────────────

def get_token_with_prompt() -> str:
    token = get_token()
    if not token:
        if ui.is_json_mode():
            ui.json_exit(
                console,
                False,
                error="Not authenticated",
                hint="register or login",
                next_commands=["market register", "market login", "market doctor"],
                status=401,
            )
        en = ui.is_en()
        ui.print_actionable_error(
            console,
            "No esta autenticado." if not en else "Not authenticated.",
            status=401,
            title="Auth" if en else "Autenticacion",
        )
        sys.exit(1)
    return token

def cli_api(method: str, path: str, json_data: dict | None = None) -> dict:
    result = api(method, path, json_data)
    if isinstance(result, dict) and "error" in result:
        err = str(result.get("error", "Unknown error"))
        status = result.get("status")
        cmds = ui.error_next_commands(status, err)
        if ui.is_json_mode():
            ui.json_exit(
                console,
                False,
                error=err,
                next_commands=cmds,
                status=status,
            )
        if status == 401:
            ui.print_actionable_error(
                console,
                "Sesion expirada o token invalido." if not ui.is_en() else "Session expired or invalid token.",
                status=401,
            )
        else:
            ui.print_actionable_error(console, err, status=status)
        ui.print_hints(console, cmds)
        sys.exit(1)
    return result

# ── Commands ─────────────────────────────────────────────────────────────────

def cmd_login(args):
    data = cli_api("POST", "/auth/login", {"username": args.username, "password": args.password})
    console.print(f"[#00FF88]✓ {data.get('message', 'OK')}[/]")
    console.print(f"[dim]Usuario: {data.get('username')}[/]")
    console.print(f"[dim]Token guardado en {SESSION_FILE}[/]")

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
        ui.emit_json(ui.json_response(True, data, next_commands=[
            f'market compare "{args.query}"',
            "market add 1 --qty 2",
        ]), console)
        return
    save_last_search(results)
    if not results:
        console.print(f"\n[yellow]Sin resultados para '{args.query}'[/]")
        return
    table = Table(title=f'[bold white]Resultados: "{args.query}" ({data["total"]})[/]', border_style=ui.TABLE_BORDER)
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
    ui.price_data_footer(console)
    if args.country:
        ui.set_default_country(args.country)
    q = args.query.replace('"', '\\"')
    cc = f" --country {args.country}" if args.country else f" --country {ui.get_default_country()}"
    ui.print_hints(console, [
        f'market compare "{q}"{cc}',
        "market add 1 --qty 2",
        "market basket leche:1",
    ])

def cmd_compare(args):
    with console.status(f"[cyan]Comparando '{args.query}'..."):
        data = cli_api("POST", "/products/compare", {"query": args.query, "line": args.line, "limit": args.limit})
    comp = data.get("comparison", [])
    if getattr(args, "json", False):
        ui.emit_json(ui.json_response(True, data, next_commands=[
            "market add 1 --qty 2",
            f'market search "{args.query}"',
        ]), console)
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
    table = Table(title=f'[bold white]Comparativa: "{args.query}"[/]', border_style=ui.TABLE_BORDER)
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Producto", style="white", max_width=30, no_wrap=False)
    table.add_column("Marca", style="blue", max_width=12)
    for sk in display_stores:
        store_name = STORES.get(sk, {}).get("name", sk)
        table.add_column(store_name, justify="right", width=11)
    table.add_column("Mejor", justify="center", width=10)
    def _pcell(sk: str, prices: dict) -> str:
        if sk in prices:
            currency = STORES.get(sk, {}).get("currency", "PEN")
            return f"[{store_color(sk)}]{fmt_price(prices[sk], currency)}[/]"
        return "[dim]—[/]"

    for i, item in enumerate(comp, 1):
        prices = item.get("prices", {})
        best = item.get("best_store", "")
        best_color = store_color(best) if best else "dim"
        row = [str(i), item.get("name", ""), item.get("brand", "")]
        for sk in display_stores:
            row.append(_pcell(sk, prices))
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
    table = Table(title="[bold white]Carrito[/]", border_style=ui.TABLE_BORDER)
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
    tier = ui.fetch_tier()
    ui.tier_gate(console, "checkout", tier, json_args=args)
    routes = {
        "yape": "/checkout/yape",
        "plin": "/checkout/yape",
        "tarjeta": "/checkout/paypal",
        "paypal": "/checkout/paypal",
    }
    path = routes.get(args.payment, "/checkout/yape")
    data = cli_api("POST", path, {})
    order_id = data.get("order_id", "?")
    total = data.get("total", 0)
    currency = data.get("currency", "PEN")
    status = data.get("status", "pending")

    if data.get("approve_url"):
        console.print(Panel.fit(
            f"[bold]Orden {order_id}[/] — {currency} {total:.2f}\n\n"
            f"Completa el pago en PayPal:\n[cyan underline]{data['approve_url']}[/]\n\n"
            "[dim]Tras pagar, la orden pasa a 'paid' vía webhook.[/]",
            title="Checkout PayPal",
            border_style="#00FF88",
        ))
        return

    if data.get("checkout_url"):
        console.print(Panel.fit(
            f"[bold]Orden {order_id}[/] — {currency} {total:.2f}\n\n"
            f"[cyan underline]{data['checkout_url']}[/]",
            title="Checkout",
            border_style="#00FF88",
        ))
        return

    msg = data.get("message", "Orden creada — pago pendiente")
    console.print(f"[#00FF88]✓ {msg}[/]")
    console.print(f"[bold]Orden: {order_id}[/] — Total: {currency} {total:.2f} — Estado: {status}")
    if data.get("qr_url"):
        console.print(f"[dim]QR: {data['qr_url']}[/]")

def cmd_orders(args):
    data = cli_api("GET", "/orders")
    orders = data.get("orders", [])
    if not orders:
        console.print("[yellow]Sin órdenes previas[/]")
        return
    table = Table(title="[bold white]Historial de órdenes[/]", border_style=ui.TABLE_BORDER)
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
    table = Table(title="[bold #3cffd0]Países[/]", border_style=ui.TABLE_BORDER)
    table.add_column("País", style="bold")
    table.add_column("Tiendas")
    table.add_column("Cant.", justify="center")
    for _code, info in sorted(countries.items()):
        table.add_row(info["name"], ", ".join(info["stores"]), str(info["count"]))
    console.print()
    console.print(table)
    console.print("\n[dim]market search --country PE[/] [dim]para buscar en un solo país[/]")

def cmd_lines(args):
    data = cli_api("GET", "/lines")
    lines = data.get("lines", {})
    table = Table(title="[bold #3cffd0]Líneas de negocio[/]", border_style=ui.TABLE_BORDER)
    table.add_column("Línea", style="bold")
    table.add_column("Retailers")
    table.add_column("Cant.", justify="center")
    for _line_id, info in lines.items():
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
    table = Table(title=f"[bold #3cffd0]Código: {args.code}[/]", border_style=ui.TABLE_BORDER)
    for k, v in data.items():
        if v:
            table.add_row(k, str(v)[:100])
    console.print(table)

def cmd_enrich(args):
    with console.status(f"[cyan]Buscando '{args.query}' en Open Food Facts..."):
        data = cli_api("GET", f"/products/enrich?query={args.query}&limit={args.limit}")
    results = data.get("results", [])
    table = Table(title=f"[bold #3cffd0]Open Food Facts: {args.query} ({data.get('total', 0):,} total)[/]", border_style=ui.TABLE_BORDER)
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
    table = Table(title="[bold white]Comparativa de canasta[/]", border_style=ui.TABLE_BORDER)
    table.add_column("Tienda", style="bold")
    table.add_column("Productos", max_width=50)
    table.add_column("Total", style="bold yellow", justify="right")
    for _store_key, info in sorted(comp.items(), key=lambda x: x[1]["total"]):
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
        table = Table(title="[bold white]Variación de precios[/]", border_style=ui.TABLE_BORDER)
        table.add_column("Producto", max_width=35)
        table.add_column("Desde", style="dim")
        table.add_column("Hasta", style="dim")
        table.add_column("Δ %", justify="right")
        for i in items[:15]:
            c = "#FF6B35" if i["delta_pct"] > 0 else "#00FF88"
            table.add_row(i["product"][:35], f"{i['currency']} {i['first_price']:.2f}", f"{i['currency']} {i['last_price']:.2f}", f"[{c}]{i['delta_pct']:+.1f}%[/]")
        console.print(table)

def cmd_indicators(args):
    if args.refresh:
        qs = f"country={args.country}" if args.country else ""
        with console.status("[cyan]Refrescando indicadores..."):
            data = cli_api("POST", f"/v1/intel/refresh?{qs}" if qs else "/v1/intel/refresh")
        if getattr(args, "json", False):
            console.print(json.dumps(data, indent=2, ensure_ascii=False))
            return
        console.print(
            f"[#3cffd0]✓ Indicadores actualizados — "
            f"internal={data.get('internal_written', 0)} "
            f"external={data.get('external_written', 0)} "
            f"enrichment={data.get('enrichment_written', 0)}[/]"
        )
        return

    with console.status("[cyan]Cargando catálogo de indicadores..."):
        catalog = cli_api("GET", "/v1/intel/indicators")
    items = catalog.get("indicators", [])
    if getattr(args, "json", False):
        if args.country:
            latest = cli_api("GET", f"/v1/intel/scores?country={args.country}")
            console.print(json.dumps({"catalog": catalog, "scores": latest}, indent=2, ensure_ascii=False))
        else:
            console.print(json.dumps(catalog, indent=2, ensure_ascii=False))
        return

    cc = args.country or ui.get_default_country()
    meta = (
        f"{len(items)} indicadores · país {cc}"
        if not ui.is_en()
        else f"{len(items)} indicators · country {cc}"
    )
    ui.print_section_header(
        console,
        "Data Moat",
        subtitle=(
            "Catálogo por capa (anaquel | macro)"
            if not ui.is_en()
            else "Catalog by layer (shelf | macro)"
        ),
        meta=meta,
    )
    ui.print_indicator_catalog(console, items)

    if args.country:
        scores = cli_api("GET", f"/v1/intel/scores?country={args.country}")
        sc = scores.get("scores", {})
        panel = ui.scores_panel(sc, country=args.country, width=ui.layout_width(console))
        if panel:
            console.print()
            console.print(panel)
        elif not ui.is_en():
            console.print("[yellow]Sin scores aún. Corré: market indicators --refresh -c PE[/]")
        else:
            console.print("[yellow]No scores yet. Run: market indicators --refresh -c PE[/]")

    ui.print_intel_footer(
        console,
        ["market indicators --refresh -c PE", "market scores -c PE", "market enrichment -c PE"],
    )


def cmd_scores(args):
    params = []
    if args.country:
        params.append(f"country={args.country}")
    if args.line:
        params.append(f"line={args.line}")
    qs = "&".join(params)
    with console.status("[cyan]Calculando scores compuestos..."):
        data = cli_api("GET", f"/v1/intel/scores?{qs}" if qs else "/v1/intel/scores")
    if getattr(args, "json", False):
        console.print(json.dumps(data, indent=2, ensure_ascii=False))
        return
    scores = data.get("scores", {})
    if not scores:
        msg = (
            "Sin scores aún. Corré: market indicators --refresh -c PE"
            if not ui.is_en()
            else "No scores yet. Run: market indicators --refresh -c PE"
        )
        console.print(f"[yellow]{msg}[/]")
        return
    country = data.get("country") or "global"
    ui.print_section_header(
        console,
        "Scores compuestos" if not ui.is_en() else "Composite scores",
        meta=f"{'país' if not ui.is_en() else 'country'} {country}",
    )
    panel = ui.scores_panel(scores, country=country, width=ui.layout_width(console))
    if panel:
        console.print(panel)
    disclaimer = data.get("disclaimer", "")
    if disclaimer:
        console.print(f"[dim]{disclaimer}[/]")
    ui.print_intel_footer(console, ["market indicators --refresh -c PE", "market enrichment -c PE"])


def cmd_enrichment(args):
    cc = args.country or "PE"
    if args.refresh:
        with console.status(f"[cyan]Refrescando enriquecimiento — {cc}..."):
            refresh_data = cli_api("POST", f"/v1/intel/enrichment/refresh?country={cc}")
        if getattr(args, "json", False):
            console.print(json.dumps(refresh_data, indent=2, ensure_ascii=False))
            return
        console.print(
            f"[#3cffd0]✓ Enriquecimiento actualizado — "
            f"written={refresh_data.get('enrichment_written', 0)} · {cc}[/]"
        )

    with console.status(f"[cyan]Cargando enriquecimiento — {cc}..."):
        data = cli_api("GET", f"/v1/intel/enrichment?country={cc}")
    items = data.get("indicators", [])
    if getattr(args, "json", False):
        console.print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    if not items:
        msg = (
            "Sin datos aún. Corré: market enrichment --refresh -c PE"
            if not ui.is_en()
            else "No data yet. Run: market enrichment --refresh -c PE"
        )
        console.print(f"[yellow]{msg}[/]")
        return

    ui.print_section_header(
        console,
        "Enriquecimiento" if not ui.is_en() else "Enrichment",
        subtitle="OFF · Wiki · clima · food CPI",
        meta=f"{len(items)} señales · {cc}" if not ui.is_en() else f"{len(items)} signals · {cc}",
    )

    col_w = ui.column_width(console)
    score_panel = None
    try:
        scores = cli_api("GET", f"/v1/intel/scores?country={cc}")
        sc = scores.get("scores", {})
        score_panel = ui.scores_panel(
            sc,
            country=cc,
            width=col_w,
            subset=ui.ENRICHMENT_SCORE_KEYS,
        )
    except Exception:
        pass

    ui.print_columns(
        console,
        [
            ui.enrichment_values_panel(items, country=cc, width=col_w),
            score_panel,
        ],
    )

    try:
        sub = cli_api("GET", f"/v1/intel/enrichment/subcategories?country={cc}")
        sub_items = sub.get("items", [])
        sub_panel = ui.subcategories_panel(sub_items, width=ui.layout_width(console))
        if sub_panel:
            console.print()
            console.print(sub_panel)
    except Exception:
        pass

    sources = ", ".join(data.get("sources", []))
    if sources:
        label = "Fuentes" if not ui.is_en() else "Sources"
        console.print(f"\n[dim]{label}: {sources}[/]")
    ui.print_intel_footer(
        console,
        ["market enrichment --refresh -c PE", "market scores -c PE", "market indicators -c PE"],
    )




def cmd_tools(args):
    """Catálogo MCP agrupado (43 tools) — misma superficie que market-mcp tools/list."""
    if getattr(args, "json", False):
        try:
            from market_core.market_mcp import TOOLS
            console.print(json.dumps({"tools": TOOLS, "total": len(TOOLS)}, indent=2, ensure_ascii=False))
        except ImportError:
            console.print(json.dumps({"error": "market_mcp unavailable"}, indent=2))
        return
    from market_stats import MCP_TOOLS

    ui.print_section_header(
        console,
        "MCP Tools" if ui.is_en() else "Herramientas MCP",
        subtitle=(
            "Grupos para Cursor / Claude / Codex — comando market-mcp"
            if not ui.is_en()
            else "Groups for Cursor / Claude / Codex — run market-mcp"
        ),
        meta=f"{MCP_TOOLS} tools · cli-market.dev/tools",
    )
    ui.print_mcp_tools_catalog(console)
    ui.print_intel_footer(
        console,
        ["market init", "market doctor", "market indicators -c PE"],
    )

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
        tier = ui.fetch_tier()
        ui.tier_gate(console, "alerts_create", tier, json_args=args)
        data = cli_api("POST", "/v1/alerts", {"product": args.product, "threshold_pct": args.threshold, "action": "create"})
        console.print(f"[#3cffd0]✓ Alerta creada para {args.product}[/]")

def cmd_about(args):
    console.print(Panel.fit(
        "[bold #00FF88]CLI Market[/] — Infraestructura de comercio para agentes IA.\n\n"
        f"[#888888]Un solo pip install. Una API. {RETAILERS_VERIFIED} retailers en {MS_COUNTRIES} países. {MCP_TOOLS} MCP tools.[/]\n"
        "[#888888]Comparación de precios cross-border. Data moat con precios reales.[/]\n"
        "[#888888]Open source (MIT). Gratis para developers.[/]\n\n"
        "[dim]github.com/Treevu-ai/cli-market-world[/]",
        border_style="#00FF88"
    ))

def _format_limit(value: int) -> str:
    if value < 0:
        return "unlimited"
    return f"{value:,}"




def cmd_account(args):
    """Dashboard de cuenta: tier, uso, límites y siguiente upgrade."""
    get_token_with_prompt()
    lang = "en" if ui.is_en() else "es"
    with console.status("[cyan]Cargando cuenta..." if lang == "es" else "[cyan]Loading account..."):
        data = cli_api("GET", f"/auth/account?lang={lang}")
    if getattr(args, "json", False):
        ui.emit_json(ui.json_response(True, data), console)
        return
    if isinstance(data, dict) and data.get("error"):
        ui.print_actionable_error(console, data["error"])
        return
    ui.print_account_dashboard(console, data)


def cmd_whoami(args):
    get_token_with_prompt()
    data = cli_api("GET", "/auth/whoami")
    sub_data = cli_api("GET", "/auth/subscription")
    sub = sub_data.get("subscription") or {}
    tier = sub.get("tier", "free")
    username = data.get("username", sub_data.get("username", "?"))
    if getattr(args, "json", False):
        ui.emit_json(ui.json_response(True, {
            "username": username,
            "subscription": sub,
            "api_keys": sub_data.get("api_keys"),
        }), console)
        return
    ui.print_context_bar(console, tier=tier, username=username)
    console.print(f"[#3cffd0]OK {username}[/]  [dim]tier:[/] [bold]{tier}[/]")
    console.print(
        f"[dim]limits:[/] {sub.get('req_limit_day', '?')}/day · "
        f"{sub.get('req_limit_min', '?')}/min · "
        f"alerts: {_format_limit(int(sub.get('alerts', 0) or 0))} · "
        f"checkout: {'yes' if tier in ('pro', 'builder', 'enterprise') else 'no'}"
    )
    if tier == "free":
        console.print("[dim]Dashboard: market account  ·  Upgrade: market upgrade[/]")


def cmd_register(args):
    """Create a free account via POST /auth/register and persist API key locally."""
    with ui.run_with_status(console, "Creando cuenta..." if not ui.is_en() else "Creating account..."):
        data = api("POST", "/auth/register")
    if isinstance(data, dict) and data.get("error"):
        if getattr(args, "json", False):
            ui.json_exit(console, False, error=data["error"], next_commands=ui.error_next_commands(None, data["error"]))
        ui.print_actionable_error(console, data["error"])
        ui.print_hints(console, ui.error_next_commands(None, data["error"]))
        sys.exit(1)
    if getattr(args, "json", False):
        ui.emit_json(ui.json_response(True, data, next_commands=[
            'market search "leche" --country PE', "market whoami", "market doctor",
        ]), console)
        return
    key = data.get("api_key", "")
    console.print(Panel.fit(
        f"[bold #00FF88]Cuenta creada[/]\n\n"
        f"Usuario: [cyan]{data.get('username', '?')}[/]\n"
        f"API key: [bold white]{key}[/]\n\n"
        "[yellow]Guardala ahora — no se vuelve a mostrar.[/]\n\n"
        "Prueba: [cyan]market search \"leche\" --country PE[/]\n"
        "MCP: [cyan]https://cli-market.dev/tools[/]",
        title="CLI Market",
        border_style="#00FF88",
    ))
    ui.print_hints(console, ['market search "leche" --country PE', "market whoami", "market init"])


def cmd_doctor(args):
    """Check API URL, connectivity, auth, tier, MCP, readiness score."""
    import shutil
    import httpx

    checks: list[tuple[str, str, str]] = []
    ok = True
    en = ui.is_en()

    env_url = os.environ.get("MARKET_API_URL")
    checks.append(("API URL", API, "ok" if env_url else "default (production)"))

    with ui.run_with_status(console, "Verificando API..." if not en else "Checking API..."):
        try:
            resp = httpx.get(f"{API}/health/db", timeout=10)
            if resp.status_code == 200:
                snaps = resp.json().get("snapshots", "?")
                checks.append(("API health", f"200 OK - {snaps:,} snapshots", "ok"))
            else:
                checks.append(("API health", f"HTTP {resp.status_code}", "fail"))
                ok = False
        except httpx.ConnectError:
            checks.append(("API health", "connection refused", "fail"))
            ok = False
        except Exception as exc:
            checks.append(("API health", str(exc)[:80], "fail"))
            ok = False

    token = get_token()
    if token:
        who = api("GET", "/auth/whoami")
        if who.get("error"):
            checks.append(("Auth", who["error"], "warn"))
        else:
            checks.append(("Auth", who.get("username", "?"), "ok"))
            sub = api("GET", "/auth/subscription")
            tier = (sub.get("subscription") or {}).get("tier", "?")
            checks.append(("Tier", tier, "ok"))
    else:
        checks.append(("Auth", "no token", "warn"))

    checks.append(("País", ui.get_default_country(), "ok"))
    checks.append(("Countries", str(len(COUNTRIES)), "ok"))
    mcp_bin = shutil.which("market-mcp")
    checks.append(("market-mcp", mcp_bin or "not in PATH", "ok" if mcp_bin else "warn"))
    checks.append(("MCP snippet", "cli-market.dev/tools", "ok"))

    pct, summary = ui.readiness_score(checks)

    if getattr(args, "json", False):
        ui.emit_json(ui.json_response(ok, {
            "readiness_pct": pct,
            "readiness_summary": summary,
            "checks": [{"name": n, "detail": d, "status": s} for n, d, s in checks],
        }, next_commands=["market init", "market register", "market hello"]), console)
        sys.exit(0 if ok else 1)

    table = Table(show_header=True, header_style=f"bold {ui.MINT}", box=ui.table_box(), border_style=ui.TABLE_BORDER)
    table.add_column("Check")
    table.add_column("Detail")
    table.add_column("Status")
    for name, detail, status in checks:
        style = {"ok": "green", "fail": "red", "warn": "yellow"}.get(status, "dim")
        table.add_row(name, detail, f"[{style}]{status}[/]")
    console.print(table)
    console.print(Panel(
        f"[bold #00FF88]{pct}%[/] [dim]readiness[/]\n{summary}",
        title="Readiness" if en else "Preparacion",
        border_style=ui.MINT,
    ))
    if not ok:
        ui.print_hints(console, ["market doctor", "market init"])
        sys.exit(1)
    if not token:
        ui.print_hints(console, ["market register", "market init"])
    else:
        ui.print_hints(console, ['market search "leche" --country PE', "market hello"])

def cmd_lang(args):
    if args.lang_code:
        set_lang(args.lang_code)
        console.print(f"[#3cffd0]Idioma cambiado a {args.lang_code}[/]")
    else:
        current = get_lang()
        console.print(f"[dim]Idioma actual: {current}. Usá market lang en para inglés.[/]")





# ── market hello  -  agent-terminal UI (Antigravity / Codex / Claude style) ─────

_HELLO_ASCII_WORDMARK = (
    "        C L I   -   M A R K E T        ",
)

def _hello_color_art(lines: tuple[str, ...]) -> str:
    return "\n".join(f"[bold #00FF88]{line}[/]" for line in lines)


def _hello_api_host() -> str:
    host = API.replace("https://", "").replace("http://", "").rstrip("/")
    return host[:36] + ("..." if len(host) > 36 else "")


def _hello_wordmark_panel(is_en: bool, width: int) -> Panel:
    subtitle = (
        "A G E N T - N A T I V E   C O M M E R C E   L A Y E R    -    L A T A M"
    )
    tag = (
        "Programmable retail data for AI agents  -  one API  -  zero scraping"
        if is_en
        else "Datos de retail programables para agentes IA  -  una API  -  sin scraping"
    )
    art = _hello_color_art(_HELLO_ASCII_WORDMARK)
    body = f"{art}\n\n[dim]{subtitle}[/]\n[dim italic]{tag}[/]"
    return Panel(
        Align.center(Text.from_markup(body)),
        border_style="#00FF88",
        box=box.DOUBLE_EDGE,
        padding=(1, 1),
        width=width,
    )


def _hello_activation_panel(is_en: bool, width: int) -> Panel:
    if is_en:
        body = (
            "[bold white]Post-install activation[/]\n"
            "[dim]You installed[/] [cyan]cli-market[/][dim]. Run[/] [bold cyan]market init[/] "
            "[dim]for a free API key, readiness check, and MCP snippet.[/]\n"
            "[dim]Or[/] [cyan]market register[/] [dim]if you only need credentials.[/]"
        )
        title = "[bold #00FF88]NEXT STEP[/]"
    else:
        body = (
            "[bold white]Activación post-install[/]\n"
            "[dim]Instalaste[/] [cyan]cli-market[/][dim]. Ejecuta[/] [bold cyan]market init[/] "
            "[dim]para API key gratis, readiness y snippet MCP.[/]\n"
            "[dim]O[/] [cyan]market register[/] [dim]si solo necesitas credenciales.[/]"
        )
        title = "[bold #00FF88]SIGUIENTE PASO[/]"
    return Panel(body, title=title, border_style="#00FF88", box=box.ROUNDED, padding=(1, 2), width=width)


def _hello_status_bar(is_en: bool, width: int) -> Panel:
    label = "EN LINEA" if not is_en else "ONLINE"
    line = (
        f"[dim]v{PACKAGE_VERSION}[/]  [#00FF88]|[/]  "
        f"[dim]API[/]  [bold]{_hello_api_host()}[/]  [#00FF88]|[/]  "
        f"[dim]MCP[/]  [bold #00FF88]{MCP_TOOLS}[/] tools  [#00FF88]|[/]  "
        f"[dim]RETAILERS[/]  [bold #00FF88]{RETAILERS_VERIFIED}[/]  [#00FF88]|[/]  "
        f"[dim]STATUS[/]  [bold #00FF88]{label}[/]"
    )
    return Panel(line, border_style="#00FF88", box=box.HEAVY, padding=(0, 1), width=width)


def _hello_capabilities_panel(is_en: bool, width: int | None = None) -> Panel:
    platforms = (PLATFORM_LIST_EN if is_en else PLATFORM_LIST_ES).replace("·", " - ")
    if is_en:
        body = (
            f"[bold #00FF88]COVERAGE[/]\n"
            f"  {RETAILERS_VERIFIED} verified retailers  -  {MS_COUNTRIES} countries\n"
            f"  {PRICES_VERIFIED_LABEL} prices  -  refresh {PRICES_REFRESH_HOURS}h\n\n"
            f"[bold #00FF88]PLATFORMS[/]\n"
            f"  [dim]{platforms}[/]\n\n"
            f"[bold #00FF88]DATA MOAT[/]\n"
            f"  {INDICATORS_COUNT} indicators  -  kg/L normalized\n"
            f"  Yape/Plin + PayPal  -  MIT open source"
        )
        title = "[bold #00FF88]CAPABILITIES[/]"
    else:
        body = (
            f"[bold #00FF88]COBERTURA[/]\n"
            f"  {RETAILERS_VERIFIED} retailers verificados  -  {MS_COUNTRIES} países\n"
            f"  {PRICES_VERIFIED_LABEL} precios  -  actualización {PRICES_REFRESH_HOURS}h\n\n"
            f"[bold #00FF88]PLATAFORMAS[/]\n"
            f"  [dim]{platforms}[/]\n\n"
            f"[bold #00FF88]DATA MOAT[/]\n"
            f"  {INDICATORS_COUNT} indicadores  -  normalizado kg/L\n"
            f"  Yape/Plin + PayPal  -  código abierto MIT"
        )
        title = "[bold #00FF88]CAPACIDADES[/]"
    return Panel(body, title=title, border_style="#00FF88", box=box.ROUNDED, padding=(1, 2), width=width)


def _hello_quickstart_panel(is_en: bool, width: int | None = None) -> Panel:
    if is_en:
        body = (
            "[bold #00FF88]ONBOARDING[/]\n"
            "  [cyan]0.[/] [cyan]market hello[/]        [dim]you are here[/]\n"
            "  [cyan]1.[/] [cyan]market init[/]         [dim]API + account + MCP[/]\n"
            "  [cyan]2.[/] [cyan]market register[/]     [dim]sk-... shown once[/]\n"
            '  [cyan]3.[/] [cyan]market search "milk" --country PE[/]\n'
            "  [cyan]4.[/] [cyan]market doctor[/]       [dim]readiness %[/]\n\n"
            "[bold #00FF88]DOCS[/]\n"
            "  cli-market.dev/docs#quickstart\n"
            "  cli-market.dev/tools"
        )
        title = "[bold #00FF88]QUICK START[/]"
    else:
        body = (
            "[bold #00FF88]INICIO RÁPIDO[/]\n"
            "  [cyan]0.[/] [cyan]market hello[/]        [dim]estás aquí[/]\n"
            "  [cyan]1.[/] [cyan]market init[/]         [dim]API + cuenta + MCP[/]\n"
            "  [cyan]2.[/] [cyan]market register[/]     [dim]sk-... una sola vez[/]\n"
            '  [cyan]3.[/] [cyan]market search "leche" --country PE[/]\n'
            "  [cyan]4.[/] [cyan]market doctor[/]       [dim]preparacion %[/]\n\n"
            "[bold #00FF88]DOCS[/]\n"
            "  cli-market.dev/docs#quickstart\n"
            "  cli-market.dev/tools"
        )
        title = "[bold #00FF88]INICIO RÁPIDO[/]"
    return Panel(body, title=title, border_style="#00FF88", box=box.ROUNDED, padding=(1, 2), width=width)



def _hello_intermediate_panel(is_en: bool, width: int | None = None) -> Panel:
    if is_en:
        body = (
            "[bold #00FF88]INTERMEDIATE[/]\n"
            '  [cyan]market basket[/] [dim]"milk:2 rice:1" --country PE[/]\n'
            '  [cyan]market compare[/] [dim]"sunflower oil" --country AR[/]\n'
            "  [cyan]market inflation[/] [dim]--country PE[/]\n"
            "  [cyan]market tools[/]            [dim]43 MCP grouped[/]\n"
            "  [cyan]market indicators[/] [dim]--country PE[/]\n"
            "  [cyan]market enrichment[/] [dim]--refresh -c PE[/]\n"
            "  [cyan]market alerts[/] [dim]--action list[/]"
        )
        title = "[bold #00FF88]USE CASES[/]"
    else:
        body = (
            "[bold #00FF88]NIVEL INTERMEDIO[/]\n"
            '  [cyan]market basket[/] [dim]"leche:2 arroz:1" --country PE[/]\n'
            '  [cyan]market compare[/] [dim]"aceite de girasol" --country AR[/]\n'
            "  [cyan]market inflation[/] [dim]--country PE[/]\n"
            "  [cyan]market tools[/]            [dim]43 MCP agrupadas[/]\n"
            "  [cyan]market indicators[/] [dim]--country PE[/]\n"
            "  [cyan]market enrichment[/] [dim]--refresh -c PE[/]\n"
            "  [cyan]market alerts[/] [dim]--action list[/]"
        )
        title = "[bold #00FF88]CASOS DE USO[/]"
    return Panel(body, title=title, border_style="#00FF88", box=box.ROUNDED, padding=(1, 2), width=width)


def _hello_insight_panel(is_en: bool, width: int) -> Panel:
    if is_en:
        hook = "[bold white]Your agent can reason. It still needs verified shelf prices.[/]"
        gartner = (
            "[dim]Gartner (Oct 2025): by 2030, 20% of monetary transactions will be programmable "
            "for AI agents with economic agency  -  agentic traffic becomes structural.[/]"
        )
        title = "[bold #00FF88]INSIGHT[/]"
    else:
        hook = "[bold white]Su agente de IA ya puede razonar; aún requiere precios reales de góndola.[/]"
        gartner = (
            "[dim]Gartner (oct. 2025): hacia 2030, el 20% de las transacciones monetarias serán "
            "programables para agentes de IA; el tráfico agéntico deja de ser marginal.[/]"
        )
        title = "[bold #00FF88]CONTEXTO[/]"
    return Panel(
        f"{hook}\n\n{gartner}",
        title=title,
        border_style="#00FF88",
        box=box.HEAVY_HEAD,
        padding=(1, 2),
        width=width,
    )


def _hello_contact_panel(is_en: bool, width: int) -> Panel:
    if is_en:
        body = (
            "[dim]CLI Market[/]  linkedin.com/company/cli-market   -   x.com/cli_market_dev   -   "
            "instagram.com/cli.market\n\n"
            "[#888888]- Ricardo Cuba[/]  [dim]Founder & Product Owner  -  Sinapsis Innovadora S.A.C.  -  Lima, Peru[/]\n"
            "[dim]linkedin.com/in/ricardo-cuba-alvan   -   hello@cli-market.dev   -   cli-market.dev[/]"
        )
        title = "[dim]CONNECT[/]"
    else:
        body = (
            "[dim]CLI Market[/]  linkedin.com/company/cli-market   -   x.com/cli_market_dev   -   "
            "instagram.com/cli.market\n\n"
            "[#888888]- Ricardo Cuba[/]  [dim]Founder y Product Owner  -  Sinapsis Innovadora S.A.C.  -  Lima, Perú[/]\n"
            "[dim]linkedin.com/in/ricardo-cuba-alvan   -   hello@cli-market.dev   -   cli-market.dev[/]"
        )
        title = "[dim]CONTACTO[/]"
    return Panel(body, title=title, border_style="dim", box=box.ROUNDED, padding=(1, 2), width=width)


def cmd_hello(args):
    """Post-install activation: show next steps after pip install."""
    is_en = get_lang() == "en"
    width = min(max(console.width, 80), 100)
    _report_install_event(source="hello")

    console.print()
    console.print(_hello_wordmark_panel(is_en, width))
    console.print(_hello_activation_panel(is_en, width))
    console.print(_hello_status_bar(is_en, width))
    col_w = max((width - 6) // 2, 36)
    console.print(
        Columns(
            [
                _hello_capabilities_panel(is_en, col_w),
                _hello_quickstart_panel(is_en, col_w),
            ],
            equal=True,
            expand=False,
        )
    )
    console.print(_hello_intermediate_panel(is_en, width))
    console.print(_hello_insight_panel(is_en, width))
    console.print(_hello_contact_panel(is_en, width))
    ui.mcp_snippet_panel(console, width)
    hint = (
        "run market init to begin"
        if is_en
        else "ejecute market init para comenzar"
    )
    console.print(
        f"[bold #00FF88]market>[/] [dim]{hint}[/][bold #00FF88]_[/]"
    )
    console.print()




def cmd_init(args):
    """Full onboarding: API, auth, readiness, MCP snippet."""
    en = ui.is_en()
    steps = [
        "API" if en else "API",
        "Auth" if en else "Cuenta",
        "Readiness" if en else "Preparacion",
        "MCP" if en else "MCP",
    ]
    console.print()
    console.print(Panel(
        f"[bold]{'Zero-to-hero onboarding' if en else 'Onboarding completo'}[/]\n"
        f"[dim]{'Steps' if en else 'Pasos'}:[/] {' -> '.join(steps)}",
        border_style=ui.MINT,
        box=box.DOUBLE_EDGE,
    ))
    with ui.run_with_status(console, steps[0] + "..."):
        import httpx
        try:
            httpx.get(f"{API}/health/db", timeout=10).raise_for_status()
            console.print(f"[{ui.MINT}]OK[/] API")
        except Exception as exc:
            ui.print_actionable_error(console, str(exc))
            sys.exit(1)
    if not get_token():
        console.print(f"[dim]{'Creating free account...' if en else 'Creando cuenta gratuita...'}[/]")
        reg_args = argparse.Namespace(json=getattr(args, "json", False))
        cmd_register(reg_args)
    else:
        console.print(f"[{ui.MINT}]OK[/] Auth (session exists)")
    cmd_doctor(argparse.Namespace(json=False))
    ui.mcp_snippet_panel(console)
    ui.print_hints(console, [
        'market search "leche" --country PE',
        "market shell",
        "market hello",
    ])
    console.print(f"{ui.PROMPT} [dim]{'ready' if en else 'listo'}[/][bold #00FF88]_[/]")


def cmd_shell(args):
    """Interactive REPL — agent-style session."""
    import shlex
    en = ui.is_en()
    tier = ui.fetch_tier()
    ui.print_context_bar(console, tier=tier)
    console.print(Panel(
        "[dim]help[/]  [dim]exit[/]  [dim]search leche --country PE[/]  [dim]whoami[/]  [dim]doctor[/]",
        title="CLI Market Shell" if en else "Sesion CLI Market",
        border_style=ui.MINT,
    ))
    while True:
        try:
            line = console.input(f"{ui.PROMPT} ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print()
            break
        if not line or line.lower() in ("exit", "quit", "q"):
            break
        if line.lower() == "help":
            console.print("[cyan]search QUERY[/]  [cyan]compare QUERY[/]  [cyan]whoami[/]  [cyan]doctor[/]  [cyan]cart[/]  [cyan]hello[/]  [cyan]init[/]")
            continue
        try:
            tokens = shlex.split(line)
        except ValueError as exc:
            console.print(f"[red]{exc}[/]")
            continue
        if not tokens:
            continue
        ns = argparse.Namespace(
            command=tokens[0],
            json=getattr(args, "json", False),
            query="",
            store=None,
            country=None,
            line=None,
            limit=10,
            page=1,
            product_id="",
            name=None,
            price=None,
            qty=1,
            payment="yape",
            order_id=None,
            prompt="",
            code="",
            items=[],
            action="list",
            product=None,
            threshold=5.0,
            email=None,
            resend=False,
            username="",
            password="",
            lang_code=None,
            refresh=False,
        )
        cmd = tokens[0]
        rest = tokens[1:]
        handlers = {
            "search": cmd_search, "compare": cmd_compare, "account": cmd_account,
        "whoami": cmd_whoami,
            "doctor": cmd_doctor, "cart": cmd_cart, "hello": cmd_hello,
            "register": cmd_register, "init": cmd_init, "countries": cmd_countries,
            "lines": cmd_lines, "about": cmd_about,
        }
        if cmd not in handlers:
            console.print(f"[yellow]Unknown: {cmd}[/]")
            continue
        if cmd in ("search", "compare") and rest:
            ns.query = rest[0]
            for i, tok in enumerate(rest):
                if tok in ("--country", "-c") and i + 1 < len(rest):
                    ns.country = rest[i + 1]
        if cmd == "login" and len(rest) >= 2:
            ns.username, ns.password = rest[0], rest[1]
        handlers[cmd](ns)


def cmd_share(args):
    """Generate referral link for growth tracking."""
    import hashlib
    seed = get_token() or "cli-market"
    ref = hashlib.sha256(seed.encode()).hexdigest()[:8]
    url = f"https://cli-market.dev/?ref={ref}"
    if getattr(args, "json", False):
        console.print(json.dumps({"referral_url": url, "ref": ref}, indent=2))
        return
    console.print(Panel.fit(
        f"[bold]Share CLI Market[/]\n\n{url}\n\n"
        "[dim]When developers install via your link, we track activation (opt-in).[/]",
        border_style="#00FF88",
    ))


def cmd_upgrade(args):
    """Upgrade via PayPal subscription (Starter $29 or Pro $79 — auto-activate webhook)."""
    get_token_with_prompt()
    es = get_lang() == "es"
    plan = (getattr(args, "plan", None) or "pro").strip().lower()
    if plan not in ("pro", "starter"):
        plan = "pro"
    manual = getattr(args, "resend", False) and getattr(args, "email", None) and plan == "pro"

    if manual:
        email = (args.email or "").strip()
        payload = {"email": email, "lang": get_lang(), "resend": True}
        data = cli_api("POST", "/billing/request-pro", payload)
        if getattr(args, "json", False):
            ui.emit_json(ui.json_response(True, data), console)
            return
        console.print(Panel.fit(
            f"[bold #00FF88]Pro — fallback manual[/]\n{data.get('message', '')}",
            title="Upgrade",
            border_style="#00FF88",
        ))
        return

    endpoint = "/billing/starter" if plan == "starter" else "/billing/paypal"
    label = "Starter — $29/mo" if plan == "starter" else "Pro — $79/mo"
    with ui.run_with_status(console, "Creando suscripción PayPal..." if es else "Creating PayPal subscription..."):
        data = cli_api("POST", endpoint, {})
    url = data.get("approve_url", "")
    if getattr(args, "json", False):
        ui.emit_json(ui.json_response(True, data, next_commands=["market whoami"]), console)
        return
    console.print(Panel.fit(
        f"[bold #00FF88]CLI Market {label}[/]\n\n"
        f"{data.get('message', '')}\n\n"
        f"[cyan underline]{url}[/]\n\n"
        + (f"[dim]{'Se activa al confirmar en PayPal. Luego: market whoami' if es else 'Activates on PayPal confirm. Then: market whoami'}[/]"),
        title="Upgrade",
        border_style="#00FF88",
    ))
    ui.print_hints(console, ["market whoami", "market doctor"])

# ── Main ────────────────────────────────────────────────────────────────────


def _install_session_id() -> str:
    """Stable anonymous id for CLI funnel events (per machine profile)."""
    sid_file = SESSION_FILE.parent / "funnel_session"
    if sid_file.is_file():
        return sid_file.read_text(encoding="utf-8").strip()
    import uuid

    sid = str(uuid.uuid4())
    sid_file.parent.mkdir(parents=True, exist_ok=True)
    sid_file.write_text(sid, encoding="utf-8")
    return sid


def _report_install_event(*, source: str = "cli") -> bool:
    """Report first CLI activation after pip install (once per machine)."""
    flag = SESSION_FILE.parent / "funnel_install"
    if flag.is_file():
        return False
    try:
        import platform

        api(
            "POST",
            "/v1/events",
            {
                "event": "install",
                "dedupe": True,
                "session_id": _install_session_id(),
                "meta": {
                    "source": source,
                    "cli_version": PACKAGE_VERSION,
                    "platform": platform.system(),
                },
            },
        )
        flag.parent.mkdir(parents=True, exist_ok=True)
        flag.write_text("1", encoding="utf-8")
        return True
    except Exception:
        return False


def main():
    parser = argparse.ArgumentParser(description=t("desc"), usage=t("usage"))
    parser.add_argument("--json", action="store_true", help=t("json_help"))
    sub = parser.add_subparsers(dest="command")

    # login
    p = sub.add_parser("login", help=t("login"))
    p.add_argument("--username", default="", help=t("username"))
    p.add_argument("--password", default="", help=t("password"))

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
    p.add_argument("--payment", choices=["yape", "plin", "tarjeta", "paypal"], default="yape")

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
    sub.add_parser("account", help="Dashboard: tier, uso y upgrade")
    sub.add_parser("whoami", help=t("whoami"))

    # register
    sub.add_parser("register", help=t("register"))

    # doctor
    sub.add_parser("doctor", help=t("doctor"))
    sub.add_parser("init", help=t("init"))
    sub.add_parser("shell", help=t("shell"))

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

    # indicators
    p = sub.add_parser("indicators", help="Catálogo y refresh de indicadores del data moat")
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default=None)
    p.add_argument("--refresh", action="store_true", help="Recalcular indicadores (internal + APIs públicas)")

    # enrichment (data moat signals from public APIs)
    p = sub.add_parser("enrichment", help="Indicadores de enriquecimiento (OFF, Wiki, clima, food CPI)")
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default="PE")
    p.add_argument("--refresh", action="store_true", help="Solo refrescar enriquecimiento (sin recalcular todo el moat)")

    # scores
    p = sub.add_parser("scores", help="Scores compuestos del moat (fairness, stress, aggression)")
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default=None)
    p.add_argument("--line", choices=list(LINES.keys()), default=None)

    # alerts
    p = sub.add_parser("alerts", help="Gestionar alertas de precios")
    p.add_argument("action", nargs="?", default="list", choices=["list", "create"])
    p.add_argument("--product")
    p.add_argument("--threshold", type=float, default=5.0)

    sub.add_parser("tools", help="Catálogo MCP agrupado (43 tools)")
    sub.add_parser("hello", help=t("hello"))
    sub.add_parser("share", help=t("share"))
    p = sub.add_parser("upgrade", help=t("upgrade"))
    p.add_argument("--plan", choices=["pro", "starter"], default="pro", help="Tier: pro (default) or starter")
    p.add_argument("--email", help="Email to receive payment link (manual Pro fallback)")
    p.add_argument("--resend", action="store_true", help="Resend payment link email (manual Pro fallback)")

    args = parser.parse_args()
    ui.set_json_mode(getattr(args, "json", False))
    install_source = "hello" if not getattr(args, "command", None) or args.command == "hello" else "cli"
    _report_install_event(source=install_source)
    ui.maybe_version_notice(console)
    if not args.command:
        cmd_hello(argparse.Namespace(json=getattr(args, "json", False)))
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
        "inflation": cmd_inflation, "indicators": cmd_indicators, "enrichment": cmd_enrichment, "scores": cmd_scores,
        "tools": cmd_tools,
        "alerts": cmd_alerts,
        "about": cmd_about, "whoami": cmd_whoami, "register": cmd_register, "doctor": cmd_doctor, "lang": cmd_lang,
        "hello": cmd_hello, "init": cmd_init, "shell": cmd_shell, "share": cmd_share, "upgrade": cmd_upgrade,
    }
    handler = handlers.get(args.command)
    if handler:
        handler(args)

if __name__ == "__main__":
    main()
