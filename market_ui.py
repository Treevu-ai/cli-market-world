"""CLI Market terminal UX — theme, actionable errors, hints, tier gates, JSON envelope."""

from __future__ import annotations

import json
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Iterator

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.table import Table
from rich import box

from market_core import API, SESSION_FILE, LANG_FILE, get_token, api
from market_stats import PACKAGE_VERSION, PRICES_REFRESH_HOURS

# ── Theme (Antigravity / Codex / Claude inspired) ─────────────────────────────

MINT = "#00FF88"
WARN = "#FFD600"
TABLE_BORDER = MINT
PANEL_BORDER = MINT
PROMPT = f"[bold {MINT}]market>[/]"

PRO_TIERS = frozenset({"pro", "builder", "enterprise"})
STARTER_TIERS = frozenset({"starter", "pro", "builder", "enterprise"})

_json_mode = False
_country_file = SESSION_FILE.parent / "country"


def set_json_mode(enabled: bool) -> None:
    global _json_mode
    _json_mode = enabled


def is_json_mode() -> bool:
    return _json_mode


def get_lang() -> str:
    if LANG_FILE.exists():
        return LANG_FILE.read_text(encoding="utf-8").strip()
    return "es"


def is_en() -> bool:
    return get_lang() == "en"


def get_default_country() -> str:
    if _country_file.exists():
        cc = _country_file.read_text(encoding="utf-8").strip().upper()
        if len(cc) == 2:
            return cc
    return "PE"


def set_default_country(code: str) -> None:
    _country_file.parent.mkdir(parents=True, exist_ok=True)
    _country_file.write_text(code.upper(), encoding="utf-8")


def table_box():
    return box.ROUNDED


def api_host() -> str:
    return API.replace("https://", "").replace("http://", "").rstrip("/")


# ── JSON envelope for agents ────────────────────────────────────────────────────

def json_response(
    ok: bool,
    data: Any = None,
    *,
    error: str | None = None,
    hint: str | None = None,
    next_commands: list[str] | None = None,
    status: int | None = None,
) -> dict:
    out: dict[str, Any] = {
        "ok": ok,
        "data": data,
        "error": error,
        "hint": hint,
        "next_commands": next_commands or [],
        "meta": {
            "version": PACKAGE_VERSION,
            "api": API,
            "as_of": datetime.now(timezone.utc).isoformat(),
        },
    }
    if status is not None:
        out["status"] = status
    return out


def emit_json(payload: dict, console: Console | None = None) -> None:
    text = json.dumps(payload, indent=2, ensure_ascii=False)
    if console:
        console.print(text)
    else:
        print(text)


def json_exit(
    console: Console,
    ok: bool,
    data: Any = None,
    *,
    error: str | None = None,
    hint: str | None = None,
    next_commands: list[str] | None = None,
    status: int | None = None,
    code: int | None = None,
) -> None:
    emit_json(
        json_response(ok, data, error=error, hint=hint, next_commands=next_commands, status=status),
        console,
    )
    sys.exit(0 if ok else (code if code is not None else 1))


# ── Actionable errors & hints ─────────────────────────────────────────────────

def error_next_commands(status: int | None, message: str) -> list[str]:
    msg = (message or "").lower()
    if status == 401 or "token" in msg or "login" in msg:
        return ["market register", "market login", "market doctor"]
    if "connect" in msg or "reach" in msg or "running" in msg:
        return ["market doctor", "market hello"]
    if status == 403 or "pro" in msg or "tier" in msg:
        return ["market whoami", "market upgrade --email you@example.com"]
    return ["market doctor", "market hello"]


def print_actionable_error(
    console: Console,
    message: str,
    *,
    status: int | None = None,
    title: str | None = None,
) -> None:
    en = is_en()
    cmds = error_next_commands(status, message)
    if title is None:
        title = "Error" if en else "Error"
    body = f"[bold]{message}[/]\n\n[dim]{'Next' if en else 'Siguiente'}:[/]\n"
    for c in cmds:
        body += f"  [cyan]-> {c}[/]\n"
    console.print(Panel(body.strip(), title=title, border_style=WARN, box=box.ROUNDED))


