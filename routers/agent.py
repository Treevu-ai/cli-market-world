"""Agent-shaped endpoints — natural-language intent → action mapping + per-user prefs.

Endpoints:
  GET  /agent/preferences  User's order patterns (favorite stores, spend)
  POST /agent/ask          Natural-language → structured action ({action, query, ...})

This is the simplest possible natural-language layer; it intentionally does
NOT call an LLM. The action mapping is a finite-state classifier suitable
for an MCP-tool dispatch where the LLM is on the caller side.
"""

from __future__ import annotations

import re

from fastapi import APIRouter, Header
from pydantic import BaseModel

from market_core import db_get_orders
from server_deps import require_pro, require_user

router = APIRouter(tags=["agent"])

# Kept in sync with routers/integrations/telegram.py's _COUNTRY_HINTS.
_COUNTRY_HINTS = {
    "peru": "PE", "perú": "PE",
    "colombia": "CO",
    "mexico": "MX", "méxico": "MX",
    "argentina": "AR",
    "chile": "CL",
    "brasil": "BR", "brazil": "BR",
}

# "canasta" alone also matches single-SKU products like "canasta de frutas";
# requiring one of these companion words is what marks it as a basic-basket
# (multi-item) request instead of a single-product compare.
_BASKET_QUALIFIERS = ("basica", "básica", "familiar", "combinacion", "combinación")


class AskRequest(BaseModel):
    prompt: str


@router.get("/agent/preferences")
def agent_preferences(authorization: str | None = Header(None)):
    """Order history → favorite stores + total spent. Used by the CLI to
    personalize results."""
    username = require_user(authorization)
    user_orders = db_get_orders(username)
    stores: dict[str, float] = {}
    total_spent = 0.0
    for o in user_orders:
        total_spent += o.get("total", 0)
        for item in o.get("items", []):
            s = item.get("store_name", "?")
            stores[s] = stores.get(s, 0) + item.get("price", 0) * item.get("quantity", 1)
    return {
        "username": username,
        "total_orders": len(user_orders),
        "total_spent": round(total_spent, 2),
        "favorite_stores": sorted(stores.items(), key=lambda x: x[1], reverse=True)[:3],
    }


@router.post("/agent/ask")
async def agent_ask(body: AskRequest, authorization: str | None = Header(None)):
    """Map a natural-language prompt to a structured action dict.

    Action vocabulary: search, reorder, compare, cart, checkout.
    The MCP server uses this for chat-style intent dispatch.
    """
    require_pro(authorization)
    prompt = body.prompt.lower().strip()
    if any(w in prompt for w in ("compra", "comprar", "agregar", "add")):
        words = re.sub(r"[^a-záéíóúñ ]", "", prompt).split()
        qty = 1
        for w in words:
            if w.isdigit():
                qty = int(w)
                break
        query = (
            prompt.replace("compra", "")
            .replace("comprar", "")
            .replace("agrega", "")
            .replace("agregar", "")
            .replace("add", "")
            .strip()
        )
        return {"action": "search", "query": query, "quantity": qty, "message": f"Buscando '{query}'..."}
    if any(w in prompt for w in ("repite", "repetir", "reorder")):
        return {"action": "reorder", "message": "Repitiendo última orden..."}
    if any(w in prompt for w in ("compara", "comparar", "compare")):
        query = prompt.replace("compara", "").replace("comparar", "").replace("compare", "").strip()
        # "canasta basica" / "canasta familiar" are multi-item basket
        # requests, not a single product to fuzzy-match by name. Routing
        # these through /products/compare fed the whole free-text sentence
        # as a search string and matched unrelated products on generic
        # words like "canasta" or "para" (e.g. "Canastilla de Acero",
        # "CHOCOLATE PARA TAZA"). Route to the canonical canasta básica
        # snapshot (GET /v1/basket) instead.
        if "canasta" in query and any(w in query for w in _BASKET_QUALIFIERS):
            country = next((code for name, code in _COUNTRY_HINTS.items() if name in query), None)
            message = "Comparando canasta básica" + (f" ({country})" if country else "") + "..."
            result: dict = {"action": "basket", "message": message}
            if country:
                result["country"] = country
            return result
        return {"action": "compare", "query": query, "message": f"Comparando '{query}'..."}
    if any(w in prompt for w in ("carrito", "cart", "ver")):
        return {"action": "cart", "message": "Mostrando carrito..."}
    if any(w in prompt for w in ("pagar", "checkout", "finalizar")):
        return {"action": "checkout", "message": "Iniciando checkout..."}
    return {"action": "search", "query": prompt, "quantity": 1, "message": f"Buscando '{prompt}'..."}
