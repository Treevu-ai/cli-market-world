#!/usr/bin/env python3
"""API latency benchmark — search endpoint p50/p95.

Usage:
    python3 ops/benchmark_api.py
    python3 ops/benchmark_api.py --base https://cli-market-production.up.railway.app --runs 20
"""

from __future__ import annotations

import argparse
import re
import statistics
import time
import urllib.error
import urllib.request
import json


def validate_url(url: str) -> bool:
    """Validate URL to prevent SSRF attacks. Only allow https:// URLs with valid hostnames."""
    allowed_hosts = [
        "cli-market-production.up.railway.app",
        "localhost",
        "127.0.0.1",
    ]
    # Check if URL starts with https://
    if not url.startswith("https://"):
        # Allow http:// only for localhost in development
        if not url.startswith("http://localhost") and not url.startswith("http://127.0.0.1"):
            return False
    # Check for allowed hosts
    for host in allowed_hosts:
        if host in url:
            return True
    return False


def percentile(values: list[float], pct: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    idx = int(len(ordered) * pct / 100)
    idx = min(idx, len(ordered) - 1)
    return ordered[idx]


def bench_search(base: str, query: str, runs: int) -> dict:
    url = f"{base.rstrip('/')}/products/search"
    body = json.dumps({"query": query, "limit": 5}).encode()
    latencies: list[float] = []
    errors = 0

    for _ in range(runs):
        req = urllib.request.Request(
            url,
            data=body,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        start = time.perf_counter()
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                resp.read()
                if resp.status >= 400:
                    errors += 1
        except (urllib.error.URLError, TimeoutError):
            errors += 1
        else:
            latencies.append((time.perf_counter() - start) * 1000)

    return {
        "endpoint": "/products/search",
        "query": query,
        "runs": runs,
        "ok": len(latencies),
        "errors": errors,
        "p50_ms": round(statistics.median(latencies), 1) if latencies else None,
        "p95_ms": round(percentile(latencies, 95), 1) if latencies else None,
        "max_ms": round(max(latencies), 1) if latencies else None,
        "sla_2s": all(x < 2000 for x in latencies) if latencies else False,
    }


def bench_health(base: str) -> dict:
    start = time.perf_counter()
    with urllib.request.urlopen(f"{base.rstrip('/')}/", timeout=10) as resp:
        data = json.loads(resp.read())
    ms = (time.perf_counter() - start) * 1000
    return {"endpoint": "/", "status": data.get("status"), "latency_ms": round(ms, 1)}


def main() -> None:
    parser = argparse.ArgumentParser(description="CLI Market API benchmark")
    parser.add_argument(
        "--base",
        default="https://cli-market-production.up.railway.app",
        help="API base URL",
    )
    parser.add_argument("--runs", type=int, default=10, help="Search iterations")
    parser.add_argument("--query", default="leche", help="Search query")
    args = parser.parse_args()

    # Validate URL to prevent SSRF
    if not validate_url(args.base):
        print(f"ERROR: Invalid or unauthorized URL: {args.base}")
        print("Allowed URLs: https://cli-market-production.up.railway.app, localhost, 127.0.0.1")
        raise SystemExit(1)

    print(f"Benchmark: {args.base}")
    health = bench_health(args.base)
    print(json.dumps({"health": health}, indent=2))

    search = bench_search(args.base, args.query, args.runs)
    print(json.dumps({"search": search}, indent=2))

    if search["p95_ms"] and search["p95_ms"] > 2000:
        print("WARN: p95 exceeds 2s SLA")
        raise SystemExit(1)
    if search["errors"] > args.runs // 2:
        print("WARN: too many errors")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
