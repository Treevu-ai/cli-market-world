#!/usr/bin/env python3
"""
market-server — Agentic Market backend.

FastAPI que expone búsqueda real en Wong/Metro/Plaza Vea,
carrito, checkout y órdenes. Todo accionable vía CLI, API o agente IA.

Ejecutar:
    python market_server.py
    → http://localhost:8765
    → http://localhost:8765/docs
"""

import asyncio
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Header, Body
from pydantic import BaseModel

# ── Config ─────────────────────────────────────────────────────────────────

DATA_DIR = Path.home() / ".market"
DATA_DIR.mkdir(exist_ok=True)
USERS_FILE = DATA_DIR / "users.json"
CARTS_FILE = DATA_DIR / "carts.json"
ORDERS_FILE = DATA_DIR / "orders.json"
SESSION_FILE = DATA_DIR / "session.json"

STORES = {
    "wong":      {"name": "Wong",       "base": "https://www.wong.pe",          "country": "PE", "currency": "PEN", "emoji": "🇵🇪"},
    "metro":     {"name": "Metro",      "base": "https://www.metro.pe",         "country": "PE", "currency": "PEN", "emoji": "🇵🇪"},
    "plazavea":  {"name": "Plaza Vea",  "base": "https://www.plazavea.com.pe",  "country": "PE", "currency": "PEN", "emoji": "🇵🇪"},
    "carrefour": {"name": "Carrefour",  "base": "https://www.carrefour.com.ar", "country": "AR", "currency": "ARS", "emoji": "🇦🇷"},
    "jumbo_ar":  {"name": "Jumbo",      "base": "https://www.jumbo.com.ar",     "country": "AR", "currency": "ARS", "emoji": "🇦🇷"},
    "carrefour_br": {"name": "Carrefour", "base": "https://www.carrefour.com.br", "country": "BR", "currency": "BRL", "emoji": "🇧🇷"},
    "chedraui":  {"name": "Chedraui",   "base": "https://www.chedraui.com.mx", "country": "MX", "currency": "MXN", "emoji": "🇲🇽"},
    "heb":       {"name": "HEB",        "base": "https://www.heb.com.mx",       "country": "MX", "currency": "MXN", "emoji": "🇲🇽"},
    "olimpica":  {"name": "Olímpica",   "base": "https://www.olimpica.com",     "country": "CO", "currency": "COP", "emoji": "🇨🇴"},
}

COUNTRIES = {
    "PE": {"name": "Perú", "stores": ["wong", "metro", "plazavea"]},
    "AR": {"name": "Argentina", "stores": ["carrefour", "jumbo_ar"]},
    "BR": {"name": "Brasil", "stores": ["carrefour_br"]},
    "MX": {"name": "México", "stores": ["chedraui", "heb"]},
    "CO": {"name": "Colombia", "stores": ["olimpica"]},
}
DEFAULT_STORES = list(STORES.keys())
PAGE_SIZE = 20

app = FastAPI(
    title="Agentic Market API",
    description="AI-native supermarket infrastructure — 8 stores across 5 LATAM countries.",
    version="1.0.0",
)


# ── Persistencia ───────────────────────────────────────────────────────────

def load_json(path: Path, default: Any) -> Any:
    if path.exists():
        return json.loads(path.read_text())
    return default


def save_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, indent=2, default=str))


def get_users() -> dict:
    if not USERS_FILE.exists():
        default = {"admin": {"password": "market", "token": str(uuid.uuid4())}}
        save_json(USERS_FILE, default)
        return default
    return load_json(USERS_FILE, {})


def get_carts() -> dict:
    return load_json(CARTS_FILE, {})


def get_orders() -> list:
    return load_json(ORDERS_FILE, [])


# ── Auth ───────────────────────────────────────────────────────────────────

def auth_user(token: str) -> str:
    users = get_users()
    for username, data in users.items():
        if data.get("token") == token:
            return username
    raise HTTPException(status_code=401, detail="Token inválido. Usá 'market login'.")


# ── VTEX Search ────────────────────────────────────────────────────────────

def parse_price(price: Any) -> float:
    try:
        return float(price or 0)
    except (ValueError, TypeError):
        return 0.0


def clean_name(name: str) -> str:
    return name.replace("-", " ")


async def fetch_store(store: str, term: str, page: int = 1, limit: int = PAGE_SIZE) -> list[dict]:
    base = STORES[store]["base"]
    url = f"{base}/api/catalog_system/pub/products/search/{term}"
    _from = (page - 1) * PAGE_SIZE
    _to = min(_from + limit - 1, _from + PAGE_SIZE - 1)
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url, params={"_from": str(_from), "_to": str(_to)})
        resp.raise_for_status()
        return resp.json()


