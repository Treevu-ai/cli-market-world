#!/usr/bin/env python3
"""
market_core — Shared utilities for CLI Market.

Imports once, used everywhere: server, CLI, MCP server, collector.
Eliminates the 4-way code duplication of api(), product_from_json(),
STORES/LINES, get_token(), and price helpers.
"""

import json
import os
import sys
import sqlite3
import logging
from pathlib import Path
from typing import Any

import httpx

# ── Database backend selection ──────────────────────────────────────────────

DATABASE_URL = os.getenv("DATABASE_URL", "")

def _pg_host_reachable(url: str) -> bool:
    """Quick check: can we resolve the PostgreSQL hostname?"""
    import re, socket
    m = re.search(r"@([^:/]+)", url) or re.search(r"://([^:/]+)", url)
    if not m:
        return True  # no hostname found, let it fail later
    host = m.group(1)
    # Skip known cross-platform dead-ends
    if os.getenv("RENDER") and "railway.internal" in host:
        return False
    try:
        socket.getaddrinfo(host, 5432, socket.AF_UNSPEC, socket.SOCK_STREAM)
        return True
    except socket.gaierror:
        return False

USE_PG = bool(DATABASE_URL) and _pg_host_reachable(DATABASE_URL)

if USE_PG:
    try:
        import psycopg2
        import psycopg2.extras
        logger_pg = logging.getLogger("market.pg")
        logger_pg.info("Using PostgreSQL backend")
    except ImportError:
        logging.getLogger("market").error(
            "DATABASE_URL is set but psycopg2 is not installed. "
            "Install: pip install psycopg2-binary. Falling back to SQLite."
        )
        USE_PG = False

# ── Logging ───────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
logger = logging.getLogger("market")

# ── Paths & config ────────────────────────────────────────────────────────────

API = os.environ.get("MARKET_API_URL", "http://127.0.0.1:8765")
DATA_DIR = Path(os.getenv("MARKET_DATA_DIR", Path.home() / ".market"))
# Ensure writable: fall back to cwd if home is not writable (e.g. serverless)
try:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
except PermissionError:
    DATA_DIR = Path(os.getenv("MARKET_DATA_DIR", Path.cwd() / ".market"))
    DATA_DIR.mkdir(parents=True, exist_ok=True)

SESSION_FILE = DATA_DIR / "session.json"
LANG_FILE = DATA_DIR / "lang"
LAST_SEARCH_FILE = DATA_DIR / "last_search.json"
USERS_FILE = DATA_DIR / "users.json"
CARTS_FILE = DATA_DIR / "carts.json"
ORDERS_FILE = DATA_DIR / "orders.json"
DB_FILE = DATA_DIR / "market.db"

# ── Stores (VTEX retailers) ───────────────────────────────────────────────────

# Canonical STORES source: market_stores.py (27 verified VTEX retailers with base URLs).
# Set MARKET_STORES=expanded to use market_stores_cli.py (3,760 entries, display-only, no base URLs).
# To add/remove retailers: edit stores_curated.csv, run: python3 gen_stores.py
if os.getenv("MARKET_STORES", "") == "expanded":
    try:
        from market_stores_cli import STORES
    except ImportError:
        from market_stores import STORES
else:
    from market_stores import STORES

LINES = {
    "supermercados":   {"name": "Supermercados",          "emoji": "🛒", "description": "Alimentos, bebidas y consumo diario"},
    "farmacias":       {"name": "Farmacias y Salud",      "emoji": "💊", "description": "Medicamentos, bienestar y cuidado personal"},
    "electro":         {"name": "Electro y Tecnología",   "emoji": "📱", "description": "Electrónicos, electrodomésticos y gadgets"},
    "hogar":           {"name": "Hogar y Construcción",   "emoji": "🏠", "description": "Mejoramiento del hogar, muebles, ferretería"},
    "departamentales": {"name": "Tiendas Departamentales", "emoji": "🏬", "description": "Ropa, hogar, electrónicos y más"},
    "moda":            {"name": "Moda y Vestimenta",      "emoji": "👕", "description": "Ropa, calzado y accesorios"},
}

COUNTRIES: dict[str, dict] = {}
for _sk, _sv in STORES.items():
    _cc = _sv["country"]
    if _cc not in COUNTRIES:
        COUNTRIES[_cc] = {"name": _cc, "stores": []}
    COUNTRIES[_cc]["stores"].append(_sk)
