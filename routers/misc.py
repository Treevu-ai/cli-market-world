"""Endpoints that don't fit a bigger domain.

Endpoints:
  POST /favorites             Add/remove/list user favorite products
  POST /v1/utils/exchange     Static currency conversion
  POST /telegram/webhook      Telegram bot inbound webhook
"""

from __future__ import annotations

import os

import httpx
from fastapi import APIRouter, Header, HTTPException, Request

from market_core import COUNTRIES, LINES, STORES, get_db
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

# Static rates in PEN-equivalent. For live rates use /checkout/rates (Wise-backed).
_FX_RATES = {
    "PEN": 1.0,
    "ARS": 0.0027,
    "BRL": 1.02,
    "MXN": 0.29,
    "COP": 0.0013,
    "CLP": 0.0053,
    "EUR": 4.05,
    "USD": 3.70,
}


@router.post("/v1/utils/exchange")
def utils_exchange(body: dict):
    """Static currency conversion. Use /checkout/rates for live Wise rates."""
    amount = body.get("amount", 0)
    frm = body.get("from", "PEN").upper()
    to = body.get("to", "PEN").upper()
    if frm not in _FX_RATES or to not in _FX_RATES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported currency. Supported: {list(_FX_RATES.keys())}",
        )
    converted = round(amount * _FX_RATES[to] / _FX_RATES[frm], 2)
    return {
        "amount": amount,
        "from": frm,
        "to": to,
        "converted": converted,
        "rate": round(_FX_RATES[to] / _FX_RATES[frm], 6),
    }


# ── Telegram bot webhook ──────────────────────────────────────────────────────

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


async def _send_telegram(chat_id: str, text: str) -> bool:
    if not TELEGRAM_TOKEN:
        return False
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
                json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"},
            )
            return r.status_code == 200
    except Exception:
        return False


@router.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    """Webhook endpoint registered in @BotFather → receives Telegram updates."""
    if not TELEGRAM_TOKEN:
        return {"status": "disabled", "hint": "Set TELEGRAM_BOT_TOKEN env var"}
    try:
        body = await request.json()
    except Exception:
        return {"status": "invalid_json"}
    message = body.get("message", {})
    chat = message.get("chat", {})
    text = (message.get("text") or "").strip().lower()
    chat_id = str(chat.get("id", ""))
    first_name = chat.get("first_name", "")
    if not text or not chat_id:
        return {"status": "no_message"}
    try:
        db = get_db()
        db.execute(
            "INSERT OR REPLACE INTO contacts (chat_id, first_name, username, last_message, created_at) "
            "VALUES (?,?,?,?,datetime('now'))",
            (chat_id, first_name, chat.get("username", ""), text),
        )
        db.commit()
        db.close()
    except Exception:
        pass

    if text in ("/start", "hola", "hi", "hello"):
        reply = (
            f"Hola <b>{first_name}</b> \U0001f44b\n\n"
            "Soy el bot de <b>CLI Market</b> — infraestructura de comercio para agentes de IA.\n\n"
            "<b>Comandos:</b>\n"
            "/search leche — buscar productos\n"
            "/status — estado\n"
            "/coverage — cobertura\n"
            "/pricing — acceso\n"
            "/docs — docs\n"
            "/help — ayuda"
        )
    elif text.startswith("/search") or text.startswith("buscar"):
        query = text.replace("/search", "").replace("buscar", "").strip() or "leche"
        reply = f"\U0001f50d <b>Buscando:</b> {query}\n\n"
        try:
            db_q = get_db()
            rows = db_q.execute(
                "SELECT * FROM price_snapshots WHERE name LIKE ? "
                "ORDER BY queried_at DESC LIMIT 5",
                (f"%{query}%",),
            ).fetchall()
            db_q.close()
            if rows:
                for r in rows:
                    reply += f"\u2022 <b>{r['name']}</b>\n  {r['store_name']} — {r['currency']} {r['price']}\n"
                reply += f"\n{len(rows)} resultados del data moat."
            else:
                reply += "No hay datos todavía."
        except Exception:
            reply += "Error consultando."
    elif text.startswith("/status") or text == "status":
        reply = (
            f"<b>CLI Market</b> — ONLINE\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n"
            f"\u2022 {len(STORES)} retailers en {len(LINES)} líneas\n"
            f"\u2022 {len(COUNTRIES)} países\n"
            "\u2022 12 MCP tools\n"
            "\u2022 API: cli-market-api.onrender.com"
        )
    elif text.startswith("/coverage") or text in ("coverage", "cobertura"):
        reply = "<b>Cobertura por línea:</b>\n"
        for lk in LINES:
            c = sum(1 for v in STORES.values() if v["line"] == lk)
            reply += f"{LINES[lk]['emoji']} {LINES[lk]['name']}: {c}\n"
        reply += "\n<b>Por pais:</b>\n"
        for _ck, cv in COUNTRIES.items():
            reply += f"{cv['name']}: {len(cv['stores'])}\n"
    elif text in ("/pricing", "pricing", "precio", "costo"):
        reply = (
            "<b>Acceso:</b>\n"
            "\u2022 CLI: open source (MIT)\n"
            "\u2022 API: free tier (10/min, 100/día)\n"
            "\u2022 Planes pagos: pronto\n\n"
            "Repo: github.com/Treevu-ai/cli-market-latam"
        )
    elif text in ("/docs", "docs", "api"):
        reply = (
            "<b>Documentación:</b>\n"
            "\u2022 Swagger: /docs\n"
            "\u2022 llms.txt: cli-market.dev/llms.txt\n"
            "\u2022 README: github.com/Treevu-ai/cli-market-latam"
        )
    else:
        reply = "<b>CLI Market Bot</b>\n\nComandos: /search /status /coverage /pricing /docs /help"
    await _send_telegram(chat_id, reply)
    return {"status": "ok", "reply": reply[:100]}
