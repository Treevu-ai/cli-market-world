#!/usr/bin/env python3
"""CLI Market — Monday Ops Playbook (v2).

Fetches dashboard data. Produces a structured report with:
  TL;DR · Inflation · Price Movers · Store Health · Freshness · Outreach Drafts.

Usage:
  python3 ops/monday.py                  # full run
  python3 ops/monday.py --dry-run        # report only, no Slack
  python3 ops/monday.py --slack <URL>    # override Slack webhook

Env vars:
  DASHBOARD_DATA_URL   default: https://cli-market-production.up.railway.app/dashboard/data
  SLACK_WEBHOOK_URL    optional
"""

from __future__ import annotations

import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

CORE_ROOT = Path(__file__).resolve().parent.parent.parent / "cli-market-core"
if str(CORE_ROOT) not in sys.path:
    sys.path.insert(0, str(CORE_ROOT))

from market_core import market_stats as ms  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content_paths import content_root, metrics_dir  # noqa: E402

DASHBOARD_URL = os.getenv(
    "DASHBOARD_DATA_URL",
    "https://cli-market-production.up.railway.app/dashboard/data",
)

OUTREACH_ES = """Asunto: {store_name} — reactivar tienda en CLI Market

Hola, equipo de {store_name}:

CLI Market indexa precios de 30 retailers en 8 países para agentes de IA.
Su tienda no responde en las últimas {failures} consultas (éxito {pct:.0f}%).
{line} — {country}.

Si la API cambió, avísenos. Reactivamos en minutos. Gratis, sin integración.

Saludos,
Antonio Cuba · CLI Market · cli-market.dev"""

OUTREACH_EN = """Subject: {store_name} — your store on CLI Market needs attention

Hi {store_name} team,

CLI Market indexes prices from 30 retailers across 8 countries for AI agents.
Your store hasn't responded in {failures} queries ({pct:.0f}% success).
{line} — {country}.

If your API changed, let us know. We can reactivate in minutes.
Listing is free. Zero integration. Visibility to AI agents.

Best,
Antonio Cuba · CLI Market · cli-market.dev"""

LOCALE_MAP = {
    "PE": "es", "AR": "es", "MX": "es", "CO": "es", "CL": "es",
    "ES": "es", "IT": "en", "FR": "en", "US": "en", "CH": "en", "BR": "en",
}

LINE_LABELS = {
    "supermercados": "Supermercados",
    "farmacias": "Farmacias y Salud",
    "electro": "Electro",
    "moda": "Moda",
    "hogar": "Hogar",
    "departamentales": "Departamentales",
}