# Human-readable country names
_country_names: dict[str, str] = {
    "PE": "Perú", "AR": "Argentina", "BR": "Brasil", "MX": "México", "CO": "Colombia",
    "CL": "Chile", "ES": "España", "FR": "Francia", "IT": "Italia", "DE": "Alemania",
    "GB": "Reino Unido", "PT": "Portugal", "NL": "Países Bajos", "BE": "Bélgica",
    "PL": "Polonia", "SE": "Suecia", "DK": "Dinamarca", "FI": "Finlandia",
    "NO": "Noruega", "AT": "Austria", "CH": "Suiza", "IE": "Irlanda",
    "GR": "Grecia", "CZ": "República Checa", "RO": "Rumania", "HU": "Hungría",
    "SK": "Eslovaquia", "BG": "Bulgaria", "HR": "Croacia", "SI": "Eslovenia",
    "LU": "Luxemburgo", "EE": "Estonia", "LV": "Letonia", "LT": "Lituania",
    "UY": "Uruguay", "EC": "Ecuador", "BO": "Bolivia", "PY": "Paraguay",
    "VE": "Venezuela", "CR": "Costa Rica", "GT": "Guatemala", "SV": "El Salvador",
    "PA": "Panamá", "DO": "República Dominicana", "HN": "Honduras", "NI": "Nicaragua",
    "US": "Estados Unidos", "CA": "Canadá", "AU": "Australia", "NZ": "Nueva Zelanda",
    "JP": "Japón", "KR": "Corea del Sur", "CN": "China", "TW": "Taiwán",
    "HK": "Hong Kong", "SG": "Singapur", "IN": "India", "MY": "Malasia",
    "TH": "Tailandia", "ID": "Indonesia", "PH": "Filipinas", "VN": "Vietnam",
    "TR": "Turquía", "RU": "Rusia", "AE": "Emiratos Árabes Unidos",
    "ZA": "Sudáfrica", "NG": "Nigeria",
}
for _cc in COUNTRIES:
    COUNTRIES[_cc]["name"] = _country_names.get(_cc, _cc)

DEFAULT_STORES = list(STORES.keys())
PAGE_SIZE = 20

# ── Currency ──────────────────────────────────────────────────────────────────

CURRENCY_SYMBOLS: dict[str, str] = {
    "PEN": "S/", "ARS": "ARS", "BRL": "R$", "MXN": "MXN", "COP": "COP",
    "CLP": "CLP", "EUR": "€", "GBP": "£",
}

def fmt_price(price: float, currency: str = "PEN") -> str:
    symbol = CURRENCY_SYMBOLS.get(currency, currency)
    return f"{symbol} {price:,.2f}"

def store_color(store: str) -> str:
    colors: dict[str, str] = {
        "wong": "#3cffd0", "metro": "#5200ff", "plazavea": "#ffe600",
        "carrefour": "#3cffd0", "jumbo_ar": "#00FF88", "carrefour_br": "#3cffd0",
        "chedraui": "#FF6B35", "heb": "#FF6B35",
        "olimpica": "#60A5FA", "exito": "#60A5FA",
        "drogaraia": "#FF6B35", "drogasil": "#FF6B35",
        "magazineluiza": "#A78BFA", "motorola_br": "#A78BFA",
        "renner": "#FFD600", "centauro": "#4ADE80", "homecenter": "#F5F5F0",
        "carrefour_es": "#FFD600", "decathlon_fr": "#4ADE80",
    }
    return colors.get(store, "#e9e9e9")

def store_emoji(store: str) -> str:
    return STORES.get(store, {}).get("emoji", "📦")

# ── Session / auth helpers ────────────────────────────────────────────────────

def get_token() -> str:
    if not SESSION_FILE.exists():
        return ""
    data = json.loads(SESSION_FILE.read_text())
    return data.get("token", "")

# ── API client (sync — used by CLI and MCP) ───────────────────────────────────

def api(method: str, path: str, json_data: dict | None = None) -> dict:
    token = None
    if path not in ("/auth/login", "/"):
        token = get_token()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        if method == "GET":
            resp = httpx.get(f"{API}{path}", headers=headers, timeout=30)
        elif method == "POST":
            resp = httpx.post(f"{API}{path}", headers=headers, json=json_data, timeout=30)
        elif method == "PUT":
            resp = httpx.put(f"{API}{path}", headers=headers, json=json_data, timeout=30)
        elif method == "DELETE":
            resp = httpx.delete(f"{API}{path}", headers=headers, timeout=30)
        else:
            raise ValueError(f"Unknown method: {method}")
        if resp.status_code >= 400:
            detail = resp.json().get("detail", resp.text)
            return {"error": detail, "status": resp.status_code}
        return resp.json()
    except httpx.ConnectError:
        return {"error": "Server not running. Start: python market_server.py"}

# ── Multi-platform store access ────────────────────────────────────────────

async def fetch_store(store: str, term: str, page: int = 1, limit: int = PAGE_SIZE) -> list[dict]:
    """Search a store's catalog API. Platform-agnostic."""
    store_config = STORES[store]
    platform = store_config.get("platform", "vtex")
    from market_connectors import get_connector
    connector = get_connector(platform)
    return await connector.search(store_config, term, page, limit)

def product_from_json(p: dict, store: str) -> dict:
    """Normalize a product JSON into a flat dict. Platform-agnostic."""
    if not isinstance(p, dict):
        return {"id": "", "name": str(p)[:80], "price": 0, "store": store, "store_name": store, "currency": "USD"}
    store_config = STORES[store]
    platform = store_config.get("platform", "vtex")
    from market_connectors import get_connector
    connector = get_connector(platform)
    return connector.normalize(p, store, store_config)

