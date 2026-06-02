"""Data Moat indicator definitions and value queries.

34 indicators across 8 categories. Definitions are seeded into the DB at startup;
values are computed by the collector (private backend) or the intel refresh endpoint.

This module is the public half — definitions and read queries. The private
collector writes indicator_values during each run.
"""

from __future__ import annotations

import logging

logger = logging.getLogger("market").getChild("indicators")

# ── Indicator definitions (34) ────────────────────────────────────────────────

_CANASTA_ITEMS = [
    "leche", "arroz", "aceite", "azucar", "huevos",
    "pan", "cafe", "pollo", "queso", "jabon",
]

_INDICATOR_DEFS: list[dict] = [
    # ── Core moat + macro (10) ────────────────────────────────────────────────
    {
        "key": "promo_intensity",
        "name": "Intensidad promocional",
        "category": "retail",
        "source": "internal:price_snapshots",
        "unit": "pct",
        "refresh_hours": 8,
        "description": "% de SKUs con descuento activo en góndola",
        "formula": "COUNT(price < list_price) / COUNT(*) * 100",
    },
    {
        "key": "price_dispersion",
        "name": "Dispersión de precios",
        "category": "retail",
        "source": "internal:price_snapshots",
        "unit": "ratio",
        "refresh_hours": 8,
        "description": "Coeficiente de variación medio entre tiendas por producto",
        "formula": "AVG(STDDEV(price) / AVG(price)) por subcategoría",
    },
    {
        "key": "basket_stress_index",
        "name": "Índice de estrés de canasta",
        "category": "affordability",
        "source": "internal:price_snapshots",
        "unit": "index",
        "refresh_hours": 8,
        "description": "Costo mínimo de canasta / baseline 30d × 100",
        "formula": "MIN(canasta_total) / AVG(canasta_total_30d) * 100",
    },
    {
        "key": "search_momentum",
        "name": "Momentum de búsquedas",
        "category": "demand",
        "source": "internal:search_queries",
        "unit": "ratio",
        "refresh_hours": 24,
        "description": "Búsquedas 7d / 7d previos",
        "formula": "COUNT(search_7d) / NULLIF(COUNT(search_prev_7d), 0)",
    },
    {
        "key": "moat_freshness",
        "name": "Frescura del moat",
        "category": "quality",
        "source": "internal:price_snapshots",
        "unit": "pct",
        "refresh_hours": 8,
        "description": "% de snapshots con menos de 24h de antigüedad",
        "formula": "snapshots_24h / total_indexed * 100",
    },
    {
        "key": "store_coverage",
        "name": "Cobertura de tiendas",
        "category": "quality",
        "source": "internal:price_snapshots",
        "unit": "count",
        "refresh_hours": 8,
        "description": "Tiendas distintas con al menos un precio indexado",
        "formula": "COUNT(DISTINCT store) WHERE price > 0",
    },
    {
        "key": "fx_usd_local",
        "name": "Tipo de cambio USD → moneda local",
        "category": "macro",
        "source": "external:open.er-api.com",
        "unit": "rate",
        "refresh_hours": 24,
        "description": "USD a moneda local vía Open Exchange Rates API",
        "formula": "GET https://open.er-api.com/v6/latest/USD",
    },
    {
        "key": "cpi_official_yoy",
        "name": "IPC oficial interanual",
        "category": "macro",
        "source": "external:World Bank",
        "unit": "pct",
        "refresh_hours": 168,
        "description": "CPI YoY del World Bank (FP.CPI.TOTL.ZG)",
        "formula": "API World Bank indicator FP.CPI.TOTL.ZG",
    },
    {
        "key": "food_price_index",
        "name": "Índice de precios de alimentos",
        "category": "macro",
        "source": "external:World Bank",
        "unit": "index",
        "refresh_hours": 168,
        "description": "Food Price Index (AG.PRD.FOOD.XD)",
        "formula": "API World Bank indicator AG.PRD.FOOD.XD",
    },
    {
        "key": "collector_vs_official_gap",
        "name": "Brecha collector vs CPI oficial",
        "category": "composite",
        "source": "computed",
        "unit": "pp",
        "refresh_hours": 24,
        "description": "Inflación observada por collector − CPI oficial (puntos porcentuales)",
        "formula": "collector_inflation_pct - cpi_official_yoy",
    },

    # ── Enriquecimiento público (11) ───────────────────────────────────────────
    {
        "key": "off_match_rate",
        "name": "Tasa de match Open Food Facts",
        "category": "product",
        "source": "external:Open Food Facts",
        "unit": "pct",
        "refresh_hours": 168,
        "description": "% de SKUs de supermercado matcheados con OFF (muestra)",
        "formula": "COUNT(matched) / COUNT(sampled) * 100",
    },
    {
        "key": "off_nutriscore_ab_pct",
        "name": "% Nutri-Score A/B",
        "category": "product",
        "source": "external:Open Food Facts",
        "unit": "pct",
        "refresh_hours": 168,
        "description": "% de productos matcheados con Nutri-Score A o B",
        "formula": "COUNT(nutriscore IN (a,b)) / COUNT(matched) * 100",
    },
    {
        "key": "off_nova_avg",
        "name": "NOVA promedio",
        "category": "product",
        "source": "external:Open Food Facts",
        "unit": "index",
        "refresh_hours": 168,
        "description": "NOVA promedio (1–4) en productos matcheados",
        "formula": "AVG(nova_group) WHERE nova_group > 0",
    },
    {
        "key": "off_ultra_processed_pct",
        "name": "% Ultra-procesados",
        "category": "product",
        "source": "external:Open Food Facts",
        "unit": "pct",
        "refresh_hours": 168,
        "description": "% NOVA 4 (ultra-procesados) en productos matcheados",
        "formula": "COUNT(nova_group=4) / COUNT(matched) * 100",
    },
    {
        "key": "off_ecoscore_avg",
        "name": "Eco-Score promedio",
        "category": "product",
        "source": "external:Open Food Facts",
        "unit": "index",
        "refresh_hours": 168,
        "description": "Eco-Score promedio (A=5 … E=1)",
        "formula": "AVG(ecoscore_numeric) WHERE ecoscore IS NOT NULL",
    },
    {
        "key": "wiki_demand_momentum",
        "name": "Momentum de demanda Wikipedia",
        "category": "demand",
        "source": "external:Wikimedia Pageviews",
        "unit": "ratio",
        "refresh_hours": 24,
        "description": "Pageviews 7d / 7d previos para artículos de canasta",
        "formula": "SUM(pageviews_7d) / NULLIF(SUM(pageviews_prev_7d), 0)",
    },
    {
        "key": "wiki_staple_momentum",
        "name": "Momentum Wikipedia — básicos",
        "category": "demand",
        "source": "external:Wikimedia Pageviews",
        "unit": "ratio",
        "refresh_hours": 24,
        "description": "Momentum pageviews para leche, arroz, aceite",
        "formula": "wiki_demand_momentum filtrado a básicos",
    },
    {
        "key": "staple_price_momentum",
        "name": "Momentum de precios básicos",
        "category": "affordability",
        "source": "internal:price_history",
        "unit": "pct",
        "refresh_hours": 8,
        "description": "Δ% precio canasta básica 7d",
        "formula": "(avg_price_now - avg_price_7d_ago) / avg_price_7d_ago * 100",
    },
    {
        "key": "weather_logistics_stress",
        "name": "Estrés logístico por clima",
        "category": "logistics",
        "source": "external:Open-Meteo",
        "unit": "index",
        "refresh_hours": 12,
        "description": "Índice 0–100 de estrés logístico por lluvia/calor",
        "formula": "precip_weight * rain_mm + temp_weight * max(0, temp_C - 30)",
    },
    {
        "key": "food_cpi_yoy",
        "name": "Inflación alimentaria oficial",
        "category": "macro",
        "source": "external:World Bank",
        "unit": "pct",
        "refresh_hours": 168,
        "description": "Food CPI YoY del World Bank (FP.CPI.FOOD.ZG)",
        "formula": "API World Bank FP.CPI.FOOD.ZG",
    },
    {
        "key": "food_inflation_spread",
        "name": "Spread alimentos vs headline CPI",
        "category": "composite",
        "source": "computed",
        "unit": "pp",
        "refresh_hours": 168,
        "description": "Food CPI YoY − headline CPI YoY",
        "formula": "food_cpi_yoy - cpi_official_yoy",
    },

    # ── Tier 2 — fuentes públicas secundarias (10) ─────────────────────────────
    {
        "key": "imf_inflation_yoy",
        "name": "IMF Inflación YoY",
        "category": "macro",
        "source": "external:IMF DataMapper",
        "unit": "pct",
        "refresh_hours": 168,
        "description": "PCPIPCH — validación cruzada CPI vía IMF",
        "formula": "IMF DataMapper PCPIPCH",
    },
    {
        "key": "imf_gdp_growth_yoy",
        "name": "IMF Crecimiento PIB YoY",
        "category": "macro",
        "source": "external:IMF DataMapper",
        "unit": "pct",
        "refresh_hours": 168,
        "description": "NGDP_RPCH — crecimiento PIB real",
        "formula": "IMF DataMapper NGDP_RPCH",
    },
    {
        "key": "imf_epi_inflation_yoy",
        "name": "IMF Inflación fin de período",
        "category": "macro",
        "source": "external:IMF DataMapper",
        "unit": "pct",
        "refresh_hours": 168,
        "description": "PCPIEPCH — inflación fin de período",
        "formula": "IMF DataMapper PCPIEPCH",
    },
    {
        "key": "eurostat_food_hicp_yoy",
        "name": "Eurostat Food HICP YoY",
        "category": "macro",
        "source": "external:Eurostat",
        "unit": "pct",
        "refresh_hours": 168,
        "description": "Food HICP para IT, FR",
        "formula": "Eurostat Food HICP",
    },
    {
        "key": "eurostat_headline_hicp_yoy",
        "name": "Eurostat Headline HICP YoY",
        "category": "macro",
        "source": "external:Eurostat",
        "unit": "pct",
        "refresh_hours": 168,
        "description": "Headline HICP CP00 para IT, FR",
        "formula": "Eurostat HICP CP00",
    },
    {
        "key": "bcb_food_inflation_mom",
        "name": "BCB Inflación alimentos MoM",
        "category": "macro",
        "source": "external:BCB",
        "unit": "pct",
        "refresh_hours": 168,
        "description": "IPCA alimentos MoM (BR)",
        "formula": "BCB API IPCA alimentos",
    },
    {
        "key": "bcb_headline_inflation_mom",
        "name": "BCB Inflación general MoM",
        "category": "macro",
        "source": "external:BCB",
        "unit": "pct",
        "refresh_hours": 168,
        "description": "IPCA general MoM (BR)",
        "formula": "BCB API IPCA general",
    },
    {
        "key": "macro_unemployment_rate",
        "name": "Tasa de desempleo",
        "category": "macro",
        "source": "external:World Bank",
        "unit": "pct",
        "refresh_hours": 168,
        "description": "Desempleo % (SL.UEM.TOTL.ZS)",
        "formula": "World Bank SL.UEM.TOTL.ZS",
    },
    {
        "key": "wb_gdp_growth_yoy",
        "name": "World Bank Crecimiento PIB YoY",
        "category": "macro",
        "source": "external:World Bank",
        "unit": "pct",
        "refresh_hours": 168,
        "description": "Crecimiento PIB (NY.GDP.MKTP.KD.ZG)",
        "formula": "World Bank NY.GDP.MKTP.KD.ZG",
    },
    {
        "key": "imf_wb_cpi_gap",
        "name": "Brecha IMF vs World Bank CPI",
        "category": "composite",
        "source": "computed",
        "unit": "pp",
        "refresh_hours": 168,
        "description": "IMF CPI − World Bank CPI (consistencia)",
        "formula": "imf_inflation_yoy - cpi_official_yoy",
    },
]

