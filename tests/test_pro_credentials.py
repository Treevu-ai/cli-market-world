"""Pro activation provisions login credentials for the welcome email."""

import sys
import uuid
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from account_service import provision_pro_login_credentials
from market_core import db_get_users, db_save_user
from server_deps import hash_password, verify_password


@pytest.fixture(autouse=True)
def _clean_user():
    from market_core import get_db, ensure_db_initialized

    ensure_db_initialized()
    db = get_db()
    db.execute("DELETE FROM app_users WHERE username='pro-cred-test'")
    db.commit()
    db.close()
    yield
    ensure_db_initialized()
    db = get_db()
    db.execute("DELETE FROM app_users WHERE username='pro-cred-test'")
    db.commit()
    db.close()


def test_provision_creates_login_password():
    password = provision_pro_login_credentials("pro-cred-test")
    assert password
    users = db_get_users()
    assert "pro-cred-test" in users
    assert verify_password(password, users["pro-cred-test"]["password"])


def test_provision_rotates_password_keeps_token():
    token = str(uuid.uuid4())
    db_save_user("pro-cred-test", hash_password("old-pass"), token)
    new_password = provision_pro_login_credentials("pro-cred-test")
    users = db_get_users()
    assert verify_password(new_password, users["pro-cred-test"]["password"])
    assert users["pro-cred-test"]["token"] == token