def print_hints(console: Console, commands: list[str], label: str | None = None) -> None:
    if not commands:
        return
    en = is_en()
    if label is None:
        label = "Next" if en else "Siguiente"
    line = f"[dim]{label}:[/] " + "  |  ".join(f"[cyan]{c}[/]" for c in commands)
    console.print(line)


def print_context_bar(
    console: Console,
    *,
    tier: str = "?",
    country: str | None = None,
    username: str | None = None,
) -> None:
    cc = country or get_default_country()
    user = username or "anon"
    line = (
        f"[dim]market[/]  [#00FF88]|[/]  [dim]tier[/] [bold]{tier}[/]  [#00FF88]|[/]  "
        f"[dim]{'country' if is_en() else 'pais'}[/] [bold]{cc}[/]  [#00FF88]|[/]  "
        f"[dim]API[/] [bold]{api_host()[:28]}[/]  [#00FF88]|[/]  "
        f"[dim]user[/] [bold]{user}[/]"
    )
    console.print(Panel(line, border_style="dim", box=box.HEAVY, padding=(0, 1)))


# ── Tier gates ────────────────────────────────────────────────────────────────

def tier_gate(console: Console, feature: str, tier: str, *, json_args: Any = None) -> bool:
    """Return True if allowed. On deny, print guidance and exit."""
    en = is_en()
    tier_l = (tier or "free").lower()
    allowed = True
    msg = ""
    next_cmds = ["market whoami", "market upgrade --email you@example.com"]

    if feature == "checkout" and tier_l not in PRO_TIERS:
        allowed = False
        msg = (
            "Checkout requires Pro tier."
            if en
            else "Checkout requiere plan Pro."
        )
    elif feature == "alerts_create" and tier_l == "free":
        allowed = False
        msg = (
            "Price alerts require Pro."
            if en
            else "Alertas de precio requieren Pro."
        )

    if allowed:
        return True

    if json_args and getattr(json_args, "json", False):
        json_exit(
            console,
            False,
            error=msg,
            hint="upgrade",
            next_commands=next_cmds,
            status=403,
        )
    print_actionable_error(console, msg, status=403, title="Plan" if en else "Plan")
    print_hints(console, next_cmds)
    sys.exit(1)
    return False


# ── Status phases (Codex-style) ───────────────────────────────────────────────

@contextmanager
def status_phases(console: Console, phases: list[str]) -> Iterator[None]:
    label = phases[0] if phases else "..."
    with console.status(f"[cyan]{label}[/]"):
        yield


def run_with_status(console: Console, label: str):
    return console.status(f"[cyan]{label}[/]")


# ── Doctor readiness ────────────────────────────────────────────────────────────

def readiness_score(checks: list[tuple[str, str, str]]) -> tuple[int, str]:
    weights = {
        "API URL": 5,
        "API health": 30,
        "Auth": 25,
        "Tier": 10,
        "País": 5,
        "Countries": 5,
        "market-mcp": 15,
        "MCP snippet": 5,
    }
    score = 0
    total = sum(weights.values())
    for name, _detail, status in checks:
        w = weights.get(name, 5)
        if status == "ok":
            score += w
        elif status == "warn":
            score += w // 2
    pct = round(score * 100 / total)
    en = is_en()
    if pct >= 85:
        summary = "Ready for search and MCP integration." if en else "Listo para search e integracion MCP."
    elif pct >= 60:
        summary = "Partially ready — complete auth." if en else "Parcialmente listo — complete autenticacion."
    else:
        summary = "Not ready — run market init." if en else "No listo — ejecute market init."
    return pct, summary


# ── MCP snippets ────────────────────────────────────────────────────────────────

def get_mcp_config() -> dict:
    """Machine-readable MCP server configuration for agents / Cursor / Claude etc."""
    return {
        "mcpServers": {
            "cli-market": {
                "command": "market-mcp",
                "args": [],
                "env": {"MARKET_API_URL": API},
            }
        }
    }


def mcp_cursor_snippet() -> str:
    """Pretty-printed JSON snippet for pasting into ~/.cursor/mcp.json (human use)."""
    return json.dumps(get_mcp_config(), indent=2)


