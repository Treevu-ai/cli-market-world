"""Academy waitlist endpoint — insert, validation, and ops notification."""

from __future__ import annotations

from unittest.mock import patch

import pytest
from fastapi import HTTPException


def _valid_body(**overrides):
    body = {
        "email": "ana@example.com",
        "rol": "Comercial / Ventas",
        "track": "Intelligence",
        "pais": "PE",
        "empresa": "Acme SAC",
    }
    body.update(overrides)
    return body


def test_waitlist_rejects_invalid_email(isolated_db):
    isolated_db.ensure_db_initialized()
    import routers.academy as academy_module

    with pytest.raises(HTTPException) as exc:
        academy_module.academy_waitlist(_valid_body(email="not-an-email"))
    assert exc.value.status_code == 400


def test_waitlist_rejects_missing_rol(isolated_db):
    isolated_db.ensure_db_initialized()
    import routers.academy as academy_module

    with pytest.raises(HTTPException) as exc:
        academy_module.academy_waitlist(_valid_body(rol=""))
    assert exc.value.status_code == 400


def test_waitlist_rejects_invalid_track(isolated_db):
    isolated_db.ensure_db_initialized()
    import routers.academy as academy_module

    with pytest.raises(HTTPException) as exc:
        academy_module.academy_waitlist(_valid_body(track="Bitcoin"))
    assert exc.value.status_code == 400


def test_waitlist_rejects_missing_pais(isolated_db):
    isolated_db.ensure_db_initialized()
    import routers.academy as academy_module

    with pytest.raises(HTTPException) as exc:
        academy_module.academy_waitlist(_valid_body(pais=""))
    assert exc.value.status_code == 400


def test_waitlist_inserts_row_and_notifies_ops(isolated_db):
    isolated_db.ensure_db_initialized()
    import routers.academy as academy_module

    with patch.object(academy_module, "_send_ops_notification", return_value={"sent": True}) as notify:
        result = academy_module.academy_waitlist(_valid_body())

    assert result["registered"] is True
    assert result["ops_notified"] is True
    notify.assert_called_once()

    db = isolated_db.get_db()
    row = db.execute(
        "SELECT email, rol, track, pais, empresa FROM academy_waitlist WHERE id = ?",
        (result["id"],),
    ).fetchone()
    db.close()
    row = dict(row)
    assert row["email"] == "ana@example.com"
    assert row["track"] == "Intelligence"
    assert row["pais"] == "PE"
