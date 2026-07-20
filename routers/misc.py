"""Endpoints that don't fit a bigger domain.

Endpoints:
  POST /favorites             Add/remove/list user favorite products
  POST /v1/utils/exchange     Static currency conversion
  POST /telegram/webhook      (Deprecated) Telegram bot inbound webhook
"""

from __future__ import annotations


from fastapi import APIRouter, Header, HTTPException, Request

from market_core import FX_PEN_PER_UNIT, convert_currency, get_db
from server_deps import require_user

router = APIRouter(tags=["misc"])


# ── Favorites ─────────────────────────────────────────────────────────────────

@router.post("/favorites")
def favorites(body: dict, authorization: str | None = Header(None)):
    """Manage favorite products. action ∈ {'list', 'add', 'remove'}."""
    username = require_user(authorization)
    action = body.get("action", "list")
    db = get_db()
    if action == "add":
        db.execute(
            "INSERT OR IGNORE INTO app_favorites (username, product_id, name, store) VALUES (?,?,?,?)",
            (
                username,
                body.get("product_id", ""),
                body.get("name", ""),
                body.get("store", ""),
            ),
        )
        db.commit()
    elif action == "remove":
        db.execute(
            "DELETE FROM app_favorites WHERE username=? AND product_id=?",
            (username, body.get("product_id", "")),
        )
        db.commit()
    rows = db.execute(
        "SELECT product_id, name, store FROM app_favorites WHERE username=? ORDER BY product_id",
        (username,),
    ).fetchall()
    db.close()
    return {"favorites": [dict(r) for r in rows], "total": len(rows)}


# ── Currency conversion (static table) ────────────────────────────────────────

@router.post("/v1/utils/exchange")
def utils_exchange(body: dict):
    """Static currency conversion. Use /checkout/rates for live Wise rates."""
    amount = body.get("amount", 0)
    frm = body.get("from", "PEN").upper()
    to = body.get("to", "PEN").upper()
    if frm not in FX_PEN_PER_UNIT or to not in FX_PEN_PER_UNIT:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported currency. Supported: {list(FX_PEN_PER_UNIT.keys())}",
        )
    try:
        converted = round(convert_currency(float(amount), frm, to), 2)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid amount")
    return {
        "amount": amount,
        "from": frm,
        "to": to,
        "converted": converted,
        "rate": round(convert_currency(1.0, frm, to), 6),
    }


# ── Telegram bot webhook (DEPRECATED) ─────────────────────────────────────────
# Moved to routers/integrations/telegram.py

@router.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    return {"status": "moved", "new_endpoint": "/v1/integrations/telegram/webhook"}
