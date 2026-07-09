#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CLI Market — Brand Intelligence Monthly Report Generator.

Genera el reporte PDF mensual de 8 páginas para un cliente de Brand Intelligence.
Estructura según PRD (docs/prd-brand-intelligence-v1.md §3 SKU B):

  Pág 1  Portada + resumen ejecutivo (3 bullets)
  Pág 2  Mis SKUs: precios por cadena + desvío vs PVP, semáforo
  Pág 3  Mapa de competidores: precio relativo, ranking en categoría
  Pág 4  Promo tracker: activaciones del mes, duración, cadena
  Pág 5  Price dispersion: mi marca vs industria
  Pág 6  Top movers de la categoría (mayor variación de precio)
  Pág 7  Contexto macro (RPV de la línea, BSI, presión de canasta)
  Pág 8  Recomendaciones de acción (3 bullets)

Uso:
  python3 ops/brand_report.py --brand Gloria --country PE --out /tmp/gloria-brand-report.pdf
  python3 ops/brand_report.py --brand demo   --demo        # Datos sintéticos para piloto
  python3 ops/brand_report.py --brand Gloria --month 2026-06
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Load project .env (overrides any stale system env vars like a Windsurf/Cursor token)
_env_file = Path(__file__).resolve().parent.parent / ".env"
if _env_file.exists():
    for _line in _env_file.read_text(encoding="utf-8").splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ[_k.strip()] = _v.strip().strip('"').strip("'")

import httpx
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

# ── Paleta ────────────────────────────────────────────────────────────────────
VERDE   = colors.HexColor("#00C896")
VERDE_D = colors.HexColor("#00906E")
NEGRO   = colors.HexColor("#0D0D0D")
CARBON  = colors.HexColor("#1A1A2E")
GRIS_M  = colors.HexColor("#4A5568")
GRIS_L  = colors.HexColor("#F7FAFC")
GRIS_B  = colors.HexColor("#E2E8F0")
BLANCO  = colors.white
ROJO    = colors.HexColor("#E53E3E")
ROJO_L  = colors.HexColor("#FED7D7")
AMARILLO= colors.HexColor("#F6E05E")
AMAR_L  = colors.HexColor("#FFFFF0")

W, H = A4  # 595 × 842 pts

# ── Estilos ───────────────────────────────────────────────────────────────────
def ps(name: str, **kw) -> ParagraphStyle:
    return ParagraphStyle(name, **kw)

BRAND   = ps("brand",  fontName="Helvetica-Bold",   fontSize=28, textColor=VERDE,  leading=34)
TAGLINE = ps("tagline",fontName="Helvetica",         fontSize=11, textColor=GRIS_M, leading=15)
H1      = ps("H1",     fontName="Helvetica-Bold",   fontSize=20, textColor=NEGRO,  leading=24, spaceAfter=4)
H1W     = ps("H1W",    fontName="Helvetica-Bold",   fontSize=18, textColor=BLANCO, leading=22, spaceAfter=4)
H2      = ps("H2",     fontName="Helvetica-Bold",   fontSize=14, textColor=VERDE_D,leading=18, spaceAfter=3)
H2W     = ps("H2W",    fontName="Helvetica-Bold",   fontSize=13, textColor=VERDE,  leading=17, spaceAfter=3)
H3      = ps("H3",     fontName="Helvetica-Bold",   fontSize=10, textColor=NEGRO,  leading=13, spaceAfter=2)
BODY    = ps("BODY",   fontName="Helvetica",         fontSize=9,  textColor=GRIS_M, leading=13, spaceAfter=4)
BODYB   = ps("BODYB",  fontName="Helvetica-Bold",   fontSize=9,  textColor=NEGRO,  leading=13, spaceAfter=4)
BODYW   = ps("BODYW",  fontName="Helvetica",         fontSize=9,  textColor=BLANCO, leading=13, spaceAfter=4)
SMALL   = ps("SMALL",  fontName="Helvetica",         fontSize=7.5,textColor=GRIS_M, leading=11)
NOTE    = ps("NOTE",   fontName="Helvetica-Oblique", fontSize=7.5,textColor=GRIS_M, leading=11)
SECLBL  = ps("SECLBL", fontName="Helvetica-Bold",   fontSize=8,  textColor=GRIS_M, leading=10, spaceAfter=2)
BIG     = ps("BIG",    fontName="Helvetica-Bold",   fontSize=24, textColor=NEGRO,  leading=28)
BIGV    = ps("BIGV",   fontName="Helvetica-Bold",   fontSize=24, textColor=VERDE,  leading=28)
BULLET  = ps("BULLET", fontName="Helvetica",         fontSize=9.5,textColor=NEGRO,  leading=14, spaceAfter=5,
             leftIndent=10, bulletIndent=0, bulletFontName="Helvetica-Bold", bulletFontSize=9.5)
CONF    = ps("CONF",   fontName="Helvetica",         fontSize=7.5,textColor=GRIS_M, leading=10)
LABEL   = ps("LABEL",  fontName="Helvetica-Bold",   fontSize=7,  textColor=VERDE,  leading=9)
CAPTION = ps("CAPTION",fontName="Helvetica-BoldOblique",fontSize=8,textColor=VERDE_D,leading=12)


