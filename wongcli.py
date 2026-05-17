#!/usr/bin/env python3
"""
wongcli — Buscador de productos de supermercados peruanos desde la terminal.

Usa la API pública de VTEX de Wong, Metro y Plaza Vea para buscar productos
y comparar precios entre las tres cadenas.

Uso:
    python wongcli.py "leche"                     # compara las 3 tiendas
    python wongcli.py "leche" --tienda wong       # solo Wong
    python wongcli.py "leche" --tienda metro      # solo Metro
    python wongcli.py "leche" --tienda plazavea   # solo Plaza Vea
    python wongcli.py "aceite" --limit 10 --orden precio-asc
    python wongcli.py "café" --url
"""

import argparse
import asyncio
import re
import sys
from dataclasses import dataclass, field
from typing import Any

import httpx
from rich.console import Console
from rich.table import Table

# ── Configuración ──────────────────────────────────────────────────────────

STORES = {
    "wong": {
        "name": "Wong",
        "base": "https://www.wong.pe",
        "color": "cyan",
    },
    "metro": {
        "name": "Metro",
        "base": "https://www.metro.pe",
        "color": "magenta",
    },
    "plazavea": {
        "name": "Plaza Vea",
        "base": "https://www.plazavea.com.pe",
        "color": "yellow",
    },
}

DEFAULT_STORES = list(STORES.keys())
PAGE_SIZE = 20
MAX_RESULTS = 100
REQUEST_HEADERS = {"Accept": "application/json"}

console = Console()


# ── Modelo de producto ─────────────────────────────────────────────────────

@dataclass
class Product:
    name: str
    brand: str
    price: float
    list_price: float
    link_text: str
    product_ref: str
    store: str

    @property
    def discount(self) -> int | None:
        if self.list_price > self.price > 0:
            return round((1 - self.price / self.list_price) * 100)
        return None

    @property
    def url(self) -> str:
        base = STORES[self.store]["base"]
        return f"{base}/{self.link_text}/p"

    @property
    def display_name(self) -> str:
        return self.name.replace("-", " ")


@dataclass
class MatchPair:
    """Un producto matcheado entre múltiples tiendas."""
    products: dict[str, Product | None] = field(default_factory=dict)

    @property
    def name(self) -> str:
        for p in self.products.values():
            if p:
                return p.display_name
        return "?"

    @property
    def brand(self) -> str:
        for p in self.products.values():
            if p:
                return p.brand
        return "?"

    @property
    def best_store(self) -> str | None:
        best: str | None = None
        best_price = float("inf")
        for store, p in self.products.items():
            if p and 0 < p.price < best_price:
                best_price = p.price
                best = store
        return best

    @property
    def price_range(self) -> tuple[float, float]:
        prices = [p.price for p in self.products.values() if p and p.price > 0]
        if not prices:
            return (0, 0)
        return (min(prices), max(prices))

    @property
    def savings(self) -> float | None:
        lo, hi = self.price_range
        if hi > lo > 0:
            return hi - lo
        return None

    def present_in(self) -> list[str]:
        return [s for s, p in self.products.items() if p is not None]


# ── Helpers ─────────────────────────────────────────────────────────────────

def parse_price(price: Any) -> float:
    try:
        return float(price or 0)
    except (ValueError, TypeError):
        return 0.0


def fmt_price(price: float) -> str:
    return f"S/ {price:,.2f}"


def fmt_discount(discount: int) -> str:
    if discount >= 30:
        return f"[bold green]{discount}%[/]"
    if discount >= 15:
        return f"[green]{discount}%[/]"
    return f"[yellow]{discount}%[/]"


