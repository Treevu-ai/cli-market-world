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
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Header, Body
from pydantic import BaseModel

# ── Config ─────────────────────────────────────────────────────────────────

DATA_DIR = Path(os.getenv("MARKET_DATA_DIR", Path.home() / ".market"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
USERS_FILE = DATA_DIR / "users.json"
CARTS_FILE = DATA_DIR / "carts.json"
ORDERS_FILE = DATA_DIR / "orders.json"
SESSION_FILE = DATA_DIR / "session.json"
DB_FILE = DATA_DIR / "market.db"

# ── SQLite Data Moat ────────────────────────────────────────────────────────

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_FILE))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn

def init_db():
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS price_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id TEXT NOT NULL,
            name TEXT,
            brand TEXT,
            price REAL,
            list_price REAL,
            discount INTEGER,
            store TEXT NOT NULL,
            store_name TEXT,
            currency TEXT,
            line TEXT,
            line_name TEXT,
            category TEXT,
            stock INTEGER,
            url TEXT,
            queried_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_ps_product ON price_snapshots(product_id, store);
        CREATE INDEX IF NOT EXISTS idx_ps_store ON price_snapshots(store);
        CREATE INDEX IF NOT EXISTS idx_ps_line ON price_snapshots(line);
        CREATE INDEX IF NOT EXISTS idx_ps_queried ON price_snapshots(queried_at);

        CREATE TABLE IF NOT EXISTS search_queries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT NOT NULL,
            line TEXT,
            country TEXT,
            store_filter TEXT,
            num_results INTEGER DEFAULT 0,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_sq_created ON search_queries(created_at);
    """)
    db.commit()
    db.close()

def save_price_snapshot(p: dict) -> None:
    try:
        db = get_db()
        db.execute("""
            INSERT INTO price_snapshots
                (product_id, name, brand, price, list_price, discount,
                 store, store_name, currency, line, line_name, category, stock, url)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            p.get("id", p.get("product_id", "")),
            p.get("name", ""),
            p.get("brand", ""),
            p.get("price", 0),
            p.get("list_price", 0),
            p.get("discount"),
            p.get("store", ""),
            p.get("store_name", ""),
            p.get("currency", STORES.get(p.get("store", ""), {}).get("currency", "")),
            STORES.get(p.get("store", ""), {}).get("line", ""),
            p.get("line_name", ""),
            p.get("category", ""),
            p.get("stock", 0),
            p.get("url", ""),
        ))
        db.commit()
        db.close()
    except Exception:
        pass

def save_search_query(query: str, line: str | None, store: str | None, num_results: int) -> None:
    try:
        db = get_db()
        db.execute(
            "INSERT INTO search_queries (query, line, store_filter, num_results) VALUES (?,?,?,?)",
            (query, line, store, num_results)
        )
        db.commit()
        db.close()
    except Exception:
        pass

# ── Initialize ───────────────────────────────────────────────────────────────

init_db()

# ── Stores (VTEX retailers) ─────────────────────────────────────────────────
# Cada store pertenece a una línea de negocio (line).
# Para agregar un retailer nuevo: copiar un entry y cambiar base, name, country, line.

