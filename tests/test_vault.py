"""Tests for payment vault endpoints — PayPal Vault + MercadoPago card tokenization."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).parent.parent))

from market_core import db_save_user, db_set_subscription, ensure_db_initialized, get_db
from market_server import app, hash_password
from market_vault import bind_vault_customer, bind_vault_payment_token

import market_audit
import market_vault

ensure_db_initialized()
client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_db():
    market_vault._schema_ready = False
    market_vault.ensure_vault_schema()
    market_audit._schema_ready = False
    market_audit.ensure_audit_schema()
    db = get_db()
    for t in ("audit_log", "rate_limits", "vault_bindings", "vault_setup_tokens"):
        try:
            db.execute(f"DELETE FROM {t}")
        except Exception:
            pass
    db.execute("DELETE FROM app_users")
    db.commit()
    db.close()
    db_save_user("vault_tester", hash_password("pw"), "vault-token-001")
    db_set_subscription("vault_tester", "pro")
    yield


def _auth():
    return {"Authorization": "Bearer vault-token-001"}


# ── Auth required ─────────────────────────────────────────────────────────────


def test_vault_setup_requires_auth():
    r = client.post("/billing/vault-setup", json={})
    assert r.status_code in (401, 403)


def test_vault_confirm_requires_auth():
    r = client.post("/billing/vault-confirm", json={"setup_token_id": "x"})
    assert r.status_code in (401, 403)


def test_vault_charge_requires_auth():
    r = client.post("/billing/vault-charge", json={"payment_token_id": "x", "amount": 10})
    assert r.status_code in (401, 403)


def test_card_payment_requires_auth():
    r = client.post("/checkout/card-payment", json={"card_token_id": "x", "amount": 10})
    assert r.status_code in (401, 403)


# ── Validation ────────────────────────────────────────────────────────────────


def test_vault_confirm_empty_token():
    r = client.post("/billing/vault-confirm", headers=_auth(), json={"setup_token_id": ""})
    assert r.status_code == 400
    assert "setup_token_id required" in r.json()["detail"]


def test_vault_charge_missing_token():
    r = client.post("/billing/vault-charge", headers=_auth(), json={"amount": 10})
    assert r.status_code == 400


def test_vault_charge_zero_amount():
    r = client.post(
        "/billing/vault-charge",
        headers=_auth(),
        json={"payment_token_id": "tok_123", "amount": 0},
    )
    assert r.status_code == 400
    assert "amount" in r.json()["detail"]


def test_card_payment_missing_token():
    r = client.post("/checkout/card-payment", headers=_auth(), json={"amount": 10})
    assert r.status_code == 400
    assert "card_token_id required" in r.json()["detail"]


def test_card_payment_zero_amount():
    r = client.post(
        "/checkout/card-payment",
        headers=_auth(),
        json={"card_token_id": "ct_abc", "amount": -1},
    )
    assert r.status_code == 400


def test_vault_tokens_requires_customer_id():
    r = client.get("/billing/vault-tokens", headers=_auth())
    assert r.status_code == 400
    assert "customer_id" in r.json()["detail"]


def test_save_card_missing_card_token():
    r = client.post("/checkout/save-card", headers=_auth(), json={"customer_id": "cust_1"})
    assert r.status_code == 400
    assert "card_token_id required" in r.json()["detail"]


def test_save_card_no_customer_id_requires_email_on_file():
    # customer_id is now optional (server can mint one) — but that path
    # needs an email on file, which this test's user doesn't have.
    r = client.post("/checkout/save-card", headers=_auth(), json={"card_token_id": "ct_abc"})
    assert r.status_code == 400
    assert "email" in r.json()["detail"]


# ── Happy paths with mocked connectors ────────────────────────────────────────


def test_vault_setup_success():
    # customer_id omitted — PayPal will mint a fresh one, bound at confirm time.
    mock_result = {"setup_token_id": "st_abc", "approve_url": "https://paypal.com/vault/st_abc"}
    with patch(
        "market_connectors.paypal_payments.create_vault_setup_token",
        new=AsyncMock(return_value=mock_result),
        create=True,
    ):
        r = client.post("/billing/vault-setup", headers=_auth(), json={})
    assert r.status_code == 200
    assert r.json()["setup_token_id"] == "st_abc"


def test_vault_setup_reuses_own_customer_id():
    bind_vault_customer("vault_tester", "c1")
    mock_result = {"setup_token_id": "st_abc", "approve_url": "https://paypal.com/vault/st_abc"}
    with patch(
        "market_connectors.paypal_payments.create_vault_setup_token",
        new=AsyncMock(return_value=mock_result),
        create=True,
    ):
        r = client.post("/billing/vault-setup", headers=_auth(), json={"customer_id": "c1"})
    assert r.status_code == 200


def test_vault_confirm_success():
    market_vault.bind_vault_setup_token("vault_tester", "st_abc")
    mock_result = {"payment_token_id": "pt_xyz", "customer_id": "c1"}
    with patch(
        "market_connectors.paypal_payments.create_vault_payment_token",
        new=AsyncMock(return_value=mock_result),
        create=True,
    ):
        r = client.post(
            "/billing/vault-confirm",
            headers=_auth(),
            json={"setup_token_id": "st_abc"},
        )
    assert r.status_code == 200
    assert r.json()["payment_token_id"] == "pt_xyz"


def test_vault_charge_success():
    bind_vault_payment_token("vault_tester", "c1", "pt_xyz")
    mock_result = {"ok": True, "order_id": "ORD-001", "status": "COMPLETED"}
    with patch(
        "market_connectors.paypal_payments.charge_vault_payment_token",
        new=AsyncMock(return_value=mock_result),
        create=True,
    ):
        r = client.post(
            "/billing/vault-charge",
            headers=_auth(),
            json={"payment_token_id": "pt_xyz", "amount": 39.0},
        )
    assert r.status_code == 200
    assert r.json()["order_id"] == "ORD-001"


def test_vault_tokens_list():
    bind_vault_customer("vault_tester", "c1")
    mock_result = {"tokens": [{"id": "pt_1"}, {"id": "pt_2"}]}
    with patch(
        "market_connectors.paypal_payments.list_vault_payment_tokens",
        new=AsyncMock(return_value=mock_result),
        create=True,
    ):
        r = client.get("/billing/vault-tokens?customer_id=c1", headers=_auth())
    assert r.status_code == 200
    assert len(r.json()["tokens"]) == 2


def test_vault_delete_token():
    bind_vault_payment_token("vault_tester", "c1", "pt_xyz")
    mock_result = {"ok": True}
    with patch(
        "market_connectors.paypal_payments.delete_vault_payment_token",
        new=AsyncMock(return_value=mock_result),
        create=True,
    ):
        r = client.delete("/billing/vault-tokens/pt_xyz", headers=_auth())
    assert r.status_code == 200


def test_card_payment_success():
    mock_result = {"payment_id": 12345, "status": "approved", "card_last_four": "4242"}
    with patch(
        "market_connectors.mercadopago_payments.create_card_payment",
        new=AsyncMock(return_value=mock_result),
        create=True,
    ):
        r = client.post(
            "/checkout/card-payment",
            headers=_auth(),
            json={"card_token_id": "ct_tok", "amount": 25.0, "email": "test@test.com"},
        )
    assert r.status_code == 200
    assert r.json()["status"] == "approved"


def test_save_card_success():
    # Caller already owns cust_1 from a prior save — reused as-is.
    bind_vault_customer("vault_tester", "cust_1")
    mock_result = {"card_id": "card_99", "last_four": "1234"}
    with patch(
        "market_connectors.mercadopago_payments.save_card_for_customer",
        new=AsyncMock(return_value=mock_result),
        create=True,
    ):
        r = client.post(
            "/checkout/save-card",
            headers=_auth(),
            json={"card_token_id": "ct_tok", "customer_id": "cust_1"},
        )
    assert r.status_code == 200
    assert r.json()["card_id"] == "card_99"


def test_save_card_first_use_mints_server_side_customer():
    """No prior binding + no valid customer_id from the client -> server creates one."""
    from market_core import db_create_subscription_request

    db_create_subscription_request("vault_tester", "vault_tester@example.com", "")
    mock_save = {"card_id": "card_99", "last_four": "1234"}
    mock_create = {"customer_id": "mp_cust_fresh"}
    with (
        patch(
            "market_connectors.mercadopago_payments.create_customer",
            new=AsyncMock(return_value=mock_create),
            create=True,
        ) as mock_create_fn,
        patch(
            "market_connectors.mercadopago_payments.save_card_for_customer",
            new=AsyncMock(return_value=mock_save),
            create=True,
        ) as mock_save_fn,
    ):
        r = client.post(
            "/checkout/save-card",
            headers=_auth(),
            # Client-supplied id is unowned/attacker-adjacent — must be ignored.
            json={"card_token_id": "ct_tok", "customer_id": "someone_elses_id"},
        )
    assert r.status_code == 200
    mock_create_fn.assert_called_once()
    mock_save_fn.assert_called_once_with("ct_tok", "mp_cust_fresh")
    assert market_vault.vault_customer_owned("vault_tester", "mp_cust_fresh")


def test_saved_cards_list():
    bind_vault_customer("vault_tester", "cust_1")
    mock_result = {"cards": [{"id": "card_99", "last_four": "1234"}]}
    with patch(
        "market_connectors.mercadopago_payments.list_customer_cards",
        new=AsyncMock(return_value=mock_result),
        create=True,
    ):
        r = client.get("/checkout/saved-cards/cust_1", headers=_auth())
    assert r.status_code == 200
    assert len(r.json()["cards"]) == 1


def test_save_card_rejects_foreign_customer():
    bind_vault_customer("other_user", "victim_cid")
    mock_result = {"card_id": "card_99", "last_four": "1234"}
    with patch(
        "market_connectors.mercadopago_payments.save_card_for_customer",
        new=AsyncMock(return_value=mock_result),
        create=True,
    ):
        r = client.post(
            "/checkout/save-card",
            headers=_auth(),
            json={"card_token_id": "ct_tok", "customer_id": "victim_cid"},
        )
    assert r.status_code == 403
    assert "not owned" in r.json()["detail"]


def test_vault_setup_rejects_foreign_customer():
    bind_vault_customer("other_user", "victim_cid")
    mock_result = {"setup_token_id": "st_abc", "approve_url": "https://paypal.com/vault/st_abc"}
    with patch(
        "market_connectors.paypal_payments.create_vault_setup_token",
        new=AsyncMock(return_value=mock_result),
        create=True,
    ) as mock_setup:
        r = client.post(
            "/billing/vault-setup",
            headers=_auth(),
            json={"customer_id": "victim_cid"},
        )
    assert r.status_code == 403
    assert "not owned" in r.json()["detail"]
    mock_setup.assert_not_called()


def test_vault_confirm_rejects_foreign_customer():
    market_vault.bind_vault_setup_token("vault_tester", "st_abc")
    bind_vault_customer("other_user", "victim_cid")
    mock_result = {"payment_token_id": "pt_xyz", "customer_id": "victim_cid"}
    with patch(
        "market_connectors.paypal_payments.create_vault_payment_token",
        new=AsyncMock(return_value=mock_result),
        create=True,
    ) as mock_confirm:
        r = client.post(
            "/billing/vault-confirm",
            headers=_auth(),
            json={"setup_token_id": "st_abc"},
        )
    assert r.status_code == 403
    assert "not owned" in r.json()["detail"]
    mock_confirm.assert_called_once()


def test_saved_cards_rejects_foreign_customer():
    bind_vault_customer("other_user", "victim_cid")
    mock_result = {"cards": [{"id": "card_99", "last_four": "1234"}]}
    with patch(
        "market_connectors.mercadopago_payments.list_customer_cards",
        new=AsyncMock(return_value=mock_result),
        create=True,
    ):
        r = client.get("/checkout/saved-cards/victim_cid", headers=_auth())
    assert r.status_code == 403
    assert "not owned" in r.json()["detail"]


def test_vault_charge_rejects_foreign_token():
    bind_vault_payment_token("other_user", "c2", "pt_victim")
    mock_result = {"ok": True, "order_id": "ORD-EVIL"}
    with patch(
        "market_connectors.paypal_payments.charge_vault_payment_token",
        new=AsyncMock(return_value=mock_result),
        create=True,
    ):
        r = client.post(
            "/billing/vault-charge",
            headers=_auth(),
            json={"payment_token_id": "pt_victim", "amount": 99.0},
        )
    assert r.status_code == 403
    assert "not owned" in r.json()["detail"]


def test_vault_tokens_rejects_foreign_customer():
    bind_vault_customer("other_user", "victim_cid")
    mock_result = {"tokens": [{"id": "pt_1"}]}
    with patch(
        "market_connectors.paypal_payments.list_vault_payment_tokens",
        new=AsyncMock(return_value=mock_result),
        create=True,
    ):
        r = client.get("/billing/vault-tokens?customer_id=victim_cid", headers=_auth())
    assert r.status_code == 403
    assert "not owned" in r.json()["detail"]


def test_vault_delete_rejects_foreign_token():
    bind_vault_payment_token("other_user", "c2", "pt_victim")
    mock_result = {"ok": True}
    with patch(
        "market_connectors.paypal_payments.delete_vault_payment_token",
        new=AsyncMock(return_value=mock_result),
        create=True,
    ):
        r = client.delete("/billing/vault-tokens/pt_victim", headers=_auth())
    assert r.status_code == 403
    assert "not owned" in r.json()["detail"]


def test_backfill_vault_bindings_from_save_card_audit():
    import market_audit
    from market_vault import backfill_vault_bindings_from_audit, vault_customer_owned

    market_audit.record_audit(
        "save_card",
        username="vault_tester",
        detail={"customer_id": "legacy_mp_cust", "last_four": "4242"},
    )
    stats = backfill_vault_bindings_from_audit()
    assert stats["customers_bound"] >= 1
    assert vault_customer_owned("vault_tester", "legacy_mp_cust")


def test_backfill_vault_bindings_from_vault_confirm_audit():
    import market_audit
    from market_vault import backfill_vault_bindings_from_audit, vault_payment_token_owned

    market_audit.record_audit(
        "vault_confirm",
        username="vault_tester",
        detail={"payment_token": "pt_legacy", "customer_id": "legacy_pp_cust"},
    )
    stats = backfill_vault_bindings_from_audit()
    assert stats["tokens_bound"] >= 1
    assert vault_payment_token_owned("vault_tester", "pt_legacy")


def test_backfill_vault_bindings_skips_customer_conflict():
    import market_audit
    from market_vault import backfill_vault_bindings_from_audit, bind_vault_customer

    bind_vault_customer("other_user", "contested_cid")
    market_audit.record_audit(
        "save_card",
        username="vault_tester",
        detail={"customer_id": "contested_cid", "last_four": "1111"},
    )
    stats = backfill_vault_bindings_from_audit()
    assert stats["customers_skipped"] >= 1


# ── Approve-link phishing fix (setup_token ownership + single-use) ─────────────


def test_vault_confirm_rejects_setup_token_from_another_user():
    """Core phishing regression: attacker cannot confirm a token they didn't create."""
    market_vault.bind_vault_setup_token("victim_user", "st_stolen")
    mock_result = {"payment_token_id": "pt_stolen", "customer_id": "victim_paypal_cust"}
    with patch(
        "market_connectors.paypal_payments.create_vault_payment_token",
        new=AsyncMock(return_value=mock_result),
        create=True,
    ) as mock_confirm:
        r = client.post(
            "/billing/vault-confirm",
            headers=_auth(),  # calling as vault_tester, not victim_user
            json={"setup_token_id": "st_stolen"},
        )
    assert r.status_code == 403
    assert "not owned" in r.json()["detail"]
    mock_confirm.assert_not_called()


