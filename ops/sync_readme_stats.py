#!/usr/bin/env python3
"""Refresh README.md hero stats from market_stats."""
from pathlib import Path
import re
import sys

CORE = Path(__file__).resolve().parent.parent.parent / "cli-market-core"
sys.path.insert(0, str(CORE))
from market_core import market_stats as s

_prices = getattr(s, "PRICES_VERIFIED", None)
if _prices is None:
    import re as _re
    m = _re.search(r"([\d,]+)", s.PRICES_VERIFIED_LABEL)
    _prices = int(m.group(1).replace(",", "")) if m else 45000

readme = Path(__file__).resolve().parent.parent / "README.md"
text = readme.read_text(encoding="utf-8")

replacements = [
    (r"\*\*66 retailers \(36 verificados activos\)\*\*", f"**{s.RETAILERS_DEFINED} retailers ({s.RETAILERS_VERIFIED} verificados activos)**"),
    (r"66 retailers \(36 verificados activos\)", f"{s.RETAILERS_DEFINED} retailers ({s.RETAILERS_VERIFIED} verificados activos)"),
    (r"3 plataformas", f"{s.PLATFORMS} plataformas"),
    (r"PayPal \+ QR \(Yape / Plin\)", s.PAYMENTS_LABEL.replace("·", "+").replace("  ", " ")),
    (r"Pago con PayPal \+ QR \(Yape / Plin\)", f"Pago con {s.PAYMENTS_LABEL}"),
    (r"Más de 46,000\+ precios", f"Más de {_prices:,}+ precios"),
    (r"45,000\+ verified shelf prices", s.PRICES_VERIFIED_LABEL),
    (r"66 retailers, 45,000\+ shelf prices", f"{s.RETAILERS_DEFINED} retailers, {_prices:,}+ shelf prices"),
]
for pat, repl in replacements:
    text = re.sub(pat, repl, text)

readme.write_text(text, encoding="utf-8")
print(f"Updated {readme}")