def mcp_snippet_panel(console: Console, width: int | None = None) -> None:
    en = is_en()
    title = "MCP / Cursor" if en else "MCP / Cursor"
    body = (
        f"[dim]{'Paste in' if en else 'Pegar en'} ~/.cursor/mcp.json[/]\n\n"
        f"[white]{mcp_cursor_snippet()}[/]"
    )
    console.print(
        Panel(body, title=title, border_style=MINT, box=box.ROUNDED, padding=(1, 2), width=width)
    )


# ── Version notice ─────────────────────────────────────────────────────────────

def maybe_version_notice(console: Console) -> None:
    flag = SESSION_FILE.parent / "version_check"
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if flag.exists() and flag.read_text(encoding="utf-8").strip() == today:
        return
    try:
        r = httpx.get("https://pypi.org/pypi/cli-market-world/json", timeout=4)
        r.raise_for_status()
        latest = r.json()["info"]["version"]
        if latest and latest != PACKAGE_VERSION:
            en = is_en()
            console.print(
                f"[dim]CLI Market {PACKAGE_VERSION} — "
                f"{'available' if en else 'disponible'} {latest} "
                f"([cyan]pip install -U cli-market-world[/])[/]"
            )
    except Exception:
        pass
    try:
        flag.parent.mkdir(parents=True, exist_ok=True)
        flag.write_text(today, encoding="utf-8")
    except OSError:
        pass


# ── Data footer for price commands ────────────────────────────────────────────

def price_data_footer(console: Console) -> None:
    en = is_en()
    if en:
        line = (
            f"[dim]Verified store prices · normalized kg/L · "
            f"refresh every {PRICES_REFRESH_HOURS}h · catalog APIs (VTEX/Shopify/Magento/WooCommerce)[/]"
        )
    else:
        line = (
            f"[dim]Precios de tienda verificados · normalizado kg/L · "
            f"actualizacion cada {PRICES_REFRESH_HOURS}h · APIs de catalogo[/]"
        )
    console.print(line)


def fetch_tier() -> str:
    token = get_token()
    if not token:
        return "free"
    sub = api("GET", "/auth/subscription")
    if sub.get("error"):
        return "?"
    return (sub.get("subscription") or {}).get("tier", "free")


# ── Grouped terminal layouts (MCP tools + data moat) ─────────────────────────

INDICATOR_SHELF_CATEGORIES = frozenset(
    {"retail", "product", "quality", "affordability", "demand", "logistics"}
)
INDICATOR_MACRO_CATEGORIES = frozenset({"macro", "composite"})

INDICATOR_GROUP_LABELS = {
    "es": {
        "shelf": "Anaquel y demanda",
        "macro": "Macro y compuestos",
    },
    "en": {
        "shelf": "Shelf and demand",
        "macro": "Macro and composite",
    },
}

MCP_TOOL_GROUPS: list[tuple[str, str, list[str]]] = [
    (
        "session",
        "Sesión y cuenta",
        "Session and account",
        [
            "market_login",
            "market_whoami",
            "market_subscription",
            "market_preferences",
        ],
    ),
    (
        "commerce",
        "Comercio",
        "Commerce",
        [
            "market_search",
            "market_compare",
            "market_add",
            "market_cart",
            "market_cart_update",
            "market_cart_remove",
            "market_checkout",
            "market_orders",
            "market_reorder",
            "market_ask",
            "market_basket",
        ],
    ),
    (
        "moat",
        "Data moat",
        "Data moat",
        [
            "market_inflation",
            "market_indicators",
            "market_scores",
            "market_intel_refresh",
            "market_enrichment",
            "market_enrichment_subcategories",
            "market_enrichment_refresh",
            "market_analytics_indicators",
            "market_stats",
            "market_alerts",
            "market_export",
            "market_trending",
            "market_price_history",
        ],
    ),
    (
        "catalog",
        "Catálogo y utilidades",
        "Catalog and utilities",
        [
            "market_lines",
            "market_stores",
            "market_countries",
            "market_categories",
            "market_barcode",
            "market_enrich",
            "market_brands",
            "market_stock",
            "market_scan",
            "market_ticket",
            "market_voice",
            "market_favorites",
            "market_notify",
            "market_exchange",
            "market_delivery",
        ],
    ),
]