def load_store_meta() -> dict[str, dict[str, str]]:
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("ms", "market_stores.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        stores = getattr(mod, "STORES", {})
        return {
            k: {"country": v.get("country", "??"), "line": v.get("line", "unknown"), "name": v.get("name", k)}
            for k, v in stores.items()
        }
    except Exception:
        return {}


def fetch_data() -> dict[str, Any]:
    r = httpx.get(DASHBOARD_URL, timeout=30)
    r.raise_for_status()
    return r.json()


def tldr(data: dict) -> str:
    k = data.get("kpis", {})
    indexed = k.get("total_indexed", k.get("total_snapshots", 0))
    snap = k.get("snapshots_24h", k.get("total_snapshots", 0))
    active = k.get("stores_indexed", k.get("active_stores", 0))
    runs = k.get("total_runs", 0)

    inflation = data.get("inflation", [])
    rising = [i for i in inflation if i.get("delta_pct", 0) > 0]
    falling = [i for i in inflation if i.get("delta_pct", 0) < 0]
    movers_up = len(data.get("top_risers", []))
    movers_down = len(data.get("top_fallers", []))
    critical_count = sum(
        1 for h in data.get("store_health", [])
        if float(h.get("success_pct", 0) or 0) < 30
    )

    parts = [f"**{indexed:,}** indexados · **{snap:,}** refresh 24h · **{active}** tiendas · **{runs}** ciclos."]
    if rising:
        parts.append(f"📈 Inflación al alza en {len(rising)} líneas (max +{max(i['delta_pct'] for i in rising)}%).")
    if falling:
        parts.append(f"📉 Deflación en {len(falling)} líneas (max {min(i['delta_pct'] for i in falling)}%).")
    if movers_up or movers_down:
        parts.append(f"📊 {movers_up}↑ subieron · {movers_down}↓ bajaron (últimas 24h).")
    if critical_count:
        parts.append(f"🔴 **{critical_count}** tiendas críticas (<30% éxito).")
    else:
        parts.append("✅ Sin tiendas críticas.")
    return "  \n".join(parts)


def build_report(data: dict, meta: dict) -> str:
    now = datetime.now(timezone.utc)
    ds = now.strftime("%Y-%m-%d")

    lines = [
        f"# CLI Market — Monday Ops {ds}",
        "",
        "## TL;DR",
        "",
        tldr(data),
        "",
        "---",
        "",
        "## 📊 Inflación 7d",
        "",
    ]

    inflation = data.get("inflation", [])
    if inflation and any(i.get("delta_pct", 0) != 0 for i in inflation):
        lines.append("| Línea | Avg ahora | Avg antes | Delta |")
        lines.append("|---|---|---|---|")
        for i in inflation:
            delta = i.get("delta_pct", 0) or 0
            lines.append(
                f"| {i['line']} | {(i['avg_now'] or 0):.2f} | {(i['avg_before'] or 0):.2f} | "
                f"{'+' if delta > 0 else ''}{delta:.1f}% |"
            )
    else:
        lines.append("_Sin histórico suficiente (necesita 7+ días de datos)._")

    lines += ["", "---", "", "## 📈 Price Movers (último ciclo)", ""]

    risers = data.get("top_risers", [])[:3]
    fallers = data.get("top_fallers", [])[:3]

    if risers:
        lines.append("### ▲ Subieron")
        lines.append("| Producto | Antes | Ahora | Delta |")
        lines.append("|---|---|---|---|")
        for r in risers:
            lines.append(
                f"| {r['product_id'][:25]} | {(r['price_before'] or 0):.2f} | "
                f"{(r['price_now'] or 0):.2f} | +{r['delta_pct']}% |"
            )
        lines.append("")
    if fallers:
        lines.append("### ▼ Bajaron")
        lines.append("| Producto | Antes | Ahora | Delta |")
        lines.append("|---|---|---|---|")
        for r in fallers:
            lines.append(
                f"| {r['product_id'][:25]} | {(r['price_before'] or 0):.2f} | "
                f"{(r['price_now'] or 0):.2f} | {r['delta_pct']}% |"
            )
        lines.append("")
    if not risers and not fallers:
        lines.append("_Sin datos (necesita 2+ ciclos separados)._")

    lines += ["", "---", "", "## 🏪 Store Health", ""]

    health = data.get("store_health", [])[:15]
    lines.append("| Tienda | País | Línea | Éxito | Estado |")
    lines.append("|---|---|---|---|---|")
    for h in health:
        pct = float(h.get("success_pct", 0) or 0)
        store_id = h.get("store", "")
        info = meta.get(store_id, {})
        country = info.get("country", "??")
        line = LINE_LABELS.get(info.get("line", ""), info.get("line", "?"))
        badge = "✅ OK" if pct >= 90 else ("🟡 WARN" if pct >= 30 else "🔴 DEAD")
        lines.append(f"| {store_id} | {country} | {line} | {pct:.0f}% | {badge} |")

    lines += ["", "---", "", "## ⏱️ Frescura", ""]

    freshness = data.get("freshness", [])[:10]
    if freshness:
        lines.append("| Tienda | Último snapshot |")
        lines.append("|---|---|")
        for f in freshness:
            ts = str(f.get("last_seen", ""))[:19]
            lines.append(f"| {f.get('store_name','?')} | {ts} |")
    else:
        lines.append("_Sin datos._")

    # ── Critical + outreach ─────────────────────────────────────────────
    critical = [
        {**h, "pct": float(h.get("success_pct", 0) or 0)}
        for h in data.get("store_health", [])
        if float(h.get("success_pct", 0) or 0) < 30
    ]

    if critical:
        lines += ["", "---", "", "## 🔴 Tiendas críticas (<30% éxito)", ""]
        lines.append("| Tienda | País | Línea | Éxito | Fallos |")
        lines.append("|---|---|---|---|---|")
        for s in sorted(critical, key=lambda x: x["pct"]):
            sid = s.get("store", "")
            info = meta.get(sid, {})
            country = info.get("country", "??")
            line = LINE_LABELS.get(info.get("line", ""), info.get("line", "?"))
            lines.append(
                f"| {sid} | {country} | {line} | {s['pct']:.0f}% | "
                f"{s.get('consecutive_failures','?')} |"
            )

        lines += ["", "---", "", "## ✉️ Outreach Drafts", ""]
        for s in sorted(critical, key=lambda x: x["pct"]):
            sid = s.get("store", "")
            info = meta.get(sid, {})
            country = info.get("country", "??")
            line = LINE_LABELS.get(info.get("line", ""), info.get("line", "?"))
            locale = LOCALE_MAP.get(country, "es")
            tpl = OUTREACH_ES if locale == "es" else OUTREACH_EN
            store_name = info.get("name", sid)
            draft = tpl.format(
                store_name=store_name,
                pct=s["pct"],
                failures=s.get("consecutive_failures", "?"),
                country=country,
                line=line,
            )
            lines.append(f"### {store_name} ({country}, {line}) — {s['pct']:.0f}%")
            lines.append("```")
            lines.append(draft)
            lines.append("```")
            lines.append("")
    else:
        lines += ["", "---", "", "## ✅ Sin tiendas críticas", ""]

    return "\n".join(lines)


def _iso_week(now: datetime) -> str:
    return f"{now.isocalendar().year}-W{now.isocalendar().week:02d}"


def build_price_pulse(data: dict, meta: dict) -> str:
    """LinkedIn-ready weekly metrics file (GTM metrics/price-pulse-YYYY-WW.md)."""
    now = datetime.now(timezone.utc)
    week = _iso_week(now)
    ds = now.strftime("%Y-%m-%d")
    k = data.get("kpis", {})
    total = k.get("total_stores") or len(meta)
    healthy = k.get("healthy_stores", 0)
    success_pct = k.get("store_success_pct", 0)
    indexed = k.get("total_indexed", k.get("total_snapshots", 0))
    snapshots = k.get("snapshots_24h", k.get("total_snapshots", 0))
    active = k.get("stores_indexed", k.get("active_stores", 0))
    fresh_24h = k.get("stores_fresh_24h", k.get("active_stores", 0))
    coverage_7d = k.get("coverage_7d_pct", 0)
    moat = data.get("moat_summary", {})
    runs = k.get("total_runs", 0)
    coll = data.get("collector", {})

    critical = [
        h for h in data.get("store_health", [])
        if float(h.get("success_pct", 0) or 0) < 30
    ]

    lines = [
        "---",
        f"week: {week}",
        f"updated: {ds}",
        "---",
        "",
        f"# Price Pulse — Semana {week.split('-W')[1]}",
        "",
        "## Collector",
        f"- Moat indexado: **{indexed:,}** precios · **{active}** tiendas con datos",
        f"- Refresh 24h: **{snapshots:,}** · tiendas fresh: **{fresh_24h}**",
        f"- Coverage 7d: **{coverage_7d}%**",
        f"- Stores success lifetime (≥80%): **{healthy} / {total}** ({success_pct}%)",
        f"- Collector runs: **{runs}**",
        f"- Last run status: **{coll.get('status', 'unknown')}**",
        f"- Moat stale: **{moat.get('collector_stale', False)}**",
        "",
        "## Data stories (auto)",
        f"- Precios en moat: **{indexed:,}**",
        f"- Refresh 24h: **{snapshots:,}** · retailers fresh: **{fresh_24h}**",
        "",
        "## Marketing",
        "- LinkedIn impressions:",
        "- PyPI installs (week):",
        "- Landing → Pro requests:",
        "",
        "## Product",
        "- Self-serve signups:",
        "- Pro activations (manual):",
        "",
        "## Tiendas críticas (<30%)",
    ]
    if critical:
        for h in critical[:10]:
            sid = h.get("store", "?")
            info = meta.get(sid, {})
            lines.append(
                f"- {info.get('name', sid)} ({info.get('country', '??')}): "
                f"{float(h.get('success_pct', 0) or 0):.0f}%"
            )
    else:
        lines.append("- Ninguna en catálogo activo ✅")

    lines += [
        "",
        "## Hook LinkedIn (copiar)",
        "",
        f"Esta semana: **{snapshots:,}** precios frescos · **{active}** retailers activos · "
        f"**{healthy}/{total}** tiendas saludables. Un solo `{ms.PIP_INSTALL_CMD}`.",
        "",
        "Fuente: `/dashboard/data` · [[GTM-Hub]]",
        "",
    ]
    return "\n".join(lines)


def notify_slack(url: str, text: str) -> None:
    httpx.post(url, json={"text": text}, timeout=10)


def main() -> None:
    dry = "--dry-run" in sys.argv
    slack_url = os.getenv("SLACK_WEBHOOK_URL", "")
    for i, a in enumerate(sys.argv):
        if a == "--slack" and i + 1 < len(sys.argv):
            slack_url = sys.argv[i + 1]

    print("Fetching dashboard...")
    data = fetch_data()
    meta = load_store_meta()
    report = build_report(data, meta)
    pulse = build_price_pulse(data, meta)

    now = datetime.now(timezone.utc)
    ds = now.strftime("%Y-%m-%d")
    week = _iso_week(now)
    reports_dir = content_root() / "generated" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    metrics_dir().mkdir(parents=True, exist_ok=True)
    path = reports_dir / f"{ds}.md"
    pulse_path = metrics_dir() / f"price-pulse-{week}.md"
    path.write_text(report, encoding="utf-8")
    pulse_path.write_text(pulse, encoding="utf-8")

    critical_count = sum(
        1 for h in data.get("store_health", [])
        if float(h.get("success_pct", 0) or 0) < 30
    )

    print(f"Report written: {path}" + (" [dry-run]" if dry else ""))
    print(f"Price pulse: {pulse_path}" + (" [dry-run]" if dry else ""))

    if slack_url and not dry:
        k = data.get("kpis", {})
        msg = (
            f"📊 CLI Market Monday Ops {ds}\n"
            f"{k.get('total_indexed', k.get('total_snapshots',0)):,} indexados · "
            f"{k.get('snapshots_24h', k.get('total_snapshots',0)):,} 24h · "
            f"{k.get('stores_indexed', k.get('active_stores',0))} tiendas\n"
        )
        if critical_count:
            msg += f"🔴 {critical_count} tiendas críticas:\n"
            for h in data.get("store_health", []):
                pct = float(h.get("success_pct", 0) or 0)
                if pct < 30:
                    msg += f"• {h.get('store','?')} ({pct:.0f}%)\n"
        else:
            msg += "✅ Todas las tiendas saludables.\n"
        msg += f"Reporte: {path}\nPrice pulse: {pulse_path}"
        notify_slack(slack_url, msg)
        print("Slack notified.")


if __name__ == "__main__":
    main()
