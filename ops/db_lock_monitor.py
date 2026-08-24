#!/usr/bin/env python3
"""
DB Lock & Collector Freshness Monitor.

Catches the failure mode behind the 2026-07-09 incident: an ops/backfill
script left an `idle in transaction` Postgres session holding row locks on
price_snapshots, silently blocking the collector's UPSERTs for one store
(no error surfaced anywhere except collector logs — required manual
`pg_stat_activity` inspection to find). This script automates that check.

Alerts to Slack #alertas when:
  - Any session has been idle-in-transaction longer than --max-idle-minutes
    (default 5 — legitimate transactions on this codebase commit in
    milliseconds to low seconds; anything idle for minutes is stuck).
  - The collector hasn't completed a run in --max-stale-hours (default 6;
    the collect cycle is every 4h, so 6h gives one missed cycle of slack
    before alerting).

Usage:
  python ops/db_lock_monitor.py               # console report
  python ops/db_lock_monitor.py --slack       # report + Slack alert on problems
  python ops/db_lock_monitor.py --json

Integration:
  - Cron: every 15 min (see .github/workflows/db-lock-monitor.yml)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ops"))

try:
    from load_env import load_repo_env
    load_repo_env()
except Exception:
    pass

import httpx

API_BASE = os.getenv("MARKET_API_URL", "https://cli-market-api.fly.dev")
DASHBOARD_URL = f"{API_BASE}/dashboard/data"

MAX_IDLE_MINUTES_DEFAULT = 5
MAX_STALE_HOURS_DEFAULT = 6


def check_idle_transactions(max_idle_minutes: int) -> tuple[list[dict], str | None]:
    """Query pg_stat_activity directly for idle-in-transaction sessions older
    than the threshold. Returns (sessions, error). error is None on success —
    a connection failure is reported as an error string (not silently treated
    as "no problem"), but never raises, so the collector-freshness half still
    runs and the workflow doesn't hard-crash on a transient DB blip."""
    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        return [], "DATABASE_URL not set — idle-transaction check skipped"

    import psycopg2
    import psycopg2.extras

    try:
        conn = psycopg2.connect(
            database_url, connect_timeout=10, sslmode=os.getenv("PG_SSL_MODE", "prefer")
        )
    except Exception as exc:
        return [], f"DB connection failed: {exc}"

    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(
                """
                SELECT pid, usename, state,
                       EXTRACT(EPOCH FROM (now() - xact_start)) / 60 AS idle_minutes,
                       left(query, 200) AS query
                FROM pg_stat_activity
                WHERE state = 'idle in transaction'
                  AND now() - xact_start > (%s || ' minutes')::interval
                ORDER BY xact_start ASC
                """,
                (max_idle_minutes,),
            )
            return [dict(r) for r in cur.fetchall()], None
    except Exception as exc:
        return [], f"query failed: {exc}"
    finally:
        conn.close()