# ── Subcategory indicators (3 types × 10 staples) ─────────────────────────────

_SUBCAT_TYPES = [
    ("subcat_price_momentum", "Momentum precio", "affordability", "internal:price_history", "pct", 8,
     "Δ% precio 7d de"),
    ("subcat_wiki_momentum", "Momentum Wiki", "demand", "external:Wikimedia Pageviews", "ratio", 24,
     "Pageviews 7d / 7d previos del artículo wiki de"),
    ("subcat_min_price", "Precio mínimo", "affordability", "internal:price_snapshots", "rate", 8,
     "Precio mínimo indexado de"),
]

for prefix, name_prefix, cat, src, unit, refresh, desc_prefix in _SUBCAT_TYPES:
    for item in _CANASTA_ITEMS:
        _INDICATOR_DEFS.append({
            "key": f"{prefix}_{item}",
            "name": f"{name_prefix} {item}",
            "category": cat,
            "source": src,
            "unit": unit,
            "refresh_hours": refresh,
            "description": f"{desc_prefix} {item}",
            "formula": "Internal query on price_snapshots / price_history",
        })

INDICATOR_DEFINITIONS = _INDICATOR_DEFS

# Keys that come from enrichment sources (OFF, Wiki, Open-Meteo, etc.)
ENRICHMENT_INDICATOR_KEYS: set[str] = {
    "off_match_rate", "off_nutriscore_ab_pct", "off_nova_avg",
    "off_ultra_processed_pct", "off_ecoscore_avg",
    "wiki_demand_momentum", "wiki_staple_momentum",
    "weather_logistics_stress",
    "food_cpi_yoy",
    *[f"subcat_wiki_momentum_{item}" for item in _CANASTA_ITEMS],
}

