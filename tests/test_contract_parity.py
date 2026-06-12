"""P1-E contract parity — pins and OpenAPI diff helpers."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(REPO_ROOT / "ops"))

from contract_parity import (  # noqa: E402
    CHECKOUT_PREFIX,
    PARITY_EXACT,
    check_core_pins,
    compare_openapi,
    default_backend_path,
    openapi_spec_from_app,
    parse_core_pin,
)

BACKEND_ROOT = default_backend_path()


def test_core_pin_world_matches_backend():
    errors = check_core_pins()
    if not (REPO_ROOT.parent / "cli-market-backend" / "requirements.txt").is_file():
        pytest.skip("cli-market-backend not checked out locally")
    assert errors == []


def test_parse_core_pin_from_pyproject():
    text = (REPO_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert parse_core_pin(text, label="test") >= (1, 9, 0)


def test_compare_openapi_identical_specs():
    paths = {p: {m: {}} for p, methods in PARITY_EXACT.items() for m in methods}
    paths["/checkout/yape"] = {"post": {}}
    paths["/checkout/webhook"] = {"post": {}}
    spec = {"paths": paths}
    assert compare_openapi(spec, spec) == []


def test_compare_openapi_detects_missing_path():
    full = {"paths": {p: {m: {}} for p, methods in PARITY_EXACT.items() for m in methods}}
    full["paths"]["/checkout/yape"] = {"post": {}}
    partial = {"paths": dict(full["paths"])}
    del partial["paths"]["/products/search"]
    errors = compare_openapi(partial, full)
    assert any("world missing path /products/search" in e for e in errors)


@pytest.mark.skipif(BACKEND_ROOT is None, reason="cli-market-backend not available")
def test_world_backend_openapi_parity_live():
    os_env = __import__("os").environ
    os_env.setdefault("MARKET_SKIP_LIVE", "1")
    os_env.setdefault("DATABASE_URL", "")

    from contract_parity import _load_app

    world_app = _load_app(REPO_ROOT)
    world_spec = openapi_spec_from_app(world_app)

    saved = {k: sys.modules.pop(k) for k in list(sys.modules) if k.startswith(("routers", "server_deps", "market_server"))}
    try:
        backend_app = _load_app(BACKEND_ROOT)
        backend_spec = openapi_spec_from_app(backend_app)
    finally:
        sys.modules.update(saved)

    errors = compare_openapi(world_spec, backend_spec)
    assert errors == [], "\n".join(errors)


def test_checkout_prefix_constant():
    assert CHECKOUT_PREFIX == "/checkout/"
