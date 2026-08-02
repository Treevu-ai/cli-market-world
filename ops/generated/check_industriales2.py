#!/usr/bin/env python3
import urllib.request, json

SITES = [
    ("FAGY PERU", "https://fagy.com.pe"),
    ("Prosinfer WC API", "https://prosinfer.com/wp-json/wc/v3/products?per_page=2"),
    ("TECNOTOTAL alt", "https://www.tecnototalperu.com"),
    ("Ferreindustrias prod", "https://www.ferreindustrias.pe/productos"),
]

H = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

for label, url in SITES:
    print(f"\n{'='*55}")
    print(f">> {label}: {url}")
    try:
        req = urllib.request.Request(url, headers=H)
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read(40000).decode("utf-8",errors="ignore").lower()
        
        plat = "Custom"
        for p,sigs in [("VTEX",["vtex"]),("Shopify",["shopify"]),("WooCommerce",["woocommerce"]),("Magento",["magento"])]:
            if any(s in html for s in sigs):
                plat = p
                break
        
        # Check if it's JSON API response
        if "products.json" in url or "wp-json" in url:
            try:
                data = json.loads(html)
                if isinstance(data, list):
                    print(f"   API WC: {len(data)} productos")
                    for p in data[:2]:
                        print(f"      - {p.get('name','?')[:60]}: S/ {p.get('price','?')}")
                elif isinstance(data, dict):
                    prods = data.get("products", data.get("data", []))
                    print(f"   API: {len(prods)} productos")
                    for p in prods[:2]:
                        if isinstance(p, dict):
                            name = p.get("name", p.get("title", "?"))
                            price = p.get("price", p.get("variants",[{}])[0].get("price","?"))
                            print(f"      - {name[:60]}: S/ {price}")
            except:
                pass
        
        title = html.split("<title>")[-1].split("</title>")[0][:100] if "<title>" in html else "N/A"
        cart = any(w in html for w in ["carrito","cart","add-to-cart","comprar","checkout"])
        print(f"   HTTP {resp.status} | Title: {title}")
        print(f"   Plataforma: {plat} | Carrito: {'SI' if cart else 'NO'}")
    except Exception as e:
        print(f"   ERROR: {type(e).__name__}: {str(e)[:100]}")

print(f"\n{'='*55}")
print("Listo.")
