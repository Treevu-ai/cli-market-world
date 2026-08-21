"""
Index Gate — Semantic enrichment bridge for CLI Market.

Delegates to cli-market-index IndexService with persistent Golden Records.
Postgres is used automatically when DATABASE_URL is set.

Usage (in any router):
    from index_gate import enrich_product, enrich_list
"""

from __future__ import annotations

import contextlib
import logging
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from connectors.gov.adapters.bcrp import BCRPConnector
from persistence.factory import create_store
from services.index_service import IndexService

from price_snapshots_schema import ensure_canonical_product_id_column, ensure_match_metadata_columns

logger = logging.getLogger("market.index_gate")

_service: Optional[IndexService] = None

_HEALTH_CACHE_KEY = "index_gate:health"


def _bootstrap_index_env() -> None:
    """Wire index persistence to backend database paths when not explicitly set."""
    if not os.getenv("INDEX_DATABASE_URL", "").strip():
        db_url = os.getenv("DATABASE_URL", "").strip()
        if db_url.startswith(("postgres://", "postgresql://")):
            os.environ.setdefault("INDEX_DATABASE_URL", db_url)

    if not os.getenv("INDEX_DATA_DIR") and os.getenv("MARKET_DATA_DIR"):
        os.environ.setdefault(
            "INDEX_DATA_DIR",
            str(Path(os.environ["MARKET_DATA_DIR"]).expanduser() / "index"),
        )


def _get_service() -> IndexService:
    global _service
    if _service is None:
        _bootstrap_index_env()
        if os.getenv("INDEX_PERSISTENCE", "1").strip().lower() in ("0", "false", "no"):
            _service = IndexService()
        else:
            _service = IndexService(store=create_store())
        logger.info(
            "Index gate ready (persistence=%s, registry_size=%d)",
            "on" if _service._store else "off",
            _service.size,
        )
    return _service


def registry_size() -> int:
    """Current Golden Record count in the index store."""
    try:
        return _get_service().size
    except Exception:
        return 0


def _brand_slug(product: Any) -> str:
    brand = product.brand
    if isinstance(brand, str):
        return brand
    return getattr(brand, "slug", str(brand))


def _product_payload(product: Any, *, match_type: str, confidence: float) -> Dict[str, Any]:
    measurement = None
    if product.measurement:
        measurement = {
            "value": product.measurement.value,
            "unit": product.measurement.unit,
            "display": product.measurement.display,
        }
    return {
        "object": "product",
        "id": product.id,
        "name": product.name,
        "brand": _brand_slug(product),
        "measurement": measurement,
        "match_type": match_type,
        "confidence": confidence,
    }


def index_resolve(snapshot: Dict[str, Any]) -> Dict[str, Any]:
    """Resolve a retailer snapshot to a Golden Record. Never raises."""
    try:
        svc = _get_service()
        result = svc.resolve_snapshot(
            {
                "store": snapshot.get("store", ""),
                "sku": snapshot.get("sku") or snapshot.get("product_id", ""),
                "name": snapshot.get("name", ""),
                "brand": snapshot.get("brand", ""),
                "price": float(snapshot.get("price", 0) or 0),
                "currency": snapshot.get("currency", "USD"),
                "url": snapshot.get("url", ""),
            }
        )
        if not result.product:
            return {"resolved": False, "product": None, "match_type": result.match_type}
        return {
            "resolved": True,
            "product": _product_payload(
                result.product,
                match_type=result.match_type,
                confidence=result.confidence,
            ),
            "registry_size": svc.size,
        }
    except Exception as exc:
        logger.warning("index_resolve failed: %s", exc)
        return {"resolved": False, "error": str(exc)}


