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

API = "http://127.0.0.1:8765"
SESSION_FILE = Path.home() / ".market" / "session.json"
console = Console()

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

WELCOME_BANNER = """[#3cffd0]
 ██████╗██╗     ██╗     █████╗  ██████╗ ███████╗███╗   ██╗████████╗██╗ ██████╗
██╔════╝██║     ██║    ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██║██╔════╝
██║     ██║     ██║    ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   ██║██║
██║     ██║     ██║    ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ██║██║
╚██████╗███████╗██║    ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ██║╚██████╗
 ╚═════╝╚══════╝╚═╝    ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝ ╚═════╝
 ███╗   ███╗ █████╗ ██████╗ ██╗  ██╗███████╗████████╗
 ████╗ ████║██╔══██╗██╔══██╗██║ ██╔╝██╔════╝╚══██╔══╝
 ██╔████╔██║███████║██████╔╝█████╔╝ █████╗     ██║
 ██║╚██╔╝██║██╔══██║██╔══██╗██╔═██╗ ██╔══╝     ██║
 ██║ ╚═╝ ██║██║  ██║██║  ██║██║  ██╗███████╗   ██║
 ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝[/]
[bold #3cffd0]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CLI Market LATAM · v1.0
Infrastructure layer — supermarkets as programmable commerce
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]
[#3cffd0]Stripe transformó pagos en APIs.
Nosotros transformamos supermercados en APIs para agentes IA.[/]

[dim]Human-friendly[/] [#3cffd0]▸[/] [dim]Terminal CLI · Comandos · Tablas · Flujo de compra[/]
[dim]Agent-friendly [/] [#3cffd0]▸[/] [dim]REST API · MCP Tools · JSON · Agentes autónomos[/]

[bold #3cffd0]COMANDOS[/]
  [#3cffd0]market login[/]              Autenticarse
  [#3cffd0]market search[/] [dim]"leche"[/]        Buscar en Wong, Metro y Plaza Vea
  [#3cffd0]market compare[/] [dim]"aceite"[/]      Comparar precios entre tiendas
  [#3cffd0]market add[/] [dim]<id> --qty 2[/]      Agregar al carrito
  [#3cffd0]market cart[/]               Ver carrito y total
  [#3cffd0]market checkout[/]           Finalizar compra
  [#3cffd0]market ask[/] [dim]"compra arroz"[/]    Lenguaje natural → acción
  [#3cffd0]market preferences[/]        Perfil de compra inferido
  [#3cffd0]market about[/]              Modelo de negocio
  [#3cffd0]market --json[/]             Modo agente (machine-readable)

[dim]Backend:[/] [#3cffd0]market-server[/] [dim]· MCP:[/] [#3cffd0]python market_mcp.py[/]
"""

BUSINESS_MODEL_BANNER = """[bold #3cffd0]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CLI Market LATAM · MODELO DE NEGOCIO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/]

[bold]Posicionamiento[/]
Infrastructure layer that transforms traditional LATAM
supermarkets into AI-agent compatible commerce systems.

[bold #3cffd0]▸ Problema[/]
  · E-commerce tradicional optimizado para clicks, no agentes
  · Retailers no preparados para comercio autónomo
  · No existe capa agentic estandarizada en LATAM
  · APIs de supermercados fragmentadas o inexistentes

[bold #3cffd0]▸ Solución[/]
  Agent Layer · MCP compatible · Búsqueda semántica
  Checkout autónomo · Multi-retailer (Wong, Metro, Plaza Vea)

[bold #3cffd0]▸ Mercado objetivo[/]
  Primario:   Supermercados · Retail · Dark stores · Farmacias
  Secundario: AI startups · Asistentes voz · Fintechs · Smart home

[bold #3cffd0]▸ Modelo de ingresos[/]
  SaaS B2B:     Starter $499/mes · Growth $1,999/mes · Enterprise
  API usage:    Cobro por request, checkout, acción de agente
  Transacción:  1-5% por orden completada
  White-label:  Infraestructura bajo marca del retailer

[bold #3cffd0]▸ Moat estratégico[/]
  Primera capa agentic de supermercados en LATAM
  MCP nativo · Inteligencia semántica · Interoperabilidad retail

[bold #3cffd0]▸ Expansión[/]
  Fase 1: Perú · Chile · Colombia
  Fase 2: México · Brasil · Argentina

[dim]market --json about[/] [dim]para versión machine-readable[/]
"""


# ── Helpers ─────────────────────────────────────────────────────────────────

