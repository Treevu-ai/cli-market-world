#!/usr/bin/env python3
import urllib.request, json

url = "https://www.total-toolsperu.com"
print(f">> {url}")

try:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    resp = urllib.request.urlopen(req, timeout=15)
    html = resp.read(40000).decode("utf-8", errors="ignore").lower()
    
    platform = "Custom"
    for p, sigs in [("VTEX", ["vtex"]), ("Shopify", ["shopify","myshopify"]), ("WooCommerce", ["woocommerce","wc-"]), ("Magento", ["magento"]), ("PrestaShop", ["prestashop"])]:
        if any(s in html for s in sigs):
            platform = p
            break
    
    title = html.split("<title>")[-1].split("</title>")[0][:120] if "<title>" in html else "N/A"
    cart = any(w in html for w in ["carrito","cart","add-to-cart","comprar","checkout"])
    print(f"   HTTP {resp.status} | Title: {title}")
    print(f"   Plataforma: {platform} | Carrito: {'SI' if cart else 'NO'}")
    
    if platform == "Shopify":
        for api in ["/products.json?limit=2", "/collections/all/products.json?limit=2"]:
            try:
                r = urllib.request.urlopen(urllib.request.Request(f"https://www.total-toolsperu.com{api}", headers={"User-Agent": "Mozilla/5.0"}), timeout=10)
                data = json.loads(r.read().decode("utf-8"))
                prods = data.get("products", [])
                print(f"   API {api}: {len(prods)} productos")
                for p in prods[:2]:
                    v = p.get("variants", [])
                    print(f"      - {p.get('title','?')[:60]}: S/ {v[0].get('price','?') if v else '?'}")
                break
            except Exception as e:
                print(f"   API: {type(e).__name__}")
    
    if platform == "WooCommerce":
        try:
            r = urllib.request.urlopen(urllib.request.Request("https://www.total-toolsperu.com/wp-json/wc/v3/products?per_page=2", headers={"User-Agent": "Mozilla/5.0"}), timeout=10)
            data = json.loads(r.read().decode("utf-8"))
            print(f"   API WC: {len(data)} productos")
            for p in data[:2]:
                print(f"      - {p.get('name','?')[:60]}: S/ {p.get('price','?')}")
        except Exception as e:
            print(f"   API WC: {type(e).__name__}")
except Exception as e:
    print(f"   ERROR: {type(e).__name__}: {str(e)[:120]}")
