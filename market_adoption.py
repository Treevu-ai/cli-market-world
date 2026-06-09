"""PyPI (Pepy) vs onboarding funnel — adoption comparison."""

from __future__ import annotations

from typing import Any

from market_funnel import funnel_summary
from market_pepy import pepy_multi_summary


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


def adoption_recent_users(*, days: int = 30, limit: int = 50) -> dict[str, Any]:
    """Admin view: real users with funnel milestones (smoke filtered)."""
    from market_funnel import funnel_recent_users

    days = max(1, min(days, 90))
    limit = max(1, min(limit, 200))
    users = funnel_recent_users(hours=days * 24, limit=limit, exclude_noise=True)
    return {
        "window_days": days,
        "count": len(users),
        "noise_filter": True,
        "noise_patterns": ["smoke*", "deploy-test*", "shiptest*", "user-<hex>"],
        "users": users,
    }


def adoption_summary(*, days: int = 30) -> dict[str, Any]:
    """Merge Pepy PyPI stats (multi-project: core + world combined) with funnel aggregates (no PII)."""
    days = max(1, min(days, 90))
    pypi_multi = pepy_multi_summary()
    combined = pypi_multi.get("combined", {}) or {}
    by_project = pypi_multi.get("packages", {}) or {}
    projects = pypi_multi.get("projects") or ["cli-market-core", "cli-market-world"]

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

    # Use combined for volume metrics (so index + comparisons see total PyPI traction)
    pypi_30d = combined.get("downloads_last_30d") if combined.get("ok") else None
    pypi_7d = combined.get("downloads_last_7d") if combined.get("ok") else None
    pypi_total = combined.get("total_downloads") if combined.get("ok") else None

    register_per_pypi = _conv(register, pypi_30d) if isinstance(pypi_30d, int) else None
    register_per_install = _conv(register, install)
    search_per_register = _conv(first_search, register)
    install_per_pypi = _conv(install, pypi_30d) if isinstance(pypi_30d, int) else None

    notes: list[str] = []
    if combined.get("ok") and isinstance(pypi_30d, int) and pypi_30d > 0:
        if install == 0:
            notes.append(
                "Sin eventos install en el embudo; Pepy cuenta `pip install`, no telemetría CLI."
            )
        elif install < pypi_30d * 0.1:
            notes.append(
                f"install (embudo) << Pepy 30d ({install:,} vs {pypi_30d:,}) — "
                "la mayoría de descargas PyPI no reportan evento install."
            )
    if not combined.get("ok"):
        notes.append("PyPI (Pepy multi) sin datos.")
    if register > 0 and first_search == 0:
        notes.append("Hay registros sin first_search en la ventana.")

    funnel_conv = funnel.get("conversion", {})
    pricing_health = _conv(activated, first_search)

    # Rich pypi structure: combined for scoring/compat + by_project pulled out for visibility.
    # Flat keys are populated from combined so existing consumers (markdown, slack, old index code) keep working.
    pypi_flat: dict[str, Any] = {
        "ok": bool(combined.get("ok") or pypi_multi.get("ok")),
        "project": " + ".join(projects) if projects else "combined",
        "projects": projects,
        "total_downloads": pypi_total,
        "downloads_last_7d": pypi_7d,
        "downloads_last_30d": pypi_30d,
        "downloads_last_7d_raw": combined.get("downloads_last_7d_raw"),
        "downloads_last_30d_raw": combined.get("downloads_last_30d_raw"),
        "downloads_last_7d_no_ci": combined.get("downloads_last_7d_no_ci"),
        "downloads_last_30d_no_ci": combined.get("downloads_last_30d_no_ci"),
        "ci_share_pct_30d": combined.get("ci_share_pct_30d"),
        "daily_series_14d": combined.get("daily_series_14d") or [],
        "top_versions_30d": combined.get("top_versions_30d") or [],
        "top_version_30d": None,  # not meaningful across packages
        "latest_version": None,
        "windows_source": combined.get("windows_source"),
        "pro_time_range": combined.get("pro_time_range"),
        "combined": {
            "total_downloads": combined.get("total_downloads"),
            "downloads_last_7d": combined.get("downloads_last_7d"),
            "downloads_last_30d": combined.get("downloads_last_30d"),
            "downloads_last_7d_raw": combined.get("downloads_last_7d_raw"),
            "downloads_last_30d_raw": combined.get("downloads_last_30d_raw"),
            "downloads_last_7d_no_ci": combined.get("downloads_last_7d_no_ci"),
            "downloads_last_30d_no_ci": combined.get("downloads_last_30d_no_ci"),
            "ci_share_pct_30d": combined.get("ci_share_pct_30d"),
            "daily_series_14d": combined.get("daily_series_14d"),
            "top_versions_30d": combined.get("top_versions_30d"),
            "windows_source": combined.get("windows_source"),
            "pro_time_range": combined.get("pro_time_range"),
        },
        "by_project": {
            name: {
                "ok": bool(pkg.get("ok")),
                "total_downloads": pkg.get("total_downloads"),
                "downloads_last_7d": pkg.get("downloads_last_7d"),
                "downloads_last_30d": pkg.get("downloads_last_30d"),
                "downloads_last_7d_raw": pkg.get("downloads_last_7d_raw"),
                "downloads_last_30d_raw": pkg.get("downloads_last_30d_raw"),
                "downloads_last_7d_no_ci": pkg.get("downloads_last_7d_no_ci"),
                "downloads_last_30d_no_ci": pkg.get("downloads_last_30d_no_ci"),
                "ci_share_pct_30d": pkg.get("ci_share_pct_30d"),
                "top_version_30d": pkg.get("top_version_30d"),
                "top_versions_30d": pkg.get("top_versions_30d"),
                "latest_version": pkg.get("latest_version"),
            }
            for name, pkg in by_project.items()
            if isinstance(pkg, dict)
        },
    }

    return {
        "window_days": days,
        "pypi": pypi_flat,
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
            "funnel_register_to_search": funnel_conv.get("register_to_search"),
            "funnel_search_to_starter": funnel_conv.get("search_to_starter"),
            "funnel_search_to_pro": funnel_conv.get("search_to_pro"),
            "funnel_pro_to_activated": funnel_conv.get("pro_to_activated"),
            "pricing_health": pricing_health,
        },
        "notes": notes,
        "fetched_at": combined.get("fetched_at") or pypi_multi.get("fetched_at"),
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
        f"_Ventana embudo: **{w}d** · PyPI (core+world combined) vía Pepy · embudo P3 (install → register → search → starter)_",
        "",
        "| Métrica | Valor |",
        "|---|---|",
    ]

    if p.get("ok"):
        lines.append(f"| PyPI total (combined) | {_fmt(p.get('total_downloads'))} |")
        lines.append(f"| PyPI últimos 30d (combined) | {_fmt(p.get('downloads_last_30d'))} |")
        lines.append(f"| PyPI últimos 7d (combined) | {_fmt(p.get('downloads_last_7d'))} |")
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
    ]

    # Pull out per-package PyPI breakdown (in addition to the combined rows in the table above)
    by_proj = p.get("by_project") or {}
    if by_proj:
        lines.append("")
        lines.append("**PyPI por paquete (30d)**")
        for name in sorted(by_proj.keys()):
            pkg = by_proj.get(name) or {}
            d30 = pkg.get("downloads_last_30d")
            if d30 is not None:
                lines.append(f"- {name}: **{_fmt(d30)}**")

    lines += [
        "",
        "**Conversión (embudo vs PyPI)**",
        "",
        f"- Register / PyPI 30d: **{_pct(c.get('register_per_pypi_30d'))}** "
        "_(pip install ≠ registro; referencia de volumen)_",
        f"- Register / install (embudo): **{_pct(c.get('register_per_install'))}**",
        f"- First search / register: **{_pct(c.get('search_per_register'))}**",
        f"- Install / PyPI 30d (cobertura telemetría): **{_pct(c.get('install_per_pypi_30d'))}**",
        "",
        "**Pricing (post-spike)**",
        "",
        f"- search → request_pro: **{_pct(c.get('funnel_search_to_pro'))}**",
        f"- request_pro → activated: **{_pct(c.get('funnel_pro_to_activated'))}**",
        f"- **pricing_health** (activated / search): **{_pct(c.get('pricing_health'))}**",
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

    lines = [f"*Adopción ({w}d)* · PyPI (core+world combined) vs embudo P3", ""]

    if p.get("ok"):
        lines.append(
            f"• PyPI (combined): *{_fmt(p.get('downloads_last_30d'))}* dl 30d · "
            f"*{_fmt(p.get('downloads_last_7d'))}* 7d · total *{_fmt(p.get('total_downloads'))}*"
        )
        if p.get("top_version_30d"):
            lines.append(f"  top versión 30d: `{p['top_version_30d']}`")

        # Pull per-package numbers
        by_proj = p.get("by_project") or {}
        if by_proj:
            pkg_parts = []
            for name in sorted(by_proj.keys()):
                d = by_proj.get(name) or {}
                d30 = d.get("downloads_last_30d")
                if d30 is not None:
                    pkg_parts.append(f"{name}: *{d30:,}*")
            if pkg_parts:
                lines.append("  " + " | ".join(pkg_parts))
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