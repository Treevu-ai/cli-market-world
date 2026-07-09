"""Console entry and thin re-export layer for MCP server (`market-mcp` after pip install)."""

from __future__ import annotations

import json
import os
import sys
import time

# Force UTF-8 for stdio on Windows so MCP JSON-RPC does not crash on Unicode
# characters (e.g. →, ·) when the console code page is cp1252.
#
# Skipped under pytest (PYTEST_CURRENT_TEST is set for the lifetime of a test
# run): this reassignment is permanent and process-wide — module imports are
# cached, so it only ever runs once per process. If the first import happens
# while pytest's own per-test capture plugin has sys.stdout/stderr swapped to
# a per-test buffer, this wraps *that* buffer and never lets go. When pytest
# closes the buffer at the end of that one test, every subsequent test's
# stdout/stderr access (capsys, TestClient, logging, ...) fails with
# "ValueError: I/O operation on closed file" for the rest of the session —
# reproducible only via the full suite (whichever test first imports
# market_mcp, e.g. test_regression.py::test_market_mcp_imports), never in
# isolation. Real `market-mcp` CLI/MCP server usage never sets this env var,
# so production behavior is unchanged.
if sys.platform == "win32" and "PYTEST_CURRENT_TEST" not in os.environ:
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", line_buffering=True)

from market_agent_id import get_agent_id, patch_core_api_agent_header

patch_core_api_agent_header()

from market_core.market_mcp import api, get_token, handle_tool as _core_handle_tool, main as _core_main

__all__ = ["api", "get_token", "handle_tool", "main"]


def _client_telemetry_enabled() -> bool:
    return os.getenv("MARKET_MCP_CLIENT_TELEMETRY", "1").strip().lower() not in (
        "0",
        "false",
        "no",
    )


def _report_tool_execution(name: str, raw: str, *, elapsed_ms: int) -> None:
    """Best-effort client-side tool report (API-backed MCP already hits Observatory middleware)."""
    if not _client_telemetry_enabled():
        return
    try:
        payload = json.loads(raw) if raw else {}
        success = "error" not in payload
    except json.JSONDecodeError:
        success = False
    try:
        from market_core.market_mcp_registry import resolve_tool_name

        tool = resolve_tool_name(name) or name
        api(
            "POST",
            "/v1/events",
            {
                "event": "mcp_tool_call",
                "dedupe": False,
                "meta": {
                    "tool": tool,
                    "success": success,
                    "latency_ms": elapsed_ms,
                    "source": "mcp_client",
                    "agent_id": get_agent_id() or None,
                },
            },
        )
    except Exception:
        pass


def handle_tool(name: str, args: dict) -> str:
    t0 = time.perf_counter()
    result = _core_handle_tool(name, args)
    elapsed_ms = int((time.perf_counter() - t0) * 1000)
    _report_tool_execution(name, result, elapsed_ms=elapsed_ms)
    return result


def main() -> None:
    _core_main()

if __name__ == "__main__":
    main()