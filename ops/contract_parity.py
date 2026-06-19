#!/usr/bin/env python3
"""P1-E — OpenAPI parity (world vs backend) and cli-market-core pin alignment.

Compares mirrored API surfaces without running servers by loading FastAPI apps
and diffing OpenAPI path/method sets.

Usage:
    python ops/contract_parity.py
    python ops/contract_parity.py --backend-path ../cli-market-backend
    python ops/contract_parity.py --pins-only
"""

from __future__ import annotations

import argparse
import importlib
import os
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent

# Paths that must stay in lockstep between world mirror and production backend.
PARITY_EXACT: dict[str, set[str]] = {
    "/products/search": {"post"},
    "/products/compare": {"post"},
    "/analytics/observatory": {"get"},
    "/v1/capabilities": {"get"},
    "/v1/sources/health": {"get"},
    "/health/stats": {"get"},
    "/v1/retailers/apply": {"post"},
    # Semantic index (Golden Records) — world mirror ↔ backend prod
    "/index/resolve": {"post"},
    "/resolve": {"get"},
    "/index/lookup/{product_id}": {"get"},
    "/index/stats": {"get"},
    "/index/backfill": {"post"},
}

CHECKOUT_PREFIX = "/checkout/"

_CORE_PIN_RE = re.compile(
    r"cli-market-core\s*>=\s*(\d+)\.(\d+)\.(\d+)",
    re.IGNORECASE,
)
_CORE_URL_RE = re.compile(
    r"cli-market-core\s*@\s*https://[^\s]*cli_market_core-(\d+)\.(\d+)\.(\d+)-",
    re.IGNORECASE,
)
_CORE_GIT_RE = re.compile(
    r"cli-market-core\s*@\s*git\+https://[^\s]*",
    re.IGNORECASE,
)
_CORE_PIN_EQ_RE = re.compile(
    r"cli-market-core\s*==\s*(\d+)\.(\d+)\.(\d+)",
    re.IGNORECASE,
)
_INDEX_PIN_RE = re.compile(
    r"cli-market-index\[postgres\]\s*@\s*git\+https://github\.com/Treevu-ai/cli-market-index@([0-9a-f]{40})",
    re.IGNORECASE,
)


def _methods_for_path(spec: dict[str, Any], path: str) -> set[str]:
    entry = (spec.get("paths") or {}).get(path) or {}
    return {m.lower() for m in entry if m.lower() in {"get", "post", "put", "patch", "delete", "head", "options"}}


def _checkout_paths(spec: dict[str, Any]) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for path in spec.get("paths") or {}:
        if path.startswith(CHECKOUT_PREFIX):
            out[path] = _methods_for_path(spec, path)
    return out


def openapi_spec_from_app(app: Any) -> dict[str, Any]:
    return app.openapi()


def _load_app(repo_root: Path):
    repo_root = repo_root.resolve()
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    os.environ.setdefault("MARKET_SKIP_LIVE", "1")
    os.environ.setdefault("DATABASE_URL", "")
    os.environ.setdefault("MARKET_DATA_DIR", str(repo_root / ".contract-parity-data"))
    try:
        import market_server  # noqa: WPS433 — dynamic import after sys.path
    except ModuleNotFoundError:
        return None

    importlib.reload(market_server)
    return market_server.app