STORES = {
    # ── 🛒 SUPERMERCADOS ──
    "wong":      {"name": "Wong",       "base": "https://www.wong.pe",          "country": "PE", "currency": "PEN", "emoji": "🇵🇪", "line": "supermercados"},
    "metro":     {"name": "Metro",      "base": "https://www.metro.pe",         "country": "PE", "currency": "PEN", "emoji": "🇵🇪", "line": "supermercados"},
    "plazavea":  {"name": "Plaza Vea",  "base": "https://www.plazavea.com.pe",  "country": "PE", "currency": "PEN", "emoji": "🇵🇪", "line": "supermercados"},
    "carrefour": {"name": "Carrefour",  "base": "https://www.carrefour.com.ar", "country": "AR", "currency": "ARS", "emoji": "🇦🇷", "line": "supermercados"},
    "jumbo_ar":  {"name": "Jumbo",      "base": "https://www.jumbo.com.ar",     "country": "AR", "currency": "ARS", "emoji": "🇦🇷", "line": "supermercados"},
    "carrefour_br": {"name": "Carrefour", "base": "https://www.carrefour.com.br", "country": "BR", "currency": "BRL", "emoji": "🇧🇷", "line": "supermercados"},
    "chedraui":  {"name": "Chedraui",   "base": "https://www.chedraui.com.mx", "country": "MX", "currency": "MXN", "emoji": "🇲🇽", "line": "supermercados"},
    "heb":       {"name": "HEB",        "base": "https://www.heb.com.mx",       "country": "MX", "currency": "MXN", "emoji": "🇲🇽", "line": "supermercados"},
    "olimpica":  {"name": "Olímpica",   "base": "https://www.olimpica.com",     "country": "CO", "currency": "COP", "emoji": "🇨🇴", "line": "supermercados"},
    "exito":     {"name": "Éxito",      "base": "https://www.exito.com",         "country": "CO", "currency": "COP", "emoji": "🇨🇴", "line": "supermercados"},

    # ── 💊 FARMACIAS ──
    "drogaraia":   {"name": "Droga Raia",   "base": "https://www.drogaraia.com.br",   "country": "BR", "currency": "BRL", "emoji": "🇧🇷", "line": "farmacias"},
    "drogasil":    {"name": "Drogasil",     "base": "https://www.drogasil.com.br",    "country": "BR", "currency": "BRL", "emoji": "🇧🇷", "line": "farmacias"},

    # ── 📱 ELECTRO Y TECNOLOGÍA ──
    "magazineluiza": {"name": "Magazine Luiza", "base": "https://www.magazineluiza.com.br", "country": "BR", "currency": "BRL", "emoji": "🇧🇷", "line": "electro"},
    "motorola_br":   {"name": "Motorola",       "base": "https://www.motorola.com.br",       "country": "BR", "currency": "BRL", "emoji": "🇧🇷", "line": "electro"},

    # ── 👕 MODA ──
    "renner": {"name": "Lojas Renner", "base": "https://www.lojasrenner.com.br", "country": "BR", "currency": "BRL", "emoji": "🇧🇷", "line": "moda"},

    # ── ⚽ DEPORTES ──
    "centauro": {"name": "Centauro", "base": "https://www.centauro.com.br", "country": "BR", "currency": "BRL", "emoji": "🇧🇷", "line": "deportes"},

    # ── 🏠 HOGAR ──
    "homecenter": {"name": "Homecenter", "base": "https://www.homecenter.com.co", "country": "CO", "currency": "COP", "emoji": "🇨🇴", "line": "hogar"},
}

# ── Lines (verticals) ────────────────────────────────────────────────────────

LINES = {
    "supermercados": {"name": "Supermercados",            "emoji": "🛒", "description": "Alimentos, bebidas y consumo diario"},
    "farmacias":     {"name": "Farmacias y Salud",        "emoji": "💊", "description": "Medicamentos, bienestar y cuidado personal"},
    "electro":       {"name": "Electro y Tecnología",     "emoji": "📱", "description": "Electrónicos, electrodomésticos y gadgets"},
    "moda":          {"name": "Moda y Calzado",            "emoji": "👕", "description": "Ropa, calzado y accesorios"},
    "deportes":      {"name": "Deportes y Fitness",        "emoji": "⚽", "description": "Artículos deportivos, ropa deportiva y equipo"},
    "hogar":         {"name": "Hogar y Construcción",      "emoji": "🏠", "description": "Mejoramiento del hogar, muebles, ferretería"},
}

COUNTRIES = {
    "PE": {"name": "Perú",       "stores": [k for k, v in STORES.items() if v["country"] == "PE"]},
    "AR": {"name": "Argentina",  "stores": [k for k, v in STORES.items() if v["country"] == "AR"]},
    "BR": {"name": "Brasil",     "stores": [k for k, v in STORES.items() if v["country"] == "BR"]},
    "MX": {"name": "México",     "stores": [k for k, v in STORES.items() if v["country"] == "MX"]},
    "CO": {"name": "Colombia",   "stores": [k for k, v in STORES.items() if v["country"] == "CO"]},
}
DEFAULT_STORES = list(STORES.keys())
PAGE_SIZE = 20

