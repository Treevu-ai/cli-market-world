#!/usr/bin/env python3
"""E2E verification for CLI Market — calling handlers directly."""
import sys, os, time, threading, tempfile, shutil

# ── Use temp dir to avoid lock conflicts ──
TEST_DIR = tempfile.mkdtemp(prefix="market_e2e_")
os.environ["MARKET_DATA_DIR"] = TEST_DIR

print(f"=== Starting server (data: {TEST_DIR}) ===")
import uvicorn
def serve():
    uvicorn.run("market_server:app", host="127.0.0.1", port=8767, log_level="error")
t = threading.Thread(target=serve, daemon=True)
t.start()
time.sleep(3)

import httpx
try:
    r = httpx.get("http://127.0.0.1:8767/", timeout=5)
    print(f"  Server: {r.json()}")
except httpx.ConnectError:
    print("  Server: FAIL (could not connect)")
    shutil.rmtree(TEST_DIR, ignore_errors=True)
    sys.exit(1)

import market_cli
market_cli.API = "http://127.0.0.1:8767"

session = market_cli.SESSION_FILE
if session.exists():
    session.unlink()

print("\n=== Human Developer Flow ===")

from argparse import Namespace

def test(name, fn, args, expect_ok=True):
    try:
        fn(args)
        ok = True
    except SystemExit:
        ok = False
    status = "OK" if ok == expect_ok else "FAIL"
    print(f"  [{status}] {name}")

test("login", market_cli.cmd_login, Namespace(username="admin", password="market"))
test("search leche --country PE", market_cli.cmd_search,
     Namespace(query="leche", store=None, country="PE", line=None, limit=3, page=1, json=False))
test("search '' (shows help)", market_cli.cmd_search,
     Namespace(query="", store=None, country=None, line=None, limit=10, page=1, json=False))
test("add #1 --qty 2", market_cli.cmd_add,
     Namespace(product_id="1", name=None, price=None, store=None, qty=2))
test("cart", market_cli.cmd_cart, Namespace(json=False))
test("cart-update", market_cli.cmd_cart_update,
     Namespace(product_id="1", quantity=3))
test("cart-remove", market_cli.cmd_cart_update,
     Namespace(product_id="1", quantity=0))
test("lines", market_cli.cmd_lines, Namespace())
test("search celular --line electro", market_cli.cmd_search,
     Namespace(query="celular", store=None, country=None, line="electro", limit=2, page=1, json=False))
test("compare leche --country PE", market_cli.cmd_compare,
     Namespace(query="leche", country="PE", line=None, limit=3, json=False))
test("checkout (empty cart)", market_cli.cmd_checkout,
     Namespace(payment="yape"), expect_ok=False)

print("\n=== MCP Agent Flow ===")
import market_mcp
print(f"  Tools registered: {len(market_mcp.TOOLS)}")
for t in market_mcp.TOOLS:
    print(f"  · {t['name']}: {t['description'][:85]}")

print("\n=== Config verification ===")
print(f"  STORES: {len(market_cli.STORES)}")
print(f"  LINES: {list(market_cli.LINES.keys())}")
print(f"  COUNTRIES: {list(market_cli.COUNTRIES.keys())}")

shutil.rmtree(TEST_DIR, ignore_errors=True)

print("\n=== ALL DONE ===")
