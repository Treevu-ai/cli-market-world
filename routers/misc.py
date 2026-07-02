"""Endpoints that don't fit a bigger domain.

Endpoints:
  POST /favorites             Add/remove/list user favorite products
  POST /v1/utils/exchange     Static currency conversion
  POST /telegram/webhook      Telegram bot inbound webhook (messages + inline queries)
"""

from __future__ import annotations

import os
import uuid

import httpx
from fastapi import APIRouter, Header, HTTPException, Request

from market_core import COUNTRIES, FX_PEN_PER_UNIT, LINES, STORES, convert_currency, get_db
from market_core.market_mcp_registry import public_tool_count
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


TELEGRAM_COMMANDS = [
    {"command": "start", "description": "Bienvenida y lista de comandos"},
    {"command": "search", "description": "Buscar precios — ej. /search leche"},
    {"command": "status", "description": "Estado de la plataforma"},
    {"command": "coverage", "description": "Cobertura por línea y país"},
    {"command": "pricing", "description": "Planes y acceso"},
    {"command": "docs", "description": "Documentación y API"},
    {"command": "help", "description": "Ayuda"},
]


async def register_telegram_commands() -> bool:
    """Register the native Telegram command menu. Idempotent — safe to call on every startup."""
    if not TELEGRAM_TOKEN:
        return False
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/setMyCommands",
                json={"commands": TELEGRAM_COMMANDS},
            )
            return r.status_code == 200
    except Exception:
        return False


async def _answer_inline_query(inline_query_id: str, results: list[dict]) -> bool:
    if not TELEGRAM_TOKEN:
        return False
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(
                f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/answerInlineQuery",
                json={"inline_query_id": inline_query_id, "results": results, "cache_time": 30},
            )
            return r.status_code == 200
    except Exception:
        return False


def _inline_price_results(query: str) -> list[dict]:
    """Build InlineQueryResultArticle list for `@climarketbot <product>` in any chat."""
    db = get_db()
    rows = db.execute(
        "SELECT * FROM price_snapshots WHERE name LIKE ? ORDER BY queried_at DESC LIMIT 10",
        (f"%{query}%",),
    ).fetchall()
    db.close()
    results = []
    for r in rows:
        text = f"\U0001f50d <b>{r['name']}</b>\n{r['store_name']} — {r['currency']} {r['price']}\n\nVía @climarketbot — t.me/climarketbot"
        results.append(
            {
                "type": "article",
                "id": str(uuid.uuid4()),
                "title": r["name"],
                "description": f"{r['store_name']} — {r['currency']} {r['price']}",
                "input_message_content": {"message_text": text, "parse_mode": "HTML"},
            }
        )
    return results


@router.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    """Webhook endpoint registered in @BotFather → receives Telegram updates."""
    if not TELEGRAM_TOKEN:
        return {"status": "disabled", "hint": "Set TELEGRAM_BOT_TOKEN env var"}
    try:
        body = await request.json()
    except Exception:
        return {"status": "invalid_json"}

    inline_query = body.get("inline_query")
    if inline_query:
        query = (inline_query.get("query") or "").strip()
        inline_query_id = inline_query.get("id", "")
        results = _inline_price_results(query) if query else []
        await _answer_inline_query(inline_query_id, results)
        return {"status": "ok", "inline_results": len(results)}

    message = body.get("message", {})
    chat = message.get("chat", {})
    text = (message.get("text") or "").strip().lower()
    if text.startswith("/"):
        parts = text.split(maxsplit=1)
        parts[0] = parts[0].split("@")[0]
        text = " ".join(parts)
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
            f"\u2022 {public_tool_count('default')} MCP tools "
            f"(default; {public_tool_count('legacy')} legacy)\n"
            "\u2022 API: cli-market-api.fly.dev\n"
            "\u2022 Pro: cli-market.dev/#pricing"
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
            "<b>Planes CLI Market:</b>\n"
            "\u2022 Free: 1,000 req/día — pip install cli-market-world\n"
            "\u2022 Starter: $9/mes — 5,000 req/día, export CSV, 3 alertas\n"
            "\u2022 Pro: $49/mes — checkout, MCP completo, 10 alertas\n"
            "\u2022 Enterprise: hello@cli-market.dev\n\n"
            "Detalle: cli-market.dev/#pricing\n"
            "Docs: cli-market.dev/docs"
        )
    elif text in ("/docs", "docs", "api"):
        reply = (
            "<b>Documentación:</b>\n"
            "\u2022 Swagger: cli-market-api.fly.dev/docs\n"
            "\u2022 llms.txt: cli-market.dev/llms.txt\n"
            "\u2022 Docs: cli-market.dev/docs"
        )
    elif text in ("/help", "help", "ayuda"):
        reply = (
            "<b>Comandos disponibles:</b>\n"
            "/search [producto] \u2014 buscar precios, ej. /search leche\n"
            "/status \u2014 estado de la plataforma\n"
            "/coverage \u2014 cobertura por l\u00ednea y pa\u00eds\n"
            "/pricing \u2014 planes y acceso\n"
            "/docs \u2014 documentaci\u00f3n y API\n\n"
            "Tambi\u00e9n puedes escribir <code>@climarketbot producto</code> en cualquier chat."
        )
    else:
        reply = "<b>CLI Market Bot</b>\n\nComandos: /search /status /coverage /pricing /docs /help"
    await _send_telegram(chat_id, reply)
    return {"status": "ok", "reply": reply[:100]}
