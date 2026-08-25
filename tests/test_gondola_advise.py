"""Vendored gondola engine used on Fly until cli-market-core 1.12.49 is pinned."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from gondola_advise import (
    DENYLIST,
    GondolaAdviceError,
    advise_gondola,
    validate_advice,
)
from market_core import ensure_db_initialized
from routers.intel import _gondola_engine

ensure_db_initialized()


def test_engine_loader_returns_callable():
    advise, err = _gondola_engine()
    assert callable(advise)
    assert issubclass(err, ValueError)


def test_validate_advice_rejects_list_without_evidence():
    with pytest.raises(GondolaAdviceError, match="evidence"):
        validate_advice({
            "actions": [{
                "type": "LIST",
                "rationale": "listar en metro",
                "evidence": [],
            }]
        })


def test_validate_advice_rejects_denylist_rationale():
    with pytest.raises(GondolaAdviceError):
        validate_advice({
            "actions": [{
                "type": "HOLD",
                "rationale": "aumentar facings en el planograma",
                "evidence": [],
            }]
        })
    assert "facing" in DENYLIST


def test_vendor_advise_gondola_list_on_fresh_store(monkeypatch):
    from market_core import get_db

    catalog = {
        "wong": {"name": "Wong", "country": "PE", "line": "supermercados"},
        "metro": {"name": "Metro", "country": "PE", "line": "supermercados"},
        "exito": {"name": "Éxito", "country": "CO", "line": "supermercados"},
    }
    monkeypatch.setattr("market_core.store_credentials.get_all_stores", lambda: catalog)
    now = datetime.now(timezone.utc)
    db = get_db()
    try:
        db.execute("DELETE FROM price_snapshots WHERE store IN ('wong','metro','exito')")
        db.execute(
            """INSERT INTO price_snapshots
               (product_id, store, store_name, name, brand, price, list_price, discount,
                line, currency, queried_at, confidence)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'supermercados', 'PEN', ?, 'ok')""",
            ("g1", "wong", "Wong", "Leche Gloria Entera 1L", "Gloria", 4.5, None, 0, now.isoformat()),
        )
        db.execute(
            """INSERT INTO price_snapshots
               (product_id, store, store_name, name, brand, price, list_price, discount,
                line, currency, queried_at, confidence)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'supermercados', 'PEN', ?, 'ok')""",
            ("g2", "metro", "Metro", "Arroz Costeno 1kg", "Costeno", 5.0, None, 0, now.isoformat()),
        )
        db.commit()
        out = advise_gondola(
            db,
            country="PE",
            category="leche",
            portfolio=[{"query": "leche gloria 1l", "pvp": 4.2}],
            line="supermercados",
        )
    finally:
        db.close()

    cells = {(c["sku"], c["store"]): c["status"] for c in out["coverage"]["cells"]}
    assert cells[("leche gloria 1l", "wong")] == "listed"
    assert cells[("leche gloria 1l", "metro")] == "missing"
    assert "exito" not in {c["store"] for c in out["coverage"]["cells"]}
    assert any(a["type"] == "LIST" for a in out["actions"])
