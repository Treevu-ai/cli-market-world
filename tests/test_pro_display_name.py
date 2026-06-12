"""Display name resolution for Pro welcome emails."""

import subprocess
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from account_service import build_pro_email_context, resolve_pro_display_name
from market_core import db_create_subscription_request, db_find_subscription_request


def test_compose_subject_uses_display_name():
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "cli-market-core"))
    from market_connectors.email_outbound import compose_pro_welcome_email

    composed = compose_pro_welcome_email(
        display_name="Antonio Cuba",
        username="acubatruweb",
        email="acubatruweb@outlook.com",
        password="secret",
        lang="es",
        payment_method="yape",
        request_id="PRO-3E2A9E04",
    )
    assert composed["subject"] == "Antonio Cuba, tu CLI Market Pro ya está listo"
    assert "Hola Antonio Cuba" in composed["text"]
    assert "Usuario CLI · acubatruweb" in composed["text"]


def test_resolve_from_explicit_name():
    assert resolve_pro_display_name(
        username="acubatruweb",
        email="acubatruweb@outlook.com",
        display_name="Ricardo",
    ) == "Ricardo"


def test_resolve_from_human_username():
    assert resolve_pro_display_name(
        username="acubatruweb",
        email="acubatruweb@outlook.com",
    ) == "Acubatruweb"


def test_resolve_from_auto_user_handle():
    assert resolve_pro_display_name(
        username="user-87db316c7763",
        email="smoke@test.com",
    ) == "Smoke"


def test_build_context_links_email_username_password():
    ctx = build_pro_email_context(
        "acubatruweb",
        email="acubatruweb@outlook.com",
        password="pass-123",
        display_name="Ricardo",
    )
    assert ctx["display_name"] == "Ricardo"
    assert ctx["email"] == "acubatruweb@outlook.com"
    assert ctx["username"] == "acubatruweb"
    assert ctx["password"] == "pass-123"


def test_activate_pro_persists_display_name_override():
    from market_core import ensure_db_initialized

    from conftest import activate_pro_subprocess_env

    ensure_db_initialized()
    req = db_create_subscription_request("dn-ops-user", "dn-ops@test.com", "yape:manual")
    proc = subprocess.run(
        [
            sys.executable,
            "ops/activate_pro.py",
            "dn-ops-user",
            "--request-id",
            req["id"],
            "--display-name",
            "Antonio Cuba",
        ],
        cwd=str(Path(__file__).parent.parent),
        capture_output=True,
        text=True,
        env=activate_pro_subprocess_env(),
    )
    assert proc.returncode == 0, proc.stderr + proc.stdout
    updated = db_find_subscription_request(request_id=req["id"])
    assert updated["display_name"] == "Antonio Cuba"
    assert "Display name saved" in proc.stdout