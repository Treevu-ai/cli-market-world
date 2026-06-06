#!/usr/bin/env python3
"""One-off landing doc patches (WooCommerce + Mercado Pago)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "landing" / "components"

# ScaleCoverageSection
p = ROOT / "ScaleCoverageSection.tsx"
t = p.read_text(encoding="utf-8")
if "platformWooCommerce" not in t:
    t = t.replace("sm:grid-cols-3 gap-3 mb-10", "sm:grid-cols-2 lg:grid-cols-4 gap-3 mb-10", 1)
    t = t.replace(
        '{ name: "Magento", count: MARKET_STATS.platformMagento, note: isES ? "departamentales" : "department stores" },\n          ].map((p) => (',
        '{ name: "Magento", count: MARKET_STATS.platformMagento, note: isES ? "departamentales" : "department stores" },\n'
        '            { name: "WooCommerce", count: MARKET_STATS.platformWooCommerce, note: isES ? "FMCG organico PE (piloto)" : "organic FMCG PE (pilot)" },\n'
        "          ].map((p) => (",
    )
    p.write_text(t, encoding="utf-8")
    print("patched ScaleCoverageSection")

# RetailersSection
p2 = ROOT / "RetailersSection.tsx"
t2 = p2.read_text(encoding="utf-8")
t2 = t2.replace("VTEX, Shopify o Magento", "VTEX, Shopify, Magento o WooCommerce")
t2 = t2.replace("VTEX, Shopify, or Magento", "VTEX, Shopify, Magento, or WooCommerce")
p2.write_text(t2, encoding="utf-8")
print("patched RetailersSection")

# FAQ
p3 = ROOT / "FAQ.tsx"
t3 = p3.read_text(encoding="utf-8")
t3 = t3.replace("3 plataformas:", f"{4} plataformas:")
t3 = t3.replace("3 platforms:", f"{4} platforms:")
t3 = t3.replace("(VTEX, Shopify, Magento)", "(VTEX, Shopify, Magento, WooCommerce)")
p3.write_text(t3, encoding="utf-8")
print("patched FAQ")

# UseCasesSection
p4 = ROOT / "UseCasesSection.tsx"
t4 = p4.read_text(encoding="utf-8")
t4 = t4.replace("PayPal/QR", "PayPal/Mercado Pago/QR")
p4.write_text(t4, encoding="utf-8")
print("patched UseCasesSection")