def sp(h: float = 6) -> Spacer:
    return Spacer(1, h)


def hr(c: Any = VERDE, t: float = 1.0) -> HRFlowable:
    return HRFlowable(width="100%", thickness=t, color=c, spaceAfter=4, spaceBefore=2)


def section_header(label: str, title: str) -> KeepTogether:
    return KeepTogether([
        Paragraph(label, SECLBL),
        Paragraph(title, H2),
        hr(),
        sp(4),
    ])


def kpi_bar(items: list[tuple[str, str]], bg: Any = CARBON) -> Table:
    """items = list of (value, label)"""
    n = len(items)
    cw = (W - 30 * mm) / n
    cells = []
    for val, lbl in items:
        txt = (
            f"<font name='Helvetica-Bold' size='16' color='#00C896'>{val}</font><br/>"
            f"<font name='Helvetica' size='7' color='#A0AEC0'>{lbl}</font>"
        )
        cells.append(Paragraph(txt, ps("kpi_cell", fontName="Helvetica", fontSize=9,
                                       textColor=BLANCO, leading=20, alignment=TA_CENTER)))
    t = Table([cells], colWidths=[cw] * n, rowHeights=[30])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
    ]))
    return t


# ── Semáforo de desvío ────────────────────────────────────────────────────────
def desvio_badge(precio: float, pvp: float | None) -> tuple[str, Any]:
    """Devuelve (texto, color_fondo) según desvío vs PVP sugerido."""
    if pvp is None or pvp == 0:
        return "—", GRIS_B
    ratio = precio / pvp
    if ratio > 1.05:
        pct = (ratio - 1) * 100
        return f"+{pct:.0f}%", ROJO_L
    if ratio < 0.85:
        pct = (1 - ratio) * 100
        return f"-{pct:.0f}%", AMAR_L
    return "✓", colors.HexColor("#C6F6D5")


# ── Data layer ────────────────────────────────────────────────────────────────
# Read lazily (after .env is loaded) via helper
def _api_base() -> str:
    return os.getenv("MARKET_API_URL", "https://cli-market-api.fly.dev").rstrip("/")

def _api_key() -> str:
    return os.getenv("MARKET_API_TOKEN", "")

PE_STORES = ["wong", "metro", "plazavea", "mimercado_delivery"]
STORE_LABELS = {
    "wong": "Wong", "metro": "Metro", "plazavea": "Plaza Vea",
    "mimercado_delivery": "Mi Mercado", "promart": "Promart",
    "sodimac_pe": "Sodimac", "ripley_pe": "Ripley", "falabella_pe": "Falabella",
}


def fetch_brand_data(brand: str, country: str = "PE", days: int = 30,
                     competitors: list[str] | None = None) -> dict:
    """Consulta /v1/brand-monitor para obtener datos reales."""
    params: dict[str, Any] = {"brand": brand, "country": country, "days": days}
    if competitors:
        params["competitors"] = ",".join(competitors)
    key = _api_key()
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    url = f"{_api_base()}/v1/brand-monitor"
    r = httpx.get(url, params=params, headers=headers, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"brand-monitor API error {r.status_code}: {r.text[:300]}")
    return r.json()


def fetch_dashboard(country: str = "PE") -> dict:
    """Consulta /dashboard/data para contexto macro."""
    key = _api_key()
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    url = f"{_api_base()}/dashboard/data"
    try:
        r = httpx.get(url, params={"country": country}, headers=headers, timeout=20)
        if r.status_code < 400:
            return r.json()
    except Exception:
        pass
    return {}


