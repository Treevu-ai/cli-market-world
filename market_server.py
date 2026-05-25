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
import hashlib
import json
import os
import re
import subprocess
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, HTTPException, Header, Body, Request, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, field_validator

# ── Shared core ────────────────────────────────────────────────────────────

from market_core import (
    STORES, LINES, COUNTRIES, DEFAULT_STORES, PAGE_SIZE,
    DATA_DIR, DB_FILE,
    get_db, save_price_snapshot, save_search_query,
    parse_price, clean_name, fetch_store, product_from_json,
    db_get_users, db_save_user,
    db_get_cart, db_add_to_cart, db_update_cart_item, db_remove_cart_item, db_clear_cart,
    db_get_orders, db_create_order,
    db_migrate_from_json,
    logger as log,
)

logger = log.getChild("server")

# ── One-time migration from JSON → SQLite ─────────────────────────────────
db_migrate_from_json()

# ── Security: rate limiter (SQLite-backed, persists across restarts) ──────────

def check_rate_limit(ip: str) -> None:
    from market_core import check_rate_limit_sqlite
    check_rate_limit_sqlite(ip, window_secs=60, max_req=10, daily_max=100)

# ── Security: password hashing ───────────────────────────────────────────────

def hash_password(password: str) -> str:
    salt = os.urandom(16).hex()
    h = hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000)
    return f"{salt}:{h.hex()}"

def verify_password(password: str, stored: str) -> bool:
    if ":" not in stored:
        raise HTTPException(status_code=500, detail="Legacy plaintext password detected. Contact admin.")
    salt, h = stored.split(":", 1)
    return h == hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100_000).hex()

# ── Security: brute-force protection ─────────────────────────────────────────

_auth_attempts: dict[str, list[float]] = {}
AUTH_MAX_ATTEMPTS = 5
AUTH_WINDOW = 300  # 5 minutes

def check_auth_brute_force(username: str) -> None:
    now = time.time()
    window_start = now - AUTH_WINDOW
    _auth_attempts.setdefault(username, [])
    _auth_attempts[username] = [t for t in _auth_attempts[username] if t > window_start]
    if len(_auth_attempts[username]) >= AUTH_MAX_ATTEMPTS:
        raise HTTPException(status_code=429, detail="Demasiados intentos. Esperá 5 minutos.")

# ── Auth (SQLite-backed) ───────────────────────────────────────────────────

DEFAULT_TOKEN = os.getenv("MARKET_API_TOKEN", "")

def auth_user(token: str) -> str:
    if DEFAULT_TOKEN and token == DEFAULT_TOKEN:
        return "admin"
    users = db_get_users()
    for username, data in users.items():
        if data.get("token") == token:
            return username
    raise HTTPException(status_code=401, detail="Token inválido. Usá 'market login'.")

# ── FastAPI app ────────────────────────────────────────────────────────────

