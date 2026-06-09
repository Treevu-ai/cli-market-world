"""Account summary for customer dashboard (CLI + landing + API)."""

from __future__ import annotations

import time
from typing import Any

from market_core import (
    TIERS,
    db_find_subscription_request,
    db_get_latest_subscription_request_for_user,
    db_get_subscription,
    db_get_user_email,
    db_list_api_keys,
    get_db,
)
from procure_billing import is_procure_tier, resolve_tier_config, tier_to_procure_plan


def _rate_count(db, key: str, window_start: float) -> int:
    row = db.execute(
        "SELECT SUM(counter) as n FROM rate_limits WHERE key=? AND window_start >= ?",
        (key, window_start),
    ).fetchone()
    return int(row["n"] or 0)


def _daily_window_start() -> float:
    now = time.time()
    return time.mktime(time.strptime(time.strftime("%Y-%m-%d", time.gmtime(now)), "%Y-%m-%d"))


def upgrade_next_step(tier: str, *, lang: str = "es") -> dict[str, Any]:
    tier_l = (tier or "free").lower()
    es = lang == "es"
    steps = {
        "free": {
            "next_tier": "pro",
            "title_es": "Pro — alertas, checkout y full MCP (foco principal para Agent Builders)",
            "title_en": "Pro — alerts, checkout and full MCP (primary for AI Agent Builders)",
            "cli_es": "market register  →  Pro en cli-market.dev/#pricing",
            "cli_en": "market register  →  Pro at cli-market.dev/#pricing",
            "url": "https://cli-market.dev/#pricing",
            "cta_es": "Activar Pro",
            "cta_en": "Activate Pro",
        },
        "starter": {
            "next_tier": "pro",
            "title_es": "Pro — checkout y 10k req/día",
            "title_en": "Pro — checkout and 10k req/day",
            "cli_es": "market upgrade",
            "cli_en": "market upgrade",
            "url": "https://cli-market.dev/#pricing",
            "cta_es": "Activar Pro",
            "cta_en": "Activate Pro",
        },
        "pro": {
            "next_tier": "builder",
            "title_es": "Builder — Intelligence API completa",
            "title_en": "Builder — full Intelligence API",
            "cli_es": "cli-market.dev/#pricing",
            "cli_en": "cli-market.dev/#pricing",
            "url": "https://cli-market.dev/#pricing",
            "cta_es": "Contactar ventas",
            "cta_en": "Contact sales",
        },
        "procure_starter": {
            "next_tier": "procure_pro",
            "title_es": "Procure Pro — aprobaciones y checkout",
            "title_en": "Procure Pro — approvals and checkout",
            "cli_es": "cli-market.dev/#procure",
            "cli_en": "cli-market.dev/#procure",
            "url": "https://cli-market.dev/#procure",
            "cta_es": "Upgrade Procure Pro",
            "cta_en": "Upgrade Procure Pro",
        },
        "procure_pro": {
            "next_tier": "procure_builder",
            "title_es": "Procure Builder — multi-país y volumen",
            "title_en": "Procure Builder — multi-country volume",
            "cli_es": "cli-market.dev/#procure",
            "cli_en": "cli-market.dev/#procure",
            "url": "https://cli-market.dev/#procure",
            "cta_es": "Upgrade Procure Builder",
            "cta_en": "Upgrade Procure Builder",
        },
    }
    if tier_l in ("builder", "enterprise", "procure_builder"):
        return {
            "next_tier": None,
            "title": "Plan máximo" if es else "Top tier",
            "cli": "market doctor",
            "url": None,
            "cta": None,
        }
    step = steps.get(tier_l, steps["free"])
    return {
        "next_tier": step["next_tier"],
        "title": step["title_es"] if es else step["title_en"],
        "cli": step["cli_es"] if es else step["cli_en"],
        "url": step["url"],
        "cta": step["cta_es"] if es else step["cta_en"],
    }


def _is_auto_activate_link(payment_link: str) -> bool:
    link = (payment_link or "").lower()
    return (
        "billing/subscriptions" in link
        or "/subscriptions?" in link
        or "mercadopago.com" in link
        or "mercadolibre" in link
        or "mercadopago:pending" in link
        or ":mercadopago:pending" in link
    )


def _billing_status(username: str, tier: str, *, lang: str = "es") -> dict[str, Any]:
    es = lang == "es"
    if tier in ("pro", "builder", "enterprise") or is_procure_tier(tier):
        return {
            "state": "active",
            "activation": None,
            "request_id": None,
            "message": None,
        }

    email = db_get_user_email(username) or ""
    pending = db_find_subscription_request(email=email) if email else None
    if not pending or pending.get("status") != "pending":
        return {"state": "none", "activation": None, "request_id": None, "message": None}

    req_id = pending.get("id") or ""
    is_starter = req_id.startswith("STR-") or req_id.startswith("PCS-")
    is_procure_req = req_id.startswith(("PCS-", "PCP-", "PCB-"))
    auto = _is_auto_activate_link(pending.get("payment_link") or "")
    if auto:
        label = "Procure" if is_procure_req else ("Starter" if is_starter else "Pro")
        mp_pending = "mercadopago" in (pending.get("payment_link") or "").lower()
        return {
            "state": "starter_pending_auto" if is_starter else "pro_pending_auto",
            "activation": "auto",
            "request_id": req_id,
            "approve_url": pending.get("payment_link"),
            "message": (
                f"{label} pendiente: complete el pago en Mercado Pago — activación en minutos."
                if es and mp_pending
                else f"{label} pendiente: confirme en PayPal — activación en segundos."
                if es
                else f"{label} pending: complete Mercado Pago checkout — activates in minutes."
                if mp_pending
                else f"{label} pending: confirm on PayPal — activates in seconds."
            ),
        }
    if is_starter:
        return {
            "state": "starter_pending_manual",
            "activation": "manual",
            "request_id": pending.get("id"),
            "approve_url": pending.get("payment_link"),
            "message": (
                "Starter pendiente: complete el checkout en la landing (enlace por email)."
                if es
                else "Starter pending: complete checkout on the landing (link emailed)."
            ),
        }
    return {
        "state": "pro_pending_manual",
        "activation": "manual",
        "request_id": pending.get("id"),
        "approve_url": pending.get("payment_link"),
        "message": (
            "Pro pendiente: activación manual ≤24 h hábiles tras confirmar pago."
            if es
            else "Pro pending: manual activation within 24 business hours after payment."
        ),
    }