def test_vault_confirm_rejects_unknown_setup_token():
    r = client.post(
        "/billing/vault-confirm",
        headers=_auth(),
        json={"setup_token_id": "st_never_created"},
    )
    assert r.status_code == 403


def test_vault_confirm_is_single_use():
    market_vault.bind_vault_setup_token("vault_tester", "st_once")
    mock_result = {"payment_token_id": "pt_1", "customer_id": "c1"}
    with patch(
        "market_connectors.paypal_payments.create_vault_payment_token",
        new=AsyncMock(return_value=mock_result),
        create=True,
    ):
        first = client.post(
            "/billing/vault-confirm", headers=_auth(), json={"setup_token_id": "st_once"}
        )
        second = client.post(
            "/billing/vault-confirm", headers=_auth(), json={"setup_token_id": "st_once"}
        )
    assert first.status_code == 200
    assert second.status_code == 403
    assert "already used" in second.json()["detail"]


def test_vault_setup_rejects_unowned_customer_id_preemption():
    """No one owns 'unclaimed_cid' yet — vault-setup must not let a client
    preemptively claim it; only a provider-confirmed vault-confirm may bind it."""
    mock_result = {"setup_token_id": "st_x", "approve_url": "https://paypal.com/vault/st_x"}
    with patch(
        "market_connectors.paypal_payments.create_vault_setup_token",
        new=AsyncMock(return_value=mock_result),
        create=True,
    ) as mock_setup:
        r = client.post(
            "/billing/vault-setup",
            headers=_auth(),
            json={"customer_id": "unclaimed_cid"},
        )
    assert r.status_code == 403
    mock_setup.assert_not_called()
    assert not market_vault.vault_customer_owned("vault_tester", "unclaimed_cid")


