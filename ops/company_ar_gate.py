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


# ── Commodity spread marker resolution (Company-Day-16, 20, 21, 24) ──────────


def _get_spread_for(seed: str, currency: str, data: dict[str, Any]) -> dict[str, Any] | None:
    """Return the first matching spread row for seed+currency from dashboard data."""
    for row in (data.get("canasta_spreads") or []) + (data.get("marketing_spreads") or []):
        item = (row.get("item") or row.get("seed") or "").lower()
        cur = (row.get("currency") or "").upper()
        if seed.lower() in item and cur == currency.upper():
            return row
    return None


def _build_aceite_spread_lines(data: dict[str, Any]) -> list[str]:
    """Build aceite AR spread lines for Company-Day-16."""
    row = _get_spread_for("aceite", "ARS", data)
    if not row:
        return []
    avg = float(row.get("avg_price") or 0)
    lo = float(row.get("min_price") or row.get("price_min") or 0)
    hi = float(row.get("max_price") or row.get("price_max") or 0)
    spread = float(row.get("spread_ratio") or (hi / lo if lo else 0))
    basis = row.get("price_basis") or "per_L"
    unit = _basis_unit(basis)
    lines = []
    if lo and hi:
        lines.append(
            f"Esta semana, el precio del aceite vegetal por {unit} en Argentina "
            f"varió entre ARS {lo:,.0f} y ARS {hi:,.0f} entre las principales cadenas "
            f"— un spread de {(hi - lo) / lo * 100:.0f}% sobre el mínimo."
        )
    elif avg and spread:
        lines.append(
            f"Esta semana, el spread de aceite vegetal en Argentina "
            f"alcanzó {spread:.2f}x entre las principales cadenas "
            f"(precio promedio por {unit}: ARS {avg:,.0f})."
        )
    return lines


def _build_leche_pe_ar_lines(data: dict[str, Any]) -> list[str]:
    """Build leche PE vs AR comparison lines for Company-Day-20."""
    row_ars = _get_spread_for("leche", "ARS", data)
    row_pen = _get_spread_for("leche", "PEN", data)
    lines = []
    if row_pen:
        lo = float(row_pen.get("min_price") or row_pen.get("price_min") or 0)
        hi = float(row_pen.get("max_price") or row_pen.get("price_max") or 0)
        if lo and hi:
            lines.append(
                f"En Perú, el precio por litro de leche entera se mueve en un rango "
                f"de S/ {lo:.2f} a S/ {hi:.2f} entre las principales cadenas."
            )
    if row_ars:
        lo = float(row_ars.get("min_price") or row_ars.get("price_min") or 0)
        hi = float(row_ars.get("max_price") or row_ars.get("price_max") or 0)
        if lo and hi:
            lines.append(
                f"En Argentina, el mismo producto muestra un rango "
                f"de ARS {lo:,.0f} a ARS {hi:,.0f} por litro."
            )
    return lines


def _build_top_spreads_lines(data: dict[str, Any]) -> list[str]:
    """Build top-3 spread products block for Company-Day-21."""
    rows = (data.get("top_discounts") or data.get("marketing_spreads") or [])
    if not rows:
        return []
    top = sorted(rows, key=lambda r: float(r.get("spread_ratio") or r.get("discount_pct") or 0), reverse=True)[:3]
    lines = []
    for i, row in enumerate(top, 1):
        seed = (row.get("seed") or row.get("item") or row.get("name") or "Producto").capitalize()
        cur = (row.get("currency") or "ARS").upper()
        lo = float(row.get("min_price") or row.get("price_min") or 0)
        hi = float(row.get("max_price") or row.get("price_max") or 0)
        spread = float(row.get("spread_ratio") or (hi / lo if lo else 0))
        country = "AR" if cur == "ARS" else ("PE" if cur == "PEN" else cur)
        basis = _basis_unit(row.get("price_basis") or "per_kg")
        line = f"**{i}. {seed} — {country}**"
        lines.append(line)
        if lo and hi:
            lines.append(f"Rango: {cur} {lo:,.0f} – {cur} {hi:,.0f} por {basis}. Spread: {(hi - lo) / lo * 100:.0f}%.")
        elif spread:
            lines.append(f"Spread: {spread:.2f}x entre las principales cadenas.")
    return lines


