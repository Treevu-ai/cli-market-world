"""Per-store API credentials from environment (never commit secrets).

Env pattern (store id uppercased, e.g. falabella_pe → FALABELLA_PE):

  STORE_FALABELLA_PE_MAGENTO_TOKEN       Magento / Adobe Commerce integration token
  STORE_GYMSHARK_STOREFRONT_TOKEN        Shopify Storefront API token
  STORE_WONG_VTEX_APP_KEY                VTEX app key (optional — higher rate limits)
  STORE_WONG_VTEX_APP_TOKEN              VTEX app token

Stores with ``enable_with_credentials: True`` in market_stores.py join the active
catalog when matching credentials are present.
"""

from __future__ import annotations

import os
import re
from typing import Any

from market_stores import STORES

_ENV_PREFIX = "STORE_"
_ENV_KEY = re.compile(r"^STORE_([A-Z0-9_]+)_(MAGENTO_TOKEN|STOREFRONT_TOKEN|VTEX_APP_KEY|VTEX_APP_TOKEN|API_TOKEN)$")


def _env_store_id(raw: str) -> str:
    """Map FALABELLA_PE → falabella_pe."""
    return raw.lower()


def _env_suffix(store_id: str) -> str:
    return store_id.upper().replace("-", "_")


def load_credentials_from_env() -> dict[str, dict[str, str]]:
    """Parse STORE_* env vars into {store_id: {field: value}}."""
    out: dict[str, dict[str, str]] = {}
    for key, value in os.environ.items():
        if not key.startswith(_ENV_PREFIX) or not value.strip():
            continue
        m = _ENV_KEY.match(key)
        if not m:
            continue
        store_id = _env_store_id(m.group(1))
        kind = m.group(2)
        if store_id not in STORES:
            continue
        bucket = out.setdefault(store_id, {})
        if kind == "MAGENTO_TOKEN":
            bucket["magento_token"] = value.strip()
        elif kind == "STOREFRONT_TOKEN":
            bucket["storefront_token"] = value.strip()
        elif kind == "VTEX_APP_KEY":
            bucket["vtex_app_key"] = value.strip()
        elif kind == "VTEX_APP_TOKEN":
            bucket["vtex_app_token"] = value.strip()
        elif kind == "API_TOKEN":
            bucket["api_token"] = value.strip()
    return out


# Loaded once at import; set STORE_CREDENTIALS_RELOAD=1 in tests to refresh.
_CREDENTIALS: dict[str, dict[str, str]] = load_credentials_from_env()


def reload_credentials() -> None:
    """Re-read env (tests only)."""
    global _CREDENTIALS
    _CREDENTIALS = load_credentials_from_env()


def get_store_credentials(store_id: str) -> dict[str, str]:
    return dict(_CREDENTIALS.get(store_id, {}))


def resolve_store_config(store_id: str) -> dict[str, Any]:
    """Base store config merged with runtime credentials (copy, never mutates STORES)."""
    if store_id not in STORES:
        raise KeyError(store_id)
    cfg = dict(STORES[store_id])
    creds = get_store_credentials(store_id)
    if cfg.get("platform") == "need_token":
        cfg["platform"] = "vtex"
    if not creds:
        return cfg

    platform = cfg.get("platform", "vtex")
    generic = creds.get("api_token", "")

    if creds.get("magento_token"):
        cfg["magento_token"] = creds["magento_token"]
    elif platform == "magento" and generic:
        cfg["magento_token"] = generic

    if creds.get("storefront_token"):
        cfg["storefront_token"] = creds["storefront_token"]
    elif platform == "shopify" and generic:
        cfg["storefront_token"] = generic

    if creds.get("vtex_app_key"):
        cfg["vtex_app_key"] = creds["vtex_app_key"]
    if creds.get("vtex_app_token"):
        cfg["vtex_app_token"] = creds["vtex_app_token"]
    elif platform == "vtex" and generic and not cfg.get("vtex_app_token"):
        cfg["vtex_app_token"] = generic

    return cfg


def has_store_credentials(store_id: str) -> bool:
    """True when env provides enough credentials for this store's platform."""
    cfg = STORES.get(store_id, {})
    platform = cfg.get("platform", "vtex")
    creds = get_store_credentials(store_id)
    if not creds:
        return False

    if platform == "magento":
        return bool(creds.get("magento_token") or creds.get("api_token"))
    if platform == "shopify":
        return bool(creds.get("storefront_token") or creds.get("api_token"))
    if platform == "vtex":
        return bool(creds.get("vtex_app_key") and creds.get("vtex_app_token"))
    return bool(creds.get("api_token"))


def compute_default_stores() -> list[str]:
    """Active catalog: enabled stores + credential-gated stores with secrets set."""
    active: list[str] = []
    for store_id, cfg in STORES.items():
        if not cfg.get("disabled"):
            active.append(store_id)
        elif cfg.get("enable_with_credentials") and has_store_credentials(store_id):
            active.append(store_id)
    return active


def credential_summary() -> list[dict[str, Any]]:
    """Non-secret summary for ops/debug."""
    rows: list[dict[str, Any]] = []
    for store_id, cfg in STORES.items():
        creds = get_store_credentials(store_id)
        if not creds:
            continue
        rows.append({
            "store": store_id,
            "platform": cfg.get("platform"),
            "enabled_via_credentials": store_id in compute_default_stores(),
            "fields": sorted(k for k, v in creds.items() if v),
        })
    return rows
