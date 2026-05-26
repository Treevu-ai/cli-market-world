#!/usr/bin/env python3
"""
collect_prices.py — VTEX price collector for CLI Market data moat.

PostgreSQL (DATABASE_URL) or SQLite fallback.
Railway-compatible: set DATABASE_URL=${{Postgres.DATABASE_URL}}

Usage:
    python collect_prices.py              # run once
    python collect_prices.py --daemon     # run every 4h
    python collect_prices.py --status     # collection stats
    python collect_prices.py --report     # latest prices per line
"""

import asyncio, json, os, sqlite3, sys, time
from collections import defaultdict
from datetime import datetime, timezone
import httpx

from market_core import STORES, DATA_DIR, DB_FILE, logger as log, product_from_json as _pfj, fetch_store as _fetch_store

logger = log.getChild("collector")

DATABASE_URL = os.getenv("DATABASE_URL", "")

PARALLEL = int(os.getenv("COLLECT_PARALLEL", "50"))
REQUEST_DELAY = float(os.getenv("COLLECT_DELAY", "0.15"))
QUERY_TIMEOUT = 10.0
DAEMON_INTERVAL = int(os.getenv("COLLECT_INTERVAL_HOURS", "4"))

LINES = {
    "supermercados":{"name":"Supermercados"}, "farmacias":{"name":"Farmacias y Salud"},
    "electro":{"name":"Electro y Tecnología"}, "moda":{"name":"Moda y Accesorios"},
    "deportes":{"name":"Deportes y Outdoor"}, "hogar":{"name":"Hogar y Construcción"},
    "financiero":{"name":"Financiero y Seguros"}, "automotriz":{"name":"Automotriz"},
    "libros":{"name":"Libros y Educación"}, "viajes":{"name":"Viajes y Turismo"},
    "hogar_construccion":{"name":"Hogar y Construcción"}, "educacion":{"name":"Educación Ejecutiva"},
}

