"""T-177 — mirror diff gate unit tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "ops"))

from mirror_diff_gate import (  # noqa: E402
    compare_exact_files,
    compare_market_server_observatory,
    compare_mirror,
    compare_server_deps_observatory,
    default_backend_path,
    extract_market_server_observatory_fingerprint,
    normalize_text,
)

BACKEND_ROOT = default_backend_path()

SHIM = '''"""Shim."""
from market_core.market_observatory import *  # noqa: F403,F401
'''

ROUTER = '''"""Observatory router."""
from fastapi import APIRouter
router = APIRouter()
@router.get("/analytics/observatory")
def analytics_observatory_public(days: int = 30):
    return {}
'''

SERVER_DEPS = '''DEFAULT_TOKEN = "x"

def auth_user(token: str) -> str:
    return token

def require_user(authorization: str | None) -> str:
    return authorization or ""

def require_admin(authorization: str | None) -> str:
    return require_user(authorization)

def require_api_key(authorization: str | None) -> str:
    return require_user(authorization)
'''

MARKET_SERVER = '''
async def lifespan(_app):
    from market_observatory import ensure_observatory_schema
    ensure_observatory_schema()
    yield

from market_observatory import ObservatoryMiddleware
app.add_middleware(
    ObservatoryMiddleware,
    auth_user_fn=auth_user,
    api_key_fn=db_validate_api_key,
)
app.add_middleware(
    CORSMiddleware,
    allow_headers=["Authorization", "Content-Type", "X-Agent-ID", "X-Session-ID", "X-Country"],
)
from routers.observatory import router as observatory_router
for r in (
    observatory_router,
):
    app.include_router(r)
'''


def _write_tree(root: Path, server_deps: str = SERVER_DEPS, market_server: str = MARKET_SERVER) -> None:
    (root / "market_observatory.py").write_text(SHIM, encoding="utf-8")
    (root / "routers").mkdir(parents=True, exist_ok=True)
    (root / "routers" / "observatory.py").write_text(ROUTER, encoding="utf-8")
    (root / "server_deps.py").write_text(server_deps, encoding="utf-8")
    (root / "market_server.py").write_text(market_server, encoding="utf-8")


def test_normalize_text_strips_trailing_blank_lines():
    assert normalize_text("a\n\n") == "a\n"


def test_compare_exact_files_detects_drift(tmp_path: Path):
    world = tmp_path / "world"
    backend = tmp_path / "backend"
    world.mkdir()
    backend.mkdir()
    (world / "market_observatory.py").write_text(SHIM, encoding="utf-8")
    (backend / "market_observatory.py").write_text("# different\n", encoding="utf-8")
    (world / "routers").mkdir()
    (backend / "routers").mkdir()
    (world / "routers" / "observatory.py").write_text(ROUTER, encoding="utf-8")
    (backend / "routers" / "observatory.py").write_text(ROUTER, encoding="utf-8")
    errors = compare_exact_files(world, backend)
    assert any("market_observatory.py" in e for e in errors)


def test_compare_mirror_ok_on_identical_trees(tmp_path: Path):
    world = tmp_path / "world"
    backend = tmp_path / "backend"
    world.mkdir()
    backend.mkdir()
    _write_tree(world)
    _write_tree(backend)
    assert compare_mirror(world, backend) == []


def test_server_deps_symbol_drift(tmp_path: Path):
    world = tmp_path / "world"
    backend = tmp_path / "backend"
    world.mkdir()
    backend.mkdir()
    _write_tree(world)
    drift_deps = SERVER_DEPS.replace('return token', 'return "other"')
    _write_tree(backend, server_deps=drift_deps)
    errors = compare_server_deps_observatory(world, backend)
    assert any("auth_user" in e for e in errors)


def test_market_server_fingerprint_missing_line():
    with pytest.raises(ValueError, match="missing line"):
        extract_market_server_observatory_fingerprint("app = FastAPI()\n")


def test_market_server_observatory_drift(tmp_path: Path):
    world = tmp_path / "world"
    backend = tmp_path / "backend"
    world.mkdir()
    backend.mkdir()
    _write_tree(world)
    bad = MARKET_SERVER.replace("observatory_router,", "health_router,")
    _write_tree(backend, market_server=bad)
    errors = compare_market_server_observatory(world, backend)
    assert errors


@pytest.mark.skipif(BACKEND_ROOT is None, reason="cli-market-backend not checked out")
def test_world_backend_mirror_live():
    errors = compare_mirror(REPO_ROOT, BACKEND_ROOT)
    assert errors == [], "\n".join(errors)
