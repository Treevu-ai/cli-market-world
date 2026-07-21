"""Known-brands registry — backs the "new brand" signal on GET /v1/analytics/brands.

A brand seen for the first time in a given country is a real discovery
signal (a scrape found a new market entrant, enriching the moat) — but
telling "new" from "already catalogued" requires remembering what's been
seen before. Casing isn't a reliable identity key on its own (the same
scraper run can emit "Gloria" on one SKU and "GLORIA" on another), so
first-seen tracking is keyed on the same normalized form used to
canonicalize display names in analytics_brands.
"""

from __future__ import annotations

from market_core import USE_PG, get_db

_DDL_PG = """
CREATE TABLE IF NOT EXISTS known_brands (
    brand_normalized TEXT NOT NULL,
    country TEXT NOT NULL,
    display_brand TEXT NOT NULL,
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (brand_normalized, country)
)
"""

_DDL_SQLITE = """
CREATE TABLE IF NOT EXISTS known_brands (
    brand_normalized TEXT NOT NULL,
    country TEXT NOT NULL,
    display_brand TEXT NOT NULL,
    first_seen_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (brand_normalized, country)
)
"""


def ensure_known_brands_schema() -> None:
    db = get_db()
    db.execute(_DDL_PG if USE_PG else _DDL_SQLITE)
    db.commit()
    db.close()


def normalize_brand(raw: str) -> str:
    return raw.strip().lower()


def diff_and_record_new_brands(db, country: str, brands: list[str]) -> set[str]:
    """Given the brands returned for *country* right now, return the subset
    (normalized form) never seen before for that country, then record ALL of
    them as known — so the same brand isn't reported as "new" on every call.

    Caller owns the db connection/commit lifecycle (mirrors the rest of this
    router — no db.commit()/close() here).
    """
    normalized = {normalize_brand(b): b for b in brands if b.strip()}
    if not normalized:
        return set()

    placeholders = ",".join("?" * len(normalized))
    rows = db.execute(
        f"SELECT brand_normalized FROM known_brands WHERE country = ? AND brand_normalized IN ({placeholders})",
        [country, *normalized.keys()],
    ).fetchall()
    already_known = {r["brand_normalized"] for r in rows}
    new_ones = set(normalized.keys()) - already_known

    # ON CONFLICT DO NOTHING / OR IGNORE (not try/except around a plain
    # INSERT): a concurrent request inserting the same brand_normalized+
    # country first would raise a PK-violation error that, on Postgres,
    # poisons the rest of this transaction until rolled back — silently
    # breaking every other insert (and the final commit) in this same loop.
    insert_sql = (
        "INSERT INTO known_brands (brand_normalized, country, display_brand) "
        "VALUES (?, ?, ?) ON CONFLICT (brand_normalized, country) DO NOTHING"
        if USE_PG else
        "INSERT OR IGNORE INTO known_brands (brand_normalized, country, display_brand) VALUES (?, ?, ?)"
    )
    for norm, display in normalized.items():
        if norm in already_known:
            continue
        db.execute(insert_sql, (norm, country, display))
    db.commit()
    return new_ones