SEED_QUERIES = [
    # ═══════════════════════════════════════════════════════════════════════════
    # 🛒 Supermercados (14 tiendas)
    # ═══════════════════════════════════════════════════════════════════════════
    ("leche","supermercados"),("arroz","supermercados"),("aceite","supermercados"),("azucar","supermercados"),("huevos","supermercados"),
    ("pan","supermercados"),("cafe","supermercados"),("pollo","supermercados"),("carne","supermercados"),("queso","supermercados"),
    ("yogur","supermercados"),("mantequilla","supermercados"),("detergente","supermercados"),("jabon","supermercados"),
    ("papel higienico","supermercados"),("pasta","supermercados"),("agua","supermercados"),("cerveza","supermercados"),("vino","supermercados"),
    ("gaseosa","supermercados"),("atun","supermercados"),("fideos","supermercados"),
    ("galletitas","supermercados"),("yerba","supermercados"),
    ("desodorante","supermercados"),("shampoo","supermercados"),
    ("jamon","supermercados"),("salchicha","supermercados"),
    ("helado","supermercados"),("congelados","supermercados"),
    ("harina","supermercados"),("salsa","supermercados"),("conservas","supermercados"),
    ("milk","supermercados"),("bread","supermercados"),("eggs","supermercados"),
    ("rice","supermercados"),("chicken","supermercados"),("coffee","supermercados"),
    ("oil","supermercados"),("sugar","supermercados"),("butter","supermercados"),
    ("leite","supermercados"),("açúcar","supermercados"),("queijo","supermercados"),
    ("frango","supermercados"),("cerveja","supermercados"),("pão","supermercados"),
    # ═══════════════════════════════════════════════════════════════════════════
    # 💊 Farmacias (2 tiendas: Pacheco BR, Farmatodo MX)
    # ═══════════════════════════════════════════════════════════════════════════
    ("paracetamol","farmacias"),("ibuprofeno","farmacias"),("vitamina c","farmacias"),
    ("protector solar","farmacias"),("shampoo","farmacias"),("crema","farmacias"),
    ("jabon liquido","farmacias"),("pañales","farmacias"),
    ("aspirina","farmacias"),("omeprazol","farmacias"),("loratadina","farmacias"),
    ("curitas","farmacias"),("alcohol","farmacias"),("termometro","farmacias"),
    ("mascarilla","farmacias"),("gel antibacterial","farmacias"),
    ("antigripal","farmacias"),("antidiarreico","farmacias"),
    ("preservativos","farmacias"),("prueba embarazo","farmacias"),
    ("agua oxigenada","farmacias"),("algodon","farmacias"),
    ("dipirona","farmacias"),("losartana","farmacias"),

    # ═══════════════════════════════════════════════════════════════════════════
    # ⚡ Electro (9 tiendas: Motorola AR/BR/MX/CL, Electrolux AR/CL, Whirlpool AR/IT/FR)
    # ═══════════════════════════════════════════════════════════════════════════
    # Smartphones / Motorola
    ("moto g","electro"),("moto edge","electro"),("razr","electro"),
    ("motorola","electro"),("celular","electro"),("telefono","electro"),
    ("smartphone","electro"),("phone","electro"),("iphone","electro"),
    ("xiaomi","electro"),("samsung galaxy","electro"),
    # Accesorios
    ("auriculares","electro"),("cargador","electro"),("funda","electro"),
    ("cable","electro"),("bateria","electro"),("headphones","electro"),
    ("parlante","electro"),("tablet","electro"),("laptop","electro"),
    ("smartwatch","electro"),("monitor","electro"),("teclado","electro"),
    ("mouse","electro"),("impresora","electro"),
    # Línea blanca — Electrolux / Whirlpool
    ("lavarropas","electro"),("heladera","electro"),("cocina","electro"),
    ("aspiradora","electro"),("refrigerador","electro"),("horno","electro"),
    ("microondas","electro"),("lavadora","electro"),("secarropas","electro"),
    ("lavaplatos","electro"),("freezer","electro"),("aire acondicionado","electro"),
    ("purificador","electro"),("cafetera","electro"),("licuadora","electro"),
    ("plancha","electro"),("tostadora","electro"),("batidora","electro"),
    # Samsung
    ("galaxy","electro"),("samsung tv","electro"),("samsung monitor","electro"),
    ("galaxy watch","electro"),("galaxy buds","electro"),("samsung tablet","electro"),
    ("samsung notebook","electro"),("samsung soundbar","electro"),
    # English
    ("fridge","electro"),("washer","electro"),("dryer","electro"),
    ("dishwasher","electro"),("stove","electro"),("vacuum","electro"),
    # Italiano (Whirlpool IT)
    ("frigorifero","electro"),("lavatrice","electro"),("aspirapolvere","electro"),
    ("forno","electro"),
    # Francés (Whirlpool FR)
    ("réfrigérateur","electro"),("lave-linge","electro"),("aspirateur","electro"),
    ("four","electro"),("téléphone","electro"),
    # Portugués (Motorola BR)
    ("celular motorola","electro"),("fone","electro"),("carregador","electro"),
    ("geladeira","electro"),("fogão","electro"),("aspirador","electro"),
    ("notebook","electro"),("monitor gamer","electro"),

    # ═══════════════════════════════════════════════════════════════════════════
    # 👗 Moda (2 tiendas: C&A BR, Hering BR)
    # ═══════════════════════════════════════════════════════════════════════════
    ("camiseta","moda"),("jeans","moda"),("vestido","moda"),("chaqueta","moda"),
    ("zapatos","moda"),("pantalon","moda"),("camisa","moda"),("short","moda"),
    ("blusa","moda"),("falda","moda"),("sueter","moda"),
    ("bufanda","moda"),("traje baño","moda"),("gorra","moda"),
    ("sandalias","moda"),("tenis","moda"),("accesorios","moda"),
    ("bolso mujer","moda"),("cinturon","moda"),("calcetines","moda"),
    ("ropa interior","moda"),("pijama","moda"),("bikini","moda"),
    # English / Portuguese
    ("tshirt","moda"),("dress","moda"),("shoes","moda"),("jacket","moda"),
    ("calça","moda"),("sapato","moda"),("bermuda","moda"),
    ("blusa feminina","moda"),("jaqueta","moda"),("saia","moda"),
    ("camisa social","moda"),("tenis esportivo","moda"),("chinelo","moda"),
    # Shopify
    ("leggings","moda"),("sneakers","moda"),("hoodie","moda"),
    ("running","moda"),("wool","moda"),("lipstick","moda"),
    ("eyeshadow","moda"),("shorts","moda"),("sports bra","moda"),

    # ═══════════════════════════════════════════════════════════════════════════
    # 🔨 Hogar (2 tiendas: Easy AR, Promart PE)
    # ═══════════════════════════════════════════════════════════════════════════
    ("taladro","hogar"),("sarten","hogar"),("silla","hogar"),("lampara","hogar"),
    ("cortina","hogar"),("pintura","hogar"),("martillo","hogar"),
    ("destornillador","hogar"),("toalla","hogar"),("sabana","hogar"),
    ("ceramica","hogar"),("griferia","hogar"),("inodoro","hogar"),
    ("lavatorio","hogar"),("ducha","hogar"),("piso flotante","hogar"),
    ("puerta","hogar"),("ventana","hogar"),("escalera","hogar"),
    ("tornillo","hogar"),("tarugo","hogar"),("cinta","hogar"),
    ("mueble","hogar"),("cama","hogar"),("colchon","hogar"),
    ("jardin","hogar"),("maceta","hogar"),("manguera","hogar"),
    ("pala","hogar"),("balde","hogar"),("clavo","hogar"),
    ("bisagra","hogar"),("cerradura","hogar"),("enchufe","hogar"),
    ("foco","hogar"),("cable electrico","hogar"),

    # ═══════════════════════════════════════════════════════════════════════════
    # 🏬 Departamentales (1 tienda: Coppell AR)
    # ═══════════════════════════════════════════════════════════════════════════
    ("sofa","departamentales"),("cama","departamentales"),
    ("perfume","departamentales"),("reloj","departamentales"),
    ("bolso","departamentales"),("mochila","departamentales"),
    ("juguete","departamentales"),("maquillaje","departamentales"),
    ("televisor","departamentales"),("celular","departamentales"),
    ("zapatillas","departamentales"),("ropa","departamentales"),
    ("mueble","departamentales"),("colchon","departamentales"),
    ("electrodomestico","departamentales"),("bicicleta","departamentales"),
    ("notebook","departamentales"),("auriculares","departamentales"),
]

