#!/usr/bin/env python3
"""Debug: ver estructura de respuesta."""
import json, os, urllib.request

API_URL = "https://cli-market-api.fly.dev"
SESSION_FILE = os.path.join(os.path.expanduser("~"), ".market", "session.json")

with open(SESSION_FILE) as f:
    TOKEN = json.load(f).get("api_key", "")

body = json.dumps({"query": "pintura", "country": "PE", "limit": 3}).encode("utf-8")
req = urllib.request.Request(
    f"{API_URL}/products/search",
    data=body,
    headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
    method="POST",
)
with urllib.request.urlopen(req, timeout=30) as resp:
    data = json.loads(resp.read().decode("utf-8"))
    # Print top-level keys
    print("Top-level keys:", list(data.keys()))
    print("Total:", data.get("total"))
    items = data.get("items", [])
    print("Items count:", len(items))
    if items:
        item0 = items[0]
        print("Item[0] keys:", list(item0.keys()))
        print(json.dumps(item0, indent=2, ensure_ascii=False))
    else:
        # Maybe items is nested?
        print("Raw structure (first 1000 chars):")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:1000])
