#!/usr/bin/env python3
import urllib.request, json, os

API = "https://cli-market-api.fly.dev"
SESSION_FILE = os.path.join(os.path.expanduser("~"), ".market", "session.json")
with open(SESSION_FILE) as f:
    TOKEN = json.load(f).get("api_key", "")
H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

body = json.dumps({"query": "taladro", "country": "PE", "limit": 1}).encode()
req = urllib.request.Request(f"{API}/products/search", data=body, headers=H, method="POST")
with urllib.request.urlopen(req, timeout=20) as resp:
    data = json.loads(resp.read().decode())
    stores = data.get("source_health", {}).get("stores", [])
    
    # Filter for interested stores
    target = ["sodimac", "promart", "ferrincorp"]
    for s in stores:
        store_key = s.get("store", "")
        if any(t in store_key.lower() for t in target):
            print(f"{store_key}: state={s.get('state')}, success={s.get('success_pct')}%, failures={s.get('consecutive_failures')}, last_success={s.get('last_success')}")
    
    # Also show all PE hogar/industrial stores
    print("\n--- PE non-supermercado ---")
    for s in stores:
        store_key = s.get("store", "")
        if s.get("country") == "PE" and store_key not in ["wong", "metro", "plazavea", "mimercado_delivery"]:
            print(f"  {store_key}: {s.get('store_name')} state={s.get('state')} success={s.get('success_pct')}%")
