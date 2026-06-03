"""Price alert evaluation and dispatch.

Conditions (list-closed):
  price_jump       — price rose >= threshold_pct vs previous snapshot
  price_drop       — price fell >= threshold_pct vs previous snapshot
  price_min_30d    — current price is the lowest in the last 30 days
  dispersion_anomaly — price spread across stores exceeds threshold_pct std devs

Channels:
  email   — via market_connectors.email_outbound (Pro)
  webhook — HTTP POST to notify_webhook URL (Enterprise)

evaluate_alerts(db) is called post-collection and fires any triggered alerts.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone

import httpx

from market_core import get_db

logger = logging.getLogger("market.alerts")

SUPPORTED_CONDITIONS = ("price_jump", "price_drop", "price_min_30d", "dispersion_anomaly")


# ── DB helpers ────────────────────────────────────────────────────────────────

def db_create_alert(
    username: str,
    name: str,
    condition: str,
    product_query: str,
    store: str,
    threshold_pct: float,
    notify_email: str,
    notify_webhook: str,
    cooldown_hours: int,
) -> dict:
    alert_id = f"ALT-{uuid.uuid4().hex[:8].upper()}"
    db = get_db()
    db.execute(
        """INSERT INTO price_alerts
           (id, username, name, condition, product_query, store,
            threshold_pct, notify_email, notify_webhook, cooldown_hours)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (alert_id, username, name, condition, product_query, store,
         threshold_pct, notify_email, notify_webhook, cooldown_hours),
    )
    db.commit()
    db.close()
    return db_get_alert(alert_id)


def db_get_alert(alert_id: str) -> dict | None:
    db = get_db()
    row = db.execute("SELECT * FROM price_alerts WHERE id=?", (alert_id,)).fetchone()
    db.close()
    return dict(row) if row else None


def db_list_alerts(username: str) -> list[dict]:
    db = get_db()
    rows = db.execute(
        "SELECT * FROM price_alerts WHERE username=? ORDER BY created_at DESC",
        (username,),
    ).fetchall()
    db.close()
    return [dict(r) for r in rows]


def db_delete_alert(username: str, alert_id: str) -> bool:
    db = get_db()
    cur = db.execute(
        "DELETE FROM price_alerts WHERE id=? AND username=?", (alert_id, username)
    )
    db.commit()
    db.close()
    return cur.rowcount > 0


def db_toggle_alert(username: str, alert_id: str, active: bool) -> dict | None:
    db = get_db()
    db.execute(
        "UPDATE price_alerts SET active=? WHERE id=? AND username=?",
        (1 if active else 0, alert_id, username),
    )
    db.commit()
    db.close()
    return db_get_alert(alert_id)


def _mark_fired(db, alert_id: str, now_iso: str) -> None:
    db.execute(
        "UPDATE price_alerts SET last_fired_at=? WHERE id=?", (now_iso, alert_id)
    )