def layout_width(console: Console, *, minimum: int = 72, maximum: int = 100) -> int:
    return min(max(console.width, minimum), maximum)


def column_width(console: Console, columns: int = 2, *, gap: int = 4, minimum: int = 34) -> int:
    total = layout_width(console)
    return max((total - gap * (columns - 1)) // columns, minimum)


def print_section_header(
    console: Console,
    title: str,
    *,
    subtitle: str = "",
    meta: str = "",
) -> None:
    body = f"[bold {MINT}]{title}[/]"
    if subtitle:
        body += f"\n[dim]{subtitle}[/]"
    if meta:
        body += f"\n[dim]{meta}[/]"
    console.print(
        Panel(body, border_style=MINT, box=box.HEAVY, padding=(0, 1), width=layout_width(console))
    )


def print_columns(console: Console, panels: list[Panel], *, equal: bool = True) -> None:
    visible = [p for p in panels if p is not None]
    if not visible:
        return
    if len(visible) == 1:
        console.print(visible[0])
        return
    console.print(Columns(visible, equal=equal, expand=True))


def _indicator_group_items(items: list[dict[str, Any]], group: str) -> list[dict[str, Any]]:
    cats = INDICATOR_SHELF_CATEGORIES if group == "shelf" else INDICATOR_MACRO_CATEGORIES
    return [i for i in items if i.get("category") in cats]


def indicator_catalog_panel(
    items: list[dict[str, Any]],
    *,
    group: str,
    width: int | None = None,
) -> Panel:
    lang = "en" if is_en() else "es"
    labels = INDICATOR_GROUP_LABELS[lang]
    title = labels[group]
    subset = _indicator_group_items(items, group)
    table = Table(border_style=TABLE_BORDER, box=table_box(), show_header=True, expand=True)
    table.add_column("Key", style="cyan", no_wrap=True)
    table.add_column("Fuente" if lang == "es" else "Source", max_width=22)
    table.add_column("TTL", justify="right", style="dim", no_wrap=True)
    for i in subset:
        table.add_row(
            i.get("key", ""),
            (i.get("source") or "")[:22],
            f"{i.get('refresh_hours', 24)}h",
        )
    count = len(subset)
    return Panel(
        table,
        title=f"[bold {MINT}]{title}[/] [dim]({count})[/]",
        border_style=MINT,
        box=box.ROUNDED,
        padding=(0, 1),
        width=width,
    )


def print_indicator_catalog(console: Console, items: list[dict[str, Any]]) -> None:
    col_w = column_width(console)
    print_columns(
        console,
        [
            indicator_catalog_panel(items, group="shelf", width=col_w),
            indicator_catalog_panel(items, group="macro", width=col_w),
        ],
    )


def scores_table(scores: dict[str, Any], *, title: str | None = None) -> Table:
    lang = "en" if is_en() else "es"
    table = Table(
        title=title,
        border_style=TABLE_BORDER,
        box=table_box(),
        show_header=True,
        expand=True,
    )
    table.add_column("Score", style="bold")
    table.add_column("Valor" if lang == "es" else "Value", justify="right")
    table.add_column("Señal" if lang == "es" else "Signal")
    for name, info in scores.items():
        if not isinstance(info, dict):
            continue
        table.add_row(name, str(info.get("score", "—")), info.get("label", ""))
    return table


def scores_panel(
    scores: dict[str, Any],
    *,
    country: str = "",
    width: int | None = None,
    subset: frozenset[str] | None = None,
) -> Panel | None:
    filtered = {
        k: v for k, v in scores.items() if isinstance(v, dict) and (subset is None or k in subset)
    }
    if not filtered:
        return None
    lang = "en" if is_en() else "es"
    label = f"Scores — {country}" if country else ("Composite scores" if lang == "en" else "Scores compuestos")
    return Panel(
        scores_table(filtered),
        title=f"[bold {MINT}]{label}[/]",
        border_style=MINT,
        box=box.ROUNDED,
        padding=(0, 1),
        width=width,
    )


ENRICHMENT_SCORE_KEYS = frozenset(
    {
        "food_premium",
        "nutrition_quality",
        "staple_demand",
        "product_intelligence",
        "macro_validation",
        "labor_stress",
        "growth_outlook",
    },
)


def enrichment_values_panel(
    items: list[dict[str, Any]],
    *,
    country: str,
    width: int | None = None,
) -> Panel:
    lang = "en" if is_en() else "es"
    title = f"Enrichment — {country}" if lang == "en" else f"Enriquecimiento — {country}"
    table = Table(border_style=TABLE_BORDER, box=table_box(), expand=True)
    table.add_column("Indicador" if lang == "es" else "Indicator", style="cyan")
    table.add_column("Valor" if lang == "es" else "Value", justify="right")
    table.add_column("Unidad" if lang == "es" else "Unit")
    table.add_column("Actualizado" if lang == "es" else "Updated", style="dim")
    for i in items:
        table.add_row(
            i.get("key", ""),
            str(i.get("value", "—")),
            i.get("unit") or "",
            (i.get("recorded_at") or "")[:16],
        )
    return Panel(
        table,
        title=f"[bold {MINT}]{title}[/] [dim]({len(items)})[/]",
        border_style=MINT,
        box=box.ROUNDED,
        padding=(0, 1),
        width=width,
    )


def subcategories_panel(sub_items: list[dict[str, Any]], *, width: int | None = None) -> Panel | None:
    if not sub_items:
        return None
    lang = "en" if is_en() else "es"
    table = Table(border_style=TABLE_BORDER, box=table_box(), expand=True)
    table.add_column("Subcat", style="cyan")
    table.add_column("Δ 7d", justify="right")
    table.add_column("Wiki", justify="right")
    table.add_column("Min", justify="right")
    for row in sub_items:
        sig = row.get("signals", {})
        table.add_row(
            row.get("subcategory", ""),
            str(sig.get("subcat_price_momentum", {}).get("value", "—")),
            str(sig.get("subcat_wiki_momentum", {}).get("value", "—")),
            str(sig.get("subcat_min_price", {}).get("value", "—")),
        )
    title = "By subcategory" if lang == "en" else "Por subcategoría"
    return Panel(
        table,
        title=f"[bold {MINT}]{title}[/]",
        border_style=MINT,
        box=box.ROUNDED,
        padding=(0, 1),
        width=width,
    )


def _mcp_tool_lookup() -> dict[str, str]:
    try:
        from market_core.market_mcp import TOOLS
    except ImportError:
        return {}
    return {t["name"]: t.get("description", "") for t in TOOLS}


def mcp_group_panel(
    group_key: str,
    title_es: str,
    title_en: str,
    tool_names: list[str],
    *,
    descriptions: dict[str, str],
    width: int | None = None,
) -> Panel:
    lang = "en" if is_en() else "es"
    title = title_en if lang == "en" else title_es
    lines: list[str] = []
    for name in tool_names:
        desc = descriptions.get(name, "")
        short = (desc[:52] + "…") if len(desc) > 55 else desc
        lines.append(f"[cyan]{name}[/]\n[dim]{short or '—'}[/]")
    body = "\n\n".join(lines)
    return Panel(
        body,
        title=f"[bold {MINT}]{title}[/] [dim]({len(tool_names)})[/]",
        border_style=MINT,
        box=box.ROUNDED,
        padding=(1, 1),
        width=width,
    )


def print_mcp_tools_catalog(console: Console) -> None:
    descriptions = _mcp_tool_lookup()
    col_w = column_width(console, columns=2)
    row1 = [
        mcp_group_panel(key, es, en, names, descriptions=descriptions, width=col_w)
        for key, es, en, names in MCP_TOOL_GROUPS[:2]
    ]
    row2 = [
        mcp_group_panel(key, es, en, names, descriptions=descriptions, width=col_w)
        for key, es, en, names in MCP_TOOL_GROUPS[2:]
    ]
    print_columns(console, row1)
    console.print()
    print_columns(console, row2)


def print_intel_footer(console: Console, hints: list[str]) -> None:
    print_hints(console, hints)


# ── Account dashboard (P2 #14) ────────────────────────────────────────────────

def _usage_bar(used: int, limit: Any, *, width: int = 24) -> str:
    if limit in (None, "unlimited") or (isinstance(limit, int) and limit < 0):
        return f"[dim]{'unlimited' if is_en() else 'ilimitado'}[/]"
    lim = int(limit)
    if lim <= 0:
        return "[dim]—[/]"
    filled = min(int(used / lim * width), width)
    bar = f"[{MINT}]{'#' * filled}[/][dim]{'-' * (width - filled)}[/]"
    return f"{bar}  {used:,}/{lim:,}"


def print_account_dashboard(console: Console, data: dict[str, Any]) -> None:
    lang_es = not is_en()
    tier = data.get("tier", "free")
    limits = data.get("limits") or {}
    usage = data.get("usage") or {}
    upgrade = data.get("upgrade") or {}
    username = data.get("username", "?")

    print_section_header(
        console,
        "Cuenta" if lang_es else "Account",
        subtitle=f"{'usuario' if lang_es else 'user'} {username} · tier [bold]{tier}[/]",
    )

    col_w = column_width(console)
    limits_body = (
        f"[bold {MINT}]{'Límites' if lang_es else 'Limits'}[/]\n"
        f"  {'Consultas/día' if lang_es else 'Requests/day'}: [bold]{limits.get('req_day', '?')}[/]\n"
        f"  {'Consultas/min' if lang_es else 'Requests/min'}: [bold]{limits.get('req_min', '?')}[/]\n"
        f"  API keys: [bold]{limits.get('api_keys', '?')}[/]\n"
        f"  Checkout: [bold]{'sí' if limits.get('checkout') else 'no'}[/]\n"
        f"  {'Alertas' if lang_es else 'Alerts'}: [bold]{limits.get('alerts', 0)}[/]\n"
        f"  Export: [bold]{'sí' if limits.get('export') else 'no'}[/]"
    )
    usage_body = (
        f"[bold {MINT}]{'Uso hoy' if lang_es else 'Usage today'}[/]\n"
        f"  {'Día' if lang_es else 'Daily'}: {_usage_bar(int(usage.get('requests_today', 0)), limits.get('req_day'))}\n"
        f"  {'Minuto' if lang_es else 'Minute'}: {_usage_bar(int(usage.get('requests_last_minute', 0)), limits.get('req_min'))}\n"
        f"  API keys: [bold]{usage.get('api_keys_used', 0)}[/]"
    )
    print_columns(
        console,
        [
            Panel(limits_body, border_style=MINT, box=box.ROUNDED, padding=(1, 2), width=col_w),
            Panel(usage_body, border_style=MINT, box=box.ROUNDED, padding=(1, 2), width=col_w),
        ],
    )

    billing = data.get("billing") or {}
    if billing.get("message"):
        console.print()
        console.print(
            Panel(
                f"[yellow]{billing['message']}[/]"
                + (
                    f"\n[dim]ref:[/] [cyan]{billing.get('request_id', '')}[/]"
                    if billing.get("request_id")
                    else ""
                ),
                title=f"[bold {MINT}]{'Facturación' if lang_es else 'Billing'}[/]",
                border_style="yellow",
                box=box.ROUNDED,
                padding=(1, 2),
                width=layout_width(console),
            )
        )

    if upgrade.get("next_tier"):
        up_body = (
            f"[bold]{upgrade.get('title', '')}[/]\n\n"
            f"[dim]CLI:[/] [cyan]{upgrade.get('cli', '')}[/]"
        )
        if upgrade.get("url"):
            up_body += f"\n[dim]Web:[/] [cyan]{upgrade.get('url', '')}[/]"
        console.print()
        console.print(
            Panel(
                up_body,
                title=f"[bold {MINT}]{'Siguiente paso' if lang_es else 'Next step'}[/]",
                border_style=MINT,
                box=box.ROUNDED,
                padding=(1, 2),
                width=layout_width(console),
            )
        )

    hints = ["market doctor", "market search \"leche\" --country PE"]
    if tier == "free":
        hints.insert(0, "market upgrade --plan starter")
    elif tier == "starter":
        hints.insert(0, "market upgrade --plan pro")
    print_intel_footer(console, hints)