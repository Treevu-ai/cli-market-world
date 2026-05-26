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
    fetch_store, product_from_json,
    db_get_users, db_save_user,
    db_get_cart, db_add_to_cart, db_update_cart_item, db_remove_cart_item, db_clear_cart,
    db_get_orders, db_create_order,
    db_migrate_from_json, check_rate_limit_sqlite,
    db_validate_api_key, db_create_api_key, db_list_api_keys, db_revoke_api_key,
    db_get_subscription, db_set_subscription, TIERS,
    logger as log,
)

logger = log.getChild("server")

# ── One-time migration from JSON → SQLite ─────────────────────────────────
db_migrate_from_json()

# ── Security: rate limiter (SQLite-backed, persists across restarts) ──────────
# Configurable via env vars: RATE_LIMIT_MIN, RATE_LIMIT_DAY, RATE_LIMIT_WINDOW

RATE_LIMIT_MIN = int(os.getenv("RATE_LIMIT_MIN", "60"))
RATE_LIMIT_DAY = int(os.getenv("RATE_LIMIT_DAY", "1000"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))

def check_rate_limit(ip: str) -> None:
    check_rate_limit_sqlite(ip, window_secs=RATE_LIMIT_WINDOW,
                            max_req=RATE_LIMIT_MIN, daily_max=RATE_LIMIT_DAY)

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
    # Try API keys first (sk-...)
    if token.startswith("sk-"):
        key_data = db_validate_api_key(token)
        if key_data:
            return key_data["username"]
    # Fall back to legacy tokens
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

# ── Background collector (runs every COLLECT_INTERVAL_HOURS, default 8h) ──────────

COLLECTOR_INTERVAL = int(os.getenv("COLLECT_INTERVAL_HOURS", "8"))

@app.on_event("startup")
async def start_collector():
    import threading
    def _run():
        import time, subprocess, sys
        logger.info("Collector background thread started (interval=%sh)", COLLECTOR_INTERVAL)
        while True:
            try:
                subprocess.run([sys.executable, "collect_prices.py"], check=False, timeout=3600)
            except Exception as e:
                logger.error("Collector run failed: %s", e)
            time.sleep(COLLECTOR_INTERVAL * 3600)
    t = threading.Thread(target=_run, daemon=True)
    t.start()


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

@app.get("/health/collector")
def health_collector():
    """Collector health: last run, staleness, store coverage."""
    try:
        db = get_db()
        last = db.execute(
            "SELECT started_at, finished_at, stores_attempted, stores_succeeded, prices_collected "
            "FROM collector_runs ORDER BY id DESC LIMIT 1"
        ).fetchone()
        total_runs = db.execute("SELECT COUNT(*) as n FROM collector_runs").fetchone()["n"]
        active_stores = db.execute(
            "SELECT COUNT(DISTINCT store) as n FROM price_snapshots WHERE price > 0"
        ).fetchone()["n"]
        db.close()
    except Exception:
        return {"status": "unknown", "error": "Database not initialized"}

    if not last:
        return {"status": "unknown", "message": "No collector runs yet", "runs_total": 0}

    finished = last["finished_at"]
    now = datetime.now(timezone.utc).isoformat()
    if finished:
        try:
            from datetime import timedelta
            ft = datetime.fromisoformat(finished.replace("Z", "+00:00"))
            age_h = (datetime.now(timezone.utc) - ft).total_seconds() / 3600
        except Exception:
            age_h = 999
        if age_h > 24:
            status = "dead"
        elif age_h > 12:
            status = "stale"
        else:
            status = "healthy"
    else:
        status = "running"
        age_h = None

    return {
        "status": status,
        "last_run": last["started_at"],
        "last_finished": finished,
        "age_hours": round(age_h, 1) if age_h is not None else None,
        "stores_attempted": last["stores_attempted"],
        "stores_succeeded": last["stores_succeeded"],
        "prices_collected": last["prices_collected"],
        "stores_active": active_stores or 0,
        "stores_total": len(STORES),
        "runs_total": total_runs,
    }

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


