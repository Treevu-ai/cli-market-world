"""Regression test for market_cli.cmd_upgrade.

--manual-transfer used to be forwarded to POST /billing/pro-checkout as
"manual_transfer", and cmd_upgrade had a rendering branch for
payment_mode == "manual_transfer" / manual_steps / payment_phone. The
backend (cli-market-backend/routers/payments.py) never read that field
and never returned those keys — the flag and its branch were dead code
that silently did nothing. Both were removed; this test locks in that
the checkout payload stays clean and the Mercado Pago panel is always
what renders for yape/plin/mercadopago.
"""

from __future__ import annotations

import argparse

import market_cli


def _args(**overrides):
    base = dict(plan=None, payment="yape", email=None, resend=False, promo_code=None, json=False)
    base.update(overrides)
    return argparse.Namespace(**base)


def test_upgrade_payload_has_no_manual_transfer_key(monkeypatch):
    captured = {}

    def fake_api(method, path, body=None):
        captured["body"] = body
        return {"message": "Listo", "approve_url": "https://mp.example/pay"}

    monkeypatch.setattr(market_cli, "get_token_with_prompt", lambda: "sk-test")
    monkeypatch.setattr(market_cli, "cli_api", fake_api)
    monkeypatch.setattr(market_cli.console, "print", lambda *a, **k: None)

    market_cli.cmd_upgrade(_args())

    assert "manual_transfer" not in captured["body"]
    assert captured["body"] == {"payment_method": "yape", "lang": market_cli.get_lang()}


def test_no_manual_transfer_references_remain():
    import pathlib
    source = pathlib.Path(market_cli.__file__).read_text(encoding="utf-8")
    for needle in ("manual_transfer", "manual-transfer", "manual_steps", "payment_mode", "payment_phone"):
        assert needle not in source, f"dead manual-transfer reference still present: {needle!r}"
