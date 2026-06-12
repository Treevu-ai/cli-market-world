#!/usr/bin/env python3
"""Price Pulse async job worker — drains intel_jobs queue.

Usage:
  python3 ops/price_pulse_worker.py              # process one job and exit
  python3 ops/price_pulse_worker.py --loop       # poll until idle
  python3 ops/price_pulse_worker.py --job-id PP-ABC123  # reprocess specific job

Requires DATABASE_URL (or local SQLite) and dashboard data reachable.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import httpx

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

REPORTS_DIR = Path(__file__).resolve().parent / "generated" / "reports"
POLL_SECS = int(os.getenv("PRICE_PULSE_POLL_SECS", "30"))


def _ensure_db() -> None:
    from market_core import ensure_db_initialized

    ensure_db_initialized()


def _generate_report(country: str) -> tuple[str, Path]:
    """Build markdown report from dashboard data; return (text, path)."""
    ops_dir = Path(__file__).resolve().parent
    if str(ops_dir) not in sys.path:
        sys.path.insert(0, str(ops_dir))
    from price_pulse_client import build_client_report, fetch_data

    local = os.getenv("MARKET_API_URL", "").startswith("http://127.0.0.1")
    data = fetch_data(local=local)
    report = build_client_report(data, country=country or None)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    ds = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    cc = (country or "PE").upper()[:2]
    path = REPORTS_DIR / f"price-pulse-{cc}-{ds}.md"
    path.write_text(report, encoding="utf-8")
    return report, path


def _notify_callback(callback_url: str, job: dict) -> None:
    url = (callback_url or "").strip()
    if not url:
        return
    try:
        httpx.post(url, json=job, timeout=15)
    except Exception as exc:
        print(f"  ⚠️  callback failed: {exc}", file=sys.stderr)


def process_job(job: dict) -> bool:
    from market_core.intel_jobs import db_update_intel_job

    job_id = job["job_id"]
    country = job.get("country") or "PE"
    print(f"▶ {job_id} ({country})")

    db_update_intel_job(job_id, progress=10, progress_label="fetching_dashboard")
    try:
        _, path = _generate_report(country)
    except Exception as exc:
        db_update_intel_job(
            job_id,
            status="failed",
            progress=100,
            progress_label="error",
            error=str(exc)[:500],
        )
        print(f"  ❌ failed: {exc}", file=sys.stderr)
        return False

    db_update_intel_job(
        job_id,
        status="completed",
        progress=100,
        progress_label="done",
        output_path=str(path.resolve()),
    )
    updated = dict(job)
    updated.update({"status": "completed", "output_path": str(path.resolve()), "progress": 100})
    _notify_callback(job.get("callback_url") or "", updated)
    print(f"  ✅ {path}")
    return True


def run_once(*, job_id: str | None = None) -> bool:
    from market_core.intel_jobs import db_claim_next_intel_job, db_get_intel_job, db_update_intel_job

    _ensure_db()
    if job_id:
        job = db_get_intel_job(job_id)
        if not job:
            print(f"Job not found: {job_id}", file=sys.stderr)
            return False
        if job.get("status") not in ("queued", "failed"):
            print(f"Job {job_id} status={job.get('status')} — skip")
            return False
        db_update_intel_job(job_id, status="running", progress=0, progress_label="starting", error="")
        job = db_get_intel_job(job_id) or job
    else:
        job = db_claim_next_intel_job("price_pulse")
    if not job:
        return False
    return process_job(job)


def main() -> None:
    parser = argparse.ArgumentParser(description="Price Pulse intel_jobs worker")
    parser.add_argument("--loop", action="store_true", help="Poll queue until idle")
    parser.add_argument("--job-id", default="", help="Process a specific job id")
    args = parser.parse_args()

    if args.loop:
        print(f"Polling intel_jobs every {POLL_SECS}s (Ctrl+C to stop)")
        while True:
            if not run_once(job_id=args.job_id or None):
                time.sleep(POLL_SECS)
            elif args.job_id:
                break
    else:
        ok = run_once(job_id=args.job_id or None)
        if not ok and not args.job_id:
            print("No queued jobs")
        sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