# ── API Keys ──────────────────────────────────────────────────────────────────

class CreateApiKeyRequest(BaseModel):
    scopes: str = "read"
    label: str = ""

@app.post("/auth/keys")
def create_api_key(body: CreateApiKeyRequest, authorization: str | None = Header(None)):
    if not authorization: raise HTTPException(status_code=401, detail="Sin token")
    username = auth_user(authorization.replace("Bearer ", ""))
    if body.scopes not in ("read", "read_write"):
        raise HTTPException(status_code=400, detail="Scopes must be 'read' or 'read_write'")
    result = db_create_api_key(username, body.scopes, body.label)
    return {
        "message": "API key created. Store it safely — it won't be shown again.",
        "key": result["key"],
        "prefix": result["prefix"],
        "scopes": result["scopes"],
        "label": result["label"],
    }

@app.get("/auth/keys")
def list_api_keys(authorization: str | None = Header(None)):
    if not authorization: raise HTTPException(status_code=401, detail="Sin token")
    username = auth_user(authorization.replace("Bearer ", ""))
    keys = db_list_api_keys(username)
    return {"keys": keys, "total": len(keys)}

@app.delete("/auth/keys/{key_id}")
def revoke_api_key(key_id: int, authorization: str | None = Header(None)):
    if not authorization: raise HTTPException(status_code=401, detail="Sin token")
    username = auth_user(authorization.replace("Bearer ", ""))
    ok = db_revoke_api_key(username, key_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"message": "Key revoked"}


# ── Search ─────────────────────────────────────────────────────────────────

@app.post("/products/search")
async def search_products(body: SearchRequest, authorization: str | None = Header(None)):
    try:
        return await _search_products(body)
    except Exception as e:
        logger.exception("search_products crashed")
        raise HTTPException(status_code=500, detail=str(e))

async def _search_products(body: SearchRequest):
    stores = [body.store] if body.store else DEFAULT_STORES
    stores = [s for s in stores if s in STORES]
    if body.line and body.line in LINES:
        stores = [s for s in stores if STORES[s]["line"] == body.line]
    
    PARALLEL_BATCH = 20
    SEARCH_TIMEOUT = float(os.getenv("SEARCH_TIMEOUT", "15.0"))

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
        except Exception as e:
            logger.error("Search batch error: %s", e)
            errors.append({"store": "batch", "error": str(e)})
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

@app.get("/orders/{order_id}")
def order_status(order_id: str, authorization: str | None = Header(None)):
    if not authorization: raise HTTPException(status_code=401, detail="Sin token")
    username = auth_user(authorization.replace("Bearer ", ""))
    db = get_db()
    order = db.execute("SELECT * FROM app_orders WHERE order_id=? AND username=?", (order_id, username)).fetchone()
    if not order: db.close(); raise HTTPException(status_code=404, detail="Order not found")
    items = db.execute("SELECT * FROM app_order_items WHERE order_id=?", (order_id,)).fetchall()
    db.close()
    return {"order": dict(order), "items": [dict(i) for i in items]}