def index_lookup(product_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a Golden Record by prod_* id."""
    try:
        product = _get_service().get_product(product_id)
        if not product:
            return None
        return _product_payload(product, match_type="lookup", confidence=1.0)
    except Exception as exc:
        logger.warning("index_lookup failed for %s: %s", product_id, exc)
        return None


def _record_index_health(status: str, error: str | None = None) -> None:
    """Persist certify_round's outcome so a total index-gate failure is
    visible via GET /index/stats instead of looking identical to "nothing
    new to resolve" — collect_prices.py's _run_index_cycle only branches on
    stats["resolved"], never on the "failed" flag certify_round already
    returns, so a dead IndexService today produces the exact same log line
    as a healthy cycle with no price changes. Reuses the existing
    enrichment_cache table (market_core.market_enrich_sources.cache_set) —
    no new infra."""
    try:
        import market_core
        from market_core.market_enrich_sources import cache_get, cache_set

        db = market_core.get_db()
        try:
            prior = cache_get(db, _HEALTH_CACHE_KEY, max_age_hours=24 * 365) or {}
            consecutive_failures = int(prior.get("consecutive_failures", 0))
            consecutive_failures = consecutive_failures + 1 if status == "failed" else 0
            now_iso = datetime.now(timezone.utc).isoformat()
            payload = {
                "status": status,
                "consecutive_failures": consecutive_failures,
                "last_ok_at": now_iso if status == "ok" else prior.get("last_ok_at"),
                "last_failure_at": now_iso if status == "failed" else prior.get("last_failure_at"),
                "last_error": (error or "")[:500] if status == "failed" else prior.get("last_error"),
            }
            cache_set(db, _HEALTH_CACHE_KEY, "index_gate", payload)
            db.commit()
        finally:
            db.close()
    except Exception as exc:
        # WARNING, not debug: this function exists specifically to make a
        # silent index-gate failure visible. If recording the health snapshot
        # itself fails silently, GET /index/stats can keep reporting a stale
        # "failed" (or stale "ok") status indefinitely with zero trace of why —
        # the exact failure mode this mechanism was built to eliminate.
        logger.warning("index_gate health record failed: %s", exc)


def _read_index_health() -> Dict[str, Any]:
    try:
        import market_core
        from market_core.market_enrich_sources import cache_get

        db = market_core.get_db()
        try:
            return cache_get(db, _HEALTH_CACHE_KEY, max_age_hours=24 * 365) or {}
        finally:
            db.close()
    except Exception as exc:
        logger.warning("index_gate health read failed: %s", exc)
        return {}


def index_stats() -> Dict[str, Any]:
    """Registry size plus price_snapshots linkage metrics."""
    import market_core

    stats: Dict[str, Any] = {
        "registry_size": registry_size(),
        "snapshots_linked": 0,
        "golden_records_distinct": 0,
        "unlinked_snapshots": 0,
        "linkage_pct": 0.0,
    }
    db = market_core.get_db()
    try:
        ensure_canonical_product_id_column(db)
        ensure_match_metadata_columns(db)
        total = db.execute(
            "SELECT COUNT(*) as n FROM price_snapshots WHERE price > 0"
        ).fetchone()["n"]
        linked = db.execute(
            """
            SELECT COUNT(*) as n FROM price_snapshots
            WHERE price > 0
              AND canonical_product_id IS NOT NULL AND canonical_product_id != ''
            """
        ).fetchone()["n"]
        distinct = db.execute(
            """
            SELECT COUNT(DISTINCT canonical_product_id) as n FROM price_snapshots
            WHERE canonical_product_id IS NOT NULL AND canonical_product_id != ''
            """
        ).fetchone()["n"]
        stats["snapshots_linked"] = int(linked)
        stats["golden_records_distinct"] = int(distinct)
        stats["unlinked_snapshots"] = int(total) - int(linked)
        stats["linkage_pct"] = round(int(linked) / int(total) * 100, 1) if total else 0.0

        # match_type distribution + confidence buckets — without these,
        # linkage_pct alone can't distinguish "confidently exact-matched"
        # from "no match found, so a brand-new Golden Record was created"
        # (match_type "none"/"auto"), which have the same effect on
        # linkage_pct but very different reliability.
        by_type = db.execute(
            """
            SELECT COALESCE(NULLIF(match_type, ''), 'unrecorded') as match_type, COUNT(*) as n
            FROM price_snapshots
            WHERE price > 0 AND canonical_product_id IS NOT NULL AND canonical_product_id != ''
            GROUP BY match_type
            """
        ).fetchall()
        stats["match_type_distribution"] = {r["match_type"]: int(r["n"]) for r in by_type}

        buckets = db.execute(
            """
            SELECT
                SUM(CASE WHEN match_confidence >= 0.8 THEN 1 ELSE 0 END) as high,
                SUM(CASE WHEN match_confidence >= 0.4 AND match_confidence < 0.8 THEN 1 ELSE 0 END) as medium,
                SUM(CASE WHEN match_confidence < 0.4 THEN 1 ELSE 0 END) as low,
                SUM(CASE WHEN match_confidence IS NULL THEN 1 ELSE 0 END) as unrecorded
            FROM price_snapshots
            WHERE price > 0 AND canonical_product_id IS NOT NULL AND canonical_product_id != ''
            """
        ).fetchone()
        stats["confidence_buckets"] = {
            "high_ge_0.8": int(buckets["high"] or 0),
            "medium_0.4_0.8": int(buckets["medium"] or 0),
            "low_lt_0.4": int(buckets["low"] or 0),
            "unrecorded": int(buckets["unrecorded"] or 0),
            # match_type/match_confidence are only persisted going forward —
            # links made before this feature shipped (2026-08-06) show as
            # "unrecorded", not because they're untrustworthy. Don't read a
            # large "unrecorded" count as "most links are low confidence".
            "note": "unrecorded = linked before match_type/confidence tracking existed, not low confidence",
        }
    except Exception as exc:
        logger.debug("index_stats db metrics skipped: %s", exc)
    finally:
        db.close()
    stats["health"] = _read_index_health()
    return stats


def enrich_product(item: Dict[str, Any], store_key: str = "") -> Dict[str, Any]:
    """Enrich a single product dict with canonical Index data. Never raises."""
    try:
        return _get_service().enrich(item, store_key=store_key or item.get("store", ""))
    except Exception as exc:
        logger.debug("enrich_product skipped '%s': %s", item.get("name", "?")[:40], exc)
        return item


def enrich_list(items: List[Dict[str, Any]], store_key: str = "") -> List[Dict[str, Any]]:
    """Enrich a list of product dicts in-place."""
    for item in items:
        if isinstance(item, dict):
            enrich_product(item, store_key=store_key or item.get("store", ""))
    return items


def infer_category(name: str) -> Optional[str]:
    """Best-effort canasta-staple category for a product or query name.

    Returns a staple key (``leche``, ``arroz``, ``aceite``, …) or ``None`` when
    nothing matches. Delegates to the index taxonomy, which already encodes the
    cross-category exclusions that token matching can't express — e.g.
    ``"Filete de Atún en Aceite Vegetal"`` resolves to ``None`` (not ``aceite``).

    Returns ``None`` (never raises) when the index taxonomy is unavailable, so
    callers degrade to plain token matching.
    """
    if not name:
        return None
    try:
        from taxonomy.canasta import infer_canasta_item

        return infer_canasta_item(name)
    except Exception:
        return None


async def gov_collect_bcrp() -> Dict[str, Any]:
    """Fetch + resolve BCRP macro series (tipo de cambio USD/PEN, IPC Lima)
    into gov-sourced Golden Records. Safe to call on demand — unlike the
    retail collector cycle, BCRP has no anti-bot protection and returns a
    handful of rows, not thousands (specs/gov-connectors-prd.md Fase 1)."""
    svc = _get_service()
    connector = BCRPConnector()
    try:
        snapshots = await connector.collect()
    except Exception as exc:
        logger.warning("gov_collect_bcrp: fetch failed: %s", exc)
        return {"collected": 0, "resolved": 0, "error": str(exc)}

    resolved = 0
    for snapshot in snapshots:
        try:
            result = svc.resolve_snapshot(snapshot.to_index_snapshot())
            if result.product:
                resolved += 1
        except Exception as exc:
            logger.debug("gov_collect_bcrp: resolve failed for %s: %s", snapshot.commodity_slug, exc)

    logger.info("Gov collect (BCRP): %d fetched, %d resolved", len(snapshots), resolved)
    return {"collected": len(snapshots), "resolved": resolved, "registry_size": svc.size}


def gov_list_observations(
    commodity_slug: str = "", region: str = "", limit: int = 30
) -> List[Dict[str, Any]]:
    """Recent gov-source price observations (BCRP, SISAP, Osinergmin), most
    recent first, optionally filtered by commodity_slug and/or region.
    Never raises — callers get an empty list on failure instead of a 500."""
    try:
        svc = _get_service()
        return svc.list_gov_observations(
            commodity_slug=commodity_slug, region=region, limit=limit
        )
    except Exception as exc:
        logger.warning("gov_list_observations failed: %s", exc)
        return []


def gov_macro_snapshot() -> Dict[str, Any]:
    """Latest tipo de cambio (venta/compra) + IPC Lima from gov-sourced
    Golden Records. Never raises — callers get an empty-shaped response on
    failure instead of a 500."""
    try:
        svc = _get_service()
        tc_rows = svc.list_gov_observations(commodity_slug="tipo_cambio_usd_pen", limit=2)
        ipc_rows = svc.list_gov_observations(commodity_slug="ipc_lima", limit=1)
    except Exception as exc:
        logger.warning("gov_macro_snapshot failed: %s", exc)
        return {"tipo_cambio": None, "ipc_lima": None, "source": "bcrp_pe", "error": str(exc)}

    by_price_type = {row["price_type"]: row for row in tc_rows}
    return {
        "tipo_cambio": (
            {"venta": by_price_type.get("venta"), "compra": by_price_type.get("compra")}
            if by_price_type
            else None
        ),
        "ipc_lima": ipc_rows[0] if ipc_rows else None,
        "source": "bcrp_pe",
    }


def _row_to_snapshot(row: Any) -> tuple[str, str, Dict[str, Any]]:
    store = str(row["store"] or "")
    pid = str(row["product_id"] or "")
    snapshot = {
        "store": store,
        "sku": pid,
        "name": str(row["name"] or ""),
        "brand": str(row["brand"] or ""),
        "price": float(row["price"] or 0),
        "currency": str(row["currency"] or "USD"),
    }
    return store, pid, snapshot


def _resolve_exact_only(resolver: Any, raw_name: str, raw_brand: str) -> Any:
    """Resolve using only an exact canonical_product_id match — never
    Resolver._fuzzy_search/_name_match_search.

    Bypasses a known cli-market-index bug: Resolver.index_product() also
    indexes every product under canonicalize_brand("", product.name) as an
    alias bucket (intended for legitimate private-label cross-referencing).
    For old mis-branded-but-correctly-named products (prod_genrico_*,
    prod_noinformado_* — brand normalization was buggy, but the stored
    product name was always correct), that alias equals the brand a fresh
    resolution attempt for the same real product now correctly computes —
    so _fuzzy_search/_name_match_search rediscover the stale product and the
    fresh attempt inherits its dead ID instead of getting a new correct one.
    Confirmed live 2026-08-07 by tracing resolution against the production
    registry (50,332 products) — see ops/reresolve_stale_brands.py. Used
    only for that residual re-resolution sweep; normal collector traffic
    still goes through Resolver.resolve()."""
    from core.resolver import ResolutionResult, _build_product_id, _variety_fingerprint, infer_category
    from engines.normalizer.brand_normalizer import canonicalize_brand
    from engines.normalizer.unit_normalizer import extract_measurement, format_display

    brand_slug = canonicalize_brand(raw_brand, raw_name)
    measurement = extract_measurement(raw_name)
    category_hint = infer_category(raw_name)
    if not measurement:
        if brand_slug == "unknown":
            return ResolutionResult(None, 0.0, "none")
        measurement = (1.0, "unit")

    qty, unit = measurement
    variety = _variety_fingerprint(raw_name, brand_slug, category_hint)
    lookup_id = _build_product_id(brand_slug, category_hint, qty, unit, variety)

    existing = resolver.registry.get(lookup_id)
    if existing is not None:
        return ResolutionResult(product=existing, confidence=0.98, match_type="exact")

    from api.resources import Measurement as MeasurementDTO
    from api.resources import Product
    from taxonomy.canasta import apply_canasta_taxonomy

    display = format_display(qty, unit)
    candidate = Product(
        id=lookup_id,
        name=raw_name.title(),
        brand=f"brnd_{brand_slug}",
        category=f"cat_{category_hint}",
        measurement=MeasurementDTO(value=qty, unit=unit, display=display),
        created=int(time.time()),
    )
    candidate = apply_canasta_taxonomy(candidate, raw_name)
    return ResolutionResult(product=candidate, confidence=0.0, match_type="none")


@contextlib.contextmanager
def _exact_only_resolution(svc: IndexService):
    """Swap Resolver.resolve for _resolve_exact_only for the duration of one
    resolve_snapshot() call, then restore it. Reuses IndexService's own
    register_product/audit_link/record_snapshot bookkeeping instead of
    duplicating it — only the matching strategy changes. Not thread-safe,
    but this module's re-resolution sweeps run single-threaded."""
    original_resolve = svc.resolver.resolve

    def _patched(raw_name="", raw_brand="", store_key="", price=0.0, currency="USD"):
        return _resolve_exact_only(svc.resolver, raw_name, raw_brand)

    svc.resolver.resolve = _patched
    try:
        yield
    finally:
        svc.resolver.resolve = original_resolve


def _resolve_and_link(
    svc: IndexService,
    db: Any,
    row: Any,
    *,
    dry_run: bool,
    stats: Dict[str, int],
    exact_only: bool = False,
) -> None:
    store, pid, snapshot = _row_to_snapshot(row)
    try:
        if exact_only:
            with _exact_only_resolution(svc):
                result = svc.resolve_snapshot(snapshot)
        else:
            result = svc.resolve_snapshot(snapshot)
    except Exception as exc:
        # Regression: PostgresStore (cli-market-index) opens exactly one
        # psycopg2 connection at construction and never reconnects. Once
        # Postgres drops it (idle timeout), every resolve_snapshot() call on
        # the long-lived _service singleton throws forever, silently, until
        # the process restarts — confirmed live: 0/50 resolved via the warm
        # production process, 50/50 resolved immediately after a restart
        # (fresh singleton, fresh connection). The retry-with-reconnect logic
        # in _index_snapshot_rows only reconnects its own `market_core` db
        # handle, never this module's `_service` global, so it can't recover
        # this failure mode on its own. Drop the dead singleton and retry
        # once against a freshly constructed one before counting it as a
        # real error.
        global _service
        _service = None
        try:
            fresh_svc = _get_service()
            if exact_only:
                with _exact_only_resolution(fresh_svc):
                    result = fresh_svc.resolve_snapshot(snapshot)
            else:
                result = fresh_svc.resolve_snapshot(snapshot)
        except Exception as exc2:
            stats["errors"] += 1
            logger.debug("resolve snapshot %s/%s: %s (retry after service reset: %s)", store, pid, exc, exc2)
            return
    if not result.product:
        stats["skipped"] += 1
        return
    stats["resolved"] += 1
    match = result.match_type
    if match in stats:
        stats[match] += 1
    elif match == "none":
        stats["auto"] += 1

    prod_id = result.product.id
    if not dry_run and prod_id:
        # DB errors (including a dropped connection) propagate to the caller
        # instead of being swallowed here — a dead connection used to go
        # undetected for the rest of the batch (hundreds of silent failures
        # in DEBUG logs) until the final commit crashed the whole process.
        # match_type/match_confidence persist the raw ResolutionResult here —
        # previously discarded after being used only for the in-memory stats
        # counter, leaving no way to later tell an "exact" link from a
        # low-confidence "auto" one without re-running the resolver.
        db.execute(
            """
            UPDATE price_snapshots
            SET canonical_product_id = ?, match_type = ?, match_confidence = ?
            WHERE store = ? AND product_id = ?
            """,
            (prod_id, match, result.confidence, store, pid),
        )
        stats["linked"] += 1


def _fetch_recent_snapshot_rows(db: Any, *, since_minutes: int, limit: int) -> list[Any]:
    import market_core

    if market_core.USE_PG:
        return db.execute(
            """
            SELECT store, product_id, name, brand, price, currency
            FROM price_snapshots
            WHERE queried_at >= NOW() - (%s * INTERVAL '1 minute')
              AND price > 0 AND name IS NOT NULL AND trim(name) != ''
            ORDER BY queried_at DESC
            LIMIT %s
            """,
            (since_minutes, limit),
        ).fetchall()
    return db.execute(
        """
        SELECT store, product_id, name, brand, price, currency
        FROM price_snapshots
        WHERE queried_at >= datetime('now', ?)
          AND price > 0 AND name IS NOT NULL AND trim(name) != ''
        ORDER BY queried_at DESC
        LIMIT ?
        """,
        (f"-{since_minutes} minutes", limit),
    ).fetchall()


def _fetch_unlinked_snapshot_rows(db: Any, *, limit: int) -> list[Any]:
    """One row per (store, product_id) so each batch covers new SKUs, not duplicate history rows."""
    import market_core

    if market_core.USE_PG:
        return db.execute(
            """
            SELECT DISTINCT ON (store, product_id)
              store, product_id, name, brand, price, currency
            FROM price_snapshots
            WHERE (canonical_product_id IS NULL OR canonical_product_id = '')
              AND price > 0 AND name IS NOT NULL AND trim(name) != ''
            ORDER BY store, product_id, queried_at DESC
            LIMIT %s
            """,
            (limit,),
        ).fetchall()
    return db.execute(
        """
        SELECT store, product_id,
               MAX(name) AS name, MAX(brand) AS brand,
               MAX(price) AS price, MAX(currency) AS currency
        FROM price_snapshots
        WHERE (canonical_product_id IS NULL OR canonical_product_id = '')
          AND price > 0 AND name IS NOT NULL AND trim(name) != ''
        GROUP BY store, product_id
        ORDER BY store, product_id
        LIMIT ?
        """,
        (limit,),
    ).fetchall()


def _index_snapshot_rows(
    rows: list[Any],
    *,
    dry_run: bool = False,
    exact_only: bool = False,
) -> Dict[str, int]:
    import market_core

    svc = _get_service()
    stats = {
        "resolved": 0,
        "linked": 0,
        "exact": 0,
        "fuzzy": 0,
        "auto": 0,
        "skipped": 0,
        "errors": 0,
        "registry_size": svc.size,
    }

    db = market_core.get_db()
    try:
        ensure_canonical_product_id_column(db)
        ensure_match_metadata_columns(db)
        seen: set[tuple[str, str]] = set()
        for row in rows:
            store = str(row["store"] or "")
            pid = str(row["product_id"] or "")
            key = (store, pid)
            if key in seen:
                continue
            seen.add(key)
            try:
                _resolve_and_link(svc, db, row, dry_run=dry_run, stats=stats, exact_only=exact_only)
                if not dry_run:
                    # Commit per row instead of once for the whole batch: a
                    # single multi-hundred-row transaction can stay open for
                    # tens of minutes when registry matching is slow, holding
                    # row locks on price_snapshots long enough to block the
                    # collector's concurrent UPSERTs (root cause of the
                    # 2026-07-09 promart insert-error incident).
                    db.commit()
            except Exception as exc:
                # Connection may have dropped mid-batch (idle timeout,
                # network blip). Reconnect once and retry this row instead of
                # continuing to hammer a dead connection for the rest of the
                # batch, or letting the exception kill the whole process.
                logger.warning("index snapshot %s/%s: %s — reconnecting", store, pid, exc)
                try:
                    db.close()
                except Exception:
                    pass
                db = market_core.get_db()
                try:
                    _resolve_and_link(svc, db, row, dry_run=dry_run, stats=stats, exact_only=exact_only)
                    if not dry_run:
                        db.commit()
                except Exception as exc2:
                    stats["errors"] += 1
                    logger.debug("index snapshot %s/%s: retry failed: %s", store, pid, exc2)
    finally:
        db.close()

    stats["registry_size"] = svc.size
    return stats


def _index_recent_snapshots(
    *,
    limit: Optional[int] = None,
    since_minutes: Optional[int] = None,
) -> Dict[str, int]:
    """Batch-resolve recent price_snapshots into Golden Records."""
    import market_core

    limit = limit if limit is not None else int(os.getenv("INDEX_COLLECT_LIMIT", "500"))
    since_minutes = since_minutes if since_minutes is not None else int(
        os.getenv("INDEX_COLLECT_SINCE_MINUTES", "15")
    )

    db = market_core.get_db()
    try:
        ensure_canonical_product_id_column(db)
        ensure_match_metadata_columns(db)
        rows = _fetch_recent_snapshot_rows(db, since_minutes=since_minutes, limit=limit)
    finally:
        db.close()

    return _index_snapshot_rows(rows)


def backfill_canonical_product_ids(
    *,
    limit: Optional[int] = None,
    dry_run: bool = False,
) -> Dict[str, int]:
    """Resolve snapshots missing canonical_product_id and stamp the UPID column."""
    import market_core

    limit = limit if limit is not None else int(os.getenv("INDEX_BACKFILL_LIMIT", "1000"))
    db = market_core.get_db()
    try:
        ensure_canonical_product_id_column(db)
        ensure_match_metadata_columns(db)
        rows = _fetch_unlinked_snapshot_rows(db, limit=limit)
    finally:
        db.close()

    stats = _index_snapshot_rows(rows, dry_run=dry_run)
    stats["fetched"] = len(rows)
    return stats


def _fetch_stale_snapshot_rows(db: Any, *, brand_slugs: list[str], limit: int) -> list[Any]:
    """One row per (store, product_id) whose current canonical_product_id's
    brand segment matches a known-stale slug — a brand fix already shipped in
    BRAND_MAP/GENERIC_BRAND_TOKENS (cli-market-index) that was never
    reapplied to snapshots resolved before the fix. backfill_canonical_product_ids
    only touches NULL canonical_product_id rows, so these stay wrong
    indefinitely without this — confirmed live 2026-08-06 via
    ops/mine_brand_candidates.py: ~8,300 snapshots still carried
    prod_ca_*/prod_heringadulto_*/prod_heringkids_*/prod_noinformado_*/
    prod_genrico_* canonical IDs despite BRAND_MAP/GENERIC_BRAND_TOKENS
    already covering those exact raw brand strings."""
    import market_core

    if not brand_slugs:
        return []
    # Escape the two literal underscores framing the slug so LIKE's '_'
    # single-char wildcard doesn't match anything unintended — brand_slug
    # itself is always underscore-free (core/resolver.py's _slugify strips
    # everything but [a-z0-9]), so nothing inside the slug needs escaping.
    patterns = [f"prod\\_{slug}\\_%" for slug in brand_slugs]

    if market_core.USE_PG:
        clauses = " OR ".join(["canonical_product_id LIKE %s ESCAPE '\\'"] * len(brand_slugs))
        return db.execute(
            f"""
            SELECT DISTINCT ON (store, product_id)
              store, product_id, name, brand, price, currency
            FROM price_snapshots
            WHERE ({clauses}) AND price > 0 AND name IS NOT NULL AND trim(name) != ''
            ORDER BY store, product_id, queried_at DESC
            LIMIT %s
            """,
            (*patterns, limit),
        ).fetchall()
    clauses = " OR ".join(["canonical_product_id LIKE ? ESCAPE '\\'"] * len(brand_slugs))
    return db.execute(
        f"""
        SELECT store, product_id,
               MAX(name) AS name, MAX(brand) AS brand,
               MAX(price) AS price, MAX(currency) AS currency
        FROM price_snapshots
        WHERE ({clauses}) AND price > 0 AND name IS NOT NULL AND trim(name) != ''
        GROUP BY store, product_id
        ORDER BY store, product_id
        LIMIT ?
        """,
        (*patterns, limit),
    ).fetchall()


def _fetch_snapshot_rows_by_canonical_id(db: Any, *, canonical_ids: list[str], limit: int) -> list[Any]:
    """One row per (store, product_id) currently linked to one of the given
    exact canonical_product_id values — for re-resolving snapshots stuck on
    a Golden Record that predates a later improvement to
    cli-market-index's variety-fingerprint logic (a fuzzy/name-match bucket
    or a code fix that now computes a more specific id for the same raw
    name). Unlike _fetch_stale_snapshot_rows (brand-slug LIKE pattern),
    this targets specific known-over-fused canonical_product_id values —
    confirmed live 2026-08-06: prod_laive_lacteos_0.18kg and
    prod_gloria_lacteos_0.946l each grouped multiple genuinely different
    products (cheese varieties; milk vs. cooking cream) under one id,
    despite the current resolver computing a distinct, correct id for each
    when run directly against their raw names (see cli-market-index#16)."""
    import market_core

    if not canonical_ids:
        return []

    if market_core.USE_PG:
        return db.execute(
            """
            SELECT DISTINCT ON (store, product_id)
              store, product_id, name, brand, price, currency
            FROM price_snapshots
            WHERE canonical_product_id = ANY(%s) AND price > 0 AND name IS NOT NULL AND trim(name) != ''
            ORDER BY store, product_id, queried_at DESC
            LIMIT %s
            """,
            (canonical_ids, limit),
        ).fetchall()
    placeholders = ",".join("?" * len(canonical_ids))
    return db.execute(
        f"""
        SELECT store, product_id,
               MAX(name) AS name, MAX(brand) AS brand,
               MAX(price) AS price, MAX(currency) AS currency
        FROM price_snapshots
        WHERE canonical_product_id IN ({placeholders}) AND price > 0 AND name IS NOT NULL AND trim(name) != ''
        GROUP BY store, product_id
        ORDER BY store, product_id
        LIMIT ?
        """,
        (*canonical_ids, limit),
    ).fetchall()


def reresolve_snapshots_by_canonical_id(
    canonical_ids: list[str],
    *,
    limit: Optional[int] = None,
    dry_run: bool = False,
    exact_only: bool = True,
) -> Dict[str, int]:
    """Re-run resolution for snapshots currently linked to specific
    over-fused canonical_product_id values (see
    _fetch_snapshot_rows_by_canonical_id). exact_only defaults to True here
    (unlike reresolve_stale_snapshots) because the whole point is to let
    each raw name compute its own distinct, correct id via an exact match
    or a fresh registration — routing through normal fuzzy/name-match
    resolution risks re-matching everything back onto the same over-fused
    id it's trying to split apart."""
    import market_core

    limit = limit if limit is not None else 2000
    db = market_core.get_db()
    try:
        ensure_canonical_product_id_column(db)
        ensure_match_metadata_columns(db)
        rows = _fetch_snapshot_rows_by_canonical_id(db, canonical_ids=canonical_ids, limit=limit)
    finally:
        db.close()

    stats = _index_snapshot_rows(rows, dry_run=dry_run, exact_only=exact_only)
    stats["fetched"] = len(rows)
    return stats


def reresolve_stale_snapshots(
    brand_slugs: list[str],
    *,
    limit: Optional[int] = None,
    dry_run: bool = False,
    exact_only: bool = False,
) -> Dict[str, int]:
    """Re-run resolution for snapshots stuck on a canonical_product_id from a
    brand-mapping bug that's since been fixed upstream. Unlike
    backfill_canonical_product_ids, _resolve_and_link's UPDATE has no guard
    on the prior canonical_product_id value, so feeding it already-linked
    rows safely overwrites them with the corrected resolution — this is a
    one-off maintenance sweep (see ops/reresolve_stale_brands.py), not part
    of the routine collector cycle.

    exact_only=True routes through _resolve_exact_only instead of the normal
    Resolver.resolve() — required for slugs whose stale products are
    discoverable via cli-market-index's alias-indexing bug (see
    _resolve_exact_only's docstring); normal fuzzy/name-match resolution
    would just re-match them onto the same stale product it's trying to fix."""
    import market_core

    limit = limit if limit is not None else 2000
    db = market_core.get_db()
    try:
        ensure_canonical_product_id_column(db)
        ensure_match_metadata_columns(db)
        rows = _fetch_stale_snapshot_rows(db, brand_slugs=brand_slugs, limit=limit)
    finally:
        db.close()

    stats = _index_snapshot_rows(rows, dry_run=dry_run, exact_only=exact_only)
    stats["fetched"] = len(rows)
    return stats


def sync_golden_taxonomy_to_core() -> int:
    """Export index Golden Record taxonomy → core enrichment_cache for indicators."""
    try:
        import market_core
        from market_core.golden_taxonomy import set_taxonomy_registry

        svc = _get_service()
        products = svc.export_taxonomy_registry()
        if not products:
            return 0
        db = market_core.get_db()
        try:
            set_taxonomy_registry(db, products, registry_size=svc.size)
            db.commit()
        finally:
            db.close()
        logger.info("Index taxonomy synced: %d golden records", len(products))
        return len(products)
    except Exception as exc:
        logger.warning("sync_golden_taxonomy_to_core failed: %s", exc)
        return 0


def certify_round(
    products_saved: int,
    store_sample: str = "",
    *,
    limit: Optional[int] = None,
    since_minutes: Optional[int] = None,
) -> Dict[str, int]:
    """
    Called after each collect_prices.py cycle.
    Batch-resolves recent snapshots and returns indexing stats.
    """
    try:
        stats = _index_recent_snapshots(limit=limit, since_minutes=since_minutes)
        stats["taxonomy_synced"] = sync_golden_taxonomy_to_core()
        logger.info(
            "Index gate: %d prices collected → %d resolved, %d linked "
            "(%d exact, %d fuzzy, %d auto) registry=%d taxonomy=%d store=%s",
            products_saved,
            stats["resolved"],
            stats["linked"],
            stats["exact"],
            stats["fuzzy"],
            stats["auto"],
            stats["registry_size"],
            stats.get("taxonomy_synced", 0),
            store_sample or "mixed",
        )
        _record_index_health("ok")
        return stats
    except Exception as exc:
        logger.warning("Index gate certify_round failed: %s", exc)
        _record_index_health("failed", error=str(exc))
        return {
            "resolved": 0,
            "linked": 0,
            "exact": 0,
            "fuzzy": 0,
            "auto": 0,
            "skipped": 0,
            "errors": 0,
            "registry_size": 0,
            "failed": 1,
        }