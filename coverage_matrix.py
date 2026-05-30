"""Coverage matrix country × line for GET /v1/coverage/matrix."""

from __future__ import annotations

from market_core import STORES


def build_coverage_matrix(db, *, line: str | None = None) -> dict:
    """Build line × country store counts from price_snapshots."""
    q = """
        SELECT ps.line, ps.store, COUNT(*) as n
        FROM price_snapshots ps
        WHERE ps.price > 0
    """
    params: list = []
    if line:
        q += " AND ps.line = ?"
        params.append(line)
    q += " GROUP BY ps.line, ps.store"

    rows = db.execute(q, params).fetchall()
    line_country_map: dict[str, set[str]] = {}
    for r in rows:
        country = STORES.get(r["store"], {}).get("country", "??")
        key = f"{r['line']}|{country}"
        line_country_map.setdefault(key, set()).add(r["store"])

    cells = [
        {
            "line": key.split("|")[0],
            "country": key.split("|")[1],
            "stores": len(stores),
        }
        for key, stores in line_country_map.items()
    ]
    cells.sort(key=lambda c: (c["line"], c["country"]))

    lines = sorted({c["line"] for c in cells})
    countries = sorted({c["country"] for c in cells})
    lookup = {f"{c['line']}|{c['country']}": c["stores"] for c in cells}

    gaps: list[str] = []
    for ln in lines:
        for country in countries:
            if lookup.get(f"{ln}|{country}", 0) == 0:
                gaps.append(f"{ln}×{country}")

    return {
        "lines": lines,
        "countries": countries,
        "cells": cells,
        "gaps": gaps,
    }


def build_line_country_matrix(db) -> list[dict]:
    """Legacy shape used by /dashboard/data."""
    matrix = build_coverage_matrix(db)
    return matrix["cells"]
