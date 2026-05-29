"""Parse pack sizes from product titles and normalize to price per base unit."""

from __future__ import annotations

import re

_NUM = r"(\d+(?:[.,]\d+)?)"


def _to_float(raw: str) -> float:
    return float(raw.replace(",", "."))


def parse_pack_size(name: str) -> tuple[float, str] | None:
    """Return (quantity, base_unit) where base_unit is kg, L, or unit."""
    if not name:
        return None
    text = name.lower()

    patterns: list[tuple[re.Pattern[str], str, float]] = [
        (re.compile(rf"{_NUM}\s*(?:kg|kilo|kilos|kilogramo?s?)\b", re.I), "kg", 1.0),
        (re.compile(rf"{_NUM}\s*g(?:ramos?)?\b", re.I), "kg", 0.001),
        (re.compile(rf"{_NUM}\s*(?:l|lt|lts|litro?s?)\b", re.I), "L", 1.0),
        (re.compile(rf"{_NUM}\s*ml\b", re.I), "L", 0.001),
        (re.compile(rf"{_NUM}\s*(?:un|und|uni|u\.?)\b", re.I), "unit", 1.0),
        (re.compile(rf"\bx\s*{_NUM}\b", re.I), "unit", 1.0),
        (re.compile(rf"{_NUM}\s*x\s*{_NUM}\s*(?:g|ml|kg|l)\b", re.I), "unit", 1.0),
    ]

    for pat, base, mult in patterns:
        m = pat.search(text)
        if m:
            qty = _to_float(m.group(1)) * mult
            if qty > 0:
                return qty, base
    return None


def price_per_base_unit(price: float, name: str) -> dict | None:
    parsed = parse_pack_size(name)
    if not parsed or price <= 0:
        return None
    qty, base = parsed
    return {
        "basis": base,
        "pack_qty": qty,
        "price_per": round(price / qty, 4),
    }


# Target ~1 kg / ~1 L (aceite often 900 ml).
_LIQUID_ITEMS = frozenset({"leche", "aceite"})
_WEIGHT_1KG_ITEMS = frozenset({"arroz", "azucar"})


def is_standard_canasta_pack(name: str, item: str) -> bool:
    """Keep canasta rows comparable: ~1 kg, ~1 L, or item-specific unit packs."""
    parsed = parse_pack_size(name)
    if not parsed:
        return False
    qty, base = parsed
    if item in _LIQUID_ITEMS:
        return base == "L" and 0.85 <= qty <= 1.05
    if item in _WEIGHT_1KG_ITEMS:
        return base == "kg" and 0.9 <= qty <= 1.15
    if item == "pan":
        return base == "kg" and 0.4 <= qty <= 1.15
    if item in ("cafe", "queso"):
        return base == "kg" and 0.2 <= qty <= 1.15
    if item == "pollo":
        return base == "kg" and 0.7 <= qty <= 2.5
    if item == "huevos":
        return base == "unit" and 6 <= qty <= 30
    if item == "jabon":
        return (base == "kg" and 0.07 <= qty <= 0.25) or (base == "unit" and qty <= 3)
    return False
