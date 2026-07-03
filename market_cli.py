#!/usr/bin/env python3
"""
market — Commerce CLI.

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
import html
import json
import os
import re
import sys

from rich.console import Console
from rich.panel import Panel
from rich import box
from rich.table import Table

from market_core import (
    STORES, LINES, COUNTRIES, SESSION_FILE, get_token, get_session_username, api, API,
    fmt_price, store_color, save_last_search, load_last_search,
)
from market_core.market_food_match import matches_food_basket_query
import market_ui as ui
from market_stats import (
    COUNTRIES as MS_COUNTRIES, RETAILERS_VERIFIED, PACKAGE_VERSION,
)
from market_cli_i18n import get_lang, set_lang, t, _LEGACY_INTEL_CMDS, _META_CMDS
from market_cli_telemetry import (
    _report_install_event,
    _report_onboarding_event,
    report_command_attempted,
    report_command_result,
    report_auth_wall_hit,
    command_timer,
)
from market_cli_hello import cmd_hello, _render_splash, _mcp_profile_counts

_NO_COLOR = bool(os.environ.get("NO_COLOR", ""))
console = Console(no_color=_NO_COLOR)

_ = lambda x: x

# ── Canasta básica (default when `market` is run without arguments) ──────────

CANASTA_BASICA = ["arroz", "leche", "aceite", "pan", "huevos", "azúcar", "pollo", "papa", "cebolla"]



def _read_nag_count() -> int:
    try:
        return int((SESSION_FILE.parent / ".nag_count").read_text().strip())
    except Exception:
        return 0


def _write_nag_count(n: int) -> None:
    try:
        (SESSION_FILE.parent / ".nag_count").write_text(str(n))
    except Exception:
        pass

_INTEL_SUBCMDS_WITH_COUNTRY = {"brief", "inflation", "scores", "enrichment", "indicators"}


def _rewrite_positional_country(argv: list[str]) -> list[str]:
    """Accept `market intel brief uy` as shorthand for `--country UY`.

    Only rewrites a single bare positional token that (a) immediately follows
    an intel subcommand accepting --country, (b) isn't already flagged with
    -c/--country, and (c) matches a known country code case-insensitively.
    """
    idx = None
    if len(argv) >= 3 and argv[1] == "intel" and argv[2] in _INTEL_SUBCMDS_WITH_COUNTRY:
        idx = 3
    elif len(argv) >= 2 and argv[1] in _INTEL_SUBCMDS_WITH_COUNTRY:
        idx = 2
    if idx is None or len(argv) <= idx:
        return argv

    rest = argv[idx:]
    if any(a in ("-c", "--country") for a in rest):
        return argv
    candidate = rest[0]
    if candidate.startswith("-"):
        return argv
    if candidate.upper() not in COUNTRIES:
        return argv
    return [*argv[:idx], "--country", candidate.upper(), *rest[1:]]


def _normalize_market_argv(argv: list[str]) -> list[str]:
    """Map legacy top-level commands without cluttering --help."""
    if len(argv) < 2:
        return argv
    cmd = argv[1]
    if cmd in _LEGACY_INTEL_CMDS:
        argv = [argv[0], "intel", cmd, *argv[2:]]
    return _rewrite_positional_country(argv)


def _strip_json_flag(argv: list[str]) -> tuple[list[str], bool]:
    """Pull --json out of argv regardless of position and report whether it
    was present.

    --json is documented as a global flag, but argparse only recognizes an
    optional registered on the top-level parser when it appears BEFORE the
    subcommand token — placed after subcommand-specific args (e.g. "market
    search leche --country AR --json", the natural place an agent would put
    it) it hits "unrecognized arguments: --json" since individual
    subparsers never redeclared it (cli-market-backend#127 --json
    global-flag finding, S9).
    """
    if "--json" not in argv[1:]:
        return argv, False
    return [argv[0]] + [a for a in argv[1:] if a != "--json"], True


def _attach_intel_parsers(parent, helps: dict[str, str]) -> None:
    """Register intelligence CLI commands on *parent* (market intel * or hidden legacy)."""
    p = parent.add_parser("brief", help=helps.get("brief", "Executive intel brief"))
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default=None)
    p.add_argument("--line", choices=list(LINES.keys()), default=None)
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--catalog", action="store_true", help="Incluir catálogo completo de indicadores")

    p = parent.add_parser("inflation", help=helps["inflation"])
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default=None)
    p.add_argument("--line", choices=list(LINES.keys()), default=None)
    p.add_argument("--days", type=int, default=7, help="Ventana de análisis en días (default 7)")

    p = parent.add_parser("indicators", help=helps["indicators"])
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default=None)
    p.add_argument("--refresh", action="store_true", help=argparse.SUPPRESS)

    p = parent.add_parser("enrichment", help=helps["enrichment"])
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default="PE")
    p.add_argument("--refresh", action="store_true", help=argparse.SUPPRESS)

    p = parent.add_parser("scores", help=helps["scores"])
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default=None)
    p.add_argument("--line", choices=list(LINES.keys()), default=None)

# ── Welcome banner ───────────────────────────────────────────────────────────

WELCOME_BANNER = """\n[#00FF88]  ╭───────────────────────────────────────────────────────────────╮
  │                                                               │
     [#FFFFFF bold] C L I   M A R K E T[/]
     [#888888]infraestructura de comercio para humanos y agentes ia[/]

     [#00FF88]>[/] 30 retailers    [#00FF88]>[/] 8 países       [#00FF88]>[/] API + CLI
     [#00FF88]>[/] cross-border       [#00FF88]>[/] autónomo         [#00FF88]>[/] listo para integrar

     [#555555]pip install cli-market-world[/]
     [#555555]cli-market.dev[/]

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

     [#00FF88]>[/] 30 retailers    [#00FF88]>[/] 8 countries    [#00FF88]>[/] API + CLI
     [#00FF88]>[/] cross-border       [#00FF88]>[/] autonomous       [#00FF88]>[/] integration-ready

     [#555555]pip install cli-market-world[/]
     [#555555]cli-market.dev[/]

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
        f"[#00FF88]>[/] API + CLI"
    )
    if is_en:
        body = WELCOME_BANNER_EN.replace(
            "[#00FF88]>[/] 30 retailers    [#00FF88]>[/] 8 countries    [#00FF88]>[/] API + CLI",
            stats,
        ).replace(
            "[#00FF88]market login[/]        [#888888]authenticate[/]",
            "[#00FF88]market register[/]     [#888888]free API key[/]\n"
            "     [#00FF88]market login[/]        [#888888]existing account[/]",
        )
    else:
        body = WELCOME_BANNER.replace(
            "[#00FF88]>[/] 30 retailers    [#00FF88]>[/] 8 países       [#00FF88]>[/] API + CLI",
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

_ACTIVATION_QUERIES = {
    "PE": "leche",
    "AR": "leche",
    "MX": "leche",
    "CO": "leche",
    "CL": "leche",
    "ES": "leche",
    "US": "milk",
    "BR": "leite",
}


def _activation_query(country: str) -> str:
    return _ACTIVATION_QUERIES.get((country or "PE").upper(), "leche")


def _activation_search_done() -> bool:
    return (SESSION_FILE.parent / "activation_search_done").is_file()


def _mark_activation_search_done() -> None:
    flag = SESSION_FILE.parent / "activation_search_done"
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.write_text("1", encoding="utf-8")


def _run_activation_search(*, skip: bool = False) -> bool:
    """Guided first search after register/init — drives funnel first_search + TTFV."""
    if skip or _activation_search_done() or not get_token():
        return False

    en = ui.is_en()
    country = ui.get_default_country()
    query = _activation_query(country)
    status = (
        f"First search (activation): '{query}' in {country}..."
        if en
        else f"Primera búsqueda (activación): '{query}' en {country}..."
    )
    try:
        with ui.run_with_status(console, status):
            data = api(
                "POST",
                "/products/search",
                {"query": query, "limit": 3, "country": country},
            )
        if isinstance(data, dict) and data.get("error"):
            console.print(
                f"[yellow]{'Activation search skipped:' if en else 'Búsqueda de activación omitida:'} "
                f"{data['error']}[/]"
            )
            return False

        results = data.get("results", [])
        total = int(data.get("total", len(results)) or 0)
        if not results:
            console.print(
                f"[yellow]{'No results yet — try:' if en else 'Sin resultados aún — prueba:'} "
                f'market search "{query}" --country {country}[/]'
            )
            return False

        table = Table(
            title=(
                f'Activation: "{query}" ({total} hits)'
                if en
                else f'Activación: "{query}" ({total} resultados)'
            ),
            border_style=ui.TABLE_BORDER,
            show_header=True,
            header_style=f"bold {ui.MINT}",
            box=ui.table_box(),
        )
        table.add_column("#", style="dim", width=3, justify="right")
        table.add_column("Producto" if not en else "Product", max_width=34)
        table.add_column("Tienda" if not en else "Store", max_width=14)
        table.add_column("Precio" if not en else "Price", justify="right")
        for i, p in enumerate(results[:3], 1):
            color = store_color(p.get("store", ""))
            table.add_row(
                str(i),
                p.get("name", "?")[:34],
                f"[{color}]{p.get('store_name', p.get('store', '?'))}[/]",
                fmt_price(p.get("price", 0), p.get("currency", "PEN")),
            )
        console.print()
        console.print(table)
        ui.price_data_footer(console)
        _mark_activation_search_done()
        try:
            api("POST", "/v1/events", {"event": "first_search", "meta": {"query": query, "source": "activation"}})
        except Exception:
            pass
        title = "TTFV" if en else "TTFV"
        console.print(
            Panel(
                (
                    "[bold #00FF88]First real prices loaded.[/] "
                    "[dim]Your agent can now compare verified shelf data.[/]"
                    if en
                    else "[bold #00FF88]Primeros precios reales cargados.[/] "
                    "[dim]Tu agente ya puede comparar datos verificados de góndola.[/]"
                ),
                title=title,
                border_style="#00FF88",
            )
        )
        q = query.replace('"', '\\"')
        ui.print_hints(
            console,
            [
                f'market compare "{q}" --country {country}',
                f'market basket "{query}:1" --country {country}',
                "market doctor",
            ],
        )
        return True
    except Exception as exc:
        console.print(
            f"[dim]{'Activation search skipped' if en else 'Búsqueda de activación omitida'}: "
            f"{exc}[/]"
        )
        return False


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
            # P1 tracking: usuario chocó con el muro de autenticación
            try:
                import sys as _sys
                _cmd = _sys.argv[1] if len(_sys.argv) > 1 else "unknown"
                report_auth_wall_hit(_cmd)
            except Exception:
                pass
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


def _unwrap_v1(payload: dict) -> dict:
    """Extract ``data`` from v1 envelope responses."""
    if isinstance(payload, dict) and "data" in payload and "meta" in payload:
        inner = payload.get("data")
        return inner if isinstance(inner, dict) else {}
    return payload if isinstance(payload, dict) else {}


def _parse_basket_items(raw_items: list[str]) -> list[dict]:
    items: list[dict] = []
    for arg in raw_items:
        token = str(arg).strip().strip('"')
        if ":" in token:
            name, qty = token.rsplit(":", 1)
            try:
                qty_int = max(1, int(qty.strip()))
            except ValueError:
                items.append({"name": token, "qty": 1})
                continue
            items.append({"name": name.strip(), "qty": qty_int})
        else:
            items.append({"name": token, "qty": 1})
    return items


def _country_supermarket_stores(country: str) -> list[str]:
    """Supermarket retailers for a country — avoids hogar/departamentales breaking live basket.

    Excludes permanently-disabled connectors (same rule as COUNTRIES in
    market_geo_currency.py) — a disabled store (e.g. exito, WAF-blocked)
    can still have stale price_snapshots rows from before it was disabled,
    so leaving it in preferred_stores let optimize/basket serve frozen,
    unmaintained catalog data as if it were live (cli-market-backend#127
    optimize O1/O2 investigation).
    """
    cc = (country or "").strip().upper()
    return [
        k for k, v in STORES.items()
        if v.get("country") == cc
        and v.get("line") == "supermercados"
        and (not v.get("disabled") or v.get("enable_with_credentials"))
    ]


def _format_basket_item_label(breakdown_item: dict) -> str:
    """Build the "qty x Brand — Name" label for one basket breakdown item.

    TCO path's "item" is the raw search query, not the matched product —
    "resolved_name" carries the real product name there. Live path's "item"
    already is the product name. Brand is omitted when absent, when it's the
    VTEX/Magento "—" placeholder for unknown brand, or when it's already
    part of the product name (avoids "Gloria — Leche Gloria 1L").
    """
    name = breakdown_item.get("resolved_name") or breakdown_item.get("item") or "?"
    brand = (breakdown_item.get("brand") or "").strip()
    # Word-boundary match, not a raw substring check — a brand like "San"
    # must not be treated as already-present just because it's a substring
    # of an unrelated word like "Sancocho" (CodeRabbit review on world#497).
    brand_in_name = bool(brand) and re.search(rf"\b{re.escape(brand.lower())}\b", name.lower())
    label = f"{brand} — {name}" if brand and brand != "—" and not brand_in_name else name
    return f"{breakdown_item.get('qty', 1)}x {label}"


def _format_basket_alternates(breakdown_item: dict, currency: str) -> str:
    """Build the "other brands seen: X (PEN 3.90), Y (PEN 5.20)" hint for one
    breakdown item. Returns "" when there's nothing to show — the item had
    only one matching candidate at that store."""
    alternates = breakdown_item.get("alternates") or []
    if not alternates:
        return ""
    parts = []
    for alt in alternates:
        brand = (alt.get("brand") or "").strip()
        label = brand if brand and brand != "—" else (alt.get("name") or "?")
        price = alt.get("price")
        parts.append(f"{label} ({currency} {price:.2f})" if price is not None else label)
    return ", ".join(parts)


def _normalize_basket_store_rows(data: dict) -> list[dict]:
    """Wave 4 returns ``stores``; legacy live API returns ``comparison`` keyed by store."""
    rows = data.get("stores") or []
    if rows:
        return rows
    comparison = data.get("comparison") or {}
    if not comparison:
        return []
    normalized: list[dict] = []
    for store_key, row in comparison.items():
        if not isinstance(row, dict):
            continue
        items = row.get("items") or []
        breakdown = [
            {
                "item": i.get("name"),
                "brand": i.get("brand"),
                "qty": i.get("qty", 1),
                "price": i.get("price"),
                "alternates": i.get("alternates") or [],
            }
            for i in items
        ]
        normalized.append(
            {
                "store": store_key,
                "store_name": row.get("store_name") or store_key,
                "total": row.get("total"),
                "tco_total": row.get("tco_total") or row.get("total"),
                "currency": row.get("currency") or "PEN",
                "breakdown": breakdown,
            }
        )
    return normalized

# ── Commands ─────────────────────────────────────────────────────────────────

def cmd_login(args):
    data = cli_api("POST", "/auth/login", {"username": args.username, "password": args.password})
    ctx = ui.fetch_session_context() or {}
    tier = ctx.get("tier", "free")
    username = ctx.get("username") or data.get("username", "?")
    console.print(f"[#00FF88]✓ {data.get('message', 'OK')}[/]")
    ui.print_context_bar(console, tier=tier, username=username)
    if ui.is_pro_tier(tier):
        en = ui.is_en()
        console.print(Panel.fit(
            (
                f"[bold #00FF88]Build Pro activo[/] — [cyan]{username}[/]\n"
                f"[dim]Checkout, alertas y límites ampliados listos.[/]"
                if not en
                else f"[bold #00FF88]Build Pro active[/] — [cyan]{username}[/]\n"
                f"[dim]Checkout, alerts, and higher limits are ready.[/]"
            ),
            border_style="#00FF88",
        ))
    else:
        console.print(f"[dim]Usuario: {username}[/]")
    console.print(f"[dim]Token guardado en {SESSION_FILE}[/]")

def cmd_search(args):
    if not args.query.strip():
        console.print(welcome_banner())
        return
    params = {"query": args.query, "limit": args.limit, "page": args.page}
    if args.store:
        params["store"] = args.store
    if args.country:
        params["country"] = args.country
    if args.line:
        params["line"] = args.line
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
    try:
        api("POST", "/v1/events", {"event": "first_search", "meta": {"query": args.query}})
    except Exception:
        pass
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
    token = get_token()
    username = get_session_username()
    if not token or username in (None, "admin"):
        nag = _read_nag_count()
        if nag < 5:
            console.print()
            console.print(
                "[dim]Using demo account ([cyan]admin/market[/]). "
                "[bold #FFD600]Create your free account?[/] [cyan]market init[/][/]"
            )
            _write_nag_count(nag + 1)

def cmd_compare(args):
    params = {"query": args.query, "line": args.line, "limit": args.limit}
    if args.store:
        params["store"] = args.store
    if args.country:
        params["country"] = args.country
    with console.status(f"[cyan]Comparando '{args.query}'..."):
        data = cli_api("POST", "/products/compare", params)
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
    # Always include stores that are "best" for any product so the Mejor column
    # is never pointing at a store with no visible price column.
    best_stores = {item.get("best_store") for item in comp if item.get("best_store")}
    priority = [s for s in all_stores if s in best_stores]
    rest = [s for s in all_stores if s not in best_stores]
    display_stores = (priority + rest)[:max(6, len(priority))]
    table = Table(title=f'[bold white]Comparativa: "{args.query}"[/]', border_style=ui.TABLE_BORDER)
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Producto", style="white", max_width=30, no_wrap=False)
    table.add_column("Marca", style="blue", max_width=12)
    for sk in display_stores:
        store_name = STORES.get(sk, {}).get("name", sk)
        table.add_column(store_name, justify="right", width=11)
    table.add_column("Mejor", justify="center", width=10)
    def _pcell(sk: str, prices: dict, prices_per_unit: dict) -> str:
        if sk in prices:
            currency = STORES.get(sk, {}).get("currency", "PEN")
            cell = f"[{store_color(sk)}]{fmt_price(prices[sk], currency)}[/]"
            ppu = prices_per_unit.get(sk)
            if ppu:
                cell += f"\n[dim]{fmt_price(ppu['price_per'], currency)}/{ppu['basis']}[/]"
            return cell
        return "[dim]—[/]"

    has_any_unit_price = any(item.get("prices_per_unit") for item in comp)
    for i, item in enumerate(comp, 1):
        prices = item.get("prices", {})
        prices_per_unit = item.get("prices_per_unit", {})
        best = item.get("best_store", "")
        best_color = store_color(best) if best else "dim"
        row = [str(i), item.get("name", ""), item.get("brand", "")]
        for sk in display_stores:
            row.append(_pcell(sk, prices, prices_per_unit))
        row.append(f"[bold {best_color}]{STORES.get(best, {}).get('name', best)}[/]" if best else "—")
        table.add_row(*row)
    console.print()
    console.print(table)
    if has_any_unit_price:
        console.print("[dim]Precio/unidad (kg o L) bajo el precio de lista cuando el tamaño del paquete se pudo determinar.[/]")

def _missions_enabled() -> bool:
    return os.environ.get("MARKET_MISSIONS", "1").strip().lower() not in ("0", "false", "no")


def _dispatch_investigate(
    query: str,
    country: str,
    *,
    line: str | None = None,
    include_intel: bool = True,
    intel_days: int = 30,
):
    from market_core.market_missions import run_investigate

    return run_investigate(
        query,
        country,
        line=line,
        include_intel=include_intel,
        intel_days=intel_days,
    )


def cmd_investigate(args):
    en = ui.is_en()
    cc = getattr(args, "country", None) or ui.get_default_country()
    if not _missions_enabled():
        msg = "Investigate missions are disabled (MARKET_MISSIONS=0)." if en else "Misiones investigate deshabilitadas (MARKET_MISSIONS=0)."
        if getattr(args, "json", False) or ui.is_json_mode():
            ui.json_exit(console, False, error=msg, next_commands=[f'market search "leche" --country {cc}'])
        console.print(f"[yellow]{msg}[/]")
        sys.exit(1)

    query = (args.query or "").strip()
    if not query:
        hint = f'market investigate "arroz" --country {cc}'
        if getattr(args, "json", False) or ui.is_json_mode():
            ui.json_exit(console, False, error="query required", next_commands=[hint])
        console.print(f"[yellow]{'Query required' if en else 'Query requerido'}[/]")
        ui.print_hints(console, [hint])
        sys.exit(1)

    tier = ui.fetch_tier()
    ui.tier_gate(console, "investigate", tier, json_args=args)

    country = args.country or ui.get_default_country()
    if args.country:
        ui.set_default_country(args.country)

    try:
        with console.status(f"[cyan]{'Running investigate mission...' if en else 'Ejecutando misión investigate...'}[/]"):
            report = _dispatch_investigate(
                query,
                country,
                line=args.line,
                include_intel=not getattr(args, "no_intel", False),
                intel_days=getattr(args, "days", 30) or 30,
            )
    except ImportError:
        msg = (
            "Investigate requires cli-market-core>=1.9.36. Run: pip install -U cli-market-world"
            if en
            else "Investigate requiere cli-market-core>=1.9.36. Ejecuta: pip install -U cli-market-world"
        )
        if getattr(args, "json", False) or ui.is_json_mode():
            ui.json_exit(console, False, error=msg, next_commands=["market doctor"])
        ui.print_actionable_error(console, msg)
        sys.exit(1)

    ok = report.get("status") != "error"
    q = query.replace('"', '\\"')
    next_cmds = [
        f'market compare "{q}" --country {country}',
        f'market intel inflation --country {country}',
    ]

    if getattr(args, "json", False) or ui.is_json_mode():
        ui.emit_json(
            ui.json_response(ok, report, error=report.get("error"), next_commands=next_cmds),
            console,
        )
        sys.exit(0 if ok else 1)

    if report.get("error"):
        console.print(f"[red]{report['error']}[/]")
        sys.exit(1)

    ui.print_investigate_report(console, report)
    if report.get("status") == "partial":
        sys.exit(1)

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
    is_en = ui.is_en()
    total = sum(i["price"] * i["quantity"] for i in cart)
    n = len(cart)
    confirm_msg = (
        f"Clear {n} item(s) — {fmt_price(total)}? [y/N] "
        if is_en
        else f"¿Vaciar {n} item(s) — {fmt_price(total)}? [s/N] "
    )
    try:
        resp = input(confirm_msg).strip().lower()
    except (EOFError, KeyboardInterrupt):
        console.print("\n[dim]Cancelado[/]")
        return
    if resp not in ("s", "y"):
        console.print("[dim]Cancelado[/]")
        return
    for item in cart:
        cli_api("DELETE", f"/cart/{item['cart_id']}")
    console.print("[#3cffd0]✓ Carrito vaciado[/]" if not is_en else "[#3cffd0]✓ Cart cleared[/]")

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
    if data.get("confirmation_mode") == "manual":
        console.print("[yellow]Confirmación manual: el pago se valida por webhook o confirmación ops.[/]")
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
    is_en = ui.is_en()
    with console.status("[cyan]Procesando...[/]" if not is_en else "[cyan]Processing...[/]"):
        data = cli_api("POST", "/agent/ask", {"prompt": " ".join(args.prompt) if isinstance(args.prompt, list) else args.prompt})

    if getattr(args, "json", False) or ui.is_json_mode():
        ui.emit_json(ui.json_response(True, {"result": data}, next_commands=["market ask", "market cart"]), console)
        return

    error = data.get("error") or data.get("detail")
    if error:
        console.print(f"[red]{error}[/]")
        return

    if "answer" in data:
        # LLM-powered agent (Claude Haiku with tool use) — server already
        # called search_products/compare_basket internally and wrote the
        # final natural-language answer; there's no action/query to drive
        # a follow-up CLI call for.
        for tool in data.get("tools_used", []):
            console.print(f"[dim]→ {tool}[/]")
        answer = (data.get("answer") or "").strip()
        if answer:
            console.print()
            console.print(Panel(answer, border_style=ui.TABLE_BORDER, padding=(1, 2)))
        else:
            console.print("[yellow]Sin respuesta del agente[/]" if not is_en else "[yellow]No answer from agent[/]")
        return

    action = data.get("action", "search")
    query = data.get("query", "")
    qty = data.get("quantity", 1)

    console.print(f"[dim]→ {action}" + (f": \"{query}\"" if query else "") + "[/]")

    if action == "search" and query:
        search_params = {"query": query, "limit": 5}
        country_hint = data.get("country")
        if country_hint:
            search_params["country"] = country_hint
        with console.status(f"[cyan]Buscando '{query}'...[/]"):
            results = cli_api("POST", "/products/search", search_params)
        products = results.get("results", [])
        if not products:
            console.print(f"[yellow]Sin resultados para '{query}'[/]")
            return
        table = Table(border_style=ui.TABLE_BORDER, show_header=True)
        table.add_column("#", style="dim", width=3, justify="right")
        table.add_column("Producto", max_width=38)
        table.add_column("Tienda", max_width=12)
        table.add_column("Precio", style="yellow", justify="right")
        for i, p in enumerate(products, 1):
            table.add_row(
                str(i), p["name"][:38],
                p.get("store_name", p.get("store", "?")),
                fmt_price(p.get("price", 0), p.get("currency", "PEN")),
            )
        console.print()
        console.print(table)
        p0 = products[0]
        confirm_msg = (
            f"Add {qty}x {p0['name'][:35]} ({fmt_price(p0['price'])}) to cart? [y/N] "
            if is_en
            else f"¿Agregar {qty}x {p0['name'][:35]} ({fmt_price(p0['price'])}) al carrito? [s/N] "
        )
        try:
            resp = input(confirm_msg).strip().lower()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[dim]Cancelado[/]")
            return
        if resp in ("s", "y"):
            cli_api("POST", "/cart/add", {
                "product_id": p0.get("product_id", p0.get("id", "")),
                "name": p0["name"],
                "price": p0["price"],
                "store": p0.get("store", ""),
                "quantity": qty,
            })
            console.print("[#3cffd0]✓ Agregado al carrito[/]" if not is_en else "[#3cffd0]✓ Added to cart[/]")
            console.print("[dim]market cart · market checkout[/]")
        else:
            console.print("[dim]Usa market add <ID> cuando estés listo[/]" if not is_en else "[dim]Use market add <ID> when ready[/]")

    elif action == "compare" and query:
        with console.status(f"[cyan]Comparando '{query}'...[/]"):
            results = cli_api("POST", "/products/compare", {"query": query, "limit": 5})
        comparison = results.get("comparison", [])
        if not comparison:
            console.print(f"[yellow]Sin resultados para '{query}'[/]")
            return
        table = Table(border_style=ui.TABLE_BORDER, show_header=True)
        table.add_column("Producto", max_width=36)
        table.add_column("Mejor tienda", max_width=14)
        table.add_column("Mejor precio", style="yellow", justify="right")
        for item in comparison[:5]:
            table.add_row(
                item.get("name", "")[:36],
                item.get("best_store", "?"),
                fmt_price(item.get("best_price", 0)),
            )
        console.print()
        console.print(table)
        console.print(f"[dim]market compare \"{query}\" para ver todos los precios[/]")

    elif action == "cart":
        cmd_cart(args)

    elif action == "checkout":
        console.print("[dim]Usa: market checkout --payment yape|plin|tarjeta[/]" if not is_en else "[dim]Use: market checkout --payment yape|plin|card[/]")

    elif action == "reorder":
        result = cli_api("POST", "/orders/reorder")
        console.print(f"[#3cffd0]✓ {result.get('message', 'OK')}[/]")

    else:
        console.print(f"[#3cffd0]✓ {data.get('message', 'OK')}[/]")

def cmd_preferences(args):
    data = cli_api("GET", "/agent/preferences")
    if getattr(args, "json", False) or ui.is_json_mode():
        ui.emit_json(ui.json_response(True, data, next_commands=["market preferences", "market whoami"]), console)
        return
    console.print(f"[bold]Total gastado:[/] {fmt_price(data.get('total_spent', 0))}")
    console.print(f"[bold]Órdenes:[/] {data.get('total_orders', 0)}")

def cmd_countries(args):
    data = cli_api("GET", "/countries")
    countries = data.get("countries", {})
    if getattr(args, "json", False) or ui.is_json_mode():
        ui.emit_json(
            ui.json_response(True, {"countries": countries, "count": len(countries)}, next_commands=["market countries", "market lines"]),
            console,
        )
        return
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
    if getattr(args, "json", False) or ui.is_json_mode():
        ui.emit_json(
            ui.json_response(True, {"lines": lines, "count": len(lines)}, next_commands=["market lines", "market countries"]),
            console,
        )
        return
    table = Table(title="[bold #3cffd0]Líneas de negocio[/]", border_style=ui.TABLE_BORDER)
    table.add_column("Línea", style="bold")
    table.add_column("Retailers")
    table.add_column("Cant.", justify="center")
    for _line_id, info in lines.items():
        stores_str = ", ".join(s["name"] for s in info["stores"].values())
        table.add_row(f"{info['emoji']} {info['name']}", stores_str, str(info["total_stores"]))
    console.print()
    console.print(table)

def cmd_discover(args):
    """Retail coverage in one call — combines lines + countries (mirrors market_discover MCP tool)."""
    country_filter = (getattr(args, "country", None) or "").upper() or None
    line_filter = getattr(args, "line", None) or None
    data_c = cli_api("GET", "/countries")
    data_l = cli_api("GET", "/lines")
    countries = data_c.get("countries", {})
    lines = data_l.get("lines", {})
    if getattr(args, "json", False) or ui.is_json_mode():
        ui.emit_json(
            ui.json_response(True, {"countries": countries, "lines": lines}, next_commands=["market search", "market compare"]),
            console,
        )
        return
    table_c = Table(title="[bold #3cffd0]Cobertura — Países[/]", border_style=ui.TABLE_BORDER)
    table_c.add_column("País", style="bold")
    table_c.add_column("Tiendas")
    table_c.add_column("Cant.", justify="center")
    for code, info in sorted(countries.items()):
        if country_filter and code != country_filter:
            continue
        table_c.add_row(info["name"], ", ".join(info["stores"]), str(info["count"]))
    console.print()
    console.print(table_c)
    table_l = Table(title="[bold #3cffd0]Líneas de negocio[/]", border_style=ui.TABLE_BORDER)
    table_l.add_column("Línea", style="bold")
    table_l.add_column("Retailers")
    table_l.add_column("Cant.", justify="center")
    for lid, info in lines.items():
        if line_filter and lid != line_filter:
            continue
        stores_str = ", ".join(s["name"] for s in info["stores"].values())
        table_l.add_row(f"{info['emoji']} {info['name']}", stores_str, str(info["total_stores"]))
    console.print()
    console.print(table_l)
    discover_cc = country_filter or ui.get_default_country()
    console.print(f"\n[dim]market search --country {discover_cc} · market compare --line super[/]")


def cmd_stores(args):
    """List retailers from GET /stores (filterable by country and line)."""
    country = (getattr(args, "country", None) or "").upper() or None
    line = getattr(args, "line", None) or None
    qs_parts: list[str] = []
    if country:
        qs_parts.append(f"country={country}")
    if line:
        qs_parts.append(f"line={line}")
    path = "/stores" + ("?" + "&".join(qs_parts) if qs_parts else "")
    data = cli_api("GET", path)
    stores = data.get("stores", {})
    total = int(data.get("total", len(stores)))

    if getattr(args, "json", False) or ui.is_json_mode():
        cc = country or ui.get_default_country()
        ui.emit_json(
            ui.json_response(
                True,
                {"stores": stores, "total": total, "country": country, "line": line},
                next_commands=[f"market stores --country {cc}", f"market search --country {cc}"],
            ),
            console,
        )
        return

    title = "[bold #3cffd0]Retailers"
    if country:
        country_name = COUNTRIES.get(country, {}).get("name", country)
        title += f" — {country_name}"
    if line:
        line_name = LINES.get(line, {}).get("name", line)
        title += f" · {line_name}"
    table = Table(title=title + "[/]", border_style=ui.TABLE_BORDER)
    table.add_column("ID", style="dim")
    table.add_column("Nombre" if not ui.is_en() else "Name", style="bold")
    table.add_column("País" if not ui.is_en() else "Country")
    table.add_column("Línea" if not ui.is_en() else "Line")
    table.add_column("Moneda" if not ui.is_en() else "Currency", justify="center")

    for store_id, info in sorted(
        stores.items(),
        key=lambda item: (item[1].get("country", ""), item[1].get("name", "")),
    ):
        line_name = info.get("line_name") or LINES.get(info.get("line", ""), {}).get("name", info.get("line", ""))
        table.add_row(
            store_id,
            info.get("name", store_id),
            info.get("country", ""),
            line_name or "",
            info.get("currency", ""),
        )
    console.print()
    console.print(table)
    hint_cc = country or ui.get_default_country()
    hint = (
        f"\n[dim]{total} retailers · market search --country {hint_cc} \"leche\"[/]"
        if not ui.is_en()
        else f'\n[dim]{total} retailers · market search --country {hint_cc} "milk"[/]'
    )
    console.print(hint)


def cmd_categories(args):
    with console.status(f"[cyan]Cargando categorías de {STORES[args.store]['name']}..."):
        data = cli_api("GET", f"/categories/{args.store}")
    # /categories/{store} now returns {"store", "categories", "disclaimer"}
    # instead of a bare list (cli-market-backend#127/#135) — support both
    # shapes so this doesn't break against an older pinned backend.
    if isinstance(data, dict) and "categories" in data:
        cats = data.get("categories") or []
        disclaimer = data.get("disclaimer")
    else:
        cats = data if isinstance(data, list) else []
        disclaimer = None
    if getattr(args, "json", False) or ui.is_json_mode():
        ui.emit_json(ui.json_response(True, {"store": args.store, "categories": cats, "disclaimer": disclaimer}, next_commands=["market categories --store " + args.store]), console)
        return
    if cats:
        _print_cat_tree(cats, indent=0)
        if disclaimer:
            console.print(f"\n[dim]{disclaimer}[/]")
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

def cmd_canasta_basica(json_mode=False, country="PE"):
    """Canasta básica — default when `market` is run without arguments."""
    is_en = get_lang() == "en"
    console.print(f"\n[bold white]{'🧺 Canasta Básica' if not is_en else '🧺 Basic Basket'}[/] [dim]({country})[/]\n")
    args = argparse.Namespace(
        items=CANASTA_BASICA,
        country=country,
        json=json_mode,
    )
    cmd_basket(args)


def cmd_procure(args):
    """Complete procurement loop: search items, find best prices, compare to budget, add to cart, checkout."""
    items = [item.strip() for item in args.items_list.split(",") if item.strip()]
    budget = args.budget
    country = args.country or "PE"
    is_en = get_lang() == "en"
    is_json = getattr(args, "json", False)

    if not items:
        console.print(f"[yellow]{'No items specified' if is_en else 'Sin productos especificados'}[/]")
        return

    console.print(f"\n[bold white]{'🔍 Procure' if not is_en else '🔍 Procure'}[/] [dim]— {len(items)} {'productos' if not is_en else 'items'}, {'presupuesto' if not is_en else 'budget'}: {budget}[/]\n")

    # Step 1: Search each item individually
    best_picks = []
    for item in items:
        with console.status(f"[cyan]{'Buscando' if not is_en else 'Searching'} '{item}'..."):
            data = cli_api("POST", "/products/search", {"query": item, "limit": 5, "country": country})
        results = data.get("results", [])
        # /products/search does plain keyword matching with no category
        # guard — "arroz" (rice) matched a "Cuchara Para Arroz" (rice
        # spoon utensil) and the cheapest-wins ranking below picked it as
        # the "best" result (S8, cli-market-backend#127). Filter through
        # the same staple/exclusion matcher already used by basket compare
        # before ranking by price, so a real food match wins when one
        # exists in the result set.
        food_results = [r for r in results if matches_food_basket_query(item, r)]
        candidates = food_results or results
        if candidates:
            best = min(candidates, key=lambda p: p.get("price", float("inf")))
            best_picks.append({
                "name": item,
                "product": best.get("name", item),
                "price": best.get("price", 0),
                "currency": best.get("currency", "PEN"),
                "store": best.get("store_name", best.get("store", "?")),
                "store_key": best.get("store", ""),
                "product_id": str(best.get("id", best.get("product_id", ""))),
                "uncertain_match": not food_results,
            })
        else:
            console.print(f"  [yellow]⚠ {'Not found' if is_en else 'No encontrado'}: {item}[/]")

    if not best_picks:
        console.print(f"[yellow]{'No products found' if is_en else 'No se encontraron productos'}[/]")
        return

    # Step 2: Show results table
    total = sum(p["price"] for p in best_picks)
    currency = best_picks[0]["currency"]
    within_budget = total <= budget

    if is_json:
        console.print(json.dumps({
            "items": best_picks,
            "total": total,
            "currency": currency,
            "budget": budget,
            "within_budget": within_budget,
        }, indent=2, ensure_ascii=False))
        return

    table = Table(title=f"[bold white]{'Procurement Results' if is_en else 'Resultados de Procure'}[/]", border_style=ui.TABLE_BORDER)
    table.add_column("#", style="dim", width=3, justify="right")
    table.add_column("Producto", style="white", max_width=24)
    table.add_column("Tienda", max_width=16)
    table.add_column("Precio", style="yellow", justify="right")

    for i, p in enumerate(best_picks, 1):
        color = store_color(p["store_key"])
        product_label = p["product"]
        if p.get("uncertain_match"):
            product_label += " [yellow]⚠[/]"
        table.add_row(str(i), product_label, f"[{color}]{p['store']}[/]", fmt_price(p["price"], p["currency"]))

    console.print(table)
    if any(p.get("uncertain_match") for p in best_picks):
        console.print(
            "[yellow]⚠ Uno o más productos no coincidieron con un match confiable de categoría — revisá antes de confirmar.[/]"
            if not is_en else
            "[yellow]⚠ One or more products didn't match a confident category — review before confirming.[/]"
        )

    # Step 3: Summary vs budget
    status_color = "#00FF88" if within_budget else "#FF6B6B"
    status_icon = "✓" if within_budget else "✗"
    console.print(f"\n  [{status_color}]{status_icon} Total: {currency} {total:.2f}[/]  [dim]|[/]  {'Presupuesto' if not is_en else 'Budget'}: {currency} {budget:.2f}")
    if not within_budget:
        over = total - budget
        console.print(f"  [#FF6B6B]{'Excede por' if not is_en else 'Over by'}: {currency} {over:.2f}[/]")
        ui.print_hints(console, ["market procure \"lista\" --budget N --country PE"])
        return

    # Step 4: Add all items to cart
    token = get_token()
    if not token:
        console.print(f"\n[dim]{'Login to add to cart:' if is_en else 'Inicia sesión para agregar al carrito:'} [cyan]market login[/][/]")
        return

    # procure used to go straight from search results to cart/add with no
    # review step — a wrong match (e.g. a kitchen utensil for "arroz") was
    # already in the cart before the user could reject it (S22,
    # cli-market-backend#127). Require explicit confirmation, same pattern
    # already used by `market ask`'s search->cart flow.
    confirm_msg = (
        f"Add {len(best_picks)} items ({currency} {total:.2f}) to cart? [y/N] "
        if is_en
        else f"¿Agregar {len(best_picks)} productos ({currency} {total:.2f}) al carrito? [s/N] "
    )
    try:
        resp = input(confirm_msg).strip().lower()
    except (EOFError, KeyboardInterrupt):
        console.print("\n[dim]Cancelado[/]" if not is_en else "\n[dim]Cancelled[/]")
        return
    if resp not in ("s", "y"):
        console.print("[dim]Cancelado[/]" if not is_en else "[dim]Cancelled[/]")
        return

    with console.status(f"[cyan]{'Adding to cart...' if is_en else 'Agregando al carrito...'}"):
        for p in best_picks:
            try:
                cli_api("POST", "/cart/add", {
                    "product_id": p["product_id"],
                    "name": p["product"],
                    "price": p["price"],
                    "store": p["store_key"],
                    "quantity": 1,
                })
            except Exception:
                pass

    console.print(f"\n[#00FF88]✓ {'Added to cart' if is_en else 'Agregado al carrito'}[/] ({len(best_picks)} {'items' if is_en else 'productos'}, {currency} {total:.2f})")
    ui.print_hints(console, ["market cart", "market checkout --payment paypal"])


def cmd_basket(args):
    items = _parse_basket_items(args.items)
    country = getattr(args, "country", None) or "PE"
    stores = _country_supermarket_stores(country) if country else []
    line = getattr(args, "line", None)
    payload = {
        "items": items,
        "country": country,
        "stores": stores or None,
        "line": line,
        "include_tco": bool(getattr(args, "tco", False)),
        "include_delivery": not bool(getattr(args, "no_delivery", False)),
        "include_action_links": bool(getattr(args, "action_links", False)),
    }
    is_en = ui.is_en()
    with console.status(
        "[cyan]Comparando canasta con TCO..." if payload["include_tco"] and not is_en
        else "[cyan]Comparing basket with TCO..." if payload["include_tco"]
        else "[cyan]Comparando canasta..." if not is_en
        else "[cyan]Comparing basket..."
    ):
        raw = cli_api("POST", "/v1/basket/compare", payload)
    if getattr(args, "json", False) or ui.is_json_mode():
        console.print(json.dumps(raw, indent=2, ensure_ascii=False))
        return
    data = _unwrap_v1(raw)
    store_rows = _normalize_basket_store_rows(data)
    if not store_rows:
        console.print(
            "[yellow]No se encontraron productos en ninguna tienda[/]"
            if not is_en
            else "[yellow]No products found at any store[/]"
        )
        return
    title = "Comparativa de canasta (TCO)" if payload["include_tco"] and not is_en else (
        "Basket comparison (TCO)" if payload["include_tco"] else (
            "Comparativa de canasta" if not is_en else "Basket comparison"
        )
    )
    show_alternates = bool(getattr(args, "show_alternates", False))
    table = Table(title=f"[bold white]{title}[/]", border_style=ui.TABLE_BORDER)
    table.add_column("Tienda" if not is_en else "Store", style="bold")
    table.add_column("Items", max_width=56)
    if show_alternates:
        table.add_column("Otras marcas" if not is_en else "Other brands", max_width=48, style="dim")
    total_col = "TCO" if payload["include_tco"] else ("Total" if is_en else "Total")
    table.add_column(total_col, style="bold yellow", justify="right")
    for row in sorted(
        store_rows,
        key=lambda s: float(s.get("tco_total") or s.get("total") or 999999),
    ):
        breakdown = row.get("breakdown") or []
        currency = row.get("currency") or "PEN"
        items_str = ", ".join(_format_basket_item_label(b) for b in breakdown[:4])
        amount = float(row.get("tco_total") or row.get("total") or 0)
        row_cells = [row.get("store_name") or row.get("store", "?"), items_str]
        if show_alternates:
            alt_str = "; ".join(
                filter(None, (_format_basket_alternates(b, currency) for b in breakdown[:4]))
            )
            row_cells.append(alt_str or "—")
        row_cells.append(f"{currency} {amount:.2f}")
        table.add_row(*row_cells)
    console.print(table)
    leader = min(store_rows, key=lambda s: float(s.get("tco_total") or s.get("total") or 999999))
    shelf_hint = data.get("cheapest_shelf_store")
    tco_hint = data.get("cheapest_tco_store")
    if shelf_hint and tco_hint and shelf_hint != tco_hint:
        console.print(
            f"\n[dim]{'Góndola' if not is_en else 'Shelf'}: {shelf_hint} · TCO: {tco_hint}[/]"
        )
    console.print(
        f"\n[#00FF88]✓ {'Mejor opción' if not is_en else 'Best option'}: "
        f"{leader.get('store_name')} — {leader.get('currency', 'PEN')} "
        f"{float(leader.get('tco_total') or leader.get('total') or 0):.2f}[/]"
    )
    links = data.get("action_links") or []
    if links:
        console.print(f"\n[bold]{'Enlaces' if not is_en else 'Action links'}:[/]")
        for link in links[:4]:
            kind = link.get("type", "?")
            url = link.get("url") or link.get("token") or ""
            aff = " [affiliate]" if link.get("affiliate") else ""
            console.print(f"  [cyan]{kind}[/]{aff} {url[:80]}")


def cmd_optimize(args):
    """One-call purchase optimization — basket + TCO + substitutes + intel + action links."""
    items = _parse_basket_items(args.items)
    if not items:
        console.print("[yellow]Sin productos[/]" if not ui.is_en() else "[yellow]No items[/]")
        return
    country = getattr(args, "country", None) or "PE"
    constraints: dict = {
        "include_tco": not bool(getattr(args, "no_tco", False)),
        "allow_substitutes": not bool(getattr(args, "no_substitutes", False)),
        "include_action_links": True,
    }
    if getattr(args, "budget", None) is not None:
        constraints["max_budget"] = float(args.budget)
    if getattr(args, "payment", None):
        constraints["payment_method"] = args.payment
    if country and not constraints.get("preferred_stores"):
        local_stores = _country_supermarket_stores(country)
        if local_stores:
            constraints["preferred_stores"] = local_stores
    os.environ.setdefault(
        "MARKET_API_TIMEOUT",
        os.environ.get("MARKET_MISSION_TIMEOUT", "180"),
    )
    payload = {
        "country": country,
        "items": items,
        "constraints": constraints,
        "include_intel": not bool(getattr(args, "no_intel", False)),
    }
    is_en = ui.is_en()
    with console.status(
        "[cyan]Optimizando compra..." if not is_en else "[cyan]Optimizing purchase..."
    ):
        raw = cli_api("POST", "/v1/missions/optimize-purchase", payload)
    if getattr(args, "json", False) or ui.is_json_mode():
        console.print(json.dumps(raw, indent=2, ensure_ascii=False))
        return
    data = _unwrap_v1(raw)
    if data.get("status") != "ok":
        err = data.get("error") or ("Error en misión" if not is_en else "Mission error")
        console.print(f"[red]{err}[/]")
        return
    rec = data.get("recommendation") or {}
    action = rec.get("action", "monitor")
    action_color = {"buy_now": "#00FF88", "wait": "#FF6B35", "monitor": "yellow"}.get(action, "white")
    currency = rec.get("currency") or "PEN"
    console.print(
        f"\n[bold]{'Recomendación' if not is_en else 'Recommendation'}:[/] "
        f"[{action_color}]{action.upper()}[/]"
    )
    console.print(
        f"  {'Tienda' if not is_en else 'Store'}: {rec.get('primary_store_name') or rec.get('primary_store')}"
    )
    console.print(
        f"  {'Góndola' if not is_en else 'Shelf'}: {currency} {float(rec.get('shelf_total') or 0):.2f} · "
        f"TCO: {currency} {float(rec.get('tco_total') or 0):.2f}"
    )
    items_requested = rec.get("items_requested")
    items_matched = rec.get("items_matched")
    if items_requested is not None and items_matched is not None and items_matched < items_requested:
        # The shelf/TCO total above is a SUM over only the matched items — an
        # implausibly low total (e.g. ARS 615 for a 4-item basket) is usually
        # this, not a pricing bug: 1-2 items silently failed to match at the
        # winning store and were dropped from the total instead of excluding
        # that store from consideration (cli-market-backend#127 optimize O1).
        console.print(
            f"  [yellow]⚠ Solo {items_matched}/{items_requested} items encontrados en esta tienda "
            f"— el total no representa la canasta completa.[/]"
            if not is_en else
            f"  [yellow]⚠ Only {items_matched}/{items_requested} items matched at this store "
            f"— the total does not reflect the full basket.[/]"
        )
    headroom = rec.get("budget_headroom")
    if headroom is not None:
        console.print(f"  {'Presupuesto restante' if not is_en else 'Budget headroom'}: {currency} {headroom:.2f}")
    rationale = rec.get("rationale_es") or rec.get("rationale")
    if rationale:
        console.print(f"\n[dim]{rationale}[/]")
    links = data.get("action_links") or []
    if links:
        console.print(f"\n[bold]{'Siguiente paso' if not is_en else 'Next step'}:[/]")
        for link in links[:4]:
            kind = link.get("type", "?")
            url = link.get("url") or ""
            if link.get("type") == "export_list" and link.get("token"):
                url = f"/v1/export/shopping-list/{link['token']}"
            aff = " [affiliate]" if link.get("affiliate") else ""
            console.print(f"  [cyan]{kind}[/]{aff} {url[:90]}")
    ui.print_hints(
        console,
        [
            f"market basket {' '.join(args.items)} --country {country} --tco",
            "market checkout --payment yape",
        ],
    )

def cmd_inflation(args):
    params = []
    if args.country:
        params.append(f"country={args.country}")
    if args.line:
        params.append(f"line={args.line}")
    days = getattr(args, "days", None) or 7
    params.append(f"days={days}")
    qs = "&".join(params)
    with console.status("[cyan]Calculando RPV (Retail Price Velocity)..."):
        data = cli_api("GET", f"/v1/intel/inflation?{qs}" if qs else "/v1/intel/inflation")
    items = data.get("items", [])
    n_products = sum(int(i.get("n_products") or 0) for i in items)
    no_coverage = n_products == 0
    if getattr(args, "json", False) or ui.is_json_mode():
        ui.emit_json(ui.json_response(
            True, data,
            next_commands=[f"market intel inflation --country {args.country or 'PE'}", "market intel indicators"],
            status=2 if no_coverage else None,
        ), console)
        if no_coverage:
            sys.exit(2)
        return
    avg = data.get("avg_rpv_7d_pct", data.get("avg_inflation_pct", 0))
    color = "#FF6B35" if avg > 0 else "#00FF88"
    meta = (
        f"{n_products} productos · {len(items)} líneas"
        if not ui.is_en()
        else f"{n_products} products · {len(items)} lines"
    )
    console.print(f"\n[bold]RPV promedio (7d): [{color}]{avg:+.1f}%[/] ({meta})[/]")
    console.print("[dim]Retail Price Velocity — no es inflación oficial IPC.[/]")
    if no_coverage:
        cc_label = args.country or "LATAM"
        warn = (
            f"[yellow]Sin cobertura activa para {cc_label} en esta ventana — 0 tiendas con datos.[/]"
            if not ui.is_en()
            else f"[yellow]No active coverage for {cc_label} in this window — 0 stores with data.[/]"
        )
        console.print(warn)
        sys.exit(2)
    if items:
        title = "Variación por línea" if not ui.is_en() else "Change by line"
        table = Table(title=f"[bold white]{title}[/]", border_style=ui.TABLE_BORDER)
        table.add_column("Línea" if not ui.is_en() else "Line", max_width=28)
        table.add_column("Antes" if not ui.is_en() else "Before", style="dim")
        table.add_column("Ahora" if not ui.is_en() else "Now", style="dim")
        table.add_column("Delta %", justify="right")
        for i in items[:15]:
            delta = float(i.get("delta_pct") or 0)
            cur = i.get("currency") or ""
            before = float(i.get("avg_before") or i.get("first_price") or 0)
            now = float(i.get("avg_now") or i.get("last_price") or 0)
            raw_label = i.get("line") or i.get("line_key") or i.get("product") or "?"
            label = html.unescape(str(raw_label))[:28]
            c = "#FF6B35" if delta > 0 else "#00FF88"
            table.add_row(
                label,
                f"{cur} {before:.2f}".strip(),
                f"{cur} {now:.2f}".strip(),
                f"[{c}]{delta:+.1f}%[/]",
            )
        console.print(table)

def cmd_indicators(args):
    if args.refresh:
        qs = f"country={args.country}" if args.country else ""
        with console.status("[cyan]Refrescando indicadores..."):
            data = cli_api("POST", f"/v1/intel/refresh?{qs}" if qs else "/v1/intel/refresh")
        if getattr(args, "json", False) or ui.is_json_mode():
            ui.emit_json(ui.json_response(True, data, next_commands=[f"market intel indicators -c {args.country or ui.get_default_country()}"]), console)
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
    if getattr(args, "json", False) or ui.is_json_mode():
        if args.country:
            latest = cli_api("GET", f"/v1/intel/scores?country={args.country}")
            ui.emit_json(ui.json_response(True, {"catalog": catalog, "scores": latest}, next_commands=[f"market intel indicators -c {args.country}", f"market intel scores -c {args.country}"]), console)
        else:
            ui.emit_json(ui.json_response(True, catalog, next_commands=[f"market intel indicators -c {ui.get_default_country()}"]), console)
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
            console.print(f"[yellow]Sin scores aún. Corré: market intel indicators -c {args.country}[/]")
        else:
            console.print(f"[yellow]No scores yet. Run: market intel indicators -c {args.country}[/]")

    ui.print_intel_footer(
        console,
        [f"market intel indicators -c {cc}", f"market intel scores -c {cc}", f"market intel enrichment -c {cc}"],
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
        _sc_cc = args.country or "PE"
        msg = (
            f"Sin scores aún. Corré: market intel indicators -c {_sc_cc}"
            if not ui.is_en()
            else f"No scores yet. Run: market intel indicators -c {_sc_cc}"
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
    _footer_cc = args.country or ui.get_default_country()
    ui.print_intel_footer(console, [f"market intel indicators -c {_footer_cc}", f"market intel enrichment -c {_footer_cc}"])


def cmd_intel_brief(args):
    """Executive intel brief: headline + shelf signals + scores in one call."""
    is_en = ui.is_en()
    params = []
    cc = getattr(args, "country", None)
    line = getattr(args, "line", None)
    days = getattr(args, "days", None) or 7
    catalog = getattr(args, "catalog", False)
    if cc:
        params.append(f"country={cc}")
    if line:
        params.append(f"line={line}")
    params.append(f"days={days}")
    if catalog:
        params.append("include_catalog=true")
    qs = "&".join(params)
    scope = cc or ("LATAM" if not line else line)

    with console.status(f"[cyan]{'Generando brief' if not is_en else 'Generating brief'} — {scope}..."):
        data = cli_api("GET", f"/v1/intel/brief?{qs}" if qs else "/v1/intel/brief")

    if getattr(args, "json", False) or ui.is_json_mode():
        ui.emit_json(ui.json_response(True, data, next_commands=[
            f"market intel brief --country {cc or 'PE'}",
            f"market intel inflation --country {cc or 'PE'}",
            f"market intel scores --country {cc or 'PE'}",
        ]), console)
        return

    headline = data.get("headline", "")
    shelf = data.get("shelf", {})
    macro_gap = data.get("macro_gap", {})
    confidence = data.get("confidence", {})
    scores = data.get("scores", {})
    sources = data.get("sources", [])
    disclaimer = data.get("disclaimer", "")

    # ── Headline panel ───────────────────────────────────────────────────────
    console.print()
    console.print(Panel.fit(
        f"[bold white]{headline}[/]",
        title=f"[bold #3cffd0]CLI Market Intel Brief — {scope}[/]",
        subtitle=f"[dim]{days}d window[/]",
        border_style="#3cffd0",
    ))

    # ── Shelf signals ────────────────────────────────────────────────────────
    shelf_labels = {
        "shelf_inflation_avg_pct": ("RPV 7d (góndola)" if not is_en else "RPV 7d (shelf)", "%"),
        "staple_momentum_7d_pct": ("Momentum básicos 7d" if not is_en else "Staple momentum 7d", "%"),
        "promo_intensity": ("Intensidad promo (≥3%)" if not is_en else "Promo intensity (≥3%)", ""),
        "price_dispersion": ("Dispersión CV" if not is_en else "Price dispersion (CV)", ""),
        "basket_stress_index": ("Índice estrés canasta (BSI)" if not is_en else "Basket stress index (BSI)", ""),
    }
    if shelf:
        t_shelf = Table(
            title="[bold white]" + ("Señales de góndola" if not is_en else "Shelf signals") + "[/]",
            border_style=ui.TABLE_BORDER,
        )
        t_shelf.add_column("Señal" if not is_en else "Signal", max_width=30)
        t_shelf.add_column("Valor" if not is_en else "Value", justify="right")
        for key, val in shelf.items():
            label, unit = shelf_labels.get(key, (key, ""))
            if isinstance(val, float):
                color = "#FF6B35" if val > 0 else "#00FF88"
                fmt = f"[{color}]{val:+.2f}{unit}[/]" if unit == "%" else f"{val:.2f}"
            else:
                fmt = str(val)
            t_shelf.add_row(label, fmt)
        if macro_gap:
            gap = macro_gap.get("collector_vs_official_gap_pp")
            if gap is not None:
                color = "#FF6B35" if gap > 0 else "#00FF88"
                t_shelf.add_row(
                    "Gap vs CPI alimentos (anexo)" if not is_en else "Gap vs food CPI (appendix)",
                    f"[{color}]{gap:+.1f} pp[/]",
                )
        console.print()
        console.print(t_shelf)

    # ── Scores ───────────────────────────────────────────────────────────────
    if scores:
        t_scores = Table(
            title="[bold white]" + ("Scores compuestos" if not is_en else "Composite scores") + "[/]",
            border_style=ui.TABLE_BORDER,
        )
        t_scores.add_column("Score", max_width=26)
        t_scores.add_column("Valor" if not is_en else "Value", justify="center", width=8)
        t_scores.add_column("Label" if is_en else "Nivel", max_width=12)
        for name, sc in list(scores.items())[:8]:
            val = sc.get("score")
            label = sc.get("label", "")
            if sc.get("confidence") == "low":
                label = f"[dim]⚠ {label}[/]"
            if val is not None:
                color = "#FF6B35" if float(val) > 60 else "#00FF88"
                t_scores.add_row(name.replace("_", " "), f"[{color}]{val:.0f}[/]", label)
        console.print()
        console.print(t_scores)

    # ── Confidence + sources ─────────────────────────────────────────────────
    freshness = confidence.get("moat_freshness_pct")
    stores = confidence.get("stores_active")
    meta_parts = []
    if freshness is not None:
        meta_parts.append(f"freshness {freshness:.0f}%")
    if stores is not None:
        meta_parts.append(f"{stores} stores")
    if sources:
        meta_parts.append("sources: " + ", ".join(sources))
    if meta_parts:
        console.print(f"\n[dim]{' · '.join(meta_parts)}[/]")
    if disclaimer:
        console.print(f"[dim]{disclaimer}[/]")

    ui.print_intel_footer(console, [
        f"market intel brief --country {cc or 'PE'} --days 14",
        f"market intel inflation --country {cc or 'PE'}",
        f"market intel scores --country {cc or 'PE'}",
    ])


def cmd_enrichment(args):
    cc = args.country or "PE"
    if args.refresh:
        with console.status(f"[cyan]Refrescando enriquecimiento — {cc}..."):
            refresh_data = cli_api("POST", f"/v1/intel/enrichment/refresh?country={cc}")
        if getattr(args, "json", False) or ui.is_json_mode():
            ui.emit_json(ui.json_response(True, refresh_data, next_commands=[f"market intel enrichment -c {cc}"]), console)
            return
        console.print(
            f"[#3cffd0]✓ Enriquecimiento actualizado — "
            f"written={refresh_data.get('enrichment_written', 0)} · {cc}[/]"
        )

    with console.status(f"[cyan]Cargando enriquecimiento — {cc}..."):
        data = cli_api("GET", f"/v1/intel/enrichment?country={cc}")
    items = data.get("indicators", [])
    if getattr(args, "json", False) or ui.is_json_mode():
        ui.emit_json(ui.json_response(True, data, next_commands=[f"market intel enrichment -c {cc}"]), console)
        if not items:
            sys.exit(2)
        return

    if not items:
        msg = (
            f"Sin datos aún para {cc}. Corré: market intel enrichment -c {cc}"
            if not ui.is_en()
            else f"No data yet for {cc}. Run: market intel enrichment -c {cc}"
        )
        console.print(f"[yellow]{msg}[/]")
        sys.exit(2)

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
        [f"market intel enrichment -c {cc}", f"market intel scores -c {cc}", f"market intel indicators -c {cc}"],
    )




def cmd_tools(args):
    """Catálogo MCP por bundle — misma superficie que market-mcp tools/list."""
    profile = getattr(args, "profile", None) or "default"
    try:
        from market_core.market_mcp_registry import list_tools
    except Exception as e:
        if getattr(args, "json", False) or ui.is_json_mode():
            ui.emit_json(ui.json_response(False, error=f"MCP tools unavailable: {e}"), console)
            return
        console.print("[yellow]MCP tools catalog not available in this build.[/]")
        return

    tools = list_tools(profile)
    mcp_default, mcp_legacy = _mcp_profile_counts()
    if getattr(args, "json", False) or ui.is_json_mode():
        ui.emit_json(
            ui.json_response(
                True,
                {
                    "profile": profile,
                    "tools": tools,
                    "total": len(tools),
                    "default_total": mcp_default,
                    "legacy_total": mcp_legacy,
                    "bundles": {
                        key: names
                        for key, _, _, names in ui.mcp_tool_groups(profile)
                    },
                },
                next_commands=["market tools", "market tools --profile legacy", "market hello"],
            ),
            console,
        )
        return

    profile_note = (
        f"perfil {profile} · {len(tools)} tools"
        if not ui.is_en()
        else f"profile {profile} · {len(tools)} tools"
    )
    ui.print_section_header(
        console,
        "MCP Tools" if ui.is_en() else "Herramientas MCP",
        subtitle=(
            "Shop · Intel · Account — market-mcp (MCP_TOOL_PROFILE=default)"
            if ui.is_en()
            else "Shop · Intel · Account — market-mcp (MCP_TOOL_PROFILE=default)"
        ),
        meta=f"{profile_note} · legacy {mcp_legacy} · cli-market.dev/tools",
    )
    ui.print_mcp_tools_catalog(console, profile=profile)
    ui.print_intel_footer(
        console,
        [
            "market tools --profile legacy",
            "market init",
            "market doctor",
        ],
    )


def cmd_mcp(args):
    """Read-only MCP center: doctor health + tool registry."""
    profile = getattr(args, "profile", None) or "default"
    checks, ok = _collect_doctor_checks()
    pct, summary = ui.readiness_score(checks)

    try:
        from market_core.market_mcp_registry import list_tools
    except Exception as e:
        if getattr(args, "json", False) or ui.is_json_mode():
            ui.emit_json(ui.json_response(False, error=f"MCP tools unavailable: {e}"), console)
            sys.exit(1)
        console.print("[yellow]MCP tools catalog not available in this build.[/]")
        sys.exit(1)

    tools = list_tools(profile)
    mcp_default, mcp_legacy = _mcp_profile_counts()

    if getattr(args, "json", False) or ui.is_json_mode():
        ui.emit_json(
            ui.json_response(
                ok,
                {
                    "profile": profile,
                    "tools": tools,
                    "total": len(tools),
                    "default_total": mcp_default,
                    "legacy_total": mcp_legacy,
                    "readiness_pct": pct,
                    "readiness_summary": summary,
                    "checks": [{"name": n, "detail": d, "status": s} for n, d, s in checks],
                },
                next_commands=["market mcp-setup", "market doctor", "market tools"],
            ),
            console,
        )
        sys.exit(0 if ok else 1)

    ui.print_mcp_center(
        console,
        profile=profile,
        tools=tools,
        checks=checks,
        readiness_pct=pct,
        readiness_summary=summary,
        ok=ok,
    )


def cmd_alerts(args):
    if args.action == "list":
        data = cli_api("GET", "/v1/alerts")
        alerts_list = data.get("alerts", [])
        if getattr(args, "json", False) or ui.is_json_mode():
            ui.emit_json(ui.json_response(True, {"alerts": alerts_list}, next_commands=["market alerts", "market whoami"]), console)
            return
        if not alerts_list:
            console.print("[yellow]No hay alertas configuradas.[/]")
            return
        for a in alerts_list:
            product = a.get("product_query") or a.get("product") or "?"
            condition = a.get("condition") or "?"
            threshold = a.get("threshold_pct", "?")
            console.print(f"  [{a.get('id', '?')}] {product} | {condition} | threshold: {threshold}%")
    else:
        tier = ui.fetch_tier()
        ui.tier_gate(console, "alerts_create", tier, json_args=args)
        if not args.product:
            console.print("[red]Indica --product para crear una alerta.[/]")
            return
        email = getattr(args, "email", None) or ""
        if not email:
            try:
                prefs = cli_api("GET", "/auth/subscription")
                email = (prefs.get("email") or "").strip()
            except Exception:
                email = ""
        if not email:
            console.print("[red]Indica --email para recibir notificaciones de la alerta.[/]")
            return
        condition = getattr(args, "condition", None) or "price_drop"
        data = cli_api(
            "POST",
            "/v1/alerts",
            {
                "condition": condition,
                "product_query": args.product,
                "threshold_pct": args.threshold,
                "notify_email": email,
            },
        )
        if getattr(args, "json", False) or ui.is_json_mode():
            ui.emit_json(ui.json_response(True, {"created": data}, next_commands=["market alerts --action list"]), console)
            return
        alert = data.get("alert", {})
        console.print(f"[#3cffd0]✓ Alerta creada: {alert.get('id', '?')} — {args.product}[/]")

def cmd_about(args):
    mcp_default, mcp_legacy = _mcp_profile_counts()
    about_text = (
        "[bold #00FF88]CLI Market[/] — Infraestructura de comercio para agentes IA.\n\n"
        f"[#888888]Un solo pip install. Una API. {RETAILERS_VERIFIED} retailers en {MS_COUNTRIES} países. "
        f"{mcp_default} MCP tools ({mcp_legacy} legacy).[/]\n"
        "[#888888]Comparación de precios cross-border. Data moat con precios reales.[/]\n"
        "[#888888]MIT · Gratis para developers.[/]\n\n"
    )
    if getattr(args, "json", False) or ui.is_json_mode():
        ui.emit_json(ui.json_response(True, {
            "name": "CLI Market",
            "description": "Agent-native commerce infrastructure for AI agents",
            "retailers": RETAILERS_VERIFIED,
            "countries": MS_COUNTRIES,
            "mcp_tools": mcp_default,
            "mcp_tools_legacy": mcp_legacy,
            "license": "MIT",
            "website": "https://cli-market.dev"
        }, next_commands=["market hello", "market tools"]), console)
        return
    console.print(Panel.fit(
        about_text + "\n[dim]cli-market.dev · pypi.org/project/cli-market-world[/]",
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
    elif tier == "starter":
        console.print("[dim]Dashboard: market account  ·  Upgrade: market upgrade[/]")


def cmd_register(args):
    """Create a free account via POST /auth/register + /auth/verify-email (2-step OTP)."""
    ref_code = getattr(args, "ref", None)
    es = not ui.is_en()

    # ── Step 1: collect email (required) ──────────────────────────────────
    email = (getattr(args, "email", None) or "").strip().lower() or None
    if not email and not getattr(args, "json", False) and sys.stdin.isatty():
        prompt = (
            "Email (requerido para verificación): "
            if es
            else "Email (required for verification): "
        )
        try:
            raw = input(prompt).strip()
            if raw and "@" in raw:
                email = raw.lower()
        except (EOFError, KeyboardInterrupt):
            pass
    if not email or "@" not in email:
        msg = "Email es requerido para registrarse." if es else "Email is required to register."
        if getattr(args, "json", False):
            ui.json_exit(console, False, error=msg, next_commands=["market register --email you@example.com"])
        console.print(f"[red]{msg}[/]")
        sys.exit(1)

    body: dict = {"email": email}
    if ref_code:
        body["ref_code"] = ref_code

    with ui.run_with_status(console, "Enviando código..." if es else "Sending verification code..."):
        data = api("POST", "/auth/register", body)
    if isinstance(data, dict) and data.get("error"):
        if getattr(args, "json", False):
            ui.json_exit(console, False, error=data["error"], next_commands=ui.error_next_commands(None, data["error"]))
        ui.print_actionable_error(console, data["error"])
        ui.print_hints(console, ui.error_next_commands(None, data["error"]))
        sys.exit(1)

    # ── Step 2: prompt for OTP code ───────────────────────────────────────
    masked_email = data.get("email", email)
    email_sent = data.get("email_sent", True)  # legacy backends may omit this field
    if not getattr(args, "json", False):
        if email_sent:
            console.print(
                f"\n[bold #00FF88]Código enviado a {masked_email}[/]\n"
                "[dim]Revisa tu bandeja de entrada (y spam).[/]\n"
            )
        else:
            console.print(
                f"\n[bold #FF6B35]No se pudo enviar el correo a {masked_email}.[/]\n"
                "[dim]El servidor generó el código pero el envío de email falló "
                "(SMTP no configurado o error del proveedor) — no va a llegar ningún correo. "
                "Contacta a soporte o reintenta más tarde.[/]\n"
            )

    code: str = (getattr(args, "code", None) or "").strip()
    if not code and not getattr(args, "json", False):
        prompt_code = "Código de verificación: " if es else "Verification code: "
        try:
            code = input(prompt_code).strip()
        except (EOFError, KeyboardInterrupt):
            console.print("\n[yellow]Registro cancelado.[/]" if es else "\n[yellow]Registration cancelled.[/]")
            sys.exit(1)

    if not code:
        msg = "Código requerido." if es else "Verification code required."
        if getattr(args, "json", False):
            ui.json_exit(console, False, error=msg, next_commands=[])
        console.print(f"[red]{msg}[/]")
        sys.exit(1)

    with ui.run_with_status(console, "Verificando..." if es else "Verifying..."):
        verify_data = api("POST", "/auth/verify-email", {"email": email, "code": code})
    if isinstance(verify_data, dict) and verify_data.get("error"):
        if getattr(args, "json", False):
            ui.json_exit(console, False, error=verify_data["error"], next_commands=["market register"])
        ui.print_actionable_error(console, verify_data["error"])
        sys.exit(1)

    # ── Success ───────────────────────────────────────────────────────────
    if getattr(args, "json", False):
        ui.emit_json(ui.json_response(True, verify_data, next_commands=[
            'market search "leche" --country PE', "market whoami", "market doctor",
        ]), console)
        return
    key = verify_data.get("api_key", "")
    next_steps = verify_data.get("next_steps") or []
    steps_text = ""
    if next_steps:
        en = ui.is_en()
        label = "Next steps:" if en else "Próximos pasos:"
        steps_text = f"\n[bold]{label}[/]\n"
        for i, step in enumerate(next_steps, 1):
            steps_text += f"  {i}. [cyan]{step.get('command', '')}[/]  {step.get('description', '')}\n"
    console.print(Panel.fit(
        f"[bold #00FF88]Email verificado — cuenta creada[/]\n\n"
        f"Usuario: [cyan]{verify_data.get('username', '?')}[/]\n"
        f"Email: [cyan]{email}[/]\n"
        f"API key: [bold white]{key}[/]\n\n"
        "[yellow]Guardala ahora — no se vuelve a mostrar.[/]\n"
        f"MCP (claude.ai): [cyan]{API}/mcp?token={key}[/]"
        + steps_text,
        title="CLI Market",
        border_style="#00FF88",
    ))
    ui.print_hints(console, ['market search "leche" --country PE', "market whoami", "market init"])
    if not getattr(args, "skip_search", False):
        _run_activation_search()


def _collect_doctor_checks() -> tuple[list[tuple[str, str, str]], bool]:
    """Pure function to collect doctor checks (no prints, no exit, no status). For reuse in init --json and doctor."""
    import shutil
    import httpx

    checks: list[tuple[str, str, str]] = []
    ok = True

    env_url = os.environ.get("MARKET_API_URL")
    checks.append(("API URL", API, "ok" if env_url else "default (production)"))

    try:
        resp = httpx.get(f"{API}/health/db", timeout=10)
        if resp.status_code == 200:
            body = resp.json()
            if body.get("backend") == "error":
                # /health/db returns HTTP 200 even when the DB connection
                # itself failed — the real diagnosis is in "detail".
                checks.append(("API health", body.get("detail", "unknown error")[:80], "fail"))
                ok = False
            else:
                snaps = body.get("snapshots", "?")
                snaps_display = f"{snaps:,}" if isinstance(snaps, int) else str(snaps)
                checks.append(("API health", f"200 OK - {snaps_display} snapshots", "ok"))
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
        try:
            who = api("GET", "/auth/whoami")
            if who.get("error"):
                checks.append(("Auth", who["error"], "warn"))
            else:
                checks.append(("Auth", who.get("username", "?"), "ok"))
                sub = api("GET", "/auth/subscription")
                tier = (sub.get("subscription") or {}).get("tier", "?")
                checks.append(("Tier", tier, "ok"))
        except Exception as e:
            checks.append(("Auth", str(e)[:60], "warn"))
    else:
        checks.append(("Auth", "no token", "warn"))

    checks.append(("País", ui.get_default_country(), "ok"))
    checks.append(("Countries", str(len(COUNTRIES)), "ok"))

    try:
        src = httpx.get(f"{API}/v1/sources/health", timeout=15)
        if src.status_code == 200:
            body = src.json()
            if body.get("error"):
                checks.append(("Sources health", body["error"], "warn"))
            else:
                sm = body.get("summary") or {}
                checks.append((
                    "Sources health",
                    f"{sm.get('ok', 0)} ok · {sm.get('partial', 0)} partial · {sm.get('dead', 0)} dead",
                    "ok" if int(sm.get("dead", 0) or 0) == 0 else "warn",
                ))
        else:
            checks.append(("Sources health", f"HTTP {src.status_code}", "warn"))
    except Exception as exc:
        checks.append(("Sources health", str(exc)[:60], "warn"))

    try:
        stats = httpx.get(f"{API}/health/stats", timeout=15)
        if stats.status_code == 200:
            body = stats.json()
            if body.get("error"):
                # /health/stats also returns HTTP 200 on a backend failure
                # (DB down, stats build raised) — don't read that as "no data".
                checks.append(("Golden linkage", str(body["error"])[:60], "warn"))
            else:
                linkage = body.get("golden_linkage_pct", body.get("linkage_pct"))
                if linkage is not None:
                    pct = float(linkage)
                    checks.append((
                        "Golden linkage",
                        f"{pct:.1f}%",
                        "ok" if pct >= 50 else "warn",
                    ))
                else:
                    checks.append(("Golden linkage", "no data", "warn"))
        else:
            checks.append(("Golden linkage", f"HTTP {stats.status_code}", "warn"))
    except Exception as exc:
        checks.append(("Golden linkage", str(exc)[:60], "warn"))

    mcp_bin = shutil.which("market-mcp")
    checks.append(("market-mcp", mcp_bin or "not in PATH", "ok" if mcp_bin else "warn"))
    checks.append(("MCP snippet", "cli-market.dev/tools", "ok"))

    return checks, ok


def cmd_doctor(args):
    """Check API URL, connectivity, auth, tier, MCP, readiness score."""
    en = ui.is_en()
    checks, ok = _collect_doctor_checks()
    pct, summary = ui.readiness_score(checks)

    if getattr(args, "json", False) or ui.is_json_mode():
        ui.emit_json(ui.json_response(ok, {
            "readiness_pct": pct,
            "readiness_summary": summary,
            "checks": [{"name": n, "detail": d, "status": s} for n, d, s in checks],
        }, next_commands=["market init", "market register", "market hello"]), console)
        sys.exit(0 if ok else 1)

    # Human output
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
    token = get_token()
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







def _init_data(en: bool, api_ok: bool, account_created: bool, search_done: bool, tier: str | None = None, username: str | None = None) -> dict:
    """Structured data for `market init --json` (agent-friendly onboarding summary)."""
    return {
        "command": "init",
        "version": PACKAGE_VERSION,
        "lang": "en" if en else "es",
        "steps": [
            "API" if en else "API",
            "Auth" if en else "Cuenta",
            "Readiness" if en else "Preparacion",
            "First search" if en else "Primera busqueda",
            "MCP" if en else "MCP",
        ],
        "api_health": {"ok": api_ok},
        "auth": {
            "account_created": account_created,
            "session_exists": not account_created,
            "tier": tier,
            "username": username,
        },
        "first_search_performed": search_done,
        "mcp": ui.get_mcp_config(),
        "next_steps": ["market search", "market whoami", "market doctor", "market tools"],
    }


def cmd_init(args):
    """Full onboarding: API, auth, readiness, first search, MCP snippet."""
    en = ui.is_en()
    is_json = ui.is_json_mode() or getattr(args, "json", False)

    steps = [
        "API" if en else "API",
        "Auth" if en else "Cuenta",
        "Readiness" if en else "Preparacion",
        "First search" if en else "Primera busqueda",
        "MCP" if en else "MCP",
    ]

    if not is_json:
        console.print()
        console.print(Panel(
            f"[bold]{'Zero-to-hero onboarding' if en else 'Onboarding completo'}[/]\n"
            f"[dim]{'Steps' if en else 'Pasos'}:[/] {' -> '.join(steps)}",
            border_style=ui.MINT,
            box=box.DOUBLE_EDGE,
        ))

    api_ok = False
    if not is_json:
        with ui.run_with_status(console, steps[0] + "..."):
            import httpx
            try:
                resp = httpx.get(f"{API}/health/db", timeout=10)
                resp.raise_for_status()
                body = resp.json()
                # /health/db returns HTTP 200 even when the DB connection
                # itself failed — a 2xx status alone doesn't mean "healthy".
                if body.get("backend") == "error":
                    raise RuntimeError(body.get("detail", "DB connection failed"))
                console.print(f"[{ui.MINT}]OK[/] API")
                api_ok = True
            except Exception as exc:
                ui.print_actionable_error(console, str(exc))
                sys.exit(1)
    else:
        import httpx
        try:
            resp = httpx.get(f"{API}/health/db", timeout=10)
            resp.raise_for_status()
            body = resp.json()
            if body.get("backend") == "error":
                raise RuntimeError(body.get("detail", "DB connection failed"))
            api_ok = True
        except Exception as exc:
            ui.json_exit(console, False, error=str(exc), status=500)

    account_created = False
    tier = None
    username = None
    if not get_token():
        if not is_json:
            console.print(f"[dim]{'Creating free account...' if en else 'Creando cuenta gratuita...'}[/]")
        # Always call register without json when inside init --json, to guarantee SINGLE final payload from init.
        # We collect the resulting auth info afterwards.
        reg_args = argparse.Namespace(
            json=False,
            skip_search=True,
            ref=getattr(args, "ref", None),
            email=None,
            code=None,
        )
        cmd_register(reg_args)
        account_created = True
    else:
        if not is_json:
            console.print(f"[{ui.MINT}]OK[/] Auth (session exists)")

    # Collect auth info (after possible register in this run)
    tier = None
    username = None
    try:
        if get_token():
            sub = api("GET", "/auth/subscription")
            tier = (sub.get("subscription") or {}).get("tier")
            username = sub.get("username")
    except Exception:
        pass

    # For JSON init: force sub-calls to non-JSON to ensure SINGLE clean payload at the end.
    # Collect doctor data using the pure helper.
    search_done = _run_activation_search(
        skip=getattr(args, "skip_search", False) or is_json
    )

    doctor_checks = []
    doctor_ok = True
    doctor_pct = 0
    doctor_summary = ""
    if is_json:
        # Register was called with json=is_json above — it may have emitted, but for composite we prioritize final init payload.
        # To get clean single output, re-collect doctor purely.
        doctor_checks, doctor_ok = _collect_doctor_checks()
        doctor_pct, doctor_summary = ui.readiness_score(doctor_checks)
    else:
        # Human: let doctor print its nice table + readiness
        cmd_doctor(argparse.Namespace(json=False))

    try:
        from market_funnel import record_funnel_event

        if username:
            record_funnel_event(
                "onboarding_complete",
                username=username,
                meta={"source": "market_init", "search_done": bool(search_done)},
                dedupe=True,
            )
    except Exception:
        pass

    if is_json:
        data = _init_data(en, api_ok, account_created, bool(search_done), tier, username)
        data["doctor"] = {
            "readiness_pct": doctor_pct,
            "readiness_summary": doctor_summary,
            "checks": [{"name": n, "detail": d, "status": s} for n, d, s in doctor_checks],
            "ok": doctor_ok,
        }
        # Include a copy of the final mcp for convenience
        data["mcp"] = ui.get_mcp_config()
        try:
            mcp_written = _write_mcp_config(_detect_ide())
            data["mcp_config_path"] = mcp_written["cfg_path"]
        except Exception:
            data["mcp_config_path"] = None
        ui.emit_json(
            ui.json_response(
                doctor_ok and api_ok,
                data,
                next_commands=["market search", "market whoami", "market doctor", "market tools"],
            ),
            console,
        )
        return

    # Human path only (JSON path returned earlier)
    try:
        mcp_written = _write_mcp_config(_detect_ide())
        scope = "proyecto" if mcp_written["project_level"] else "global"
        restart_hint = "restart Cursor/VS Code" if en else "reinicia Cursor/VS Code"
        console.print(
            f"[{ui.MINT}]OK[/] MCP ({scope}): [cyan]{mcp_written['cfg_path']}[/] "
            f"[dim]— {restart_hint}[/]"
        )
    except Exception:
        ui.mcp_snippet_panel(console)
    ui.print_hints(console, [
        'market compare "leche" --country PE',
        "market shell",
        "market hello",
    ])
    console.print(f"{ui.PROMPT} [dim]{'ready' if en else 'listo'}[/][bold #00FF88]_[/]")


def _shell_parse_investigate(rest: list[str]) -> argparse.Namespace:
    ns = argparse.Namespace(
        query="",
        country=None,
        line=None,
        no_intel=False,
        days=30,
        json=False,
    )
    i = 0
    while i < len(rest):
        tok = rest[i]
        if tok in ("--country", "-c") and i + 1 < len(rest):
            ns.country = rest[i + 1]
            i += 2
        elif tok == "--no-intel":
            ns.no_intel = True
            i += 1
        elif tok == "--days" and i + 1 < len(rest):
            ns.days = int(rest[i + 1])
            i += 2
        elif tok == "--line" and i + 1 < len(rest):
            ns.line = rest[i + 1]
            i += 2
        elif not tok.startswith("-") and not ns.query:
            ns.query = tok
            i += 1
        else:
            i += 1
    return ns


def _shell_mission_help(console: Console) -> None:
    en = ui.is_en()
    if en:
        console.print(
            "[cyan]investigate QUERY[/]  [cyan]compare QUERY[/]  [cyan]intel inflation[/]  "
            "[cyan]doctor[/]  [cyan]mcp[/]  [cyan]whoami[/]  [cyan]search QUERY[/]  "
            "[cyan]hello[/]  [cyan]exit[/]"
        )
    else:
        console.print(
            "[cyan]investigate QUERY[/]  [cyan]compare QUERY[/]  [cyan]intel inflation[/]  "
            "[cyan]doctor[/]  [cyan]mcp[/]  [cyan]whoami[/]  [cyan]search QUERY[/]  "
            "[cyan]hello[/]  [cyan]exit[/]"
        )


def cmd_shell(args):
    """Interactive REPL — agent-style session."""
    import shlex
    en = ui.is_en()
    tier = ui.fetch_tier()
    ctx = ui.fetch_session_context()
    username = (ctx or {}).get("username")
    missions = _missions_enabled()

    if missions:
        observatory = ui.fetch_observatory_public()
        ui.print_mission_control(
            console,
            tier=tier,
            observatory=observatory,
            username=username,
        )
    else:
        _render_splash(en, ctx)

    while True:
        try:
            line = console.input(f"{ui.PROMPT} ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print()
            break
        if not line or line.lower() in ("exit", "quit", "q"):
            break
        if line.lower() == "help":
            if missions:
                _shell_mission_help(console)
            else:
                console.print(
                    "[bold]Búsqueda:[/]  [cyan]search QUERY[/]  [cyan]compare QUERY[/]  [cyan]basket item:qty ...[/]  [cyan]optimize item:qty ...[/]\n"
                    "[bold]Carrito:[/]   [cyan]add ID[/]  [cyan]cart[/]  [cyan]cart-remove ID[/]  [cyan]cart-clear[/]  [cyan]checkout[/]\n"
                    "[bold]Pedidos:[/]   [cyan]orders[/]  [cyan]reorder[/]  [cyan]ask PROMPT[/]\n"
                    "[bold]Datos:[/]     [cyan]brief[/]  [cyan]inflation[/]  [cyan]indicators[/]  [cyan]scores[/]  [cyan]enrichment[/]\n"
                    "[bold]Catálogo:[/]  [cyan]discover[/]  [cyan]categories[/]  [cyan]barcode CODE[/]  [cyan]enrich ID[/]\n"
                    "[bold]Alertas:[/]   [cyan]alerts list[/]  [cyan]alerts create --product X[/]\n"
                    "[bold]Cuenta:[/]    [cyan]whoami[/]  [cyan]account[/]  [cyan]preferences[/]  [cyan]upgrade[/]  [cyan]share[/]\n"
                    "[bold]Setup:[/]     [cyan]init[/]  [cyan]register[/]  [cyan]login USER PASS[/]  [cyan]doctor[/]  [cyan]lang CODE[/]\n"
                    "[bold]MCP:[/]       [cyan]tools[/]  [cyan]mcp-setup[/]  [cyan]demo[/]  [cyan]tutorial[/]\n"
                    "[dim]exit / quit / q → salir[/]"
                )
            continue
        try:
            tokens = shlex.split(line)
        except ValueError as exc:
            console.print(f"[red]{exc}[/]")
            continue
        if not tokens:
            continue

        cmd = tokens[0]
        rest = tokens[1:]
        if len(tokens) >= 2 and tokens[0] == "intel":
            cmd = tokens[1]
            rest = tokens[2:]

        ns = argparse.Namespace(
            command=cmd,
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
            profile="default",
            no_intel=False,
            days=30,
            quantity=1,
            catalog=False,
            condition="price_drop",
            plan=None,
            promo_code=None,
            demo=False,
            ide=None,
            dry_run=False,
            tco=False,
            no_delivery=False,
            action_links=False,
            budget=None,
            no_tco=False,
            no_substitutes=False,
        )
        handlers = {
            "login": cmd_login,
            "search": cmd_search,
            "compare": cmd_compare,
            "add": cmd_add,
            "cart": cmd_cart,
            "cart-remove": cmd_cart_remove,
            "cart-update": cmd_cart_update,
            "cart-clear": cmd_cart_clear,
            "clear-cart": cmd_cart_clear,
            "checkout": cmd_checkout,
            "orders": cmd_orders,
            "reorder": cmd_reorder,
            "ask": cmd_ask,
            "preferences": cmd_preferences,
            "account": cmd_account,
            "whoami": cmd_whoami,
            "doctor": cmd_doctor,
            "hello": cmd_hello,
            "register": cmd_register,
            "init": cmd_init,
            "countries": cmd_countries,
            "lines": cmd_lines,
            "discover": cmd_discover,
            "categories": cmd_categories,
            "barcode": cmd_barcode,
            "enrich": cmd_enrich,
            "basket": cmd_basket,
            "optimize": cmd_optimize,
            "indicators": cmd_indicators,
            "enrichment": cmd_enrichment,
            "scores": cmd_scores,
            "brief": cmd_intel_brief,
            "intel-brief": cmd_intel_brief,
            "tools": cmd_tools,
            "alerts": cmd_alerts,
            "lang": cmd_lang,
            "share": cmd_share,
            "upgrade": cmd_upgrade,
            "demo": cmd_demo,
            "tutorial": cmd_tutorial,
            "mcp-setup": cmd_mcp_setup,
            "about": cmd_about,
        }
        if missions:
            handlers.update({
                "investigate": cmd_investigate,
                "mcp": cmd_mcp,
                "inflation": cmd_inflation,
            })

        if cmd not in handlers:
            console.print(f"[yellow]{'Unknown' if en else 'Desconocido'}: {cmd}[/]")
            continue

        # ── Argument parsing per command ───────────────────────────────────
        if cmd == "investigate":
            inv = _shell_parse_investigate(rest)
            ns.query = inv.query
            ns.country = inv.country
            ns.line = inv.line
            ns.no_intel = inv.no_intel
            ns.days = inv.days
        elif cmd in ("search", "compare") and rest:
            pos = [t for t in rest if not t.startswith("-")]
            ns.query = pos[0] if pos else ""
            for i, tok in enumerate(rest):
                if tok in ("--country", "-c") and i + 1 < len(rest):
                    ns.country = rest[i + 1]
                elif tok in ("--store", "-s") and i + 1 < len(rest):
                    ns.store = rest[i + 1]
                elif tok in ("--limit", "-n") and i + 1 < len(rest):
                    try:
                        ns.limit = int(rest[i + 1])
                    except ValueError:
                        pass
        elif cmd == "add" and rest:
            ns.product_id = rest[0]
            for i, tok in enumerate(rest[1:], 1):
                if tok in ("--qty", "-q") and i + 1 < len(rest):
                    try:
                        ns.qty = int(rest[i + 1])
                    except ValueError:
                        pass
        elif cmd in ("cart-remove", "enrich") and rest:
            ns.product_id = rest[0]
        elif cmd == "cart-update" and rest:
            ns.product_id = rest[0]
            ns.quantity = int(rest[1]) if len(rest) > 1 else 1
        elif cmd in ("reorder",) and rest:
            ns.order_id = rest[0]
        elif cmd == "ask" and rest:
            ns.prompt = " ".join(rest)
        elif cmd == "barcode" and rest:
            ns.code = rest[0]
        elif cmd == "basket" and rest:
            pos = [t for t in rest if not t.startswith("-")]
            ns.items = pos
            for i, tok in enumerate(rest):
                if tok in ("--country", "-c") and i + 1 < len(rest):
                    ns.country = rest[i + 1]
                elif tok == "--tco":
                    ns.tco = True
                elif tok == "--no-delivery":
                    ns.no_delivery = True
                elif tok == "--action-links":
                    ns.action_links = True
        elif cmd == "optimize" and rest:
            pos = [t for t in rest if not t.startswith("-")]
            ns.items = pos
            for i, tok in enumerate(rest):
                if tok in ("--country", "-c") and i + 1 < len(rest):
                    ns.country = rest[i + 1]
                elif tok in ("--budget", "-b") and i + 1 < len(rest):
                    try:
                        ns.budget = float(rest[i + 1])
                    except ValueError:
                        pass
                elif tok == "--payment" and i + 1 < len(rest):
                    ns.payment = rest[i + 1]
                elif tok == "--no-intel":
                    ns.no_intel = True
                elif tok == "--no-tco":
                    ns.no_tco = True
                elif tok == "--no-substitutes":
                    ns.no_substitutes = True
        elif cmd == "alerts" and rest:
            ns.action = rest[0] if rest[0] in ("list", "create") else "list"
            for i, tok in enumerate(rest):
                if tok in ("--product", "-p") and i + 1 < len(rest):
                    ns.product = rest[i + 1]
                elif tok in ("--threshold", "-t") and i + 1 < len(rest):
                    try:
                        ns.threshold = float(rest[i + 1])
                    except ValueError:
                        pass
                elif tok == "--email" and i + 1 < len(rest):
                    ns.email = rest[i + 1]
        elif cmd in ("discover", "inflation", "indicators", "enrichment", "scores",
                     "brief", "intel-brief", "basket", "optimize") and rest:
            for i, tok in enumerate(rest):
                if tok in ("--country", "-c") and i + 1 < len(rest):
                    ns.country = rest[i + 1]
                elif tok in ("--line", "-l") and i + 1 < len(rest):
                    ns.line = rest[i + 1]
                elif tok in ("--days", "-d") and i + 1 < len(rest):
                    try:
                        ns.days = int(rest[i + 1])
                    except ValueError:
                        pass
        elif cmd == "mcp":
            for i, tok in enumerate(rest):
                if tok == "--profile" and i + 1 < len(rest):
                    ns.profile = rest[i + 1]
        elif cmd == "lang" and rest:
            ns.lang_code = rest[0]
        elif cmd == "login" and len(rest) >= 2:
            ns.username, ns.password = rest[0], rest[1]
        elif cmd == "checkout" and rest:
            for i, tok in enumerate(rest):
                if tok in ("--payment", "-p") and i + 1 < len(rest):
                    ns.payment = rest[i + 1]

        try:
            handlers[cmd](ns)
        except Exception as exc:
            console.print(f"[red]{exc}[/]")


def cmd_share(args):
    """Generate referral link and register it with the backend for tracking."""
    import hashlib
    seed = get_token() or "cli-market"
    ref = hashlib.sha256(seed.encode()).hexdigest()[:8]
    url = f"https://cli-market.dev/?ref={ref}"

    stats: dict = {}
    try:
        data = cli_api("POST", "/auth/referral", {"ref_code": ref})
        installs = data.get("install_count", 0)
        activated = data.get("activated_count", 0)
        stats = {"installs": installs, "activated": activated}
    except Exception:
        pass

    try:
        sdata = cli_api("GET", "/auth/referral/stats")
        stats["total_installs"] = sdata.get("total_installs", 0)
        stats["total_activated"] = sdata.get("total_activated", 0)
    except Exception:
        pass

    if getattr(args, "json", False):
        console.print(json.dumps({"referral_url": url, "ref": ref, **stats}, indent=2))
        return

    lines = [f"[bold]Share CLI Market[/]\n\n[bold #00FF88]{url}[/]"]
    if stats:
        installs = stats.get("total_installs", stats.get("installs", 0))
        activated = stats.get("total_activated", stats.get("activated", 0))
        lines.append(f"\n[dim]📊 {installs} install{'s' if installs != 1 else ''} vía tu link · {activated} activados[/]")
    lines.append("\n[dim]Comparte el link — cada dev que instale vía tu referral queda registrado.[/]")
    console.print(Panel.fit("\n".join(lines), border_style="#00FF88"))


_TUTORIAL_UTM = "?utm_source=terminal&utm_campaign=tutorial"
_MCP_SETUP_UTM = "?utm_source=terminal&utm_campaign=mcp-setup"


def _detect_ide() -> str:
    for ide, (subdir, _) in _IDE_CONFIGS.items():
        if ide in ("claude","cursor","vscode","windsurf"): continue
        if os.path.isdir(os.path.join(os.path.expanduser("~"), subdir)): return ide
    if os.environ.get("CURSOR_TRACE_ID") or os.environ.get("CURSOR_SESSION"): return "cursor"
    if os.environ.get("WINDSURF_SESSION") or os.environ.get("CODEIUM_WINDSURF"): return "windsurf"
    if os.environ.get("TERM_PROGRAM") == "vscode": return "vscode"
    return "cursor"

def _claude_config_path() -> str:
    if sys.platform == "win32":
        base = os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Roaming")
        return os.path.join(base, "Claude", "claude_desktop_config.json")
    if sys.platform == "darwin":
        return os.path.join(
            os.path.expanduser("~"),
            "Library",
            "Application Support",
            "Claude",
            "claude_desktop_config.json",
        )
    return os.path.join(os.path.expanduser("~"), ".config", "Claude", "claude_desktop_config.json")


_IDE_CONFIGS = {
    "cursor": (".cursor", "mcpServers"),
    "windsurf": (".windsurf", "mcpServers"),
    "vscode": (".vscode", "servers"),
    "claude": (".Claude", "mcpServers"),
    "codex": (".codex", "mcpServers"),
    "devin": (".devin", "mcpServers"),
    "perplexity": (".perplexity", "mcpServers"),
    "kiro": (".kiro", "mcpServers"),
    "kilo": (".kilo", "mcpServers"),
    "antigravity": (".augment", "mcpServers"),
    "opencode": (".opencode", "mcpServers"),
    "deepseek": (".deepseek", "servers"),
    "gptlatam": (".gptlatam", "mcpServers"),
    "cline": (".cline", "mcpServers"),
    "continue": (".continue", "mcpServers"),
    "copilot": (".copilot", "mcpServers"),
    "factory": (".factory", "mcpServers"),
    "qoder": (".qoder", "mcpServers"),
    "junie": (".junie", "mcpServers"),
    "gemini": (".gemini", "mcpServers"),
}

_IDE_CONFIGS = {
    "cursor": (".cursor", "mcpServers"),
    "windsurf": (".windsurf", "mcpServers"),
    "vscode": (".vscode", "servers"),
    "claude": (".Claude", "mcpServers"),
    "codex": (".codex", "mcpServers"),
    "devin": (".devin", "mcpServers"),
    "perplexity": (".perplexity", "mcpServers"),
    "kiro": (".kiro", "mcpServers"),
    "kilo": (".kilo", "mcpServers"),
    "antigravity": (".augment", "mcpServers"),
    "opencode": (".opencode", "mcpServers"),
    "deepseek": (".deepseek", "servers"),
    "gptlatam": (".gptlatam", "mcpServers"),
    "cline": (".cline", "mcpServers"),
    "continue": (".continue", "mcpServers"),
    "copilot": (".copilot", "mcpServers"),
    "factory": (".factory", "mcpServers"),
    "qoder": (".qoder", "mcpServers"),
    "junie": (".junie", "mcpServers"),
    "gemini": (".gemini", "mcpServers"),
    "warp": (".warp", "mcpServers"),
    "qwen": (".qwen", "mcpServers"),
    "antigravity-ide": (".antigravity-ide", "mcpServers"),
    "cagent": (".cagent", "mcpServers"),
    "grok": (".grok", "mcpServers"),
    "granite": (".granite-code", "mcpServers"),
    "vibe": (".vibe", "mcpServers"),
    "pi": (".pi", "mcpServers"),
    "vscode-insiders": (".vscode-insiders", "servers"),
    "overture": (".overture", "mcpServers"),
    "securecoder": (".securecoder", "mcpServers"),
    "openclaw": (".openclaw", "mcpServers"),
}

_IDE_CONFIGS = {
    "cursor": (".cursor", "mcpServers"),
    "windsurf": (".windsurf", "mcpServers"),
    "vscode": (".vscode", "servers"),
    "claude": (".Claude", "mcpServers"),
    "codex": (".codex", "mcpServers"),
    "devin": (".devin", "mcpServers"),
    "perplexity": (".perplexity", "mcpServers"),
    "kiro": (".kiro", "mcpServers"),
    "kilo": (".kilo", "mcpServers"),
    "antigravity": (".augment", "mcpServers"),
    "opencode": (".opencode", "mcpServers"),
    "deepseek": (".deepseek", "servers"),
    "gptlatam": (".gptlatam", "mcpServers"),
    "cline": (".cline", "mcpServers"),
    "continue": (".continue", "mcpServers"),
    "copilot": (".copilot", "mcpServers"),
    "factory": (".factory", "mcpServers"),
    "qoder": (".qoder", "mcpServers"),
    "junie": (".junie", "mcpServers"),
    "gemini": (".gemini", "mcpServers"),
    "warp": (".warp", "mcpServers"),
    "qwen": (".qwen", "mcpServers"),
    "antigravity-ide": (".antigravity-ide", "mcpServers"),
    "cagent": (".cagent", "mcpServers"),
    "grok": (".grok", "mcpServers"),
    "granite": (".granite-code", "mcpServers"),
    "vibe": (".vibe", "mcpServers"),
    "pi": (".pi", "mcpServers"),
    "vscode-insiders": (".vscode-insiders", "servers"),
    "overture": (".overture", "mcpServers"),
    "securecoder": (".securecoder", "mcpServers"),
    "openclaw": (".openclaw", "mcpServers"),
}

def _looks_like_project_root(path: str) -> bool:
    markers = (".git", "pyproject.toml", "package.json", "Cargo.toml", "go.mod")
    return any(os.path.exists(os.path.join(path, name)) for name in markers)


def _mcp_config_location(ide: str) -> tuple[str, str, bool]:
    """Return (config_dir, config_path, project_level)."""
    if ide == "claude":
        path = _claude_config_path()
        return os.path.dirname(path), path, False

    cwd = os.path.abspath(os.getcwd())
    home = os.path.abspath(os.path.expanduser("~"))
    subdir = _IDE_CONFIGS.get(ide, (".cursor", "mcpServers"))[0]
    filename = "mcp.json"
    project_dir = os.path.join(cwd, subdir)
    if cwd != home and (_looks_like_project_root(cwd) or os.path.isdir(project_dir)):
        return project_dir, os.path.join(project_dir, filename), True

    global_dir = os.path.join(home, subdir)
    return global_dir, os.path.join(global_dir, filename), False


def _mcp_config_key(ide: str) -> str:
    """JSON root key for MCP servers — VS Code uses ``servers``, most IDEs ``mcpServers``."""
    return _IDE_CONFIGS.get(ide, (".cursor", "mcpServers"))[1]


def _mcp_server_entry(*, token: str | None, api_url: str, ide: str = "cursor") -> dict:
    from market_agent_id import get_agent_id

    env = {"MARKET_API_URL": api_url, "MCP_TOOL_PROFILE": "default"}
    agent_id = get_agent_id()
    if agent_id:
        env["MARKET_AGENT_ID"] = agent_id
    if token:
        env["MARKET_API_TOKEN"] = token
    entry: dict = {"command": "market-mcp", "args": [], "env": env}
    # VS Code / VS Code Insiders / Deepseek: .vscode/mcp.json requires type=stdio (not HTTP /mcp URL).
    if _mcp_config_key(ide) == "servers":
        return {"type": "stdio", **entry}
    return entry


def _merge_mcp_config(cfg_path: str, ide: str, server_entry: dict) -> dict:
    servers_key = _mcp_config_key(ide)
    existing: dict = {}
    if os.path.isfile(cfg_path):
        with open(cfg_path, encoding="utf-8") as f:
            existing = json.load(f)
    merged = dict(existing)
    bucket = dict(merged.get(servers_key) or {})
    bucket["cli-market"] = server_entry
    merged[servers_key] = bucket
    return merged


def _ping_api() -> tuple[bool, str]:
    import time

    import httpx

    started = time.perf_counter()
    try:
        resp = httpx.get(f"{API}/health/db", timeout=10)
        ms = int((time.perf_counter() - started) * 1000)
        if resp.status_code == 200:
            return True, f"200 OK ({ms}ms)"
        return False, f"HTTP {resp.status_code}"
    except Exception as exc:
        return False, str(exc)[:60]


def _demo_api(method: str, path: str, token: str, json_data: dict | None = None) -> dict:
    import httpx

    headers: dict[str, str] = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    url = f"{API}{path}"
    if method == "GET":
        resp = httpx.get(url, headers=headers, timeout=30)
    else:
        resp = httpx.post(url, headers=headers, json=json_data or {}, timeout=30)
    if resp.status_code >= 400:
        detail = resp.json().get("detail", resp.text) if resp.headers.get("content-type", "").startswith("application/json") else resp.text
        return {"error": detail, "status": resp.status_code}
    return resp.json()


def cmd_demo(args):
    """Unified dev activation: demo token → search → compare (no account)."""
    country = getattr(args, "country", "PE") or "PE"
    is_en = ui.is_en()
    console.print(Panel.fit(
        "[bold]CLI Market Demo[/] — "
        + ("no account, live prices in <5 min" if is_en else "sin cuenta, precios reales en <5 min"),
        border_style="#00FF88",
    ))
    console.print("[dim]Fetching demo session...[/]" if is_en else "[dim]Obteniendo sesión demo...[/]")
    session = _demo_api("POST", "/public/demo/session", "", {})
    if session.get("error"):
        console.print(f"[red]{session['error']}[/]")
        sys.exit(1)
    token = session.get("demo_token") or ""
    if not token:
        console.print("[red]Demo session failed[/]" if is_en else "[red]No se pudo crear la sesión demo[/]")
        sys.exit(1)
    expires = session.get("expires_at", "?")
    remaining = session.get("requests_remaining", session.get("max_requests", 50))
    console.print(
        f"[green]✓[/] Demo token · expires {expires} · {remaining} requests left"
        if is_en
        else f"[green]✓[/] Token demo · expira {expires} · {remaining} requests"
    )

    query = "leche"
    console.print(f'\n[cyan]1/2[/] market search "{query}" --country {country}')
    search = _demo_api("POST", "/products/search", token, {"query": query, "limit": 5})
    if search.get("error"):
        console.print(f"[yellow]{search['error']}[/]")
        if search.get("status") != 401:
            if sys.platform == "win32":
                console.print("[dim]Tip: py -m pip install -U cli-market-world[/]")
                console.print("[dim]     market demo[/]")
            else:
                console.print("[dim]Tip: pip install -U cli-market-world && market demo[/]")
    else:
        total = search.get("total", len(search.get("results", [])))
        console.print(f"[green]✓[/] {total} results" if is_en else f"[green]✓[/] {total} resultados")
        if search.get("source_health", {}).get("summary"):
            sh = search["source_health"]["summary"]
            console.print(f"[dim]store health: ok={sh.get('ok', 0)} partial={sh.get('partial', 0)} dead={sh.get('dead', 0)}[/]")

    console.print(f'\n[cyan]2/2[/] market compare "{query}" --country {country}')
    compare = _demo_api("POST", "/products/compare", token, {"query": query, "limit": 5})
    if compare.get("error"):
        console.print(f"[yellow]{compare['error']}[/]")
    else:
        n = len(compare.get("comparison", []))
        stores = compare.get("stores_compared", "?")
        console.print(
            f"[green]✓[/] {n} products across {stores} stores"
            if is_en
            else f"[green]✓[/] {n} productos en {stores} tiendas"
        )

    if ui.is_json_mode():
        ui.emit_json(ui.json_response(True, {
            "command": "demo",
            "session": session,
            "search": search,
            "compare": compare,
            "next_commands": ["market init", "market register", "market mcp-setup --ide cursor"],
        }), console)
        return

    console.print()
    if is_en:
        console.print("[bold]Next:[/] [cyan]market init[/] — account + checkout + MCP")
        if sys.platform == "win32":
            console.print("[dim]On PowerShell: run each command on its own line.[/]")
    else:
        console.print("[bold]Siguiente:[/] [cyan]market init[/] — cuenta + checkout + MCP")
        if sys.platform == "win32":
            console.print("[dim]En PowerShell: ejecuta cada comando en su propia línea.[/]")
    console.print("[dim]Demo tokens cannot checkout. Register when you need cart/payments.[/]" if is_en else "[dim]Los tokens demo no pueden hacer checkout. Registrate para carrito y pagos.[/]")
    _report_onboarding_event("use_case_demo", meta={"flow": "market_demo", "country": country, "agent_source": "demo"})


def cmd_tutorial(args):
    """Interactive 3-step tutorial (P0 from product handoff)."""
    country = getattr(args, "country", "PE") or "PE"
    demo = getattr(args, "demo", False)
    if demo:
        console.print("[dim]Tip: `market demo` is the preferred no-account path. tutorial --demo uses offline fallbacks.[/]")
    console.print(Panel.fit(
        "[bold]CLI Market Tutorial — 3 ejercicios en 60 segundos[/]",
        border_style="#00FF88",
    ))
    console.print("\nEjercicio 1/3: Buscar")
    console.print(f'  $ market search "arroz" --country {country}')
    if demo:
        console.print("  ✓ 15 resultados. Precio mín: S/ 2.90/kg (Metro)")
    else:
        try:
            ns = argparse.Namespace(query="arroz", country=country, limit=5, page=1, json=False, store=None, line=None)
            cmd_search(ns)
            console.print("  ✓ Búsqueda completada")
        except Exception:
            console.print("  (usando demo data)")
            console.print("  ✓ 15 resultados. Precio mín: S/ 2.90/kg (Metro)")
    console.print("\nEjercicio 2/3: Comparar")
    console.print(f'  $ market compare "aceite" --country {country}')
    if demo:
        console.print("  ✓ 8 productos comparados. Spread: 12%")
    else:
        try:
            ns = argparse.Namespace(query="aceite", country=country, limit=5, json=False)
            cmd_compare(ns)
            console.print("  ✓ Comparación completada")
        except Exception:
            console.print("  (usando demo data)")
            console.print("  ✓ 8 productos comparados. Spread: 12%")
    console.print("\nEjercicio 3/3: Exportar")
    export_name = "precios-tutorial.json"
    export_path = SESSION_FILE.parent / export_name
    sample = {
        "tutorial": True,
        "country": country,
        "query": "arroz",
        "items": [{"name": "Arroz extra", "price": 2.9, "store": "metro", "currency": "PEN"}],
    }
    os.makedirs(os.path.dirname(export_path), exist_ok=True)
    with open(export_path, "w", encoding="utf-8") as f:
        json.dump(sample, f, indent=2, ensure_ascii=False)
    console.print(f"  $ market search \"arroz\" --country {country} --json > {export_name}")
    console.print(f"  ✓ Exportado a {export_path}")
    tools_url = f"https://cli-market.dev/tools{_TUTORIAL_UTM}"
    console.print("\n[bold]Tutorial completo.[/]")
    console.print("Próximo paso: `market mcp-setup --ide cursor`")
    console.print(f"[dim]Docs MCP: {tools_url}[/]")
    if not demo:
        console.print("[dim]Usa --demo para modo sin collector live.[/]")
    _report_onboarding_event(
        "tutorial_completed",
        meta={"country": country, "demo": demo, "export_path": export_path},
        dedupe=True,
    )


def _write_mcp_config(ide: str | None = None) -> dict:
    """Persist MCP server config for an IDE. Auto-detects IDE when omitted."""
    ide = ide or _detect_ide()
    token = get_token() or "sk-CLI-MARKET-PLACEHOLDER"
    api_url = os.getenv("MARKET_API_URL", API)
    cfg_dir, cfg_path, project_level = _mcp_config_location(ide)
    server_entry = _mcp_server_entry(token=token, api_url=api_url, ide=ide)
    json_key = _mcp_config_key(ide)
    cfg = _merge_mcp_config(cfg_path, ide, server_entry) if os.path.isfile(cfg_path) else (
        {json_key: {"cli-market": server_entry}}
    )
    os.makedirs(cfg_dir, exist_ok=True)
    with open(cfg_path, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
    return {
        "ide": ide,
        "cfg_dir": cfg_dir,
        "cfg_path": cfg_path,
        "project_level": project_level,
        "config": cfg,
    }


def cmd_mcp_setup(args):
    """One-liner MCP config for IDEs (P0)."""
    ide = getattr(args, "ide", None) or _detect_ide()
    dry = getattr(args, "dry_run", False)
    if dry:
        token = get_token() or "sk-CLI-MARKET-PLACEHOLDER"
        api_url = os.getenv("MARKET_API_URL", API)
        cfg_dir, cfg_path, project_level = _mcp_config_location(ide)
        server_entry = _mcp_server_entry(token=token, api_url=api_url, ide=ide)
        json_key = _mcp_config_key(ide)
        cfg = _merge_mcp_config(cfg_path, ide, server_entry) if os.path.isfile(cfg_path) else (
            {json_key: {"cli-market": server_entry}}
        )
        console.print(f"[dim]Dry-run for {ide}:[/]")
        console.print(json.dumps(cfg, indent=2))
        return

    result = _write_mcp_config(ide)
    cfg_dir = result["cfg_dir"]
    cfg_path = result["cfg_path"]
    project_level = result["project_level"]
    token = get_token() or "sk-CLI-MARKET-PLACEHOLDER"
    ping_ok, ping_detail = _ping_api()
    tool_count, _ = _mcp_profile_counts()
    scope = "proyecto" if project_level else "global"
    tools_url = f"https://cli-market.dev/tools{_MCP_SETUP_UTM}"
    token_preview = f"{token[:10]}..." if len(token) > 10 else token
    lines = [
        f"[bold]MCP Setup — {ide}[/]",
        "",
        f"✓ Directorio detectado ({scope}): {cfg_dir}",
        f"✓ Configuración escrita en: {cfg_path}",
        f"✓ Token: {token_preview}",
        f"{'✓' if ping_ok else '⚠'} Ping a API: {ping_detail}",
        "",
        f"[green]MCP config ready for {ide}. {tool_count} tools available.[/]",
        "",
        'Reiniciá el IDE y preguntale a tu agente: "Busca arroz en Perú"',
        f"[dim]{tools_url}[/]",
    ]
    console.print(Panel.fit("\n".join(lines), border_style="#00FF88"))
    _report_onboarding_event(
        "mcp_setup_completed",
        meta={"ide": ide, "project_level": project_level, "ping_ok": ping_ok},
        dedupe=True,
    )


def cmd_upgrade(args):
    """Upgrade Starter/Pro — PayPal, Mercado Pago, or Yape/Plin via MP checkout."""
    get_token_with_prompt()
    es = get_lang() == "es"
    plan = (getattr(args, "plan", None) or "pro").strip().lower().replace("-", "_")
    if plan in ("annual",):
        plan = "pro_annual"
    if plan not in ("starter", "pro", "pro_annual"):
        plan = "pro"
    payment = (getattr(args, "payment", None) or "").strip().lower()
    if not payment:
        payment = "mercadopago" if es else "paypal"
    manual = getattr(args, "resend", False) and getattr(args, "email", None) and plan == "pro"

    from market_billing import price_label_for_plan
    plan_label = price_label_for_plan(plan)

    if manual:
        email = (args.email or "").strip()
        payload = {
            "email": email,
            "lang": get_lang(),
            "resend": True,
            "payment_method": "paypal",
        }
        data = cli_api("POST", "/billing/pro-checkout", payload)
        if getattr(args, "json", False):
            ui.emit_json(ui.json_response(True, data), console)
            return
        console.print(Panel.fit(
            f"[bold #00FF88]Pro — fallback manual[/]\n{data.get('message', '')}",
            title="Upgrade",
            border_style="#00FF88",
        ))
        return

    if payment in ("yape", "plin", "mercadopago"):
        payload = {
            "payment_method": payment,
            "lang": get_lang(),
        }
        email = (getattr(args, "email", None) or "").strip()
        if email:
            payload["email"] = email
        status_msg = (
            f"Preparando pago {payment} (Mercado Pago)..."
            if es and payment in ("yape", "plin")
            else f"Preparing {payment} checkout..."
            if not es
            else "Preparando Mercado Pago..."
        )
        with ui.run_with_status(console, status_msg):
            data = cli_api("POST", "/billing/pro-checkout", payload)
        url = data.get("approve_url") or data.get("checkout_url") or ""
        if getattr(args, "json", False):
            ui.emit_json(ui.json_response(True, data, next_commands=["market whoami"]), console)
            return
        console.print(Panel.fit(
            f"[bold #00FF88]Pro — Mercado Pago[/]\n\n"
            f"{data.get('message', '')}\n\n"
            f"[cyan underline]{url}[/]\n\n"
            + (f"[dim]Paga con {payment.upper()} en Mercado Pago. Pro se activa en minutos. Luego: market whoami[/]"
               if es and payment in ("yape", "plin")
               else "[dim]Activates in minutes via webhook. Then: market whoami[/]"
               if not es
               else "[dim]Pro se activa en minutos (webhook). Luego: market whoami[/]"),
            title="Upgrade",
            border_style="#00FF88",
        ))
        ui.print_hints(console, ["market whoami", "market doctor"])
        return

    endpoint = "/billing/paypal"
    payload: dict = {"plan": plan}
    email_arg = (getattr(args, "email", None) or "").strip()
    if not email_arg and not getattr(args, "json", False) and sys.stdin.isatty():
        prompt = (
            "Email para recibir el link de pago (Enter para omitir): "
            if es
            else "Email to receive the payment link (Enter to skip): "
        )
        try:
            raw = input(prompt).strip()
            if raw and "@" in raw:
                email_arg = raw.lower()
        except (EOFError, KeyboardInterrupt):
            pass
    if email_arg:
        payload["email"] = email_arg
    label = f"CLI Market {plan.replace('_', ' ').title()} — {plan_label}"
    with ui.run_with_status(console, "Creando suscripción PayPal..." if es else "Creating PayPal subscription..."):
        data = cli_api("POST", endpoint, payload)
    url = data.get("approve_url", "")
    if getattr(args, "json", False):
        ui.emit_json(ui.json_response(True, data, next_commands=["market whoami"]), console)
        return
    console.print(Panel.fit(
        f"[bold #00FF88]CLI Market {label}[/]\n\n"
        f"{data.get('message', '')}\n\n"
        f"[cyan underline]{url}[/]\n\n"
        + ("[dim]Se activa al confirmar en PayPal. Luego: market whoami\nYape/Plin: market upgrade --payment yape[/]"
           if es else
           "[dim]Activates on PayPal confirm. Then: market whoami\nYape/Plin: market upgrade --payment yape[/]"),
        title="Upgrade",
        border_style="#00FF88",
    ))
    ui.print_hints(console, ["market whoami", "market doctor"])

# ── Main ────────────────────────────────────────────────────────────────────


def main():
    from market_agent_id import patch_core_api_agent_header

    patch_core_api_agent_header()
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.argv = _normalize_market_argv(sys.argv)
    sys.argv, _json_flag_present = _strip_json_flag(sys.argv)
    if _json_flag_present:
        ui.set_json_mode(True)
    if len(sys.argv) > 1 and sys.argv[1] in _META_CMDS:
        ns = argparse.Namespace(json="--json" in sys.argv)
        if sys.argv[1] == "about":
            return cmd_about(ns)
        return cmd_share(ns)

    parser = argparse.ArgumentParser(
        description=f"CLI Market v{PACKAGE_VERSION} — Commerce infrastructure. "
                    f"{RETAILERS_VERIFIED} verified retailers, {MS_COUNTRIES} countries.",
        usage="market <command> [options]",
    )
    parser.add_argument("--json", action="store_true", help=t("json_help"))
    parser.add_argument(
        "--version", action="version",
        version=f"cli-market-world {PACKAGE_VERSION}"
    )
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
    p.add_argument("--store", "-s", choices=list(STORES.keys()), default=None)
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default=None)
    p.add_argument("--line", choices=list(LINES.keys()), default=None)
    p.add_argument("--limit", "-l", type=int, default=10)

    # investigate
    p = sub.add_parser("investigate", help=t("investigate"))
    p.add_argument("query", nargs="?", default="")
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default=None)
    p.add_argument("--line", choices=list(LINES.keys()), default=None)
    p.add_argument("--no-intel", action="store_true", help="Skip intel inflation section")
    p.add_argument("--days", type=int, default=30, help="Intel inflation window (days)")

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

    # cart-clear / clear-cart (alias)
    sub.add_parser("cart-clear", help=t("cart_clear"))
    sub.add_parser("clear-cart", help=t("cart_clear"))

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
    p.add_argument("prompt", nargs="+")

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

    # stores
    p = sub.add_parser("stores", help=t("stores"))
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default=None)
    p.add_argument("--line", choices=list(LINES.keys()), default=None)

    # discover (combined: lines + countries — mirrors market_discover MCP tool)
    p = sub.add_parser("discover", help=t("discover"))
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default=None)
    p.add_argument("--line", choices=list(LINES.keys()), default=None)

    # whoami
    sub.add_parser("account", help="Dashboard: tier, uso y upgrade")
    sub.add_parser("whoami", help=t("whoami"))

    # register
    p = sub.add_parser("register", help=t("register"))
    p.add_argument(
        "--skip-search",
        action="store_true",
        help="Skip guided first search after account creation",
    )
    p.add_argument(
        "--ref",
        default=None,
        help="Referral code from market share (credits the referrer)",
    )
    p.add_argument(
        "--email",
        default=None,
        help="Email for account verification (required — prompted interactively if omitted)",
    )
    p.add_argument(
        "--code",
        default=None,
        help="Verification code (for non-interactive/scripted usage)",
    )

    # doctor
    sub.add_parser("doctor", help=t("doctor"))
    p = sub.add_parser("init", help=t("init"))
    p.add_argument(
        "--skip-search",
        action="store_true",
        help="Skip guided first search during onboarding",
    )
    p.add_argument(
        "--ref",
        default=None,
        help="Referral code from market share (credits the referrer)",
    )
    sub.add_parser("shell", help=t("shell"))

    # lang
    p_lang = sub.add_parser("lang", help=t("lang"))
    p_lang.add_argument("lang_code", nargs="?")

    # procure
    p = sub.add_parser("procure", help="Procurement loop: search, compare, cart, checkout")
    p.add_argument("items_list", help="Comma-separated product list, e.g. 'leche, arroz, aceite'")
    p.add_argument("--budget", "-b", type=float, required=True, help="Maximum budget in local currency")
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default=None)

    # optimize (Cost-of-Living OS compound mission)
    p = sub.add_parser("optimize", help=t("optimize"))
    p.add_argument("items", nargs="+", help="Items with optional qty, e.g. leche:2 arroz:1")
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default="PE")
    p.add_argument("--budget", "-b", type=float, default=None, help="Max budget in local currency")
    p.add_argument("--payment", choices=["yape", "plin", "paypal", "tarjeta"], default="yape")
    p.add_argument("--no-intel", action="store_true", help="Skip procurement/affordability intel")
    p.add_argument("--no-tco", action="store_true", help="Shelf price only (no delivery/payment fees)")
    p.add_argument("--no-substitutes", action="store_true", help="Do not auto-substitute products")

    # basket
    p = sub.add_parser("basket", help=t("basket"))
    p.add_argument("items", nargs="+", help="Productos con cantidad, ej: leche:2 arroz:1")
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default=None)
    p.add_argument("--line", "-l", choices=list(LINES.keys()), default=None, help="Filtrar por tipo de tienda (ej: supermercados, hogar)")
    p.add_argument("--tco", action="store_true", help="Include delivery + payment fees in totals")
    p.add_argument("--no-delivery", action="store_true", help="Exclude delivery fee from TCO")
    p.add_argument("--action-links", action="store_true", help="Attach deeplink + export list")
    p.add_argument(
        "--show-alternates", action="store_true",
        help="Show other brands/models matched per item, not just the cheapest",
    )

    # intelligence (Price Pulse / data moat — not default commerce CLI)
    p_intel = sub.add_parser("intel", help=t("intel"))
    intel_sub = p_intel.add_subparsers(dest="intel_cmd", required=True)
    _attach_intel_parsers(
        intel_sub,
        {
            "brief": t("intel_brief"),
            "inflation": t("intel_inflation"),
            "indicators": t("intel_indicators"),
            "enrichment": t("intel_enrichment"),
            "scores": t("intel_scores"),
        },
    )

    # intel-brief top-level alias (matches 'market intel-brief --country PE' used in demo GIF)
    p = sub.add_parser("intel-brief", help=t("intel_brief"))
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default=None)
    p.add_argument("--line", choices=list(LINES.keys()), default=None)
    p.add_argument("--days", type=int, default=7)
    p.add_argument("--catalog", action="store_true")

    # alerts
    p = sub.add_parser("alerts", help="Gestionar alertas de precios")
    p.add_argument("action", nargs="?", default="list", choices=["list", "create"])
    p.add_argument("--product")
    p.add_argument("--threshold", type=float, default=5.0)
    p.add_argument(
        "--condition",
        choices=["price_jump", "price_drop", "price_min_30d", "dispersion_anomaly"],
        default="price_drop",
    )
    p.add_argument("--email", help="Email para notificaciones (requerido en create si no hay en cuenta)")

    # P0 onboarding features (from handoff)
    p = sub.add_parser("tutorial", help=t("tutorial"))
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default="PE")
    p.add_argument("--demo", action="store_true", help="Run with demo data (no live collector)")

    p = sub.add_parser("demo", help=t("demo"))
    p.add_argument("--country", "-c", choices=list(COUNTRIES.keys()), default="PE")

    p = sub.add_parser("mcp-setup", help=t("mcp_setup"))
    p.add_argument(
        "--ide",
        choices=['antigravity', 'antigravity-ide', 'cagent', 'claude', 'cline', 'codex', 'continue', 'copilot', 'cursor', 'deepseek', 'devin', 'factory', 'gemini', 'gptlatam', 'granite', 'grok', 'junie', 'kilo', 'kiro', 'openclaw', 'opencode', 'overture', 'perplexity', 'pi', 'qoder', 'qwen', 'securecoder', 'vibe', 'vscode', 'vscode-insiders', 'warp', 'windsurf'],
        default=None,
        help="IDE target (auto-detect if omitted)",
    )
    p.add_argument("--dry-run", action="store_true", help="Print config without writing file")

    api_tool_count, legacy_count = _mcp_profile_counts()
    p_tools = sub.add_parser(
        "tools",
        help=f"API tools catalog ({api_tool_count} default / {legacy_count} legacy)",
    )
    p_tools.add_argument(
        "--profile",
        choices=["default", "legacy", "full"],
        default="default",
        help="Tool profile (default: curated Shop/Intel/Account)",
    )
    p_mcp = sub.add_parser("mcp", help=t("mcp"))
    p_mcp.add_argument(
        "--profile",
        choices=["default", "legacy", "full"],
        default="default",
        help="Tool profile (default: curated Shop/Intel/Account)",
    )
    sub.add_parser("hello", help=t("hello"))
    p = sub.add_parser("upgrade", help=t("upgrade"))
    p.add_argument(
        "--plan",
        choices=["starter", "pro", "pro_annual", "annual"],
        default=None,
        help="Build tier: starter ($9), pro ($49), pro_annual ($490)",
    )
    p.add_argument("--promo-code", dest="promo_code", help="Promo code")
    p.add_argument(
        "--payment",
        choices=["paypal", "mercadopago", "yape", "plin"],
        default=None,
        help="Payment method (default: Mercado Pago in es, PayPal in en)",
    )
    p.add_argument("--email", help="Email for checkout receipt (optional if registered)")
    p.add_argument("--resend", action="store_true", help="Resend payment link email (manual Pro fallback)")

    args = parser.parse_args()
    if ui.is_json_mode():
        # --json was stripped from argv above (present but in a position
        # argparse's top-level parser doesn't recognize) — force it onto the
        # namespace too, since ~half of the command handlers check
        # getattr(args, "json", False) directly without the ui.is_json_mode()
        # fallback.
        args.json = True
    else:
        ui.set_json_mode(getattr(args, "json", False))
    install_source = "hello" if not getattr(args, "command", None) or args.command == "hello" else "cli"
    _report_install_event(source=install_source)
    ui.maybe_version_notice(console)
    if not args.command:
        cmd_canasta_basica(json_mode=getattr(args, "json", False))
        return

    handlers = {
        "login": cmd_login, "search": cmd_search, "compare": cmd_compare,
        "investigate": cmd_investigate,
        "add": cmd_add, "cart": cmd_cart,
        "cart-remove": cmd_cart_remove, "cart-update": cmd_cart_update,
        "cart-clear": cmd_cart_clear, "clear-cart": cmd_cart_clear, "checkout": cmd_checkout,
        "orders": cmd_orders, "reorder": cmd_reorder,
        "ask": cmd_ask, "preferences": cmd_preferences,
        "countries": cmd_countries, "lines": cmd_lines, "stores": cmd_stores, "discover": cmd_discover,
        "categories": cmd_categories, "barcode": cmd_barcode,
        "enrich": cmd_enrich, "basket": cmd_basket, "optimize": cmd_optimize,
        "brief": cmd_intel_brief, "intel-brief": cmd_intel_brief,
        "inflation": cmd_inflation, "indicators": cmd_indicators, "enrichment": cmd_enrichment, "scores": cmd_scores,
        "tools": cmd_tools,
        "mcp": cmd_mcp,
        "alerts": cmd_alerts,
        "account": cmd_account,
        "about": cmd_about, "whoami": cmd_whoami, "register": cmd_register, "doctor": cmd_doctor, "lang": cmd_lang,
        "hello": cmd_hello, "init": cmd_init, "shell": cmd_shell, "share": cmd_share, "upgrade": cmd_upgrade,
        "demo": cmd_demo, "tutorial": cmd_tutorial, "mcp-setup": cmd_mcp_setup,
        "procure": cmd_procure,
    }
    cmd = args.command
    if cmd == "intel":
        cmd = args.intel_cmd
    handler = handlers.get(cmd)
    if handler:
        # P1 tracking: comando intentado + resultado con timing
        report_command_attempted(cmd)
        _, get_elapsed = command_timer()
        try:
            handler(args)
            report_command_result(cmd, success=True, elapsed_ms=get_elapsed())
        except SystemExit as exc:
            # sys.exit(1) desde cli_api indica error (auth, API, etc.)
            code = exc.code if isinstance(exc.code, int) else 1
            report_command_result(cmd, success=(code == 0), elapsed_ms=get_elapsed(),
                                  error_type="exit" if code != 0 else None)
            raise

if __name__ == "__main__":
    main()