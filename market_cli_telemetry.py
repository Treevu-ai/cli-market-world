"""Best-effort funnel/telemetry helpers for the `market` CLI.

Extracted from market_cli.py — used by cmd_hello, cmd_demo, cmd_tutorial,
cmd_mcp_setup, and main() to report install/onboarding events. All calls
are fire-and-forget: failures never block the CLI command itself.

P1 — Dropoff tracking (install → register):
  report_command_attempted()   — qué comando fue el primero en ejecutarse
  report_command_result()      — si el comando tuvo éxito o falló
  report_auth_wall_hit()       — cuándo el usuario choca con el muro de auth (401)
"""

from __future__ import annotations

import time

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


# ---------------------------------------------------------------------------
# P1 — Dropoff granular tracking (install → register)
# ---------------------------------------------------------------------------

# Archivo flag: marca que ya se reportó el primer comando exitoso (una vez por máquina)
def _first_command_flag() -> "Path":  # noqa: F821
    return SESSION_FILE.parent / "funnel_first_cmd_ok"


def report_command_attempted(command: str) -> None:
    """Registra qué comando intentó el usuario. Dedupe: solo el primer intento."""
    flag = SESSION_FILE.parent / "funnel_cmd_attempted"
    if flag.is_file():
        return
    try:
        import platform
        api(
            "POST",
            "/v1/events",
            {
                "event": "cli_command_attempted",
                "dedupe": True,
                "session_id": _install_session_id(),
                "meta": {
                    "command": command,
                    "cli_version": PACKAGE_VERSION,
                    "platform": platform.system(),
                },
            },
        )
        flag.parent.mkdir(parents=True, exist_ok=True)
        flag.write_text(command, encoding="utf-8")
    except Exception:
        pass


def report_command_result(
    command: str,
    *,
    success: bool,
    elapsed_ms: int | None = None,
    error_type: str | None = None,
) -> None:
    """Registra si el primer comando tuvo éxito o falló y de qué tipo.

    Este evento es no-deduplicado para poder contar tasas de error a lo largo
    del tiempo, pero solo enviamos los primeros N comandos por sesión para no
    saturar el endpoint.
    """
    # Contamos invocaciones en la sesión para limitar telemetría a primeras 5
    counter_file = SESSION_FILE.parent / "funnel_cmd_count"
    try:
        count = int(counter_file.read_text(encoding="utf-8").strip()) if counter_file.is_file() else 0
    except Exception:
        count = 0
    if count >= 5:
        return
    try:
        meta: dict = {
            "command": command,
            "success": success,
            "cli_version": PACKAGE_VERSION,
        }
        if elapsed_ms is not None:
            meta["elapsed_ms"] = elapsed_ms
        if error_type:
            meta["error_type"] = error_type
        api(
            "POST",
            "/v1/events",
            {
                "event": "cli_command_result",
                "dedupe": False,
                "session_id": _install_session_id(),
                "meta": meta,
            },
        )
        counter_file.parent.mkdir(parents=True, exist_ok=True)
        counter_file.write_text(str(count + 1), encoding="utf-8")
    except Exception:
        pass


def report_auth_wall_hit(command: str) -> None:
    """El usuario intentó un comando que requiere auth y no está registrado.

    Este es el evento más crítico para P1: cuantifica cuántos usuarios llegan
    al muro de autenticación (0.43% no lo superan para llegar a register).
    """
    try:
        api(
            "POST",
            "/v1/events",
            {
                "event": "cli_auth_wall_hit",
                "dedupe": False,
                "session_id": _install_session_id(),
                "meta": {
                    "command": command,
                    "cli_version": PACKAGE_VERSION,
                    "registered": bool(get_session_username()),
                },
            },
        )
    except Exception:
        pass


def command_timer() -> "tuple[float, callable]":
    """Retorna (start_time, get_elapsed_ms). Usado en main() para medir latencia."""
    t0 = time.monotonic()

    def elapsed() -> int:
        return int((time.monotonic() - t0) * 1000)

    return t0, elapsed