# Score definitions
SCORE_DEFINITIONS: list[dict] = [
    {"key": "retail_aggression", "name": "Agresividad retail", "inputs": ["promo_intensity"], "interpretation": "Alta promo → score alto"},
    {"key": "price_fairness", "name": "Equidad de precios", "inputs": ["price_dispersion"], "interpretation": "Alta dispersión → score bajo"},
    {"key": "basket_stress", "name": "Estrés de canasta", "inputs": ["basket_stress_index"], "interpretation": ">105 elevado, <95 aliviado"},
    {"key": "data_confidence", "name": "Confianza del dato", "inputs": ["moat_freshness"], "interpretation": "≥80 fresh"},
    {"key": "macro_alignment", "name": "Alineación macro", "inputs": ["collector_vs_official_gap"], "interpretation": "Gap pequeño → alineado"},
    {"key": "product_intelligence", "name": "Inteligencia de producto", "inputs": ["off_match_rate", "off_nova_avg"], "interpretation": "Cobertura OFF − penalización NOVA"},
    {"key": "demand_outlook", "name": "Perspectiva de demanda", "inputs": ["wiki_demand_momentum"], "interpretation": ">1.1 rising, <0.9 cooling"},
    {"key": "logistics_risk", "name": "Riesgo logístico", "inputs": ["weather_logistics_stress"], "interpretation": ">40 elevated"},
    {"key": "food_premium", "name": "Prima alimentaria", "inputs": ["food_inflation_spread"], "interpretation": "Spread food vs headline CPI"},
    {"key": "nutrition_quality", "name": "Calidad nutricional", "inputs": ["off_nutriscore_ab_pct", "off_ultra_processed_pct", "off_ecoscore_avg"], "interpretation": "Calidad nutricional + ambiental"},
    {"key": "staple_demand", "name": "Demanda de básicos", "inputs": ["wiki_staple_momentum"], "interpretation": "Demanda Wikipedia en básicos"},
    {"key": "macro_validation", "name": "Validación macro", "inputs": ["imf_wb_cpi_gap"], "interpretation": "Consistencia IMF vs World Bank"},
    {"key": "labor_stress", "name": "Estrés laboral", "inputs": ["macro_unemployment_rate"], "interpretation": "Presión laboral / desempleo"},
    {"key": "growth_outlook", "name": "Perspectiva de crecimiento", "inputs": ["imf_gdp_growth_yoy"], "interpretation": "Expansión vs desaceleración PIB"},
]


