"""CLI Market terminal UX — theme, actionable errors, hints, tier gates, JSON envelope."""

from __future__ import annotations

import json
import os
import sys
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Iterator

import httpx
from rich.console import Console
from rich.panel import Panel
from rich.columns import Columns
from rich.table import Table
from rich import box

from market_core import API, SESSION_FILE, LANG_FILE, get_token, get_session_username, api
from market_stats import (
    COUNTRIES,
    PACKAGE_VERSION,
    PRICES_REFRESH_HOURS,
    PRICES_VERIFIED_LABEL,
    RETAILERS_VERIFIED,
)

# ── Theme (Antigravity / Codex / Claude inspired) ────────────────────────────────────────────

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


# ── JSON envelope for agents ───────────────────────────────────────────────

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


# ── Actionable errors & hints ───────────────────────────────────────────────────

def error_next_commands(status: int | None, message: str) -> list[str]:
    msg = (message or "").lower()
    if status == 401 or "token" in msg or "login" in msg:
        return ["market register", "market login", "market doctor"]
    if "connect" in msg or "reach" in msg or "running" in msg:
        return ["market doctor", "market hello"]
    if "price_stale_or_drift" in msg or "refresh_cart" in msg or "missing_snapshot" in msg:
        return ["market search PRODUCTO --country PE", "market cart", "market checkout"]
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