# ── Last-search cache (for CLI auto-fill via table #) ─────────────────────────

def save_last_search(results: list[dict]) -> None:
    slim: list[dict] = []
    for p in results[:50]:
        slim.append({
            "product_id": p.get("id", p.get("product_id", "")),
            "name": p.get("name", ""),
            "price": p.get("price", 0),
            "store": p.get("store", ""),
            "store_name": p.get("store_name", ""),
            "currency": p.get("currency", "PEN"),
            "brand": p.get("brand", ""),
        })
    LAST_SEARCH_FILE.parent.mkdir(parents=True, exist_ok=True)
    LAST_SEARCH_FILE.write_text(json.dumps(slim))

def load_last_search() -> list[dict]:
    if LAST_SEARCH_FILE.exists():
        try:
            return json.loads(LAST_SEARCH_FILE.read_text())
        except (json.JSONDecodeError, OSError):
            return []
    return []

# ── Database abstraction (PostgreSQL or SQLite) ──────────────────────────────

class _PgCursor:
    """Mimics sqlite3.Cursor for psycopg2."""
    def __init__(self, cur):
        self._cur = cur
        self.lastrowid = None

    def fetchall(self):
        return [dict(r) for r in self._cur.fetchall()]

    def fetchone(self):
        row = self._cur.fetchone()
        return dict(row) if row else None


class _DB:
    """Unified DB connection: PostgreSQL or SQLite."""
    def __init__(self):
        if USE_PG:
            self._conn = psycopg2.connect(DATABASE_URL)
            self._pg = True
        else:
            self._conn = sqlite3.connect(str(DB_FILE))
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA busy_timeout=5000")
            self._pg = False

    def execute(self, sql, params=None):
        if self._pg:
            sql = sql.replace("?", "%s")
            sql = sql.replace("datetime('now')", "NOW()")
            sql = sql.replace("INSERT OR IGNORE", "INSERT")
            cur = self._conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute(sql, params)
            wrapper = _PgCursor(cur)
            # Capture lastrowid from RETURNING clause
            if "RETURNING" in sql.upper():
                row = cur.fetchone()
                if row:
                    wrapper.lastrowid = list(row.values())[0] if row else None
            return wrapper
        else:
            return self._conn.execute(sql, params or ())

    def executescript(self, sql):
        if self._pg:
            for stmt in sql.split(";"):
                stmt = stmt.strip()
                if stmt:
                    self.execute(stmt)
        else:
            self._conn.executescript(sql)

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()


def get_db() -> _DB:
    import time as _time
    for attempt in range(3):
        try:
            return _DB()
        except Exception:
            if attempt < 2:
                _time.sleep(0.2 * (attempt + 1))
            else:
                raise


