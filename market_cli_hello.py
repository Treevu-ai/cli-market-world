"""`market hello` — post-install activation screen + shared splash UI.

Extracted from market_cli.py. _render_splash is also used by cmd_shell
in market_cli.py, which imports it from here.
"""

from __future__ import annotations

import os

from rich import box
from rich.align import Align
from rich.columns import Columns
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

import market_ui as ui
from market_core import API, get_session_username
from market_cli_i18n import get_lang
from market_cli_telemetry import _report_install_event
from market_stats import (
    COUNTRIES as MS_COUNTRIES, RETAILERS_VERIFIED,
    PRICES_VERIFIED_LABEL, INDICATORS_COUNT, PLATFORM_LIST_ES, PLATFORM_LIST_EN,
    PRICES_REFRESH_HOURS, PACKAGE_VERSION,
)

_NO_COLOR = bool(os.environ.get("NO_COLOR", ""))
console = Console(no_color=_NO_COLOR)


def _mcp_profile_counts() -> tuple[int, int]:
    from market_core.market_mcp_registry import public_tool_count
    return public_tool_count("default"), public_tool_count("legacy")


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
            "[dim]for API key, readiness,[/] [bold]first verified search[/][dim], and MCP snippet.[/]\n"
            "[dim]Or[/] [cyan]market register[/] [dim]if you only need credentials.[/]"
        )
        title = "[bold #00FF88]NEXT STEP[/]"
    else:
        body = (
            "[bold white]Activación post-install[/]\n"
            "[dim]Instalaste[/] [cyan]cli-market[/][dim]. Ejecuta[/] [bold cyan]market init[/] "
            "[dim]para API key, readiness,[/] [bold]primera búsqueda verificada[/][dim] y snippet MCP.[/]\n"
            "[dim]O[/] [cyan]market register[/] [dim]si solo necesitas credenciales.[/]"
        )
        title = "[bold #00FF88]SIGUIENTE PASO[/]"
    return Panel(body, title=title, border_style="#00FF88", box=box.ROUNDED, padding=(1, 2), width=width)


def _hello_pro_panel(is_en: bool, width: int, *, username: str, sub: dict) -> Panel:
    limits = (
        f"{sub.get('req_limit_day', '?')}/day · checkout · alertas"
        if not is_en
        else f"{sub.get('req_limit_day', '?')}/day · checkout · alerts"
    )
    if is_en:
        body = (
            f"[bold white]Welcome back,[/] [cyan]{username}[/]\n"
            f"[bold #00FF88]Build Pro[/] is active on this machine.\n"
            f"[dim]Limits:[/] {limits}\n\n"
            f"[dim]Try[/] [cyan]market search \"rice\" --country PE[/] "
            f"[dim]or[/] [cyan]market account[/] [dim]for usage.[/]"
        )
        title = "[bold #00FF88]PRO ACCOUNT[/]"
    else:
        body = (
            f"[bold white]Bienvenido de vuelta,[/] [cyan]{username}[/]\n"
            f"[bold #00FF88]Build Pro[/] activo en esta máquina.\n"
            f"[dim]Límites:[/] {limits}\n\n"
            f"[dim]Prueba[/] [cyan]market search \"arroz\" --country PE[/] "
            f"[dim]o[/] [cyan]market account[/] [dim]para ver uso.[/]"
        )
        title = "[bold #00FF88]CUENTA PRO[/]"
    return Panel(body, title=title, border_style="#00FF88", box=box.ROUNDED, padding=(1, 2), width=width)


