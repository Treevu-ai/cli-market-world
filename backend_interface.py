"""Single import boundary between the public repo and the private backend.

Every symbol the public repo consumes from the private backend (cli-market-backend)
is imported here — once — with a typed fallback stub when the package is absent.

Rules:
  1. No other file should import directly from market_indicators, price_confidence,
     store_credentials, source_health, or retailer_onboarding.
     Import from here instead.
  2. Stubs must match the real signature exactly so type checkers catch drift.
  3. When a stub is active, it either returns a safe neutral value or raises
     HTTPException(503) — never silently corrupts data.

Detecting backend presence: BACKEND_AVAILABLE is True when the package loaded.
"""

from __future__ import annotations

from typing import Any

from fastapi import HTTPException

# ── Availability flag ─────────────────────────────────────────────────────────

BACKEND_AVAILABLE = False

# ── market_indicators ─────────────────────────────────────────────────────────

try:
    from market_indicators import (  # type: ignore[import]
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
    try:
        from market_indicators import get_scores  # type: ignore[import]
        _SCORES_AVAILABLE = True
    except ImportError:
        _SCORES_AVAILABLE = False
        def get_scores(*_a: Any, **_kw: Any) -> Any:  # type: ignore[misc]
            raise HTTPException(503, "Composite scores unavailable (private backend not installed).")
    BACKEND_AVAILABLE = True
except ImportError:
    ENRICHMENT_INDICATOR_KEYS: list[str] = []
    INDICATOR_DEFINITIONS: dict[str, Any] = {}
    _SCORES_AVAILABLE = False

    def compute_internal_inflation_avg(db: Any, country: str | None, line: str | None, days: int = 30) -> float | None:  # type: ignore[misc]
        return None

    def compute_staple_price_momentum(db: Any, country: str | None, days: int = 7) -> float | None:  # type: ignore[misc]
        return None

    def get_indicator_catalog(*_a: Any, **_kw: Any) -> list[dict]:  # type: ignore[misc]
        return []

    def get_latest_values(db: Any, *, country: str | None = None, line: str | None = None, limit: int = 100) -> list[dict]:  # type: ignore[misc]
        return []

    def refresh_after_collection(countries: list[str] | None = None) -> dict[str, Any]:  # type: ignore[misc]
        return {"ok": False, "reason": "backend_unavailable"}

    def refresh_enrichment_only(country: str | None = None) -> dict[str, Any]:  # type: ignore[misc]
        return {"ok": False, "reason": "backend_unavailable"}

    def refresh_indicators(country: str | None = None, line: str | None = None) -> dict[str, int]:  # type: ignore[misc]
        return {}

    def seed_indicator_definitions(db: Any) -> None:  # type: ignore[misc]
        pass

    def get_scores(*_a: Any, **_kw: Any) -> Any:  # type: ignore[misc]
        raise HTTPException(503, "Composite scores unavailable (private backend not installed).")


# ── price_confidence ──────────────────────────────────────────────────────────

try:
    from price_confidence import (  # type: ignore[import]
        compute_snapshot_confidence,
        discount_is_scrape_error,
        spread_confidence,
        spread_public_ok,
    )
except ImportError:
    def compute_snapshot_confidence(price: float, list_price: float | None) -> str:  # type: ignore[misc]
        return "ok"

    def discount_is_scrape_error(discount_pct: float | None) -> bool:  # type: ignore[misc]
        return False

    def spread_confidence(spread_ratio: float) -> str:  # type: ignore[misc]
        return "ok"

    def spread_public_ok(spread_ratio: float) -> bool:  # type: ignore[misc]
        return True


# ── store_credentials ─────────────────────────────────────────────────────────

try:
    from store_credentials import (  # type: ignore[import]
        credential_summary,
        get_default_stores,
        get_store_profile,
        invalidate_credential_cache,
        resolve_store_config,
        store_exists,
    )
    _STORE_CREDENTIALS_AVAILABLE = True
except ImportError:
    _STORE_CREDENTIALS_AVAILABLE = False

    def credential_summary() -> list[dict]:  # type: ignore[misc]
        return []

    def get_default_stores() -> list[str]:  # type: ignore[misc]
        from market_core import STORES
        return list(STORES.keys())

    def get_store_profile(store_id: str) -> dict[str, Any] | None:  # type: ignore[misc]
        return None

    def invalidate_credential_cache() -> None:  # type: ignore[misc]
        pass

    def resolve_store_config(store_id: str) -> dict[str, Any]:  # type: ignore[misc]
        from market_core import STORES
        return STORES.get(store_id, {})

    def store_exists(store_id: str) -> bool:  # type: ignore[misc]
        from market_core import STORES
        return store_id in STORES


# ── source_health ─────────────────────────────────────────────────────────────

try:
    from source_health import build_sources_health  # type: ignore[import]
    _SOURCE_HEALTH_AVAILABLE = True
except ImportError:
    _SOURCE_HEALTH_AVAILABLE = False

    def build_sources_health(db: Any, *, country: str | None = None) -> list[dict]:  # type: ignore[misc]
        return []


# ── retailer_onboarding ───────────────────────────────────────────────────────

try:
    from retailer_onboarding import (  # type: ignore[import]
        approve_retailer_application,
        reject_retailer_application,
        submit_retailer_application,
        token_hint,
    )
    _RETAILER_ONBOARDING_AVAILABLE = True
except ImportError:
    _RETAILER_ONBOARDING_AVAILABLE = False

    def approve_retailer_application(*_a: Any, **_kw: Any) -> dict:  # type: ignore[misc]
        raise HTTPException(503, "Retailer onboarding unavailable (private backend not installed).")

    def reject_retailer_application(*_a: Any, **_kw: Any) -> dict:  # type: ignore[misc]
        raise HTTPException(503, "Retailer onboarding unavailable (private backend not installed).")

    def submit_retailer_application(*_a: Any, **_kw: Any) -> dict:  # type: ignore[misc]
        raise HTTPException(503, "Retailer onboarding unavailable (private backend not installed).")

    def token_hint(store_id: str) -> str:  # type: ignore[misc]
        return ""


# ── data_v1_service ───────────────────────────────────────────────────────────

try:
    from data_v1_service import (  # type: ignore[import]
        build_coverage_matrix,
        count_flagged_outliers,
        intelligence_acceso_examples,
        query_dispersion,
        query_flagged,
        query_prices,
    )
except ImportError:
    def build_coverage_matrix(db: Any, *, line: str | None = None) -> dict:  # type: ignore[misc]
        return {}

    def count_flagged_outliers(db: Any) -> int:  # type: ignore[misc]
        return 0

    def intelligence_acceso_examples(base: str = "") -> list[dict]:  # type: ignore[misc]
        return []

    def query_dispersion(db: Any, *, clean: bool = True, line: str | None = None, currency: str | None = None, limit: int = 50) -> dict:  # type: ignore[misc]
        return {"items": [], "total": 0}

    def query_flagged(db: Any, **_kw: Any) -> dict:  # type: ignore[misc]
        return {"items": [], "total": 0}

    def query_prices(db: Any, *, clean: bool = True, country: str | None = None, line: str | None = None, currency: str | None = None, store: str | None = None, limit: int = 50) -> dict:  # type: ignore[misc]
        return {"items": [], "total": 0}