def _parse_ts(raw) -> datetime | None:
    if raw is None:
        return None
    ts = str(raw).replace("Z", "+00:00")
    if " " in ts and "T" not in ts:
        ts = ts.replace(" ", "T", 1)
    try:
        dt = datetime.fromisoformat(ts)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def check_run_clock(max_run_hours: float = 5.0) -> dict | None:
    """COL-8: freshness from /health/collector last_finished (collector_runs)."""
    url = f"{API_BASE}/health/collector"
    try:
        resp = httpx.get(url, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        return {"clock": "collector_runs", "error": f"health/collector fetch failed: {exc}"}

    last_finished = data.get("last_finished") or data.get("last_run")
    dt = _parse_ts(last_finished)
    if dt is None:
        return {"clock": "collector_runs", "error": f"unparseable last_finished: {last_finished}"}
    age_hours = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
    if age_hours > max_run_hours:
        return {
            "clock": "collector_runs",
            "last_finished": last_finished,
            "age_hours": round(age_hours, 1),
            "max_hours": max_run_hours,
            "status": data.get("status"),
        }
    return None


def check_collector_freshness(max_stale_hours: int, *, max_run_hours: float = 5.0) -> dict | None:
    """Dual-clock freshness: snapshot KPI (6h) OR collector_runs (5h).

    Returns a problem dict if either clock is stale/unreachable, else None.
    HTTP /health/collector is the run-clock fallback when the PG proxy is down.
    """
    snapshot_problem = None
    try:
        resp = httpx.get(DASHBOARD_URL, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
        kpis = data.get("kpis", {})
        last_collected_raw = kpis.get("last_collected_at")
        if not last_collected_raw:
            snapshot_problem = {"clock": "snapshot", "error": "last_collected_at missing from dashboard/data"}
        else:
            last_dt = _parse_ts(last_collected_raw)
            if last_dt is None:
                snapshot_problem = {
                    "clock": "snapshot",
                    "error": f"unparseable last_collected_at: {last_collected_raw}",
                }
            else:
                age_hours = (datetime.now(timezone.utc) - last_dt).total_seconds() / 3600
                if age_hours > max_stale_hours:
                    snapshot_problem = {
                        "clock": "snapshot",
                        "last_collected_at": last_collected_raw,
                        "age_hours": round(age_hours, 1),
                        "max_hours": max_stale_hours,
                    }
    except Exception as exc:
        snapshot_problem = {"clock": "snapshot", "error": f"dashboard fetch failed: {exc}"}

    run_problem = check_run_clock(max_run_hours=max_run_hours)
    if snapshot_problem and run_problem:
        return {"clocks": [snapshot_problem, run_problem], "clock": "both"}
    return snapshot_problem or run_problem


def main() -> int:
    ap = argparse.ArgumentParser(description="DB lock and collector freshness monitor")
    ap.add_argument("--max-idle-minutes", type=int, default=MAX_IDLE_MINUTES_DEFAULT)
    ap.add_argument("--max-stale-hours", type=int, default=MAX_STALE_HOURS_DEFAULT)
    ap.add_argument("--slack", action="store_true", help="Post to #alertas on problems")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    idle_sessions, idle_error = check_idle_transactions(args.max_idle_minutes)
    stale = check_collector_freshness(args.max_stale_hours)

    problems = bool(idle_sessions) or bool(stale) or bool(idle_error)

    if args.json:
        print(json.dumps(
            {
                "idle_sessions": idle_sessions,
                "idle_check_error": idle_error,
                "collector_stale": stale,
            },
            default=str, indent=2,
        ))
    else:
        print(f"idle-in-transaction sessions (>{args.max_idle_minutes}min): {len(idle_sessions)}")
        for s in idle_sessions:
            print(f"  pid={s['pid']} idle={s['idle_minutes']:.1f}min query={s['query']!r}")
        if idle_error:
            print(f"idle-transaction check error: {idle_error}")
        if stale:
            print(f"COLLECTOR STALE / CHECK FAILED: {stale}")
        else:
            print("collector: fresh")

    if problems and args.slack:
        lines = ["*DB Lock / Collector Monitor — problema detectado*"]
        if idle_sessions:
            lines.append(f"\n*Sesiones idle-in-transaction (>{args.max_idle_minutes} min):*")
            for s in idle_sessions[:5]:
                lines.append(
                    f"- pid `{s['pid']}` — {s['idle_minutes']:.1f} min — `{s['query'][:120]}`"
                )
            lines.append(
                "\nEsto bloquea los UPSERT del collector (mismo patron del incidente "
                "2026-07-09: backfill script dejo una transaccion sin commit). "
                "Terminar con `SELECT pg_terminate_backend(<pid>);` si no es una "
                "transaccion legitima en curso."
            )
        if idle_error:
            lines.append(f"\n*Chequeo de locks fallo:* {idle_error}")
        if stale:
            clock = stale.get("clock", "unknown")
            if stale.get("clocks"):
                bits = []
                for c in stale["clocks"]:
                    if "error" in c:
                        bits.append(f"{c.get('clock')}: {c['error']}")
                    else:
                        bits.append(
                            f"{c.get('clock')} {c.get('age_hours')}h "
                            f"(umbral {c.get('max_hours')}h)"
                        )
                lines.append("\n*Collector stale (doble reloj):* " + " · ".join(bits))
            elif "error" in stale:
                lines.append(f"\n*Collector check fallo ({clock}):* {stale['error']}")
            else:
                marker = stale.get("last_finished") or stale.get("last_collected_at")
                lines.append(
                    f"\n*Collector stale ({clock}):* edad {stale.get('age_hours')}h "
                    f"(ultimo: {marker}). Ciclo esperado: 4h. "
                    f"Umbral runs=5h / snapshot=6h."
                )

        try:
            from slack_notify import deliver_to_alertas
            deliver_to_alertas("\n".join(lines))
        except Exception as exc:
            print(f"Slack delivery failed: {exc}", file=sys.stderr)

    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