def _hello_status_bar(is_en: bool, width: int, *, ctx: dict | None = None) -> Panel:
    label = "EN LINEA" if not is_en else "ONLINE"
    mcp_default, _ = _mcp_profile_counts()
    line = (
        f"[dim]v{PACKAGE_VERSION}[/]  [#00FF88]|[/]  "
        f"[dim]API[/]  [bold]{_hello_api_host()}[/]  [#00FF88]|[/]  "
        f"[dim]MCP[/]  [bold #00FF88]{mcp_default}[/] tools  [#00FF88]|[/]  "
        f"[dim]RETAILERS[/]  [bold #00FF88]{RETAILERS_VERIFIED}[/]  [#00FF88]|[/]  "
        f"[dim]STATUS[/]  [bold #00FF88]{label}[/]"
    )
    if ctx and ctx.get("valid"):
        line += (
            f"  [#00FF88]|[/]  [dim]{'user' if is_en else 'usuario'}[/]  "
            f"[bold cyan]{ctx.get('username', '?')}[/]  [#00FF88]|[/]  "
            f"[dim]tier[/]  [bold #00FF88]{ctx.get('tier', '?')}[/]"
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
            "  [cyan]1.[/] [cyan]market demo[/]         [dim]no account · search + compare[/]\n"
            "  [cyan]2.[/] [cyan]market init[/]         [dim]account + checkout + MCP[/]\n"
            '  [cyan]3.[/] [cyan]market search "milk" --country PE[/]\n'
            "  [cyan]4.[/] [cyan]market doctor[/]       [dim]readiness %[/]\n"
            "  [dim]     market register[/]  [dim]optional if you only need sk-...[/]\n\n"
            "[bold #00FF88]DOCS[/]\n"
            "  cli-market.dev/docs#quickstart\n"
            "  cli-market.dev/tools"
        )
        title = "[bold #00FF88]QUICK START[/]"
    else:
        body = (
            "[bold #00FF88]INICIO RÁPIDO[/]\n"
            "  [cyan]0.[/] [cyan]market hello[/]        [dim]estás aquí[/]\n"
            "  [cyan]1.[/] [cyan]market demo[/]         [dim]sin cuenta · buscar + comparar[/]\n"
            "  [cyan]2.[/] [cyan]market init[/]         [dim]cuenta + checkout + MCP[/]\n"
            '  [cyan]3.[/] [cyan]market search "leche" --country PE[/]\n'
            "  [cyan]4.[/] [cyan]market doctor[/]       [dim]preparacion %[/]\n"
            "  [dim]     market register[/]  [dim]opcional si solo necesitas sk-...[/]\n\n"
            "[bold #00FF88]DOCS[/]\n"
            "  cli-market.dev/docs#quickstart\n"
            "  cli-market.dev/tools"
        )
        title = "[bold #00FF88]INICIO RÁPIDO[/]"
    return Panel(body, title=title, border_style="#00FF88", box=box.ROUNDED, padding=(1, 2), width=width)



