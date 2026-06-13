"""Smoke tests for dashboard_view_model (phase 6 / ticket 3.7)."""

from __future__ import annotations

from market_core.dashboard_view_model import SPEC_VERSION, build_dashboard_view_model


def _minimal_dashboard_payload() -> dict:
    return {
        "generated_at": "2026-06-13T12:00:00+00:00",
        "kpis": {
            "total_indexed": 54000,
            "stores_indexed": 38,
            "fresh_24h_pct": 85.0,
            "moat_age_hours": 2.0,
            "snapshots_24h": 1200,
        },
        "collector": {"status": "ok", "interval_hours": 8},
        "by_country": [{"country": "PE"}, {"country": "AR"}, {"country": "BR"}],
        "quality_funnel": {
            "captured": 54000,
            "clean": 50000,
            "flagged": 4000,
            "citable": 48000,
        },
        "moat_guide": {
            "layers": [{"id": "freshness", "metrics": {"status": "fresh"}}],
        },
        "canasta_basica": [
            {
                "store_name": "Plaza Vea",
                "currency": "PEN",
                "total": 45.5,
                "items": 8,
            },
            {
                "store_name": "Tottus",
                "currency": "PEN",
                "total": 42.0,
                "items": 4,
            },
        ],
    }


def test_build_dashboard_view_model_spec_and_locale():
    view = build_dashboard_view_model(_minimal_dashboard_payload())
    assert view["spec_version"] == SPEC_VERSION
    assert view["locale"] == "es"
    assert view["generated_at"]
    assert view["footer_stamp"]
    assert isinstance(view["tooltips"], dict)
    assert view["tooltips"]["freshness"]


def test_build_dashboard_view_model_required_blocks():
    view = build_dashboard_view_model(_minimal_dashboard_payload())
    blocks = view["blocks"]
    for block_id in (
        "global_bar",
        "portada",
        "quality_funnel",
        "hero",
        "moat_narrative",
        "canasta",
        "price_spreads",
        "inflation",
        "enrichment",
        "exploration",
        "ops",
    ):
        assert block_id in blocks, f"missing block {block_id}"
        assert blocks[block_id]["id"] == block_id


def test_build_dashboard_view_model_hero_ok_state():
    view = build_dashboard_view_model(_minimal_dashboard_payload())
    hero = view["blocks"]["hero"]
    assert hero["state"] == "ok"
    assert hero["title"]
    assert hero["subtitle"]
    assert len(hero["trust_badges"]) == 3
    assert hero["sticky"] is True


def test_build_dashboard_view_model_portada_acceso():
    view = build_dashboard_view_model(_minimal_dashboard_payload())
    portada = view["blocks"]["portada"]
    assert len(portada["cards"]) == 3
    acceso = portada["acceso"]
    assert isinstance(acceso, list)
    assert len(acceso) >= 5
    assert all("cmd" in row and "use" in row for row in acceso)
    assert any("/v1/sources/health" in row["cmd"] for row in acceso)


def test_build_dashboard_view_model_canasta_comparability():
    view = build_dashboard_view_model(_minimal_dashboard_payload())
    stores = view["blocks"]["canasta"]["stores"]
    assert len(stores) == 2
    by_name = {s["store_name"]: s for s in stores}
    assert by_name["Plaza Vea"]["comparable"] is True
    assert by_name["Tottus"]["comparable"] is False
    assert by_name["Tottus"]["warning"]


def test_build_dashboard_view_model_reading_order():
    view = build_dashboard_view_model(_minimal_dashboard_payload())
    order = view["reading_order"]
    assert order[0] == "global_bar"
    assert "hero" in order
    assert "ops" in order
    assert set(order) <= set(view["blocks"])
