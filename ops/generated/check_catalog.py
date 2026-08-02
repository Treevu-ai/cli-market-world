#!/usr/bin/env python3
"""Verificar catalogo disponible en Peru."""
import json, os, urllib.request

API_URL = "https://cli-market-api.fly.dev"
SESSION_FILE = os.path.join(os.path.expanduser("~"), ".market", "session.json")

with open(SESSION_FILE) as f:
    TOKEN = json.load(f).get("api_key", "")

def api_call(endpoint):
    req = urllib.request.Request(
        f"{API_URL}{endpoint}",
        headers={"Authorization": f"Bearer {TOKEN}"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

# Check lines/stores available
print("=== INTEL BRIEF PE ===")
body = json.dumps({"country": "PE"}).encode("utf-8")
req = urllib.request.Request(
    f"{API_URL}/intel/brief",
    data=body,
    headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        print(json.dumps(data, indent=2, ensure_ascii=False)[:2000])
except Exception as e:
    print(f"Error: {e}")

# Try a broader search for construction items  
print("\n=== SEARCH: 'pintura' PE ===")
body = json.dumps({"query": "pintura", "country": "PE", "limit": 5}).encode("utf-8")
req = urllib.request.Request(
    f"{API_URL}/products/search",
    data=body,
    headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        items = data.get("items", [])
        print(f"Total: {data.get('total', 0)}")
        for i, item in enumerate(items[:5]):
            print(f"  {i+1}. {item.get('name','?')[:80]}")
            print(f"     {item.get('price','?')} | {item.get('retailer_name','?')} | {item.get('line','?')}")
except Exception as e:
    print(f"Error: {e}")

print("\n=== SEARCH: 'construccion' PE ===")
body = json.dumps({"query": "construccion", "country": "PE", "limit": 5}).encode("utf-8")
req = urllib.request.Request(
    f"{API_URL}/products/search",
    data=body,
    headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode("utf-8"))
        items = data.get("items", [])
        print(f"Total: {data.get('total', 0)}")
        for i, item in enumerate(items[:5]):
            print(f"  {i+1}. {item.get('name','?')[:80]}")
            print(f"     {item.get('price','?')} | {item.get('retailer_name','?')} | {item.get('line','?')}")
except Exception as e:
    print(f"Error: {e}")
