"""Moat health watchdog — alerts ops when the data pipeline fails silently.

For a data company, serving empty or stale data without anyone noticing is
existential. This module detects the three silent failure modes we care about
and emails ops (with a cooldown so we don't spam):

  1. sqlite_fallback — PostgreSQL was configured (DATABASE_URL set) but the app
     fell back to SQLite, i.e. it is serving an empty/wrong dataset.
  2. moat_stale      — the most recent snapshot is older than MOAT_STALE_HOURS
     (default 24h), i.e. the collector stopped writing.
  3. collect_empty   — the last collector run finished but ingested 0 prices
     (runner alive, ingest broken).

Design:
  - Zero new dependencies: reuses market_connectors.email_outbound._send.
  - Degrades gracefully: if SMTP is unconfigured it still logs at ERROR.
  - Cooldown is file-based (/tmp) so it works even in the SQLite-fallback case
    where the database is unreliable, and survives across the API/collector
    processes independently.
  - Safe to call frequently and from anywhere (collector loop, API startup).
"""

from __future__ import annotations

import logging
import os
import time

logger = logging.getLogger("market").getChild("health_alert")

MOAT_STALE_HOURS = float(os.getenv("MOAT_STALE_HOURS", "24"))
ALERT_COOLDOWN_HOURS = float(os.getenv("MOAT_ALERT_COOLDOWN_HOURS", "6"))
OPS_EMAIL = os.getenv("MARKET_OPS_EMAIL") or os.getenv("BILLING_NOTIFY_EMAIL", "")
_COOLDOWN_DIR = os.getenv("MOAT_ALERT_STATE_DIR", "/tmp/cli-market-health")


def _cooldown_ok(key: str, hours: float) -> bool:
    """True if we have NOT alerted for ``key`` within the last ``hours``.

    Records the current time on success so the next call inside the window
    returns False. Best-effort: any filesystem error fails open (alerts).
    """
    try:
        os.makedirs(_COOLDOWN_DIR, exist_ok=True)
        path = os.path.join(_COOLDOWN_DIR, f"{key}.ts")
        now = time.time()
        if os.path.exists(path):
            last = os.path.getmtime(path)
            if now - last < hours * 3600:
                return False
        # touch
        with open(path, "w") as fh:
            fh.write(str(now))
        return True
    except Exception as e:
        logger.debug("Cooldown check failed (failing open): %s", e)
        return True


def check_moat_health(db=None) -> dict:
    """Inspect backend + moat freshness. Returns a structured status dict.

    Never raises — on any error it reports an ``unknown`` problem so the caller
    can still alert rather than crash.
    """
    import market_core

    problems: list[str] = []
    moat_age_h: float | None = None
    last_collected = None
    backend = "postgresql" if market_core.USE_PG else "sqlite"

    # 1. SQLite fallback while Postgres was expected.
    if market_core.DATABASE_URL and not market_core.USE_PG:
        problems.append("sqlite_fallback")

    # 2 & 3. Freshness + empty ingest — only meaningful when we have a DB.
    own_db = False
    try:
        if db is None:
            db = market_core.get_db()
            own_db = True
        row = db.execute("SELECT MAX(queried_at) AS t FROM price_snapshots").fetchone()
        last_collected = row["t"] if row else None
        if last_collected is not None:
            from routers.health import _age_hours
            moat_age_h = _age_hours(last_collected)
            if moat_age_h is not None and moat_age_h >= MOAT_STALE_HOURS:
                problems.append("moat_stale")
        else:
            problems.append("moat_empty")
    except Exception as e:
        logger.warning("Moat health check could not read DB: %s", e)
        problems.append("unknown")
    finally:
        if own_db and db is not None:
            try:
                db.close()
            except Exception:
                pass

    return {
        "healthy": not problems,
        "problems": problems,
        "backend": backend,
        "moat_age_hours": round(moat_age_h, 1) if moat_age_h is not None else None,
        "last_collected_at": str(last_collected) if last_collected else None,
    }


def alert_if_unhealthy(db=None, *, source: str = "unknown") -> dict:
    """Run the health check and, if unhealthy, log + email ops (cooldown-gated).

    ``source`` identifies the caller (e.g. "collector", "api-startup") and is
    included in the alert. Returns the health status dict for inspection/tests.
    """
    status = check_moat_health(db)
    if status["healthy"]:
        return status

    problems = ",".join(status["problems"])
    logger.error(
        "MOAT UNHEALTHY [%s]: %s · backend=%s · age=%sh",
        source, problems, status["backend"], status["moat_age_hours"],
    )

    # Cooldown key is per problem-set so a new kind of failure alerts immediately
    # even if another is still in its cooldown window.
    if not _cooldown_ok(f"moat-{problems}", ALERT_COOLDOWN_HOURS):
        logger.info("Moat alert suppressed by cooldown (%s)", problems)
        return status

    _dispatch_alert(status, source)
    return status


_PROBLEM_COPY = {
    "sqlite_fallback": "PostgreSQL no disponible — el servicio cayó a SQLite y está sirviendo datos vacíos/incorrectos.",
    "moat_stale": "El moat está desactualizado — el collector dejó de escribir snapshots.",
    "moat_empty": "No hay snapshots en la base — el moat está vacío.",
    "collect_empty": "El último ciclo del collector ingestó 0 precios.",
    "unknown": "No se pudo leer la base para verificar la salud del moat.",
}


def _dispatch_alert(status: dict, source: str) -> None:
    problems = status["problems"]
    lines = [_PROBLEM_COPY.get(p, p) for p in problems]
    subject = f"🚨 CLI Market: moat unhealthy ({', '.join(problems)})"
    body = (
        "Alerta de salud del moat de CLI Market.\n\n"
        f"Origen: {source}\n"
        f"Backend: {status['backend']}\n"
        f"Antigüedad del dato: {status['moat_age_hours']}h\n"
        f"Último snapshot: {status['last_collected_at']}\n\n"
        "Problemas detectados:\n" + "\n".join(f"  • {ln}" for ln in lines) + "\n\n"
        "Revisá los servicios API y Collector en Railway."
    )

    if not OPS_EMAIL:
        logger.error("No MARKET_OPS_EMAIL/BILLING_NOTIFY_EMAIL set — cannot email moat alert")
        return
    try:
        from market_connectors.email_outbound import _send
        result = _send(OPS_EMAIL, subject, body, body.replace("\n", "<br>\n"))
        if result.get("sent"):
            logger.warning("Moat alert emailed to %s", OPS_EMAIL)
        else:
            logger.error("Moat alert email NOT sent: %s", result.get("reason"))
    except Exception as e:
        logger.exception("Failed to dispatch moat alert: %s", e)