def demo_data(brand: str = "Gloria") -> dict:
    """Datos sintéticos para demo / piloto sin API key."""
    now_str = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return {
        "brand": brand,
        "period_days": 30,
        "my_skus": [
            {"name": f"{brand} Leche Evaporada 400ml", "store": "plazavea", "price": 3.50,
             "list_price": 3.50, "discount": 0, "queried_at": now_str, "pvp_suggested": 3.60},
            {"name": f"{brand} Leche Evaporada 400ml", "store": "metro",    "price": 3.70,
             "list_price": 3.90, "discount": 5, "queried_at": now_str, "pvp_suggested": 3.60},
            {"name": f"{brand} Leche Evaporada 400ml", "store": "wong",     "price": 3.80,
             "list_price": 3.80, "discount": 0, "queried_at": now_str, "pvp_suggested": 3.60},
            {"name": f"{brand} Leche UHT 1L",           "store": "plazavea", "price": 4.90,
             "list_price": 4.90, "discount": 0, "queried_at": now_str, "pvp_suggested": 5.00},
            {"name": f"{brand} Leche UHT 1L",           "store": "metro",    "price": 4.70,
             "list_price": 5.20, "discount": 10,"queried_at": now_str, "pvp_suggested": 5.00},
            {"name": f"{brand} Queso Fresco 200g",       "store": "plazavea", "price": 6.50,
             "list_price": 6.50, "discount": 0, "queried_at": now_str, "pvp_suggested": 6.50},
            {"name": f"{brand} Queso Fresco 200g",       "store": "wong",     "price": 7.10,
             "list_price": 7.10, "discount": 0, "queried_at": now_str, "pvp_suggested": 6.50},
        ],
        "competitor_skus": [
            {"name": "Laive Leche Evaporada 400ml",  "brand": "Laive",  "store": "plazavea", "price": 3.30,
             "list_price": 3.30, "discount": 0, "queried_at": now_str},
            {"name": "Laive Leche Evaporada 400ml",  "brand": "Laive",  "store": "metro",    "price": 3.45,
             "list_price": 3.60, "discount": 4, "queried_at": now_str},
            {"name": "Nestlé Leche Evaporada 400ml","brand": "Nestlé", "store": "plazavea", "price": 3.55,
             "list_price": 3.55, "discount": 0, "queried_at": now_str},
            {"name": "Nestlé Leche Evaporada 400ml","brand": "Nestlé", "store": "metro",    "price": 3.60,
             "list_price": 3.80, "discount": 5, "queried_at": now_str},
            {"name": "Laive Leche UHT 1L",           "brand": "Laive",  "store": "plazavea", "price": 4.50,
             "list_price": 4.50, "discount": 0, "queried_at": now_str},
            {"name": "Nestlé Nido UHT 1L",           "brand": "Nestlé", "store": "plazavea", "price": 5.20,
             "list_price": 5.20, "discount": 0, "queried_at": now_str},
        ],
        "promo_events": [
            {"name": f"{brand} Leche Evaporada 400ml", "store": "metro",    "discount": 5,
             "start": "2026-06-10", "end": "2026-06-17", "duration_days": 7},
            {"name": f"{brand} Leche UHT 1L",           "store": "metro",    "discount": 10,
             "start": "2026-06-18", "end": "2026-06-30", "duration_days": 13},
            {"name": "Laive Leche Evaporada 400ml",     "store": "metro",    "discount": 4,
             "start": "2026-06-05", "end": "2026-06-12", "duration_days": 8},
            {"name": "Laive Leche Evaporada 400ml",     "store": "plazavea", "discount": 6,
             "start": "2026-06-20", "end": "2026-06-30", "duration_days": 11},
            {"name": "Nestlé Leche Evaporada 400ml",   "store": "metro",    "discount": 5,
             "start": "2026-06-14", "end": "2026-06-21", "duration_days": 8},
        ],
        "dispersion_score": 0.048,
        "industry_dispersion": 0.062,
        "category_rank": 2,
        "category_total_brands": 4,
        "top_movers": [
            {"name": "Laive Leche Evaporada 400ml", "brand": "Laive",  "change_pct": -4.2, "store": "plazavea"},
            {"name": f"{brand} Leche UHT 1L",       "brand": brand,    "change_pct": -6.5, "store": "metro"},
            {"name": "Nestlé Nido UHT 1L",          "brand": "Nestlé", "change_pct": +2.1, "store": "plazavea"},
            {"name": f"{brand} Queso Fresco 200g",  "brand": brand,    "change_pct": +8.3, "store": "wong"},
            {"name": "Laive Leche UHT 1L",          "brand": "Laive",  "change_pct": -3.0, "store": "plazavea"},
        ],
        "macro": {
            "rpv_supermercados": 1.034,
            "promo_intensity_pct": 18.2,
            "canasta_basica_index": 112.4,
            "inflation_mom_pct": 0.41,
        },
    }


# ── Páginas ───────────────────────────────────────────────────────────────────

def page_portada(brand: str, month_label: str, data: dict) -> list:
    """Página 1 — Portada + resumen ejecutivo."""
    my_skus      = data.get("my_skus", [])
    comp_skus    = data.get("competitor_skus", [])
    promo_events = data.get("promo_events", [])
    macro        = data.get("macro", {})

    # Bullets ejecutivos
    n_alertas  = sum(1 for s in my_skus if desvio_badge(s["price"], s.get("pvp_suggested"))[0] not in ("✓", "—"))
    n_promos   = len([e for e in promo_events if e.get("store") in PE_STORES])
    comp_promos = len([e for e in promo_events if e.get("name", "").split()[0] != brand.split()[0]])
    rpv        = macro.get("rpv_supermercados", 1.0)
    rpmov      = f"{'subió' if rpv > 1 else 'bajó'} {abs(rpv-1)*100:.1f}%"

    content: list = []
    # Fondo oscuro: bloque portada
    cover_bg = Table(
        [[Paragraph("CLI MARKET", BRAND)]],
        colWidths=[W - 30*mm], rowHeights=[35]
    )
    cover_bg.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), CARBON),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("LEFTPADDING",   (0,0), (-1,-1), 12),
    ]))
    content.append(cover_bg)
    content.append(sp(4))
    content.append(Paragraph("Brand Intelligence", H1W if False else H1))
    content.append(Paragraph(
        f"Reporte mensual · <b>{brand}</b> · {month_label}",
        TAGLINE
    ))
    content.append(sp(2))
    content.append(Paragraph(
        "Confidencial · Uso exclusivo del equipo de Trade Marketing / Pricing",
        CONF
    ))
    content.append(sp(14))
    content.append(hr())
    content.append(section_header("01", "Resumen Ejecutivo"))

    bullets = [
        (f"{n_alertas} SKU{'s' if n_alertas!=1 else ''} con desvío vs PVP sugerido — "
         f"{'acción requerida' if n_alertas>0 else 'todo en rango'}.",),
        (f"{n_promos} activación{'es' if n_promos!=1 else ''} promocional{'es' if n_promos!=1 else ''} "
         f"de {brand} en el mes ({comp_promos} de competidores).",),
        (f"Precio relativo de canasta supermercados {rpmov} en el período. "
         f"Promo intensity sectorial: {macro.get('promo_intensity_pct',0):.1f}%.",),
    ]
    for (txt,) in bullets:
        content.append(Paragraph(f"• {txt}", BULLET))

    content.append(sp(14))
    content.append(kpi_bar([
        (str(len(set(s["name"] for s in my_skus))), "SKUs propios"),
        (str(len(set(s["store"] for s in my_skus))), "Cadenas"),
        (str(len(set(s.get("brand") for s in comp_skus))), "Marcas competidoras"),
        (str(n_promos), "Promos activas"),
        (f"#{data.get('category_rank','—')}", "Rank en categoría"),
    ]))
    content.append(sp(10))
    content.append(Paragraph(
        f"Período: {data.get('period_days', 30)} días · Fuente: CLI Market price_snapshots "
        f"(+50K precios, refresh 8h, 41 retailers verificados VTEX)",
        NOTE
    ))
    content.append(PageBreak())
    return content


