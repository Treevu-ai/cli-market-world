"""Tests for dashboard content view model."""

from dashboard_view_model import build_dashboard_view_model, _fmt_age_es, _global_system_status


def test_fmt_age_es_minutes():
    assert "minuto" in _fmt_age_es(0.4)


def test_global_system_status_ok():
    st = _global_system_status(
        fresh_24h_pct=90,
        moat_age_h=2,
        collector_status="ok",
        snapshots_24h=100,
        total_indexed=1000,
        freshness_label="fresh",
    )
    assert st["state"] == "ok"
    assert "ok" in st["label"]


def test_build_dashboard_view_model_blocks():
    data = {
        "generated_at": "2026-05-29T12:00:00+00:00",
        "kpis": {
            "total_indexed": 38464,
            "stores_indexed": 35,
            "fresh_24h_pct": 97,
            "moat_age_hours": 0.4,
            "snapshots_24h": 500,
        },
        "by_country": [{"country": "PE", "count": 1}, {"country": "AR", "count": 1}],
        "moat_guide": {
            "layers": [{"id": "freshness", "metrics": {"status": "fresh"}}],
        },
        "collector": {"status": "ok"},
        "canasta_basica": [
            {"store_name": "Wong", "items": 8, "total": 120.5, "currency": "PEN"},
            {"store_name": "Metro", "items": 3, "total": 40.0, "currency": "PEN"},
        ],
        "cheapest_by_line": [{"line_name": "Supermercados", "store_name": "Metro", "avg_price": 4.5, "currency": "PEN"}],
        "marketing_spreads": [
            {"seed": "aceite", "spread_ratio": 2.6, "stores": 3, "sample_name": "Aceite 1L", "currency": "ARS"},
        ],
        "inflation": [{"line": "Super", "currency": "PEN", "avg_now": 10, "avg_before": 0, "delta_pct": 0}],
        "top_risers": [],
        "top_fallers": [],
        "analytics_meta": {"marketing_canasta_min_spread": 2.5},
        "quality_funnel": {
            "captured": 38464,
            "flagged": 100,
            "clean": 38364,
            "citable": 1,
            "filters": ["discount>=90%"],
        },
        "indicators": {
            "enrichment": [
                {
                    "key": "imf_inflation_yoy",
                    "name": "IMF inflation YoY",
                    "value": 3.5,
                    "unit": "pct",
                    "country": "PE",
                    "source": "IMF",
                },
            ],
        },
        "store_health": [],
        "suspect_discounts": [],
        "outliers": [],
        "dispersion": [],
        "by_line_currency": [],
    }
    view = build_dashboard_view_model(data)
    assert view["spec_version"] == "1.2"
    assert view["locale"] == "es"
    assert "hero" in view["blocks"]
    hero = view["blocks"]["hero"]
    assert "38.464" in hero["subtitle"]
    assert len(hero["trust_badges"]) == 3

    canasta = view["blocks"]["canasta"]
    assert canasta["stores"][0]["store_name"] == "Wong"
    assert canasta["stores"][0]["comparable"] is True
    assert canasta["stores"][1]["warning"] is not None

    spreads = view["blocks"]["price_spreads"]
    assert spreads["items"][0]["spread_ratio"] == 2.6
    assert spreads["data_rule"] == "marketing_spreads ONLY (not dispersion)"

    infl = view["blocks"]["inflation"]
    assert infl["state"] == "measuring"
    assert "Midiendo" in infl["measuring_copy"]

    assert "global_bar" in view["blocks"]
    assert "portada" in view["blocks"]
    assert "quality_funnel" in view["blocks"]
    assert view["blocks"]["portada"]["cards"][0]["label"] == "INVENTORY"

    enrich = view["blocks"]["enrichment"]
    assert enrich["state"] == "ok"
    assert enrich["items"][0]["tier"] == "tier2"
    assert "enrichment" in view["reading_order"]