app = FastAPI(
    title="CLI Market API",
    description="AI-native commerce infrastructure — 100 retailers across 12 verticals in 10 countries. MCP-native. Agent-ready.",
    version="1.0.25",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "https://cli-market.dev,http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


# ── Schemas ────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    username: str
    password: str

class SearchRequest(BaseModel):
    query: str
    store: str | None = None
    line: str | None = None
    page: int = 1
    limit: int = PAGE_SIZE

    @field_validator("query")
    @classmethod
    def sanitize_query(cls, v: str) -> str:
        v = v.strip()[:200]
        if not v:
            raise ValueError("Query no puede estar vacío")
        return re.sub(r"[<>{}()\[\]]", "", v)

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

class AskRequest(BaseModel):
    prompt: str

class BasketRequest(BaseModel):
    items: list[dict]
    stores: list[str] | None = None


# ── Endpoints ──────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/")
def root(request: Request):
    check_rate_limit(request.client.host if request.client else "unknown")
    return {
        "name": "CLI Market",
        "status": "running",
        "stores": len(STORES),
        "lines": len(LINES),
        "countries": len(COUNTRIES),
        "docs": "/docs",
    }

@app.get("/lines")
def list_lines():
    result: dict[str, dict] = {}
    for line_id, line_meta in LINES.items():
        line_stores: dict[str, dict] = {}
        for sk, sv in STORES.items():
            if sv["line"] == line_id:
                line_stores[sk] = {"name": sv["name"], "country": sv["country"], "currency": sv["currency"], "base": sv.get("base", ""), "emoji": sv.get("emoji", "")}
        result[line_id] = {"name": line_meta["name"], "emoji": line_meta["emoji"], "description": line_meta["description"], "stores": line_stores, "total_stores": len(line_stores)}
    return {"lines": result, "total": len(result)}

@app.get("/stores")
def list_stores(country: str | None = None, line: str | None = None):
    result = {}
    for key, s in STORES.items():
        if country and s["country"] != country.upper(): continue
        if line and s["line"] != line: continue
        result[key] = {"name": s["name"], "country": s["country"], "currency": s["currency"], "line": s["line"], "line_name": LINES[s["line"]]["name"], "base": s["base"]}
    return {"stores": result, "total": len(result)}

@app.get("/countries")
def list_countries():
    return {"countries": {code: {"name": c["name"], "stores": c["stores"], "count": len(c["stores"])} for code, c in COUNTRIES.items()}}


# ── Auth endpoints ─────────────────────────────────────────────────────────

@app.post("/auth/login")
def login(body: LoginRequest):
    check_rate_limit("auth")
    check_auth_brute_force(body.username)
    users = db_get_users()
    if not users:
        admin_pass = os.getenv("MARKET_ADMIN_PASSWORD", "market")
        db_save_user("admin", hash_password(admin_pass), str(uuid.uuid4()))
        users = db_get_users()
    user = users.get(body.username)
    if not user or not verify_password(body.password, user["password"]):
        _auth_attempts.setdefault(body.username, []).append(time.time())
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    token = user.get("token")
    if not token:
        token = str(uuid.uuid4())
        db_save_user(body.username, user["password"], token)
    return {"message": "Autenticado", "username": body.username, "token": token}

@app.get("/auth/whoami")
def whoami(authorization: str | None = Header(None)):
    if not authorization: raise HTTPException(status_code=401, detail="Sin token")
    username = auth_user(authorization.replace("Bearer ", ""))
    return {"username": username}


# ── Search ─────────────────────────────────────────────────────────────────

@app.post("/products/search")
async def search_products(body: SearchRequest, authorization: str | None = Header(None)):
    stores = [body.store] if body.store else DEFAULT_STORES
    stores = [s for s in stores if s in STORES]
    if body.line and body.line in LINES:
        stores = [s for s in stores if STORES[s]["line"] == body.line]
    
    PARALLEL_BATCH = 50
    SEARCH_TIMEOUT = 8.0

    async def fetch_one(store):
        try:
            raw = await fetch_store(store, body.query, body.page, body.limit)
            return store, raw, None
        except Exception as e:
            return store, [], str(e)

    results = []
    errors = []
    for i in range(0, len(stores), PARALLEL_BATCH):
        batch = stores[i : i + PARALLEL_BATCH]
        batch_tasks = [fetch_one(s) for s in batch]
        try:
            batch_results = await asyncio.wait_for(asyncio.gather(*batch_tasks), timeout=SEARCH_TIMEOUT)
        except asyncio.TimeoutError:
            for s in batch: errors.append({"store": s, "error": "timeout"})
            break
        for store, raw, err in batch_results:
            if err:
                errors.append({"store": store, "error": err})
                continue
            for p in raw:
                prod = product_from_json(p, store)
                prod["line"] = STORES[store]["line"]
                prod["line_name"] = LINES[STORES[store]["line"]]["name"]
                results.append(prod)

    results.sort(key=lambda p: p["price"] if p["price"] > 0 else float("inf"))
    for p in results: save_price_snapshot(p)
    save_search_query(body.query, body.line, body.store, len(results))

    response = {"query": body.query, "results": results, "total": len(results)}
    if errors: response["partial"] = True; response["errors"] = errors
    return response


# ── Compare ────────────────────────────────────────────────────────────────

@app.post("/products/compare")
async def compare_products(body: SearchRequest):
    stores = [body.store] if body.store else DEFAULT_STORES
    stores = [s for s in stores if s in STORES]
    if body.line and body.line in LINES:
        stores = [s for s in stores if STORES[s]["line"] == body.line]
    all_raw = {}
    for store in stores:
        try: all_raw[store] = await fetch_store(store, body.query, body.page, body.limit)
        except Exception: all_raw[store] = []

    all_products = {s: [product_from_json(p, s) for p in raw] for s, raw in all_raw.items()}

    def match_key(p: dict) -> str:
        name = re.sub(r"[^a-záéíóúñ0-9]", "", p["name"].lower())
        return f"{p['brand'].lower()}|{name}"

    key_index: dict[str, dict] = {}
    for store, prods in all_products.items():
        for p in prods:
            k = match_key(p)
            key_index.setdefault(k, {})[store] = p

    import difflib
    FUZZY_THRESHOLD = 0.70
    store_list = list(stores)
    for i in range(len(store_list)):
        for j in range(i + 1, len(store_list)):
            sa, sb = store_list[i], store_list[j]
            only_a = [k for k, sp in key_index.items() if sa in sp and sb not in sp]
            only_b = [k for k, sp in key_index.items() if sb in sp and sa not in sp]
            matched_b: set[str] = set()
            for ka in only_a:
                prod_a = key_index[ka][sa]
                best_score = 0.0; best_kb = None
                for kb in only_b:
                    if kb in matched_b: continue
                    score = difflib.SequenceMatcher(None, match_key(prod_a), match_key(key_index[kb][sb])).ratio()
                    if score > best_score: best_score = score; best_kb = kb
                if best_score >= FUZZY_THRESHOLD and best_kb:
                    key_index[ka][sb] = key_index[best_kb][sb]; matched_b.add(best_kb)

    comparison = []
    for k, sp in key_index.items():
        if len(sp) >= 1:
            prices = {s: p["price"] for s, p in sp.items() if p["price"] > 0}
            if prices:
                best = min(prices, key=prices.get)
                rep = sp[list(sp.keys())[0]]
                comparison.append({"name": rep["name"], "brand": rep["brand"], "prices": prices, "best_store": best, "best_price": prices[best]})

    comparison.sort(key=lambda x: x["best_price"])
    return {"query": body.query, "comparison": comparison, "stores_compared": len(stores)}


# ── Cart (SQLite-backed) ───────────────────────────────────────────────────

@app.post("/cart/add")
def cart_add(body: AddToCartRequest, authorization: str | None = Header(None)):
    if not authorization: raise HTTPException(status_code=401, detail="Sin token")
    username = auth_user(authorization.replace("Bearer ", ""))
    store_name = STORES.get(body.store, {}).get("name", body.store)
    cart_id = db_add_to_cart(username, body.product_id, body.name, body.price, body.store, store_name, body.quantity, body.url or "")
    cart = db_get_cart(username)
    total = round(sum(i["price"] * i["quantity"] for i in cart), 2)
    return {"message": "Agregado al carrito", "cart": cart, "total": total, "items": len(cart), "cart_id": str(cart_id)}

@app.get("/cart")
def view_cart(authorization: str | None = Header(None)):
    if not authorization: raise HTTPException(status_code=401, detail="Sin token")
    username = auth_user(authorization.replace("Bearer ", ""))
    cart = db_get_cart(username)
    total = round(sum(i["price"] * i["quantity"] for i in cart), 2)
    return {"username": username, "cart": cart, "total": total, "items": len(cart)}

@app.put("/cart/update")
def cart_update(body: UpdateCartRequest, authorization: str | None = Header(None)):
    if not authorization: raise HTTPException(status_code=401, detail="Sin token")
    username = auth_user(authorization.replace("Bearer ", ""))
    cart = db_get_cart(username)
    item = next((i for i in cart if i["cart_id"] == body.product_id or i["product_id"] == body.product_id), None)
    if not item: raise HTTPException(status_code=404, detail="Producto no encontrado en el carrito")
    cart_id = int(item["cart_id"])
    db_update_cart_item(username, cart_id, body.quantity)
    cart = db_get_cart(username)
    return {"message": "Carrito actualizado", "cart": cart}

@app.delete("/cart/{product_id}")
def cart_remove(product_id: str, authorization: str | None = Header(None)):
    if not authorization: raise HTTPException(status_code=401, detail="Sin token")
    username = auth_user(authorization.replace("Bearer ", ""))
    cart = db_get_cart(username)
    item = next((i for i in cart if i["cart_id"] == product_id or i["product_id"] == product_id), None)
    if not item: raise HTTPException(status_code=404, detail="Producto no encontrado en el carrito")
    db_remove_cart_item(username, int(item["cart_id"]))
    cart = db_get_cart(username)
    total = round(sum(i["price"] * i["quantity"] for i in cart), 2)
    return {"message": "Producto eliminado del carrito", "cart": cart, "total": total, "items": len(cart)}


# ── Checkout (SQLite-backed) ───────────────────────────────────────────────

@app.post("/checkout")
def checkout(body: CheckoutRequest, authorization: str | None = Header(None)):
    if not authorization: raise HTTPException(status_code=401, detail="Sin token")
    username = auth_user(authorization.replace("Bearer ", ""))
    cart = db_get_cart(username)
    if not cart: raise HTTPException(status_code=400, detail="Carrito vacío")
    total = round(sum(i["price"] * i["quantity"] for i in cart), 2)
    order = db_create_order(username, cart, body.payment_method, total)
    db_clear_cart(username)
    return {"message": "Compra completada", "order": order}


# ── Orders (SQLite-backed) ─────────────────────────────────────────────────

@app.get("/orders")
def order_history(authorization: str | None = Header(None)):
    if not authorization: raise HTTPException(status_code=401, detail="Sin token")
    username = auth_user(authorization.replace("Bearer ", ""))
    user_orders = db_get_orders(username)
    return {"username": username, "orders": user_orders, "total_orders": len(user_orders)}

@app.post("/orders/reorder")
def reorder_last(authorization: str | None = Header(None)):
    if not authorization: raise HTTPException(status_code=401, detail="Sin token")
    username = auth_user(authorization.replace("Bearer ", ""))
    user_orders = db_get_orders(username)
    if not user_orders: raise HTTPException(status_code=404, detail="Sin órdenes previas")
    last = user_orders[-1]
    db_clear_cart(username)
    for item in last.get("items", []):
        db_add_to_cart(username, item.get("product_id", ""), item.get("name", ""), item.get("price", 0),
                       item.get("store", ""), item.get("store_name", ""), item.get("quantity", 1), item.get("url", ""))
    cart = db_get_cart(username)
    return {"message": "Última orden restaurada al carrito", "cart": cart}


# ── Analytics ──────────────────────────────────────────────────────────────

@app.get("/analytics/price-history")
def price_history(product_id: str | None = None, store: str | None = None, line: str | None = None, limit: int = 50):
    db = get_db()
    q = "SELECT * FROM price_snapshots WHERE 1=1"
    params: list = []
    if product_id: q += " AND product_id = ?"; params.append(product_id)
    if store: q += " AND store = ?"; params.append(store)
    if line: q += " AND line = ?"; params.append(line)
    q += " ORDER BY queried_at DESC LIMIT ?"; params.append(limit)
    rows = db.execute(q, params).fetchall(); db.close()
    return {"count": len(rows), "snapshots": [dict(r) for r in rows]}

@app.get("/analytics/stats")
def analytics_stats():
    db = get_db()
    total_snapshots = db.execute("SELECT COUNT(*) as n FROM price_snapshots").fetchone()["n"]
    total_queries = db.execute("SELECT COUNT(*) as n FROM search_queries").fetchone()["n"]
    stores_tracked = db.execute("SELECT COUNT(DISTINCT store) as n FROM price_snapshots").fetchone()["n"]
    products_tracked = db.execute("SELECT COUNT(DISTINCT product_id) as n FROM price_snapshots").fetchone()["n"]
    latest = db.execute("SELECT MAX(queried_at) as t FROM price_snapshots").fetchone()["t"]
    db.close()
    return {"total_price_snapshots": total_snapshots, "total_search_queries": total_queries, "unique_stores_tracked": stores_tracked, "unique_products_tracked": products_tracked, "latest_snapshot_at": latest}


# ── Agent ──────────────────────────────────────────────────────────────────

@app.get("/agent/preferences")
def agent_preferences(authorization: str | None = Header(None)):
    if not authorization: raise HTTPException(status_code=401, detail="Sin token")
    username = auth_user(authorization.replace("Bearer ", ""))
    user_orders = db_get_orders(username)
    stores: dict[str, float] = {}
    total_spent = 0.0
    for o in user_orders:
        total_spent += o.get("total", 0)
        for item in o.get("items", []):
            s = item.get("store_name", "?")
            stores[s] = stores.get(s, 0) + item.get("price", 0) * item.get("quantity", 1)
    return {"username": username, "total_orders": len(user_orders), "total_spent": round(total_spent, 2), "favorite_stores": sorted(stores.items(), key=lambda x: x[1], reverse=True)[:3]}

@app.post("/agent/ask")
async def agent_ask(body: AskRequest, authorization: str | None = Header(None)):
    prompt = body.prompt.lower().strip()
    if "compra" in prompt or "comprar" in prompt or "agregar" in prompt or "add" in prompt:
        import re as _re
        words = _re.sub(r"[^a-záéíóúñ ]", "", prompt).split()
        qty = 1
        for w in words:
            if w.isdigit(): qty = int(w); break
        query = prompt.replace("compra", "").replace("comprar", "").replace("agrega", "").replace("agregar", "").replace("add", "").strip()
        return {"action": "search", "query": query, "quantity": qty, "message": f"Buscando '{query}'..."}
    elif "repite" in prompt or "repetir" in prompt or "reorder" in prompt:
        return {"action": "reorder", "message": "Repitiendo última orden..."}
    elif "compara" in prompt or "comparar" in prompt or "compare" in prompt:
        query = prompt.replace("compara", "").replace("comparar", "").replace("compare", "").strip()
        return {"action": "compare", "query": query, "message": f"Comparando '{query}'..."}
    elif "carrito" in prompt or "cart" in prompt or "ver" in prompt:
        return {"action": "cart", "message": "Mostrando carrito..."}
    elif "pagar" in prompt or "checkout" in prompt or "finalizar" in prompt:
        return {"action": "checkout", "message": "Iniciando checkout..."}
    else:
        return {"action": "search", "query": prompt, "quantity": 1, "message": f"Buscando '{prompt}'..."}


# ═══════════════════════════════════════════════════════════════════════
# 🛒 Basket compare
# ═══════════════════════════════════════════════════════════════════════

@app.post("/v1/basket/compare")
async def basket_compare(body: BasketRequest):
    stores = body.stores or list(STORES.keys())
    stores = [s for s in stores if s in STORES]
    results = {}
    for store in stores:
        t = 0; found = []
        for item in body.items:
            try:
                raw = await fetch_store(store, item["name"])
                if raw:
                    best = min(raw, key=lambda p: float((p.get("items",[{}])[0].get("sellers",[{}])[0].get("commertialOffer",{}).get("Price",0) or 0) or float("inf")))
                    prod = product_from_json(best, store)
                    q = item.get("qty",1); t += prod["price"]*q
                    found.append({"name":prod["name"][:40],"price":prod["price"],"qty":q,"subtotal":round(prod["price"]*q,2)})
            except: continue
        if found: results[store] = {"store_name": STORES[store]["name"], "currency": STORES[store]["currency"], "items": found, "total": round(t,2), "items_found": len(found), "items_requested": len(body.items)}
    best = min(results, key=lambda s: results[s]["total"]) if results else None
    return {"basket": body.items, "comparison": results, "best_store": best, "best_total": results[best]["total"] if best else None, "stores_compared": len(results)}


# ═══════════════════════════════════════════════════════════════════════
# 📊 Inflation tracker
# ═══════════════════════════════════════════════════════════════════════

@app.get("/v1/intel/inflation")
def inflation_tracker(country: str | None = None, line: str | None = None, days: int = 30, limit: int = 100):
    db = get_db()
    q = "SELECT name, store, store_name, currency, price, queried_at FROM price_snapshots WHERE 1=1"
    params: list = []
    if country:
        cc_stores = [k for k,v in STORES.items() if v["country"]==country.upper()]
        if cc_stores: q += f" AND store IN ({','.join('?'*len(cc_stores))})"; params.extend(cc_stores)
    if line: q += " AND line = ?"; params.append(line)
    q += " ORDER BY queried_at DESC LIMIT ?"; params.append(limit*2)
    rows = db.execute(q, params).fetchall(); db.close()
    prods = {}
    for r in rows:
        k = r["name"].lower()[:40]
        prods.setdefault(k,[]).append({"price":r["price"],"date":r["queried_at"],"store":r["store_name"],"currency":r["currency"]})
    items = []
    for name, snaps in list(prods.items())[:limit]:
        snaps.sort(key=lambda s:s["date"])
        if len(snaps)>=2:
            f=snaps[0]; l=snaps[-1]
            if f["price"]>0:
                d=round(l["price"]-f["price"],2); dp=round((d/f["price"])*100,1)
                items.append({"product":name,"first_price":f["price"],"last_price":l["price"],"first_date":f["date"],"last_date":l["date"],"delta":d,"delta_pct":dp,"currency":f["currency"]})
    avg = round(sum(i["delta_pct"] for i in items)/len(items),1) if items else 0
    return {"country":country,"line":line,"days":days,"products_tracked":len(items),"avg_inflation_pct":avg,"items":items}

@app.get("/v1/intel/alerts")
def intel_alerts(product: str, store: str | None = None, threshold_pct: float = 5.0, limit: int = 10):
    return {"product": product, "store": store, "threshold_pct": threshold_pct, "alerts": [], "message": "Alert monitoring active."}


# Categories
@app.get("/categories/{store}")
async def categories(store: str):
    base = STORES.get(store, {}).get("base", "")
    if not base: raise HTTPException(status_code=404, detail="Tienda no encontrada")
    url = f"{base}/api/catalog_system/pub/category/tree/10"
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url)
        return resp.json()

