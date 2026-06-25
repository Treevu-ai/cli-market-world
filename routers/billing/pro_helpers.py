"""Shared Pro checkout helpers (dedupe, MP notes, env flags)."""

from __future__ import annotations

import os
import re

_MP_URL_RE = re.compile(r"https?://[^\s]*mercadopago|mercadolibre", re.I)


def wallet_manual_fallback_enabled() -> bool:
    return os.getenv("WALLET_MANUAL_FALLBACK", "").strip().lower() in ("1", "true", "yes")


def procure_mp_checkout_enabled() -> bool:
    """Feature flag — Procure Mercado Pago / wallet checkout (Sprint 1 dark launch default off)."""
    return os.getenv("PROCURE_MP_CHECKOUT", "").strip().lower() in ("1", "true", "yes")


def mp_pay_note(wallet_method: str = "") -> str:
    wallet = (wallet_method or "").strip().lower()
    if wallet in ("yape", "plin"):
        return f"{wallet}:mercadopago:pending"
    return "mercadopago:pending"


def is_mp_billing_method(method: str) -> bool:
    return (method or "").strip().lower() in ("mercadopago", "yape", "plin")


def is_manual_wallet_pro_payment_link(payment_link: str) -> bool:
    """Yape/Plin in-app transfer — ops activates after confirming bank receipt."""
    low = (payment_link or "").strip().lower()
    if not low.startswith(("yape:", "plin:")):
        return False
    return "mercadopago" not in low


def is_mercadopago_checkout_link(payment_link: str) -> bool:
    link = (payment_link or "").strip()
    if not link:
        return False
    if link.lower().startswith(("http://", "https://")):
        return bool(_MP_URL_RE.search(link))
    low = link.lower()
    return (
        low.startswith("mercadopago")
        or ":mercadopago:pending" in low
        or low.endswith(":mercadopago:pending")
    )


def mp_method_matches_link(method: str, payment_link: str) -> bool:
    low = (payment_link or "").lower()
    m = (method or "").strip().lower()
    if not is_mp_billing_method(m):
        return False
    if low.startswith(("http://", "https://")):
        return bool(_MP_URL_RE.search(low))
    if m == "mercadopago":
        return low.startswith("mercadopago") or ":mercadopago:pending" in low
    if m in ("yape", "plin"):
        return low.startswith(f"{m}:") or f"{m}:mercadopago" in low
    return False


def checkout_url_from_request(row: dict) -> str:
    link = (row.get("payment_link") or "").strip()
    if link.lower().startswith(("http://", "https://")):
        return link
    return ""


def duplicate_mp_checkout_payload(
    recent: dict,
    *,
    method: str,
    lang: str,
) -> dict | None:
    """Return a duplicate checkout response when a recent MP request matches."""
    if (recent.get("status") or "").lower() != "pending":
        return None
    if not mp_method_matches_link(method, recent.get("payment_link") or ""):
        return None
    checkout_url = checkout_url_from_request(recent)
    if not checkout_url:
        return None
    display_method = method if method in ("yape", "plin") else "mercadopago"
    return {
        "ok": True,
        "request_id": recent["id"],
        "username": recent["username"],
        "email": recent["email"],
        "payment_method": display_method,
        "payment_rail": "mercadopago",
        "payment_mode": "mercadopago_checkout",
        "wallet_checkout": method in ("yape", "plin"),
        "checkout_url": checkout_url or None,
        "approve_url": checkout_url or None,
        "payment_link": checkout_url or recent.get("payment_link"),
        "auto_activate": True,
        "email_sent": bool(recent.get("email_sent")),
        "duplicate": True,
        "message": (
            "Ya enviamos el enlace de Mercado Pago recientemente. Revisa tu bandeja (y spam)."
            if lang == "es"
            else "We already sent the Mercado Pago link recently. Check inbox (and spam)."
        ),
    }