def clean_for_match(text: str) -> str:
    """Normaliza un nombre para matching: lowercase, sin unidades ni puntuación."""
    text = text.lower()
    text = re.sub(r"\b\d+\s*(g|gr|kg|ml|l|lt|un|und|unidad|unidades|pack|sixpack)\b", "", text)
    text = re.sub(r"[^a-záéíóúñ0-9\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def product_from_json(p: dict, store: str) -> Product:
    items = p.get("items", [])
    item = items[0] if items else {}
    sellers = item.get("sellers", [])
    seller = sellers[0] if sellers else {}
    offer = seller.get("commertialOffer", {})

    return Product(
        name=p.get("productName", ""),
        brand=p.get("brand") or "—",
        price=parse_price(offer.get("Price")),
        list_price=parse_price(offer.get("ListPrice")),
        link_text=p.get("linkText", ""),
        product_ref=p.get("productReference", ""),
        store=store,
    )


# ── API ─────────────────────────────────────────────────────────────────────

async def fetch_store(store: str, term: str, page: int, limit: int) -> list[dict]:
    """Busca productos en una tienda VTEX."""
    base = STORES[store]["base"]
    url = f"{base}/api/catalog_system/pub/products/search/{term}"
    _from = (page - 1) * PAGE_SIZE
    _to = min(_from + limit - 1, _from + PAGE_SIZE - 1)

    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(
            url,
            params={"_from": str(_from), "_to": str(_to)},
            headers=REQUEST_HEADERS,
        )
        resp.raise_for_status()
        return resp.json()


# ── Lógica de comparación ──────────────────────────────────────────────────

def match_products(all_products: dict[str, list[Product]]) -> list[MatchPair]:
    """Empareja productos de múltiples tiendas por referencia y nombre.

    1. Agrupar por productReference (mismo SKU entre tiendas del mismo grupo).
    2. Agrupar por marca + nombre normalizado (mismo producto entre grupos).
    3. Los productos sin pareja quedan solos en su fila.
    """
    store_keys = list(all_products.keys())

    # Índice global por productReference
    ref_index: dict[str, dict[str, Product]] = {}
    for store in store_keys:
        for p in all_products[store]:
            if p.product_ref:
                ref_index.setdefault(p.product_ref, {})[store] = p

    # Índice global por clave normalizada
    key_index: dict[str, dict[str, Product]] = {}
    for store in store_keys:
        for p in all_products[store]:
            key = f"{p.brand.lower()} | {clean_for_match(p.name)}"
            key_index.setdefault(key, {})[store] = p

    # Merge: si un producto está en ref_index, usar esa entrada
    used_keys: set[str] = set()
    pairs: list[MatchPair] = []

    for ref, store_prods in ref_index.items():
        found_key = None
        for store, p in store_prods.items():
            key = f"{p.brand.lower()} | {clean_for_match(p.name)}"
            if key in key_index:
                found_key = key
                break
        if found_key:
            used_keys.add(found_key)
            pairs.append(MatchPair(products=dict(key_index[found_key])))
        else:
            pairs.append(MatchPair(products=dict(store_prods)))

    for key, store_prods in key_index.items():
        if key not in used_keys:
            pairs.append(MatchPair(products=dict(store_prods)))

    return pairs


# ── Tablas ──────────────────────────────────────────────────────────────────

def build_single_table(products: list[Product], store: str, term: str, show_url: bool) -> Table:
    """Tabla para una sola tienda."""
    store_info = STORES[store]
    table = Table(
        title=f'[bold white]Resultados para "[bold cyan]{term}[/]" en [bold {store_info["color"]}]{store_info["name"]}[/][/]',
        title_style="bold white",
        header_style=f"bold {store_info['color']}",
        border_style="dim blue",
        show_lines=False,
    )

    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Producto", style="white", max_width=42, no_wrap=False)
    table.add_column("Marca", style="blue", max_width=16)
    table.add_column("Precio", style="bold yellow", justify="right")
    table.add_column("P. Lista", style="dim", justify="right")
    table.add_column("Desc.", justify="center", width=8)
    if show_url:
        table.add_column("Link", style="dim", max_width=50, no_wrap=True)

    for i, p in enumerate(products, 1):
        price_str = fmt_price(p.price)
        list_str = fmt_price(p.list_price) if p.list_price != p.price else "—"
        disc = p.discount
        if disc:
            price_str = f"[bold yellow]{price_str}[/]"
            disc_str = fmt_discount(disc)
        else:
            disc_str = "—"

        row = [str(i), p.display_name, p.brand, price_str, list_str, disc_str]
        if show_url:
            row.append(p.url)
        table.add_row(*row)

    return table


def build_comparison_table(
    pairs: list[MatchPair],
    store_keys: list[str],
    term: str,
) -> Table:
    """Tabla comparativa con una columna de precio por tienda."""
    store_colors = {k: STORES[k]["color"] for k in store_keys}
    store_labels = [f"[bold {store_colors[k]}]{STORES[k]['name']}[/]" for k in store_keys]
    title = f'[bold white]Comparativa para "[bold cyan]{term}[/]" — {" vs ".join(store_labels)}[/]'

    table = Table(
        title=title,
        title_style="bold white",
        header_style="bold white",
        border_style="dim blue",
        show_lines=False,
    )

    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Producto", style="white", max_width=34, no_wrap=False)
    table.add_column("Marca", style="blue", max_width=12)
    price_width = 11
    for store in store_keys:
        table.add_column(STORES[store]["name"], justify="right", width=price_width)
    table.add_column("Mejor", justify="center", width=10)
    table.add_column("Ahorro", justify="right", width=10)

    for i, pair in enumerate(pairs, 1):
        row = [str(i), pair.name, pair.brand]
        for store in store_keys:
            p = pair.products.get(store)
            color = store_colors[store]
            row.append(f"[{color}]{fmt_price(p.price)}[/]" if p else "[dim]—[/]")

        best = pair.best_store
        if best:
            row.append(f"[bold {store_colors[best]}]{STORES[best]['name']}[/]")
        else:
            row.append("[dim]—[/]")

        savings = pair.savings
        row.append(f"[bold green]S/ {savings:,.2f}[/]" if savings else "—")

        table.add_row(*row)

    return table


# ── Ordenamiento ────────────────────────────────────────────────────────────

def sort_products(products: list[Product], order: str) -> list[Product]:
    reverse = order == "precio-desc"
    return sorted(products, key=lambda p: p.price if p.price > 0 else float("inf"), reverse=reverse)


def sort_pairs(pairs: list[MatchPair], order: str) -> list[MatchPair]:
    reverse = order == "precio-desc"

    def best_price(pair: MatchPair) -> float:
        prices = [p.price for p in pair.products.values() if p and p.price > 0]
        return min(prices) if prices else float("inf")

    return sorted(pairs, key=best_price, reverse=reverse)


# ── Main ────────────────────────────────────────────────────────────────────

async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Busca productos en supermercados peruanos desde la terminal.",
        usage="python wongcli.py TÉRMINO [opciones]",
    )
    parser.add_argument("termino", help="Término de búsqueda (ej: 'leche', 'arroz')")
    parser.add_argument("--limit", "-l", type=int, default=PAGE_SIZE,
                        help=f"Resultados máx (default: {PAGE_SIZE}, max: {MAX_RESULTS})")
    parser.add_argument("--pagina", "-p", type=int, default=1,
                        help="Número de página (default: 1)")
    parser.add_argument("--orden", "-o", choices=["precio-asc", "precio-desc"], default=None,
                        help="Ordenar por precio")
    parser.add_argument("--url", action="store_true",
                        help="Mostrar enlace del producto")
    parser.add_argument("--tienda", "-t", choices=list(STORES.keys()), default=None,
                        help="Buscar solo en una tienda (default: todas)")

    args = parser.parse_args()
    limit = min(args.limit, MAX_RESULTS)
    order = args.orden
    active_stores = [args.tienda] if args.tienda else DEFAULT_STORES

    # ── Modo tienda única ───────────────────────────────────────────────
    if len(active_stores) == 1:
        store = active_stores[0]
        store_name = STORES[store]["name"]
        with console.status(f"[cyan]Buscando [bold]'{args.termino}'[/] en {store_name}..."):
            try:
                raw = await fetch_store(store, args.termino, args.pagina, limit)
            except httpx.HTTPStatusError as e:
                console.print(f"[red]Error HTTP en {store_name}: {e.response.status_code}[/]")
                sys.exit(1)
            except httpx.RequestError as e:
                console.print(f"[red]Error de conexión con {store_name}: {e}[/]")
                sys.exit(1)

        products = [product_from_json(p, store) for p in raw]

        if not products:
            console.print(f"\n[yellow]No se encontraron productos para [bold]'{args.termino}'[/] en {store_name}.[/]")
            return

        if order:
            products = sort_products(products, order)

        table = build_single_table(products, store, args.termino, show_url=args.url)
        console.print()
        console.print(table)
        console.print(f"\n[dim]Mostrando {len(products)} producto(s) en {store_name}[/]")
        return

    # ── Modo comparación (múltiples tiendas) ────────────────────────────
    store_names = ", ".join(STORES[s]["name"] for s in active_stores)
    with console.status(f"[cyan]Buscando [bold]'{args.termino}'[/] en {store_names}..."):
        try:
            all_raw = {s: await fetch_store(s, args.termino, args.pagina, limit) for s in active_stores}
        except httpx.HTTPStatusError as e:
            console.print(f"[red]Error HTTP: {e.response.status_code}[/]")
            sys.exit(1)
        except httpx.RequestError as e:
            console.print(f"[red]Error de conexión: {e}[/]")
            sys.exit(1)

    all_products: dict[str, list[Product]] = {
        store: [product_from_json(p, store) for p in raw]
        for store, raw in all_raw.items()
    }

    pairs = match_products(all_products)

    if not pairs:
        console.print(f"\n[yellow]No se encontraron productos para [bold]'{args.termino}'[/] en ninguna tienda.[/]")
        return

    if order:
        pairs = sort_pairs(pairs, order)

    table = build_comparison_table(pairs, active_stores, args.termino)
    console.print()
    console.print(table)

    # Resumen
    parts = []
    matched_all = sum(1 for p in pairs if all(p.products.get(s) for s in active_stores))
    parts.append(f"[bold]{matched_all} en todas[/]")
    for store in active_stores:
        count = sum(1 for p in pairs if p.products.get(store))
        color = STORES[store]["color"]
        parts.append(f"[{color}]{count} en {STORES[store]['name']}[/]")
    console.print(f"\n[dim]{len(pairs)} producto(s) — {' · '.join(parts)}[/]")


if __name__ == "__main__":
    asyncio.run(main())