app = FastAPI(
    title="Agentic Market API",
    description="AI-native commerce infrastructure — 17 retailers across 6 verticals in 5 LATAM countries. MCP-native. Agent-ready.",
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
        "currency": STORES[store]["currency"],
        "url": f"{STORES[store]['base']}/{p.get('linkText', '')}/p",
    }


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
        "lines": len(LINES),
        "countries": len(COUNTRIES),
        "docs": "/docs",
    }


@app.get("/lines")
def list_lines():
    """Lista todas las líneas de negocio con sus retailers."""
    result = {}
    for line_id, line_meta in LINES.items():
        line_stores = {
            k: {"name": v["name"], "country": v["country"], "currency": v["currency"], "emoji": v["emoji"]}
            for k, v in STORES.items() if v["line"] == line_id
        }
        result[line_id] = {
            "name": line_meta["name"],
            "emoji": line_meta["emoji"],
            "description": line_meta["description"],
            "stores": line_stores,
            "total_stores": len(line_stores),
        }
    return {"lines": result, "total": len(result)}


@app.get("/stores")
def list_stores(country: str | None = None, line: str | None = None):
    """Lista todas las tiendas. Filtrar por país (?country=PE) o línea (?line=supermercados)."""
    result = {}
    for key, s in STORES.items():
        if country and s["country"] != country.upper():
            continue
        if line and s["line"] != line:
            continue
        result[key] = {
            "name": s["name"],
            "country": s["country"],
            "currency": s["currency"],
            "line": s["line"],
            "line_name": LINES[s["line"]]["name"],
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
    # Filtrar por línea si se especifica
    if body.line and body.line in LINES:
        stores = [s for s in stores if STORES[s]["line"] == body.line]
    results = []
    for store in stores:
        try:
            raw = await fetch_store(store, body.query, body.page, body.limit)
            for p in raw:
                prod = product_from_json(p, store)
                prod["line"] = STORES[store]["line"]
                prod["line_name"] = LINES[STORES[store]["line"]]["name"]
                results.append(prod)
        except Exception:
            continue
    results.sort(key=lambda p: p["price"] if p["price"] > 0 else float("inf"))

    # ── Data moat: persist every price seen ──
    for p in results:
        save_price_snapshot(p)
    save_search_query(body.query, body.line, body.store, len(results))

    return {"query": body.query, "results": results, "total": len(results)}


@app.post("/products/compare")
async def compare_products(body: SearchRequest):
    stores = [body.store] if body.store else DEFAULT_STORES
    stores = [s for s in stores if s in STORES]
    if body.line and body.line in LINES:
        stores = [s for s in stores if STORES[s]["line"] == body.line]
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


@app.get("/categories/{store}")
async def category_tree(store: str):
    """Navegación por categorías de una tienda VTEX."""
    if store not in STORES:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(f"{STORES[store]['base']}/api/catalog_system/pub/category/tree/5")
        return resp.json()


@app.post("/products/category/{store}/{category_id}")
async def search_by_category(store: str, category_id: str, limit: int = 20):
    """Buscar productos por categoría en una tienda."""
    if store not in STORES:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    base = STORES[store]["base"]
    url = f"{base}/api/catalog_system/pub/products/search?fq=C:/{category_id}/&_from=0&_to={limit-1}"
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get(url)
        resp.raise_for_status()
        raw = resp.json()
        return {
            "store": store,
            "category_id": category_id,
            "results": [product_from_json(p, store) for p in raw],
            "total": len(raw),
        }


@app.get("/products/barcode/{code}")
async def barcode_lookup(code: str):
    """Buscar producto por código de barras en Open Food Facts."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"https://world.openfoodfacts.org/api/v0/product/{code}.json",
            headers={"User-Agent": "AgenticMarket/1.0"}
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Open Food Facts no disponible")
        data = resp.json()
        if data.get("status") == 0:
            raise HTTPException(status_code=404, detail="Producto no encontrado")
        p = data["product"]
        return {
            "barcode": code,
            "name": p.get("product_name", ""),
            "brand": p.get("brands", ""),
            "category": p.get("categories", ""),
            "nutriscore": p.get("nutriscore_grade", "").upper(),
            "image": p.get("image_url", ""),
            "ingredients": p.get("ingredients_text", "")[:300] if p.get("ingredients_text") else None,
        }


@app.get("/products/enrich")
async def enrich_products(query: str = "leche", limit: int = 5):
    """Enriquecer búsqueda con datos de Open Food Facts."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            "https://world.openfoodfacts.org/cgi/search.pl",
            params={"search_terms": query, "search_simple": 1, "json": 1, "page_size": limit},
            headers={"User-Agent": "AgenticMarket/1.0"}
        )
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="Open Food Facts no disponible")
        data = resp.json()
        results = []
        for p in data.get("products", []):
            results.append({
                "name": p.get("product_name", ""),
                "brand": p.get("brands", ""),
                "category": p.get("categories", ""),
                "nutriscore": (p.get("nutriscore_grade") or "").upper(),
                "image": p.get("image_url", ""),
                "barcode": p.get("code", ""),
            })
        return {"query": query, "source": "openfoodfacts", "total": data.get("count", 0), "results": results}


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