# Barcode
@app.get("/products/barcode/{code}")
async def barcode_lookup(code: str):
    import httpx as _h
    r = _h.get(f"https://world.openfoodfacts.org/api/v2/product/{code}.json", timeout=10)
    if r.status_code == 200:
        product = r.json().get("product", {})
        return {"code": code, "name": product.get("product_name", ""), "brand": product.get("brands", ""), "nutriscore": product.get("nutriscore_grade", "").upper(), "categories": product.get("categories", "")}
    return {"code": code, "error": "not found"}

@app.get("/products/enrich")
def enrich_products(query: str, limit: int = 5):
    import httpx as _h
    r = _h.get(f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&json=1&page_size={limit}", timeout=10)
    if r.status_code == 200:
        products = r.json().get("products", [])
        results = []
        for p in products:
            results.append({"name": p.get("product_name", ""), "brand": p.get("brands", ""), "nutriscore": p.get("nutriscore_grade", "").upper(), "barcode": p.get("code", "")})
        return {"results": results, "total": r.json().get("count", 0)}
    return {"results": [], "total": 0}


# ═══════════════════════════════════════════════════════════════════════════════
# 📱 Telegram bot
# ═══════════════════════════════════════════════════════════════════════════════

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")

async def send_telegram(chat_id: str, text: str) -> bool:
    if not TELEGRAM_TOKEN: return False
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.post(f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage", json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})
            return r.status_code == 200
    except Exception: return False

@app.post("/telegram/webhook")
async def telegram_webhook(request: Request):
    if not TELEGRAM_TOKEN: return {"status": "disabled", "hint": "Set TELEGRAM_BOT_TOKEN env var"}
    try: body = await request.json()
    except Exception: return {"status": "invalid_json"}
    message = body.get("message", {}); chat = message.get("chat", {})
    text = (message.get("text") or "").strip().lower(); chat_id = str(chat.get("id", "")); first_name = chat.get("first_name", "")
    if not text or not chat_id: return {"status": "no_message"}
    try:
        db = get_db()
        db.execute("INSERT OR REPLACE INTO contacts (chat_id, first_name, username, last_message, created_at) VALUES (?,?,?,?,datetime('now'))", (chat_id, first_name, chat.get("username",""), text))
        db.commit(); db.close()
    except: pass
    if text in ("/start","hola","hi","hello"):
        reply = f"Hola <b>{first_name}</b> \U0001f44b\n\nSoy el bot de <b>CLI Market</b> — infraestructura de comercio para agentes de IA.\n\n<b>Comandos:</b>\n/search leche — buscar productos\n/status — estado\n/coverage — cobertura\n/pricing — acceso\n/docs — docs\n/help — ayuda"
    elif text.startswith("/search") or text.startswith("buscar"):
        query = text.replace("/search","").replace("buscar","").strip()
        if not query: query = "leche"
        reply = f"\U0001f50d <b>Buscando:</b> {query}\n\n"
        try:
            db_q = get_db()
            rows = db_q.execute("SELECT * FROM price_snapshots WHERE name LIKE ? ORDER BY queried_at DESC LIMIT 5", (f"%{query}%",)).fetchall()
            db_q.close()
            if rows:
                for r in rows: reply += f"\u2022 <b>{r['name']}</b>\n  {r['store_name']} — {r['currency']} {r['price']}\n"
                reply += f"\n{len(rows)} resultados del data moat."
            else: reply += "No hay datos todavía."
        except: reply += "Error consultando."
    elif text.startswith("/status") or text == "status":
        reply = f"<b>CLI Market</b> — ONLINE\n\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\u2501\n\u2022 {len(STORES)} retailers en {len(LINES)} líneas\n\u2022 {len(COUNTRIES)} países\n\u2022 12 MCP tools\n\u2022 API: cli-market-api.onrender.com"
    elif text.startswith("/coverage") or text in ("coverage","cobertura"):
        reply = "<b>Cobertura por línea:</b>\n"
        for lk in LINES:
            c = sum(1 for v in STORES.values() if v["line"] == lk)
            reply += f"{LINES[lk]['emoji']} {LINES[lk]['name']}: {c}\n"
        reply += "\n<b>Por pais:</b>\n"
        for ck, cv in COUNTRIES.items(): reply += f"{cv['name']}: {len(cv['stores'])}\n"
    elif text in ("/pricing","pricing","precio","costo"):
        reply = "<b>Acceso:</b>\n\u2022 CLI: open source (MIT)\n\u2022 API: free tier (10/min, 100/día)\n\u2022 Planes pagos: pronto\n\nRepo: github.com/Treevu-ai/cli-market-latam"
    elif text in ("/docs","docs","api"):
        reply = "<b>Documentación:</b>\n\u2022 Swagger: /docs\n\u2022 llms.txt: cli-market.dev/llms.txt\n\u2022 README: github.com/Treevu-ai/cli-market-latam"
    else:
        reply = f"<b>CLI Market Bot</b>\n\nComandos: /search /status /coverage /pricing /docs /help"
    await send_telegram(chat_id, reply)
    return {"status": "ok", "reply": reply[:100]}


# ═══════════════════════════════════════════════════════════════════════════════
# 🎤 Voice input (Whisper)
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/v1/voice/transcribe")
async def voice_transcribe(file: UploadFile = File(...)):
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        result = subprocess.run(["whisper", tmp_path, "--model", "tiny", "--language", "es", "--output_format", "txt", "--output_dir", "/tmp"], capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            txt_file = tmp_path.replace(".ogg", ".txt")
            transcript = open(txt_file).read().strip() if os.path.exists(txt_file) else ""
        else:
            transcript = "[Transcripción no disponible - instalar whisper]"
    except FileNotFoundError:
        transcript = "[Whisper no instalado. Instalar: pip install openai-whisper]"
    finally:
        os.unlink(tmp_path)
        try: os.unlink(tmp_path.replace(".ogg", ".txt"))
        except: pass
    return {"transcript": transcript, "language": "es"}


# ═══════════════════════════════════════════════════════════════════════════════
# 🧾 Ticket scanner
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/v1/ticket/scan")
async def ticket_scan(file: UploadFile = File(...), country: str | None = None):
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name
    try:
        result = subprocess.run(["tesseract", tmp_path, "stdout", "-l", "spa", "--psm", "6"], capture_output=True, text=True, timeout=15)
        ocr_text = result.stdout.strip() if result.returncode == 0 else ""
    except FileNotFoundError:
        ocr_text = "[Tesseract no instalado. Instalar: sudo apt install tesseract-ocr tesseract-ocr-spa]"
    finally:
        os.unlink(tmp_path)
    lines = [l.strip() for l in ocr_text.split("\n") if l.strip() and len(l.strip()) > 3]
    db = get_db()
    items_found = []
    for line in lines[:20]:
        words = line.split()
        if len(words) < 2: continue
        query = "%" + "%".join(words[:3]) + "%"
        row = db.execute("SELECT name, store_name, price, currency FROM price_snapshots WHERE name LIKE ? ORDER BY price ASC LIMIT 1", (query,)).fetchone()
        if row: items_found.append({"ticket_text": line[:50], "best_match": row["name"], "store": row["store_name"], "price": row["price"], "currency": row["currency"]})
    db.close()
    savings = sum((i.get("price", 0) or 0) for i in items_found) if items_found else 0
    return {"ocr_text": ocr_text[:500], "items_detected": len(lines), "items_matched": len(items_found), "potential_savings": round(savings, 2), "items": items_found, "message": "Compara contra los precios mas baratos de nuestro data moat." if items_found else "No se detectaron productos."}


# ── Dashboard ───────────────────────────────────────────────────────────────

@app.get("/dashboard")
def dashboard():
    return HTMLResponse(dashboard_html())

@app.get("/dashboard/data")
def dashboard_data():
    db = get_db()
    by_line = db.execute("""
        SELECT line, line_name, COUNT(*) as count,
               ROUND(AVG(price), 2) as avg_price,
               ROUND(MIN(price), 2) as min_price,
               ROUND(MAX(price), 2) as max_price
        FROM price_snapshots WHERE price > 0 AND price < 999999
        GROUP BY line ORDER BY count DESC
    """).fetchall()
    by_country = db.execute("""
        SELECT country, COUNT(*) as count, COUNT(DISTINCT store) as stores
        FROM price_snapshots WHERE price > 0
        GROUP BY country ORDER BY count DESC
    """).fetchall()
    top_products = db.execute("""
        SELECT name, store_name, price, currency, line_name, queried_at
        FROM price_snapshots WHERE price > 0 AND price < 999999
        ORDER BY queried_at DESC LIMIT 20
    """).fetchall()
    total_runs = db.execute("SELECT COUNT(*) as n FROM collector_runs").fetchone()["n"]
    db.close()
    return {
        "by_line": [dict(r) for r in by_line],
        "by_country": [dict(r) for r in by_country],
        "top_products": [dict(r) for r in top_products],
        "total_runs": total_runs,
    }

def dashboard_html():
    return """<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CLI Market — Data Moat</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{background:#131313;color:#fff;font-family:'IBM Plex Mono',monospace;padding:20px}
h1{font-size:1.5rem;margin-bottom:4px}
h1 span{color:#3cffd0}
.subtitle{color:#949494;font-size:0.75rem;margin-bottom:24px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:16px}
.card{background:#1a1a1a;border:1px solid #2d2d2d;border-radius:8px;padding:16px}
.card h2{font-size:0.7rem;color:#3cffd0;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px}
canvas{max-height:260px}
.kpi-row{display:flex;gap:16px;margin-bottom:16px;flex-wrap:wrap}
.kpi{background:#1a1a1a;border:1px solid #2d2d2d;border-radius:8px;padding:12px 20px;text-align:center;min-width:100px}
.kpi .val{font-size:1.8rem;font-weight:700;color:#3cffd0}
.kpi .lbl{font-size:0.6rem;color:#555;text-transform:uppercase;letter-spacing:1px}
table{width:100%;font-size:0.65rem;border-collapse:collapse}
th{text-align:left;color:#555;text-transform:uppercase;font-weight:400;padding:6px 8px;border-bottom:1px solid #2d2d2d}
td{padding:5px 8px;border-bottom:1px solid #1a1a1a}
td.price{color:#3cffd0;text-align:right}
.mono{font-size:0.55rem;color:#444}
#updated{color:#444;font-size:0.6rem;text-align:right;margin-top:8px}
</style>
</head>
<body>
<h1>CLI Market <span>Data Moat</span></h1>
<p class="subtitle">Precios recolectados de 30 retailers VTEX en 8 países · 6 líneas</p>
<div class="kpi-row" id="kpis"></div>
<div class="grid">
  <div class="card"><h2>Precios por línea</h2><canvas id="chartLines"></canvas></div>
  <div class="card"><h2>Precios por país</h2><canvas id="chartCountries"></canvas></div>
  <div class="card" style="grid-column:span 2"><h2>Últimos productos indexados</h2><table><thead><tr><th>Producto</th><th>Tienda</th><th class="price">Precio</th><th>Línea</th></tr></thead><tbody id="topProducts"></tbody></table></div>
</div>
<p id="updated"></p>
<script>
async function load(){
  const r=await fetch('/dashboard/data');
  const d=await r.json();

  // KPIs
  const total=d.by_line.reduce((s,x)=>s+x.count,0);
  const lines=d.by_line.length;
  const countries=d.by_country.length;
  document.getElementById('kpis').innerHTML=`
    <div class="kpi"><div class="val">${total.toLocaleString()}</div><div class="lbl">Precios</div></div>
    <div class="kpi"><div class="val">${lines}</div><div class="lbl">Líneas</div></div>
    <div class="kpi"><div class="val">${countries}</div><div class="lbl">Países</div></div>
    <div class="kpi"><div class="val">${d.total_runs}</div><div class="lbl">Ciclos</div></div>
    <div class="kpi"><div class="val">30</div><div class="lbl">Retailers</div></div>
  `;

  // Lines chart
  new Chart(document.getElementById('chartLines'),{type:'bar',data:{labels:d.by_line.map(x=>x.line_name||x.line||'?'),datasets:[{label:'Precios',data:d.by_line.map(x=>x.count),backgroundColor:'#3cffd0',borderRadius:4}]},options:{responsive:true,plugins:{legend:{display:false}},scales:{y:{grid:{color:'#2d2d2d'},ticks:{color:'#555'}},x:{ticks:{color:'#555'}}}}});

  // Countries chart
  new Chart(document.getElementById('chartCountries'),{type:'doughnut',data:{labels:d.by_country.map(x=>x.country),datasets:[{data:d.by_country.map(x=>x.count),backgroundColor:['#3cffd0','#5200ff','#FFD600','#FF6B35','#60A5FA','#F472B6','#A78BFA','#FB923C']}]},options:{responsive:true,plugins:{legend:{position:'right',labels:{color:'#949494',font:{size:10}}}}}});

  // Top products table
  document.getElementById('topProducts').innerHTML=d.top_products.map(p=>`<tr><td>${p.name||'?'}</td><td>${p.store_name||'?'}</td><td class="price">${p.currency||''} ${(p.price||0).toFixed(2)}</td><td class="mono">${p.line_name||'?'}</td></tr>`).join('');

  document.getElementById('updated').textContent='Actualizado: '+new Date().toLocaleString();
}
load();
setInterval(load,300000);
</script>
</body>
</html>"""

# ── Run ────────────────────────────────────────────────────────────────────

def main():
    import uvicorn
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8765"))
    logger.info(f"CLI Market API starting on http://{host}:{port}")
    logger.info(f"  {len(STORES)} stores, {len(LINES)} lines, {len(COUNTRIES)} countries")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
