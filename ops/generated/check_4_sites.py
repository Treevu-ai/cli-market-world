#!/usr/bin/env python3
import urllib.request, json

SITES = [
    ("Glorisa", "https://glorisa.com.pe"),
    ("Gallo Mas Gallo", "https://www.elgallomasgallo.com.pe"),
    ("Carsa", "https://www.carsa.pe"),
    ("Tiendeo Callao", "https://www.tiendeo.pe/callao"),
]

PLATFORM_SIGS = {
    "VTEX": ["vtex", "vtexcommercestable", "vtexassets"],
    "Shopify": ["shopify", "myshopify", "cdn.shopify"],
    "WooCommerce": ["woocommerce", "wp-content/plugins/woocommerce", "wc-"],
    "Magento": ["magento", "mage/"],
    "PrestaShop": ["prestashop"],
    "Tiendanube": ["tiendanube", "nuvemshop"],
}

for label, url in SITES:
    print(f"\n{'='*60}")
    print(f">> {label}: {url}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read(40000).decode("utf-8", errors="ignore").lower()
        platform = "Custom"
        for p, sigs in PLATFORM_SIGS.items():
            if any(s in html for s in sigs):
                platform = p
                break
        title = html.split("<title>")[-1].split("</title>")[0][:100] if "<title>" in html else "N/A"
        has_cart = any(w in html for w in ["carrito", "cart", "add-to-cart", "comprar", "checkout"])
        print(f"   HTTP {resp.status} | Title: {title}")
        print(f"   Plataforma: {platform} | Carrito: {'SI' if has_cart else 'NO'}")
        
        if platform == "Shopify":
            for api_url in ["/products.json?limit=2", "/collections/all/products.json?limit=2"]:
                full = f"https://{url.split('://')[1].split('/')[0]}{api_url}"
                try:
                    r = urllib.request.urlopen(urllib.request.Request(full, headers={"User-Agent": "Mozilla/5.0"}), timeout=10)
                    data = json.loads(r.read().decode("utf-8"))
                    prods = data.get("products", [])
                    print(f"   API {api_url}: {len(prods)} productos")
                    for p in prods[:2]:
                        v = p.get("variants", [])
                        print(f"      - {p.get('title','?')[:60]}: S/ {v[0].get('price','?') if v else '?'}")
                    break
                except Exception as e:
                    print(f"   API fallo: {type(e).__name__}")
    except Exception as e:
        print(f"   ERROR: {type(e).__name__}: {str(e)[:120]}")

print(f"\n{'='*60}")
print("Listo.")
