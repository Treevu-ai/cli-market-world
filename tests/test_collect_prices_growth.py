"""Tests for collect_prices.py's Growth-tier per-store refresh scheduling."""

from __future__ import annotations

import pytest
from market_core import ensure_db_initialized, get_db

ensure_db_initialized()

import collect_prices as cp

_STALE = "test_cp_growth_stale"
_FRESH = "test_cp_growth_fresh"
_NON_GROWTH = "test_cp_growth_nongrowth"


@pytest.fixture(autouse=True)
def clean_growth_test_rows():
    db = get_db()
    for sid in (_STALE, _FRESH, _NON_GROWTH):
        db.execute("DELETE FROM price_snapshots WHERE store = ?", (sid,))
        db.execute("DELETE FROM store_credentials WHERE store_id = ?", (sid,))
    db.commit()
    db.close()
    yield
    db = get_db()
    for sid in (_STALE, _FRESH, _NON_GROWTH):
        db.execute("DELETE FROM price_snapshots WHERE store = ?", (sid,))
        db.execute("DELETE FROM store_credentials WHERE store_id = ?", (sid,))
    db.commit()
    db.close()


def test_stale_growth_store_is_due():
    db = get_db()
    db.execute(
        "INSERT INTO store_credentials (store_id, platform, store_name, active, is_growth) "
        "VALUES (?, 'woocommerce', ?, 1, 1)",
        (_STALE, _STALE),
    )
    db.execute(
        "INSERT INTO price_snapshots (product_id, store, name, price, currency, queried_at) "
        "VALUES (?, ?, 'X', 1, 'PEN', datetime('now', '-3 hours'))",
        (f"p-{_STALE}", _STALE),
    )
    db.commit()
    db.close()

    due = cp._get_due_growth_stores()
    assert _STALE in due


def test_fresh_growth_store_is_not_due():
    db = get_db()
    db.execute(
        "INSERT INTO store_credentials (store_id, platform, store_name, active, is_growth) "
        "VALUES (?, 'woocommerce', ?, 1, 1)",
        (_FRESH, _FRESH),
    )
    db.execute(
        "INSERT INTO price_snapshots (product_id, store, name, price, currency, queried_at) "
        "VALUES (?, ?, 'Y', 1, 'PEN', datetime('now'))",
        (f"p-{_FRESH}", _FRESH),
    )
    db.commit()
    db.close()

    due = cp._get_due_growth_stores()
    assert _FRESH not in due


def test_non_growth_store_never_due():
    db = get_db()
    db.execute(
        "INSERT INTO store_credentials (store_id, platform, store_name, active, is_growth) "
        "VALUES (?, 'woocommerce', ?, 1, 0)",
        (_NON_GROWTH, _NON_GROWTH),
    )
    db.commit()
    db.close()

    due = cp._get_due_growth_stores()
    assert _NON_GROWTH not in due


def test_never_collected_growth_store_is_due():
    db = get_db()
    db.execute(
        "INSERT INTO store_credentials (store_id, platform, store_name, active, is_growth) "
        "VALUES (?, 'woocommerce', ?, 1, 1)",
        (_STALE, _STALE),
    )
    db.commit()
    db.close()

    due = cp._get_due_growth_stores()
    assert _STALE in due


def test_no_growth_stores_returns_empty_list():
    assert cp._get_due_growth_stores() == []
