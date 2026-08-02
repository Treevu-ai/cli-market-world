#!/usr/bin/env python3
import urllib.request, json, ssl

url = "https://www.total-toolsperu.com"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "es-PE,es;q=0.9,en;q=0.8",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1",
}

print(f">> {url}")
try:
    req = urllib.request.Request(url, headers=headers)
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
        for api in ["/products.json?limit=2"]:
            try:
                r = urllib.request.urlopen(urllib.request.Request(f"https://www.total-toolsperu.com{api}", headers=headers), timeout=10)
                data = json.loads(r.read().decode("utf-8"))
                prods = data.get("products", [])
                print(f"   API: {len(prods)} productos")
                for p in prods[:2]:
                    v = p.get("variants", [])
                    print(f"      - {p.get('title','?')[:60]}: S/ {v[0].get('price','?') if v else '?'}")
            except Exception as e:
                print(f"   API: {type(e).__name__}")
except Exception as e:
    print(f"   ERROR: {type(e).__name__}: {str(e)[:120]}")

print("\nListo.")