def _log_event(
    db,
    alert_id: str,
    username: str,
    product_id: str,
    store: str,
    product_name: str,
    condition: str,
    price_now: float,
    price_before: float,
    delta_pct: float,
    notified: bool,
) -> None:
    db.execute(
        """INSERT INTO alert_events
           (alert_id, username, product_id, store, product_name,
            condition, price_now, price_before, delta_pct, notified)
           VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (alert_id, username, product_id, store, product_name,
         condition, price_now, price_before, delta_pct, 1 if notified else 0),
    )


# ── Evaluation ────────────────────────────────────────────────────────────────

def evaluate_alerts(db=None) -> int:
    """Evaluate all active alerts against current price_snapshots.

    Called post-collection. Opens its own DB connection if not provided.
    Returns number of alerts that fired.
    """
    owns_db = db is None
    if owns_db:
        db = get_db()
    try:
        return _run_evaluation(db)
    finally:
        if owns_db:
            db.commit()
            db.close()


def _run_evaluation(db) -> int:
    now = datetime.now(timezone.utc)
    now_iso = now.isoformat()
    fired = 0

    rows = db.execute(
        "SELECT * FROM price_alerts WHERE active=1"
    ).fetchall()

    for row in rows:
        alert = dict(row)
        # Cooldown check
        if alert.get("last_fired_at"):
            try:
                last = datetime.fromisoformat(
                    str(alert["last_fired_at"]).replace("Z", "+00:00")
                )
                if last.tzinfo is None:
                    last = last.replace(tzinfo=timezone.utc)
                cooldown = timedelta(hours=int(alert.get("cooldown_hours") or 24))
                if now - last < cooldown:
                    continue
            except (ValueError, TypeError):
                pass

        try:
            triggered = _evaluate_one(db, alert, now)
        except Exception as e:
            logger.warning("Alert %s evaluation error: %s", alert["id"], e)
            continue

        if triggered:
            fired += 1
            _mark_fired(db, alert["id"], now_iso)
            notified = _dispatch(alert, triggered)
            _log_event(
                db,
                alert["id"],
                alert["username"],
                triggered["product_id"],
                triggered["store"],
                triggered["product_name"],
                alert["condition"],
                triggered["price_now"],
                triggered["price_before"],
                triggered["delta_pct"],
                notified,
            )

    return fired


def _evaluate_one(db, alert: dict, now: datetime) -> dict | None:
    condition = alert["condition"]
    query = alert["product_query"]
    store_filter = alert.get("store") or ""
    threshold = float(alert.get("threshold_pct") or 5.0)

    store_clause = "AND store = ?" if store_filter else ""
    params: list = [f"%{query}%"]
    if store_filter:
        params.append(store_filter)

    if condition in ("price_jump", "price_drop"):
        return _eval_price_change(db, alert, params, store_clause, threshold, condition)
    elif condition == "price_min_30d":
        return _eval_price_min_30d(db, alert, params, store_clause, now)
    elif condition == "dispersion_anomaly":
        return _eval_dispersion(db, alert, params, store_clause, threshold)
    return None


def _eval_price_change(db, alert, params, store_clause, threshold, condition) -> dict | None:
    """Compare latest snapshot price vs previous snapshot price."""
    rows = db.execute(
        f"""SELECT product_id, store, store_name, name, price, queried_at
            FROM price_snapshots
            WHERE name LIKE ? AND price > 0 {store_clause}
            ORDER BY queried_at DESC LIMIT 20""",
        params,
    ).fetchall()

    for row in rows:
        product_id = row["product_id"]
        store = row["store"]
        price_now = float(row["price"])

        prev = db.execute(
            """SELECT price FROM price_history
               WHERE product_id=? AND store=?
               ORDER BY recorded_at DESC LIMIT 1 OFFSET 1""",
            (product_id, store),
        ).fetchone()

        if not prev:
            continue
        price_before = float(prev["price"])
        if price_before <= 0:
            continue

        delta_pct = (price_now - price_before) / price_before * 100

        triggered = (
            (condition == "price_jump" and delta_pct >= threshold) or
            (condition == "price_drop" and delta_pct <= -threshold)
        )
        if triggered:
            return {
                "product_id": product_id,
                "store": store,
                "product_name": row["name"],
                "price_now": price_now,
                "price_before": price_before,
                "delta_pct": round(delta_pct, 2),
            }
    return None


def _eval_price_min_30d(db, alert, params, store_clause, now) -> dict | None:
    """Fire if current price equals the 30-day minimum."""
    cutoff = (now - timedelta(days=30)).isoformat()
    rows = db.execute(
        f"""SELECT product_id, store, name, price
            FROM price_snapshots
            WHERE name LIKE ? AND price > 0 {store_clause}
            ORDER BY queried_at DESC LIMIT 20""",
        params,
    ).fetchall()

    for row in rows:
        product_id = row["product_id"]
        store = row["store"]
        price_now = float(row["price"])

        min_row = db.execute(
            """SELECT MIN(price) as min_price FROM price_history
               WHERE product_id=? AND store=? AND price > 0 AND recorded_at >= ?""",
            (product_id, store, cutoff),
        ).fetchone()

        if not min_row or not min_row["min_price"]:
            continue
        min_price = float(min_row["min_price"])
        if price_now <= min_price * 1.001:  # within 0.1% tolerance
            return {
                "product_id": product_id,
                "store": store,
                "product_name": row["name"],
                "price_now": price_now,
                "price_before": min_price,
                "delta_pct": 0.0,
            }
    return None


def _eval_dispersion(db, alert, params, store_clause, threshold) -> dict | None:
    """Fire if price spread across stores exceeds threshold_pct."""
    rows = db.execute(
        f"""SELECT product_id, store, name, price
            FROM price_snapshots
            WHERE name LIKE ? AND price > 0 {store_clause}
            ORDER BY queried_at DESC LIMIT 50""",
        params,
    ).fetchall()

    if len(rows) < 2:
        return None

    prices = [float(r["price"]) for r in rows]
    avg = sum(prices) / len(prices)
    if avg <= 0:
        return None
    spread_pct = (max(prices) - min(prices)) / avg * 100

    if spread_pct >= threshold:
        best = min(rows, key=lambda r: float(r["price"]))
        worst = max(rows, key=lambda r: float(r["price"]))
        return {
            "product_id": best["product_id"],
            "store": best["store"],
            "product_name": best["name"],
            "price_now": float(best["price"]),
            "price_before": float(worst["price"]),
            "delta_pct": round(-spread_pct, 2),
        }
    return None


# ── Dispatch ──────────────────────────────────────────────────────────────────

def _dispatch(alert: dict, triggered: dict) -> bool:
    """Send notification. Returns True if at least one channel succeeded."""
    ok = False
    if alert.get("notify_email"):
        ok = _send_email(alert, triggered) or ok
    if alert.get("notify_webhook"):
        ok = _send_webhook(alert, triggered) or ok
    return ok


def _send_email(alert: dict, t: dict) -> bool:
    try:
        from market_connectors.email_outbound import _send, _smtp_configured
        if not _smtp_configured():
            logger.warning("Alert %s: SMTP not configured, skipping email", alert["id"])
            return False

        condition_labels = {
            "price_jump": f"subió {abs(t['delta_pct']):.1f}%",
            "price_drop": f"bajó {abs(t['delta_pct']):.1f}%",
            "price_min_30d": "está en su mínimo de 30 días",
            "dispersion_anomaly": f"dispersión entre tiendas: {abs(t['delta_pct']):.1f}%",
        }
        label = condition_labels.get(alert["condition"], alert["condition"])
        subject = f"🔔 Alerta CLI Market — {t['product_name'][:40]} {label}"
        text = (
            f"Alerta: {alert['name']}\n\n"
            f"Producto: {t['product_name']}\n"
            f"Tienda:   {t['store']}\n"
            f"Condición: {alert['condition']} ({label})\n"
            f"Precio actual:  {t['price_now']}\n"
            f"Precio anterior: {t['price_before']}\n\n"
            f"Consultá el agente: POST /v1/intel/ask\n\n"
            f"— CLI Market Intel\n"
            f"Para desactivar esta alerta: DELETE /v1/alerts/{alert['id']}\n"
        )
        result = _send(alert["notify_email"], subject, text, text.replace("\n", "<br>\n"))
        return result.get("sent", False)
    except Exception as e:
        logger.exception("Alert %s email dispatch failed: %s", alert["id"], e)
        return False


def _send_webhook(alert: dict, t: dict) -> bool:
    url = alert.get("notify_webhook", "")
    if not url:
        return False
    try:
        payload = {
            "alert_id": alert["id"],
            "alert_name": alert["name"],
            "condition": alert["condition"],
            "product_query": alert["product_query"],
            "product_id": t["product_id"],
            "product_name": t["product_name"],
            "store": t["store"],
            "price_now": t["price_now"],
            "price_before": t["price_before"],
            "delta_pct": t["delta_pct"],
            "fired_at": datetime.now(timezone.utc).isoformat(),
        }
        r = httpx.post(url, json=payload, timeout=5.0)
        return r.status_code < 300
    except Exception as e:
        logger.warning("Alert %s webhook failed: %s", alert["id"], e)
        return False