def page_mis_skus(brand: str, data: dict) -> list:
    """Página 2 — Mis SKUs: precios por cadena + semáforo de desvío."""
    my_skus = data.get("my_skus", [])
    content: list = [section_header("02", f"Mis SKUs — {brand}")]

    content.append(Paragraph(
        "Precio actual vs PVP sugerido por cadena. "
        "<font color='#E53E3E'>Rojo</font>: precio &gt;5% sobre PVP (problema de imagen). "
        "<font color='#D69E2E'>Amarillo</font>: precio &lt;15% bajo PVP (presión de margen). "
        "<font color='#276749'>Verde</font>: en rango.",
        BODY
    ))
    content.append(sp(6))

    if not my_skus:
        content.append(Paragraph("Sin datos de SKUs propios para este período.", BODY))
        content.append(PageBreak())
        return content

    headers = ["Producto", "Cadena", "Precio actual", "PVP sugerido", "Desvío", "Promo"]
    col_w   = [(W - 30*mm) * r for r in [0.34, 0.14, 0.12, 0.12, 0.10, 0.18]]
    rows    = [[Paragraph(h, BODYB) for h in headers]]
    style   = [
        ("BACKGROUND", (0,0), (-1,0), CARBON),
        ("TEXTCOLOR",  (0,0), (-1,0), BLANCO),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [GRIS_L, BLANCO]),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("GRID",       (0,0), (-1,-1), 0.3, GRIS_B),
    ]

    for i, s in enumerate(my_skus, 1):
        name    = s.get("name", "—")
        store   = STORE_LABELS.get(s.get("store", ""), s.get("store", "—"))
        price   = s.get("price", 0.0)
        pvp     = s.get("pvp_suggested")
        disc    = s.get("discount", 0)
        badge, badge_bg = desvio_badge(price, pvp)
        pvp_txt = f"S/ {pvp:.2f}" if pvp else "—"
        promo_txt = f"{disc:.0f}% OFF" if disc and disc > 0 else "—"

        row = [
            Paragraph(name, BODY),
            Paragraph(store, BODY),
            Paragraph(f"S/ {price:.2f}", BODY),
            Paragraph(pvp_txt, BODY),
            Paragraph(badge, BODYB),
            Paragraph(promo_txt, BODY),
        ]
        rows.append(row)
        style.append(("BACKGROUND", (4, i), (4, i), badge_bg))

    t = Table(rows, colWidths=col_w)
    t.setStyle(TableStyle(style))
    content.append(t)
    content.append(sp(8))
    content.append(Paragraph(
        "PVP sugerido: ingresado en onboarding por la marca. Precio actual: última observación disponible en CLI Market.",
        NOTE
    ))
    content.append(PageBreak())
    return content