# Marker patterns for the new commodity posts
_ACEITE_SPREAD_RE = re.compile(
    r"\[ACTUALIZAR:\s*reemplazar con spread vigente de aceite[^\]]*\]\n?",
    re.IGNORECASE,
)
_ACEITE_RANGE_RE = re.compile(
    r"\[ACTUALIZAR:\s*insertar rango de precios por litro[^\]]*\]\n?",
    re.IGNORECASE,
)
_LECHE_RANGE_RE = re.compile(
    r"\[ACTUALIZAR:\s*insertar precio por litro en PE[^\]]*\]\n?",
    re.IGNORECASE,
)
_LECHE_PLACEHOLDER_PEN_RE = re.compile(r"S/\s*\[X\]\s*a\s*S/\s*\[Y\]")
_LECHE_PLACEHOLDER_ARS_RE = re.compile(r"ARS\s*\[A\]\s*a\s*ARS\s*\[B\]")
_TOP3_BLOCK_RE = re.compile(
    r"\[ACTUALIZAR:\s*insertar top 3 productos[^\]]*\]\n?",
    re.IGNORECASE,
)
_REPLACE_ALL_RE = re.compile(
    r"\[ACTUALIZAR:\s*reemplazar todos los placeholders[^\]]*\]\n?",
    re.IGNORECASE,
)


def resolve_commodity_spread_markers(text: str, data: dict[str, Any]) -> str:
    """Resolve Company-Day-16/20/21 commodity spread markers using dashboard data."""
    out = text

    # Company-Day-16: aceite AR spread
    aceite_lines = _build_aceite_spread_lines(data)
    if aceite_lines:
        replacement = "\n".join(aceite_lines) + "\n"
        out = _ACEITE_SPREAD_RE.sub(replacement, out)
        out = _ACEITE_RANGE_RE.sub("", out)
    else:
        out = _ACEITE_SPREAD_RE.sub("", out)
        out = _ACEITE_RANGE_RE.sub("", out)

    # Company-Day-20: leche PE vs AR
    leche_lines = _build_leche_pe_ar_lines(data)
    out = _LECHE_RANGE_RE.sub("", out)
    if leche_lines:
        row_pen = _get_spread_for("leche", "PEN", data)
        row_ars = _get_spread_for("leche", "ARS", data)
        if row_pen:
            lo = float(row_pen.get("min_price") or row_pen.get("price_min") or 0)
            hi = float(row_pen.get("max_price") or row_pen.get("price_max") or 0)
            if lo and hi:
                out = _LECHE_PLACEHOLDER_PEN_RE.sub(f"S/ {lo:.2f} a S/ {hi:.2f}", out)
        if row_ars:
            lo = float(row_ars.get("min_price") or row_ars.get("price_min") or 0)
            hi = float(row_ars.get("max_price") or row_ars.get("price_max") or 0)
            if lo and hi:
                out = _LECHE_PLACEHOLDER_ARS_RE.sub(f"ARS {lo:,.0f} a ARS {hi:,.0f}", out)

    # Company-Day-21: top 3 products
    top3_lines = _build_top_spreads_lines(data)
    if top3_lines:
        replacement = "\n".join(top3_lines) + "\n"
        out = _TOP3_BLOCK_RE.sub(replacement, out)
    else:
        out = _TOP3_BLOCK_RE.sub("", out)

    # Strip "replace all placeholders" cleanup instruction markers
    out = _REPLACE_ALL_RE.sub("", out)

    return out