def _hello_intermediate_panel(is_en: bool, width: int | None = None) -> Panel:
    mcp_default, mcp_legacy = _mcp_profile_counts()
    if is_en:
        body = (
            "[bold #00FF88]INTERMEDIATE[/]\n"
            '  [cyan]market basket[/] [dim]"milk:2 rice:1" --country PE[/]\n'
            '  [cyan]market compare[/] [dim]"sunflower oil" --country AR[/]\n'
            "  [cyan]market intel inflation[/] [dim]-c PE[/]\n"
            f"  [cyan]market tools[/]            [dim]{mcp_default} MCP · Shop/Intel/Account ({mcp_legacy} legacy)[/]\n"
            "  [cyan]market intel indicators[/] [dim]-c PE[/]\n"
            "  [cyan]market intel enrichment[/] [dim]-c PE[/]\n"
            "  [cyan]market alerts[/] [dim]--action list[/]"
        )
        title = "[bold #00FF88]USE CASES[/]"
    else:
        body = (
            "[bold #00FF88]NIVEL INTERMEDIO[/]\n"
            '  [cyan]market basket[/] [dim]"leche:2 arroz:1" --country PE[/]\n'
            '  [cyan]market compare[/] [dim]"aceite de girasol" --country AR[/]\n'
            "  [cyan]market intel inflation[/] [dim]-c PE[/]\n"
            f"  [cyan]market tools[/]            [dim]{mcp_default} MCP · Shop/Intel/Account ({mcp_legacy} legacy)[/]\n"
            "  [cyan]market intel indicators[/] [dim]-c PE[/]\n"
            "  [cyan]market intel enrichment[/] [dim]-c PE[/]\n"
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


# ── Two-panel splash screen (market hello + market shell) ────────────────────

_SPLASH_ICON = (
    "  ╔══════════════╗  ",
    "  ║  ◉        ◉  ║  ",
    "  ║       ▲       ║  ",
    "  ║    ╰──────╯   ║  ",
    "  ╠══════════════╣  ",
    "  ║  C L I - M K T ║  ",
    "  ╚══════════════╝  ",
)


def _splash_left(is_en: bool, ctx: dict | None) -> Panel:
    username = (ctx or {}).get("username") or ("developer" if is_en else "developer")
    tier = (ctx or {}).get("tier", "free")
    sub = (ctx or {}).get("subscription") or {}
    req_day = sub.get("req_limit_day", "1,000")
    mcp_count = _mcp_profile_counts()[0]

    greeting = (
        f"Welcome back, [bold cyan]{username}[/]!"
        if is_en
        else f"Bienvenido de vuelta, [bold cyan]{username}[/]!"
    )
    if not (ctx and ctx.get("valid")):
        greeting = (
            "[bold white]Commerce API for AI Agents[/]"
            if is_en
            else "[bold white]API de comercio para agentes IA[/]"
        )

    icon = "\n".join(f"[bold #00FF88]{line}[/]" for line in _SPLASH_ICON)

    info_rows = [
        (("Tier" if is_en else "Tier"), f"[bold #00FF88]{tier}[/]"),
        (("Retailers" if is_en else "Retailers"), f"[bold]{RETAILERS_VERIFIED}[/] [dim]· {MS_COUNTRIES} {'countries' if is_en else 'países'}[/]"),
        ("MCP tools", f"[bold #00FF88]{mcp_count}[/] [dim]curated[/]"),
        ("API", f"[dim]{_hello_api_host()}[/]"),
        (("Limit/day" if is_en else "Límite/día"), f"[dim]{req_day} req[/]"),
    ]
    info = "\n".join(f"[dim]{k}:[/]{' ' * max(1, 10 - len(k))}{v}" for k, v in info_rows)

    body = f"[bold white]{greeting}[/]\n\n{icon}\n\n{info}"
    return Panel(
        body,
        title=f"[bold #00FF88]CLI Market[/]  [dim]v{PACKAGE_VERSION}[/]",
        border_style="#00FF88",
        box=box.ROUNDED,
        padding=(1, 2),
    )


def _splash_right(is_en: bool) -> Panel:
    tips_hdr = "[bold white]Quick commands[/]" if is_en else "[bold white]Comandos frecuentes[/]"
    tips = [
        ("search",    '"arroz" --country PE'),
        ("compare",   '"leche" --country PE'),
        ("basket",    "arroz:2 aceite:1 --country PE"),
        ("intel brief", "--country PE"),
        ("mcp-setup", "--ide cursor"),
        ("shell",     ""),
    ]
    tips_lines = "\n".join(
        f"  [dim]›[/] [cyan]market {cmd}[/]{' [dim]' + arg + '[/]' if arg else ''}"
        for cmd, arg in tips
    )

    news_hdr = (
        f"[bold white]What's new — v{PACKAGE_VERSION}[/]"
        if is_en
        else f"[bold white]Novedades — v{PACKAGE_VERSION}[/]"
    )
    news = [
        ("REPL", f"40 {'commands' if is_en else 'comandos'} → [cyan]market shell[/]"),
        ("market share", f"referral {'tracking' if is_en else 'con tracking'}"),
        ("market alerts", f"real SQL {'threshold' if is_en else 'threshold'} filter"),
        ("market discover", "· [cyan]market basket[/]"),
    ]
    news_lines = "\n".join(
        f"  [dim]✦[/] [cyan]{k}[/] [dim]—[/] {v}" for k, v in news
    )

    body = f"{tips_hdr}\n{tips_lines}\n\n{news_hdr}\n{news_lines}"
    return Panel(
        body,
        border_style="#30363d",
        box=box.ROUNDED,
        padding=(1, 2),
    )


def _splash_footer(is_en: bool, ctx: dict | None) -> Panel:
    if ctx and ctx.get("valid") and ui.is_pro_tier(ctx.get("tier")):
        msg = (
            "[bold #00FF88]Build Pro[/] [dim]active[/]  [dim]·[/]  "
            "[cyan]market account[/] [dim]for usage[/]  [dim]·[/]  "
            '[cyan]market search "rice" --country PE[/] [dim]to start[/]'
            if is_en else
            "[bold #00FF88]Build Pro[/] [dim]activo[/]  [dim]·[/]  "
            "[cyan]market account[/] [dim]para uso[/]  [dim]·[/]  "
            '[cyan]market search "arroz" --country PE[/] [dim]para empezar[/]'
        )
    elif ctx and ctx.get("valid"):
        msg = (
            "[dim]Starter active[/]  [dim]·[/]  [cyan]market upgrade[/] [dim]for Pro[/]  [dim]·[/]  "
            '[cyan]market search "rice" --country PE[/]'
            if is_en else
            "[dim]Starter activo[/]  [dim]·[/]  [cyan]market upgrade[/] [dim]para Pro[/]  [dim]·[/]  "
            '[cyan]market search "arroz" --country PE[/]'
        )
    else:
        msg = (
            "[cyan]market init[/] [dim]→ activate  ·[/]  "
            "[cyan]market demo[/] [dim]→ live prices without account  ·[/]  "
            "[cyan]market register[/] [dim]→ API key only[/]"
            if is_en else
            "[cyan]market init[/] [dim]→ activar  ·[/]  "
            "[cyan]market demo[/] [dim]→ precios sin cuenta  ·[/]  "
            "[cyan]market register[/] [dim]→ solo API key[/]"
        )
    return Panel(msg, border_style="#30363d", box=box.ROUNDED, padding=(0, 2))


def _render_splash(is_en: bool, ctx: dict | None) -> None:
    """Two-panel welcome screen shared by cmd_hello and cmd_shell."""
    # Top badge line
    mcp_count = _mcp_profile_counts()[0]
    console.print(
        f" [bold #00FF88]CLI Market[/]  [dim]v{PACKAGE_VERSION}[/]  "
        f"[dim]──[/]  [bold]{RETAILERS_VERIFIED}[/] [dim]retailers[/]  "
        f"[dim]──[/]  [bold #00FF88]{mcp_count}[/] [dim]MCP tools[/]  "
        f"[dim]──[/]  [dim]MIT · pip install cli-market-world[/]"
    )
    # Two panels
    console.print(Columns([_splash_left(is_en, ctx), _splash_right(is_en)], equal=False, expand=True))
    # Footer
    console.print(_splash_footer(is_en, ctx))
    console.print()


def _hello_data(is_en: bool, ctx: dict | None = None) -> dict:
    """Structured data for `market hello --json` (agent / machine readable)."""
    platforms = (PLATFORM_LIST_EN if is_en else PLATFORM_LIST_ES).replace("·", " - ")
    mcp_default, mcp_legacy = _mcp_profile_counts()
    pro_active = bool(ctx and ctx.get("valid") and ui.is_pro_tier(ctx.get("tier")))

    onboarding = [
        {"step": 0, "cmd": "market hello", "description": "you are here" if is_en else "estás aquí", "current": True},
        {"step": 1, "cmd": "market init", "description": "account + first search + MCP" if is_en else "cuenta + primera búsqueda + MCP"},
        {"step": 2, "cmd": 'market search "leche" --country PE', "description": "first verified search" if is_en else "primera búsqueda verificada"},
        {"step": 3, "cmd": "market doctor", "description": "readiness %" if is_en else "preparación %"},
        {"step": 4, "cmd": "market register", "description": "optional — sk-... only" if is_en else "opcional — solo sk-...", "optional": True},
    ]
    if pro_active:
        next_steps = ['market search "arroz" --country PE', "market account", "market doctor"]
    elif ctx and ctx.get("valid"):
        next_steps = ['market search "leche" --country PE', "market account", "market doctor"]
    else:
        next_steps = ["market init", "market doctor"]

    payload = {
        "command": "hello",
        "version": PACKAGE_VERSION,
        "lang": "en" if is_en else "es",
        "status": {
            "api": _hello_api_host(),
            "mcp_tools": mcp_default,
            "mcp_tools_legacy": mcp_legacy,
            "mcp_profile": "default",
            "retailers_verified": RETAILERS_VERIFIED,
            "countries": MS_COUNTRIES,
            "prices": PRICES_VERIFIED_LABEL,
            "refresh_hours": PRICES_REFRESH_HOURS,
            "indicators": INDICATORS_COUNT,
            "platforms": platforms,
            "online": True,
        },
        "onboarding": onboarding,
        "capabilities": {
            "coverage": f"{RETAILERS_VERIFIED} verified retailers - {MS_COUNTRIES} countries",
            "data_moat": f"{INDICATORS_COUNT} indicators - kg/L normalized - multi-payment (Yape/Plin/PayPal) - MIT open source",
        },
        "use_cases": [
            'market basket "leche:2 arroz:1" --country PE',
            'market compare "aceite de girasol" --country AR',
            "market intel inflation --country PE",
            "market tools",
            "market intel indicators --country PE",
            "market alerts --action list",
        ],
        "mcp": ui.get_mcp_config(),
        "docs": {
            "quickstart": "https://cli-market.dev/docs#quickstart",
            "tools": "https://cli-market.dev/tools",
        },
        "next_steps": next_steps,
    }
    if ctx:
        payload["auth"] = {
            "session_exists": True,
            "valid": bool(ctx.get("valid")),
            "username": ctx.get("username"),
            "tier": ctx.get("tier"),
            "pro_active": pro_active,
        }
    else:
        payload["auth"] = {"session_exists": False, "pro_active": False}
    return payload


def cmd_hello(args):
    """Post-install activation: show next steps after pip install."""
    is_en = get_lang() == "en"
    ctx = ui.fetch_session_context()

    # Agent / machine-readable path (respects `market --json` and `market hello --json`)
    if ui.is_json_mode():
        data = _hello_data(is_en, ctx)
        ui.emit_json(
            ui.json_response(
                True,
                data,
                next_commands=data.get("next_steps"),
            ),
            console,
        )
        return

    # Human pretty path
    _report_install_event(source="hello")

    if ctx and not ctx.get("valid"):
        stale_user = ctx.get("username") or get_session_username()
        login_cmd = f"market login --username {stale_user}" if stale_user and stale_user != "?" else "market login"
        console.print(Panel.fit(
            f"[yellow]{'Session expired' if is_en else 'Sesión expirada'}.[/] [cyan]{login_cmd}[/]",
            border_style="yellow",
        ))
    elif ctx is None:
        # New user without session: show 3-step onboarding mini-tutorial
        steps = [
            ("1", "market init", "Create free account" if is_en else "Crear cuenta gratuita"),
            ("2", 'market search "arroz"', "Your first search" if is_en else "Tu primera busqueda"),
            ("3", 'market compare "leche"', "Compare prices" if is_en else "Compara precios"),
        ]
        console.print()
        console.print(Panel(
            "[bold]Welcome to CLI Market![/]\n\n"
            + "\n".join(
                f"  [bold #00FF88]{n}[/] [cyan]{cmd}[/]  [dim]{desc}[/]"
                for n, cmd, desc in steps
            )
            + "\n\n[dim]Or run [cyan]market tutorial[/] for a guided walkthrough.",
            border_style=ui.MINT,
        ))
        console.print(
            f"[dim]v{PACKAGE_VERSION}[/]  |  "
            f"{RETAILERS_VERIFIED} retailers  |  {MS_COUNTRIES} countries"
        )
        return

    _render_splash(is_en, ctx)