def get_token() -> str:
    if not SESSION_FILE.exists():
        console.print("[red]No autenticado. Ejecutá: market login[/]")
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
        else:
            raise ValueError(f"Unknown method: {method}")
        if resp.status_code >= 400:
            detail = resp.json().get("detail", resp.text)
            console.print(f"[red]Error: {detail}[/]")
            sys.exit(1)
        return resp.json()
    except httpx.ConnectError:
        console.print("[red]Error: No se pudo conectar al servidor. Ejecutá primero: python market_server.py[/]")
        sys.exit(1)


def fmt_price(price: float) -> str:
    return f"S/ {price:,.2f}"


def store_color(store: str) -> str:
    colors = {"wong": "#3cffd0", "metro": "#5200ff", "plazavea": "#ffe600"}
    return colors.get(store, "#e9e9e9")


def store_emoji(store: str) -> str:
    emojis = {"wong": "🛒", "metro": "🏪", "plazavea": "🏬"}
    return emojis.get(store, "📦")


# ── Comandos ───────────────────────────────────────────────────────────────

def cmd_login(args):
    """Autentica al usuario contra el servidor."""
    data = api("POST", "/auth/login", {"username": args.username, "password": args.password})
    console.print(f"[#3cffd0]✓ Autenticado como [bold]{data['username']}[/][/]")
    console.print(f"[dim]Token guardado en {SESSION_FILE}[/]")


def cmd_search(args):
    """Busca productos. Soporta --country para filtrar por país."""
    stores_to_search = [args.store] if args.store else None
    if args.country and not args.store:
        country_stores = [k for k, v in STORES.items() if v["country"] == args.country]
        stores_to_search = country_stores

    label = args.store or args.country or "todas"
    with console.status(f"[cyan]Buscando '{args.query}' en {label}..."):
        data = api("POST", "/products/search", {
            "query": args.query,
            "store": args.store,
            "limit": args.limit,
        })
        # Filter by country on client side if needed
        if args.country and not args.store:
            data["results"] = [p for p in data["results"] if p["store"] in stores_to_search]
            data["total"] = len(data["results"])

    results = data["results"]
    if not results:
        console.print(f"\n[yellow]Sin resultados para '{args.query}'[/]")
        return

    table = Table(
        title=f'[bold white]"{args.query}" — {len(results)} resultados[/]',
        border_style="dim blue",
        show_lines=False,
    )
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Producto", style="white", max_width=38, no_wrap=False)
    table.add_column("Marca", style="blue", max_width=14)
    table.add_column("Tienda", max_width=10)
    table.add_column("Precio", style="bold yellow", justify="right")
    table.add_column("Desc.", justify="center", width=7)
    table.add_column("ID", style="dim", max_width=20)

    for i, p in enumerate(results, 1):
        color = store_color(p["store"])
        disc = p.get("discount")
        price_str = fmt_price(p["price"])
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
            p["id"],
        )

    console.print()
    console.print(table)
    console.print(f"\n[dim]Para agregar al carrito: market add <ID> [--store {list(STORES.keys())[0]}] [--name \"...\"] [--price ...][/]")


def cmd_compare(args):
    """Compara precios entre las 3 tiendas."""
    with console.status(f"[cyan]Comparando '{args.query}'..."):
        data = api("POST", "/products/compare", {"query": args.query, "limit": args.limit})

    comp = data["comparison"]
    if not comp:
        console.print(f"\n[yellow]Sin resultados para '{args.query}'[/]")
        return

    table = Table(
        title=f'[bold white]Comparativa: "{args.query}"[/]',
        border_style="dim blue",
    )
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Producto", style="white", max_width=34, no_wrap=False)
    table.add_column("Marca", style="blue", max_width=12)
    table.add_column("Wong", justify="right", width=11)
    table.add_column("Metro", justify="right", width=11)
    table.add_column("P. Vea", justify="right", width=11)
    table.add_column("Mejor", justify="center", width=10)

    for i, item in enumerate(comp, 1):
        prices = item["prices"]
        best = item["best_store"]
        best_color = store_color(best) if best else "dim"

        def pcell(store_key):
            if store_key in prices:
                return f"[{store_color(store_key)}]{fmt_price(prices[store_key])}[/]"
            return "[dim]—[/]"

        table.add_row(
            str(i),
            item["name"],
            item["brand"],
            pcell("wong"),
            pcell("metro"),
            pcell("plazavea"),
            f"[bold {best_color}]{STORES[best]['name']}[/]" if best else "—",
        )

    console.print()
    console.print(table)


