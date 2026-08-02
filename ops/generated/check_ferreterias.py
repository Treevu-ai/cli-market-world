#!/usr/bin/env python3
"""Verificar plataformas de ferreterias nuevas para indexacion."""
import urllib.request, re

SITES = [
    ("Ferretec", "https://ferretec.pe"),
    ("Total Tools", "https://totaltools.pe"),
    ("Duque Ferreterias", "https://duqueferreterias.com"),
    ("MaqCenter", "https://maqcenterperu.com"),
]

PLATFORM_SIGS = {
    "VTEX": ["vtex", "vtexcommercestable", "vtexassets"],
    "WooCommerce": ["woocommerce", "wp-content/plugins/woocommerce"],
    "Shopify": ["shopify", "myshopify", "cdn.shopify"],
    "Magento": ["magento", "mage/"],
    "PrestaShop": ["prestashop"],
    "Tiendanube": ["tiendanube", "nuvemshop"],
    "Jumpseller": ["jumpseller"],
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
        
        has_jsonld = "application/ld+json" in html
        has_graphql = "graphql" in html
        has_rest = any(x in html for x in ["/api/", "wp-json", "rest-api", "wp/v2"])
        has_search = "search" in html or "buscar" in html or "busqueda" in html
        
        title = html.split("<title>")[-1].split("</title>")[0][:120] if "<title>" in html else "N/A"
        
        print(f"   HTTP {resp.status} | {len(html)} chars")
        print(f"   Plataforma: {platform}")
        print(f"   Title: {title}")
        print(f"   API/GraphQL: {has_graphql or has_rest} | Search form: {has_search} | JSON-LD: {has_jsonld}")
    except Exception as e:
        print(f"   ERROR: {e}")

print(f"\n{'='*60}")
print("Listo.")
