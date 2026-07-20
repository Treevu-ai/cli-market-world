"""Taller registration endpoint — insert, validation, and email dispatch."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi import HTTPException


def _valid_body(**overrides):
    body = {
        "nombre": "Ana Torres",
        "email": "ana@example.com",
        "telefono": "987654321",
        "pago": "Yape",
        "comentario": "Tienda de abarrotes",
    }
    body.update(overrides)
    return body


def test_registro_rejects_missing_nombre(isolated_db):
    isolated_db.ensure_db_initialized()
    import routers.taller as taller_module

    with pytest.raises(HTTPException) as exc:
        taller_module.registro_taller(_valid_body(nombre=""))
    assert exc.value.status_code == 400


def test_registro_rejects_invalid_email(isolated_db):
    isolated_db.ensure_db_initialized()
    import routers.taller as taller_module

    with pytest.raises(HTTPException) as exc:
        taller_module.registro_taller(_valid_body(email="not-an-email"))
    assert exc.value.status_code == 400


def test_registro_rejects_invalid_pago(isolated_db):
    isolated_db.ensure_db_initialized()
    import routers.taller as taller_module

    with pytest.raises(HTTPException) as exc:
        taller_module.registro_taller(_valid_body(pago="Bitcoin"))
    assert exc.value.status_code == 400


def test_registro_inserts_row_and_sends_emails(isolated_db):
    isolated_db.ensure_db_initialized()
    import routers.taller as taller_module

    with patch.object(taller_module, "_send_confirmation_email", return_value={"sent": True}) as ack, \
         patch.object(taller_module, "_send_ops_notification", return_value={"sent": True}) as notify:
        result = taller_module.registro_taller(_valid_body())

    assert result["registered"] is True
    assert result["email_sent"] is True
    assert result["ops_notified"] is True
    ack.assert_called_once()
    notify.assert_called_once()

    db = isolated_db.get_db()
    row = db.execute(
        "SELECT nombre, email, telefono, pago FROM taller_registrations WHERE id = ?",
        (result["id"],),
    ).fetchone()
    db.close()
    row = dict(row)
    assert row["nombre"] == "Ana Torres"
    assert row["email"] == "ana@example.com"
    assert row["pago"] == "Yape"


def test_payment_instructions_yape_vs_transferencia():
    from routers.taller import BCP_ACCOUNT_NUMBER, YAPE_PLIN_NUMBER, _payment_instructions

    yape_text = _payment_instructions("Yape")
    bank_text = _payment_instructions("Transferencia bancaria")
    assert YAPE_PLIN_NUMBER in yape_text
    assert BCP_ACCOUNT_NUMBER in bank_text