def page_competidores(brand: str, data: dict) -> list:
    """Página 3 — Mapa de competidores: precio relativo + ranking."""
    comp_skus = data.get("competitor_skus", [])
    my_skus   = data.get("my_skus", [])
    content: list = [section_header("03", "Mapa de Competidores")]

    content.append(Paragraph(
        "Precio relativo = precio_mío / precio_competidor. "
        "Ratio &gt;1 significa que eres más caro en esa cadena para ese SKU comparable.",
        BODY
    ))
    content.append(sp(6))

    # Construir comparación: por cadena, precio medio de mi marca vs competidores
    my_by_store: dict[str, list[float]] = {}
    for s in my_skus:
        store = s.get("store", "")
        my_by_store.setdefault(store, []).append(s.get("price", 0.0))

    comp_by_brand_store: dict[tuple[str,str], list[float]] = {}
    for s in comp_skus:
        key = (s.get("brand", "?"), s.get("store", ""))
        comp_by_brand_store.setdefault(key, []).append(s.get("price", 0.0))

    headers = ["Cadena", f"Precio medio {brand}", "Competidor", "Precio medio", "Ratio", "Situación"]
    col_w   = [(W - 30*mm) * r for r in [0.14, 0.16, 0.20, 0.16, 0.10, 0.24]]
    rows    = [[Paragraph(h, BODYB) for h in headers]]
    style   = [
        ("BACKGROUND", (0,0), (-1,0), CARBON),
        ("TEXTCOLOR",  (0,0), (-1,0), BLANCO),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [GRIS_L, BLANCO]),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("GRID",       (0,0), (-1,-1), 0.3, GRIS_B),
    ]

    row_idx = 1
    for (comp_brand, store), comp_prices in sorted(comp_by_brand_store.items()):
        my_prices = my_by_store.get(store, [])
        if not my_prices:
            continue
        my_avg   = sum(my_prices) / len(my_prices)
        comp_avg = sum(comp_prices) / len(comp_prices)
        ratio    = my_avg / comp_avg if comp_avg else 0
        if ratio > 1.03:
            situacion = "Soy más caro"
            sit_bg    = ROJO_L
        elif ratio < 0.97:
            situacion = "Soy más barato"
            sit_bg    = colors.HexColor("#C6F6D5")
        else:
            situacion = "En paridad"
            sit_bg    = GRIS_L

        row = [
            Paragraph(STORE_LABELS.get(store, store), BODY),
            Paragraph(f"S/ {my_avg:.2f}", BODY),
            Paragraph(comp_brand, BODY),
            Paragraph(f"S/ {comp_avg:.2f}", BODY),
            Paragraph(f"{ratio:.2f}x", BODYB),
            Paragraph(situacion, BODY),
        ]
        rows.append(row)
        style.append(("BACKGROUND", (5, row_idx), (5, row_idx), sit_bg))
        row_idx += 1

    if len(rows) > 1:
        t = Table(rows, colWidths=col_w)
        t.setStyle(TableStyle(style))
        content.append(t)
    else:
        content.append(Paragraph("Sin datos de competidores para este período.", BODY))

    content.append(sp(8))
    rank = data.get("category_rank")
    total_brands = data.get("category_total_brands")
    if rank and total_brands:
        content.append(Paragraph(
            f"Posición en categoría: <b>#{rank} de {total_brands} marcas</b> "
            f"(1 = precio más bajo en la categoría).",
            BODYB
        ))
    content.append(PageBreak())
    return content


def page_promo_tracker(brand: str, data: dict) -> list:
    """Página 4 — Promo Tracker: historial de activaciones del mes."""
    promos  = data.get("promo_events", [])
    content: list = [section_header("04", "Promo Tracker")]

    content.append(Paragraph(
        "Activaciones de descuento detectadas en el período. "
        "Duración estimada = días entre primera y última observación con descuento activo.",
        BODY
    ))
    content.append(sp(6))

    if not promos:
        content.append(Paragraph("Sin promos detectadas en el período.", BODY))
        content.append(PageBreak())
        return content

    # Separar mis promos vs competidores
    my_promos   = [p for p in promos if brand.lower() in p.get("name", "").lower()]
    comp_promos = [p for p in promos if brand.lower() not in p.get("name", "").lower()]

    for section_label, promo_list, bg_header in [
        (f"Activaciones propias ({brand})", my_promos,   VERDE_D),
        ("Activaciones de competidores",     comp_promos, CARBON),
    ]:
        if not promo_list:
            continue
        content.append(Paragraph(section_label, H3))
        content.append(sp(3))

        headers = ["SKU", "Cadena", "Descuento", "Inicio", "Fin", "Duración"]
        col_w   = [(W - 30*mm) * r for r in [0.35, 0.15, 0.12, 0.13, 0.13, 0.12]]
        rows    = [[Paragraph(h, BODYB) for h in headers]]
        style   = [
            ("BACKGROUND", (0,0), (-1,0), bg_header),
            ("TEXTCOLOR",  (0,0), (-1,0), BLANCO),
            ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE",   (0,0), (-1,-1), 8),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [GRIS_L, BLANCO]),
            ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
            ("TOPPADDING", (0,0), (-1,-1), 4),
            ("BOTTOMPADDING", (0,0), (-1,-1), 4),
            ("GRID",       (0,0), (-1,-1), 0.3, GRIS_B),
        ]
        for p in promo_list:
            dur = p.get("duration_days", "—")
            row = [
                Paragraph(p.get("name", "—"), BODY),
                Paragraph(STORE_LABELS.get(p.get("store",""), p.get("store","—")), BODY),
                Paragraph(f"{p.get('discount',0):.0f}%", BODYB),
                Paragraph(str(p.get("start", "—")), BODY),
                Paragraph(str(p.get("end", "—")), BODY),
                Paragraph(f"{dur}d" if dur != "—" else "—", BODY),
            ]
            rows.append(row)

        t = Table(rows, colWidths=col_w)
        t.setStyle(TableStyle(style))
        content.append(t)
        content.append(sp(10))

    content.append(PageBreak())
    return content


