"""Regression test for cli-market-backend#127 (O6): a "not found" barcode/
product error used to fall through to the generic market doctor/hello
hint, which is irrelevant for a missing-product error."""

from __future__ import annotations

import market_ui as ui


def test_not_found_suggests_search_and_enrich_not_doctor():
    cmds = ui.error_next_commands(404, "not found")
    assert "market doctor" not in cmds
    assert any("search" in c for c in cmds)
    assert any("enrich" in c for c in cmds)


def test_invalid_barcode_also_suggests_search():
    cmds = ui.error_next_commands(400, "invalid barcode format")
    assert "market doctor" not in cmds


def test_auth_errors_still_suggest_login():
    cmds = ui.error_next_commands(401, "token expired")
    assert "market login" in cmds


def test_truly_unknown_error_keeps_generic_fallback():
    cmds = ui.error_next_commands(None, "something unrelated exploded")
    assert cmds == ["market doctor", "market hello"]
