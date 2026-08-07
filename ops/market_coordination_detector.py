#!/usr/bin/env python3
"""Market Coordination Detector — MVP screening tool.

Gap identified in docs/INDECOPI_ARCHITECTURE_ANALYSIS.md (§3.2, Agente
"Vigilant"): CLI Market had no tool to flag price behavior across
independent retailers that *looks* coordinated rather than competitive.
This is a first working version, built against the real price_snapshots /
price_history schema (see docs/methodology.md and
docs/🏗️_moat_engine/data-integrity-prd.md for the conventions this follows).

WHAT THIS IS: a statistical screening tool over two independent signals.
WHAT THIS IS NOT: proof of collusion. Every flag needs human/economic
review — price-matching bots, a shared supplier-set MSRP, and genuine
coincidence all produce the same statistical signature as coordination.
Never present a flag from this tool as a finding on its own.

Signal A — Price uniformity
    For a canonical product sold by >=2 distinct stores, an unusually LOW
    coefficient of variation (CV) is the suspicious case here — the
    opposite of how CV is normally read in market_indicators.py, where
    CV is a *dispersion* metric and low CV is unremarkable. Near-zero
    price differences between independent competitors, sustained over
    time, is the pattern worth a human look.

Signal B — Synchronized promotions
    For the same canonical product, >=2 distinct stores starting a
    discount within a short window of each other. A single coincidence
    is noise (retailers legitimately react to the same supplier signals,
    holidays, etc.) — the signal is a store-pair doing this repeatedly
    across multiple products.

A canonical product is flagged "high" only when both signals fire for it;
"watch" when only one does. Nothing here recommends action beyond "review".

Usage:
    python3 ops/market_coordination_detector.py --country PE --line supermercados
    python3 ops/market_coordination_detector.py --demo   # synthetic data, no DB needed

Env vars: same as the rest of cli-market-world (DATABASE_URL or local sqlite
fallback via market_core.get_db()).
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import statistics
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

# CV threshold below which cross-store pricing on the same product is
# considered "uniform" rather than merely "not very dispersed". Chosen well
# under the dispersion CVs typically seen in market_indicators.py output
# (single digits to low tens of percent) — this is deliberately strict so
# the tool stays a screen, not an accusation generator.
DEFAULT_CV_THRESHOLD_PCT = 2.0
DEFAULT_SYNC_WINDOW_HOURS = 48
DEFAULT_LOOKBACK_DAYS = 30
DEFAULT_MIN_STORES = 2
# A store-pair needs to co-occur this many times before "synchronized
# promotions" moves from "could be coincidence" to "worth flagging".
DEFAULT_MIN_PAIR_OCCURRENCES = 2


@dataclass
class UniformityFlag:
    # canonical_product_id when Golden Record linkage exists, else a
    # normalized-name fallback key — see _identity_key_map.
    product_key: str
    product_name: str
    cv_pct: float
    n_stores: int
    stores: list[str]


@dataclass
class SyncEvent:
    product_key: str
    product_name: str
    store_a: str
    store_b: str
    delta_hours: float
    recorded_at_a: str
    recorded_at_b: str


@dataclass
class CoordinationReport:
    country: str
    line: str | None
    generated_at: str
    uniformity_flags: list[UniformityFlag] = field(default_factory=list)
    sync_events: list[SyncEvent] = field(default_factory=list)
    pair_occurrence_counts: dict[str, int] = field(default_factory=dict)
    high_risk_products: list[str] = field(default_factory=list)
    watch_products: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "country": self.country,
            "line": self.line,
            "generated_at": self.generated_at,
            "methodology_note": (
                "Screening tool, not proof. Every flag requires human/economic "
                "review before any regulatory action."
            ),
            "uniformity_flags": [vars(f) for f in self.uniformity_flags],
            "sync_events": [vars(e) for e in self.sync_events],
            "pair_occurrence_counts": self.pair_occurrence_counts,
            "high_risk_products": self.high_risk_products,
            "watch_products": self.watch_products,
        }


def _display_names_for_keys(db, keys: set[str]) -> dict[str, str]:
    """Resolve identity keys from _identity_key_map back to a display name.

    "name:*" keys already *are* the (truncated, lowercased) name — nothing to
    look up. "canon:*" keys need a price_snapshots lookup for the original
    canonical_product_id's product name.
    """
    names: dict[str, str] = {}
    canon_ids = {k.removeprefix("canon:") for k in keys if k.startswith("canon:")}
    for k in keys:
        if k.startswith("name:"):
            names[k] = k.removeprefix("name:")

    if canon_ids:
        placeholders = ",".join("?" * len(canon_ids))
        rows = db.execute(
            f"""SELECT canonical_product_id, name FROM price_snapshots
                WHERE canonical_product_id IN ({placeholders}) AND name IS NOT NULL""",
            list(canon_ids),
        ).fetchall()
        by_cid: dict[str, str] = {}
        for row in rows:
            cid = row["canonical_product_id"]
            if cid and cid not in by_cid:
                by_cid[cid] = row["name"]
        for k in keys:
            if k.startswith("canon:"):
                names[k] = by_cid.get(k.removeprefix("canon:"), k)

    return names


def _stores_for_country(country: str) -> list[str]:
    from market_core.store_credentials import get_all_stores

    return [
        k for k, v in get_all_stores().items()
        if v.get("country") == country.upper() and not v.get("disabled")
    ]


def _fetch_snapshot_rows(db, stores: list[str], line: str | None) -> list:
    """Single price_snapshots scan for a country+line — the shared input for
    both signal functions, so a detect_coordination() run touches this table
    once instead of three times (find_uniformity_flags used to run its own
    near-duplicate query, and both signals independently re-derived the
    identity key map from a fresh scan)."""
    if not stores:
        return []
    placeholders = ",".join("?" * len(stores))
    line_clause = " AND line = ?" if line else ""
    params: list = [*stores]
    if line:
        params.append(line)
    return db.execute(
        f"""SELECT product_id, store, price, canonical_product_id, name
            FROM price_snapshots
            WHERE store IN ({placeholders}) AND price > 0 {line_clause}""",
        params,
    ).fetchall()


def _identity_key_map(rows: list) -> dict[tuple[str, str], str]:
    """Best-available cross-store product identity per (product_id, store),
    derived from rows already fetched by _fetch_snapshot_rows.

    Prefers `canonical_product_id` (Golden Record UPID) when the collector has
    linked it. Falls back to a normalized product name — same fallback
    market_core.market_indicators_compute.compute_price_dispersion already
    uses when canonical linkage is sparse — because Golden Record coverage is
    still thin for most countries today (confirmed: 2 of 152 PE snapshot rows
    in local dev data have a non-empty canonical_product_id). Restricting to
    one country (and ideally one line, e.g. "supermercados") keeps the name
    fallback usable: cross-store name collisions are far less likely within
    one retail vertical in one country than across the whole catalog.
    """
    key_map: dict[tuple[str, str], str] = {}
    for row in rows:
        cid = (row["canonical_product_id"] or "").strip()
        if cid:
            key = f"canon:{cid}"
        else:
            name = (row["name"] or "").strip().lower()[:40]
            if not name:
                continue
            key = f"name:{name}"
        key_map[(row["product_id"], row["store"])] = key
    return key_map


def find_uniformity_flags(
    rows: list,
    key_map: dict[tuple[str, str], str],
    cv_threshold_pct: float = DEFAULT_CV_THRESHOLD_PCT,
    min_stores: int = DEFAULT_MIN_STORES,
) -> list[UniformityFlag]:
    """Signal A: products priced near-identically across independent stores."""
    buckets: dict[str, list[tuple[float, str]]] = {}
    display_names: dict[str, str] = {}
    for row in rows:
        key = key_map.get((row["product_id"], row["store"]))
        if not key:
            continue
        buckets.setdefault(key, []).append((float(row["price"]), row["store"]))
        display_names.setdefault(key, row["name"] or key)

    flags: list[UniformityFlag] = []
    for key, entries in buckets.items():
        distinct_stores = {store for _, store in entries}
        if len(distinct_stores) < min_stores:
            continue
        prices = [p for p, _ in entries]
        mean = sum(prices) / len(prices)
        if mean <= 0:
            continue
        stdev = statistics.pstdev(prices)
        cv_pct = round(stdev / mean * 100, 3)
        if cv_pct <= cv_threshold_pct:
            flags.append(UniformityFlag(
                product_key=key,
                product_name=display_names.get(key, key),
                cv_pct=cv_pct,
                n_stores=len(distinct_stores),
                stores=sorted(distinct_stores),
            ))

    return sorted(flags, key=lambda f: f.cv_pct)


def _discount_start_events(rows: list) -> list[dict]:
    """Walk one store's price_history in order, return timestamps where a
    discount newly appeared (previous row had no/zero discount, this row does)."""
    events: list[dict] = []
    prev_discount = None
    for row in rows:
        discount = row["discount"] or 0
        if discount and (prev_discount is None or not prev_discount):
            events.append({"recorded_at": row["recorded_at"], "discount": discount})
        prev_discount = discount
    return events


def find_synchronized_promotions(
    db,
    stores_in_country: list[str],
    key_map: dict[tuple[str, str], str],
    sync_window_hours: float = DEFAULT_SYNC_WINDOW_HOURS,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
) -> tuple[list[SyncEvent], dict[str, int]]:
    """Signal B: >=2 distinct stores starting a discount on the same product
    (canonical ID, or normalized name when canonical linkage is missing —
    see _identity_key_map) within `sync_window_hours` of each other."""
    if not stores_in_country or not key_map:
        return [], {}

    since = (datetime.now(timezone.utc) - timedelta(days=lookback_days)).isoformat()
    placeholders = ",".join("?" * len(stores_in_country))
    params: list = [*stores_in_country, since]

    rows = db.execute(
        f"""SELECT ph.product_id AS product_id, ph.store AS store,
                   ph.discount AS discount, ph.recorded_at AS recorded_at
            FROM price_history ph
            WHERE ph.store IN ({placeholders})
              AND ph.recorded_at >= ?
            ORDER BY ph.product_id, ph.store, ph.recorded_at""",
        params,
    ).fetchall()

    by_product_store: dict[tuple[str, str], list] = {}
    for row in rows:
        key = key_map.get((row["product_id"], row["store"]))
        if not key:
            continue
        by_product_store.setdefault((key, row["store"]), []).append(row)

    events_by_product: dict[str, dict[str, list[dict]]] = {}
    for (cid, store), store_rows in by_product_store.items():
        starts = _discount_start_events(store_rows)
        if starts:
            events_by_product.setdefault(cid, {})[store] = starts

    sync_events: list[SyncEvent] = []
    pair_counts: dict[str, int] = {}
    all_cids: set[str] = set()

    for cid, per_store in events_by_product.items():
        stores = sorted(per_store.keys())
        if len(stores) < 2:
            continue
        for i in range(len(stores)):
            for j in range(i + 1, len(stores)):
                store_a, store_b = stores[i], stores[j]
                for ev_a in per_store[store_a]:
                    for ev_b in per_store[store_b]:
                        ta = _parse_ts(ev_a["recorded_at"])
                        tb = _parse_ts(ev_b["recorded_at"])
                        if ta is None or tb is None:
                            continue
                        delta_hours = abs((ta - tb).total_seconds()) / 3600
                        if delta_hours <= sync_window_hours:
                            sync_events.append(SyncEvent(
                                product_key=cid,
                                product_name="",
                                store_a=store_a,
                                store_b=store_b,
                                delta_hours=round(delta_hours, 1),
                                recorded_at_a=str(ev_a["recorded_at"]),
                                recorded_at_b=str(ev_b["recorded_at"]),
                            ))
                            pair_key = f"{store_a}|{store_b}"
                            pair_counts[pair_key] = pair_counts.get(pair_key, 0) + 1
                            all_cids.add(cid)

    names = _display_names_for_keys(db, all_cids)
    for e in sync_events:
        e.product_name = names.get(e.product_key, e.product_key)

    return sync_events, pair_counts


def _parse_ts(value) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    try:
        s = str(value).replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def detect_coordination(
    db,
    country: str,
    line: str | None = None,
    cv_threshold_pct: float = DEFAULT_CV_THRESHOLD_PCT,
    sync_window_hours: float = DEFAULT_SYNC_WINDOW_HOURS,
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
    min_pair_occurrences: int = DEFAULT_MIN_PAIR_OCCURRENCES,
) -> CoordinationReport:
    stores = _stores_for_country(country)
    rows = _fetch_snapshot_rows(db, stores, line)
    key_map = _identity_key_map(rows)

    uniformity_flags = find_uniformity_flags(rows, key_map, cv_threshold_pct)
    sync_events, pair_counts = find_synchronized_promotions(
        db, stores, key_map, sync_window_hours, lookback_days
    )

    recurring_pairs = {
        pair for pair, count in pair_counts.items() if count >= min_pair_occurrences
    }
    sync_events_recurring = [
        e for e in sync_events if f"{e.store_a}|{e.store_b}" in recurring_pairs
    ]

    uniform_cids = {f.product_key for f in uniformity_flags}
    synced_cids = {e.product_key for e in sync_events_recurring}

    report = CoordinationReport(
        country=country,
        line=line,
        generated_at=datetime.now(timezone.utc).isoformat(),
        uniformity_flags=uniformity_flags,
        sync_events=sync_events_recurring,
        pair_occurrence_counts={k: v for k, v in pair_counts.items() if v >= min_pair_occurrences},
        high_risk_products=sorted(uniform_cids & synced_cids),
        watch_products=sorted(uniform_cids ^ synced_cids),
    )
    return report


def _seed_demo_db() -> sqlite3.Connection:
    """In-memory sqlite DB with one clean pair and one coordinated-looking pair,
    so the detector is demonstrable without a live database connection."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript(
        """
        CREATE TABLE price_snapshots (
            product_id TEXT, name TEXT, price REAL, list_price REAL,
            discount INTEGER, store TEXT, currency TEXT, line TEXT,
            canonical_product_id TEXT
        );
        CREATE TABLE price_history (
            product_id TEXT, store TEXT, price REAL, list_price REAL,
            discount INTEGER, recorded_at TEXT
        );
        """
    )
    now = datetime.now(timezone.utc)

    # Coordinated-looking pair: two stores, near-identical price, discounts
    # start within 3h of each other across 3 separate products.
    for idx in range(1, 4):
        cid = f"CANON-LECHE-{idx}"
        conn.execute(
            "INSERT INTO price_snapshots VALUES (?,?,?,?,?,?,?,?,?)",
            (f"sup_a_{idx}", f"Leche Entera 1L #{idx}", 5.20, 5.20, 0, "sup_a", "PEN", "supermercados", cid),
        )
        conn.execute(
            "INSERT INTO price_snapshots VALUES (?,?,?,?,?,?,?,?,?)",
            (f"sup_b_{idx}", f"Leche Entera 1L #{idx}", 5.21, 5.21, 0, "sup_b", "PEN", "supermercados", cid),
        )
        base = now - timedelta(days=10 - idx)
        for store, jitter_hours in (("sup_a", 0), ("sup_b", 2)):
            t0 = base + timedelta(hours=jitter_hours)
            conn.execute(
                "INSERT INTO price_history VALUES (?,?,?,?,?,?)",
                (f"{store}_{idx}", store, 6.00, 6.00, 0, (t0 - timedelta(days=1)).isoformat()),
            )
            conn.execute(
                "INSERT INTO price_history VALUES (?,?,?,?,?,?)",
                (f"{store}_{idx}", store, 5.20, 6.00, 13, t0.isoformat()),
            )

    # Clean pair: same product family, independent pricing and promo timing.
    cid_clean = "CANON-ARROZ-1"
    conn.execute(
        "INSERT INTO price_snapshots VALUES (?,?,?,?,?,?,?,?,?)",
        ("sup_a_rice", "Arroz Extra 5kg", 18.90, 18.90, 0, "sup_a", "PEN", "supermercados", cid_clean),
    )
    conn.execute(
        "INSERT INTO price_snapshots VALUES (?,?,?,?,?,?,?,?,?)",
        ("sup_b_rice", "Arroz Extra 5kg", 21.50, 21.50, 0, "sup_b", "PEN", "supermercados", cid_clean),
    )
    conn.execute(
        "INSERT INTO price_history VALUES (?,?,?,?,?,?)",
        ("sup_a_rice", "sup_a", 21.00, 21.00, 0, (now - timedelta(days=1)).isoformat()),
    )
    conn.execute(
        "INSERT INTO price_history VALUES (?,?,?,?,?,?)",
        ("sup_a_rice", "sup_a", 18.90, 21.00, 10, now.isoformat()),
    )
    conn.execute(
        "INSERT INTO price_history VALUES (?,?,?,?,?,?)",
        ("sup_b_rice", "sup_b", 21.50, 21.50, 0, (now - timedelta(days=15)).isoformat()),
    )
    conn.commit()
    return conn


