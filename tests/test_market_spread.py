"""Tests for unit parsing and spread analytics."""

from market_spread import (
    build_spread_analytics,
    compute_canasta_spreads,
    infer_subcategory,
)
from market_units import parse_pack_size, price_per_base_unit


def test_parse_pack_size_grams_and_liters():
    assert parse_pack_size("Arroz Costeño 750g") == (0.75, "kg")
    assert parse_pack_size("Leche Gloria 1L entera") == (1.0, "L")
    assert parse_pack_size("Aceite 900 ml") == (0.9, "L")


def test_price_per_base_unit():
    ppu = price_per_base_unit(7.5, "Arroz superior 750g")
    assert ppu is not None
    assert ppu["basis"] == "kg"
    assert abs(ppu["price_per"] - 10.0) < 0.01


def test_infer_subcategory_supermercados():
    assert infer_subcategory("supermercados", "Arroz Extra Costeño 1kg", "") == "arroz"
    assert infer_subcategory("supermercados", "TV Samsung 50 pulgadas", "") == "otros"


def test_dispersion_uses_subcategory_not_whole_supermercados():
    products = [
        {"line": "supermercados", "line_name": "Supermercados", "currency": "PEN",
         "category": "", "name": "Arroz 1kg", "brand": "", "price": 4.0, "store": "wong"},
        {"line": "supermercados", "line_name": "Supermercados", "currency": "PEN",
         "category": "", "name": "Arroz premium 1kg", "brand": "", "price": 5.0, "store": "metro"},
        {"line": "supermercados", "line_name": "Supermercados", "currency": "PEN",
         "category": "", "name": "Arroz familiar 1kg", "brand": "", "price": 6.0, "store": "plazavea"},
        {"line": "supermercados", "line_name": "Supermercados", "currency": "PEN",
         "category": "", "name": "Televisor 55", "brand": "", "price": 2500.0, "store": "wong"},
    ]
    data = build_spread_analytics(products)
    arroz = [d for d in data["dispersion"] if d.get("subcategory") == "arroz"]
    assert len(arroz) == 1
    assert arroz[0]["status"] != "crit"
    assert data["dispersion_crit_count"] == 0


def test_canasta_spreads_need_two_stores():
    products = [
        {"line": "supermercados", "line_name": "Super", "currency": "PEN", "category": "",
         "name": "Arroz 1kg", "brand": "", "price": 4.0, "store": "wong", "store_name": "Wong"},
        {"line": "supermercados", "line_name": "Super", "currency": "PEN", "category": "",
         "name": "Arroz 1kg", "brand": "", "price": 6.0, "store": "metro", "store_name": "Metro"},
    ]
    spreads = compute_canasta_spreads(products)
    arroz = [s for s in spreads if s["item"] == "arroz"]
    assert len(arroz) == 1
    assert arroz[0]["stores"] == 2
