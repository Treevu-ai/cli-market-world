#!/usr/bin/env python3
import urllib.request, json, os

API = "https://cli-market-api.fly.dev"
SESSION_FILE = os.path.join(os.path.expanduser("~"), ".market", "session.json")
with open(SESSION_FILE) as f:
    TOKEN = json.load(f).get("api_key", "")
H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

# 1. Search - check source_health
print("=== Source health via search ===")
body = json.dumps({"query": "taladro", "country": "PE", "limit": 1}).encode()
req = urllib.request.Request(f"{API}/products/search", data=body, headers=H, method="POST")
try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode())
        health = data.get("source_health", {})
        stores = data.get("stores_resolved", [])
        print(f"Stores resolved: {stores}")
        print(f"Source health keys: {list(health.keys())}")
        for k in ["sodimac_pe", "sodimac", "ferrincorp_pe", "promart"]:
            if k in health:
                print(f"  {k}: {health[k]}")
except Exception as e:
    print(f"Error: {e}")

# 2. Discover
print("\n=== Discover PE ===")
body = json.dumps({"country": "PE"}).encode()
req = urllib.request.Request(f"{API}/products/discover", data=body, headers=H, method="POST")
try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read().decode())
        if isinstance(data, dict):
            stores = data.get("stores", [])
            print(f"Total stores: {len(stores)}")
            # Filter for PE construction/hogar
            for s in stores:
                if s.get("store") in ["sodimac_pe", "promart", "ferrincorp_pe"]:
                    print(f"  {s}")
            # Show all PE store keys
            pe_keys = [s.get("store") for s in stores if s.get("country") == "PE"]
            print(f"PE store keys: {pe_keys}")
except Exception as e:
    print(f"Error: {e}")

# 3. Direct market CLI
print("\n=== market discover PE ===")
