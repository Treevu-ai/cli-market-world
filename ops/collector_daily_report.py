#!/usr/bin/env python3
"""
Collector Daily Report — resumen automático del barrido de precios.

Muestra:
- Último collector run: stores_succeeded / attempted + precios.
- Salud actual: ok / partial / consec failures.
- Top tiendas problemáticas (bajo success_pct o alto consecutive).
- Tendencia simple si hay historial.

Usage (como los demás daily):
  python ops/collector_daily_report.py                 # imprime + guarda snapshot
  python ops/collector_daily_report.py --slack         # postea (bitácora por defecto)
  python ops/collector_daily_report.py --dry-run       # solo imprime
  python ops/collector_daily_report.py --remote        # fuerza endpoints prod (default)

Integración:
  - Se puede llamar desde command_control_daily.py
  - Schedule vía GitHub Action o curl al /admin/cron (similar a command-control)
  - Guarda historial en ops/metrics/collector-daily/history.jsonl (opcional)

Canales recomendados:
  --channel bitacora   (salud producto)
  --channel command-control
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
sys.path.insert(0, str(ROOT / "ops"))

try:
    from load_env import load_repo_env
    load_repo_env()
except Exception:
    pass

try:
    from slack_notify import (
        channel_bitacora,
        channel_command_control,
        deliver_to_bitacora,
        post_via_bot,
    )
except Exception:
    channel_bitacora = lambda: ""
    channel_command_control = lambda: ""
    deliver_to_bitacora = None
    post_via_bot = None

API_BASE = os.getenv(
    "MARKET_API_URL",
    "https://cli-market-production.up.railway.app",
)
DASHBOARD_URL = os.getenv("DASHBOARD_DATA_URL", f"{API_BASE}/dashboard/data")
COLLECTOR_HEALTH_URL = f"{API_BASE}/health/collector"
SOURCES_HEALTH_URL = f"{API_BASE}/v1/sources/health"

METRICS_DIR = ROOT / "ops" / "metrics" / "collector-daily"
HISTORY_FILE = METRICS_DIR / "history.jsonl"
DAILY_DIR = ROOT / "ops" / "daily"


def _fetch_json(url: str, timeout: int = 45) -> dict[str, Any] | None:
    try:
        token = os.getenv("MARKET_API_TOKEN", "").strip()
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        r = httpx.get(url, headers=headers, timeout=timeout)
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict) and "error" not in data:
            return data
    except Exception as e:
        print(f"[collector-daily] fetch error {url}: {e}", file=sys.stderr)
    return None


def _get_last_run() -> dict[str, Any]:
    data = _fetch_json(COLLECTOR_HEALTH_URL) or {}
    return {
        "attempted": data.get("stores_attempted", 0),
        "succeeded": data.get("stores_succeeded", 0),
        "prices": data.get("prices_collected", 0),
        "last_finished": data.get("last_finished"),
        "age_hours": data.get("age_hours"),
        "status": data.get("status", "unknown"),
    }


def _get_store_health() -> list[dict[str, Any]]:
    data = _fetch_json(SOURCES_HEALTH_URL) or {}
    stores = data.get("stores", []) or []
    # enrich with simple rank
    for s in stores:
        s["_score"] = s.get("success_pct", 0)
    return sorted(stores, key=lambda x: (x.get("_score", 0), x.get("store", "")))


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


def _load_success_series(max_points: int = 14) -> list[float]:
    """Load recent yield success % from history.jsonl (for sparkline)."""
    if not HISTORY_FILE.exists():
        return []
    series: list[float] = []
    try:
        for line in HISTORY_FILE.read_text(encoding="utf-8").splitlines()[-max_points:]:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
                lr = rec.get("last_run", {})
                att = lr.get("attempted", 0)
                suc = lr.get("succeeded", 0)
                if att > 0:
                    series.append(round(suc / att * 100, 1))
            except Exception:
                continue
    except Exception:
        pass
    return series


def _summarize(stores: list[dict[str, Any]]) -> dict[str, Any]:
    total = len(stores)
    ok = [s for s in stores if s.get("state") == "ok" or s.get("success_pct", 0) >= 80]
    partial = [s for s in stores if s.get("state") == "partial" or (0 < s.get("success_pct", 0) < 80)]
    high_consec = sorted(
        [s for s in stores if s.get("consecutive_failures", 0) >= 3],
        key=lambda x: -x.get("consecutive_failures", 0),
    )[:5]
    worst = sorted(stores, key=lambda x: x.get("success_pct", 100))[:8]
    return {
        "total": total,
        "ok_count": len(ok),
        "partial_count": len(partial),
        "high_consec": high_consec,
        "worst": worst,
    }


def _format_report(last_run: dict, summary: dict, stores: list[dict], success_series: list[float]) -> str:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    succ = last_run.get("succeeded", 0)
    att = last_run.get("attempted", 0)
    pct = (succ / att * 100) if att else 0.0

    lines = []
    lines.append(f"# Collector Daily — {now[:10]}")
    lines.append("")
    lines.append("## Último barrido")
    lines.append(f"- **{succ}/{att} tiendas** respondieron con precios ({pct:.1f}%)")
    lines.append(f"- Precios recolectados: **{last_run.get('prices', 0):,}**")
    lines.append(f"- Estado: {last_run.get('status')} | edad ~{last_run.get('age_hours', '?')}h")
    if last_run.get("last_finished"):
        lines.append(f"- Finished: {last_run['last_finished']}")
    lines.append("")

    # Sparkline trend
    spark = _sparkline(success_series)
    trend_note = " (building history — run daily to populate)" if len(success_series) < 3 else ""
    lines.append("## Tendencia yield % (últimos barridos)")
    lines.append(f"- `{spark}`  últimos {len(success_series)} runs{trend_note}")
    lines.append("")

    lines.append("## Salud por fuente (store_health)")
    lines.append(f"- ok: **{summary['ok_count']}** | partial: **{summary['partial_count']}** | total: {summary['total']}")
    lines.append("- store_success_pct global ≈ 50% (ver dashboard)")
    lines.append("")

    if summary["high_consec"]:
        lines.append("### ⚠️ Consecutive failures altos (≥3)")
        for s in summary["high_consec"]:
            lines.append(f"- {s['store']}: {s.get('consecutive_failures')} consec | {s.get('success_pct',0):.1f}% | last_err {str(s.get('last_error',''))[:16]}")
        lines.append("")

    lines.append("### Tiendas con menor success_pct (peores 8)")
    for s in summary["worst"]:
        consec = s.get("consecutive_failures", 0)
        flag = "🔴" if consec >= 5 else ("🟡" if consec >= 2 or s.get("success_pct", 100) < 65 else "🟢")
        lines.append(f"- {flag} {s['store']:22} {s.get('success_pct',0):5.1f}%  consec={consec:2d}  last_succ={str(s.get('last_success',''))[:10]}")

    lines.append("")
    lines.append("## Acciones recomendadas")
    lines.append("- Revisar nunaorganica_pe (Woo pilot) + tiendas con alto consec.")
    lines.append("- Ver rotación de queries y posibles rate limits en supermercados grandes.")
    lines.append("- `python ops/analyze_batch_gaps.py` y `ops/investigate_collector.py` para detalle.")
    lines.append("- `python ops/collector_daily_report.py --slack` para este mismo resumen.")
    lines.append("")
    lines.append("Fuentes: /health/collector + /v1/sources/health")

    return "\n".join(lines)


def _save_daily(report_md: str, day: str | None = None) -> Path:
    day = day or date.today().isoformat()
    DAILY_DIR.mkdir(parents=True, exist_ok=True)
    path = DAILY_DIR / f"{day}-collector.md"
    path.write_text(report_md + "\n", encoding="utf-8")
    return path


def _save_history(snapshot: dict[str, Any]) -> None:
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    HISTORY_FILE.open("a", encoding="utf-8").write(
        json.dumps(snapshot, ensure_ascii=False) + "\n"
    )


def _post_slack(text: str, channel: str | None = None) -> bool:
    if not post_via_bot:
        print("[collector-daily] slack_notify no disponible (sin deps o token)")
        return False
    token = os.getenv("SLACK_BOT_TOKEN", "").strip()
    if not token:
        print("[collector-daily] SLACK_BOT_TOKEN no configurado")
        return False
    ch = channel or channel_bitacora() or channel_command_control()
    try:
        post_via_bot(token, ch, text)
        print(f"[collector-daily] posted to {ch}")
        return True
    except Exception as e:
        print(f"[collector-daily] slack post failed: {e}", file=sys.stderr)
        return False


def main() -> int:
    ap = argparse.ArgumentParser(description="Daily collector health & sweep report")
    ap.add_argument("--slack", action="store_true", help="Post to Slack (bitácora o command-control)")
    ap.add_argument("--channel", choices=["bitacora", "command-control"], default=None)
    ap.add_argument("--dry-run", action="store_true", help="Solo imprimir, no guardar ni postear")
    ap.add_argument("--remote", action="store_true", help="Forzar endpoints de producción (default)")
    args = ap.parse_args()

    last = _get_last_run()
    stores = _get_store_health()
    summ = _summarize(stores)
    success_series = _load_success_series()

    # enrich snapshot with current yield pct for better trends
    att = last.get("attempted", 0)
    suc = last.get("succeeded", 0)
    last["yield_pct"] = round(suc / att * 100, 1) if att > 0 else None

    report = _format_report(last, summ, stores, success_series)
    print(report)

    snapshot = {
        "date": date.today().isoformat(),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "last_run": last,
        "summary": {k: summ[k] for k in ("ok_count", "partial_count", "total")},
        "worst_stores": [s["store"] for s in summ["worst"][:5]],
        "high_consec": [(s["store"], s.get("consecutive_failures")) for s in summ["high_consec"]],
        "yield_pct": last.get("yield_pct"),
    }

    if not args.dry_run:
        try:
            path = _save_daily(report)
            print(f"[collector-daily] saved: {path}")
        except Exception as e:
            print(f"[collector-daily] save daily failed: {e}", file=sys.stderr)

        try:
            _save_history(snapshot)
        except Exception as e:
            print(f"[collector-daily] save history failed: {e}", file=sys.stderr)

    if args.slack and not args.dry_run:
        ch_name = args.channel or "bitacora"
        ch = channel_bitacora() if ch_name == "bitacora" else channel_command_control()
        _post_slack(report, ch)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
