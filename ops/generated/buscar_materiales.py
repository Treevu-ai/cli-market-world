#!/usr/bin/env python3
"""Busqueda de materiales de construccion en CLI Market Peru — v4 (campo results)."""
import json, os, urllib.request, urllib.error

API_URL = "https://cli-market-api.fly.dev"
SESSION_FILE = os.path.join(os.path.expanduser("~"), ".market", "session.json")

with open(SESSION_FILE) as f:
    data = json.load(f)
    TOKEN = data.get("api_key") or data.get("token", "")

QUERIES = [
    ("cola sintetica clasica", "Cola Sintetica Clasica (3 sachets)"),
    ("sellador CPP", "Sellador CPP (1 balde grande)"),
    ("temple pato 25 kg", "Temple Pato 25kg (5 cajas)"),
    ("lija fierro 80", "Lija #80 fierro (6 u)"),
    ("lija fierro 150", "Lija #150 fierro (8 u)"),
    ("yeso Henci", "Yeso fino Henci (4 u)"),
    ("Anypsa Satinlast blanco", "Anypsa Satinlast Blanco 1 galon"),
    ("Vencedor Vencelatex", "Vencedor Vencelatex (2 baldes grandes)"),
    ("Vencelatex blanco", "Vencelatex Blanco techo (2 galones)"),
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
    except urllib.error.HTTPError as e:
        print(f"   HTTP {e.code}: {e.read().decode()[:200]}")
    except Exception as e:
        print(f"   Error: {e}")

print(f"\n{'='*70}")
print("Listo.")
