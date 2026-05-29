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