# ── Error propagation ─────────────────────────────────────────────────────────


def test_vault_setup_connector_error():
    mock_result = {"error": "PayPal timeout", "status": 504}
    with patch(
        "market_connectors.paypal_payments.create_vault_setup_token",
        new=AsyncMock(return_value=mock_result),
        create=True,
    ):
        r = client.post("/billing/vault-setup", headers=_auth(), json={})
    assert r.status_code == 504


def test_vault_charge_connector_error():
    bind_vault_payment_token("vault_tester", "c1", "pt_x")
    mock_result = {"ok": False, "error": "Insufficient funds", "status": 422}
    with patch(
        "market_connectors.paypal_payments.charge_vault_payment_token",
        new=AsyncMock(return_value=mock_result),
        create=True,
    ):
        r = client.post(
            "/billing/vault-charge",
            headers=_auth(),
            json={"payment_token_id": "pt_x", "amount": 100},
        )
    assert r.status_code == 422


def test_card_payment_connector_error():
    mock_result = {"error": "Card declined", "status": 400}
    with patch(
        "market_connectors.mercadopago_payments.create_card_payment",
        new=AsyncMock(return_value=mock_result),
        create=True,
    ):
        r = client.post(
            "/checkout/card-payment",
            headers=_auth(),
            json={"card_token_id": "ct_bad", "amount": 10},
        )
    assert r.status_code == 400