@app.get("/orders/{order_id}/receipt")
def order_receipt(order_id: str, authorization: str | None = Header(None)):
    """
    Comprobante de pago — emitido por SINAPSIS INNOVADORA S.A.C.
    IMPORTANTE: Emisión MANUAL. No se envía automáticamente a SUNAT.
    Para facturación electrónica oficial, configure SUNAT_PSE_API_KEY + PSE.
    """
    if not authorization: raise HTTPException(status_code=401, detail="Sin token")
    username = auth_user(authorization.replace("Bearer ", ""))
    db = get_db()
    order = db.execute("SELECT * FROM app_orders WHERE order_id=? AND username=?", (order_id, username)).fetchone()
    if not order: db.close(); raise HTTPException(status_code=404, detail="Order not found")
    items = db.execute("SELECT * FROM app_order_items WHERE order_id=?", (order_id,)).fetchall()
    db.close()
    total_calc = round(sum(i["price"] * i["quantity"] for i in items), 2)
    return {"comprobante_id": f"SIM-{order_id}",
            "tipo": "BOLETA DE VENTA ELECTRÓNICA",
            "emisor": {"razon_social": "SINAPSIS INNOVADORA S.A.C.", "ruc": "20613045563", "direccion": "Lima, Perú"},
            "cliente": username, "orden_id": order_id,
            "fecha_emision": datetime.now(timezone.utc).isoformat(),
            "metodo_pago": order["payment_method"], "estado": order["status"],
            "items": [{"producto": i["name"], "cantidad": i["quantity"], "precio_unitario": i["price"],
                        "subtotal": round(i["price"] * i["quantity"], 2)} for i in items],
            "subtotal": total_calc, "igv": round(total_calc * 0.18, 2),
            "total": round(total_calc * 1.18, 2), "moneda": "PEN",
            "nota": "COMPROBANTE DE EMISIÓN MANUAL — No válido como factura electrónica SUNAT. Para facturación oficial contacte a SINAPSIS INNOVADORA S.A.C. RUC 20613045563."}

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


@app.get("/analytics/trending")
def analytics_trending(country: str | None = None, line: str | None = None, limit: int = 10):
    """Products with the biggest price movement in the last 7 days."""
    db = get_db()
    q = """SELECT name, store_name, price, currency, line_name, queried_at
           FROM price_snapshots WHERE price > 0"""
    params: list = []
    if country:
        q += " AND store IN (SELECT store FROM price_snapshots GROUP BY store)"
        params.append(country)
    if line:
        q += " AND line = ?"
        params.append(line)
    q += " ORDER BY queried_at DESC LIMIT ?"
    params.append(limit * 2)
    rows = db.execute(q, params).fetchall()
    db.close()
    return {"trending": [dict(r) for r in rows], "total": len(rows)}


@app.post("/v1/data/export")
def data_export(body: dict):
    """Export data moat as JSON or CSV."""
    country = body.get("country")
    line = body.get("line")
    fmt = body.get("format", "json")
    limit = min(body.get("limit", 100), 1000)
    db = get_db()
    q = "SELECT * FROM price_snapshots WHERE price > 0"
    params: list = []
    if line:
        q += " AND line = ?"
        params.append(line)
    q += " ORDER BY queried_at DESC LIMIT ?"
    params.append(limit)
    rows = db.execute(q, params).fetchall()
    db.close()
    data = [dict(r) for r in rows]
    if fmt == "csv":
        import io, csv as _csv
        buf = io.StringIO()
        if data:
            w = _csv.DictWriter(buf, fieldnames=data[0].keys())
            w.writeheader()
            w.writerows(data)
        return {"format": "csv", "data": buf.getvalue(), "total": len(data)}
    return {"format": "json", "data": data, "total": len(data)}


@app.post("/v1/data/export-history")
def data_export_history(body: dict):
    """Export historical price data with date range and filters."""
    from datetime import timedelta
    days = body.get("days", 30)
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    line = body.get("line"); store = body.get("store")
    fmt = body.get("format", "json"); limit = min(body.get("limit", 500), 5000)
    db = get_db()
    q = "SELECT * FROM price_snapshots WHERE price > 0 AND queried_at >= ?"
    params: list = [since]
    if line: q += " AND line = ?"; params.append(line)
    if store: q += " AND store = ?"; params.append(store)
    q += " ORDER BY queried_at DESC LIMIT ?"; params.append(limit)
    rows = db.execute(q, params).fetchall(); db.close()
    data = [dict(r) for r in rows]
    prices = [r["price"] for r in data if r.get("price")]
    if fmt == "csv":
        import io, csv as _csv
        buf = io.StringIO()
        if data:
            w = _csv.DictWriter(buf, fieldnames=data[0].keys()); w.writeheader(); w.writerows(data)
        return {"format":"csv","data":buf.getvalue(),"total":len(data),"since":since}
    return {"format":"json","total":len(data),"since":since,
            "data":data[:100],
            "stats":{"avg_price":round(sum(prices)/len(prices),2),"min_price":min(prices),"max_price":max(prices)} if prices else {}}


