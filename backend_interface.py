"""Thin adapter over cli-market-core.

Historically this module was the single import boundary between the public repo
and a private backend, re-exporting every consumed symbol with a stub fallback.
The data-moat modules now live in the **cli-market-core** package — a hard
dependency of the web tier — so this is a thin re-export shim, kept only so the
existing ``from backend_interface import X`` call sites across the web tier keep
working unchanged.

Two symbols never shipped in the shared core (they were private-backend-only):
``get_scores`` (composite scores) and ``submit_retailer_application``. They stay
as 503 stubs so those endpoints degrade gracefully instead of failing at import.
"""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException

# The shared core is a hard dependency now: a missing import should fail loudly
# at startup rather than silently degrade. These flags are kept True for the
# call sites (routers/search.py, routers/health.py) that still read them.
BACKEND_AVAILABLE = True
_STORE_CREDENTIALS_AVAILABLE = True
_SOURCE_HEALTH_AVAILABLE = True
_RETAILER_ONBOARDING_AVAILABLE = True

from market_indicators import (
    ENRICHMENT_INDICATOR_KEYS,
    INDICATOR_DEFINITIONS,
    compute_internal_inflation_avg,
    compute_staple_price_momentum,
    get_indicator_catalog,
    get_latest_values,
    refresh_after_collection,
    refresh_enrichment_only,
    refresh_indicators,
    seed_indicator_definitions,
)
from price_confidence import (
    compute_snapshot_confidence,
    discount_is_scrape_error,
    spread_confidence,
    spread_public_ok,
)
from store_credentials import (
    credential_summary,
    get_default_stores,
    get_store_profile,
    invalidate_credential_cache,
    resolve_store_config,
    store_exists,
)
from source_health import build_sources_health
from retailer_onboarding import (
    approve_retailer_application,
    reject_retailer_application,
    token_hint,
)
from data_v1_service import (
    build_coverage_matrix,
    count_flagged_outliers,
    intelligence_acceso_examples,
    query_dispersion,
    query_flagged,
    query_prices,
)

# ── Symbols that never shipped in the shared core ─────────────────────────────
# These were private-backend-only; keep them as 503 stubs so the affected
# endpoints respond cleanly instead of crashing at import.

_SCORES_AVAILABLE = False


def get_scores(*_a: Any, **_kw: Any) -> Any:
    raise HTTPException(503, "Composite scores unavailable (not part of the shared core).")


def submit_retailer_application(*_a: Any, **_kw: Any) -> dict:
    raise HTTPException(503, "Retailer self-serve submission unavailable (not part of the shared core).")


__all__ = [
    "BACKEND_AVAILABLE",
    "_SCORES_AVAILABLE",
    "_STORE_CREDENTIALS_AVAILABLE",
    "_SOURCE_HEALTH_AVAILABLE",
    "_RETAILER_ONBOARDING_AVAILABLE",
    # market_indicators
    "ENRICHMENT_INDICATOR_KEYS",
    "INDICATOR_DEFINITIONS",
    "compute_internal_inflation_avg",
    "compute_staple_price_momentum",
    "get_indicator_catalog",
    "get_latest_values",
    "refresh_after_collection",
    "refresh_enrichment_only",
    "refresh_indicators",
    "seed_indicator_definitions",
    "get_scores",
    # price_confidence
    "compute_snapshot_confidence",
    "discount_is_scrape_error",
    "spread_confidence",
    "spread_public_ok",
    # store_credentials
    "credential_summary",
    "get_default_stores",
    "get_store_profile",
    "invalidate_credential_cache",
    "resolve_store_config",
    "store_exists",
    # source_health
    "build_sources_health",
    # retailer_onboarding
    "approve_retailer_application",
    "reject_retailer_application",
    "submit_retailer_application",
    "token_hint",
    # data_v1_service
    "build_coverage_matrix",
    "count_flagged_outliers",
    "intelligence_acceso_examples",
    "query_dispersion",
    "query_flagged",
    "query_prices",
]
