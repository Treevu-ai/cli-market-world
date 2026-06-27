"""Security helpers for CLI Market server."""

from __future__ import annotations

import ipaddress
import logging
import os
import re
import socket
from urllib.parse import urlparse

import httpx

logger = logging.getLogger("market.security")


def is_production_deploy() -> bool:
    """True when running in production (Railway or PAYPAL_SANDBOX != 'true')."""
    # Explicit Railway env
    if os.getenv("RAILWAY_ENVIRONMENT", "").lower() == "production":
        return True
    # Tests and local dev signal non-production via PAYPAL_SANDBOX=true
    sandbox = os.getenv("PAYPAL_SANDBOX", "").lower()
    if sandbox == "true":
        return False
    if sandbox == "false":
        return True
    # Fallback: treat as production if connected to a remote Postgres
    db = os.getenv("DATABASE_URL", "")
    return "railway.internal" in db or (
        "postgres" in db and "localhost" not in db and "127.0.0.1" not in db
    )


def paypal_allow_unverified_webhooks() -> bool:
    """Allow unverified PayPal webhooks only in non-production sandbox environments."""
    if is_production_deploy():
        return False
    return os.getenv("PAYPAL_ALLOW_UNVERIFIED_WEBHOOKS", "").lower() in ("1", "true", "yes")


def production_payment_config_warnings() -> list[str]:
    """Return warnings about missing payment config in production."""
    if not is_production_deploy():
        return []
    warnings = []
    for var in ("PAYPAL_CLIENT_ID", "PAYPAL_CLIENT_SECRET", "PAYPAL_WEBHOOK_ID"):
        if not os.getenv(var):
            warnings.append(f"{var} is not set — PayPal payments will not work")
    if not os.getenv("CHECKOUT_WEBHOOK_SECRET"):
        warnings.append("CHECKOUT_WEBHOOK_SECRET is not set — checkout webhooks unprotected")
    return warnings


_SAFE_URL_RE = re.compile(r"^https://[a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=%]+$")

_PRIVATE_HOSTS = (
    "localhost",
    "127.",
    "0.0.0.0",
    "::1",
    "10.",
    "192.168.",
    "169.254.",  # link-local / AWS metadata
)


def _is_private_ip(ip_str: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_str)
    except ValueError:
        return True
    return (
        ip.is_private
        or ip.is_loopback
        or ip.is_link_local
        or ip.is_reserved
        or ip.is_multicast
        or ip.is_unspecified
    )


def _resolve_host_ips(hostname: str) -> list[str]:
    try:
        infos = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise ValueError(f"Cannot resolve host for URL: {hostname!r}") from exc
    ips: list[str] = []
    for info in infos:
        ip = info[4][0]
        if ip not in ips:
            ips.append(ip)
    if not ips:
        raise ValueError(f"Cannot resolve host for URL: {hostname!r}")
    return ips


def validate_public_http_url(url: str) -> str:
    """Validate and return a safe public HTTPS URL. Raises ValueError if invalid."""
    url = url.strip()
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()

    # Block private/local hostnames first (before scheme check so message is accurate)
    if any(host.startswith(b) or host == b.rstrip(".") for b in _PRIVATE_HOSTS):
        raise ValueError(f"Non-public or not allowed URL: {url!r}")

    if parsed.scheme != "https":
        raise ValueError(f"Only HTTPS URLs are allowed, got: {url!r}")

    if not parsed.netloc:
        raise ValueError(f"URL has no host: {url!r}")

    if parsed.username or parsed.password:
        raise ValueError(f"URL must not include credentials: {url!r}")

    for ip in _resolve_host_ips(host):
        if _is_private_ip(ip):
            raise ValueError(f"Non-public or not allowed URL: {url!r}")

    if not _SAFE_URL_RE.match(url):
        raise ValueError(f"URL contains invalid characters: {url!r}")

    return url


def safe_post_json(url: str, payload: dict, *, timeout: float = 15.0) -> httpx.Response:
    """POST JSON to a user-supplied URL after SSRF validation."""
    safe_url = validate_public_http_url(url)
    with httpx.Client(timeout=timeout, follow_redirects=False) as client:
        return client.post(safe_url, json=payload)


def patch_alert_webhook_dispatch() -> None:
    """Replace core alert webhook dispatch with SSRF-safe POST (until core pin bumps)."""
    import market_core.market_alerts as ma

    if getattr(ma, "_webhook_ssrf_patched", False):
        return

    def _send_webhook(alert: dict, triggered: dict) -> bool:
        from datetime import datetime, timezone

        url = alert.get("notify_webhook", "")
        if not url:
            return False
        payload = {
            "alert_id": alert["id"],
            "alert_name": alert["name"],
            "condition": alert["condition"],
            "product_query": alert["product_query"],
            "product_id": triggered["product_id"],
            "product_name": triggered["product_name"],
            "store": triggered["store"],
            "price_now": triggered["price_now"],
            "price_before": triggered["price_before"],
            "delta_pct": triggered["delta_pct"],
            "fired_at": datetime.now(timezone.utc).isoformat(),
        }
        try:
            response = safe_post_json(url, payload, timeout=5.0)
            return response.status_code < 300
        except ValueError as exc:
            logger.warning("Alert %s webhook blocked (SSRF): %s", alert["id"], exc)
            return False
        except Exception as exc:
            logger.warning("Alert %s webhook failed: %s", alert["id"], exc)
            return False

    ma._send_webhook = _send_webhook
    ma._webhook_ssrf_patched = True