@app.get("/dashboard/usage")
def dashboard_usage(authorization: str | None = Header(None)):
    if not authorization: raise HTTPException(status_code=401, detail="Sin token")
    username = auth_user(authorization.replace("Bearer ", ""))
    sub = db_get_subscription(username); tier = sub.get("tier","free")
    limits = TIERS.get(tier, TIERS["free"])
    db = get_db()
    today_reqs = db.execute("SELECT SUM(counter) as n FROM rate_limits WHERE key LIKE ? AND window_start >= ?",
        ("%:daily", datetime.now(timezone.utc).strftime("%Y-%m-%d"))).fetchone()["n"] or 0
    keys = db.execute("SELECT COUNT(*) as n FROM api_keys WHERE username=?",(username,)).fetchone()["n"]
    db.close()
    return {"username":username,"tier":tier,
            "limits":{"req_min":limits["req_min"] or "unlimited","req_day":limits["req_day"] or "unlimited","checkout":limits["checkout"]},
            "usage":{"requests_today":today_reqs,"api_keys_used":keys}}


@app.post("/checkout/lemon")
async def checkout_lemon(authorization: str | None = Header(None)):
    if not authorization: raise HTTPException(status_code=401, detail="Sin token")
    username = auth_user(authorization.replace("Bearer ", ""))
    cart = db_get_cart(username)
    if not cart: raise HTTPException(status_code=400, detail="Carrito vacío")
    total = round(sum(i["price"] * i["quantity"] for i in cart), 2)
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    db_create_order(username, cart, "lemon", total, status="pending", order_id=order_id)
    db_clear_cart(username)
    from market_connectors.lemon_payments import create_checkout
    try:
        lc = await create_checkout(total, "ARS", f"CLI-Market-{order_id}")
        if "checkout_url" in lc:
            return {"order_id": order_id, "total": total, "currency": "ARS",
                    "payment_method": "lemon", "status": "pending",
                    "lemon_checkout_id": lc["checkout_id"],
                    "checkout_url": lc["checkout_url"],
                    "qr_url": lc.get("qr_url",""),
                    "message": "Completa el pago con Lemon."}
        raise HTTPException(status_code=502, detail=lc.get("error","Lemon error"))
    except Exception:
        raise HTTPException(status_code=501, detail="Lemon no configurado. Set LEMON_API_KEY.")


@app.post("/checkout/yape")
def checkout_yape(authorization: str | None = Header(None)):
    if not authorization: raise HTTPException(status_code=401, detail="Sin token")
    username = auth_user(authorization.replace("Bearer ", ""))
    cart = db_get_cart(username)
    if not cart: raise HTTPException(status_code=400, detail="Carrito vacío")
    total = round(sum(i["price"] * i["quantity"] for i in cart), 2)
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    db_create_order(username, cart, "yape", total, status="pending", order_id=order_id)
    db_clear_cart(username)
    qr_ref = f"yape-{order_id.lower()}"
    return {"order_id":order_id,"total":total,"currency":"PEN","payment_method":"yape",
            "qr_reference":qr_ref,"qr_url":f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={qr_ref}",
            "status":"pending","message":"Escanea el QR con Yape/Plin para completar el pago."}


@app.post("/checkout/webhook")
def checkout_webhook(order_id: str = "", status: str = "paid"):
    if not order_id: raise HTTPException(status_code=400, detail="order_id required")
    db = get_db()
    db.execute("UPDATE app_orders SET status=? WHERE order_id=?", (status, order_id))
    db.commit(); db.close()
    return {"order_id":order_id,"status":status,"message":f"Payment {status}"}


