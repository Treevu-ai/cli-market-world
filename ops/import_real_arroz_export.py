"""Import the one real datamoat snapshot recoverable from market-reports/.

Of 29 `market export` capture files in that directory, only 4 (2026-07-13,
07-14, 07-15, 07-18) hold real product data -- the rest are 401/connection-
error responses from later runs when the saved API key had gone stale. All
four are the same `market search arroz --json` query, re-run on different
days; deduplicated by (store, id) they total 200 unique real PE products
across 5 stores (wong, metro, plazavea, nunaorganica_pe, promart), captured
mid-July. Each file also has a stray "nueva versión disponible" banner line
the CLI printed before the JSON (a redirection bug in that old CLI version,
not something to fix here) -- stripped by seeking to the first '{'.

This is real production data, just old, narrow (PE + "arroz" only) and
small -- nowhere near the full moat, but a better local starting point than
synthetic rows. queried_at is set to now() rather than preserved from July,
matching ops/seed_local_price_snapshots.sql's convention: this is local dev
data for exercising freshness-dependent code paths (moat_health, basket
compare), not a historical record.

Usage: DATABASE_URL=<local postgres> python ops/import_real_arroz_export.py
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

import psycopg2
import psycopg2.extras

SOURCE_FILES = [
    "market-reports/export_20260713_232731.json",
    "market-reports/export_20260714_202803.json",
    "market-reports/export_20260715_195014.json",
    "market-reports/export_20260718_214213.json",
]


def load_tolerant(path: str) -> dict:
    raw = open(path, encoding="utf-8").read()
    brace = raw.find("{")
    if brace == -1:
        raise ValueError(f"{path}: no JSON object found")
    return json.loads(raw[brace:], strict=False)


def collect_unique_rows() -> list[dict]:
    seen: dict[tuple[str, str], dict] = {}
    for path in SOURCE_FILES:
        doc = load_tolerant(path)
        if not doc.get("ok"):
            continue
        for row in (doc.get("data") or {}).get("results") or []:
            key = (row.get("store"), row.get("id") or row.get("name"))
            seen[key] = row
    return list(seen.values())


def main() -> int:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not set -- refusing to guess which Postgres to write to.")
        return 1

    rows = collect_unique_rows()
    print(f"Collected {len(rows)} unique real products from {len(SOURCE_FILES)} export files.")

    now = datetime.now(timezone.utc)
    conn = psycopg2.connect(database_url)
    try:
        with conn.cursor() as cur:
            psycopg2.extras.execute_values(
                cur,
                """
                INSERT INTO price_snapshots
                    (product_id, name, brand, price, list_price, discount, store,
                     store_name, currency, line, line_name, category, stock, url,
                     queried_at, confidence)
                VALUES %s
                ON CONFLICT (product_id, store) DO UPDATE SET
                    price = EXCLUDED.price,
                    list_price = EXCLUDED.list_price,
                    queried_at = EXCLUDED.queried_at
                """,
                [
                    (
                        r.get("id") or r.get("name"), r.get("name"), r.get("brand"),
                        r.get("price"), r.get("list_price"), r.get("discount"),
                        r.get("store"), r.get("store_name"), r.get("currency"),
                        r.get("line"), r.get("line_name"), r.get("category"),
                        r.get("stock"), r.get("url"), now, r.get("confidence") or "ok",
                    )
                    for r in rows
                ],
                template="(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
            )
        conn.commit()
        print(f"Upserted {len(rows)} rows into price_snapshots.")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