def compare_openapi(world_spec: dict[str, Any], backend_spec: dict[str, Any]) -> list[str]:
    """Return human-readable diff lines; empty list means parity OK."""
    errors: list[str] = []

    for path, methods in PARITY_EXACT.items():
        w = _methods_for_path(world_spec, path)
        b = _methods_for_path(backend_spec, path)
        if not w:
            errors.append(f"world missing path {path} (expected {sorted(methods)})")
        if not b:
            errors.append(f"backend missing path {path} (expected {sorted(methods)})")
        if w != methods:
            errors.append(f"world {path}: methods {sorted(w)} != expected {sorted(methods)}")
        if b != methods:
            errors.append(f"backend {path}: methods {sorted(b)} != expected {sorted(methods)}")
        if w and b and w != b:
            errors.append(f"method mismatch on {path}: world={sorted(w)} backend={sorted(b)}")

    w_checkout = _checkout_paths(world_spec)
    b_checkout = _checkout_paths(backend_spec)
    only_world = sorted(set(w_checkout) - set(b_checkout))
    only_backend = sorted(set(b_checkout) - set(w_checkout))
    if only_world:
        errors.append(f"checkout paths only on world: {only_world}")
    if only_backend:
        errors.append(f"checkout paths only on backend: {only_backend}")
    for path in sorted(set(w_checkout) & set(b_checkout)):
        if w_checkout[path] != b_checkout[path]:
            errors.append(
                f"checkout method mismatch {path}: world={sorted(w_checkout[path])} "
                f"backend={sorted(b_checkout[path])}"
            )

    return errors


def parse_core_pin(text: str, *, label: str) -> tuple[int, int, int]:
    match = _CORE_PIN_RE.search(text)
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    match = _CORE_URL_RE.search(text)
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    match = _CORE_PIN_EQ_RE.search(text)
    if match:
        return int(match.group(1)), int(match.group(2)), int(match.group(3))
    match = _CORE_GIT_RE.search(text)
    if match:
        return 1, 10, 0  # TODO: remove when 1.10.0 is on PyPI
    raise SystemExit(f"{label}: no cli-market-core>=X.Y.Z pin or @ URL found")


def parse_core_pin_eq(text: str, *, label: str) -> tuple[int, int, int]:
    match = _CORE_PIN_EQ_RE.search(text)
    if not match:
        raise SystemExit(f"{label}: no cli-market-core==X.Y.Z pin found")
    return int(match.group(1)), int(match.group(2)), int(match.group(3))


def check_core_pins(
    world_pyproject: Path | None = None,
    world_railway_req: Path | None = None,
    backend_requirements: Path | None = None,
) -> list[str]:
    world_pyproject = world_pyproject or ROOT / "pyproject.toml"
    world_railway_req = world_railway_req or ROOT / "requirements-railway.txt"
    backend_requirements = backend_requirements or ROOT.parent / "cli-market-backend" / "requirements.txt"
    errors: list[str] = []

    if world_railway_req.is_file():
        w_pin = parse_core_pin_eq(
            world_railway_req.read_text(encoding="utf-8"),
            label="world requirements-railway.txt",
        )
    elif world_pyproject.is_file():
        w_pin = parse_core_pin(world_pyproject.read_text(encoding="utf-8"), label="world pyproject.toml")
    else:
        return [f"world core pin missing: {world_railway_req} or {world_pyproject}"]

    if not backend_requirements.is_file():
        return [f"backend requirements missing: {backend_requirements}"]

    b_pin = parse_core_pin(backend_requirements.read_text(encoding="utf-8"), label="backend requirements.txt")

    if b_pin == (1, 10, 0):
        pass  # backend uses git pin until 1.10.0 is on PyPI
    elif w_pin[:2] != b_pin[:2]:
        errors.append(
            f"cli-market-core minor mismatch: world={'.'.join(map(str, w_pin))} "
            f"backend={'.'.join(map(str, b_pin))} (major.minor must match)"
        )
    elif w_pin != b_pin:
        if w_pin < b_pin:
            errors.append(
                f"cli-market-core patch mismatch: world={'.'.join(map(str, w_pin))} "
                f"backend={'.'.join(map(str, b_pin))} (world behind backend)"
            )
        else:
            print(
                f"WARN: world patch ahead of backend pin: world={'.'.join(map(str, w_pin))} "
                f"backend={'.'.join(map(str, b_pin))} — update cli-market-backend requirements.txt",
                file=sys.stderr,
            )

    return errors


def parse_index_pin(text: str, *, label: str) -> str:
    match = _INDEX_PIN_RE.search(text)
    if not match:
        raise SystemExit(f"{label}: no cli-market-index git pin found")
    return match.group(1).lower()


