"""Best-effort funnel/telemetry helpers for the `market` CLI.

Extracted from market_cli.py — used by cmd_hello, cmd_demo, cmd_tutorial,
cmd_mcp_setup, and main() to report install/onboarding events. All calls
are fire-and-forget: failures never block the CLI command itself.
"""

from __future__ import annotations

from market_core import SESSION_FILE, api, get_session_username
from market_stats import PACKAGE_VERSION


def _install_session_id() -> str:
    """Stable anonymous id for CLI funnel events (per machine profile)."""
    sid_file = SESSION_FILE.parent / "funnel_session"
    if sid_file.is_file():
        return sid_file.read_text(encoding="utf-8").strip()
    import uuid

    sid = str(uuid.uuid4())
    sid_file.parent.mkdir(parents=True, exist_ok=True)
    sid_file.write_text(sid, encoding="utf-8")
    return sid


def _report_install_event(*, source: str = "cli") -> bool:
    """Report first CLI activation after pip install (once per machine)."""
    flag = SESSION_FILE.parent / "funnel_install"
    if flag.is_file():
        return False
    try:
        import platform

        api(
            "POST",
            "/v1/events",
            {
                "event": "install",
                "dedupe": True,
                "session_id": _install_session_id(),
                "meta": {
                    "source": source,
                    "cli_version": PACKAGE_VERSION,
                    "platform": platform.system(),
                },
            },
        )
        flag.parent.mkdir(parents=True, exist_ok=True)
        flag.write_text("1", encoding="utf-8")
        return True
    except Exception:
        return False


def _report_onboarding_event(event: str, *, meta: dict | None = None, dedupe: bool = True) -> None:
    try:
        payload: dict = {
            "event": event,
            "dedupe": dedupe,
            "session_id": _install_session_id(),
            "meta": meta or {},
        }
        username = get_session_username()
        if username:
            payload["username"] = username
        api("POST", "/v1/events", payload)
    except Exception:
        pass
