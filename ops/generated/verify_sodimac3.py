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
    health = data.get("source_health", {})
    stores_health = health.get("stores", {})
    
    print(f"Type of stores_health: {type(stores_health)}")
    if isinstance(stores_health, dict):
        keys = list(stores_health.keys())
        print(f"Keys ({len(keys)}): {keys[:10]}")
        # Look at one value to understand structure
        if keys:
            k0 = keys[0]
            v0 = stores_health[k0]
            print(f"\nExample key: {k0} (type: {type(k0).__name__})")
            print(f"Value type: {type(v0).__name__}")
            if isinstance(v0, dict):
                print(f"Value keys: {list(v0.keys())}")
                print(f"Value: {json.dumps(v0, ensure_ascii=False)[:300]}")
        
        # Search for sodimac manually
        for k, v in stores_health.items():
            if isinstance(k, str) and "sodimac" in k.lower():
                print(f"\nSODIMAC FOUND: {k}")
                print(json.dumps(v, ensure_ascii=False)[:300])
            if isinstance(k, dict):
                if "sodimac" in str(k).lower():
                    print(f"\nSODIMAC in dict key: {k}")
    elif isinstance(stores_health, list):
        print(f"List of {len(stores_health)} items")
        for item in stores_health[:3]:
            print(f"  Item type: {type(item).__name__}")
            if isinstance(item, dict):
                print(f"  Item keys: {list(item.keys())}")
                print(f"  Item: {json.dumps(item, ensure_ascii=False)[:200]}")
