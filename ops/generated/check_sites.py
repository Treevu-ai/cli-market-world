#!/usr/bin/env python3
"""Verificar sitios web de marcas no encontradas en CLI Market."""
import urllib.request

SITES = [
    ("Anypsa", "https://www.anypsa.com.pe"),
    ("Anypsa alt", "https://anypsa.com.pe"),
    ("Anypsa tienda", "https://tienda.anypsa.com.pe"),
    ("CPP", "https://cpp.com.pe"),
    ("CPP alt", "https://www.cpp.com.pe"),
    ("CPP quimica", "https://www.cppquimica.com"),
    ("Henci", "https://www.henci.com.pe"),
    ("Henci alt", "https://henci.com.pe"),
    ("Oatey Peru", "https://www.oatey.com.pe"),
    ("Pavco Peru", "https://pavco.com.pe"),
    ("Pegatanke", "https://pegatanke.com.pe"),
    ("Tekno adhesivos", "https://www.tekno.com.pe"),
    ("Vencedor", "https://www.vencedor.com.pe"),
    ("Vencedor tienda", "https://tienda.vencedor.com.pe"),
    ("Pavco Wavin", "https://pavcowavin.com.pe"),
    ("Promart (base)", "https://www.promart.pe"),
    ("Sodimac (base)", "https://www.sodimac.com.pe"),
    ("Maestro (base)", "https://www.maestro.com.pe"),
]

def check_site(label, url):
    print(f"\n>> {label}: {url}")
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=10)
        content = resp.read(8192).decode("utf-8", errors="ignore").lower()
        has_cart = any(w in content for w in ["carrito", "cart", "comprar", "add-to-cart", "ecommerce", "tienda", "shop", "precio"])
        print(f"   HTTP {resp.status} | {len(content)} chars | Carrito: {'SI' if has_cart else 'NO'}")
        if "<title>" in content:
            t = content.split("<title>")[-1].split("</title>")[0][:100]
            print(f"   Title: {t}")
    except Exception as e:
        print(f"   ERROR: {e}")

for label, url in SITES:
    check_site(label, url)

print("\nListo.")