def check_index_pins(
    world_railway_req: Path | None = None,
    backend_private_req: Path | None = None,
) -> list[str]:
    world_railway_req = world_railway_req or ROOT / "requirements-railway.txt"
    backend_private_req = backend_private_req or ROOT.parent / "cli-market-backend" / "requirements-private.txt"
    errors: list[str] = []

    if not world_railway_req.is_file():
        return [f"world requirements-railway missing: {world_railway_req}"]
    if not backend_private_req.is_file():
        return [f"backend requirements-private missing: {backend_private_req}"]

    w_pin = parse_index_pin(world_railway_req.read_text(encoding="utf-8"), label="world requirements-railway.txt")
    b_pin = parse_index_pin(backend_private_req.read_text(encoding="utf-8"), label="backend requirements-private.txt")

    if w_pin != b_pin:
        errors.append(f"cli-market-index pin mismatch: world={w_pin[:12]}… backend={b_pin[:12]}…")

    return errors


def default_backend_path() -> Path | None:
    for candidate in (
        ROOT / ".deps" / "cli-market-backend",
        ROOT.parent / "cli-market-backend",
    ):
        if (candidate / "market_server.py").is_file():
            return candidate
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="World/backend API contract parity")
    parser.add_argument("--backend-path", type=Path, default=None, help="cli-market-backend checkout")
    parser.add_argument("--pins-only", action="store_true", help="Only verify cli-market-core pins")
    parser.add_argument("--skip-openapi", action="store_true", help="Only verify pins")
    args = parser.parse_args(argv)

    backend_path = args.backend_path or default_backend_path()
    backend_req = (backend_path / "requirements.txt") if backend_path else None
    backend_private_req = (backend_path / "requirements-private.txt") if backend_path else None
    pin_errors = check_core_pins(backend_requirements=backend_req)
    index_pin_errors = check_index_pins(backend_private_req=backend_private_req)
    pin_errors = pin_errors + index_pin_errors
    if pin_errors:
        for line in pin_errors:
            print(f"PIN FAIL: {line}", file=sys.stderr)
        if args.pins_only or args.skip_openapi:
            return 1

    if args.pins_only:
        print("OK: cli-market-core and cli-market-index pins aligned")
        return 0

    if backend_path is None:
        print("SKIP: backend repo not found — OpenAPI parity not checked", file=sys.stderr)
        return 1 if pin_errors else 0

    world_app = _load_app(ROOT)
    world_spec = openapi_spec_from_app(world_app)

    # Isolate backend import from world modules on sys.path.
    saved_path = sys.path.copy()
    saved_modules = {k: sys.modules.pop(k) for k in list(sys.modules) if k.startswith(("routers", "server_deps", "market_server"))}
    try:
        backend_app = _load_app(backend_path)
        if backend_app is None:
            print("::warning::Cannot import backend market_server (core version mismatch) — OpenAPI parity skipped")
            return 1 if pin_errors else 0
        backend_spec = openapi_spec_from_app(backend_app)
    finally:
        sys.path[:] = saved_path
        sys.modules.update(saved_modules)

    errors = compare_openapi(world_spec, backend_spec)
    if pin_errors:
        errors = pin_errors + errors

    if errors:
        print("CONTRACT PARITY FAIL:", file=sys.stderr)
        for line in errors:
            print(f"  - {line}", file=sys.stderr)
        return 1

    # T-177 — Observatory mirror (semantic; world may lead backend on new routes)
    ops_dir = Path(__file__).resolve().parent
    if str(ops_dir) not in sys.path:
        sys.path.insert(0, str(ops_dir))
    from mirror_diff_gate import compare_mirror

    mirror_errors = compare_mirror(ROOT, backend_path)
    if mirror_errors:
        print("MIRROR DIFF FAIL:", file=sys.stderr)
        for line in mirror_errors:
            print(f"  - {line}", file=sys.stderr)
        return 1

    print(
        f"OK: OpenAPI parity ({len(PARITY_EXACT)} exact paths incl. index + "
        f"{len(_checkout_paths(world_spec))} checkout paths) · core/index pins aligned · "
        "Observatory mirror OK"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
