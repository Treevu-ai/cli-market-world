#!/usr/bin/env python3
"""Detect raw credentials accidentally persisted in MCP funnel telemetry.

This intentionally reports only aggregate categories and counts. It never
prints usernames, API keys, session tokens, or metadata values.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Mapping

from market_core import get_db


_RAW_CREDENTIAL_SQL = """
SELECT category, COUNT(*) AS rows
FROM (
    SELECT CASE
        WHEN username LIKE 'sk-%' THEN 'api_key'
        WHEN username LIKE 'demo-%' THEN 'legacy_demo_token'
        WHEN username NOT LIKE 'redacted-mcp-%'
          AND username NOT LIKE 'demo:%'
          AND username NOT IN (SELECT username FROM app_users)
        THEN 'unknown_nonuser_value'
    END AS category
    FROM funnel_events
    WHERE event IN ('mcp_connect', 'mcp_tool_call')
      AND username IS NOT NULL
      AND username != ''
) suspect
WHERE category IS NOT NULL
GROUP BY category
ORDER BY category
"""


def credential_counts() -> dict[str, int]:
    """Return aggregate counts of disallowed MCP telemetry values."""
    db = get_db()
    try:
        rows = db.execute(_RAW_CREDENTIAL_SQL).fetchall()
    finally:
        db.close()
    return {str(row["category"]): int(row["rows"]) for row in rows}


def has_raw_credentials(counts: Mapping[str, int]) -> bool:
    return any(value > 0 for value in counts.values())


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--fail-on-detection",
        action="store_true",
        help="Exit nonzero when any raw credential-like value is detected.",
    )
    parser.add_argument("--json", action="store_true", help="Emit aggregate JSON only.")
    args = parser.parse_args()

    counts = credential_counts()
    payload = {
        "ok": not has_raw_credentials(counts),
        "credential_like_rows": sum(counts.values()),
        "categories": counts,
    }
    if args.json:
        print(json.dumps(payload, sort_keys=True))
    elif payload["ok"]:
        print("OK: MCP credential guard found no raw credential-like telemetry values.")
    else:
        print(
            "ALERT: MCP credential guard detected raw credential-like telemetry values "
            f"(rows={payload['credential_like_rows']}, categories={counts}).",
            file=sys.stderr,
        )
    return 1 if args.fail_on_detection and not payload["ok"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