def cmd_add(args):
    """Agrega un producto al carrito."""
    data = api("POST", "/cart/add", {
        "product_id": args.product_id,
        "name": args.name or args.product_id,
        "price": args.price,
        "store": args.store or "wong",
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
    """Historial de órdenes."""
    data = api("GET", "/orders")
    orders = data["orders"]
    if not orders:
        console.print("[yellow]Sin órdenes previas[/]")
        return

    table = Table(title="[bold white]Historial de órdenes[/]", border_style="dim blue")
    table.add_column("Orden", style="bold", width=10)
    table.add_column("Fecha", style="dim", width=12)
    table.add_column("Items", justify="center", width=6)
    table.add_column("Total", style="bold yellow", justify="right")
    table.add_column("Pago", width=10)

    for o in reversed(orders):
        date = o["created_at"][:10] if "created_at" in o else "?"
        table.add_row(
            o["order_id"],
            date,
            str(len(o["items"])),
            fmt_price(o["total"]),
            o.get("payment_method", "?"),
        )

    console.print()
    console.print(table)
    console.print(f"\n[dim]{len(orders)} órdenes — market reorder para repetir la última[/]")


def cmd_reorder(args):
    """Repite la última orden."""
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
    "wong":      {"name": "Wong",       "country": "PE", "currency": "PEN", "emoji": "🇵🇪"},
    "metro":     {"name": "Metro",      "country": "PE", "currency": "PEN", "emoji": "🇵🇪"},
    "plazavea":  {"name": "Plaza Vea",  "country": "PE", "currency": "PEN", "emoji": "🇵🇪"},
    "carrefour": {"name": "Carrefour",  "country": "AR", "currency": "ARS", "emoji": "🇦🇷"},
    "jumbo_ar":  {"name": "Jumbo",      "country": "AR", "currency": "ARS", "emoji": "🇦🇷"},
    "carrefour_br": {"name": "Carrefour", "country": "BR", "currency": "BRL", "emoji": "🇧🇷"},
    "chedraui":  {"name": "Chedraui",   "country": "MX", "currency": "MXN", "emoji": "🇲🇽"},
    "heb":       {"name": "HEB",        "country": "MX", "currency": "MXN", "emoji": "🇲🇽"},
    "olimpica":  {"name": "Olímpica",   "country": "CO", "currency": "COP", "emoji": "🇨🇴"},
}

COUNTRIES = {
    "PE": "Perú",
    "AR": "Argentina",
    "BR": "Brasil",
    "MX": "México",
    "CO": "Colombia",
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
    p.add_argument("--limit", "-l", type=int, default=10)

    # compare
    p = sub.add_parser("compare", help="Comparar precios entre tiendas")
    p.add_argument("query", nargs="?", default="")
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default=None)
    p.add_argument("--limit", "-l", type=int, default=10)

    # add
    p = sub.add_parser("add", help="Agregar al carrito")
    p.add_argument("product_id", help="ID del producto")
    p.add_argument("--name", help="Nombre del producto")
    p.add_argument("--price", type=float, required=True, help="Precio del producto")
    p.add_argument("--store", "-s", choices=list(STORES.keys()), default="wong")
    p.add_argument("--qty", type=int, default=1)

    # cart
    sub.add_parser("cart", help="Ver carrito")

    # checkout
    p = sub.add_parser("checkout", help="Finalizar compra")
    p.add_argument("--payment", choices=["yape", "plin", "tarjeta"], default="yape")

    # orders
    sub.add_parser("orders", help="Historial de órdenes")

    # reorder
    sub.add_parser("reorder", help="Repetir última orden")

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

    # about
    sub.add_parser("about", help="Modelo de negocio")

    # whoami
    sub.add_parser("whoami", help="Ver sesión activa")

    parser.add_argument("--json", action="store_true", help="Salida machine-readable para agentes IA")

    args = parser.parse_args()

    if args.command is None:
        if args.json:
            import json as _json
            console.print(_json.dumps(BUSINESS_MODEL_JSON, indent=2, ensure_ascii=False))
        else:
            console.print(WELCOME_BANNER)
            console.print("\n[dim]market login[/] [dim]para empezar ·[/] [#3cffd0]market --json[/] [dim]para agentes ·[/] [#3cffd0]market about[/] [dim]para el pitch[/]")
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
        "checkout": cmd_checkout,
        "orders":   cmd_orders,
        "reorder":  cmd_reorder,
        "ask":      cmd_ask,
        "preferences": cmd_preferences,
        "countries": cmd_countries,
        "categories": cmd_categories,
        "barcode":  cmd_barcode,
        "enrich":   cmd_enrich,
        "about":    lambda a: console.print(BUSINESS_MODEL_BANNER),
        "whoami":   cmd_whoami,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