class _DemoStoreCredentials:
    """Monkeypatch target so the demo run doesn't need real store config."""

    @staticmethod
    def get_all_stores():
        return {
            "sup_a": {"country": "PE", "disabled": False},
            "sup_b": {"country": "PE", "disabled": False},
        }


def _run_demo() -> CoordinationReport:
    import market_core.store_credentials as sc

    db = _seed_demo_db()
    orig_get_all_stores = sc.get_all_stores
    sc.get_all_stores = _DemoStoreCredentials.get_all_stores
    try:
        return detect_coordination(db, country="PE", line="supermercados")
    finally:
        sc.get_all_stores = orig_get_all_stores
        db.close()


def _print_report(report: CoordinationReport) -> None:
    print(f"\n=== Coordination screen — {report.country} / {report.line or 'todas las líneas'} ===")
    print(f"Generado: {report.generated_at}")
    print(f"\nSeñal A — Uniformidad de precio (CV <= umbral): {len(report.uniformity_flags)} producto(s)")
    for f in report.uniformity_flags:
        print(f"  [{f.product_key}] {f.product_name} — CV={f.cv_pct}% ({f.n_stores} tiendas: {', '.join(f.stores)})")

    print(f"\nSeñal B — Descuentos sincronizados recurrentes: {len(report.sync_events)} evento(s)")
    for e in report.sync_events:
        print(f"  [{e.product_key}] {e.product_name} — {e.store_a} vs {e.store_b}, Δ={e.delta_hours}h")

    print(f"\nPares de tienda con co-ocurrencia recurrente: {report.pair_occurrence_counts}")
    print(f"\n>>> ALTO RIESGO (ambas señales): {report.high_risk_products or 'ninguno'}")
    print(f">>> VIGILAR (una señal): {report.watch_products or 'ninguno'}")
    print(
        "\nNota metodológica: herramienta de screening estadístico, no prueba de "
        "colusión. Cada hallazgo requiere revisión humana/económica antes de "
        "cualquier acción regulatoria — bots de price-matching, un MSRP común "
        "de proveedor, y la coincidencia genuina producen la misma firma "
        "estadística que la coordinación."
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Market coordination detector (MVP)")
    parser.add_argument("--country", default="PE")
    parser.add_argument("--line", default=None)
    parser.add_argument("--cv-threshold", type=float, default=DEFAULT_CV_THRESHOLD_PCT)
    parser.add_argument("--sync-window-hours", type=float, default=DEFAULT_SYNC_WINDOW_HOURS)
    parser.add_argument("--lookback-days", type=int, default=DEFAULT_LOOKBACK_DAYS)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--demo", action="store_true", help="Run against synthetic seeded data, no DB needed")
    args = parser.parse_args()

    if args.demo:
        report = _run_demo()
    else:
        from market_core import get_db
        db = get_db()
        try:
            report = detect_coordination(
                db,
                country=args.country,
                line=args.line,
                cv_threshold_pct=args.cv_threshold,
                sync_window_hours=args.sync_window_hours,
                lookback_days=args.lookback_days,
            )
        finally:
            db.close()

    if args.json:
        print(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))
    else:
        _print_report(report)


if __name__ == "__main__":
    main()