def build_account_summary(username: str, *, lang: str = "es") -> dict[str, Any]:
    sub = db_get_subscription(username)
    tier = sub.get("tier", "free")
    tier_cfg = resolve_tier_config(tier, TIERS.get(tier, TIERS["free"]))
    keys = db_list_api_keys(username)
    keys_limit = tier_cfg.get("api_keys", 1)

    now = time.time()
    today_start = _daily_window_start()
    db = get_db()
    daily_used = _rate_count(db, f"{username}:daily", today_start)
    minute_used = _rate_count(db, f"{username}:min", now - 60)
    db.close()

    day_limit = sub.get("req_limit_day", tier_cfg["req_day"])
    min_limit = sub.get("req_limit_min", tier_cfg["req_min"])

    def pct(used: int, limit: int) -> float | None:
        if limit is None or limit < 0:
            return None
        return round(min(used / limit, 1.0) * 100, 1) if limit else 0.0

    return {
        "username": username,
        "tier": tier,
        "product_line": "procure" if is_procure_tier(tier) else "build",
        "procure_plan": tier_to_procure_plan(tier),
        "limits": {
            "req_day": day_limit if day_limit != -1 else "unlimited",
            "req_min": min_limit if min_limit != -1 else "unlimited",
            "api_keys": keys_limit if keys_limit != -1 else "unlimited",
            "checkout": bool(tier_cfg.get("checkout")),
            "alerts": tier_cfg.get("alerts", 0),
            "export": bool(tier_cfg.get("export")),
            "history_days": tier_cfg.get("history_days", 7),
        },
        "usage": {
            "requests_today": daily_used,
            "requests_last_minute": minute_used,
            "api_keys_used": len(keys),
            "daily_pct": pct(daily_used, day_limit if day_limit != -1 else 0),
            "minute_pct": pct(minute_used, min_limit if min_limit != -1 else 0),
        },
        "upgrade": upgrade_next_step(tier, lang=lang),
        "billing": _billing_status(username, tier, lang=lang),
    }


def resolve_pro_display_name(
    *,
    username: str,
    email: str = "",
    display_name: str = "",
) -> str:
    """Friendly name for emails — never the raw billing address alone."""
    explicit = (display_name or "").strip()
    if explicit:
        return explicit
    handle = (username or "").strip()
    if handle and not handle.startswith("user-"):
        return handle.replace("-", " ").replace("_", " ").title()
    local = (email or "").split("@")[0]
    local = local.replace(".", " ").replace("_", " ").replace("-", " ").strip()
    if local and not local.startswith("user"):
        return " ".join(part.capitalize() for part in local.split() if part)
    return handle or "Cliente"


def build_pro_email_context(
    username: str,
    *,
    email: str = "",
    password: str = "",
    display_name: str = "",
    request_id: str = "",
    lang: str = "es",
    payment_method: str = "paypal",
) -> dict[str, str]:
    """Unify nombre, email, usuario CLI y contraseña para el correo de bienvenida."""
    req = None
    try:
        if request_id:
            req = db_find_subscription_request(request_id=request_id)
        if not req and username:
            req = db_get_latest_subscription_request_for_user(username)
    except Exception:
        req = None
    resolved_email = (
        (email or (req or {}).get("email") or db_get_user_email(username) or "")
        .strip()
        .lower()
    )
    resolved_display = (display_name or (req or {}).get("display_name") or "").strip()
    dn = resolve_pro_display_name(
        username=username,
        email=resolved_email,
        display_name=resolved_display,
    )
    return {
        "display_name": dn,
        "username": (username or "").strip(),
        "email": resolved_email,
        "password": password,
        "lang": (lang or "es").strip().lower()[:2],
        "payment_method": (payment_method or "paypal").strip().lower(),
        "request_id": request_id or (req or {}).get("id") or "",
    }


def provision_pro_login_credentials(username: str) -> str:
    """Ensure CLI login exists for Pro; return one-time plaintext password for email."""
    import secrets
    import uuid

    from market_core import db_get_users, db_save_user
    from server_deps import hash_password

    name = (username or "").strip()
    if not name:
        raise ValueError("username required")
    password = secrets.token_urlsafe(10)
    users = db_get_users()
    existing = users.get(name) or {}
    token = existing.get("token") or str(uuid.uuid4())
    db_save_user(name, hash_password(password), token)
    return password