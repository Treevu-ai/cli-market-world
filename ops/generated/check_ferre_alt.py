#!/usr/bin/env python3
"""Verificar URLs alternativas de ferreterias."""
import urllib.request

SITES = [
    ("Total Tools www", "https://www.totaltools.pe"),
    ("Total Tools http", "http://totaltools.pe"),
    ("Total Tools (fb)", "https://www.facebook.com/totaltoolsperu"),
    ("Duque www", "https://www.duqueferreterias.com"),
    ("Duque http", "http://duqueferreterias.com"),
    ("MaqCenter www", "https://www.maqcenterperu.com"),
    ("MaqCenter http", "http://maqcenterperu.com"),
]

for label, url in SITES:
    print(f"\n>> {label}: {url}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=12)
        html = resp.read(8000).decode("utf-8", errors="ignore").lower()
        title = html.split("<title>")[-1].split("</title>")[0][:120] if "<title>" in html else "N/A"
        print(f"   HTTP {resp.status} | Title: {title}")
        
        # Quick platform check
        for sig, platform in [("vtex", "VTEX"), ("shopify", "Shopify"), ("woocommerce", "WooCommerce"), ("prestashop", "PrestaShop"), ("magento", "Magento"), ("tiendanube", "Tiendanube")]:
            if sig in html:
                print(f"   Plataforma: {platform}")
                break
    except Exception as e:
        print(f"   ERROR: {type(e).__name__}: {e}")

print("\nListo.")
