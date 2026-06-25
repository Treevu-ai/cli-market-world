#!/usr/bin/env python3
"""Backfill vault_bindings from audit_log (MercadoPago save_card + PayPal vault_confirm).

Run once after deploying vault IDOR fixes (#389 PayPal, #390 MercadoPago), or rely on
automatic backfill at API startup (market_server lifespan).

  python3 ops/backfill_vault_bindings.py
  python3 ops/backfill_vault_bindings.py --dry-run
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main() -> int:
    import market_core
    from market_core import ensure_db_initialized
    from market_vault import backfill_vault_bindings_from_audit, ensure_vault_schema

    parser = argparse.ArgumentParser(description="Backfill vault_bindings from audit_log")
    parser.add_argument("--dry-run", action="store_true", help="Report counts only")
    parser.add_argument(
        "--allow-sqlite",
        action="store_true",
        help="Allow running against local SQLite even when DATABASE_URL is set",
    )
    args = parser.parse_args()

    db_url = os.getenv("DATABASE_URL", "").strip()
    ensure_db_initialized()
    if db_url and not market_core.USE_PG and not args.allow_sqlite:
        print(
            "DATABASE_URL is set but PostgreSQL is unavailable.\n"
            "  pip install psycopg2-binary\n"
            "  export DATABASE_URL='postgresql://...'\n"
            "Or pass --allow-sqlite to backfill local market.db only.",
            file=sys.stderr,
        )
        return 1

    backend = "PostgreSQL" if market_core.USE_PG else f"SQLite ({market_core.DB_FILE})"
    print(f"Vault bindings backfill target: {backend}")

    if args.dry_run:
        from market_audit import ensure_audit_schema, get_audit_log

        ensure_audit_schema()
        save_card = len(get_audit_log(action="save_card", limit=10_000))
        vault_confirm = len(get_audit_log(action="vault_confirm", limit=10_000))
        ensure_vault_schema()
        print(f"  audit save_card rows: {save_card}")
        print(f"  audit vault_confirm rows: {vault_confirm}")
        print("  (dry-run — no writes)")
        return 0

    stats = backfill_vault_bindings_from_audit()
    print(
        "Done:",
        f"customers_bound={stats['customers_bound']}",
        f"tokens_bound={stats['tokens_bound']}",
        f"customers_skipped={stats['customers_skipped']}",
        f"tokens_skipped={stats['tokens_skipped']}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
