#!/usr/bin/env python3
"""Busqueda refinada de materiales de construccion."""
import json, os, urllib.request

API_URL = "https://cli-market-api.fly.dev"
SESSION_FILE = os.path.join(os.path.expanduser("~"), ".market", "session.json")

with open(SESSION_FILE) as f:
    TOKEN = json.load(f).get("api_key", "")

QUERIES = [
    # Cola sintetica - probar variantes de pegamento
    ("pegamento PVC", "Pegamento PVC (alternativa cola sintetica)"),
    ("cola PVC tuberia", "Cola PVC tuberia"),
    # Sellador CPP - buscar por CPP especificamente
    ("sellador CPP balde", "Sellador CPP balde grande"),
    ("CPP sellador impermeabilizante", "CPP sellador impermeabilizante"),
    # Temple Pato
    ("temple pato", "Temple Pato especifico"),
    # Lijas ya OK pero busco lija de fierro especifica
    ("lija fierro grano 80", "Lija fierro grano 80"),
    ("lija fierro grano 150", "Lija fierro grano 150"),
    # Yeso Henci
    ("Henci yeso", "Yeso marca Henci"),
    # Anypsa
    ("Anypsa", "Cualquier producto Anypsa"),
    ("esmalte satinado blanco galon", "Esmalte satinado blanco galon"),
    # Vencelatex balde grande
    ("Vencelatex balde", "Vencelatex balde grande"),
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
