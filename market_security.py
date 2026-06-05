"""Security helpers for CLI Market server."""

from __future__ import annotations

import os
import re
from urllib.parse import urlparse


def is_production_deploy() -> bool:
    """True when running on Railway (RAILWAY_ENVIRONMENT is set to 'production')."""
    env = os.getenv("RAILWAY_ENVIRONMENT", "").lower()
    if env:
        return env == "production"
    # Fallback: treat as production if DATABASE_URL points to an external host
    db = os.getenv("DATABASE_URL", "")
    return "railway.internal" in db or ("postgres" in db and "localhost" not in db and "127.0.0.1" not in db)


def paypal_allow_unverified_webhooks() -> bool:
    """Allow unverified PayPal webhooks in non-production environments."""
    return not is_production_deploy() or os.getenv("PAYPAL_ALLOW_UNVERIFIED", "").lower() in ("1", "true", "yes")


def production_payment_config_warnings() -> list[str]:
    """Return a list of warnings about missing payment config in production."""
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


def validate_public_http_url(url: str) -> str:
    """Validate and return a safe public HTTPS URL. Raises ValueError if invalid."""
    url = url.strip()
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise ValueError(f"Only HTTPS URLs are allowed, got: {url!r}")
    if not parsed.netloc:
        raise ValueError(f"URL has no host: {url!r}")
    # Block private/local addresses
    host = parsed.hostname or ""
    blocked = ("localhost", "127.", "0.0.0.0", "::1", "10.", "192.168.", "172.")
    if any(host.startswith(b) for b in blocked):
        raise ValueError(f"Private/local URLs are not allowed: {url!r}")
    if not _SAFE_URL_RE.match(url):
        raise ValueError(f"URL contains invalid characters: {url!r}")
    return url
