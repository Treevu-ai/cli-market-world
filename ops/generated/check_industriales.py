#!/usr/bin/env python3
import urllib.request, json

SITES = [
    ("INXORA", "https://inxora.com"),
    ("TECNOTOTAL", "https://tecnototal.pe"),
    ("FAGY PERU", "https://fagy.com.pe"),
    ("EPPs Peru", "https://epps.pe"),
    ("Indutex Peru", "https://indutex.com.pe"),
    ("Prosinfer", "https://prosinfer.com"),
    ("TERRAN", "https://terran.com.pe"),
    ("Cussto Textil", "https://cusstotextil.com"),
    ("Safety Store Peru", "https://safetystore.pe"),
    ("Ferreindustrias", "https://ferreindustrias.pe"),
]

PLATFORM = [("VTEX",["vtex"]),("Shopify",["shopify","myshopify"]),("WooCommerce",["woocommerce","wc-"]),("Magento",["magento"]),("PrestaShop",["prestashop"])]
H = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

for label, url in SITES:
    print(f"\n{'='*55}")
    print(f">> {label}: {url}")
    try:
        req = urllib.request.Request(url, headers=H)
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read(40000).decode("utf-8",errors="ignore").lower()
        plat = "Custom"
        for p,sigs in PLATFORM:
            if any(s in html for s in sigs):
                plat = p
                break
        title = html.split("<title>")[-1].split("</title>")[0][:100] if "<title>" in html else "N/A"
        cart = any(w in html for w in ["carrito","cart","add-to-cart","comprar","checkout"])
        print(f"   HTTP {resp.status} | Title: {title}")
        print(f"   Plataforma: {plat} | Carrito: {'SI' if cart else 'NO'}")
        domain = url.split("://")[1].split("/")[0]
        if plat == "Shopify":
            try:
                r = urllib.request.urlopen(urllib.request.Request(f"https://{domain}/products.json?limit=2",headers=H),timeout=10)
                d = json.loads(r.read().decode("utf-8"))
                prods = d.get("products",[])
                print(f"   API: {len(prods)} prod")
                for p in prods[:2]:
                    v=p.get("variants",[])
                    print(f"      - {p.get('title','?')[:55]}: S/ {v[0].get('price','?') if v else '?'}")
            except:
                pass
        if plat == "WooCommerce":
            try:
                r = urllib.request.urlopen(urllib.request.Request(f"https://{domain}/wp-json/wc/v3/products?per_page=2",headers=H),timeout=10)
                d = json.loads(r.read().decode("utf-8"))
                print(f"   API WC: {len(d)} prod")
                for p in d[:2]:
                    print(f"      - {p.get('name','?')[:55]}: S/ {p.get('price','?')}")
            except:
                pass
    except Exception as e:
        print(f"   ERROR: {type(e).__name__}: {str(e)[:100]}")

print(f"\n{'='*55}")
print("Listo.")
