#!/usr/bin/env python3
"""Busquedas finales para productos faltantes."""
import json, os, urllib.request

API_URL = "https://cli-market-api.fly.dev"
SESSION_FILE = os.path.join(os.path.expanduser("~"), ".market", "session.json")

with open(SESSION_FILE) as f:
    TOKEN = json.load(f).get("api_key", "")

QUERIES = [
    ("adhesivo PVC tuberia", "Adhesivo PVC tuberia (cola sintetica)"),
    ("soldadura PVC", "Soldadura PVC (cola sintetica)"),
    ("pegamento tubo PVC", "Pegamento tubo PVC"),
    ("sellador acrilico blanco galon", "Sellador acrilico blanco galon"),
    ("esmalte satinado latex blanco galon", "Esmalte satinado latex blanco galon"),
    ("pintura satinada blanco galon", "Pintura satinada blanco galon"),
    ("pintura latex blanco galon Promart", "Pintura latex blanco galon"),
]

for query, label in QUERIES:
    sep = "-" * 70
    print(f"\n{sep}")
    print(f">> {label}")
    print(f"   Query: '{query}'")
    print(sep)

    body = json.dumps({"query": query, "country": "PE", "limit": 5}).encode("utf-8")
    req = urllib.request.Request(
        f"{API_URL}/products/search",
        data=body,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = data.get("results", [])
            total = data.get("total", 0)
            if not results:
                print(f"   [Sin resultados] (total={total})")
            else:
                print(f"   Total: {total}")
                for i, item in enumerate(results[:5]):
                    name = item.get("name", "N/A")[:90]
                    price = item.get("price", "N/A")
                    brand = item.get("brand", "-")
                    store = item.get("store_name", item.get("store", "N/A"))
                    print(f"   {i+1}. {name}")
                    print(f"      S/ {price} | {brand} | {store}")
    except Exception as e:
        print(f"   Error: {e}")

print(f"\n{'='*70}")
print("Listo.")