@app.delete("/cart/{product_id}")
def cart_remove(product_id: str, authorization: str | None = Header(None)):
    """Elimina un producto del carrito por su ID."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Sin token")
    token = authorization.replace("Bearer ", "")
    username = auth_user(token)
    carts = get_carts()
    cart = carts.get(username, [])
    item = next((i for i in cart if i["cart_id"] == product_id or i["product_id"] == product_id), None)
    if not item:
        raise HTTPException(status_code=404, detail="Producto no encontrado en el carrito")
    cart.remove(item)
    save_json(CARTS_FILE, carts)
    total = round(sum(i["price"] * i["quantity"] for i in cart), 2)
    return {"message": "Producto eliminado del carrito", "cart": cart, "total": total, "items": len(cart)}


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


@app.get("/analytics/price-history")
def price_history(product_id: str | None = None, store: str | None = None, line: str | None = None, limit: int = 50):
    """Consultar histórico de precios capturados (data moat)."""
    db = get_db()
    q = "SELECT * FROM price_snapshots WHERE 1=1"
    params: list = []
    if product_id:
        q += " AND product_id = ?"
        params.append(product_id)
    if store:
        q += " AND store = ?"
        params.append(store)
    if line:
        q += " AND line = ?"
        params.append(line)
    q += " ORDER BY queried_at DESC LIMIT ?"
    params.append(limit)
    rows = db.execute(q, params).fetchall()
    db.close()
    return {
        "count": len(rows),
        "snapshots": [dict(r) for r in rows],
    }


@app.get("/analytics/stats")
def analytics_stats():
    """Estadísticas del data moat."""
    db = get_db()
    total_snapshots = db.execute("SELECT COUNT(*) as n FROM price_snapshots").fetchone()["n"]
    total_queries = db.execute("SELECT COUNT(*) as n FROM search_queries").fetchone()["n"]
    stores_tracked = db.execute("SELECT COUNT(DISTINCT store) as n FROM price_snapshots").fetchone()["n"]
    products_tracked = db.execute("SELECT COUNT(DISTINCT product_id) as n FROM price_snapshots").fetchone()["n"]
    latest = db.execute("SELECT MAX(queried_at) as t FROM price_snapshots").fetchone()["t"]
    db.close()
    return {
        "total_price_snapshots": total_snapshots,
        "total_search_queries": total_queries,
        "unique_stores_tracked": stores_tracked,
        "unique_products_tracked": products_tracked,
        "latest_snapshot_at": latest,
    }


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
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8765"))
    print(f"Agentic Market API → http://{host}:{port}")
    print(f"   Docs → http://{host}:{port}/docs")
    print(f"   Data → {DATA_DIR}")
    uvicorn.run(app, host=host, port=port, log_level="info")


if __name__ == "__main__":
    main()