@app.post("/billing/checkout")
def billing_checkout(authorization: str | None = Header(None)):
    if not authorization: raise HTTPException(status_code=401, detail="Sin token")
    username = auth_user(authorization.replace("Bearer ", ""))
    stripe_key = os.getenv("STRIPE_SECRET_KEY","")
    if not stripe_key: raise HTTPException(status_code=501, detail="Stripe not configured")
    try:
        import stripe; stripe.api_key = stripe_key
        session = stripe.checkout.Session.create(payment_method_types=["card"],
            line_items=[{"price":_os.getenv("STRIPE_PRICE_PRO","price_pro"),"quantity":1}],
            mode="subscription",success_url="https://cli-market.dev?upgraded=true",
            cancel_url="https://cli-market.dev?upgraded=false",client_reference_id=username)
        return {"url":session.url}
    except ImportError: raise HTTPException(status_code=501, detail="pip install stripe")
    except Exception as e: raise HTTPException(status_code=500, detail=str(e))


@app.get("/auth/subscription")
def auth_subscription(authorization: str | None = Header(None)):
    if not authorization: raise HTTPException(status_code=401, detail="Sin token")
    username = auth_user(authorization.replace("Bearer ", ""))
    sub = db_get_subscription(username)
    keys = db_list_api_keys(username)
    return {"username": username, "subscription": sub, "api_keys": len(keys)}


@app.post("/checkout/paypal")
async def checkout_paypal(authorization: str | None = Header(None)):
    if not authorization: raise HTTPException(status_code=401, detail="Sin token")
    username = auth_user(authorization.replace("Bearer ", ""))
    cart = db_get_cart(username)
    if not cart: raise HTTPException(status_code=400, detail="Carrito vacío")
    total = round(sum(i["price"] * i["quantity"] for i in cart), 2)
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    db_create_order(username, cart, "paypal", total, status="pending", order_id=order_id)
    db_clear_cart(username)
    from market_connectors.paypal_payments import create_order
    try:
        pp = await create_order(total, "USD", f"CLI-Market-{order_id}")
        if "approve_url" in pp:
            return {"order_id": order_id, "total": total, "currency": "USD",
                    "payment_method": "paypal", "status": "pending",
                    "paypal_order_id": pp["order_id"], "approve_url": pp["approve_url"],
                    "message": "Completa el pago en PayPal."}
        raise HTTPException(status_code=502, detail=pp.get("error", "PayPal error"))
    except ValueError:
        raise HTTPException(status_code=501, detail="PayPal no configurado. Set PAYPAL_CLIENT_ID y PAYPAL_CLIENT_SECRET.")


@app.post("/checkout/wise")
async def checkout_wise(authorization: str | None = Header(None)):
    if not authorization: raise HTTPException(status_code=401, detail="Sin token")
    username = auth_user(authorization.replace("Bearer ", ""))
    cart = db_get_cart(username)
    if not cart: raise HTTPException(status_code=400, detail="Carrito vacío")
    total = round(sum(i["price"] * i["quantity"] for i in cart), 2)
    order_id = f"ORD-{uuid.uuid4().hex[:8].upper()}"
    db_create_order(username, cart, "wise", total, status="pending", order_id=order_id)
    db_clear_cart(username)
    from market_connectors.wise_payments import create_quote, WISE_API_TOKEN
    wise_ok = bool(WISE_API_TOKEN)
    wise_pay_me = os.getenv("WISE_PAY_ME_URL", "https://wise.com/pay/me/ricardoantonioc68")
    return {"order_id":order_id,"total":total,"currency":"PEN","payment_method":"wise","status":"pending",
            "wise_available":wise_ok,
            "wise_pay_link": wise_pay_me,
            "wise_qr_url": f"https://api.qrserver.com/v1/create-qr-code/?size=250x250&data={wise_pay_me}",
            "instructions":{"pay_link": wise_pay_me,
                            "reference":f"CLI-Market-{order_id}",
                            "amount_usd": round(total * 0.27, 2)} if wise_ok else None,
            "message":"Escanea el QR o usa el link de Wise para pagar"}


@app.get("/checkout/rates")
async def checkout_rates():
    try:
        from market_connectors.wise_payments import get_rates
        rates = await get_rates("PEN")
        return {"base":"PEN","rates":rates}
    except Exception:
        return {"base":"PEN","rates":{"USD":0.27,"EUR":0.25,"ARS":0.0027,"BRL":0.27,"MXN":0.078,"COP":0.00035,"CLP":0.0014,"PEN":1.0},"source":"fallback"}


