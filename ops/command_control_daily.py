#!/usr/bin/env python3
"""Command & Control — panel diario founder para CLI Market.

Publica en Slack #command-control-cli-market:
  - Checklist de comandos founder (producto + GTM)
  - KPIs actuales + tendencia visual (sparklines 7–14 días)
  - Estado PAM, go-live, index, collector

Usage:
  python ops/command_control_daily.py              # imprime + guarda snapshot
  python ops/command_control_daily.py --slack      # postea al canal C&C
  python ops/command_control_daily.py --dry-run    # no guarda ni postea
  python ops/command_control_daily.py --remote     # KPIs desde producción

Env:
  SLACK_BOT_TOKEN
  SLACK_CHANNEL_COMMAND_CONTROL   — ID del canal (o auto-resolve por nombre)
  MARKET_API_TOKEN                — dashboard/index remoto
  DASHBOARD_DATA_URL
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import httpx

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from load_env import load_repo_env  # noqa: E402

load_repo_env()

METRICS_DIR = Path(__file__).resolve().parent / "metrics" / "command-control"
HISTORY_FILE = METRICS_DIR / "history.jsonl"
CHANNEL_NAME = "command-control-cli-market"

DASHBOARD_URL = os.getenv(
    "DASHBOARD_DATA_URL",
    "https://cli-market-production.up.railway.app/dashboard/data",
)
API_BASE = os.getenv(
    "MARKET_API_URL",
    DASHBOARD_URL.rsplit("/dashboard/data", 1)[0]
    or "https://cli-market-production.up.railway.app",
)
REPORT_DIR = Path(__file__).resolve().parent / "reports"

FOUNDER_COMMANDS: list[dict[str, Any]] = [
    {
        "block": "🌅 Mañana — producto",
        "items": [
            ("1", "python ops/command_control_daily.py --slack", "Este panel (KPIs + checklist)"),
            ("2", "python ops/daily_briefing.py", "Bitácora producto + contenido → Slack"),
            ("3", "python ops/go_live_check.py --remote", "3 north-star KPIs + alerts"),
            ("4", "python ops/production_acceptance.py --phase user --tier 2", "PAM tier 2 (smoke usuario)"),
        ],
    },
    {
        "block": "📊 Data moat",
        "items": [
            ("5", "python collect_prices.py --report", "Collector KPIs (crudo)"),
            ("6", "curl -H 'Authorization: Bearer $MARKET_API_TOKEN' $API/index/stats", "Golden Records + linkage %"),
            ("7", "python ops/go_live_check.py --remote --json", "JSON para scripts / alertas"),
        ],
    },
    {
        "block": "📣 GTM (cli-market-content)",
        "items": [
            ("8", "cd ../cli-market-content && make today", "Qué publicar hoy (10 canales)"),
            ("9", "make gate && make gate-remote", "Data-gate local + API live"),
            ("10", "make content && make brief", "Copy + briefing LinkedIn"),
            ("11", "make publish day=N", "Marcar día publicado"),
        ],
    },
    {
        "block": "🔁 Semanal / spike",
        "items": [
            ("12", "python ops/production_acceptance.py --tier 2", "PAM completo tier 2"),
            ("13", "python ops/payments_e2e.py", "Rails de pago (PayPal/MP/Yape/Plin)"),
            ("14", "python ops/go_live_check.py --spike --remote", "Post-spike pricing decision"),
            ("15", "cd ../cli-market-content && make week2", "Monetización semana 2"),
        ],
    },
    {
        "block": "🚀 Post-deploy",
        "items": [
            ("16", ".\\ops\\deploy_landing.ps1", "Landing Cloudflare (si UI)"),
            ("17", "Ver ops/PYPI_RELEASE.md", "Release CLI PyPI"),
            ("18", "railway up", "API Railway tras cambios backend"),
        ],
    },
]

BOOKMARKS = [
    ("Landing", "https://cli-market.dev"),
    ("Dashboard", f"{API_BASE}/dashboard"),
    ("Health", f"{API_BASE}/health"),
    ("Health DB", f"{API_BASE}/health/db"),
    ("PyPI", "https://pypi.org/project/cli-market"),
    ("GitHub", "https://github.com/Treevu-ai/cli-market-world"),
]


def _sparkline(values: list[float], *, width: int = 10) -> str:
    """Unicode mini-chart (oldest → newest, left to right)."""
    if not values:
        return "—"
    subset = values[-width:]
    lo, hi = min(subset), max(subset)
    if hi == lo:
        return "▄" * len(subset)
    blocks = "▁▂▃▄▅▆▇█"
    out: list[str] = []
    for v in subset:
        idx = int((v - lo) / (hi - lo) * (len(blocks) - 1))
        out.append(blocks[idx])
    return "".join(out)


def _delta_str(current: float, previous: float | None, *, pct: bool = False) -> str:
    if previous is None:
        return ""
    diff = current - previous
    if pct:
        return f" ({diff:+.1f}pp)"
    if abs(diff) < 1:
        return f" ({diff:+.0f})"
    return f" ({diff:+,.0f})"


def _load_history() -> list[dict[str, Any]]:
    if not HISTORY_FILE.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in HISTORY_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def _save_snapshot(snapshot: dict[str, Any]) -> None:
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.open("a", encoding="utf-8").write(
        json.dumps(snapshot, ensure_ascii=False) + "\n"
    )


def _latest_pam() -> dict[str, Any] | None:
    reports = sorted(REPORT_DIR.glob("pam-*.json"), reverse=True)
    for path in reports[:5]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if "summary" in data or "results" in data:
                return {"file": path.name, **data}
        except Exception:
            continue
    return None


def _pam_summary(pam: dict[str, Any] | None) -> dict[str, Any]:
    if not pam:
        return {"status": "unknown", "pass": 0, "fail": 0, "skip": 0}
    summary = pam.get("summary") or {}
    passed = summary.get("PASS", summary.get("pass", summary.get("passed", 0)))
    failed = summary.get("FAIL", summary.get("fail", summary.get("failed", 0)))
    skipped = summary.get("SKIP", summary.get("skip", summary.get("skipped", 0)))
    status = "ok" if int(failed or 0) == 0 else "fail"
    return {
        "status": status,
        "pass": int(passed or 0),
        "fail": int(failed or 0),
        "skip": int(skipped or 0),
        "file": pam.get("file", ""),
    }


def _fetch_dashboard_remote() -> dict[str, Any] | None:
    token = os.getenv("MARKET_API_TOKEN", "")
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        r = httpx.get(DASHBOARD_URL, headers=headers, timeout=30)
        r.raise_for_status()
        data = r.json()
        return data if isinstance(data, dict) and "error" not in data else None
    except Exception:
        return None


def _fetch_index_stats_remote() -> dict[str, Any] | None:
    token = os.getenv("MARKET_API_TOKEN", "")
    if not token:
        return None
    try:
        r = httpx.get(
            f"{API_BASE}/index/stats",
            headers={"Authorization": f"Bearer {token}"},
            timeout=20,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None


def _fetch_index_stats_local() -> dict[str, Any] | None:
    try:
        from index_gate import index_stats

        return index_stats()
    except Exception:
        return None


def _collect_metrics(*, remote: bool) -> dict[str, Any]:
    today = date.today().isoformat()
    dash = _fetch_dashboard_remote() if remote else None
    if dash is None and not remote:
        try:
            from routers.dashboard import dashboard_data

            dash = dashboard_data()
        except Exception:
            dash = {}

    kpis = (dash or {}).get("kpis", {})
    coll = (dash or {}).get("collector", {})
    moat = (dash or {}).get("moat_summary", {})

    index = (
        _fetch_index_stats_remote()
        if remote
        else _fetch_index_stats_local() or _fetch_index_stats_remote()
    )

    golive_status = "unknown"
    golive_overall = "unknown"
    try:
        from market_golive import go_live_summary

        gl = go_live_summary(days=30, dashboard_data=dash)
        golive_overall = gl.get("overall_status", "unknown")
        golive_status = gl.get("kpis", {}).get("data_moat", {}).get("status", "unknown")
    except Exception:
        pass

    pam = _pam_summary(_latest_pam())

    return {
        "date": today,
        "ts": datetime.now(timezone.utc).isoformat(),
        "source": "remote" if remote else "local",
        "moat": {
            "total_indexed": int(kpis.get("total_indexed", 0) or 0),
            "snapshots_24h": int(kpis.get("snapshots_24h", 0) or 0),
            "stores_indexed": int(kpis.get("stores_indexed", 0) or 0),
            "coverage_7d_pct": float(kpis.get("coverage_7d_pct", 0) or 0),
            "store_success_pct": float(kpis.get("store_success_pct", 0) or 0),
            "healthy_stores": int(kpis.get("healthy_stores", 0) or 0),
            "total_stores": int(kpis.get("total_stores", 0) or 0),
            "collector_status": coll.get("status", "?"),
            "collector_stale": bool(moat.get("collector_stale", False)),
        },
        "index": {
            "registry_size": int((index or {}).get("registry_size", 0) or 0),
            "linkage_pct": float((index or {}).get("linkage_pct", 0) or 0),
            "snapshots_linked": int((index or {}).get("snapshots_linked", 0) or 0),
        },
        "golive": {
            "overall": golive_overall,
            "moat_status": golive_status,
        },
        "pam": pam,
    }


def _trend_section(history: list[dict[str, Any]], current: dict[str, Any]) -> list[str]:
    """Build sparkline rows from historical snapshots."""
    if len(history) < 2:
        return ["_Sin histórico aún — vuelve mañana para ver tendencias._", ""]

    def series(key_path: str) -> list[float]:
        out: list[float] = []
        for row in history:
            node: Any = row
            for part in key_path.split("."):
                node = (node or {}).get(part, {})
            try:
                out.append(float(node))
            except (TypeError, ValueError):
                pass
        return out

    prev = history[-1] if history else {}
    m = current["moat"]
    ix = current["index"]
    pm = prev.get("moat", {})
    pi = prev.get("index", {})

    lines = [
        "*📈 Tendencia* (últimos días · izq=antiguo, der=hoy)",
        "",
        f"• Indexados: `{_sparkline(series('moat.total_indexed'))}` *{m['total_indexed']:,}*"
        f"{_delta_str(m['total_indexed'], pm.get('total_indexed'))}",
        f"• Snap 24h: `{_sparkline(series('moat.snapshots_24h'))}` *{m['snapshots_24h']:,}*"
        f"{_delta_str(m['snapshots_24h'], pm.get('snapshots_24h'))}",
        f"• Coverage 7d: `{_sparkline(series('moat.coverage_7d_pct'))}` *{m['coverage_7d_pct']:.1f}%*"
        f"{_delta_str(m['coverage_7d_pct'], pm.get('coverage_7d_pct'), pct=True)}",
        f"• Golden Records: `{_sparkline(series('index.registry_size'))}` *{ix['registry_size']:,}*"
        f"{_delta_str(ix['registry_size'], pi.get('registry_size'))}",
        f"• Linkage %: `{_sparkline(series('index.linkage_pct'))}` *{ix['linkage_pct']:.1f}%*"
        f"{_delta_str(ix['linkage_pct'], pi.get('linkage_pct'), pct=True)}",
        "",
    ]
    return lines


def build_message(*, remote: bool = False) -> str:
    history = _load_history()
    metrics = _collect_metrics(remote=remote)
    m = metrics["moat"]
    ix = metrics["index"]
    gl = metrics["golive"]
    pam = metrics["pam"]

    status_emoji = {"healthy": "✅", "degraded": "🟡", "critical": "🔴"}.get(
        gl["overall"], "⚪"
    )
    coll_emoji = "🔴" if m["collector_stale"] else "🟢"

    lines = [
        f"🎛️ *Command & Control* · {metrics['date']} · founder ops",
        "",
        f"{status_emoji} *Go-live:* {gl['overall']} · moat {gl['moat_status']}",
        f"{coll_emoji} *Collector:* {m['collector_status']}"
        + (" · _stale_" if m["collector_stale"] else ""),
        "",
        "*📊 KPIs hoy*",
        f"• Moat: *{m['total_indexed']:,}* indexados · *{m['snapshots_24h']:,}* (24h) · "
        f"*{m['stores_indexed']}* tiendas · coverage *{m['coverage_7d_pct']:.1f}%*",
        f"• Tiendas sanas: *{m['healthy_stores']}/{m['total_stores']}* "
        f"({m['store_success_pct']:.0f}% éxito)",
        f"• Index: *{ix['registry_size']:,}* Golden Records · linkage *{ix['linkage_pct']:.1f}%* "
        f"({ix['snapshots_linked']:,} snapshots)",
        f"• PAM último: *{pam['pass']} PASS / {pam['fail']} FAIL / {pam['skip']} SKIP*"
        + (f" · `{pam['file']}`" if pam.get("file") else ""),
        "",
    ]
    lines.extend(_trend_section(history, metrics))
    lines.append("*✅ Checklist founder (orden sugerido)*")
    lines.append("")
    for block in FOUNDER_COMMANDS:
        lines.append(f"*{block['block']}*")
        for num, cmd, why in block["items"]:
            lines.append(f"`{num}.` `{cmd}`")
            lines.append(f"    _{why}_")
        lines.append("")

    lines.append("*🔗 Bookmarks*")
    for label, url in BOOKMARKS:
        lines.append(f"• <{url}|{label}>")
    lines.append("")
    lines.append(
        "_Bitácora = narrativa diaria · Command & Control = checklist + métricas._ "
        "Actualiza con `python ops/command_control_daily.py --slack`."
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="CLI Market Command & Control panel")
    parser.add_argument("--slack", action="store_true", help="Post to #command-control-cli-market")
    parser.add_argument("--dry-run", action="store_true", help="Print only; no save, no Slack")
    parser.add_argument("--remote", action="store_true", help="Fetch KPIs from production API")
    parser.add_argument("--json", action="store_true", help="JSON metrics snapshot")
    args = parser.parse_args()

    metrics = _collect_metrics(remote=args.remote)

    if args.json:
        print(json.dumps(metrics, indent=2, ensure_ascii=False))
    else:
        print(build_message(remote=args.remote))

    if not args.dry_run:
        _save_snapshot(metrics)

    if args.slack and not args.dry_run:
        from slack_notify import deliver_to_command_control

        deliver_to_command_control(build_message(remote=args.remote))
        print("Slack → command-control-cli-market", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())