def product_from_json(p: dict, store: str) -> dict:
    items = p.get("items", [])
    item = items[0] if items else {}
    sellers = item.get("sellers", [])
    seller = sellers[0] if sellers else {}
    offer = seller.get("commertialOffer", {})
    price = parse_price(offer.get("Price"))
    list_price = parse_price(offer.get("ListPrice"))
    discount = round((1 - price / list_price) * 100) if list_price > price > 0 else None

    return {
        "id": p.get("productReference", p.get("productId", "")),
        "name": clean_name(p.get("productName", "")),
        "brand": p.get("brand") or "—",
        "category": p.get("categoryId", ""),
        "price": price,
        "list_price": list_price,
        "discount": discount,
        "stock": offer.get("AvailableQuantity", 0),
        "store": store,
        "store_name": STORES[store]["name"],
        "url": f"{STORES[store]['base']}/{p.get('linkText', '')}/p",
    }


# ── Schemas ────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str


class SearchRequest(BaseModel):
    query: str
    store: str | None = None
    page: int = 1
    limit: int = PAGE_SIZE


class AddToCartRequest(BaseModel):
    product_id: str
    name: str
    price: float
    store: str
    quantity: int = 1
    url: str = ""


class UpdateCartRequest(BaseModel):
    product_id: str
    quantity: int


class CheckoutRequest(BaseModel):
    payment_method: str = "yape"


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name": "Agentic Market",
        "status": "running",
        "stores": len(STORES),
        "countries": len(COUNTRIES),
        "docs": "/docs",
    }


@app.get("/stores")
def list_stores(country: str | None = None):
    """Lista todas las tiendas. Filtrar por país con ?country=PE."""
    result = {}
    for key, s in STORES.items():
        if country and s["country"] != country.upper():
            continue
        result[key] = {
            "name": s["name"],
            "country": s["country"],
            "currency": s["currency"],
            "base": s["base"],
        }
    return {"stores": result, "total": len(result)}


@app.get("/countries")
def list_countries():
    return {
        "countries": {
            code: {"name": c["name"], "stores": c["stores"], "count": len(c["stores"])}
            for code, c in COUNTRIES.items()
        }
    }


@app.post("/auth/login")
def login(body: LoginRequest):
    users = get_users()
    user = users.get(body.username)
    if not user or user["password"] != body.password:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    if "token" not in user or not user["token"]:
        user["token"] = str(uuid.uuid4())
        save_json(USERS_FILE, users)
    save_json(SESSION_FILE, {"username": body.username, "token": user["token"]})
    return {"message": "Autenticado", "username": body.username, "token": user["token"]}