# ═══════════════════════════════════════════════════════════════════════════════
# 🔬 Query expansion — line-specific modifiers to increase surface area
# ═══════════════════════════════════════════════════════════════════════════════

EXPANSION_FACTOR = int(os.getenv("COLLECT_EXPANSION", "3"))

QUERY_MODIFIERS: dict[str, list[str]] = {
    "supermercados": [
        "entero", "descremado", "light", "integral", "sin lactosa",
        "organico", "premium", "familiar", "en polvo", "en lata",
        "sin tacc", "zero", "clasico", "suave", "fuerte",
        "x1", "x2", "x6", "pack",
    ],
    "farmacias": [
        "500mg", "100mg", "infantil", "adulto", "forte",
        "caja", "gel", "crema", "spray", "liquido",
        "24hs", "12hs", "dosis unica",
    ],
    "electro": [
        "5g", "128gb", "256gb", "pro", "lite", "ultra",
        "smart", "inalambrico", "bluetooth", "usb",
        "gamer", "4k", "portatil", "digital", "automatico",
        "60hz", "144hz", "ips", "oled",
    ],
    "moda": [
        "mujer", "hombre", "niño", "niña", "unisex",
        "talle m", "talle l", "talle xl", "talle s",
        "algodon", "jean", "cuero", "lino",
        "estampado", "liso", "bordado",
    ],
    "hogar": [
        "electrico", "manual", "profesional", "industrial",
        "12v", "220v", "acero", "plastico", "madera",
        "30cm", "50cm", "1m", "blanco", "negro",
        "impermeable", "antideslizante",
    ],
    "departamentales": [
        "2 plazas", "1 plaza", "king size", "queen",
        "led", "smart tv", "inalambrico", "bluetooth",
        "infantil", "adulto", "grande", "mediano",
    ],
}

EXACT_QUERIES: set[str] = {
    "moto g", "moto edge", "razr", "iphone", "xiaomi",
    "samsung galaxy", "celular motorola", "monitor gamer",
    "dipirona", "losartana", "omeprazol", "loratadina",
    "frigorifero", "lavatrice", "aspirapolvere",
    "réfrigérateur", "lave-linge", "aspirateur",
}

def expand_queries(base: list[tuple[str, str]], cycle: int = 0) -> list[tuple[str, str]]:
    """Expand base queries with line-specific modifiers. Rotates modifier subset per cycle."""
    if EXPANSION_FACTOR <= 0:
        return list(base)
    expanded = list(base)
    seen: set[str] = {q for q, _ in base}
    for query, line in base:
        if query in EXACT_QUERIES:
            continue
        modifiers = QUERY_MODIFIERS.get(line, [])
        if not modifiers:
            continue
        start = (cycle * EXPANSION_FACTOR) % max(len(modifiers), 1)
        picked = [modifiers[(start + i) % len(modifiers)] for i in range(EXPANSION_FACTOR)]
        for mod in picked:
            variant = f"{query} {mod}"
            if variant not in seen:
                seen.add(variant)
                expanded.append((variant, line))
    return expanded


