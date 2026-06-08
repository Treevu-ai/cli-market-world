"""Procure Copilot tiers on CLI Market billing (Phase B)."""

from __future__ import annotations

import os
from typing import Any

# CLI Market subscription tier names (stored in subscriptions.tier)
PROCURE_TIER_STARTER = "procure_starter"
PROCURE_TIER_PRO = "procure_pro"
PROCURE_TIER_BUILDER = "procure_builder"

PROCURE_TIERS = frozenset({PROCURE_TIER_STARTER, PROCURE_TIER_PRO, PROCURE_TIER_BUILDER})

# Landing / PayPal plan slug → CLI Market tier
PROCURE_PLANS: dict[str, dict[str, Any]] = {
    "starter": {
        "tier": PROCURE_TIER_STARTER,
        "amount": 29.0,
        "label": "Procure Starter",
        "paypal_env": "PAYPAL_PROCURE_STARTER_PLAN_ID",
        "request_prefix": "PCS",
    },
    "pro": {
        "tier": PROCURE_TIER_PRO,
        "amount": 79.0,
        "label": "Procure Pro",
        "paypal_env": "PAYPAL_PROCURE_PRO_PLAN_ID",
        "request_prefix": "PCP",
    },
    "builder": {
        "tier": PROCURE_TIER_BUILDER,
        "amount": 149.0,
        "label": "Procure Builder",
        "paypal_env": "PAYPAL_PROCURE_BUILDER_PLAN_ID",
        "request_prefix": "PCB",
    },
}

# Minimal API limits bundled with Procure (infra included — not sold as Build Pro)
PROCURE_TIER_LIMITS: dict[str, dict[str, Any]] = {
    PROCURE_TIER_STARTER: {
        "req_min": 120,
        "req_day": 5_000,
        "api_keys": 3,
        "checkout": False,
        "alerts": 0,
        "export": False,
        "history_days": 7,
    },
    PROCURE_TIER_PRO: {
        "req_min": 300,
        "req_day": 10_000,
        "api_keys": 5,
        "checkout": True,
        "alerts": 10,
        "export": True,
        "history_days": 365,
    },
    PROCURE_TIER_BUILDER: {
        "req_min": 600,
        "req_day": 50_000,
        "api_keys": 10,
        "checkout": True,
        "alerts": -1,
        "export": True,
        "history_days": -1,
    },
}


def is_procure_tier(tier: str) -> bool:
    return (tier or "").lower() in PROCURE_TIERS


def tier_to_procure_plan(tier: str) -> str | None:
    """Map CLI Market tier → Procure app plan slug."""
    mapping = {
        PROCURE_TIER_STARTER: "starter",
        PROCURE_TIER_PRO: "pro",
        PROCURE_TIER_BUILDER: "builder",
    }
    return mapping.get((tier or "").lower())


def resolve_tier_config(tier: str, default: dict[str, Any]) -> dict[str, Any]:
    return PROCURE_TIER_LIMITS.get((tier or "").lower(), default)


def all_valid_tiers(base_tiers: dict) -> frozenset[str]:
    return frozenset(base_tiers.keys()) | PROCURE_TIERS


def procure_plan_config(plan_slug: str) -> dict[str, Any]:
    key = (plan_slug or "").strip().lower()
    if key not in PROCURE_PLANS:
        raise ValueError(f"plan must be one of {sorted(PROCURE_PLANS)}")
    cfg = dict(PROCURE_PLANS[key])
    cfg["paypal_plan_id"] = os.getenv(cfg["paypal_env"], "")
    return cfg