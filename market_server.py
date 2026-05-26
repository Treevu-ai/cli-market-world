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

from contextlib import asynccontextmanager

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
    ensure_db_initialized,
    logger as log,
)

logger = log.getChild("server")

# Server-only helpers (auth, rate limit, hashing) moved to server_deps.py to
# keep this module focused on app wiring and endpoints. Re-exported below so
# tests and external code that import them from market_server keep working.
from server_deps import (
    auth_user, hash_password, verify_password,
    check_auth_brute_force, record_auth_failure, require_user,
    check_rate_limit,
    DEFAULT_TOKEN,
    RATE_LIMIT_MIN, RATE_LIMIT_DAY, RATE_LIMIT_WINDOW,
    AUTH_MAX_ATTEMPTS, AUTH_WINDOW,
    _auth_attempts,
)


@asynccontextmanager
async def lifespan(_app):
    """Initialize DB schema and migrate legacy JSON data on startup.

    Replaces the previous side-effect-at-import pattern. Idempotent.
    """
    ensure_db_initialized()
    try:
        db_migrate_from_json()
    except Exception as e:
        logger.warning("JSON migration skipped: %s", e)
    yield

# ── FastAPI app ────────────────────────────────────────────────────────────

app = FastAPI(
    title="CLI Market API",
    description="AI-native commerce infrastructure — 100 retailers across 12 verticals in 10 countries. MCP-native. Agent-ready.",
    version="1.0.25",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "https://cli-market.dev,http://localhost:3000").split(","),
    allow_credentials=True,
    allow_methods=["GET","POST","PUT","DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# ── Background collector interval ──────────

COLLECTOR_INTERVAL = int(os.getenv("COLLECT_INTERVAL_HOURS", "8"))


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


# ── Routers ────────────────────────────────────────────────────────────────
# Health / catalog endpoints live in routers/health.py

from routers.health import router as health_router
app.include_router(health_router)


# ── Auth router ────────────────────────────────────────────────────────────
# /auth/login, /auth/whoami, /auth/keys{,/x}, /auth/subscription
# moved to routers/auth.py

from routers.auth import router as auth_router
app.include_router(auth_router)


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


# ── Cart + Orders + Checkout routers ──────────────────────────────────────
# /cart{,/add,/update,/{id}}, /checkout, /orders{,/{id},/{id}/receipt,/reorder}
# moved to routers/cart.py and routers/orders.py

from routers.cart import router as cart_router
from routers.orders import router as orders_router
app.include_router(cart_router)
app.include_router(orders_router)


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


# ── Dashboard router ──────────────────────────────────────────────────────
# /dashboard, /dashboard/data, /dashboard/usage moved to routers/dashboard.py

from routers.dashboard import router as dashboard_router
app.include_router(dashboard_router)


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


# ── Admin router ──────────────────────────────────────────────────────────
# /admin/debug-fetch, /admin/collect, /v1/admin/scan-stores moved to routers/admin.py

from routers.admin import router as admin_router
app.include_router(admin_router)


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


# (dashboard endpoints + HTML moved to routers/dashboard.py and routers/dashboard_html.py)

# ── Run ────────────────────────────────────────────────────────────────────

def main():
    import uvicorn, threading, time, subprocess, sys as _sys
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8765"))
    
    logger.info(f"CLI Market API starting on http://{host}:{port}")
    logger.info(f"  {len(STORES)} stores, {len(LINES)} lines, {len(COUNTRIES)} countries")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()

