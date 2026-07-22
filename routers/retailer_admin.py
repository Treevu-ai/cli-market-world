"""Admin endpoints for retailer application review."""

from __future__ import annotations

import secrets

from fastapi import APIRouter, Header, HTTPException

try:
    from retailer_onboarding import (
        approve_retailer_application,
        db_get_retailer_application,
        db_list_retailer_applications,
        db_public_application,
        guess_store_id,
        reject_retailer_application,
    )
    _RETAILER_ONBOARDING_AVAILABLE = True
except ImportError:
    # retailer_onboarding lives in the private cli-market-backend package.
    # When it's not installed (e.g. local/OSS checkouts), the app must still
    # boot — these admin endpoints return 503 instead of crashing at import.
    _RETAILER_ONBOARDING_AVAILABLE = False

    def _unavailable(*_args, **_kwargs):
        raise HTTPException(
            status_code=503,
            detail="retailer onboarding unavailable (private backend not installed)",
        )

    approve_retailer_application = _unavailable
    db_get_retailer_application = _unavailable
    db_list_retailer_applications = _unavailable
    db_public_application = _unavailable
    guess_store_id = _unavailable
    reject_retailer_application = _unavailable

from market_core import get_db

from server_deps import require_admin
from backend_interface import credential_summary, get_default_stores, invalidate_credential_cache

router = APIRouter(prefix="/admin", tags=["admin-retailers"])


@router.get("/contacts")
def list_contacts(
    limit: int = 100,
    authorization: str | None = Header(None),
):
    require_admin(authorization)
    capped = max(1, min(limit, 500))
    db = get_db()
    rows = db.execute(
        """
        SELECT chat_id, first_name, username, last_message, created_at, updated_at
        FROM contacts
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (capped,),
    ).fetchall()
    db.close()
    contacts = [dict(r) for r in rows]
    return {"contacts": contacts, "count": len(contacts)}


@router.get("/retailer-applications")
def list_retailer_applications(
    status: str | None = "pending",
    authorization: str | None = Header(None),
):
    require_admin(authorization)
    rows = db_list_retailer_applications(status=status or None)
    return {
        "applications": [db_public_application(r) for r in rows],
        "count": len(rows),
    }


@router.get("/retailer-applications/{app_id}")
def get_retailer_application(
    app_id: str,
    authorization: str | None = Header(None),
):
    require_admin(authorization)
    row = db_get_retailer_application(app_id)
    if not row:
        raise HTTPException(status_code=404, detail="application_not_found")
    public = db_public_application(row)
    public["suggested_store_id"] = guess_store_id(
        row.get("website", ""),
        row.get("platform", ""),
        row.get("country", ""),
    )
    return public


@router.post("/retailer-applications/{app_id}/approve")
def approve_application(
    app_id: str,
    body: dict | None = None,
    authorization: str | None = Header(None),
):
    require_admin(authorization)
    payload = body or {}
    try:
        result = approve_retailer_application(
            app_id,
            store_id=(payload.get("store_id") or "").strip() or None,
            magento_token=(payload.get("magento_token") or "").strip(),
            storefront_token=(payload.get("storefront_token") or "").strip(),
            vtex_app_key=(payload.get("vtex_app_key") or "").strip(),
            vtex_app_token=(payload.get("vtex_app_token") or "").strip(),
            line=(payload.get("line") or "supermercados").strip(),
            review_notes=(payload.get("review_notes") or payload.get("notes") or "").strip(),
        )
    except ValueError as e:
        code = str(e)
        if code == "application_not_found":
            raise HTTPException(status_code=404, detail=code) from e
        if code.startswith("application_not_pending"):
            raise HTTPException(status_code=409, detail=code) from e
        if code == "credentials_required_for_platform":
            raise HTTPException(
                status_code=400,
                detail="Magento/Shopify require api_token on apply or token fields in approve body",
            ) from e
        if code == "website_or_credentials_required":
            raise HTTPException(
                status_code=400,
                detail="VTEX public stores need website URL or VTEX app credentials",
            ) from e
        raise HTTPException(status_code=400, detail=code) from e

    invalidate_credential_cache()
    result["active_catalog_size"] = len(get_default_stores())
    return result


@router.post("/retailer-applications/{app_id}/reject")
def reject_application(
    app_id: str,
    body: dict | None = None,
    authorization: str | None = Header(None),
):
    require_admin(authorization)
    payload = body or {}
    try:
        return reject_retailer_application(
            app_id,
            review_notes=(payload.get("review_notes") or payload.get("notes") or "").strip(),
        )
    except ValueError as e:
        code = str(e)
        if code == "application_not_found":
            raise HTTPException(status_code=404, detail=code) from e
        if code.startswith("application_not_pending"):
            raise HTTPException(status_code=409, detail=code) from e
        raise HTTPException(status_code=400, detail=code) from e


@router.get("/store-credentials")
def list_store_credentials(authorization: str | None = Header(None)):
    require_admin(authorization)
    return {
        "credentials": credential_summary(),
        "active_catalog_size": len(get_default_stores()),
    }


@router.post("/stores/{store_id}/activate-growth")
def activate_growth(store_id: str, authorization: str | None = Header(None)):
    """Flip a store into the paid Growth tier ($9/mo).

    Called manually by the team after matching a Retailer Growth checkout's
    free-text email/store_name (see routers/billing/activation.py's
    _activate_retailer_growth_from_request, which only marks the billing
    request activated and Slack-notifies — it has no store_id to act on).
    Same manual-match pattern already used for retailer-application approval.
    """
    require_admin(authorization)
    db = get_db()
    try:
        row = db.execute(
            "SELECT store_id FROM store_credentials WHERE store_id = ?", (store_id,)
        ).fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="store_not_found")
        token = secrets.token_urlsafe(24)
        db.execute(
            "UPDATE store_credentials SET is_growth = 1, growth_dashboard_token = ?, "
            "growth_activated_at = datetime('now'), updated_at = datetime('now') "
            "WHERE store_id = ?",
            (token, store_id),
        )
        db.commit()
    finally:
        db.close()
    invalidate_credential_cache()
    return {"store_id": store_id, "is_growth": True, "dashboard_token": token}


@router.get("/stores/{store_id}/growth-status")
def growth_status(store_id: str, authorization: str | None = Header(None)):
    require_admin(authorization)
    db = get_db()
    try:
        row = db.execute(
            "SELECT store_id, is_growth, growth_activated_at FROM store_credentials WHERE store_id = ?",
            (store_id,),
        ).fetchone()
    finally:
        db.close()
    if not row:
        raise HTTPException(status_code=404, detail="store_not_found")
    r = dict(row)
    return {
        "store_id": r["store_id"],
        "is_growth": bool(r.get("is_growth")),
        "growth_activated_at": r.get("growth_activated_at"),
    }
