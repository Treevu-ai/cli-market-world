#!/usr/bin/env python3
"""Verificar API Shopify de Ferretec."""
import urllib.request, json

# Shopify exposes /products.json on most stores
urls = [
    "https://ferretec.pe/products.json?limit=3",
    "https://ferretec.pe/collections/all/products.json?limit=3",
]

for url in urls:
    print(f"\n>> {url}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=15)
        data = json.loads(resp.read().decode("utf-8"))
        products = data.get("products", [])
        print(f"   HTTP {resp.status} | Products: {len(products)}")
        for p in products[:3]:
            title = p.get("title", "N/A")
            variants = p.get("variants", [])
            price = variants[0].get("price", "N/A") if variants else "N/A"
            print(f"   - {title[:80]}: S/ {price}")
    except Exception as e:
        print(f"   ERROR: {type(e).__name__}: {e}")

print("\nListo.")
