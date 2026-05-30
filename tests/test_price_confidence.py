"""Tests for price confidence flags and median outlier detection."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from market_spread import find_median_outliers
from price_confidence import (
    DISCOUNT_PUBLIC_MAX,
    DISCOUNT_PUBLIC_MIN,
    compute_snapshot_confidence,
    discount_is_scrape_error,
    discount_public_ok,
    spread_public_ok,
)


def test_discount_public_range():
    assert discount_public_ok(50)
    assert discount_public_ok(DISCOUNT_PUBLIC_MIN)
    assert discount_public_ok(DISCOUNT_PUBLIC_MAX)
    assert not discount_public_ok(99)
    assert not discount_public_ok(2)
    assert discount_is_scrape_error(99)
    assert not discount_is_scrape_error(80)


def test_compute_snapshot_confidence():
    assert compute_snapshot_confidence(12.0, 15.0) == "ok"
    assert compute_snapshot_confidence(1.0, 100.0) == "suspect"
    assert compute_snapshot_confidence(10.0, None) == "ok"


def test_spread_public_ok():
    assert spread_public_ok(2.5)
    assert spread_public_ok(10.0)
    assert not spread_public_ok(10.1)


def test_median_outliers_bidirectional():
    products = [
        {"line": "supermercados", "line_name": "Super", "currency": "PEN", "category": "",
         "name": "Arroz extra A", "price": 5.0, "store": "wong", "store_name": "Wong"},
        {"line": "supermercados", "line_name": "Super", "currency": "PEN", "category": "",
         "name": "Arroz extra B", "price": 5.5, "store": "metro", "store_name": "Metro"},
        {"line": "supermercados", "line_name": "Super", "currency": "PEN", "category": "",
         "name": "Arroz extra C", "price": 4.8, "store": "plazavea", "store_name": "Plaza Vea"},
        {"line": "supermercados", "line_name": "Super", "currency": "PEN", "category": "",
         "name": "Arroz extra D", "price": 5.2, "store": "tottus", "store_name": "Tottus"},
        {"line": "supermercados", "line_name": "Super", "currency": "PEN", "category": "",
         "name": "Arroz extra E", "price": 5.1, "store": "jumbo", "store_name": "Jumbo"},
        {"line": "supermercados", "line_name": "Super", "currency": "PEN", "category": "",
         "name": "Arroz scrape error", "price": 0.5, "store": "vea", "store_name": "Vea"},
        {"line": "supermercados", "line_name": "Super", "currency": "PEN", "category": "",
         "name": "Arroz premium typo", "price": 50.0, "store": "wong2", "store_name": "Wong 2"},
    ]
    hits = find_median_outliers(products, min_group=5, band=5.0, limit=10)
    names = {h["name"] for h in hits}
    assert "Arroz scrape error" in names
    assert "Arroz premium typo" in names
    assert hits[0]["confidence"] == "suspect"
