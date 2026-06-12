"""AR canasta gate + Company LinkedIn price copy (spreads vs absolute ARS/PEN)."""

from __future__ import annotations

import re
from typing import Any

CANASTA_ITEMS = ("queso", "pan", "aceite")
ACTUALIZAR_MARKER_RE = re.compile(
    r"\[ACTUALIZAR:\s*si hay ≥ 2 cadenas AR con ≥ 6/10 ítems comparables, "
    r"reemplazar spreads con precios absolutos en ARS y PEN respectivamente\. "
    r"Nunca convertir a USD en el cuerpo del post\.\]\s*\n?",
    re.IGNORECASE,
)
SPREAD_BLOCK_RE = re.compile(
    r"Esta semana, el collector registró los siguientes spreads entre mercados[^\n]*:\n\n"
    r"(?:— [^\n]+\n)+",
    re.IGNORECASE,
)


def is_ar_store(store_name: str) -> bool:
    """True for Argentina retailers (e.g. Vea AR), not Carrefour BR."""
    low = f" {(store_name or '').strip().lower()} "
    return " ar " in low or low.endswith(" ar ")


def ar_gate_report(canasta: list[dict[str, Any]], *, min_items: int = 6) -> dict[str, Any]:
    qualifying: list[dict[str, Any]] = []
    for row in canasta:
        if not is_ar_store(row.get("store_name") or ""):
            continue
        items = int(row.get("items") or 0)
        qualifying.append(
            {
                "store_name": row.get("store_name"),
                "items": items,
                "total": row.get("total"),
                "currency": row.get("currency"),
                "passes": items >= min_items,
            }
        )
    passed = [r for r in qualifying if r["passes"]]
    return {
        "min_items": min_items,
        "qualifying_count": len(passed),
        "gate_pass": len(passed) >= 2,
        "stores": qualifying,
        "passed_stores": passed,
    }


def _spread_rows(data: dict[str, Any]) -> dict[tuple[str, str], dict[str, Any]]:
    out: dict[tuple[str, str], dict[str, Any]] = {}
    for row in data.get("canasta_spreads") or []:
        item = (row.get("item") or row.get("seed") or "").lower()
        currency = (row.get("currency") or "").upper()
        if item and currency:
            out[(item, currency)] = row
    for row in data.get("marketing_spreads") or []:
        item = (row.get("seed") or row.get("item") or "").lower()
        currency = (row.get("currency") or "").upper()
        if item and currency and (item, currency) not in out:
            out[(item, currency)] = row
    return out


def _fmt_price(value: float, currency: str, basis: str) -> str:
    unit = "/kg" if basis == "per_kg" else "/L" if basis == "per_L" else ""
    if currency == "ARS":
        return f"ARS {value:,.0f}{unit}"
    if currency == "PEN":
        return f"PEN {value:.2f}{unit}"
    return f"{currency} {value:,.2f}{unit}"


def _item_label(item: str) -> str:
    return item.capitalize()


def _basis_unit(basis: str) -> str:
    if basis == "per_L":
        return "litro"
    if basis == "per_kg":
        return "kilo"
    return "unidad"


def build_canasta_price_block(data: dict[str, Any], *, min_items: int = 6) -> tuple[str, dict[str, Any]]:
    """Return markdown block + gate metadata for Company Day PE vs AR posts."""
    canasta = data.get("canasta_basica") or []
    gate = ar_gate_report(canasta, min_items=min_items)
    spreads = _spread_rows(data)

    lines: list[str] = []
    if gate["gate_pass"]:
        lines.append(
            "Esta semana, el collector registró estos precios de referencia "
            "en moneda local (normalizados por kilo o litro):"
        )
        lines.append("")
        for item in CANASTA_ITEMS:
            ars = spreads.get((item, "ARS")) or {}
            pen = spreads.get((item, "PEN")) or {}
            ars_price = float(ars.get("avg_price") or 0)
            pen_price = float(pen.get("avg_price") or 0)
            ars_basis = ars.get("price_basis") or "per_kg"
            pen_basis = pen.get("price_basis") or ars_basis
            if ars_price <= 0 or pen_price <= 0:
                continue
            lines.append(
                f"— {_item_label(item)}: {_fmt_price(ars_price, 'ARS', ars_basis)} (AR) · "
                f"{_fmt_price(pen_price, 'PEN', pen_basis)} (PE)"
            )
        mode = "absolute"
    else:
        lines.append(
            "Esta semana, el collector registró los siguientes spreads entre mercados "
            "para ítems de canasta básica:"
        )
        lines.append("")
        defaults = {"queso": 2.93, "pan": 2.75, "aceite": 2.65}
        for item in CANASTA_ITEMS:
            ars = spreads.get((item, "ARS")) or {}
            ratio = float(ars.get("spread_ratio") or defaults.get(item) or 0)
            basis = _basis_unit(ars.get("price_basis") or "per_kg")
            if ratio <= 0:
                continue
            lines.append(
                f"— {_item_label(item)}: {ratio:.2f}x entre el precio por {basis} en AR (ARS) y PE (PEN)"
            )
        mode = "spread"

    return "\n".join(lines) + "\n", {**gate, "mode": mode}


def resolve_company_price_marker(text: str, data: dict[str, Any], *, min_items: int = 6) -> str:
    """Replace [ACTUALIZAR] + spread block with live absolute or spread copy."""
    if not ACTUALIZAR_MARKER_RE.search(text):
        return text
    block, _meta = build_canasta_price_block(data, min_items=min_items)
    out = ACTUALIZAR_MARKER_RE.sub("", text)
    if SPREAD_BLOCK_RE.search(out):
        out = SPREAD_BLOCK_RE.sub(block, out, count=1)
    else:
        out = out.replace(
            "[ACTUALIZAR: si hay ≥ 2 cadenas AR con ≥ 6/10 ítems comparables, "
            "reemplazar spreads con precios absolutos en ARS y PEN respectivamente. "
            "Nunca convertir a USD en el cuerpo del post.]",
            block.strip(),
        )
    return out