def page_dispersion(brand: str, data: dict) -> list:
    """Página 5 — Price dispersion: mi marca vs industria."""
    cv_brand    = data.get("dispersion_score", 0.0)
    cv_industry = data.get("industry_dispersion", 0.0)
    my_skus     = data.get("my_skus", [])
    content: list = [section_header("05", "Dispersión de Precio")]

    content.append(Paragraph(
        "Coeficiente de variación (CV) del precio cross-cadena. "
        "CV bajo = precio consistente entre retailers. "
        "CV alto = alta variabilidad de precio de góndola (riesgo de imagen).",
        BODY
    ))
    content.append(sp(8))

    # KPI bar de dispersión
    content.append(kpi_bar([
        (f"{cv_brand*100:.1f}%", f"CV {brand}"),
        (f"{cv_industry*100:.1f}%", "CV industria"),
        ("mejor" if cv_brand <= cv_industry else "peor",
         "vs industria"),
    ]))
    content.append(sp(12))

    # Tabla: CV por SKU
    content.append(Paragraph("Dispersión por SKU", H3))
    content.append(sp(4))

    # Calcular CV por producto
    by_product: dict[str, list[float]] = {}
    for s in my_skus:
        nm = s.get("name", "—")
        by_product.setdefault(nm, []).append(s.get("price", 0.0))

    headers = ["Producto", "Precio mín", "Precio máx", "Spread S/", "CV"]
    col_w   = [(W - 30*mm) * r for r in [0.44, 0.14, 0.14, 0.14, 0.14]]
    rows    = [[Paragraph(h, BODYB) for h in headers]]
    style   = [
        ("BACKGROUND", (0,0), (-1,0), CARBON),
        ("TEXTCOLOR",  (0,0), (-1,0), BLANCO),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [GRIS_L, BLANCO]),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("GRID",       (0,0), (-1,-1), 0.3, GRIS_B),
    ]
    import statistics
    for prod, prices in sorted(by_product.items()):
        if len(prices) < 2:
            continue
        mn, mx = min(prices), max(prices)
        spread  = mx - mn
        mean    = sum(prices) / len(prices)
        cv      = statistics.stdev(prices) / mean if mean else 0
        cv_bg   = ROJO_L if cv > 0.08 else (AMAR_L if cv > 0.04 else colors.HexColor("#C6F6D5"))
        row = [
            Paragraph(prod, BODY),
            Paragraph(f"S/ {mn:.2f}", BODY),
            Paragraph(f"S/ {mx:.2f}", BODY),
            Paragraph(f"S/ {spread:.2f}", BODY),
            Paragraph(f"{cv*100:.1f}%", BODYB),
        ]
        rows.append(row)
        style.append(("BACKGROUND", (4, len(rows)-1), (4, len(rows)-1), cv_bg))

    if len(rows) > 1:
        t = Table(rows, colWidths=col_w)
        t.setStyle(TableStyle(style))
        content.append(t)
    else:
        content.append(Paragraph("Insuficientes observaciones cross-cadena para calcular dispersión.", BODY))

    content.append(PageBreak())
    return content