# ═══════════════════════════════════════════════════════════════════════════════
# 🧠 Feedback loop — data-moat-driven queries from existing price_snapshots
# ═══════════════════════════════════════════════════════════════════════════════

FEEDBACK_LIMIT = int(os.getenv("COLLECT_FEEDBACK", "30"))
FEEDBACK_DAYS = int(os.getenv("COLLECT_FEEDBACK_DAYS", "7"))
FEEDBACK_MIN_COUNT = int(os.getenv("COLLECT_FEEDBACK_MIN", "3"))

def _dedup_seed_terms() -> set[str]:
    terms: set[str] = set()
    for q, _ in SEED_QUERIES:
        terms.add(q.lower())
        for word in q.lower().split():
            if len(word) >= 3:
                terms.add(word)
    return terms

def get_feedback_queries(db) -> list[tuple[str, str]]:
    """Extract top product names from data moat — unified PG/SQLite path."""
    feedback: list[tuple[str, str]] = []
    seed_terms = _dedup_seed_terms()
    per_line = max(1, FEEDBACK_LIMIT // max(len(QUERY_MODIFIERS), 1))
    lines = list(QUERY_MODIFIERS.keys())
    for line in lines:
        try:
            rows = db.execute("""
                SELECT name, COUNT(*) as freq
                FROM price_snapshots
                WHERE line = ? AND price > 0
                  AND queried_at >= datetime('now', ?)
                GROUP BY name
                HAVING COUNT(*) >= ?
                ORDER BY freq DESC
                LIMIT ?
            """, (line, f"-{FEEDBACK_DAYS} days", FEEDBACK_MIN_COUNT, per_line + 2)).fetchall()
        except Exception:
            continue
        for r in rows:
            name = str(r["name"]).strip().lower()
            query = " ".join(name.split()[:3])
            if len(query) < 3:
                continue
            if query in seed_terms:
                continue
            words = set(query.split())
            if len(words & seed_terms) >= len(words) * 0.75:
                continue
            if query not in seed_terms:
                seed_terms.add(query)
                feedback.append((query, line))
    return feedback[:FEEDBACK_LIMIT]


def build_query_list(db=None, cycle: int = 0) -> list[tuple[str, str]]:
    """Build the full query list: expanded seed + feedback from data moat."""
    queries = expand_queries(SEED_QUERIES, cycle)
    if db and FEEDBACK_LIMIT > 0:
        try:
            fb = get_feedback_queries(db)
            if fb:
                logger.info("Feedback: %d data-moat queries injected", len(fb))
                queries.extend(fb)
        except Exception as e:
            logger.warning("Feedback queries failed: %s", e)
    return queries


def _get_feedback_db():
    """Get a DB connection for feedback queries. Returns None if DB unavailable."""
    try:
        from market_core import get_db
        db = get_db()
        # Verify the price_snapshots table exists
        db.execute("SELECT 1 FROM price_snapshots LIMIT 1")
        return db
    except Exception:
        return None


# ── Database: PostgreSQL or SQLite ──────────────────────────────────────────

def _pg_host_ok(url: str) -> bool:
    import re, socket as _sock
    m = re.search(r"@([^:/]+)", url) or re.search(r"://([^:/]+)", url)
    if not m: return False
    try: _sock.getaddrinfo(m.group(1), 5432); return True
    except _sock.gaierror: return False

USE_PG = bool(DATABASE_URL) and _pg_host_ok(DATABASE_URL)

if USE_PG:
    import asyncpg
    _pg_pool = None

    async def get_pool():
        global _pg_pool
        if _pg_pool is None:
            _pg_pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
        return _pg_pool

    async def init_schema():
        pool = await get_pool()
        async with pool.acquire() as c:
            await c.execute("""
                CREATE TABLE IF NOT EXISTS price_snapshots (
                    id SERIAL PRIMARY KEY, product_id TEXT NOT NULL,
                    name TEXT, brand TEXT, price DOUBLE PRECISION, list_price DOUBLE PRECISION,
                    discount INTEGER, store TEXT NOT NULL, store_name TEXT, currency TEXT,
                    line TEXT, line_name TEXT, category TEXT, stock INTEGER, url TEXT,
                    queried_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    UNIQUE(product_id, store)
                );
                CREATE INDEX IF NOT EXISTS idx_ps_store ON price_snapshots(store);
                CREATE INDEX IF NOT EXISTS idx_ps_line ON price_snapshots(line);
                CREATE TABLE IF NOT EXISTS collector_runs (
                    id SERIAL PRIMARY KEY, started_at TIMESTAMPTZ DEFAULT NOW(),
                    finished_at TIMESTAMPTZ, stores_attempted INT DEFAULT 0,
                    stores_succeeded INT DEFAULT 0, prices_collected INT DEFAULT 0, errors TEXT
                );
                CREATE TABLE IF NOT EXISTS store_health (
                    store TEXT PRIMARY KEY, last_success TIMESTAMPTZ, last_error TIMESTAMPTZ,
                    consecutive_failures INT DEFAULT 0, total_requests INT DEFAULT 0,
                    total_successes INT DEFAULT 0
                );
            """)

    async def pg_insert(conn, prod):
        await conn.execute("""
            INSERT INTO price_snapshots (product_id,name,brand,price,list_price,discount,store,store_name,currency,line,line_name,category,stock,url)
            VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14)
            ON CONFLICT (product_id,store) DO UPDATE SET price=EXCLUDED.price, list_price=EXCLUDED.list_price, discount=EXCLUDED.discount, stock=EXCLUDED.stock, queried_at=NOW()
        """, prod["product_id"],prod["name"],prod["brand"],prod["price"],prod["list_price"],prod["discount"],
           prod["store"],prod["store_name"],prod["currency"],prod["line"],prod["line_name"],prod["category"],prod["stock"],prod["url"])

    async def pg_health(conn, store, ok):
        if ok:
            await conn.execute("INSERT INTO store_health (store,last_success,total_requests,total_successes) VALUES ($1,NOW(),1,1) ON CONFLICT(store) DO UPDATE SET last_success=NOW(),total_requests=store_health.total_requests+1,total_successes=store_health.total_successes+1", store)
        else:
            await conn.execute("INSERT INTO store_health (store,last_error,consecutive_failures,total_requests) VALUES ($1,NOW(),1,1) ON CONFLICT(store) DO UPDATE SET last_error=NOW(),consecutive_failures=store_health.consecutive_failures+1,total_requests=store_health.total_requests+1", store)

    async def pg_run_start(conn, n):
        return (await conn.fetchrow("INSERT INTO collector_runs (stores_attempted) VALUES ($1) RETURNING id", n))["id"]

    async def pg_run_end(conn, rid, ok, total, errs):
        await conn.execute("UPDATE collector_runs SET finished_at=NOW(), stores_succeeded=$1, prices_collected=$2, errors=$3 WHERE id=$4", ok, total, errs, rid)

else:
    def get_sqlite():
        c = sqlite3.connect(str(DB_FILE)); c.row_factory = sqlite3.Row
        c.execute("PRAGMA journal_mode=WAL"); c.execute("PRAGMA busy_timeout=5000"); return c

    def init_schema_sqlite():
        db = get_sqlite()
        # Self-healing: add UNIQUE constraint if missing (fixes old DBs created before 2026-05-26)
        try:
            db.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_ps_product_store ON price_snapshots(product_id, store)")
        except Exception:
            pass
        db.executescript("""
            CREATE TABLE IF NOT EXISTS price_snapshots (id INTEGER PRIMARY KEY AUTOINCREMENT, product_id TEXT NOT NULL, name TEXT, brand TEXT, price REAL, list_price REAL, discount INTEGER, store TEXT NOT NULL, store_name TEXT, currency TEXT, line TEXT, line_name TEXT, category TEXT, stock INTEGER, url TEXT, queried_at TEXT DEFAULT (datetime('now')), UNIQUE(product_id, store));
            CREATE INDEX IF NOT EXISTS idx_ps_store ON price_snapshots(store);
            CREATE INDEX IF NOT EXISTS idx_ps_line ON price_snapshots(line);
            CREATE TABLE IF NOT EXISTS collector_runs (id INTEGER PRIMARY KEY AUTOINCREMENT, started_at TEXT, finished_at TEXT, stores_attempted INT DEFAULT 0, stores_succeeded INT DEFAULT 0, prices_collected INT DEFAULT 0, errors TEXT);
            CREATE TABLE IF NOT EXISTS store_health (store TEXT PRIMARY KEY, last_success TEXT, last_error TEXT, consecutive_failures INT DEFAULT 0, total_requests INT DEFAULT 0, total_successes INT DEFAULT 0);
        """)
        return db

    def sq_insert(db, prod):
        db.execute("INSERT INTO price_snapshots (product_id,name,brand,price,list_price,discount,store,store_name,currency,line,line_name,category,stock,url,queried_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now')) ON CONFLICT(product_id,store) DO UPDATE SET price=excluded.price,list_price=excluded.list_price,discount=excluded.discount,stock=excluded.stock,queried_at=datetime('now')",
            (prod["product_id"],prod["name"],prod["brand"],prod["price"],prod["list_price"],prod["discount"],prod["store"],prod["store_name"],prod["currency"],prod["line"],prod["line_name"],prod["category"],prod["stock"],prod["url"]))

    def sq_health(db, store, ok):
        if ok: db.execute("INSERT INTO store_health (store,last_success,total_requests,total_successes) VALUES (?,datetime('now'),1,1) ON CONFLICT(store) DO UPDATE SET last_success=datetime('now'),total_requests=total_requests+1,total_successes=total_successes+1",(store,))
        else: db.execute("INSERT INTO store_health (store,last_error,consecutive_failures,total_requests) VALUES (?,datetime('now'),1,1) ON CONFLICT(store) DO UPDATE SET last_error=datetime('now'),consecutive_failures=consecutive_failures+1,total_requests=total_requests+1",(store,))

    def sq_run_start(db, n): return db.execute("INSERT INTO collector_runs (started_at,stores_attempted) VALUES (datetime('now'),?)",(n,)).lastrowid
    def sq_run_end(db, rid, ok, total, errs): db.execute("UPDATE collector_runs SET finished_at=datetime('now'), stores_succeeded=?, prices_collected=?, errors=? WHERE id=?",(ok,total,errs,rid))

# ── Price normalization ─────────────────────────────────────────────────────

def parse_price(p):
    try: return float(p or 0)
    except: return 0.0

def _old_product_from_json(p, store):
    items = p.get("items",[]); item = items[0] if items else {}
    sellers = item.get("sellers",[]); seller = sellers[0] if sellers else {}
    offer = seller.get("commertialOffer",{})
    price = parse_price(offer.get("Price")); list_price = parse_price(offer.get("ListPrice"))
    discount = round((1-price/list_price)*100) if list_price>price>0 else None
    sid = p.get("productReference") or p.get("productId","")
    return {"product_id":sid,"name":p.get("productName","").replace("-"," "),"brand":p.get("brand") or "","category":p.get("categoryId",""),"price":price,"list_price":list_price,"discount":discount,"stock":offer.get("AvailableQuantity",0),"store":store,"store_name":STORES.get(store,{}).get("name",store),"currency":STORES.get(store,{}).get("currency",""),"line":STORES.get(store,{}).get("line",""),"line_name":LINES.get(STORES.get(store,{}).get("line",""),{}).get("name",""),"url":f"{STORES.get(store,{}).get('base','')}/{p.get('linkText','')}/p"}

# ── Circuit breaker ─────────────────────────────────────────────────────────

class CB:
    def __init__(s): s.f=defaultdict(int); s.o={}
    def ok(s,k):
        if k in s.o:
            if time.time()<s.o[k]: return False
            del s.o[k]; s.f[k]=0
        return True
    def win(s,k): s.f[k]=0
    def lose(s,k):
        s.f[k]+=1
        if s.f[k]>=50: s.o[k]=time.time()+60
    def reset(s): s.f.clear(); s.o.clear()
cb=CB()

async def fetch_store_multi(client, store, term):
    return await _fetch_store(store, term, page=1, limit=10)

# ── Collector core ──────────────────────────────────────────────────────────

async def collect_one_pg(pool, store, queries):
    if not cb.ok(store): return 0
    line = STORES[store].get("line",""); collected=0
    try:
        async with httpx.AsyncClient(timeout=httpx.Timeout(QUERY_TIMEOUT),headers={"User-Agent":"CLI-Market-Collector/1.0"},follow_redirects=True) as client:
            async with pool.acquire() as conn:
                for q, lf in queries:
                    if lf and line!=lf: continue
                    try:
                        raw = await fetch_store_multi(client, store, q)
                        cb.win(store); await pg_health(conn, store, True)
                        for p in raw:
                            prod = _pfj(p, store)
                            prod["line"] = STORES[store].get("line","")
                            prod["line_name"] = LINES.get(STORES[store].get("line",""),{}).get("name","")
                            if prod["price"]<=0: continue
                            await pg_insert(conn, prod); collected+=1
                        await asyncio.sleep(REQUEST_DELAY)
                    except Exception: cb.lose(store); await pg_health(conn, store, False)
    except Exception: cb.lose(store)
    return collected

async def collect_one_sqlite(db, store, queries):
    from market_core import save_price_snapshot
    line = STORES[store].get("line",""); collected=0
    for q, lf in queries:
        if lf and line!=lf: continue
        try:
            raw = await _fetch_store(store, q, page=1, limit=10)
            for p in raw:
                prod = _pfj(p, store)
                prod["line"] = line
                prod["line_name"] = LINES.get(line,{}).get("name","")
                if prod.get("price", 0) and prod["price"] > 0:
                    save_price_snapshot(prod)
                    collected += 1
            await asyncio.sleep(REQUEST_DELAY)
        except Exception as _e:
            logger.warning("collect %s/%s: %s", store, q, _e)
    return collected

async def run_collection(stores, queries):
    sl = list(stores); B = PARALLEL*2; total=0; ok=0; errs=[]
    if USE_PG:
        pool = await get_pool(); await init_schema()
        async with pool.acquire() as c: rid = await pg_run_start(c, len(sl))
        for i in range(0,len(sl),B):
            batch = sl[i:i+B]; tasks = [collect_one_pg(pool, s, queries) for s in batch]
            for r in await asyncio.gather(*tasks, return_exceptions=True):
                if isinstance(r,Exception): errs.append(str(r))
                elif r>0: total+=r; ok+=1
        async with pool.acquire() as c: await pg_run_end(c, rid, ok, total, json.dumps(errs[:100]))
    else:
        db = init_schema_sqlite(); rid = sq_run_start(db, len(sl))
        for i in range(0,len(sl),B):
            batch = sl[i:i+B]; tasks = [collect_one_sqlite(db, s, queries) for s in batch]
            for r in await asyncio.gather(*tasks, return_exceptions=True):
                if isinstance(r,Exception): errs.append(str(r))
                elif r>0: total+=r; ok+=1
        sq_run_end(db, rid, ok, total, json.dumps(errs[:100])); db.commit()
    return {"stores_attempted":len(sl),"stores_succeeded":ok,"prices_collected":total,"errors":len(errs)}

# ── Status / Report ─────────────────────────────────────────────────────────

async def status_pg():
    pool=await get_pool()
    async with pool.acquire() as c:
        total=await c.fetchval("SELECT COUNT(*) FROM price_snapshots")
        stores=await c.fetchval("SELECT COUNT(DISTINCT store) FROM price_snapshots")
        latest=await c.fetchval("SELECT MAX(queried_at) FROM price_snapshots")
        runs=await c.fetchval("SELECT COUNT(*) FROM collector_runs")
        print(f"═══ Price Collector (PostgreSQL) ═══\n  Prices: {total:,} | Stores: {stores}/{len(STORES)} | Latest: {latest or 'never'} | Runs: {runs}")
        top=await c.fetch("SELECT store_name, COUNT(*) n FROM price_snapshots GROUP BY store_name ORDER BY n DESC LIMIT 5")
        if top: print("  Top:"); [print(f"    {r['store_name'][:25]:<25} {r['n']:>6}") for r in top]

def status_sqlite():
    db=get_sqlite()
    total=db.execute("SELECT COUNT(*) c FROM price_snapshots").fetchone()["c"]
    stores=db.execute("SELECT COUNT(DISTINCT store) c FROM price_snapshots").fetchone()["c"]
    latest=db.execute("SELECT MAX(queried_at) m FROM price_snapshots").fetchone()["m"]
    runs=db.execute("SELECT COUNT(*) c FROM collector_runs").fetchone()["c"]
    print(f"═══ Price Collector (SQLite) ═══\n  Prices: {total:,} | Stores: {stores}/{len(STORES)} | Latest: {latest or 'never'} | Runs: {runs}")
    top=db.execute("SELECT store_name, COUNT(*) n FROM price_snapshots GROUP BY store_name ORDER BY n DESC LIMIT 5").fetchall()
    if top: print("  Top:"); [print(f"    {r['store_name'][:25]:<25} {r['n']:>6}") for r in top]

def do_status():
    if USE_PG: asyncio.run(status_pg())
    else: status_sqlite()

def do_report():
    if USE_PG:
        async def r():
            pool=await get_pool()
            async with pool.acquire() as c:
                rows=await c.fetch("SELECT line,line_name,COUNT(*) c,MIN(price) mn,MAX(price) mx,AVG(price) av,MAX(queried_at) lt FROM price_snapshots WHERE price>0 GROUP BY line,line_name ORDER BY c DESC")
                print("═══ Latest Prices by Line ═══\n")
                for r in rows:
                    print(f"[{r['line_name']}]  {r['c']:,} prices | {r['mn']:.2f}–{r['mx']:.2f} | avg {r['av']:.2f} | {r['lt']}")
                    ch=await c.fetch("SELECT name,store_name,price,currency FROM price_snapshots WHERE line=$1 AND price>0 ORDER BY price ASC LIMIT 3", r["line"])
                    for p in ch: print(f"    ↓ {p['name'][:45]:<45} {p['store_name'][:15]:<15} {p['currency']} {p['price']:.2f}")
                    print()
        asyncio.run(r())
    else:
        db=get_sqlite()
        rows=db.execute("SELECT line,line_name,COUNT(*) c,MIN(price) mn,MAX(price) mx,AVG(price) av,MAX(queried_at) lt FROM price_snapshots WHERE price>0 GROUP BY line ORDER BY c DESC").fetchall()
        print("═══ Latest Prices by Line ═══\n")
        for r in rows:
            print(f"[{r['line_name']}]  {r['c']:,} prices | {r['mn']:.2f}–{r['mx']:.2f} | avg {r['av']:.2f} | {r['lt']}")
            ch=db.execute("SELECT name,store_name,price,currency FROM price_snapshots WHERE line=? AND price>0 ORDER BY price ASC LIMIT 3",(r["line"],)).fetchall()
            for p in ch: print(f"    ↓ {p['name'][:45]:<45} {p['store_name'][:15]:<15} {p['currency']} {p['price']:.2f}")
            print()

# ── Main ────────────────────────────────────────────────────────────────────

async def main():
    import argparse
    ap = argparse.ArgumentParser(description="CLI Market Price Collector")
    ap.add_argument("--daemon", action="store_true"); ap.add_argument("--interval", type=int, default=DAEMON_INTERVAL)
    ap.add_argument("--status", action="store_true"); ap.add_argument("--report", action="store_true")
    ap.add_argument("--stores", type=int, default=0); ap.add_argument("--queries", type=int, default=0)
    ap.add_argument("--parallel", type=int, default=50)
    args = ap.parse_args()
    global PARALLEL; PARALLEL = args.parallel
    if args.status: do_status(); return
    if args.report: do_report(); return
    stores = list(STORES.keys())[:args.stores] if args.stores else list(STORES.keys())
    label = "PostgreSQL" if USE_PG else "SQLite"

    if args.daemon:
        print(f"🔄 Daemon: every {args.interval}h | expansion: ×{EXPANSION_FACTOR} | feedback: ≤{FEEDBACK_LIMIT}")
        cycle = 0
        while True:
            db = _get_feedback_db()
            queries = build_query_list(db=db, cycle=cycle)
            if db: db.close()
            if args.queries: queries = queries[:args.queries]
            print(f"\n─── {datetime.now(timezone.utc).isoformat()} [cycle {cycle}] ───")
            print(f"🔍 {label} | {len(stores)} stores × {len(queries)} queries (seed+feedback)")
            t0=time.monotonic(); r=await run_collection(stores, queries)
            print(f"  ✓ {r['prices_collected']:,} prices | {r['stores_succeeded']} stores | {time.monotonic()-t0:.1f}s | {r['errors']} errors")
            cycle += 1
            await asyncio.sleep(args.interval*3600)
    else:
        db = _get_feedback_db()
        queries = build_query_list(db=db, cycle=0)
        if db: db.close()
        if args.queries: queries = queries[:args.queries]
        print(f"🔍 {label} | {len(stores)} stores × {len(queries)} queries (seed+feedback)")
        t0=time.monotonic(); r=await run_collection(stores, queries)
        print(f"  ✓ {r['prices_collected']:,} prices | {r['stores_succeeded']}/{r['stores_attempted']} stores | {time.monotonic()-t0:.1f}s | {r['errors']} errors")
        do_status()

if __name__ == "__main__":
    asyncio.run(main())
