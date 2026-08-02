#!/usr/bin/env python3
import urllib.request, json, sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

SITES = [
    ("FAGY PERU", "https://fagy.com.pe"),
    ("TECNOTOTAL WC API", "https://www.tecnototalperu.com/wp-json/wc/v3/products?per_page=2"),
    ("Safety Store API", "https://safetystore.pe/products.json?limit=3"),
]

H = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

for label, url in SITES:
    print(f"\n{'='*55}")
    print(f">> {label}: {url}")
    try:
        req = urllib.request.Request(url, headers=H)
        resp = urllib.request.urlopen(req, timeout=15)
        raw = resp.read(40000)
        
        # Try to detect if it's JSON
        try:
            data = json.loads(raw.decode("utf-8"))
            if isinstance(data, list):
                print(f"   API: {len(data)} productos")
                for p in data[:3]:
                    print(f"      - {p.get('name','?')[:60]}: S/ {p.get('price','?')}")
            elif isinstance(data, dict):
                prods = data.get("products", [])
                print(f"   API Shopify: {len(prods)} prod")
                for p in prods[:3]:
                    v = p.get("variants", [])
                    print(f"      - {p.get('title','?')[:60]}: S/ {v[0].get('price','?') if v else '?'}")
            continue
        except:
            pass
        
        html = raw.decode("utf-8", errors="replace").lower()
        plat = "Custom"
        for p,sigs in [("VTEX",["vtex"]),("Shopify",["shopify"]),("WooCommerce",["woocommerce"]),("Magento",["magento"])]:
            if any(s in html for s in sigs):
                plat = p
                break
        title = html.split("<title>")[-1].split("</title>")[0][:100] if "<title>" in html else "N/A"
        cart = any(w in html for w in ["carrito","cart","add-to-cart"])
        print(f"   HTTP {resp.status} | Title: {title}")
        print(f"   Plataforma: {plat} | Carrito: {'SI' if cart else 'NO'}")
    except Exception as e:
        print(f"   ERROR: {type(e).__name__}: {str(e)[:120]}")

print(f"\n{'='*55}")
print("Listo.")
