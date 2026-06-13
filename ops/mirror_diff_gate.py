#!/usr/bin/env python3
"""T-177 — Mirror diff gate: Observatory + server_deps wiring (world ↔ backend).

Compares canonical mirror paths from docs/prd-observatory-p0.md §0.2 without
requiring a full ``fc`` of large files like ``market_server.py``.

Usage:
    python ops/mirror_diff_gate.py
    python ops/mirror_diff_gate.py --backend-path .deps/cli-market-backend
"""

from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Byte-identical after normalization (Observatory surface).
MIRROR_EXACT: tuple[str, ...] = (
    "market_observatory.py",
    "routers/observatory.py",
)

# Auth helpers consumed by ObservatoryMiddleware + admin observatory routes.
SERVER_DEPS_OBSERVATORY_SYMBOLS: frozenset[str] = frozenset(
    {
        "DEFAULT_TOKEN",
        "auth_user",
        "require_user",
        "require_admin",
        "require_api_key",
    }
)

# Substrings that must appear identically (normalized) in market_server wiring.
MARKET_SERVER_OBSERVATORY_LINES: tuple[str, ...] = (
    "from market_observatory import ensure_observatory_schema",
    "ensure_observatory_schema()",
    "from market_observatory import ObservatoryMiddleware",
    "ObservatoryMiddleware,",
    "auth_user_fn=auth_user,",
    "api_key_fn=db_validate_api_key,",
    'allow_headers=["Authorization", "Content-Type", "X-Agent-ID", "X-Session-ID", "X-Country"]',
    "from routers.observatory import router as observatory_router",
    "observatory_router,",
)


def default_backend_path() -> Path | None:
    for candidate in (
        ROOT / ".deps" / "cli-market-backend",
        ROOT.parent / "cli-market-backend",
    ):
        if (candidate / "market_server.py").is_file():
            return candidate
    return None


def normalize_text(text: str) -> str:
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + ("\n" if lines else "")


def _read_rel(root: Path, rel: str) -> str:
    path = root / rel
    if not path.is_file():
        raise FileNotFoundError(rel)
    return path.read_text(encoding="utf-8")


def compare_exact_files(world_root: Path, backend_root: Path) -> list[str]:
    errors: list[str] = []
    for rel in MIRROR_EXACT:
        w_path = world_root / rel
        b_path = backend_root / rel
        if not w_path.is_file():
            errors.append(f"world missing mirror file {rel}")
            continue
        if not b_path.is_file():
            errors.append(f"backend missing mirror file {rel}")
            continue
        w_norm = normalize_text(w_path.read_text(encoding="utf-8"))
        b_norm = normalize_text(b_path.read_text(encoding="utf-8"))
        if w_norm != b_norm:
            errors.append(
                f"mirror drift {rel} — sync backend ↔ world (see ops/OBSERVATORY-CHANGE-CHECKLIST.md §3a)"
            )
    return errors


def _extract_symbol_sources(source: str, names: frozenset[str]) -> dict[str, str]:
    tree = ast.parse(source)
    found: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in names:
            segment = ast.get_source_segment(source, node)
            if segment:
                found[node.name] = normalize_text(segment)
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in names:
                    segment = ast.get_source_segment(source, node)
                    if segment:
                        found[target.id] = normalize_text(segment)
    missing = sorted(names - set(found))
    if missing:
        raise ValueError(f"missing symbols: {', '.join(missing)}")
    return found


def compare_server_deps_observatory(world_root: Path, backend_root: Path) -> list[str]:
    errors: list[str] = []
    rel = "server_deps.py"
    try:
        w_src = _read_rel(world_root, rel)
        b_src = _read_rel(backend_root, rel)
    except FileNotFoundError as exc:
        return [f"{exc.args[0]} missing in world or backend"]

    try:
        w_symbols = _extract_symbol_sources(w_src, SERVER_DEPS_OBSERVATORY_SYMBOLS)
        b_symbols = _extract_symbol_sources(b_src, SERVER_DEPS_OBSERVATORY_SYMBOLS)
    except SyntaxError as exc:
        return [f"server_deps.py parse error: {exc}"]
    except ValueError as exc:
        return [f"server_deps.py: {exc}"]

    for name in sorted(SERVER_DEPS_OBSERVATORY_SYMBOLS):
        if w_symbols.get(name) != b_symbols.get(name):
            errors.append(
                f"server_deps observatory drift in {name} — sync auth helpers used by Observatory"
            )
    return errors


def extract_market_server_observatory_fingerprint(source: str) -> str:
    norm = normalize_text(source)
    hits: list[str] = []
    for needle in MARKET_SERVER_OBSERVATORY_LINES:
        if needle not in norm:
            hits.append(f"missing line: {needle}")
    if hits:
        raise ValueError("; ".join(hits))
    block: list[str] = []
    for line in norm.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        lower = stripped.lower()
        if "observatory" in lower or "x-agent-id" in lower:
            block.append(stripped)
    return "\n".join(block)


def compare_market_server_observatory(world_root: Path, backend_root: Path) -> list[str]:
    errors: list[str] = []
    rel = "market_server.py"
    try:
        w_src = _read_rel(world_root, rel)
        b_src = _read_rel(backend_root, rel)
    except FileNotFoundError as exc:
        return [f"{exc.args[0]} missing in world or backend"]

    try:
        w_fp = extract_market_server_observatory_fingerprint(w_src)
        b_fp = extract_market_server_observatory_fingerprint(b_src)
    except ValueError as exc:
        return [f"market_server.py observatory fingerprint: {exc}"]

    if w_fp != b_fp:
        errors.append(
            "market_server.py observatory wiring drift — sync ObservatoryMiddleware, "
            "lifespan schema, router include, X-Agent-ID CORS"
        )
    return errors


def compare_mirror(world_root: Path, backend_root: Path) -> list[str]:
    errors: list[str] = []
    errors.extend(compare_exact_files(world_root, backend_root))
    errors.extend(compare_server_deps_observatory(world_root, backend_root))
    errors.extend(compare_market_server_observatory(world_root, backend_root))
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Observatory mirror diff gate (world vs backend)")
    parser.add_argument("--backend-path", type=Path, default=None)
    parser.add_argument("--world-path", type=Path, default=ROOT)
    args = parser.parse_args(argv)

    backend_path = args.backend_path or default_backend_path()
    world_path = args.world_path.resolve()

    if backend_path is None:
        print(
            "SKIP: backend repo not found — mirror diff not checked "
            "(checkout cli-market-backend or set --backend-path)",
            file=sys.stderr,
        )
        return 0

    backend_path = backend_path.resolve()
    errors = compare_mirror(world_path, backend_path)
    if errors:
        print("MIRROR DIFF FAIL:", file=sys.stderr)
        for line in errors:
            print(f"  - {line}", file=sys.stderr)
        return 1

    print(
        f"OK: Observatory mirror ({len(MIRROR_EXACT)} exact files + "
        f"server_deps[{len(SERVER_DEPS_OBSERVATORY_SYMBOLS)} symbols] + market_server wiring)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
