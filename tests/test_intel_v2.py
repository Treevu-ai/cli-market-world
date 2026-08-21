"""Unit tests for Intelligence v2 helpers (no full app import)."""

from __future__ import annotations

from market_intel_v2 import (
    PROMO_DISCOUNT_THRESHOLD,
    _affordability_disclaimer_es,
    _affordability_headline_v2,
    build_coverage_table_rows,
    coverage_partial_label,
)


def test_affordability_headline_uses_average_not_ipc_gap():
    headline = _affordability_headline_v2(
        cc="PE",
        currency="PEN",
        canasta_avg=76.5,
        canastas_per_wage_avg=14.8,
        rpv_pct=2.1,
    )
    assert "promedio" in headline
    assert "RPV" in headline
    assert "IPC" not in headline
    assert "gap" not in headline.lower()


def test_affordability_disclaimer_is_country_specific():
    """Real bug from live validation: the disclaimer said 'hogar peruano' /
    'IPC INEI' for every country including AR/MX/BR/CO/CL."""
    ar = _affordability_disclaimer_es("AR")
    mx = _affordability_disclaimer_es("MX")
    pe = _affordability_disclaimer_es("PE")

    assert "argentino" in ar
    assert "INDEC" in ar
    assert "peruano" not in ar
    assert "INEI" not in ar

    assert "mexicano" in mx
    assert "INEGI" in mx

    assert "peruano" in pe
    assert "INEI" in pe


def test_affordability_disclaimer_falls_back_for_unknown_country():
    disclaimer = _affordability_disclaimer_es("ZZ")
    assert "local" in disclaimer
    assert "oficial" in disclaimer


def _insert_canasta_snapshot(db, *, store, store_name, price, currency="PEN"):
    items = [
        ("l", "Leche Gloria 1L"),
        ("a", "Arroz Costeño 1kg"),
        ("ac", "Aceite Vegetal 1L"),
    ]
    for prefix, name in items:
        db.execute(
            """INSERT OR IGNORE INTO price_snapshots
               (product_id, store, store_name, name, price, currency, line, line_name, queried_at)
               VALUES (?, ?, ?, ?, ?, ?, 'supermercados', 'Supermercados', '2026-08-21 08:00:00')""",
            (f"{prefix}-{store}", store, store_name, name, price, currency),
        )


def test_compute_affordability_v2_gates_score_on_extreme_canasta_spread(isolated_db):
    """Real example from live validation (AR, 2026-08-21): the same 3-item
    canasta cost 1,498 ARS at one retailer and 141,550 ARS at another (a
    ~9,350% spread) -- not one comparable basket. compute_affordability_v2
    must not publish a numeric score/band on top of that average."""
    from market_intel_v2 import compute_affordability_v2

    mc = isolated_db
    mc.ensure_db_initialized()
    db = mc.get_db()
    # "wong" and "metro" are real PE store keys already in STORES.
    _insert_canasta_snapshot(db, store="wong", store_name="Wong", price=5.0)
    _insert_canasta_snapshot(db, store="metro", store_name="Metro", price=500.0)
    db.commit()

    result = compute_affordability_v2(db, country="PE", line="supermercados", days=30)
    db.close()

    assert result["components"]["canasta_band_spread_pct"] > 100
    assert result["affordability_score"] is None
    assert result["affordability_band"] == "unavailable"
    assert "unavailable_reason" in result


def test_compute_affordability_v2_scores_normally_within_spread_threshold(isolated_db):
    """No regression: a normal, comparable canasta spread still publishes a
    numeric score as before."""
    from market_intel_v2 import compute_affordability_v2

    mc = isolated_db
    mc.ensure_db_initialized()
    db = mc.get_db()
    _insert_canasta_snapshot(db, store="wong", store_name="Wong", price=10.0)
    _insert_canasta_snapshot(db, store="metro", store_name="Metro", price=11.0)
    db.commit()

    result = compute_affordability_v2(db, country="PE", line="supermercados", days=30)
    db.close()

    assert result["components"]["canasta_band_spread_pct"] <= 100
    assert result["affordability_band"] != "unavailable"


def test_promo_threshold_constant():
    assert PROMO_DISCOUNT_THRESHOLD == 0.03


def test_coverage_partial_label():
    assert coverage_partial_label(59.9) == "[COBERTURA PARCIAL]"
    assert coverage_partial_label(60.0) == ""
    assert coverage_partial_label(None) == ""


def test_build_coverage_table_rows_from_store_health():
    data = {
        "store_health": [
            {
                "store": "wong",
                "country": "PE",
                "line": "supermercados",
                "success_pct": 92.0,
                "coverage_7d_pct": 100.0,
                "last_snapshot": "2026-06-24T10:00:00",
            }
        ]
    }
    rows = build_coverage_table_rows(data)
    assert len(rows) == 1
    assert rows[0]["store"] == "wong"
    assert rows[0]["success_pct"] == 92.0