# ── Tier gates ──────────────────────────────────────────────────────────────────────────

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
    elif feature == "investigate" and tier_l not in STARTER_TIERS:
        allowed = False
        msg = (
            "Investigate requires Starter tier or higher."
            if en
            else "Investigate requiere plan Starter o superior."
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


# ── Status phases (Codex-style) ────────────────────────────────────────────────────────

@contextmanager
def status_phases(console: Console, phases: list[str]) -> Iterator[None]:
    label = phases[0] if phases else "..."
    with console.status(f"[cyan]{label}[/]"):
        yield


def run_with_status(console: Console, label: str):
    return console.status(f"[cyan]{label}[/]")


# ── Doctor readiness ───────────────────────────────────────────────────────────────────

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


# ── MCP snippets ───────────────────────────────────────────────────────────────────────

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


def _cursor_mcp_path() -> str:
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA") or str(Path.home() / "AppData" / "Roaming")
        return str(Path(appdata) / "Cursor" / "User" / "globalStorage" / "cursor.mcp" / "mcp.json")
    return "~/.cursor/mcp.json"


def mcp_snippet_panel(console: Console, width: int | None = None) -> None:
    en = is_en()
    title = "MCP / Cursor" if en else "MCP / Cursor"
    cursor_path = _cursor_mcp_path()
    body = (
        f"[dim]{'Paste in' if en else 'Pegar en'} {cursor_path}[/]\n\n"
        f"[white]{mcp_cursor_snippet()}[/]"
    )
    console.print(
        Panel(body, title=title, border_style=MINT, box=box.ROUNDED, padding=(1, 2), width=width)
    )


# ── Version notice ──────────────────────────────────────────────────────────────────────────────

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


# ── Data footer for price commands ──────────────────────────────────────────────────

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


def fetch_observatory_public(*, days: int = 30, timeout: float = 12.0) -> dict[str, Any] | None:
    """Best-effort public Observatory metrics (GET /analytics/observatory)."""
    try:
        from market_core.market_observatory import MAA_PUBLIC_THRESHOLD
    except ImportError:
        MAA_PUBLIC_THRESHOLD = 10
    try:
        resp = httpx.get(f"{API}/analytics/observatory?days={days}", timeout=timeout)
        if resp.status_code != 200:
            return None
        data = resp.json()
        if not isinstance(data, dict):
            return None
        maa = int(data.get("maa") or 0)
        proxy = int(data.get("maa_proxy") or 0)
        if maa >= MAA_PUBLIC_THRESHOLD:
            data["display_maa"] = maa
            data["display_label"] = "maa"
        elif proxy > 0:
            data["display_maa"] = proxy
            data["display_label"] = "maa_proxy"
        elif maa > 0:
            data["display_maa"] = maa
            data["display_label"] = "maa"
        else:
            data["display_maa"] = None
            data["display_label"] = None
        return data
    except Exception:
        return None


def print_mission_control(
    console: Console,
    *,
    tier: str,
    observatory: dict[str, Any] | None = None,
    username: str | None = None,
) -> None:
    """Mission Control header for market shell startup."""
    en = is_en()
    title = f"CLI MARKET OS · v{PACKAGE_VERSION}"
    console.print()
    console.print(Panel(title, border_style=MINT, box=box.HEAVY, padding=(0, 1)))

    freshness = f"{PRICES_REFRESH_HOURS}h"
    stats = Table.grid(padding=(0, 2))
    stats.add_column(style="dim")
    stats.add_column(style="bold")
    stats.add_column(style="dim")
    stats.add_column(style="bold")
    stats.add_row(
        "Freshness" if en else "Frescura",
        freshness,
        "Retailers" if en else "Retailers",
        str(RETAILERS_VERIFIED),
    )
    stats.add_row(
        "Countries" if en else "Países",
        str(COUNTRIES),
        "Prices" if en else "Precios",
        PRICES_VERIFIED_LABEL,
    )
    console.print(stats)

    if observatory and observatory.get("display_maa") is not None:
        label = observatory.get("display_label") or "maa"
        proxy_note = " (proxy)" if label == "maa_proxy" else ""
        console.print(
            f"[dim]{'Agents (MAA)' if en else 'Agentes (MAA)'}[/]  "
            f"[bold {MINT}]{observatory['display_maa']}{proxy_note}[/]  "
            f"[dim]30d[/]"
        )

    console.print("[dim]" + ("─" * 40) + "[/]")
    missions_title = "MISSIONS" if en else "MISIONES"
    console.print(f"[bold {MINT}]{missions_title}[/]")
    menu = [
        ("1", "investigate QUERY", "Deep market report" if en else "Reporte profundo de mercado"),
        ("2", "compare QUERY", "Multi-retailer prices" if en else "Precios multi-retailer"),
        ("3", "intel inflation", "Line inflation (PE default)" if en else "Inflación por línea (PE default)"),
        ("4", "doctor", "API · auth · MCP health" if en else "Salud API · auth · MCP"),
        ("5", "mcp", "Tool registry (read-only)" if en else "Registro de tools (solo lectura)"),
    ]
    for num, cmd, desc in menu:
        console.print(f"  [cyan]{num}[/]  [bold]{cmd:<22}[/] [dim]{desc}[/]")
    console.print("[dim]" + ("─" * 40) + "[/]")

    tier_l = (tier or "free").lower()
    user = username or ("anon" if en else "anónimo")
    if not get_token():
        hint = (
            "Sign in with market register / market login to unlock investigate."
            if en
            else "Inicia sesión con market register / market login para desbloquear investigate."
        )
        console.print(f"[dim]{hint}[/]")
    elif tier_l not in STARTER_TIERS:
        hint = (
            "Investigate requires Starter+. Run market upgrade."
            if en
            else "Investigate requiere Starter+. Ejecuta market upgrade."
        )
        console.print(f"[dim]{hint}[/]")
    else:
        console.print(f"[dim]{'tier' if en else 'tier'}[/] [bold]{tier}[/] · [dim]user[/] [bold]{user}[/]")


def print_mcp_center(
    console: Console,
    *,
    profile: str,
    tools: list[dict[str, Any]],
    checks: list[tuple[str, str, str]],
    readiness_pct: int,
    readiness_summary: str,
    ok: bool,
) -> None:
    """Read-only MCP center: doctor health + tool catalog."""
    en = is_en()
    status_style = MINT if ok else WARN
    print_section_header(
        console,
        "MCP Center" if en else "Centro MCP",
        subtitle=(
            f"profile {profile} · {len(tools)} tools · readiness {readiness_pct}%"
            if en
            else f"perfil {profile} · {len(tools)} tools · readiness {readiness_pct}%"
        ),
        meta="read-only · market mcp-setup to install",
    )
    console.print(
        Panel(
            f"[bold {status_style}]{readiness_summary}[/]",
            title=f"[bold {MINT}]{'Health' if en else 'Salud'}[/]",
            border_style=status_style,
            box=box.ROUNDED,
        )
    )

    key_checks = ("API health", "Auth", "Tier", "market-mcp")
    table = Table(show_header=True, header_style=f"bold {MINT}", box=table_box(), border_style=TABLE_BORDER)
    table.add_column("Check")
    table.add_column("Detail")
    table.add_column("Status")
    for name, detail, status in checks:
        if name not in key_checks:
            continue
        style = {"ok": "green", "fail": "red", "warn": "yellow"}.get(status, "dim")
        table.add_row(name, detail, f"[{style}]{status}[/]")
    console.print(table)
    console.print()
    print_mcp_tools_catalog(console, profile=profile)
    print_intel_footer(
        console,
        [
            "market mcp-setup",
            "market mcp-setup --ide cursor",
            "market doctor",
        ],
    )


def print_investigate_report(console: Console, report: dict[str, Any]) -> None:
    """Rich renderer for market_missions.run_investigate payload."""
    from market_core import fmt_price

    en = is_en()
    query = report.get("query") or "?"
    country = report.get("country") or get_default_country()
    insights = report.get("insights") or {}
    sections = report.get("sections") or {}

    header = (
        f"MISSION · investigate · {query} · {country}"
        if en
        else f"MISIÓN · investigate · {query} · {country}"
    )
    console.print()
    console.print(Panel(header, border_style=MINT, box=box.ROUNDED))

    retailers = insights.get("retailers_scanned")
    skus = insights.get("skus_matched")
    if retailers is not None or skus is not None:
        sources = (
            f"{retailers or '?'} retailers · {skus or '?'} SKUs matched"
            if en
            else f"{retailers or '?'} retailers · {skus or '?'} SKUs"
        )
        console.print(f"[dim]{'Sources' if en else 'Fuentes'}[/]     [bold]{sources}[/]")

    leader = insights.get("leader") or {}
    if leader.get("store_name"):
        price = leader.get("price")
        currency = leader.get("currency") or "PEN"
        price_str = fmt_price(price, currency) if price is not None else "—"
        console.print(
            f"[dim]{'Leader' if en else 'Líder'}[/]      "
            f"[bold]{leader['store_name']}[/] {price_str}"
        )

    laggard = insights.get("laggard") or {}
    if laggard.get("store_name"):
        pct = laggard.get("pct_vs_mean")
        pct_str = f"+{pct:.0f}% vs mean" if pct is not None else ""
        if not en and pct is not None:
            pct_str = f"+{pct:.0f}% vs media"
        console.print(
            f"[dim]{'Laggard' if en else 'Rezagado'}[/]    "
            f"[bold]{laggard['store_name']}[/] [yellow]{pct_str}[/]"
        )

    spread = insights.get("spread_pct_max")
    if spread is not None:
        console.print(
            f"[dim]{'Spread' if en else 'Spread'}[/]      "
            f"[bold]{spread:.1f}%[/] max"
        )

    inflation = insights.get("inflation_line") or {}
    infl_section = sections.get("inflation") or {}
    if inflation:
        line = inflation.get("line") or query
        delta = float(inflation.get("delta_pct") or 0)
        days = inflation.get("days") or 30
        infl_color = "#FF6B35" if delta > 0 else MINT
        console.print(
            f"[dim]{'Inflation' if en else 'Inflación'}[/]   "
            f"{line} [{infl_color}]{delta:+.1f}%[/] ({days}d)"
        )
    elif infl_section.get("status") == "unavailable":
        console.print(
            f"[dim]{'Inflation' if en else 'Inflación'}[/]   "
            f"[yellow]{'unavailable' if en else 'no disponible'}[/]"
        )

    unavailable = [
        name
        for name, section in sections.items()
        if section.get("status") == "unavailable"
    ]
    if unavailable:
        console.print(
            f"[dim]{'Partial' if en else 'Parcial'}[/] — "
            f"{', '.join(unavailable)} "
            f"{'unavailable' if en else 'no disponible'}"
        )

    recs = report.get("recommendations") or []
    if recs:
        title = "Recommendations (rules-based, v0)" if en else "Recomendaciones (reglas, v0)"
        console.print()
        console.print(f"[bold {MINT}]{title}[/]")
        for i, rec in enumerate(recs, 1):
            console.print(f"  {i}. {rec.get('text', '')}")

    price_data_footer(console)
    q = query.replace('"', '\\"')
    print_hints(
        console,
        [
            f'market compare "{q}" --country {country}',
            f'market intel inflation --country {country}',
            "market doctor",
        ],
    )


def fetch_tier() -> str:
    ctx = fetch_session_context()
    if not ctx:
        return "free"
    return ctx.get("tier", "free")


def fetch_session_context() -> dict | None:
    """Return username, tier, and subscription when a local session exists."""
    if not get_token():
        return None
    who = api("GET", "/auth/whoami")
    if who.get("error"):
        return {
            "username": get_session_username() or "?",
            "tier": "?",
            "subscription": {},
            "valid": False,
        }
    sub_data = api("GET", "/auth/subscription")
    sub = sub_data.get("subscription") or {}
    username = who.get("username") or sub_data.get("username") or get_session_username() or "?"
    return {
        "username": username,
        "tier": sub.get("tier", "free"),
        "subscription": sub,
        "valid": True,
    }


def is_pro_tier(tier: str | None) -> bool:
    return (tier or "free").lower() in PRO_TIERS


# ── Grouped terminal layouts (MCP tools + data moat) ───────────────────────────────────────────────────────

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

_MCP_BUNDLE_PREFIXES = ("[Shop] ", "[Intel] ", "[Account] ", "[Advanced] ", "[Admin] ")
_MCP_CANONICAL = frozenset({"market_discover", "market_intel_brief", "market_price_alerts"})
_MCP_BUNDLE_LABELS: dict[str, tuple[str, str]] = {
    "shop": ("Shop", "Shop"),
    "intel": ("Intel", "Intel"),
    "account": ("Cuenta", "Account"),
    "advanced": ("Avanzado", "Advanced"),
    "admin": ("Admin", "Admin"),
}


def _strip_mcp_bundle_prefix(description: str) -> str:
    for prefix in _MCP_BUNDLE_PREFIXES:
        if description.startswith(prefix):
            return description[len(prefix):]
    return description


def mcp_tool_groups(profile: str = "default") -> list[tuple[str, str, str, list[str]]]:
    """Bundle-grouped MCP tool names from registry (PR5)."""
    from market_core.market_mcp_registry import BUNDLES, TOOLS, get_tool_meta, tool_in_profile

    bundle_keys = ("shop", "intel", "account") if profile == "default" else BUNDLES
    groups: list[tuple[str, str, str, list[str]]] = []
    for bundle in bundle_keys:
        names = [
            tool["name"]
            for tool in TOOLS
            if (meta := get_tool_meta(tool["name"]))
            and meta["bundle"] == bundle
            and tool_in_profile(tool["name"], profile)
        ]
        if not names:
            continue
        es, en = _MCP_BUNDLE_LABELS[bundle]
        groups.append((bundle, es, en, names))
    return groups


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


_SCORE_HINTS: dict[str, tuple[str, str]] = {
    "retail_aggression":   ("Intensidad de descuentos y promos activas en góndola", "How aggressively retailers are discounting right now"),
    "price_fairness":      ("Qué tan competitivos son los precios vs histórico y competidores", "How fair prices are vs historical range and competitors"),
    "basket_stress":       ("Presión sobre la canasta básica (0=sin estrés, 1=crítico)", "Pressure on the basic basket (0=none, 1=critical)"),
    "data_confidence":     ("Frescura y cobertura de los datos (bajo=datos con lag)", "Data freshness and coverage (low=stale snapshots)"),
    "macro_alignment":     ("Alineación entre precios de góndola y macro (CPI, inflación)", "Alignment between shelf prices and macro indicators (CPI)"),
    "demand_outlook":      ("Perspectiva de demanda a 30d según búsquedas y volumen", "30-day demand outlook based on search trends and volume"),
    "logistics_risk":      ("Riesgo de desabasto o quiebre de stock por logística", "Risk of stock-outs or supply disruption"),
    "staple_demand":       ("Demanda específica de productos básicos (arroz, aceite, etc.)", "Demand for staple products (rice, oil, sugar, etc.)"),
    "macro_validation":    ("Consistencia interna del modelo con datos macro externos", "Internal model consistency with external macro data"),
    "labor_stress":        ("Presión salarial y laboral que puede impactar precios", "Labor cost pressure that could push prices up"),
    "search_momentum":     ("Velocidad de crecimiento en búsquedas de productos", "Growth rate of product search queries"),
    "food_premium":        ("Prima de precio en alimentos premium vs básicos", "Price premium of premium food vs staples"),
    "nutrition_quality":   ("Calidad nutricional promedio de productos en góndola", "Average nutritional quality of products in shelf"),
    "product_intelligence":("Riqueza de datos de producto (nombre, marca, categoría)", "Product data richness (name, brand, category coverage)"),
    "growth_outlook":      ("Perspectiva de crecimiento del mercado a mediano plazo", "Medium-term market growth outlook"),
}


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
    table.add_column("Qué indica" if lang == "es" else "What it means", style="dim", no_wrap=False)
    for name, info in scores.items():
        if not isinstance(info, dict):
            continue
        hints = _SCORE_HINTS.get(name, ("", ""))
        hint = hints[0] if lang == "es" else hints[1]
        table.add_row(name, str(info.get("score", "—")), info.get("label", ""), hint)
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
    return {t["name"]: _strip_mcp_bundle_prefix(t.get("description", "")) for t in TOOLS}


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
        marker = f" [bold {MINT}]★[/]" if name in _MCP_CANONICAL else ""
        lines.append(f"[cyan]{name}[/]{marker}\n[dim]{short or '—'}[/]")
    body = "\n\n".join(lines)
    return Panel(
        body,
        title=f"[bold {MINT}]{title}[/] [dim]({len(tool_names)})[/]",
        border_style=MINT,
        box=box.ROUNDED,
        padding=(1, 1),
        width=width,
    )


def print_mcp_tools_catalog(console: Console, *, profile: str = "default") -> None:
    descriptions = _mcp_tool_lookup()
    groups = mcp_tool_groups(profile)
    col_w = column_width(console, columns=2)
    panels = [
        mcp_group_panel(key, es, en, names, descriptions=descriptions, width=col_w)
        for key, es, en, names in groups
    ]
    for i in range(0, len(panels), 2):
        print_columns(console, panels[i : i + 2])
        if i + 2 < len(panels):
            console.print()


def print_intel_footer(console: Console, hints: list[str]) -> None:
    print_hints(console, hints)


# ── Account dashboard (P2 #14) ──────────────────────────────────────────────────────────────────────────────

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
        billing_body = f"[yellow]{billing['message']}[/]"
        if billing.get("eta"):
            billing_body += (
                f"\n[dim]{'ETA:' if lang_es else 'ETA:'}[/] [bold]{billing['eta']}[/]"
            )
        if billing.get("verify_cli"):
            billing_body += f"\n[dim]verify:[/] [cyan]{billing['verify_cli']}[/]"
        if billing.get("request_id"):
            billing_body += f"\n[dim]ref:[/] [cyan]{billing.get('request_id', '')}[/]"
        console.print(
            Panel(
                billing_body,
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
    if tier in ("free", "starter"):
        hints.insert(0, "market upgrade")
    print_intel_footer(console, hints)
