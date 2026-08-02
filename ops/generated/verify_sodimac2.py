#!/usr/bin/env python3
import urllib.request, json, os

API = "https://cli-market-api.fly.dev"
SESSION_FILE = os.path.join(os.path.expanduser("~"), ".market", "session.json")
with open(SESSION_FILE) as f:
    TOKEN = json.load(f).get("api_key", "")
H = {"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"}

# Full source_health
body = json.dumps({"query": "taladro", "country": "PE", "limit": 1}).encode()
req = urllib.request.Request(f"{API}/products/search", data=body, headers=H, method="POST")
with urllib.request.urlopen(req, timeout=20) as resp:
    data = json.loads(resp.read().decode())
    health = data.get("source_health", {})
    stores_health = health.get("stores", {})
    
    # Check for sodimac
    sodimac_keys = [k for k in stores_health if "sodimac" in k.lower()]
    promart_keys = [k for k in stores_health if "promart" in k.lower()]
    ferrincorp_keys = [k for k in stores_health if "ferrin" in k.lower()]
    
    print(f"Source health summary: {health.get('summary', {})}")
    print(f"\nSodimac keys in health: {sodimac_keys}")
    for k in sodimac_keys:
        print(f"  {k}: {json.dumps(stores_health[k], ensure_ascii=False)[:200]}")
    print(f"\nPromart keys in health: {promart_keys}")
    for k in promart_keys:
        print(f"  {k}: {json.dumps(stores_health[k], ensure_ascii=False)[:200]}")
    print(f"\nFerrincorp keys: {ferrincorp_keys}")
    for k in ferrincorp_keys:
        print(f"  {k}: {json.dumps(stores_health[k], ensure_ascii=False)[:200]}")
    
    # All stores with "pe" suffix
    pe_stores = [k for k in stores_health if k.endswith("_pe")]
    print(f"\nAll PE stores in health ({len(pe_stores)}): {pe_stores}")