def init_db_pg(db: _DB) -> None:
    """PostgreSQL schema."""
    db.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            chat_id TEXT PRIMARY KEY,
            first_name TEXT,
            username TEXT,
            last_message TEXT,
            created_at TEXT,
            updated_at TEXT DEFAULT NOW()
        )
    """)
    db.execute("""
        CREATE TABLE IF NOT EXISTS price_snapshots (
            id SERIAL PRIMARY KEY,
            product_id TEXT NOT NULL,
            name TEXT,
            brand TEXT,
            price DOUBLE PRECISION,
            list_price DOUBLE PRECISION,
            discount INTEGER,
            store TEXT NOT NULL,
            store_name TEXT,
            currency TEXT,
            line TEXT,
            line_name TEXT,
            category TEXT,
            stock INTEGER,
            url TEXT,
            queried_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE(product_id, store)
        )
    """)
    for idx_sql in [
        "CREATE INDEX IF NOT EXISTS idx_ps_product ON price_snapshots(product_id, store)",
        "CREATE INDEX IF NOT EXISTS idx_ps_store ON price_snapshots(store)",
        "CREATE INDEX IF NOT EXISTS idx_ps_line ON price_snapshots(line)",
        "CREATE INDEX IF NOT EXISTS idx_ps_queried ON price_snapshots(queried_at)",
    ]:
        db.execute(idx_sql)

    db.execute("""
        CREATE TABLE IF NOT EXISTS search_queries (
            id SERIAL PRIMARY KEY,
            query TEXT NOT NULL,
            line TEXT,
            country TEXT,
            store_filter TEXT,
            num_results INTEGER DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    db.execute("CREATE INDEX IF NOT EXISTS idx_sq_created ON search_queries(created_at)")

    db.execute("""
        CREATE TABLE IF NOT EXISTS app_users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            token TEXT,
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS app_carts (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            product_id TEXT NOT NULL,
            name TEXT NOT NULL,
            price DOUBLE PRECISION NOT NULL DEFAULT 0,
            store TEXT NOT NULL,
            store_name TEXT DEFAULT '',
            quantity INTEGER NOT NULL DEFAULT 1,
            url TEXT DEFAULT '',
            added_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    db.execute("CREATE INDEX IF NOT EXISTS idx_cart_user ON app_carts(username)")

    db.execute("""
        CREATE TABLE IF NOT EXISTS app_orders (
            order_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            payment_method TEXT DEFAULT 'yape',
            total DOUBLE PRECISION NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'completed',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    db.execute("CREATE INDEX IF NOT EXISTS idx_order_user ON app_orders(username)")

    db.execute("""
        CREATE TABLE IF NOT EXISTS app_order_items (
            id SERIAL PRIMARY KEY,
            order_id TEXT NOT NULL REFERENCES app_orders(order_id),
            product_id TEXT NOT NULL,
            name TEXT NOT NULL,
            price DOUBLE PRECISION NOT NULL DEFAULT 0,
            store TEXT NOT NULL,
            store_name TEXT DEFAULT '',
            quantity INTEGER NOT NULL DEFAULT 1,
            url TEXT DEFAULT ''
        )
    """)
    db.execute("CREATE INDEX IF NOT EXISTS idx_oi_order ON app_order_items(order_id)")

    db.execute("""
        CREATE TABLE IF NOT EXISTS rate_limits (
            key TEXT NOT NULL,
            window_start DOUBLE PRECISION NOT NULL,
            counter INTEGER NOT NULL DEFAULT 1,
            PRIMARY KEY (key, window_start)
        )
    """)
    db.execute("CREATE INDEX IF NOT EXISTS idx_rl_key ON rate_limits(key)")

    db.execute("""
        CREATE TABLE IF NOT EXISTS collector_runs (
            id SERIAL PRIMARY KEY,
            started_at TIMESTAMPTZ DEFAULT NOW(),
            finished_at TIMESTAMPTZ,
            stores_attempted INT DEFAULT 0,
            stores_succeeded INT DEFAULT 0,
            prices_collected INT DEFAULT 0,
            errors TEXT
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS store_health (
            store TEXT PRIMARY KEY,
            last_success TEXT,
            last_error TEXT,
            consecutive_failures INT DEFAULT 0,
            total_requests INT DEFAULT 0,
            total_successes INT DEFAULT 0
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS api_keys (
            id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            key_hash TEXT UNIQUE NOT NULL,
            key_prefix TEXT NOT NULL DEFAULT '',
            scopes TEXT NOT NULL DEFAULT 'read',
            label TEXT DEFAULT '',
            created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            last_used_at TIMESTAMPTZ
        )
    """)
    db.execute("CREATE INDEX IF NOT EXISTS idx_api_user ON api_keys(username)")

    db.execute("""
        CREATE TABLE IF NOT EXISTS app_favorites (
            username TEXT NOT NULL,
            product_id TEXT NOT NULL,
            name TEXT DEFAULT '',
            store TEXT DEFAULT '',
            PRIMARY KEY (username, product_id)
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            username TEXT PRIMARY KEY,
            tier TEXT NOT NULL DEFAULT 'free',
            req_limit_day INTEGER NOT NULL DEFAULT 1000,
            req_limit_min INTEGER NOT NULL DEFAULT 60,
            started_at TIMESTAMPTZ,
            expires_at TIMESTAMPTZ
        )
    """)
    db.commit()


_SQLITE_DDL = """\
        CREATE TABLE IF NOT EXISTS contacts (
            chat_id TEXT PRIMARY KEY,
            first_name TEXT,
            username TEXT,
            last_message TEXT,
            created_at TEXT,
            updated_at TEXT DEFAULT (datetime('now'))
        );
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
            queried_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(product_id, store)
        );
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

        CREATE TABLE IF NOT EXISTS app_users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL,
            token TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS app_carts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            product_id TEXT NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL DEFAULT 0,
            store TEXT NOT NULL,
            store_name TEXT DEFAULT '',
            quantity INTEGER NOT NULL DEFAULT 1,
            url TEXT DEFAULT '',
            added_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_cart_user ON app_carts(username);

        CREATE TABLE IF NOT EXISTS app_orders (
            order_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            payment_method TEXT DEFAULT 'yape',
            total REAL NOT NULL DEFAULT 0,
            status TEXT NOT NULL DEFAULT 'completed',
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );
        CREATE INDEX IF NOT EXISTS idx_order_user ON app_orders(username);

        CREATE TABLE IF NOT EXISTS app_order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL REFERENCES app_orders(order_id),
            product_id TEXT NOT NULL,
            name TEXT NOT NULL,
            price REAL NOT NULL DEFAULT 0,
            store TEXT NOT NULL,
            store_name TEXT DEFAULT '',
            quantity INTEGER NOT NULL DEFAULT 1,
            url TEXT DEFAULT ''
        );
        CREATE INDEX IF NOT EXISTS idx_oi_order ON app_order_items(order_id);

        CREATE TABLE IF NOT EXISTS rate_limits (
            key TEXT NOT NULL,
            window_start REAL NOT NULL,
            counter INTEGER NOT NULL DEFAULT 1,
            PRIMARY KEY (key, window_start)
        );
        CREATE INDEX IF NOT EXISTS idx_rl_key ON rate_limits(key);

        CREATE TABLE IF NOT EXISTS collector_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT,
            finished_at TEXT,
            stores_attempted INT DEFAULT 0,
            stores_succeeded INT DEFAULT 0,
            prices_collected INT DEFAULT 0,
            errors TEXT
        );

        CREATE TABLE IF NOT EXISTS store_health (
            store TEXT PRIMARY KEY,
            last_success TEXT,
            last_error TEXT,
            consecutive_failures INT DEFAULT 0,
            total_requests INT DEFAULT 0,
            total_successes INT DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            key_hash TEXT UNIQUE NOT NULL,
            key_prefix TEXT NOT NULL DEFAULT '',
            scopes TEXT NOT NULL DEFAULT 'read',
            label TEXT DEFAULT '',
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            last_used_at TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_api_user ON api_keys(username);

        CREATE TABLE IF NOT EXISTS app_favorites (
            username TEXT NOT NULL,
            product_id TEXT NOT NULL,
            name TEXT DEFAULT '',
            store TEXT DEFAULT '',
            PRIMARY KEY (username, product_id)
        );

        CREATE TABLE IF NOT EXISTS subscriptions (
            username TEXT PRIMARY KEY,
            tier TEXT NOT NULL DEFAULT 'free',
            req_limit_day INTEGER NOT NULL DEFAULT 1000,
            req_limit_min INTEGER NOT NULL DEFAULT 60,
            started_at TEXT,
            expires_at TEXT
        );
"""


def init_db() -> None:
    db = get_db()
    if USE_PG:
        init_db_pg(db)
    else:
        db.executescript(_SQLITE_DDL)
    db.commit()
    db.close()


# ── Rate limiter ────────────────────────────────────────────────────────────

def check_rate_limit_sqlite(ip: str, window_secs: int = 60, max_req: int = 10,
                            daily_max: int = 100) -> None:
    """Rate limiter. Persists across restarts."""
    import time as _time
    now = _time.time()
    db = get_db()

    # Daily cap
    today_start = _time.mktime(_time.strptime(
        _time.strftime("%Y-%m-%d", _time.gmtime(now)), "%Y-%m-%d"
    ))
    daily_key = f"{ip}:daily"
    db.execute("DELETE FROM rate_limits WHERE key=? AND window_start < ?", (daily_key, today_start))
    daily_row = db.execute(
        "SELECT SUM(counter) as total FROM rate_limits WHERE key=? AND window_start = ?",
        (daily_key, today_start)
    ).fetchone()
    daily_count = daily_row["total"] or 0
    if daily_count >= daily_max:
        db.close()
        from fastapi import HTTPException
        raise HTTPException(status_code=429, detail="Límite diario alcanzado (free tier: 100 req/día).")
    db.execute(
        "INSERT INTO rate_limits (key, window_start, counter) VALUES (?,?,1) "
        "ON CONFLICT(key, window_start) DO UPDATE SET counter = counter + 1",
        (daily_key, today_start)
    )

    # Per-minute cap — group by minute bucket
    minute_bucket = int(now // 60) * 60
    minute_key = f"{ip}:minute"
    db.execute("DELETE FROM rate_limits WHERE key=? AND window_start < ?", (minute_key, minute_bucket))
    minute_row = db.execute(
        "SELECT counter FROM rate_limits WHERE key=? AND window_start = ?",
        (minute_key, minute_bucket)
    ).fetchone()
    minute_count = minute_row["counter"] if minute_row else 0
    if minute_count >= max_req:
        db.close()
        from fastapi import HTTPException
        raise HTTPException(status_code=429, detail="Demasiadas solicitudes. Free tier: 10 req/min.")

    db.execute(
        "INSERT INTO rate_limits (key, window_start, counter) VALUES (?,?,1) "
        "ON CONFLICT(key, window_start) DO UPDATE SET counter = counter + 1",
        (minute_key, minute_bucket)
    )
    db.commit()
    db.close()

# ── Subscriptions / Tiered pricing ──────────────────────────────────────────────

def db_get_users() -> dict:
    """Return all users as a dict (for backwards compat with existing code)."""
    db = get_db()
    rows = db.execute("SELECT username, password_hash, token FROM app_users").fetchall()
    db.close()
    return {r["username"]: {"password": r["password_hash"], "token": r["token"]} for r in rows}

def db_save_user(username: str, password_hash: str, token: str | None = None) -> None:
    db = get_db()
    db.execute(
        "INSERT INTO app_users (username, password_hash, token, updated_at) VALUES (?,?,?,datetime('now')) "
        "ON CONFLICT(username) DO UPDATE SET password_hash=excluded.password_hash, token=excluded.token, updated_at=datetime('now')",
        (username, password_hash, token)
    )
    db.commit()
    db.close()

def db_get_cart(username: str) -> list[dict]:
    db = get_db()
    rows = db.execute(
        "SELECT id, product_id, name, price, store, store_name, quantity, url FROM app_carts WHERE username=?",
        (username,)
    ).fetchall()
    db.close()
    return [{"cart_id": str(r["id"]), "product_id": r["product_id"], "name": r["name"],
             "price": r["price"], "store": r["store"], "store_name": r["store_name"],
             "quantity": r["quantity"], "url": r["url"]} for r in rows]

def db_add_to_cart(username: str, product_id: str, name: str, price: float,
                   store: str, store_name: str = "", quantity: int = 1, url: str = "") -> int:
    db = get_db()
    if USE_PG:
        sql = "INSERT INTO app_carts (username, product_id, name, price, store, store_name, quantity, url) VALUES (?,?,?,?,?,?,?,?) RETURNING id"
    else:
        sql = "INSERT INTO app_carts (username, product_id, name, price, store, store_name, quantity, url) VALUES (?,?,?,?,?,?,?,?)"
    c = db.execute(sql, (username, product_id, name, price, store, store_name, quantity, url))
    cart_id = c.lastrowid
    db.commit()
    db.close()
    return cart_id

def db_update_cart_item(username: str, cart_id: int, quantity: int) -> bool:
    db = get_db()
    if quantity <= 0:
        db.execute("DELETE FROM app_carts WHERE id=? AND username=?", (cart_id, username))
    else:
        db.execute("UPDATE app_carts SET quantity=? WHERE id=? AND username=?", (quantity, cart_id, username))
    db.commit()
    db.close()
    return True

def db_remove_cart_item(username: str, cart_id: int) -> bool:
    db = get_db()
    db.execute("DELETE FROM app_carts WHERE id=? AND username=?", (cart_id, username))
    db.commit()
    db.close()
    return True

def db_clear_cart(username: str) -> None:
    db = get_db()
    db.execute("DELETE FROM app_carts WHERE username=?", (username,))
    db.commit()
    db.close()

def db_get_orders(username: str) -> list[dict]:
    db = get_db()
    orders = db.execute(
        "SELECT order_id, username, payment_method, total, status, created_at FROM app_orders WHERE username=? ORDER BY created_at DESC",
        (username,)
    ).fetchall()
    result = []
    for o in orders:
        items = db.execute(
            "SELECT product_id, name, price, store, store_name, quantity, url FROM app_order_items WHERE order_id=?",
            (o["order_id"],)
        ).fetchall()
        result.append({
            "order_id": o["order_id"],
            "username": o["username"],
            "payment_method": o["payment_method"],
            "total": o["total"],
            "status": o["status"],
            "created_at": o["created_at"],
            "items": [dict(i) for i in items],
        })
    db.close()
    return result

def db_create_order(username: str, items: list[dict], payment_method: str, total: float,
                    status: str = "completed", order_id: str | None = None) -> dict:
    import uuid
    if order_id is None:
        order_id = str(uuid.uuid4())[:8]
    db = get_db()
    db.execute(
        "INSERT INTO app_orders (order_id, username, payment_method, total, status) VALUES (?,?,?,?,?)",
        (order_id, username, payment_method, total, status)
    )
    for item in items:
        db.execute(
            "INSERT INTO app_order_items (order_id, product_id, name, price, store, store_name, quantity, url) VALUES (?,?,?,?,?,?,?,?)",
            (order_id, item.get("product_id", ""), item.get("name", ""), item.get("price", 0),
             item.get("store", ""), item.get("store_name", ""), item.get("quantity", 1), item.get("url", ""))
        )
    db.commit()
    db.close()
    return {"order_id": order_id, "username": username, "payment_method": payment_method, "total": total, "status": status}

def db_migrate_from_json() -> None:
    """One-time migration: import existing JSON data into SQLite tables."""
    import json as _json
    # Migrate users
    if USERS_FILE.exists():
        try:
            users = _json.loads(USERS_FILE.read_text())
            db = get_db()
            for username, data in users.items():
                if USE_PG:
                    db.execute(
                        "INSERT INTO app_users (username, password_hash, token) VALUES (?,?,?) ON CONFLICT(username) DO NOTHING",
                        (username, data.get("password", ""), data.get("token", ""))
                    )
                else:
                    db.execute(
                        "INSERT OR IGNORE INTO app_users (username, password_hash, token) VALUES (?,?,?)",
                        (username, data.get("password", ""), data.get("token", ""))
                    )
            db.commit()
            db.close()
            logger.info("Migrated %d users from JSON", len(users))
        except Exception as e:
            logger.warning("User migration skipped: %s", e)
    # Migrate carts
    if CARTS_FILE.exists():
        try:
            carts = _json.loads(CARTS_FILE.read_text())
            db = get_db()
            count = 0
            for username, items in carts.items():
                for item in items:
                    db.execute(
                        "INSERT OR IGNORE INTO app_carts (username, product_id, name, price, store, store_name, quantity, url) VALUES (?,?,?,?,?,?,?,?)",
                        (username, item.get("product_id", ""), item.get("name", ""), item.get("price", 0),
                         item.get("store", ""), item.get("store_name", ""), item.get("quantity", 1), item.get("url", ""))
                    )
                    count += 1
            db.commit()
            db.close()
            logger.info("Migrated %d cart items from JSON", count)
        except Exception as e:
            logger.warning("Cart migration skipped: %s", e)
    # Migrate orders
    if ORDERS_FILE.exists():
        try:
            orders = _json.loads(ORDERS_FILE.read_text())
            db = get_db()
            for o in orders:
                if USE_PG:
                    db.execute(
                        "INSERT INTO app_orders (order_id, username, payment_method, total, status, created_at) VALUES (?,?,?,?,?,?) ON CONFLICT(order_id) DO NOTHING",
                        (o.get("order_id", ""), o.get("username", ""), o.get("payment_method", "yape"),
                         o.get("total", 0), o.get("status", "completed"), o.get("created_at", ""))
                    )
                else:
                    db.execute(
                        "INSERT OR IGNORE INTO app_orders (order_id, username, payment_method, total, status, created_at) VALUES (?,?,?,?,?,?)",
                        (o.get("order_id", ""), o.get("username", ""), o.get("payment_method", "yape"),
                         o.get("total", 0), o.get("status", "completed"), o.get("created_at", ""))
                    )
                for item in o.get("items", []):
                    db.execute(
                        "INSERT OR IGNORE INTO app_order_items (order_id, product_id, name, price, store, store_name, quantity, url) VALUES (?,?,?,?,?,?,?,?)",
                        (o.get("order_id", ""), item.get("product_id", ""), item.get("name", ""), item.get("price", 0),
                         item.get("store", ""), item.get("store_name", ""), item.get("quantity", 1), item.get("url", ""))
                    )
            db.commit()
            db.close()
            logger.info("Migrated %d orders from JSON", len(orders))
        except Exception as e:
            logger.warning("Order migration skipped: %s", e)

def save_price_snapshot(p: dict, db: "_DB | None" = None) -> None:
    """Upsert one price snapshot.

    If `db` is None, opens its own connection (used by `/search`).
    If `db` is provided (collector batch), reuses it and does NOT commit/close —
    that's the caller's responsibility.
    """
    owns_db = db is None
    params = (
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
    )
    try:
        if owns_db:
            db = get_db()
        if USE_PG:
            db.execute("""
                INSERT INTO price_snapshots
                    (product_id, name, brand, price, list_price, discount,
                     store, store_name, currency, line, line_name, category, stock, url)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(product_id, store) DO UPDATE SET
                    price=EXCLUDED.price,
                    list_price=EXCLUDED.list_price,
                    discount=EXCLUDED.discount,
                    stock=EXCLUDED.stock,
                    queried_at=NOW()
            """, params)
        else:
            db.execute("""
                INSERT INTO price_snapshots
                    (product_id, name, brand, price, list_price, discount,
                     store, store_name, currency, line, line_name, category, stock, url)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(product_id, store) DO UPDATE SET
                    price=excluded.price,
                    list_price=excluded.list_price,
                    discount=excluded.discount,
                    stock=excluded.stock,
                    queried_at=datetime('now')
            """, params)
        if owns_db:
            db.commit()
            db.close()
    except Exception as e:
        logger.warning("save_price_snapshot failed: %s", e)
        if owns_db and db is not None:
            try:
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
    except Exception as e:
        logger.warning("save_search_query failed: %s", e)

# ── API Keys ────────────────────────────────────────────────────────────────────

def db_create_api_key(username: str, scopes: str = "read", label: str = "") -> dict:
    """Generate a new API key. Returns {key, prefix, scopes, id}. The raw key is only shown once."""
    import secrets, hashlib
    raw = "sk-" + secrets.token_urlsafe(32)
    prefix = raw[:10] + "..."
    key_hash = hashlib.sha256(raw.encode()).hexdigest()
    db = get_db()
    if USE_PG:
        db.execute(
            "INSERT INTO api_keys (username, key_hash, key_prefix, scopes, label) VALUES (?,?,?,?,?) RETURNING id",
            (username, key_hash, prefix, scopes, label)
        )
        key_id = db.execute("SELECT id FROM api_keys WHERE key_hash=?", (key_hash,)).fetchone()["id"]
    else:
        db.execute(
            "INSERT INTO api_keys (username, key_hash, key_prefix, scopes, label) VALUES (?,?,?,?,?)",
            (username, key_hash, prefix, scopes, label)
        )
        key_id = db.execute("SELECT last_insert_rowid()").fetchone()[0]
    db.commit()
    db.close()
    return {"id": key_id, "key": raw, "prefix": prefix, "scopes": scopes, "label": label}


def db_list_api_keys(username: str) -> list[dict]:
    db = get_db()
    rows = db.execute(
        "SELECT id, key_prefix, scopes, label, created_at, last_used_at FROM api_keys WHERE username=? ORDER BY created_at DESC",
        (username,)
    ).fetchall()
    db.close()
    return [dict(r) for r in rows]


def db_revoke_api_key(username: str, key_id: int) -> bool:
    db = get_db()
    db.execute("DELETE FROM api_keys WHERE id=? AND username=?", (key_id, username))
    affected = db.execute("SELECT changes()").fetchone()[0] if not USE_PG else db._conn.cursor().rowcount
    db.commit()
    db.close()
    return affected > 0


def db_validate_api_key(key: str) -> dict | None:
    """Validate an API key. Returns {username, scopes, key_id} or None."""
    import hashlib
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    db = get_db()
    row = db.execute(
        "SELECT username, scopes, id FROM api_keys WHERE key_hash=?",
        (key_hash,)
    ).fetchone()
    if row:
        db.execute("UPDATE api_keys SET last_used_at=datetime('now') WHERE id=?", (row["id"],))
        db.commit()
    db.close()
    return dict(row) if row else None


# ── Subscriptions / Tiered pricing ──────────────────────────────────────────────

TIERS = {
    "free":      {"req_min": 60,  "req_day": 1000, "api_keys": 1,  "checkout": False},
    "pro":       {"req_min": 300, "req_day": 10000, "api_keys": 10, "checkout": True},
    "enterprise": {"req_min": 0,  "req_day": 0,     "api_keys": 0,  "checkout": True},
}

def db_get_subscription(username: str) -> dict:
    """Get user subscription. Falls back to free tier defaults."""
    db = get_db()
    row = db.execute(
        "SELECT tier, req_limit_day, req_limit_min FROM subscriptions WHERE username=?",
        (username,)
    ).fetchone()
    db.close()
    if row:
        return dict(row)
    return {"tier": "free", "req_limit_day": TIERS["free"]["req_day"],
            "req_limit_min": TIERS["free"]["req_min"]}

def db_set_subscription(username: str, tier: str, req_day: int | None = None,
                        req_min: int | None = None, expires_days: int | None = None) -> dict:
    db = get_db()
    t = TIERS.get(tier, TIERS["free"])
    day = req_day if req_day is not None else t["req_day"]
    mn = req_min if req_min is not None else t["req_min"]
    db.execute(
        "INSERT INTO subscriptions (username, tier, req_limit_day, req_limit_min) VALUES (?,?,?,?) "
        "ON CONFLICT(username) DO UPDATE SET tier=?, req_limit_day=?, req_limit_min=?",
        (username, tier, day, mn, tier, day, mn)
    )
    db.commit()
    db.close()
    return {"username": username, "tier": tier, "req_limit_day": day, "req_limit_min": mn}


def check_rate_limit_sqlite(ip: str, window_secs: int = 60, max_req: int = 10,
                            daily_max: int = 100) -> None:
    """Rate limiter. Persists across restarts. Updated to support tiered limits."""
    import time as _time
    now = _time.time()
    db = get_db()
    # Daily cap
    today_start = _time.mktime(_time.strptime(
        _time.strftime("%Y-%m-%d", _time.gmtime(now)), "%Y-%m-%d"
    ))
    daily_key = f"{ip}:daily"
    db.execute("DELETE FROM rate_limits WHERE key=? AND window_start < ?", (daily_key, today_start))
    daily_row = db.execute(
        "SELECT SUM(counter) as total FROM rate_limits WHERE key=? AND window_start = ?",
        (daily_key, today_start)
    ).fetchone()
    daily_count = daily_row["total"] or 0
    if daily_count >= daily_max:
        db.close()
        from fastapi import HTTPException
        raise HTTPException(status_code=429, detail=f"Daily limit reached ({daily_max} req/day).")
    # Per-minute cap
    window_key = f"{ip}:min"
    db.execute("DELETE FROM rate_limits WHERE key=? AND window_start < ?", (window_key, now - window_secs))
    min_count = db.execute(
        "SELECT SUM(counter) as total FROM rate_limits WHERE key=? AND window_start >= ?",
        (window_key, now - window_secs)
    ).fetchone()["total"] or 0
    if min_count >= max_req:
        db.close()
        from fastapi import HTTPException
        raise HTTPException(status_code=429, detail=f"Rate limit reached ({max_req} req/{window_secs}s).")
    db.execute("INSERT INTO rate_limits (key, window_start, counter) VALUES (?,?,1)", (daily_key, today_start))
    db.execute("INSERT INTO rate_limits (key, window_start, counter) VALUES (?,?,1)", (window_key, now))
    db.commit()
    db.close()


# ── Initialize DB at import time ──────────────────────────────────────────────
try:
    init_db()
except Exception as e:
    logger.error("Database initialization failed: %s", e)
    if USE_PG:
        logger.warning("PostgreSQL unavailable — falling back to SQLite")
        USE_PG = False
        try:
            init_db()
        except Exception as e2:
            logger.error("SQLite fallback also failed: %s", e2)
