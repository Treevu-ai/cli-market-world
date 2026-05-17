#!/usr/bin/env python3
"""E2E verification for CLI Market — calling handlers directly."""
import sys, json, time, threading

print("=== Starting server ===")
import uvicorn
def serve():
    uvicorn.run("market_server:app", host="127.0.0.1", port=8767, log_level="error")
t = threading.Thread(target=serve, daemon=True)
t.start()
time.sleep(3)

import httpx
r = httpx.get("http://127.0.0.1:8767/", timeout=5)
print(f"  Server: {r.json()}")

# Override
import market_cli
market_cli.API = "http://127.0.0.1:8767"

# Clear session
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

# 1. login
test("login", market_cli.cmd_login, Namespace(username="admin", password="market"))

# 2. search
test("search leche --country PE", market_cli.cmd_search,
     Namespace(query="leche", store=None, country="PE", line=None, limit=3, page=1))

# 3. search empty
test("search '' (shows help)", market_cli.cmd_search,
     Namespace(query="", store=None, country=None, line=None, limit=10, page=1))

# 4. add via table #
test("add #1 --qty 2", market_cli.cmd_add,
     Namespace(product_id="1", name=None, price=None, store=None, qty=2))

# 5. cart
test("cart", market_cli.cmd_cart, Namespace())

# 6. cart-update
test("cart-update", market_cli.cmd_cart_update,
     Namespace(product_id="1", quantity=3))

# 7. cart-remove (qty=0 same handler)
test("cart-remove", market_cli.cmd_cart_update,
     Namespace(product_id="1", quantity=0))

# 8. lines
test("lines", market_cli.cmd_lines, Namespace())

# 9. search with line filter
test("search celular --line electro", market_cli.cmd_search,
     Namespace(query="celular", store=None, country=None, line="electro", limit=2, page=1))

# 10. compare dynamic
test("compare leche --country PE", market_cli.cmd_compare,
     Namespace(query="leche", country="PE", line=None, limit=3))

# 11. checkout (cart will be empty but test the flow)
test("checkout (empty cart)", market_cli.cmd_checkout,
     Namespace(payment="yape"), expect_ok=False)

print("\n=== MCP Agent Flow ===")
import market_mcp
print(f"  Tools registered: {len(market_mcp.TOOLS)}")
for t in market_mcp.TOOLS:
    print(f"  · {t['name']}: {t['description'][:85]}")

# Verify search returns correct fields
import market_server as ms
print(f"\n=== Config verification ===")
print(f"  STORES: {len(ms.STORES)}")
print(f"  LINES: {list(ms.LINES.keys())}")
print(f"  Store fields: {list(ms.STORES['wong'].keys())}")
print(f"  Exito present: {'exito' in ms.STORES}")
print(f"  COUNTRIES: {list(ms.COUNTRIES.keys())}")

print("\n=== ALL DONE ===")
