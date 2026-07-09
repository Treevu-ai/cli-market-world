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


def check_collector_freshness(max_stale_hours: int) -> dict | None:
    """Hit the public dashboard endpoint for last_collected_at. Returns a
    problem dict if stale or unreachable, else None."""
    try:
        resp = httpx.get(DASHBOARD_URL, timeout=30.0)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        return {"error": f"dashboard fetch failed: {exc}"}

    kpis = data.get("kpis", {})
    last_collected_raw = kpis.get("last_collected_at")
    if not last_collected_raw:
        return {"error": "last_collected_at missing from dashboard/data"}

    ts = str(last_collected_raw).replace("Z", "+00:00")
    if " " in ts and "T" not in ts:
        ts = ts.replace(" ", "T", 1)
    try:
        last_dt = datetime.fromisoformat(ts)
        if last_dt.tzinfo is None:
            last_dt = last_dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return {"error": f"unparseable last_collected_at: {last_collected_raw}"}

    age_hours = (datetime.now(timezone.utc) - last_dt).total_seconds() / 3600
    if age_hours > max_stale_hours:
        return {"last_collected_at": last_collected_raw, "age_hours": round(age_hours, 1)}
    return None


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
        if stale and "error" not in stale:
            lines.append(
                f"\n*Collector stale:* ultimo run hace {stale['age_hours']}h "
                f"(ultimo: {stale['last_collected_at']}). Ciclo esperado: 4h."
            )
        elif stale and "error" in stale:
            lines.append(f"\n*Collector check fallo:* {stale['error']}")

        try:
            from slack_notify import deliver_to_alertas
            deliver_to_alertas("\n".join(lines))
        except Exception as exc:
            print(f"Slack delivery failed: {exc}", file=sys.stderr)

    return 1 if problems else 0


if __name__ == "__main__":
    raise SystemExit(main())
