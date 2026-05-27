#!/usr/bin/env python3
"""CLI Market — Monday Ops Playbook.

Fetches store health from dashboard, filters failing stores (<30% success),
generates outreach drafts, writes a markdown report, optionally pings Slack.

Usage:
  python ops/monday.py                  # full run
  python ops/monday.py --dry-run        # report only, no Slack
  python ops/monday.py --slack <URL>    # override Slack webhook

Env vars:
  DASHBOARD_DATA_URL   default: https://cli-market-production.up.railway.app/dashboard/data
  SLACK_WEBHOOK_URL    optional
"""

from __future__ import annotations

import json, os, sys
from datetime import datetime, timezone
from typing import Any

import httpx

DASHBOARD_URL = os.getenv(
    "DASHBOARD_DATA_URL",
    "https://cli-market-production.up.railway.app/dashboard/data",
)

OUTREACH_ES = """Asunto: {store_name} — reactivar tienda en CLI Market

Hola equipo de {store_name},

CLI Market indexa precios de 27 retailers en 7 paises para agentes de IA.
Tu tienda no responde en los ultimos {failures} ciclos (exito {pct:.0f}%).

Si la API cambio, avisanos. Reactivamos en minutos. Gratis, sin integracion.

Saludos,
Antonio Cuba
CLI Market · cli-market.dev"""

OUTREACH_EN = """Subject: {store_name} — your store on CLI Market needs attention

Hi {store_name} team,

CLI Market indexes prices from 27 retailers across 7 countries for AI agents.
Your store hasn't responded in {failures} collection cycles ({pct:.0f}% success).

If your API changed, let us know. We can reactivate in minutes.

Listing is free. Zero integration. Visibility to AI agents.

Best,
Antonio Cuba
CLI Market · cli-market.dev"""

LOCALE_MAP = {
    "PE": "es", "AR": "es", "MX": "es", "CO": "es", "CL": "es",
    "ES": "es", "IT": "en", "FR": "en", "US": "en", "CH": "en", "BR": "en",
}


def load_store_countries() -> dict[str, str]:
    try:
        spec = __import__("importlib.util", fromlist=[""]).spec_from_file_location("ms", "market_stores.py")
        mod = __import__("importlib.util", fromlist=[""]).module_from_spec(spec)
        spec.loader.exec_module(mod)
        return {k: v.get("country", "??") for k, v in getattr(mod, "STORES", {}).items()}
    except Exception:
        return {}


def fetch_health() -> dict[str, Any]:
    r = httpx.get(DASHBOARD_URL, timeout=30)
    r.raise_for_status()
    return r.json()


def filter_critical(data: dict, countries: dict) -> list[dict]:
    out = []
    for h in data.get("store_health", []):
        pct = float(h.get("success_pct", 0) or 0)
        if pct < 30:
            store_id = h.get("store", "")
            country = countries.get(store_id, "??")
            locale = LOCALE_MAP.get(country, "es")
            out.append({**h, "pct": pct, "country": country, "locale": locale})
    out.sort(key=lambda x: (x["pct"], -int(x.get("consecutive_failures", 0) or 0)))
    return out[:5]


def generate_draft(store: dict) -> str:
    tpl = OUTREACH_ES if store["locale"] == "es" else OUTREACH_EN
    return tpl.format(
        store_name=store["store"],
        pct=store["pct"],
        failures=store.get("consecutive_failures", "?"),
    )


def notify_slack(url: str, text: str) -> None:
    httpx.post(url, json={"text": text}, timeout=10)


def main() -> None:
    dry = "--dry-run" in sys.argv
    slack_url = os.getenv("SLACK_WEBHOOK_URL", "")
    for i, a in enumerate(sys.argv):
        if a == "--slack" and i + 1 < len(sys.argv):
            slack_url = sys.argv[i + 1]

    print("Fetching dashboard...")
    data = fetch_health()
    countries = load_store_countries()
    critical = filter_critical(data, countries)

    now = datetime.now(timezone.utc)
    ds = now.strftime("%Y-%m-%d")
    k = data.get("kpis", {})

    lines = [
        f"# CLI Market — Monday Ops {ds}",
        "",
        f"**Snapshot:** {k.get('total_snapshots',0):,} prices · "
        f"{k.get('active_stores',0)} active stores · {k.get('total_runs',0)} cycles",
        "",
    ]

    if not critical:
        lines.append("## OK — no critical stores (<30% success)")
    else:
        lines.append(f"## {len(critical)} critical stores")
        lines.append("")
        lines.append("| Store | Country | Success | Failures |")
        lines.append("|---|---|---|---|")
        for s in critical:
            lines.append(f"| {s['store']} | {s['country']} | {s['pct']:.0f}% | {s.get('consecutive_failures','?')} |")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## Outreach drafts")
        for s in critical:
            lines.append(f"\n### {s['store']} ({s['country']}) — {s['pct']:.0f}%")
            lines.append("```")
            lines.append(generate_draft(s))
            lines.append("```")

    report = "\n".join(lines)
    os.makedirs("ops/reports", exist_ok=True)
    path = f"ops/reports/{ds}.md"
    with open(path, "w") as f:
        f.write(report)

    if critical:
        print(f"{len(critical)} critical stores. Report: {path}")
    else:
        print(f"No critical stores. Report: {path}")

    if slack_url and not dry:
        msg = (
            "CLI Market Monday Ops: all healthy"
            if not critical
            else f"CLI Market Monday Ops: {len(critical)} stores need attention\n" +
                 "\n".join(f"• {s['store']} ({s['pct']:.0f}%)" for s in critical)
        )
        notify_slack(slack_url, msg)
        print("Slack notified.")
    elif slack_url and dry:
        print("[dry-run] Slack notification skipped.")


if __name__ == "__main__":
    main()
