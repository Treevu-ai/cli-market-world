---
title: API Performance Baseline
tags:
  - gtm
  - perf
  - qa
hub: "[[GTM-Hub]]"
date: 2026-05-28
---

# API Performance Baseline

**Agents:** API Tester + Performance Benchmarker

## SLA targets

| Endpoint | Target p95 | Baseline 2026-05-28 |
|----------|------------|---------------------|
| `GET /` health | <500ms | **538ms** ✅ |
| `POST /products/search` | <2000ms | **4305ms** ❌ |
| `POST /products/compare` | <3000ms | TBD |

## Run benchmark

```bash
python3 ops/benchmark_api.py --runs 10
python3 ops/benchmark_api.py --base http://localhost:8000 --runs 20  # local
```

## Regression tests

```bash
# Live API (Fly.io)
python3 -m pytest tests/test_api_perf.py -v -m integration

# CI — skip live latency
MARKET_SKIP_LIVE=1 python3 -m pytest tests/test_api_perf.py -v -m integration
```

## Findings

1. **Search p95 ~4.3s** on production — fan-out to 30 retailers; optimize slow stores or parallel cap
2. **Contract stable** — search returns `name`, `price`, `store` fields
3. **Dashboard public** — `/dashboard/data` returns KPIs for data gate

## Next optimizations

- Timeout per store (fail fast)
- Cache hot queries (Redis)
- Reduce active store fan-out for Free tier

[[GTM-Hub]] · [[dx-audit]] · [[alpha-gates-2026-06-01]]