@app.get("/auth/whoami")
def whoami(authorization: str | None = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Sin token")
    token = authorization.replace("Bearer ", "")
    username = auth_user(token)
    return {"username": username}


@app.post("/products/search")
async def search_products(body: SearchRequest, authorization: str | None = Header(None)):
    stores = [body.store] if body.store else DEFAULT_STORES
    stores = [s for s in stores if s in STORES]
    results = []
    for store in stores:
        try:
            raw = await fetch_store(store, body.query, body.page, body.limit)
            for p in raw:
                results.append(product_from_json(p, store))
        except Exception:
            continue
    results.sort(key=lambda p: p["price"] if p["price"] > 0 else float("inf"))
    return {"query": body.query, "results": results, "total": len(results)}


@app.post("/products/compare")
async def compare_products(body: SearchRequest):
    stores = [body.store] if body.store else DEFAULT_STORES
    stores = [s for s in stores if s in STORES]
    all_raw = {}
    for store in stores:
        try:
            all_raw[store] = await fetch_store(store, body.query, body.page, body.limit)
        except Exception:
            all_raw[store] = []

    all_products = {s: [product_from_json(p, s) for p in raw] for s, raw in all_raw.items()}

    def match_key(p: dict) -> str:
        name = re.sub(r"[^a-záéíóúñ0-9]", "", p["name"].lower())
        return f"{p['brand'].lower()}|{name}"

    # ── Paso 1: exact match por marca + nombre ──
    key_index: dict[str, dict] = {}
    for store, prods in all_products.items():
        for p in prods:
            k = match_key(p)
            key_index.setdefault(k, {})[store] = p

    # ── Paso 2: fuzzy match entre tiendas ──
    import difflib
    FUZZY_THRESHOLD = 0.70

    store_list = list(stores)
    for i in range(len(store_list)):
        for j in range(i + 1, len(store_list)):
            sa, sb = store_list[i], store_list[j]
            # Productos que existen en sa pero no en sb
            only_a = [k for k, sp in key_index.items() if sa in sp and sb not in sp]
            # Productos que existen en sb pero no en sa
            only_b = [k for k, sp in key_index.items() if sb in sp and sa not in sp]

            matched_b: set[str] = set()
            for ka in only_a:
                prod_a = key_index[ka][sa]
                best_score = 0.0
                best_kb = None
                for kb in only_b:
                    if kb in matched_b:
                        continue
                    prod_b = key_index[kb][sb]
                    score = difflib.SequenceMatcher(
                        None,
                        prod_a["name"].lower().replace("-", " "),
                        prod_b["name"].lower().replace("-", " "),
                    ).ratio()
                    if prod_a["brand"].lower() == prod_b["brand"].lower():
                        score = min(1.0, score + 0.15)
                    if score > best_score and score >= FUZZY_THRESHOLD:
                        best_score = score
                        best_kb = kb
                if best_kb:
                    key_index[ka][sb] = key_index[best_kb][sb]
                    matched_b.add(best_kb)

    comparison = []
    for k, store_prods in key_index.items():
        prices = {s: store_prods[s]["price"] for s in store_prods}
        best = min(prices, key=prices.get) if prices else None
        comparison.append({
            "name": next(iter(store_prods.values()))["name"],
            "brand": next(iter(store_prods.values()))["brand"],
            "prices": prices,
            "best_store": best,
        })

    return {"query": body.query, "comparison": comparison, "total": len(comparison)}


@app.post("/cart/add")
def cart_add(body: AddToCartRequest, authorization: str | None = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Sin token")
    token = authorization.replace("Bearer ", "")
    username = auth_user(token)
    carts = get_carts()
    cart = carts.setdefault(username, [])
    cart_item_id = f"{body.product_id}@{body.store}"
    existing = next((i for i in cart if i.get("cart_id") == cart_item_id), None)
    if existing:
        existing["quantity"] += body.quantity
    else:
        cart.append({
            "cart_id": cart_item_id,
            "product_id": body.product_id,
            "name": body.name,
            "price": body.price,
            "store": body.store,
            "store_name": STORES.get(body.store, {}).get("name", body.store),
            "quantity": body.quantity,
            "url": body.url,
        })
    save_json(CARTS_FILE, carts)
    return {"message": "Agregado al carrito", "cart": cart}


@app.get("/cart")
def cart_view(authorization: str | None = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Sin token")
    token = authorization.replace("Bearer ", "")
    username = auth_user(token)
    carts = get_carts()
    cart = carts.get(username, [])
    total = round(sum(i["price"] * i["quantity"] for i in cart), 2)
    return {"username": username, "cart": cart, "total": total, "items": len(cart)}


@app.put("/cart/update")
def cart_update(body: UpdateCartRequest, authorization: str | None = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Sin token")
    token = authorization.replace("Bearer ", "")
    username = auth_user(token)
    carts = get_carts()
    cart = carts.get(username, [])
    item = next((i for i in cart if i["cart_id"] == body.product_id or i["product_id"] == body.product_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Producto no encontrado en el carrito")
    if body.quantity <= 0:
        cart.remove(item)
    else:
        item["quantity"] = body.quantity
    save_json(CARTS_FILE, carts)
    return {"message": "Carrito actualizado", "cart": cart}


@app.post("/checkout")
def checkout(body: CheckoutRequest, authorization: str | None = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Sin token")
    token = authorization.replace("Bearer ", "")
    username = auth_user(token)
    carts = get_carts()
    cart = carts.get(username, [])
    if not cart:
        raise HTTPException(status_code=400, detail="Carrito vacío")
    total = round(sum(i["price"] * i["quantity"] for i in cart), 2)
    order = {
        "order_id": str(uuid.uuid4())[:8],
        "username": username,
        "items": [dict(i) for i in cart],
        "payment_method": body.payment_method,
        "total": total,
        "status": "completed",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    orders = get_orders()
    orders.append(order)
    save_json(ORDERS_FILE, orders)
    carts[username] = []
    save_json(CARTS_FILE, carts)
    return {"message": "Compra completada", "order": order}


@app.get("/orders")
def order_history(authorization: str | None = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Sin token")
    token = authorization.replace("Bearer ", "")
    username = auth_user(token)
    orders = get_orders()
    user_orders = [o for o in orders if o["username"] == username]
    return {"username": username, "orders": user_orders, "total_orders": len(user_orders)}


@app.post("/orders/reorder")
def reorder_last(authorization: str | None = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Sin token")
    token = authorization.replace("Bearer ", "")
    username = auth_user(token)
    orders = get_orders()
    user_orders = [o for o in orders if o["username"] == username]
    if not user_orders:
        raise HTTPException(status_code=404, detail="Sin órdenes previas")
    last = user_orders[-1]
    carts = get_carts()
    carts[username] = [dict(i) for i in last["items"]]
    save_json(CARTS_FILE, carts)
    return {"message": "Última orden restaurada al carrito", "cart": carts[username]}


@app.get("/agent/preferences")
def agent_preferences(authorization: str | None = Header(None)):
    """Memoria de compra: preferencias inferidas del historial de órdenes."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Sin token")
    token = authorization.replace("Bearer ", "")
    username = auth_user(token)
    orders = get_orders()
    user_orders = [o for o in orders if o["username"] == username]

    brands: dict[str, int] = {}
    stores: dict[str, float] = {}
    total_spent = 0.0

    for o in user_orders:
        total_spent += o.get("total", 0)
        for item in o.get("items", []):
            s = item.get("store_name", "?")
            stores[s] = stores.get(s, 0) + item.get("price", 0) * item.get("quantity", 1)

    fav_store = max(stores, key=stores.get) if stores else None

    return {
        "username": username,
        "total_orders": len(user_orders),
        "total_spent": round(total_spent, 2),
        "favorite_store": fav_store,
        "last_order_date": user_orders[-1]["created_at"] if user_orders else None,
    }


@app.post("/agent/ask")
async def agent_ask(prompt: str = Body(..., embed=True), authorization: str | None = Header(None)):
    """Compra por lenguaje natural. Interpreta la intención y ejecuta."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Sin token")
    token = authorization.replace("Bearer ", "")
    username = auth_user(token)
    p = prompt.lower()

    # "repite la última" / "lo mismo del mes pasado"
    if any(w in p for w in ["repetir", "repite", "mismo", "última", "mes pasado"]):
        orders = get_orders()
        user_orders = [o for o in orders if o["username"] == username]
        if not user_orders:
            return {"message": "No tenés órdenes previas."}
        last = user_orders[-1]
        carts = get_carts()
        carts[username] = [dict(i) for i in last["items"]]
        save_json(CARTS_FILE, carts)
        return {"message": f"Última orden ({last['order_id']}) restaurada al carrito.", "cart": carts[username]}

    # "más barato" / "compara X"
    if any(w in p for w in ["más barato", "mas barato", "compar"]):
        q = re.sub(r'(compara[rm]?\s*|m[aá]s barato\s*|cu[aá]l es m[aá]s barato\s*)', '', p).strip().rstrip(".!?")
        if not q:
            return {"message": "¿Qué producto querés comparar?"}
        return await compare_products(SearchRequest(query=q))

    # "compra X"
    m = re.search(r'compra\s+(.+)', p)
    if m:
        item = m.group(1).strip().rstrip(".!?")
        search_result = await search_products(SearchRequest(query=item, limit=3), authorization)
        prods = search_result.get("results", [])
        if not prods:
            return {"message": f"No encontré '{item}' en ninguna tienda."}
        best = min(prods, key=lambda x: x["price"] if x["price"] > 0 else float("inf"))
        carts = get_carts()
        cart = carts.setdefault(username, [])
        cart_id = f"{best['id']}@{best['store']}"
        existing = next((i for i in cart if i.get("cart_id") == cart_id), None)
        if existing:
            existing["quantity"] += 1
        else:
            cart.append({
                "cart_id": cart_id, "product_id": best["id"], "name": best["name"],
                "price": best["price"], "store": best["store"],
                "store_name": best["store_name"], "quantity": 1, "url": best.get("url", ""),
            })
        save_json(CARTS_FILE, carts)
        return {"message": f"Agregué '{best['name']}' de {best['store_name']} a S/ {best['price']}.", "cart": cart}

    # default: search
    return await search_products(SearchRequest(query=prompt, limit=5), authorization)


@app.get("/agent/actions")
def agent_actions():
    return {
        "actions": [
            "auth.login",
            "products.search",
            "products.compare",
            "cart.add",
            "cart.view",
            "cart.update",
            "checkout.create",
            "orders.history",
            "orders.reorder",
            "agent.ask",
            "agent.preferences",
        ]
    }


# ── Run ────────────────────────────────────────────────────────────────────

def main():
    """Entry point for `market-server` command."""
    import uvicorn
    print("Agentic Market API")
    print("   -> http://localhost:8765")
    print("   -> http://localhost:8765/docs")
    print(f"   -> data in {DATA_DIR}")
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")


if __name__ == "__main__":
    main()