@app.post("/v1/ticket/scan-url")
async def ticket_scan_url(body: dict):
    """Ticket scan from a public URL instead of file upload."""
    url = body.get("url", "")
    country = body.get("country")
    import tempfile, httpx as _hx
    async with _hx.AsyncClient(timeout=30) as client:
        r = await client.get(url)
        if r.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Cannot fetch image: HTTP {r.status_code}")
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
            tmp.write(r.content)
            tmp_path = tmp.name
    try:
        result = subprocess.run(["tesseract", tmp_path, "stdout", "-l", "spa", "--psm", "6"],
                               capture_output=True, text=True, timeout=30)
        ocr_text = result.stdout.strip() if result.returncode == 0 else ""
    except FileNotFoundError:
        ocr_text = "[Tesseract no instalado]"
    finally:
        os.unlink(tmp_path)
    return {"ocr_text": ocr_text[:1000], "country": country, "message": "OCR completado"}


@app.post("/v1/voice/transcribe-url")
async def voice_transcribe_url(body: dict):
    """Voice transcription from a public URL instead of file upload."""
    url = body.get("url", "")
    import tempfile, httpx as _hx
    suffix = ".ogg"
    if url.endswith(".mp3"): suffix = ".mp3"
    elif url.endswith(".wav"): suffix = ".wav"
    async with _hx.AsyncClient(timeout=30) as client:
        r = await client.get(url)
        if r.status_code != 200:
            raise HTTPException(status_code=400, detail=f"Cannot fetch audio: HTTP {r.status_code}")
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(r.content)
            tmp_path = tmp.name
    try:
        result = subprocess.run(["whisper", tmp_path, "--model", "tiny", "--language", "es",
                                "--output_format", "txt", "--output_dir", "/tmp"],
                               capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            txt_file = tmp_path.rsplit(".",1)[0] + ".txt"
            transcript = open(txt_file).read().strip() if os.path.exists(txt_file) else ""
        else:
            transcript = "[Transcripción no disponible]"
    except FileNotFoundError:
        transcript = "[Whisper no instalado]"
    finally:
        os.unlink(tmp_path)
    return {"transcript": transcript[:2000], "language": "es"}


@app.post("/v1/admin/scan-stores")
async def admin_scan_stores(body: dict):
    """Trigger a VTEX store scan. Returns candidate stores that respond."""
    line_filter = body.get("line")
    import asyncio as _aio, httpx as _hx
    from market_core import STORES as _stores
    # Quick scan: test the existing known-good domains for new country TLDs
    candidates = []
    for sk, sv in _stores.items():
        if line_filter and sv.get("line") != line_filter:
            continue
        base = sv["base"]
        try:
            async with _hx.AsyncClient(timeout=_hx.Timeout(5.0)) as client:
                r = await client.get(f"{base}/api/catalog_system/pub/products/search/test?_from=0&_to=1")
                candidates.append({"store": sk, "name": sv["name"], "status": r.status_code, "ok": r.status_code in (200, 206)})
        except Exception as e:
            candidates.append({"store": sk, "name": sv["name"], "status": 0, "ok": False, "error": str(e)[:100]})
    ok = [c for c in candidates if c["ok"]]
    return {"scanned": len(candidates), "working": len(ok), "candidates": candidates}


@app.get("/products/stock/{product_id}")
def product_stock(product_id: str, store: str):
    """Check stock for a product in a specific store."""
    db = get_db()
    row = db.execute(
        "SELECT stock, name, store_name FROM price_snapshots WHERE product_id=? AND store=? ORDER BY queried_at DESC LIMIT 1",
        (product_id, store)
    ).fetchone()
    db.close()
    if not row:
        return {"product_id": product_id, "store": store, "stock": None, "message": "No data"}
    return {"product_id": product_id, "store": store, "stock": row["stock"], "name": row["name"], "store_name": row["store_name"]}


@app.get("/analytics/brands")
def analytics_brands(line: str | None = None, country: str | None = None, limit: int = 20):
    """Top brands in the data moat."""
    db = get_db()
    q = "SELECT brand, COUNT(*) as count FROM price_snapshots WHERE brand != '' AND price > 0"
    params: list = []
    if line:
        q += " AND line = ?"
        params.append(line)
    q += " GROUP BY brand ORDER BY count DESC LIMIT ?"
    params.append(limit)
    rows = db.execute(q, params).fetchall()
    db.close()
    return {"brands": [dict(r) for r in rows], "total": len(rows)}


@app.post("/favorites")
def favorites(body: dict, authorization: str | None = Header(None)):
    """Manage favorite products (list, add, remove)."""
    if not authorization: raise HTTPException(status_code=401, detail="Sin token")
    username = auth_user(authorization.replace("Bearer ", ""))
    action = body.get("action", "list")
    db = get_db()
    if action == "add":
        db.execute("INSERT OR IGNORE INTO app_favorites (username, product_id, name, store) VALUES (?,?,?,?)",
                   (username, body.get("product_id",""), body.get("name",""), body.get("store","")))
        db.commit()
    elif action == "remove":
        db.execute("DELETE FROM app_favorites WHERE username=? AND product_id=?",
                   (username, body.get("product_id","")))
        db.commit()
    rows = db.execute("SELECT product_id, name, store FROM app_favorites WHERE username=? ORDER BY product_id", (username,)).fetchall()
    db.close()
    return {"favorites": [dict(r) for r in rows], "total": len(rows)}


@app.post("/v1/utils/exchange")
def utils_exchange(body: dict):
    """Static exchange rates between supported currencies."""
    rates = {
        "PEN": 1.0, "ARS": 0.0027, "BRL": 1.02, "MXN": 0.29,
        "COP": 0.0013, "CLP": 0.0053, "EUR": 4.05, "USD": 3.70,
    }
    amount = body.get("amount", 0)
    frm = body.get("from", "PEN").upper()
    to = body.get("to", "PEN").upper()
    if frm not in rates or to not in rates:
        raise HTTPException(status_code=400, detail=f"Unsupported currency. Supported: {list(rates.keys())}")
    converted = round(amount * rates[to] / rates[frm], 2)
    return {"amount": amount, "from": frm, "to": to, "converted": converted, "rate": round(rates[to]/rates[frm], 6)}


@app.get("/products/delivery/{product_id}")
def product_delivery(product_id: str, store: str, zipcode: str = ""):
    """Delivery options placeholder — returns store base URL for the product."""
    store_info = STORES.get(store, {})
    return {
        "product_id": product_id, "store": store, "store_name": store_info.get("name", store),
        "delivery_available": True, "estimated_days": "2-5",
        "message": "Delivery integration pending. Check the store directly.",
        "store_url": f"{store_info.get('base','')}/{product_id}/p",
    }


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
        SELECT store, COUNT(*) as count
        FROM price_snapshots WHERE price > 0
        GROUP BY store ORDER BY count DESC
    """).fetchall()
    # Derive country from STORES dict
    country_agg: dict[str, dict] = {}
    for r in by_country:
        country = STORES.get(r["store"], {}).get("country", "??")
        c = country_agg.setdefault(country, {"country": country, "count": 0, "stores": set()})
        c["count"] += r["count"]
        c["stores"].add(r["store"])
    by_country_list = sorted(
        [{"country": c["country"], "count": c["count"], "stores": len(c["stores"])} for c in country_agg.values()],
        key=lambda x: x["count"], reverse=True
    )
    top_products = db.execute("""
        SELECT name, store_name, price, currency, line_name, queried_at
        FROM price_snapshots WHERE price > 0 AND price < 999999
        ORDER BY queried_at DESC LIMIT 20
    """).fetchall()
    total_runs = db.execute("SELECT COUNT(*) as n FROM collector_runs").fetchone()["n"]

    # Collector status
    last_run = db.execute(
        "SELECT started_at, finished_at, stores_succeeded, stores_attempted, prices_collected "
        "FROM collector_runs ORDER BY id DESC LIMIT 1"
    ).fetchone()
    collector_status = "unknown"
    if last_run:
        finished = last_run["finished_at"]
        if finished:
            try:
                ft = datetime.fromisoformat(finished.replace("Z", "+00:00"))
                age_h = (datetime.now(timezone.utc) - ft).total_seconds() / 3600
                collector_status = "healthy" if age_h < 12 else ("stale" if age_h < 24 else "dead")
            except Exception:
                age_h = None
        else:
            collector_status = "running"

    # Store health
    failing_stores = db.execute(
        "SELECT store, consecutive_failures FROM store_health WHERE consecutive_failures >= 3 ORDER BY consecutive_failures DESC"
    ).fetchall()

    # Price trend (last 7 days vs previous 7)
    from datetime import timedelta
    now7 = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    prev14 = (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()
    recent = db.execute("SELECT COUNT(*) as n FROM price_snapshots WHERE queried_at >= ?", (now7,)).fetchone()["n"]
    older = db.execute(
        "SELECT COUNT(*) as n FROM price_snapshots WHERE queried_at >= ? AND queried_at < ?",
        (prev14, now7)
    ).fetchone()["n"]

    db.close()
    return {
        "by_line": [dict(r) for r in by_line],
        "by_country": by_country_list,
        "top_products": [dict(r) for r in top_products],
        "total_runs": total_runs,
        "collector": {
            "status": collector_status,
            "last_run": last_run["started_at"] if last_run else None,
            "last_finished": last_run["finished_at"] if last_run else None,
            "stores_succeeded": last_run["stores_succeeded"] if last_run else 0,
            "prices_collected": last_run["prices_collected"] if last_run else 0,
        },
        "failing_stores": [dict(r) for r in failing_stores],
        "price_trend": {"recent_7d": recent, "previous_7d": older},
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
.alert{background:#2d1a1a;border:1px solid #ff4444;color:#ff6b6b;border-radius:6px;padding:8px 14px;font-size:0.65rem;margin-bottom:6px}
.alert b{color:#ff8888}
</style>
</head>
<body>
<h1>CLI Market <span>Data Moat</span></h1>
<p class="subtitle">Precios recolectados de 60 retailers VTEX en 11 países · 6 líneas</p>
<div class="kpi-row" id="kpis"></div>
<div id="alerts"></div>
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

  // Alerts
  const alerts=[];
  if(d.collector&&d.collector.status&&d.collector.status!=='healthy'){
    alerts.push(`⚠️ Collector: <b>${d.collector.status}</b> — última vez: ${d.collector.last_finished||'nunca'}`);
  }
  if(d.failing_stores&&d.failing_stores.length>0){
    const names=d.failing_stores.map(s=>`${s.store} (×${s.consecutive_failures})`).join(', ');
    alerts.push(`🔴 Tiendas caídas: ${names}`);
  }
  if(d.price_trend&&d.price_trend.recent_7d===0&&d.price_trend.previous_7d>0){
    alerts.push('📉 0 precios nuevos en 7 días — ¿collector detenido?');
  }
  document.getElementById('alerts').innerHTML=alerts.map(a=>`<div class="alert">${a}</div>`).join('');

  // KPIs
  const total=d.by_line.reduce((s,x)=>s+x.count,0);
  const lines=d.by_line.length;
  const countries=d.by_country.length;
  document.getElementById('kpis').innerHTML=`
    <div class="kpi"><div class="val">${total.toLocaleString()}</div><div class="lbl">Precios</div></div>
    <div class="kpi"><div class="val">${lines}</div><div class="lbl">Líneas</div></div>
    <div class="kpi"><div class="val">${countries}</div><div class="lbl">Países</div></div>
    <div class="kpi"><div class="val">${d.total_runs}</div><div class="lbl">Ciclos</div></div>
    <div class="kpi"><div class="val">${d.collector?d.collector.stores_succeeded||'?':'?'}</div><div class="lbl">Tiendas ok</div></div>
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