# ── DB helpers ─────────────────────────────────────────────────────────────────

def seed_indicator_definitions(db) -> int:
    """Insert indicator definitions (idempotent — INSERT OR IGNORE)."""
    written = 0
    for ind in INDICATOR_DEFINITIONS:
        try:
            db.execute(
                """INSERT OR IGNORE INTO indicator_definitions
                   (key, name, category, source, unit, refresh_hours, description, formula)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    ind["key"], ind["name"], ind["category"], ind["source"],
                    ind["unit"], ind["refresh_hours"], ind["description"], ind["formula"],
                ),
            )
            written += 1
        except Exception as e:
            logger.warning("seed %s skipped: %s", ind.get("key", "?"), e)
    db.commit()
    logger.info("Seeded %d indicator definitions", written)
    return written


def get_latest_values(
    db, *, country: str | None = None, line: str | None = None, limit: int = 200
) -> list[dict]:
    """Return latest indicator values, one row per indicator_key (most recent recorded_at)."""
    params: list = []
    where_clauses: list[str] = []
    if country:
        where_clauses.append("iv.country = ?")
        params.append(country.upper())
    if line:
        where_clauses.append("iv.line = ?")
        params.append(line)
    where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""
    rows = db.execute(
        f"""SELECT iv.indicator_key as key, iv.scope, iv.country, iv.line,
                   iv.value, iv.recorded_at,
                   ind.name, ind.category, ind.source, ind.unit
            FROM indicator_values iv
            LEFT JOIN indicator_definitions ind ON ind.key = iv.indicator_key
            WHERE iv.id IN (
                SELECT MAX(id) FROM indicator_values
                {where_sql}
                GROUP BY indicator_key
            )
            ORDER BY ind.category, iv.indicator_key
            LIMIT ?""",
        params + [limit],
    ).fetchall()
    return [dict(r) for r in rows]


def get_indicator_catalog(db) -> list[dict]:
    """Return all indicator definitions (catalog, not values)."""
    rows = db.execute(
        """SELECT key, name, category, source, unit, refresh_hours, description, formula
           FROM indicator_definitions ORDER BY category, key"""
    ).fetchall()
    return [dict(r) for r in rows]


def get_scores(
    db, *, country: str | None = None, line: str | None = None
) -> dict:
    """Compute composite scores from latest indicator values."""
    latest = get_latest_values(db, country=country, line=line)
    value_map: dict[str, float] = {v["key"]: float(v["value"] or 0) for v in latest}
    scores: dict[str, dict] = {}
    for sc in SCORE_DEFINITIONS:
        inputs = sc["inputs"]
        vals = [value_map.get(k) for k in inputs if value_map.get(k) is not None]
        if not vals:
            score_val = None
            label = "sin datos"
        else:
            score_val = round(sum(vals) / len(vals), 1)
            label = _interpret_score(sc["key"], score_val)
        scores[sc["key"]] = {
            "score": score_val,
            "label": label,
            "interpretation": sc["interpretation"],
            "inputs": {k: value_map.get(k) for k in inputs},
        }
    return {
        "country": country,
        "line": line,
        "scores": scores,
        "disclaimer": "Señales operativas de góndola + contexto macro público. No reemplazan índices oficiales.",
    }


def _interpret_score(key: str, value: float | None) -> str:
    if value is None:
        return "sin datos"
    thresholds: dict[str, list[tuple[float, str]]] = {
        "retail_aggression": [(20, "baja"), (50, "moderada"), (float("inf"), "alta")],
        "price_fairness": [(3, "alta"), (6, "moderada"), (float("inf"), "baja")],
        "basket_stress": [(95, "aliviado"), (105, "normal"), (float("inf"), "elevado")],
        "data_confidence": [(50, "baja"), (80, "parcial"), (float("inf"), "alta")],
        "macro_alignment": [(2, "alineado"), (5, "moderado"), (float("inf"), "desalineado")],
        "product_intelligence": [(30, "baja"), (60, "parcial"), (float("inf"), "alta")],
        "demand_outlook": [(0.9, "enfriándose"), (1.1, "estable"), (float("inf"), "creciendo")],
        "logistics_risk": [(20, "bajo"), (40, "moderado"), (float("inf"), "elevado")],
        "food_premium": [(1, "bajo"), (3, "moderado"), (float("inf"), "alto")],
        "nutrition_quality": [(30, "baja"), (60, "media"), (float("inf"), "alta")],
        "staple_demand": [(0.9, "enfriándose"), (1.1, "estable"), (float("inf"), "creciendo")],
        "macro_validation": [(0.5, "consistente"), (1.0, "leve"), (float("inf"), "divergente")],
        "labor_stress": [(5, "bajo"), (10, "moderado"), (float("inf"), "alto")],
        "growth_outlook": [(1, "desaceleración"), (3, "moderado"), (float("inf"), "expansión")],
    }
    bands = thresholds.get(key, [(50, "neutral")])
    for threshold, label in bands:
        if value <= threshold:
            return label
    return "—"
