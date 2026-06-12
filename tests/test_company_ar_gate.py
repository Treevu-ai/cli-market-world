"""AR gate + Company LinkedIn price copy resolution."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "ops"))

from company_ar_gate import (
    ar_gate_report,
    build_canasta_price_block,
    is_ar_store,
    resolve_company_price_marker,
)

POST_TEMPLATE = """\
Esta semana, el collector registró los siguientes spreads entre mercados para ítems de canasta básica:

— Queso: 2.93x entre el precio por kilo en AR (ARS) y PE (PEN)
— Pan: 2.75x entre AR y PE
— Aceite: 2.65x entre AR y PE

[ACTUALIZAR: si hay ≥ 2 cadenas AR con ≥ 6/10 ítems comparables, reemplazar spreads con precios absolutos en ARS y PEN respectivamente. Nunca convertir a USD en el cuerpo del post.]

Estos spreads no son estáticos.
"""


def test_is_ar_store():
    assert is_ar_store("Vea AR")
    assert is_ar_store("Jumbo AR")
    assert not is_ar_store("Carrefour BR")
    assert not is_ar_store("Metro")


def test_ar_gate_blocked_with_one_chain():
    canasta = [
        {"store_name": "Vea AR", "items": 10, "total": 736.17, "currency": "ARS"},
        {"store_name": "Carrefour BR", "items": 9, "total": 601.22, "currency": "BRL"},
    ]
    report = ar_gate_report(canasta)
    assert report["qualifying_count"] == 1
    assert report["gate_pass"] is False


def test_ar_gate_passes_with_two_chains():
    canasta = [
        {"store_name": "Vea AR", "items": 10, "total": 736.17, "currency": "ARS"},
        {"store_name": "Jumbo AR", "items": 8, "total": 800.0, "currency": "ARS"},
    ]
    report = ar_gate_report(canasta)
    assert report["qualifying_count"] == 2
    assert report["gate_pass"] is True


def test_resolve_marker_keeps_spreads_when_gate_blocked():
    data = {
        "canasta_basica": [{"store_name": "Vea AR", "items": 10, "total": 736.17, "currency": "ARS"}],
        "canasta_spreads": [
            {"item": "queso", "currency": "ARS", "avg_price": 314.99, "spread_ratio": 2.93, "price_basis": "per_kg"},
            {"item": "pan", "currency": "ARS", "avg_price": 853.95, "spread_ratio": 2.75, "price_basis": "per_kg"},
            {"item": "aceite", "currency": "ARS", "avg_price": 1138.57, "spread_ratio": 2.65, "price_basis": "per_L"},
            {"item": "queso", "currency": "PEN", "avg_price": 31.79, "price_basis": "per_kg"},
            {"item": "pan", "currency": "PEN", "avg_price": 14.83, "price_basis": "per_kg"},
            {"item": "aceite", "currency": "PEN", "avg_price": 18.16, "price_basis": "per_L"},
        ],
    }
    out = resolve_company_price_marker(POST_TEMPLATE, data)
    assert "[ACTUALIZAR" not in out
    assert "2.93x" in out
    assert "ARS 315" not in out


def test_resolve_marker_uses_absolute_prices_when_gate_passes():
    data = {
        "canasta_basica": [
            {"store_name": "Vea AR", "items": 10, "total": 736.17, "currency": "ARS"},
            {"store_name": "Jumbo AR", "items": 8, "total": 800.0, "currency": "ARS"},
        ],
        "canasta_spreads": [
            {"item": "queso", "currency": "ARS", "avg_price": 314.99, "spread_ratio": 2.93, "price_basis": "per_kg"},
            {"item": "pan", "currency": "ARS", "avg_price": 853.95, "spread_ratio": 2.75, "price_basis": "per_kg"},
            {"item": "aceite", "currency": "ARS", "avg_price": 1138.57, "spread_ratio": 2.65, "price_basis": "per_L"},
            {"item": "queso", "currency": "PEN", "avg_price": 31.79, "price_basis": "per_kg"},
            {"item": "pan", "currency": "PEN", "avg_price": 14.83, "price_basis": "per_kg"},
            {"item": "aceite", "currency": "PEN", "avg_price": 18.16, "price_basis": "per_L"},
        ],
    }
    out = resolve_company_price_marker(POST_TEMPLATE, data)
    assert "[ACTUALIZAR" not in out
    assert "ARS 315/kg (AR) · PEN 31.79/kg (PE)" in out
    assert "2.93x" not in out


def test_build_canasta_price_block_modes():
    blocked_data = {
        "canasta_basica": [{"store_name": "Vea AR", "items": 10, "currency": "ARS"}],
        "canasta_spreads": [
            {"item": "queso", "currency": "ARS", "spread_ratio": 2.93, "price_basis": "per_kg"},
        ],
    }
    block, meta = build_canasta_price_block(blocked_data)
    assert meta["mode"] == "spread"
    assert "2.93x" in block
