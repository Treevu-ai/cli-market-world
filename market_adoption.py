"""PyPI (Pepy) vs onboarding funnel — adoption comparison."""

from __future__ import annotations

from typing import Any

from market_funnel import funnel_summary
from market_pepy import pepy_summary


def _conv(num: int, den: int) -> float | None:
    if den <= 0:
        return None
    return round(num / den, 4)


def _pct(rate: float | None) -> str:
    if rate is None:
        return "—"
    return f"{rate * 100:.1f}%"


def _fmt(n: int | None) -> str:
    if n is None:
        return "—"
    return f"{n:,}"


def adoption_summary(*, days: int = 30) -> dict[str, Any]:
    """Merge Pepy PyPI stats with funnel aggregates (no PII)."""
    days = max(1, min(days, 90))
    pepy = pepy_summary()
    funnel = funnel_summary(days=days)

    install = int(funnel["events"].get("install", 0) or 0)
    register = int(
        funnel["funnel_steps"][1]["count"]
        if len(funnel.get("funnel_steps", [])) > 1
        else funnel["events"].get("register", 0) or 0
    )
    first_search = int(funnel["unique_users"].get("with_search", 0) or 0)
    starter = int(funnel["unique_users"].get("with_starter_subscribe", 0) or 0)
    pro_req = int(funnel["unique_users"].get("with_pro_request", 0) or 0)
    activated = int(funnel["unique_users"].get("activated", 0) or 0)

    pypi_30d = pepy.get("downloads_last_30d") if pepy.get("ok") else None
    pypi_7d = pepy.get("downloads_last_7d") if pepy.get("ok") else None
    pypi_total = pepy.get("total_downloads") if pepy.get("ok") else None

    register_per_pypi = _conv(register, pypi_30d) if isinstance(pypi_30d, int) else None
    register_per_install = _conv(register, install)
    search_per_register = _conv(first_search, register)
    install_per_pypi = _conv(install, pypi_30d) if isinstance(pypi_30d, int) else None

    notes: list[str] = []
    if pepy.get("ok") and isinstance(pypi_30d, int) and pypi_30d > 0:
        if install == 0:
            notes.append(
                "Sin eventos install en el embudo; Pepy cuenta `pip install`, no telemetría CLI."
            )
        elif install < pypi_30d * 0.1:
            notes.append(
                f"install (embudo) << Pepy 30d ({install:,} vs {pypi_30d:,}) — "
                "la mayoría de descargas PyPI no reportan evento install."
            )
    if not pepy.get("ok"):
        notes.append(pepy.get("message") or "PyPI (Pepy) sin datos.")
    if register > 0 and first_search == 0:
        notes.append("Hay registros sin first_search en la ventana.")

    return {
        "window_days": days,
        "pypi": {
            "ok": bool(pepy.get("ok")),
            "project": pepy.get("project"),
            "total_downloads": pypi_total,
            "downloads_last_7d": pypi_7d,
            "downloads_last_30d": pypi_30d,
            "downloads_last_30d_no_ci": pepy.get("downloads_last_30d_no_ci"),
            "top_version_30d": pepy.get("top_version_30d"),
            "latest_version": pepy.get("latest_version"),
        },
        "funnel": {
            "install": install,
            "register": register,
            "first_search": first_search,
            "starter_subscribe": starter,
            "request_pro": pro_req,
            "activated": activated,
        },
        "comparison": {
            "register_per_pypi_30d": register_per_pypi,
            "register_per_install": register_per_install,
            "search_per_register": search_per_register,
            "install_per_pypi_30d": install_per_pypi,
            "funnel_register_to_search": funnel["conversion"].get("register_to_search"),
            "funnel_search_to_starter": funnel["conversion"].get("search_to_starter"),
        },
        "notes": notes,
        "fetched_at": pepy.get("fetched_at"),
    }


def adoption_markdown_section(*, days: int = 30) -> str:
    data = adoption_summary(days=days)
    p = data["pypi"]
    f = data["funnel"]
    c = data["comparison"]
    w = data["window_days"]

    lines = [
        "## Adopción",
        "",
        f"_Ventana embudo: **{w}d** · PyPI vía Pepy · embudo P3 (install → register → search → starter)_",
        "",
        "| Métrica | Valor |",
        "|---|---|",
    ]

    if p.get("ok"):
        lines.append(f"| PyPI total | {_fmt(p.get('total_downloads'))} |")
        lines.append(f"| PyPI últimos 30d | {_fmt(p.get('downloads_last_30d'))} |")
        lines.append(f"| PyPI últimos 7d | {_fmt(p.get('downloads_last_7d'))} |")
        if p.get("top_version_30d"):
            lines.append(f"| Top versión 30d | `{p['top_version_30d']}` |")
    else:
        lines.append("| PyPI (Pepy) | sin datos |")

    lines += [
        f"| Embudo install | {_fmt(f['install'])} |",
        f"| Embudo register | {_fmt(f['register'])} |",
        f"| Embudo first_search | {_fmt(f['first_search'])} |",
        f"| Embudo starter_subscribe | {_fmt(f['starter_subscribe'])} |",
        f"| Embudo request_pro | {_fmt(f['request_pro'])} |",
        f"| Embudo activated | {_fmt(f['activated'])} |",
        "",
        "**Conversión (embudo vs PyPI)**",
        "",
        f"- Register / PyPI 30d: **{_pct(c.get('register_per_pypi_30d'))}** "
        "_(pip install ≠ registro; referencia de volumen)_",
        f"- Register / install (embudo): **{_pct(c.get('register_per_install'))}**",
        f"- First search / register: **{_pct(c.get('search_per_register'))}**",
        f"- Install / PyPI 30d (cobertura telemetría): **{_pct(c.get('install_per_pypi_30d'))}**",
        "",
    ]

    for note in data.get("notes") or []:
        lines.append(f"_{note}_")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def adoption_slack_lines(*, days: int = 30) -> list[str]:
    data = adoption_summary(days=days)
    p = data["pypi"]
    f = data["funnel"]
    c = data["comparison"]
    w = data["window_days"]

    lines = [f"*Adopción ({w}d)* · PyPI vs embudo P3", ""]

    if p.get("ok"):
        lines.append(
            f"• PyPI: *{_fmt(p.get('downloads_last_30d'))}* dl 30d · "
            f"*{_fmt(p.get('downloads_last_7d'))}* 7d · total *{_fmt(p.get('total_downloads'))}*"
        )
        if p.get("top_version_30d"):
            lines.append(f"  top versión 30d: `{p['top_version_30d']}`")
    else:
        lines.append("• PyPI: _sin datos Pepy_")

    lines.append(
        f"• Embudo: install *{f['install']}* → register *{f['register']}* → "
        f"search *{f['first_search']}* → starter *{f['starter_subscribe']}*"
    )
    lines.append(
        f"• Conv: register/PyPI30d *{_pct(c.get('register_per_pypi_30d'))}* · "
        f"register/install *{_pct(c.get('register_per_install'))}* · "
        f"search/register *{_pct(c.get('search_per_register'))}*"
    )

    for note in data.get("notes") or []:
        lines.append(f"_{note}_")

    lines.append("")
    return lines