def page_movers(brand: str, data: dict) -> list:
    """Página 6 — Top movers de la categoría."""
    movers  = data.get("top_movers", [])
    content: list = [section_header("06", "Top Movers de la Categoría")]

    content.append(Paragraph(
        "SKUs con mayor variación de precio en el período. "
        "Incluye todas las marcas de la misma categoría.",
        BODY
    ))
    content.append(sp(6))

    if not movers:
        content.append(Paragraph("Sin movers registrados en este período.", BODY))
        content.append(PageBreak())
        return content

    headers = ["SKU", "Marca", "Cadena", "Variación %", "Dirección"]
    col_w   = [(W - 30*mm) * r for r in [0.42, 0.16, 0.16, 0.14, 0.12]]
    rows    = [[Paragraph(h, BODYB) for h in headers]]
    style   = [
        ("BACKGROUND", (0,0), (-1,0), CARBON),
        ("TEXTCOLOR",  (0,0), (-1,0), BLANCO),
        ("FONTNAME",   (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",   (0,0), (-1,-1), 8),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [GRIS_L, BLANCO]),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("GRID",       (0,0), (-1,-1), 0.3, GRIS_B),
    ]

    for i, m in enumerate(movers, 1):
        chg      = m.get("change_pct", 0)
        brand_m  = m.get("brand", "—")
        is_mine  = brand_m.lower() == brand.lower()
        direc    = "^ Sube" if chg > 0 else "v Baja"
        chg_bg   = (ROJO_L if chg > 5 else AMAR_L) if chg > 0 else colors.HexColor("#C6F6D5")
        name_style = BODYB if is_mine else BODY
        row = [
            Paragraph(m.get("name", "—"), name_style),
            Paragraph(brand_m + (" *" if is_mine else ""), BODYB if is_mine else BODY),
            Paragraph(STORE_LABELS.get(m.get("store",""), m.get("store","—")), BODY),
            Paragraph(f"{chg:+.1f}%", BODYB),
            Paragraph(direc, BODY),
        ]
        rows.append(row)
        style.append(("BACKGROUND", (3, i), (3, i), chg_bg))

    t = Table(rows, colWidths=col_w)
    t.setStyle(TableStyle(style))
    content.append(t)
    content.append(sp(6))
    content.append(Paragraph(
        f"* SKUs de {brand}. Variacion calculada sobre periodo de {data.get('period_days',30)} dias.",
        NOTE
    ))
    content.append(PageBreak())
    return content


def page_macro(brand: str, data: dict, month_label: str) -> list:
    """Página 7 — Contexto macro."""
    macro   = data.get("macro", {})
    content: list = [section_header("07", "Contexto Macro — Mercado Retail Perú")]

    content.append(Paragraph(
        f"Indicadores macro de CLI Market para el período {month_label}. "
        "Fuente: price_snapshots supermercados PE · RPV = Retail Price Variation.",
        BODY
    ))
    content.append(sp(8))

    content.append(kpi_bar([
        (f"{(macro.get('rpv_supermercados',1)-1)*100:+.1f}%", "RPV supermercados"),
        (f"{macro.get('promo_intensity_pct',0):.1f}%",        "Promo intensity"),
        (f"{macro.get('canasta_basica_index',100):.1f}",       "BSI (Canasta)"),
        (f"{macro.get('inflation_mom_pct',0):+.2f}%",          "Inflación MoM"),
    ]))
    content.append(sp(14))

    content.append(Paragraph("¿Qué significan estos indicadores para tu marca?", H3))
    content.append(sp(4))

    rpv   = macro.get("rpv_supermercados", 1.0)
    promo = macro.get("promo_intensity_pct", 0.0)

    insights = []
    if rpv > 1.01:
        insights.append(
            f"El RPV supermercados subió {(rpv-1)*100:.1f}% — el mercado está aumentando precios. "
            f"Si {brand} no sube o mantiene, gana ventaja de precio relativo pero presiona márgenes."
        )
    elif rpv < 0.99:
        insights.append(
            f"El RPV bajó {(1-rpv)*100:.1f}% — presión de precio generalizada. "
            f"Validar si {brand} está bajando al ritmo del mercado o quedando rezagado (caro)."
        )
    else:
        insights.append("Mercado estable en precio. Sin señal de guerra de precios en la categoría.")

    if promo > 20:
        insights.append(
            f"Promo intensity alta ({promo:.1f}%) — más de 1 de cada 5 SKUs en descuento. "
            "Ambiente promocional agresivo: verificar si los descuentos de competidores "
            "están desplazando sell-out de tus SKUs."
        )
    else:
        insights.append(
            f"Promo intensity moderada ({promo:.1f}%). Ambiente sin presión promocional extrema."
        )

    for ins in insights:
        content.append(Paragraph(f"• {ins}", BULLET))

    content.append(PageBreak())
    return content


def page_recomendaciones(brand: str, data: dict) -> list:
    """Página 8 — Recomendaciones de acción."""
    my_skus      = data.get("my_skus", [])
    promo_events = data.get("promo_events", [])
    cv_brand     = data.get("dispersion_score", 0.0)

    content: list = [section_header("08", "Recomendaciones de Acción")]
    content.append(Paragraph(
        "Acciones prioritarias derivadas del análisis del período. Generadas por plantilla "
        "a partir de los datos — validar con el equipo comercial antes de ejecutar.",
        BODY
    ))
    content.append(sp(8))

    recs = []

    # Rec 1: desvíos vs PVP
    alertas_alto = [s for s in my_skus if desvio_badge(s["price"], s.get("pvp_suggested"))[0]
                    not in ("✓", "—") and s["price"] > (s.get("pvp_suggested") or 0) * 1.05]
    if alertas_alto:
        stores = list({STORE_LABELS.get(s["store"], s["store"]) for s in alertas_alto})
        recs.append((
            "Negociar corrección de precio con retail",
            f"{len(alertas_alto)} SKU(s) están por encima del PVP sugerido en "
            f"{', '.join(stores[:3])}{'...' if len(stores)>3 else ''}. "
            "Iniciar conversación con el key account de cada cadena para alinear precio de góndola."
        ))

    # Rec 2: promos competidores agresivos
    comp_promos = [e for e in promo_events if brand.lower() not in e.get("name","").lower()]
    if comp_promos:
        comp_brands = list({e.get("name","").split()[0] for e in comp_promos})
        recs.append((
            "Evaluar respuesta a promociones de competidores",
            f"{', '.join(comp_brands[:2])} {'activó' if len(comp_promos)==1 else 'activaron'} "
            f"{len(comp_promos)} promo(s) en el período. "
            "Analizar si el volumen de venta de tus SKUs se vio afectado y considerar "
            "activación defensiva en las cadenas afectadas."
        ))

    # Rec 3: dispersión alta
    if cv_brand > 0.06:
        recs.append((
            "Reducir dispersión cross-cadena",
            f"El CV de precio de {brand} ({cv_brand*100:.1f}%) supera el benchmark de industria. "
            "Implementar política de precio sugerido más clara con cada cadena para "
            "proteger consistencia de imagen de marca."
        ))

    # Rec 4: genérica si no hay alertas
    if not recs:
        recs.append((
            "Mantener monitoreo semanal",
            f"Sin alertas críticas en el período para {brand}. "
            "Continuar monitoreo semanal para detectar cambios tempranos. "
            "Considerar activar alertas automáticas por email para desvíos &gt;5%."
        ))

    for rec_title, rec_body in recs:
        content.append(KeepTogether([
            Paragraph(f"• {rec_title}", BODYB),
            Paragraph(rec_body, BODY),
            sp(6),
        ]))

    content.append(sp(10))
    content.append(hr(GRIS_B, 0.5))
    content.append(sp(6))
    content.append(Paragraph(
        "CLI Market Brand Intelligence · hello@cli-market.dev · cli-market.dev/brand · "
        "Datos: price_snapshots · Refresh: 8h · 41 retailers VTEX verificados",
        CONF
    ))
    content.append(Paragraph(
        "Este reporte es de uso confidencial y exclusivo del cliente destinatario. "
        "Los datos de una marca no son compartidos con ningún otro cliente de CLI Market.",
        CONF
    ))
    return content


# ── Generador principal ───────────────────────────────────────────────────────

def generate_report(
    brand: str,
    country: str = "PE",
    out_path: str | None = None,
    month: str | None = None,
    demo: bool = False,
    days: int = 30,
    competitors: list[str] | None = None,
) -> str:
    """Genera el PDF. Devuelve la ruta del archivo generado."""
    now = datetime.now(timezone.utc)
    if month:
        try:
            dt = datetime.strptime(month, "%Y-%m")
            month_label = dt.strftime("%B %Y")
        except ValueError:
            month_label = month
    else:
        month_label = now.strftime("%B %Y")

    brand_slug = brand.lower().replace(" ", "-")
    default_out = (
        Path(__file__).parent / "generated" / "reports" /
        f"brand-report-{brand_slug}-{now.strftime('%Y-%m')}.pdf"
    )
    pdf_path = Path(out_path) if out_path else default_out
    pdf_path.parent.mkdir(parents=True, exist_ok=True)

    # Obtener datos
    if demo:
        data = demo_data(brand)
    else:
        print(f"  Fetching brand data for {brand}...")
        data = fetch_brand_data(brand, country, days, competitors)
        # Intentar enriquecer con macro
        print("  Fetching macro context...")
        dash = fetch_dashboard(country)
        if dash:
            macro = {}
            kpis  = dash.get("kpis", {})
            if kpis.get("rpv_supermercados"):
                macro["rpv_supermercados"] = kpis["rpv_supermercados"]
            infl = dash.get("inflation", {})
            if infl:
                macro["inflation_mom_pct"] = infl.get("mom_pct", 0)
            promo = dash.get("promo_intensity", {})
            if promo:
                macro["promo_intensity_pct"] = promo.get("value", 0)
            canasta = dash.get("canasta_basica", {})
            if canasta:
                macro["canasta_basica_index"] = canasta.get("index", 100)
            data["macro"] = macro or data.get("macro", {})

    # Construir contenido
    print(f"  Building PDF: {pdf_path}")
    content: list = []
    content += page_portada(brand, month_label, data)
    content += page_mis_skus(brand, data)
    content += page_competidores(brand, data)
    content += page_promo_tracker(brand, data)
    content += page_dispersion(brand, data)
    content += page_movers(brand, data)
    content += page_macro(brand, data, month_label)
    content += page_recomendaciones(brand, data)

    # Render
    doc = SimpleDocTemplate(
        str(pdf_path),
        pagesize=A4,
        leftMargin=15*mm, rightMargin=15*mm,
        topMargin=12*mm,  bottomMargin=14*mm,
        title=f"Brand Intelligence Report — {brand} — {month_label}",
        author="CLI Market Intelligence",
        subject="Brand Intelligence Monthly Report",
    )
    doc.build(content)
    return str(pdf_path)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    # Fix Windows console encoding so UTF-8 chars don't crash stdout
    import io as _io
    if hasattr(sys.stdout, "buffer"):
        sys.stdout = _io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "buffer"):
        sys.stderr = _io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        description="CLI Market - Brand Intelligence Monthly Report Generator"
    )
    parser.add_argument("--brand",       default="Gloria", help="Marca a monitorear")
    parser.add_argument("--country",     default="PE",     help="País (ISO 2)")
    parser.add_argument("--month",       default=None,     help="Período YYYY-MM (default: mes actual)")
    parser.add_argument("--days",        default=30, type=int, help="Ventana histórica en días")
    parser.add_argument("--competitors", default=None,     help="Marcas competidoras, separadas por coma")
    parser.add_argument("--out",         default=None,     help="Ruta de salida del PDF")
    parser.add_argument("--demo",        action="store_true", help="Usar datos sintéticos (sin API key)")
    parser.add_argument("--api-url",     default=None,     help="Override MARKET_API_URL")
    parser.add_argument("--api-key",     default=None,     help="Override MARKET_API_TOKEN")
    args = parser.parse_args()

    if args.api_url:
        os.environ["MARKET_API_URL"] = args.api_url
    if args.api_key:
        os.environ["MARKET_API_TOKEN"] = args.api_key

    competitors = [c.strip() for c in args.competitors.split(",")] if args.competitors else None

    print("\nCLI Market Brand Intelligence Report")
    print(f"  Marca:   {args.brand}")
    print(f"  País:    {args.country}")
    print(f"  Período: {args.month or 'mes actual'}")
    print(f"  Modo:    {'DEMO (datos sintéticos)' if args.demo else 'producción'}")
    if competitors:
        print(f"  Competidores: {', '.join(competitors)}")
    print()

    try:
        path = generate_report(
            brand=args.brand,
            country=args.country,
            out_path=args.out,
            month=args.month,
            demo=args.demo,
            days=args.days,
            competitors=competitors,
        )
        print(f"\n✅ PDF generado: {path}")
        print(f"   Abre con: start {path}")
    except RuntimeError as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        print("   Tip: usa --demo para generar con datos sintéticos sin API key.")
        sys.exit(1)


if __name__ == "__main__":
    main()
