#!/usr/bin/env python3
"""
collect_prices.py — VTEX price collector for CLI Market data moat.

Parallel, rate-limited, circuit-breaker protected, deduplicating.
Fetches real prices from 3,760 VTEX retailers across 40 seed queries.

Usage:
    python collect_prices.py              # run once
    python collect_prices.py --daemon     # run every 4h
    python collect_prices.py --status     # collection stats
    python collect_prices.py --report     # latest prices per line
"""

import asyncio, json, os, sqlite3, sys, time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
import httpx

DATA_DIR = Path(os.getenv("MARKET_DATA_DIR", Path.home() / ".market"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_FILE = DATA_DIR / "market.db"

PARALLEL = int(os.getenv("COLLECT_PARALLEL", "50"))
REQUEST_DELAY = float(os.getenv("COLLECT_DELAY", "0.15"))
QUERY_TIMEOUT = 10.0

try:
    from market_stores import STORES
except ImportError:
    print("ERROR: market_stores.py not found. Run from project root.")
    sys.exit(1)

LINES = {
    "supermercados":   {"name": "Supermercados",        "emoji": "🛒"},
    "farmacias":       {"name": "Farmacias y Salud",    "emoji": "💊"},
    "electro":         {"name": "Electro y Tecnología", "emoji": "📱"},
    "moda":            {"name": "Moda y Accesorios",    "emoji": "👕"},
    "deportes":        {"name": "Deportes y Outdoor",   "emoji": "⚽"},
    "hogar":           {"name": "Hogar y Construcción", "emoji": "🏠"},
    "financiero":      {"name": "Financiero y Seguros","emoji": "💳"},
    "automotriz":      {"name": "Automotriz",           "emoji": "🚗"},
    "libros":          {"name": "Libros y Educación",   "emoji": "📚"},
    "viajes":          {"name": "Viajes y Turismo",     "emoji": "✈️"},
    "hogar_construccion": {"name": "Hogar y Construcción", "emoji": "🔨"},
    "educacion":       {"name": "Educación Ejecutiva",  "emoji": "🎓"},
}

SEED_QUERIES = [
    ("leche", None), ("arroz", None), ("aceite", None), ("azucar", None),
    ("huevos", None), ("pan", None), ("cafe", None), ("pollo", None),
    ("carne", None), ("queso", None), ("yogur", None), ("mantequilla", None),
    ("detergente", None), ("jabon", None), ("papel higienico", None),
    ("pasta", None), ("agua", None), ("cerveza", None), ("vino", None),
    ("milk", None), ("bread", None), ("eggs", None), ("rice", None),
    ("chicken", None), ("coffee", None), ("oil", None),
    ("paracetamol", "farmacias"), ("ibuprofeno", "farmacias"),
    ("vitamina c", "farmacias"),
    ("zapatillas", "deportes"), ("camiseta", "moda"),
    ("jeans", "moda"), ("televisor", "electro"),
    ("celular", "electro"), ("laptop", "electro"),
    ("taladro", "hogar"), ("sarten", "hogar"),
    ("silla", "hogar"), ("libro", "libros"), ("mochila", "viajes"),
]

def get_db():
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
            name TEXT, brand TEXT, price REAL, list_price REAL, discount INTEGER,
            store TEXT NOT NULL, store_name TEXT, currency TEXT,
            line TEXT, line_name TEXT, category TEXT, stock INTEGER, url TEXT,
            queried_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(product_id, store)
        );
        CREATE INDEX IF NOT EXISTS idx_ps_store ON price_snapshots(store);
        CREATE INDEX IF NOT EXISTS idx_ps_line ON price_snapshots(line);
        CREATE TABLE IF NOT EXISTS collector_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT, finished_at TEXT,
            stores_attempted INTEGER DEFAULT 0,
            stores_succeeded INTEGER DEFAULT 0,
            prices_collected INTEGER DEFAULT 0,
            errors TEXT
        );
        CREATE TABLE IF NOT EXISTS store_health (
            store TEXT PRIMARY KEY,
            last_success TEXT, last_error TEXT,
            consecutive_failures INTEGER DEFAULT 0,
            total_requests INTEGER DEFAULT 0,
            total_successes INTEGER DEFAULT 0
        );
    """)
    return db

def parse_price(p): 
    try: return float(p or 0)
    except: return 0.0

def product_from_json(p, store):
    items = p.get("items", [])
    item = items[0] if items else {}
    sellers = item.get("sellers", [])
    seller = sellers[0] if sellers else {}
    offer = seller.get("commertialOffer", {})
    price = parse_price(offer.get("Price"))
    list_price = parse_price(offer.get("ListPrice"))
    discount = round((1 - price / list_price) * 100) if list_price > price > 0 else None
    return {
        "product_id": p.get("productReference", p.get("productId", "")),
        "name": p.get("productName", "").replace("-", " "),
        "brand": p.get("brand") or "",
        "category": p.get("categoryId", ""),
        "price": price, "list_price": list_price, "discount": discount,
        "stock": offer.get("AvailableQuantity", 0),
        "store": store,
        "store_name": STORES.get(store, {}).get("name", store),
        "currency": STORES.get(store, {}).get("currency", ""),
        "line": STORES.get(store, {}).get("line", ""),
        "line_name": LINES.get(STORES.get(store, {}).get("line", ""), {}).get("name", ""),
        "url": f"{STORES.get(store, {}).get('base', '')}/{p.get('linkText', '')}/p",
    }

class CircuitBreaker:
    def __init__(self, threshold=5, cooldown=300):
        self.failures = defaultdict(int); self.open_until = {}
        self.threshold = threshold; self.cooldown = cooldown
    def allow(self, store):
        if store in self.open_until:
            if time.time() < self.open_until[store]: return False
            del self.open_until[store]; self.failures[store] = 0
        return True
    def success(self, store): self.failures[store] = 0
    def failure(self, store):
        self.failures[store] += 1
        if self.failures[store] >= self.threshold:
            self.open_until[store] = time.time() + self.cooldown

circuit = CircuitBreaker()

async def fetch_store(client: httpx.AsyncClient, store: str, term: str) -> tuple[list, float]:
    base = STORES[store]["base"]
    url = f"{base}/api/catalog_system/pub/products/search/{term}"
    t0 = time.monotonic()
    resp = await client.get(url, params={"_from": "0", "_to": "9"})
    elapsed = (time.monotonic() - t0) * 1000
    if resp.status_code >= 500:
        raise Exception(f"HTTP {resp.status_code}")
    resp.raise_for_status()
    return resp.json(), elapsed


async def collect_one(store: str, queries: list, db: sqlite3.Connection) -> int:
    """Collect prices from one store. Returns number of prices inserted."""
    if not circuit.allow(store):
        return 0
    store_line = STORES[store].get("line", "")
    collected = 0
    try:
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(QUERY_TIMEOUT),
            headers={"User-Agent": "CLI-Market-Collector/1.0"},
            follow_redirects=True,
        ) as client:
            for query, line_filter in queries:
                if line_filter and store_line != line_filter:
                    continue
                try:
                    raw, latency = await fetch_store(client, store, query)
                    circuit.success(store)
                    db.execute("""
                        INSERT INTO store_health (store, last_success, total_requests, total_successes)
                        VALUES (?, datetime('now'), 1, 1)
                        ON CONFLICT(store) DO UPDATE SET
                            last_success = datetime('now'),
                            total_requests = total_requests + 1,
                            total_successes = total_successes + 1
                    """, (store,))
                    for p in raw:
                        prod = product_from_json(p, store)
                        if prod["price"] <= 0:
                            continue
                        db.execute("""
                            INSERT INTO price_snapshots
                                (product_id, name, brand, price, list_price, discount,
                                 store, store_name, currency, line, line_name, category, stock, url, queried_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
                            ON CONFLICT(product_id, store) DO UPDATE SET
                                price = excluded.price,
                                list_price = excluded.list_price,
                                discount = excluded.discount,
                                stock = excluded.stock,
                                queried_at = datetime('now')
                        """, (
                            prod["product_id"], prod["name"], prod["brand"],
                            prod["price"], prod["list_price"], prod["discount"],
                            prod["store"], prod["store_name"], prod["currency"],
                            prod["line"], prod["line_name"], prod["category"],
                            prod["stock"], prod["url"],
                        ))
                        collected += 1
                    await asyncio.sleep(REQUEST_DELAY)
                except Exception:
                    circuit.failure(store)
                    db.execute("""
                        INSERT INTO store_health (store, last_error, consecutive_failures, total_requests)
                        VALUES (?, datetime('now'), 1, 1)
                        ON CONFLICT(store) DO UPDATE SET
                            last_error = datetime('now'),
                            consecutive_failures = consecutive_failures + 1,
                            total_requests = total_requests + 1
                    """, (store,))
    except Exception:
        circuit.failure(store)
    return collected


async def run_collection(stores, queries):
    db = get_db()
    run_id = db.execute(
        "INSERT INTO collector_runs (started_at, stores_attempted) VALUES (datetime('now'), ?)",
        (len(stores),)
    ).lastrowid

    total, succeeded = 0, 0
    errs = []
    store_list = list(stores)

    # Process in batches
    BATCH = PARALLEL * 2
    for i in range(0, len(store_list), BATCH):
        batch = store_list[i : i + BATCH]
        tasks = [collect_one(s, queries, db) for s in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for r in results:
            if isinstance(r, Exception):
                errs.append(str(r))
            elif r > 0:
                total += r
                succeeded += 1

    db.execute("""
        UPDATE collector_runs
        SET finished_at = datetime('now'),
            stores_succeeded = ?,
            prices_collected = ?,
            errors = ?
        WHERE id = ?
    """, (succeeded, total, json.dumps(errs[:100]), run_id))
    db.commit()
    return {
        "run_id": run_id,
        "stores_attempted": len(stores),
        "stores_succeeded": succeeded,
        "prices_collected": total,
        "errors": len(errs),
    }

def status():
    db = get_db()
    total = db.execute("SELECT COUNT(*) c FROM price_snapshots").fetchone()["c"]
    stores = db.execute("SELECT COUNT(DISTINCT store) c FROM price_snapshots").fetchone()["c"]
    lines = db.execute("SELECT COUNT(DISTINCT line) c FROM price_snapshots").fetchone()["c"]
    latest = db.execute("SELECT MAX(queried_at) m FROM price_snapshots").fetchone()["m"]
    runs = db.execute("SELECT COUNT(*) c FROM collector_runs").fetchone()["c"]
    last = db.execute("SELECT * FROM collector_runs ORDER BY id DESC LIMIT 1").fetchone()
    print(f"═══ Price Collector Status ═══")
    print(f"  Prices: {total:,}  |  Stores: {stores}/{len(STORES)}  |  Lines: {lines}/{len(LINES)}")
    print(f"  Latest: {latest or 'never'}  |  Runs: {runs}")
    if last:
        print(f"  Last run #{last['id']}: {last['stores_succeeded']}/{last['stores_attempted']} stores → {last['prices_collected']:,} prices")
    top = db.execute("SELECT store_name, COUNT(*) c, MAX(queried_at) last FROM price_snapshots GROUP BY store ORDER BY c DESC LIMIT 10").fetchall()
    if top:
        print("\nTop stores:")
        for r in top: print(f"  {r['store_name'][:30]:<30} {r['c']:>6} prices | {r['last']}")
    unhealthy = db.execute("SELECT store, consecutive_failures FROM store_health WHERE consecutive_failures >= 3").fetchall()
    if unhealthy:
        print(f"\n⚠  {len(unhealthy)} unhealthy stores")

def report():
    db = get_db()
    print("═══ Latest Prices by Line ═══\n")
    for r in db.execute("SELECT line, line_name, COUNT(*) c, MIN(price) min_p, MAX(price) max_p, AVG(price) avg_p, MAX(queried_at) last FROM price_snapshots WHERE price>0 GROUP BY line ORDER BY c DESC").fetchall():
        print(f"[{r['line_name']}]  {r['c']:,} prices | {r['min_p']:.2f}–{r['max_p']:.2f} | avg {r['avg_p']:.2f} | {r['last']}")
        for p in db.execute("SELECT name, store_name, price, currency FROM price_snapshots WHERE line=? AND price>0 ORDER BY price ASC LIMIT 3", (r["line"],)).fetchall():
            print(f"    ↓ {p['name'][:45]:<45} {p['store_name'][:15]:<15} {p['currency']} {p['price']:.2f}")
        print()

async def main():
    import argparse
    p = argparse.ArgumentParser(description="CLI Market Price Collector")
    p.add_argument("--daemon", action="store_true", help="Run continuously")
    p.add_argument("--interval", type=int, default=4, help="Daemon interval (hours)")
    p.add_argument("--status", action="store_true"); p.add_argument("--report", action="store_true")
    p.add_argument("--stores", type=int, default=0); p.add_argument("--queries", type=int, default=0)
    p.add_argument("--parallel", type=int, default=50)
    args = p.parse_args()
    global PARALLEL
    PARALLEL = args.parallel
    init_db()
    if args.status: status(); return
    if args.report: report(); return
    stores = list(STORES.keys())[:args.stores] if args.stores else list(STORES.keys())
    queries = SEED_QUERIES[:args.queries] if args.queries else SEED_QUERIES
    if args.daemon:
        print(f"🔄 Collector daemon (interval: {args.interval}h)")
        while True:
            print(f"\n─── Run {datetime.now(timezone.utc).isoformat()} ───")
            r = await run_collection(stores, queries)
            print(f"  ✓ {r['prices_collected']:,} prices | {r['stores_succeeded']} stores | {r['errors']} errors")
            await asyncio.sleep(args.interval * 3600)
    else:
        print(f"🔍 {len(stores)} stores × {len(queries)} queries...")
        t0 = time.monotonic()
        r = await run_collection(stores, queries)
        print(f"  ✓ {r['prices_collected']:,} prices from {r['stores_succeeded']}/{r['stores_attempted']} stores ({time.monotonic()-t0:.1f}s, {r['errors']} errors)")
        status()

if __name__ == "__main__":
    asyncio.run(main())
