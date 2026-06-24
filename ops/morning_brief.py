#!/usr/bin/env python3
"""
Post del día → #command-control-cli-market con métricas live baked in.

Corre DESPUÉS de gtm-briefing en morning-ops-chain.yml (13:30 UTC aprox).
Postea el post de LinkedIn listo para copiar-pegar, sin abrir #publicaciones.

Uso:
  python3 ops/morning_brief.py --slack --remote   # → #command-control (cron)
  python3 ops/morning_brief.py --dry-run          # imprime sin postear
  python3 ops/morning_brief.py --date 2026-06-25  # override fecha

Env:
  SLACK_BOT_TOKEN
  SLACK_CHANNEL_COMMAND_CONTROL   (default C0B8U1SNM45)
  MARKET_API_URL
  MARKET_API_TOKEN
  CLI_MARKET_CONTENT_DIR          (path al checkout del content repo)
  LINKEDIN_CAMPAIGN_START         (default 2026-06-01)
  LINKEDIN_PERSONAL_DAY_OFFSET    (default 0)
  LINKEDIN_COMPANY_DAY_OFFSET     (default -1)
  LINKEDIN_POST_UTC_HOUR          (default 13)
"""

from __future__ import annotations

import argparse
import os
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from load_env import load_repo_env  # noqa: E402

load_repo_env()

DIVIDER = "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
_API_BASE = os.getenv("MARKET_API_URL", "https://cli-market-production.up.railway.app")


# ── Dashboard ─────────────────────────────────────────────────────────────────

def _fetch_dashboard() -> dict[str, Any]:
    try:
        import httpx

        token = os.getenv("MARKET_API_TOKEN", "")
        url = f"{_API_BASE}/dashboard/data"
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        r = httpx.get(url, headers=headers, timeout=30)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict) and "error" not in data:
                return data
    except Exception:
        pass
    return {}


# ── Post builder ──────────────────────────────────────────────────────────────

def build_post_del_dia(
    dashboard_data: dict[str, Any],
    for_date: date,
) -> str | None:
    """Return compact Slack message with today's post (live metrics baked in).

    Returns None when content repo is unavailable or no post is scheduled.
    """
    try:
        from publish_pack import (
            CAMPAIGN_START,
            channels_for_date,
            marketing_metrics_from_dashboard,
            _load_channel_md,
            apply_live_metrics,
            slack_copy_block,
        )
    except ImportError:
        return None

    start = date.fromisoformat(CAMPAIGN_START)
    campaign_day = (for_date - start).days + 1

    items = channels_for_date(for_date, campaign_day)
    if not items:
        return None

    metrics = marketing_metrics_from_dashboard(dashboard_data)
    gate_ok = bool(metrics.get("gate_pass"))
    gate_icon = "✅" if gate_ok else "⛔"
    gate_label = "ABIERTO" if gate_ok else "CERRADO — usar post contingencia"
    moat_line = (
        f"*{metrics['total_indexed']:,}* indexados · "
        f"*{metrics['snapshots_24h']:,}* refresh 24h · "
        f"*{metrics['stores_indexed']}* retailers · "
        f"*{metrics['coverage_7d_pct']:.0f}%* coverage 7d · "
        f"collector `{metrics['collector_status']}`"
    )

    lines = [
        DIVIDER,
        f"📋 *BRIEF MATUTINO* · `{for_date.isoformat()}` · Día *{campaign_day}* de campaña",
        "",
        f"{gate_icon} Data-gate *{gate_label}*",
        f"• {moat_line}",
        "",
    ]

    found = False
    for label, path in items:
        copy = _load_channel_md(path)
        if not copy:
            continue

        post_raw = copy.post or ""
        comment_raw = copy.comment or ""
        post_body = apply_live_metrics(post_raw, metrics, dashboard_data=dashboard_data) if post_raw else ""
        comment_body = apply_live_metrics(comment_raw, metrics, dashboard_data=dashboard_data) if comment_raw else ""

        gate_warn = ""
        if copy.data_gated and not gate_ok:
            gate_warn = "⛔ _Data-gated — NO publicar hasta gate abierto._"

        lines.append(f"*{label}* · `{copy.path_label}` · `{copy.status}`")
        if gate_warn:
            lines.append(gate_warn)
            lines.append("")

        if post_body:
            lines.append("*Post (copy-paste):*")
            lines.append(slack_copy_block(post_body))
            lines.append("")

        if comment_body:
            lines.append("*Primer comentario:*")
            lines.append(slack_copy_block(comment_body))
            lines.append("")

        found = True

    if not found:
        return None

    lines += [
        f"✅ _Cerrar GTM:_ `cd cli-market-content && make publish date={for_date.isoformat()}`",
        DIVIDER,
    ]
    return "\n".join(lines)


# ── Entry point ───────────────────────────────────────────────────────────────

def run(
    *,
    for_date: date,
    remote: bool = True,
    dry_run: bool = False,
) -> dict[str, Any]:
    dashboard_data = _fetch_dashboard() if remote else {}
    msg = build_post_del_dia(dashboard_data, for_date)

    if dry_run:
        if msg:
            print(msg)
        else:
            print(f"⚠️  Sin post programado para {for_date} o content repo no disponible.")
        return {"ok": True, "dry_run": True, "found": bool(msg)}

    if not msg:
        print(f"⚠️  Sin post programado para {for_date} — nada que postear.", file=sys.stderr)
        return {"ok": True, "found": False}

    from slack_notify import deliver_to_command_control

    deliver_to_command_control(msg)
    print(f"✅ Morning brief enviado a #command-control-cli-market", file=sys.stderr)
    return {"ok": True, "found": True, "posted": True}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--slack", action="store_true", help="Post to #command-control-cli-market")
    parser.add_argument("--dry-run", action="store_true", help="Print only; no Slack")
    parser.add_argument("--remote", action="store_true", help="Fetch live KPIs from production API")
    parser.add_argument("--date", default=date.today().isoformat(), help="YYYY-MM-DD (default: today)")
    args = parser.parse_args()

    for_date = date.fromisoformat(args.date)
    dry = args.dry_run or not args.slack
    result = run(for_date=for_date, remote=args.remote, dry_run=dry)
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
