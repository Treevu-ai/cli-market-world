#!/usr/bin/env python3
"""CLI Market — Request Orchestrator (intent → tools → enrichers → response).

Implements docs/agents/orchestrator-contract.md (v0.1.0).

Usage:
  python ops/market_orchestrator.py --plan "optimiza leche, arroz, aceite PE hotelero budget 800"
  python ops/market_orchestrator.py --run "compara leche gloria en supermercados PE"
  python ops/market_orchestrator.py --prepare-enrich --plan-file ops/generated/orchestrator/last-plan.json
  python ops/market_orchestrator.py --assemble --plan-file ... --tools-file ... --outputs-dir ...

Phases:
  understand → plan → execute tools → prepare enrich prompts → (agent run) → assemble

Tool execution uses MARKET_API_URL (default production). Enrichment is prompt-based
like price_pulse_agents.py (LLM step is external unless --llm is wired later).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import httpx
except ImportError:  # pragma: no cover
    httpx = None  # type: ignore

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

ORCH_VERSION = "0.2.1"
GENERATED = Path(__file__).resolve().parent / "generated" / "orchestrator"
CONTEXTS = PROJECT_ROOT / "docs" / "agents" / "contexts"
CONTRACT = PROJECT_ROOT / "docs" / "agents" / "orchestrator-contract.md"

# agency-agents default path (Windows local + override)
AGENCY_ROOT = Path(
    os.getenv(
        "AGENCY_AGENTS_ROOT",
        str(Path.home() / "Proyectos" / "agency-agents"),
    )
)

API_URL = os.getenv("MARKET_API_URL", "https://cli-market-api.fly.dev").rstrip("/")

# --- Catalog -----------------------------------------------------------------

AGENT_CATALOG: dict[str, dict[str, str]] = {
    # Núcleo indispensable — cubren todos los intents con enriquecimiento real
    # (grounding concreto contra ToolResults, no boilerplate genérico).
    "pricing-analyst": {
        "role_path": "specialized/specialized-pricing-analyst.md",
        "context_path": str(CONTEXTS / "pricing-analyst-context.md"),
    },
    "supply-chain": {
        "role_path": "specialized/supply-chain-strategist.md",
        "context_path": str(CONTEXTS / "supply-chain-context.md"),
    },
    "operations": {
        "role_path": "specialized/operations-manager.md",
        "context_path": str(CONTEXTS / "operations-context.md"),
    },
    "reality-checker": {
        "role_path": "testing/testing-reality-checker.md",
        "context_path": str(CONTEXTS / "reality-checker-context.md"),
    },
    # Condicionales — solo se seleccionan para su intent/segmento específico.
    "analytics-reporter": {
        "role_path": "support/support-analytics-reporter.md",
        "context_path": str(CONTEXTS / "analytics-reporter-context.md"),
    },
    "hospitality": {
        "role_path": "specialized/hospitality-guest-services.md",
        "context_path": str(CONTEXTS / "hospitality-context.md"),
    },
    # Recortados del roster v1 (14 -> 6) tras consolidación 2026-07-16:
    # - financial-analyst / fpa-analyst / bookkeeper: contexto shape-eado para el
    #   JSON semanal de Price Pulse, no para ToolResult/FactIndex de este orquestador
    #   (siguen existiendo en docs/agents/contexts/ para Price Pulse, sin tocar).
    # - executive-summary / document-generator: redundantes con el paso SYNTHESIZE
    #   (modo deep ya cubre "resumen ejecutivo" y "deliverable" sin una llamada LLM aparte).
    # - support-responder: copy de error/ambigüedad no necesita LLM con grounding,
    #   es texto determinista (ver ramas ambiguous/commerce_action/household_prefs abajo).
    # - sales-engineer: no hay ToolResult que enriquecer -- es contenido de soporte/ventas,
    #   no inteligencia de compra. Categoría de request distinta a este pipeline.
    # - behavioral-nudge: genérico, se pliega dentro de pricing-analyst para household_prefs.
}

# Tool → HTTP mapping aligned with market_core/market_mcp.py + live OpenAPI
# (cli-market-api.fly.dev/openapi.json, 2026-07).
# Special handlers: market_discover (compose), path templates with {var}.
TOOL_HTTP: dict[str, dict[str, Any]] = {
    "market_search": {"method": "POST", "path": "/products/search"},
    "market_compare": {"method": "POST", "path": "/products/compare"},
    # One-call purchase optimization (missions); fallback to basket compare in execute_tool
    "market_optimize_purchase": {
        "method": "POST",
        "path": "/v1/missions/optimize-purchase",
        "fallback": {"method": "POST", "path": "/v1/basket/compare"},
    },
    "market_basket": {"method": "POST", "path": "/v1/basket/compare"},
    "market_substitutes": {"method": "GET", "path": "/v1/products/substitutes"},
    "market_ask": {"method": "POST", "path": "/agent/ask"},
    "market_add": {"method": "POST", "path": "/cart/add"},
    "market_cart": {"method": "GET", "path": "/cart"},
    "market_cart_update": {"method": "PUT", "path": "/cart/update"},
    "market_orders": {"method": "GET", "path": "/orders"},
    "market_barcode": {"method": "GET", "path": "/products/barcode/{code}"},
    "market_ticket": {"method": "POST", "path": "/v1/ticket/scan-url"},
    "market_intel_brief": {"method": "GET", "path": "/v1/intel/brief"},
    "market_inflation": {"method": "GET", "path": "/v1/intel/inflation"},
    "market_inflation_report": {"method": "GET", "path": "/v1/intel/inflation-report"},
    "market_scores": {"method": "GET", "path": "/v1/intel/scores"},
    "market_affordability": {"method": "GET", "path": "/v1/intel/affordability"},
    "market_price_risk": {"method": "GET", "path": "/v1/intel/price-risk"},
    "market_procurement_signal": {"method": "GET", "path": "/v1/intel/procurement-signal"},
    "market_trending": {"method": "GET", "path": "/analytics/trending"},
    "market_stats": {"method": "GET", "path": "/analytics/stats"},
    "market_price_history": {"method": "GET", "path": "/analytics/price-history"},
    "market_retailer_scorecard": {"method": "GET", "path": "/v1/intel/retailer-scorecard"},
    "market_informal_signal": {"method": "GET", "path": "/v1/intel/informal-signal"},
    "market_promo_detector": {"method": "GET", "path": "/v1/intel/promo-detector"},
    "market_export": {"method": "POST", "path": "/v1/data/export"},
    "market_household_get": {"method": "GET", "path": "/v1/household"},
    "market_whoami": {"method": "GET", "path": "/auth/whoami"},
    "market_subscription": {"method": "GET", "path": "/auth/subscription"},
    "market_favorites": {"method": "POST", "path": "/favorites"},
    "market_price_alerts": {"method": "GET", "path": "/v1/intel/alerts"},
    # market_discover uses custom compose in execute_tool
    "market_discover": {"method": "COMPOSE", "path": "/discover"},
}


@dataclass
class IntentEnvelope:
    intent_id: str
    primary: str
    secondary: list[str] = field(default_factory=list)
    language: str = "es"
    locale_hint: str | None = None
    entities: dict[str, Any] = field(default_factory=dict)
    user_tier_hint: str = "unknown"
    risk_flags: list[str] = field(default_factory=list)
    confidence: float = 0.0
    raw_request: str = ""


# --- Understand --------------------------------------------------------------

_COUNTRY_RE = re.compile(r"\b(PE|AR|MX|BR|CO|CL|IT|FR)\b", re.I)
_URL_RE = re.compile(r"https?://\S+", re.I)
_BUDGET_RE = re.compile(
    r"(?:budget|presupuesto|máximo|maximo|hasta)\s*(?:de\s*)?(?:S/\s*)?(\d+(?:[.,]\d+)?)",
    re.I,
)
_ITEM_SPLIT = re.compile(r"\s*(?:,|;|\by\b|\band\b)\s*", re.I)


def _default_entities() -> dict[str, Any]:
    return {
        "country": None,
        "line": None,
        "store": None,
        "items": [],
        "product_query": None,
        "product_id": None,
        "barcode": None,
        "ticket_url": None,
        "budget": None,
        "payment_method": None,
        "segment": None,
        "use_case": None,
        "days": 30,
        "constraints": {
            "preferred_stores": [],
            "allow_substitutes": True,
            "include_tco": True,
            "max_stores": 2,
        },
        "confirm": False,
    }


def extract_entities(text: str) -> dict[str, Any]:
    e = _default_entities()
    m = _COUNTRY_RE.search(text)
    if m:
        e["country"] = m.group(1).upper()
    url = _URL_RE.search(text)
    if url:
        e["ticket_url"] = url.group(0).rstrip(").,]")
    b = _BUDGET_RE.search(text)
    if b:
        e["budget"] = float(b.group(1).replace(",", "."))
    low = text.lower()
    for seg in ("hotelero", "restaurante", "retail", "oficina", "construccion"):
        if seg in low or (seg == "hotelero" and "hotel" in low):
            e["segment"] = seg
            break
    if "supermercado" in low:
        e["line"] = "supermercados"
    elif "farmacia" in low:
        e["line"] = "farmacias"
    elif "electro" in low:
        e["line"] = "electro"
    if any(w in low for w in ("confirmo checkout", "confirmar checkout", "sí checkout", "si checkout")):
        e["confirm"] = True
    # items: after keywords or comma lists with 2+ products
    items: list[dict[str, Any]] = []
    for pat in (
        r"(?:canasta|compra|optimiz\w*|arm[ae])\s+(?:de\s+)?(.+?)(?:\s+en\s+|\s+PE\b|\s+budget|\s+presupuesto|$)",
        r"(?:items?|productos?)\s*[:=]\s*(.+)$",
    ):
        mm = re.search(pat, text, re.I)
        if mm:
            chunk = mm.group(1)
            parts = [p.strip() for p in _ITEM_SPLIT.split(chunk) if p.strip()]
            for p in parts:
                p = re.sub(r"\b(PE|AR|MX|BR|CO|CL)\b", "", p, flags=re.I).strip(" .")
                if len(p) >= 2 and not p.isdigit():
                    items.append({"name": p, "qty": 1})
            break
    if not items and "," in text:
        parts = [p.strip() for p in text.split(",") if p.strip()]
        if len(parts) >= 2:
            for p in parts[:12]:
                p2 = re.sub(r"\b(PE|AR|MX|BR|CO|CL)\b", "", p, flags=re.I).strip()
                p2 = re.sub(r"(budget|presupuesto).*$", "", p2, flags=re.I).strip()
                if 2 <= len(p2) <= 60:
                    items.append({"name": p2, "qty": 1})
    e["items"] = items
    # single product query
    if not items:
        mq = re.search(
            r"(?:compara|compare|busca|search|precio de)\s+(.+)$",
            text,
            re.I,
        )
        if mq:
            e["product_query"] = mq.group(1).strip()[:120]
        else:
            e["product_query"] = text.strip()[:120]
    return e


def classify_intent(raw: str) -> IntentEnvelope:
    text = (raw or "").strip()
    low = text.lower()
    entities = extract_entities(text)
    secondary: list[str] = []
    confidence = 0.7
    risk_flags: list[str] = []

    def has(*words: str) -> bool:
        return any(w in low for w in words)

    primary = "ambiguous"

    if entities.get("ticket_url") or has("ticket", "boleta", "recibo", "ocr"):
        primary = "ticket_audit"
        confidence = 0.9 if entities.get("ticket_url") else 0.65
    elif has("checkout", "agregar al carrito", "add to cart", "mis pedidos", "reordenar", "reorden"):
        primary = "commerce_action"
        confidence = 0.8
        if has("checkout") and not entities.get("confirm"):
            risk_flags.append("checkout_needs_confirm")
    elif has(
        "cómo funciona",
        "como funciona",
        "qué es cli market",
        "que es cli market",
        "demo",
        "plan pro",
        "mcp",
        "api key",
    ):
        primary = "product_help"
        confidence = 0.85
    elif has("scorecard", "frescura del moat", "cobertura de tienda", "store health"):
        primary = "retailer_ops"
        confidence = 0.8
    elif has(
        "inflación",
        "inflacion",
        "affordability",
        "intel",
        "scores",
        "riesgo de precio",
        "price risk",
        "canasta básica",
        "canasta basica",
    ):
        primary = "market_intel"
        confidence = 0.85
    elif has("compro ya", "comprar ya", "forward buy", "procurement", "esperar a comprar", "buy now", "wait"):
        primary = "procurement_timing"
        confidence = 0.85
    elif has("household", "hogar", "favoritos", "alerta de precio", "price alert") and not (
        len(entities.get("items") or []) >= 2
    ):
        primary = "household_prefs"
        confidence = 0.75
    elif len(entities.get("items") or []) >= 2 or has(
        "optimiz", "canasta", "compra semanal", "basket", "tco"
    ):
        primary = "basket_optimize"
        confidence = 0.88 if len(entities.get("items") or []) >= 2 else 0.7
        if has("compro ya", "esperar", "procurement"):
            secondary.append("procurement_timing")
    elif has("compara", "compare", "busca", "search", "precio", "barcode", "ean"):
        primary = "product_search"
        confidence = 0.8
    else:
        primary = "ambiguous"
        confidence = 0.4

    if not entities.get("country"):
        entities["country"] = "PE"
        risk_flags.append("country_defaulted_PE")

    if primary == "basket_optimize" and not entities.get("line"):
        entities["line"] = "supermercados"

    if primary == "ticket_audit" and not entities.get("ticket_url"):
        confidence = min(confidence, 0.5)
        risk_flags.append("missing_ticket_url")

    if confidence < 0.55:
        primary = "ambiguous"

    return IntentEnvelope(
        intent_id=f"intent_{uuid.uuid4().hex[:10]}",
        primary=primary,
        secondary=secondary,
        language="es",
        locale_hint=entities.get("country"),
        entities=entities,
        risk_flags=risk_flags,
        confidence=confidence,
        raw_request=text,
    )


# --- Plan --------------------------------------------------------------------

def _tool(name: str, args: dict[str, Any], required: bool = True, why: str = "", on_error: str = "abort") -> dict:
    return {
        "tool": name,
        "args": args,
        "required": required,
        "on_error": on_error,
        "fallback_tool": None,
        "why": why,
    }


def _agent(agent_id: str, depends: list[str], section: str, group: int, slice_keys: list[str] | None = None) -> dict:
    meta = AGENT_CATALOG[agent_id]
    return {
        "id": agent_id,
        "role_path": meta["role_path"],
        "context_path": meta["context_path"],
        "depends_on_tools": depends,
        "input_slice": slice_keys or [],
        "output_section": section,
        "parallel_group": group,
    }


def build_plan(intent: IntentEnvelope, mode: str = "standard") -> dict[str, Any]:
    e = intent.entities
    country = e.get("country") or "PE"
    line = e.get("line") or "supermercados"
    days = int(e.get("days") or 30)
    tools: list[dict[str, Any]] = []
    agents: list[dict[str, Any]] = []
    audience = "consumer"
    primary = intent.primary

    if primary == "ambiguous":
        # Sin LLM enrichment: SYNTHESIZE arma la pregunta aclaratoria directo del intent,
        # no hay ToolResults que enriquecer todavía.
        agents = []
        audience = "consumer"
    elif primary == "product_help":
        tools = [_tool("market_discover", {"country": country}, required=False, why="Cobertura", on_error="continue")]
        # Sin LLM enrichment: explicar capacidades/tiers no es enriquecimiento de datos,
        # SYNTHESIZE responde con la data cruda de market_discover + copy estático.
        agents = []
        audience = "developer"
    elif primary == "product_search":
        q = e.get("product_query") or (e["items"][0]["name"] if e.get("items") else intent.raw_request)
        tools = [
            _tool(
                "market_compare",
                {"query": q, "line": line, "country": country, "limit": 10},
                why="Comparación cross-retailer",
                on_error="fallback",
            )
        ]
        tools[0]["fallback_tool"] = "market_search"
        if mode == "deep":
            tools.append(
                _tool(
                    "market_promo_detector",
                    {"product": q},
                    required=False,
                    on_error="continue",
                    why="Autenticidad de descuento (evita citar una promo inflada)",
                )
            )
        agents = [
            _agent("pricing-analyst", ["market_compare", "market_search", "market_promo_detector"], "ranking_and_unit_value", 1),
            _agent("reality-checker", ["market_compare", "market_search"], "caveats", 2),
        ]
    elif primary == "basket_optimize":
        items = e.get("items") or []
        if not items and e.get("product_query"):
            items = [{"name": e["product_query"], "qty": 1}]
        args: dict[str, Any] = {
            "country": country,
            "items": items,
            "constraints": {
                **(e.get("constraints") or {}),
            },
            "include_intel": True,
        }
        if e.get("budget") is not None:
            args["constraints"]["max_budget"] = e["budget"]
        if e.get("segment"):
            args["context"] = {"segment": e["segment"], "use_case": e.get("use_case")}
        tools = [
            _tool("market_optimize_purchase", args, why="TCO + substitutes + intel en un call"),
        ]
        if "procurement_timing" in intent.secondary or mode == "deep":
            tools.append(
                _tool(
                    "market_procurement_signal",
                    {"country": country, "line": line},
                    required=False,
                    why="Timing de compra",
                    on_error="continue",
                )
            )
        agents = [
            _agent("pricing-analyst", ["market_optimize_purchase"], "ranking_and_unit_value", 1),
            _agent("operations", ["market_optimize_purchase"], "execution_plan", 1),
        ]
        if e.get("segment") == "hotelero":
            agents.append(_agent("hospitality", ["market_optimize_purchase"], "segment_fit", 1))
        if e.get("segment") or mode == "deep":
            agents.append(_agent("supply-chain", ["market_optimize_purchase", "market_procurement_signal"], "timing", 1))
        agents.append(_agent("reality-checker", ["market_optimize_purchase"], "caveats", 2))
        audience = "procurement" if e.get("segment") else "consumer"
    elif primary == "procurement_timing":
        tools = [
            _tool("market_procurement_signal", {"country": country, "line": line}, why="buy_now/monitor/wait"),
            _tool("market_price_risk", {"country": country, "line": line, "days": min(days, 14)}, required=False, on_error="continue", why="Volatilidad"),
            _tool("market_intel_brief", {"country": country, "line": line, "days": days}, required=False, on_error="continue", why="Contexto"),
        ]
        agents = [
            _agent("supply-chain", ["market_procurement_signal", "market_price_risk"], "timing", 1),
            _agent("reality-checker", ["market_procurement_signal"], "caveats", 2),
        ]
        audience = "procurement"
    elif primary == "market_intel":
        tools = [
            _tool("market_intel_brief", {"country": country, "line": line, "days": days}, why="Narrativa intel one-call"),
            _tool("market_inflation_report", {"country": country, "line": line, "days": days}, required=False, on_error="continue", why="Presión inflación"),
            _tool("market_scores", {"country": country, "line": line}, required=False, on_error="continue", why="Scores compuestos"),
            _tool(
                "market_informal_signal",
                {"country": country, "line": line},
                required=False,
                on_error="continue",
                why="Honestidad de cobertura formal (NUNCA usar para afirmar % de mercado informal)",
            ),
        ]
        agents = [
            _agent("analytics-reporter", ["market_intel_brief", "market_inflation_report", "market_scores", "market_informal_signal"], "intel_report", 1),
            _agent("reality-checker", ["market_intel_brief", "market_stats"], "caveats", 2),
        ]
        audience = "executive"
        # Nota: modo "deep" ya no agrega un agente aparte (document-generator) --
        # el modo deep de SYNTHESIZE cubre el detalle extra sin una llamada LLM redundante.
    elif primary == "retailer_ops":
        store = e.get("store")
        tools = [_tool("market_discover", {"country": country, "line": line}, why="Listar tiendas")]
        if store:
            tools.append(_tool("market_retailer_scorecard", {"store": store, "days": days}, why="Scorecard"))
        tools.append(_tool("market_stats", {}, required=False, on_error="continue", why="Salud del moat"))
        agents = [
            _agent("analytics-reporter", ["market_retailer_scorecard", "market_stats", "market_discover"], "ops_report", 1),
            _agent("reality-checker", ["market_retailer_scorecard", "market_stats"], "caveats", 1),
        ]
        audience = "developer"
    elif primary == "ticket_audit":
        tools = [
            _tool(
                "market_ticket",
                {"url": e.get("ticket_url"), "country": country},
                why="OCR vs moat",
            )
        ]
        agents = [
            _agent("pricing-analyst", ["market_ticket"], "overpay_ranking", 1),
            _agent("reality-checker", ["market_ticket"], "caveats", 2),
        ]
        audience = "consumer"
    elif primary == "household_prefs":
        tools = [_tool("market_household_get", {}, required=False, on_error="continue", why="Perfil hogar")]
        # behavioral-nudge/bookkeeper/support-responder cortados: pricing-analyst ya sabe
        # leer contexto de hogar/presupuesto (household_prefs pairs_with market_optimize_purchase
        # en el catálogo de tools) y reality-checker audita cualquier regla inventada.
        agents = [
            _agent("pricing-analyst", ["market_household_get"], "budget_guidance", 1),
            _agent("reality-checker", ["market_household_get"], "caveats", 2),
        ]
    elif primary == "commerce_action":
        tools = [
            _tool("market_whoami", {}, required=False, on_error="continue", why="Sesión"),
            _tool("market_cart", {}, required=False, on_error="continue", why="Carrito actual"),
        ]
        if e.get("confirm") and "checkout" in intent.raw_request.lower():
            # Explicit only — still not auto-charging in this sketch without payment_method wiring
            risk_flags_note = "checkout_planned_not_auto_executed"
            intent.risk_flags.append(risk_flags_note)
        # support-responder cortado: la confirmación de carrito/checkout es texto
        # determinista a partir de ToolResults, no necesita una llamada LLM aparte.
        agents = [
            _agent("reality-checker", ["market_cart"], "caveats", 1),
        ]
        audience = "consumer"
    else:
        agents = []

    # mode caps — always keep reality-checker if present when truncating
    max_agents = {"fast": 2, "standard": 4, "deep": 6}.get(mode, 4)
    if len(agents) > max_agents:
        must = [a for a in agents if a["id"] == "reality-checker"]
        rest = [a for a in agents if a["id"] != "reality-checker"]
        keep_rest = max_agents - len(must)
        agents = rest[: max(0, keep_rest)] + must
        agents = agents[:max_agents]
    max_tools = {"fast": 2, "standard": 4, "deep": 6}.get(mode, 4)
    tools = tools[:max_tools]

    return {
        "plan_id": f"plan_{uuid.uuid4().hex[:10]}",
        "intent": asdict(intent),
        "mode": mode,
        "tools": tools,
        "agents": agents,
        "response_spec": {
            "format": "markdown",
            "sections": [
                "summary",
                "facts",
                "enrichment",
                "recommendation",
                "caveats",
                "next_actions",
            ],
            "max_bullets_summary": 5,
            "language": intent.language,
            "audience": audience,
        },
        "guards": {
            "max_tools": max_tools,
            "max_agents": max_agents,
            "forbid_checkout_without_confirm": True,
            "require_country": True,
        },
        "meta": {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "orchestrator_version": ORCH_VERSION,
            "contract": str(CONTRACT.relative_to(PROJECT_ROOT)) if CONTRACT.exists() else "orchestrator-contract.md",
        },
    }


# --- Execute tools -----------------------------------------------------------

def _session_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "User-Agent": f"cli-market-orchestrator/{ORCH_VERSION}",
    }
    # Prefer env key, then ~/.market/session.json (CLI session uses "token")
    api_key = os.getenv("MARKET_API_KEY") or os.getenv("CLI_MARKET_API_KEY")
    session_path = Path.home() / ".market" / "session.json"
    token = api_key
    if session_path.is_file():
        try:
            sess = json.loads(session_path.read_text(encoding="utf-8"))
            token = (
                api_key
                or sess.get("access_token")
                or sess.get("token")
                or sess.get("api_key")
            )
        except Exception:
            pass
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _format_path(path: str, args: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    """Substitute {var} path params; return remaining args for query/body."""
    remaining = dict(args)
    for key in list(remaining.keys()):
        placeholder = "{" + key + "}"
        if placeholder in path:
            path = path.replace(placeholder, str(remaining.pop(key)))
    return path, remaining


def _normalize_tool_args(tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
    """Shape args for real API bodies (optimize → basket-compatible, etc.)."""
    a = {k: v for k, v in (args or {}).items() if v is not None}
    if tool_name == "market_optimize_purchase":
        # missions/optimize-purchase accepts items + country + optional constraints/context
        out: dict[str, Any] = {
            "items": a.get("items") or [],
            "country": a.get("country") or "PE",
        }
        if a.get("constraints"):
            out["constraints"] = a["constraints"]
        if a.get("context"):
            out["context"] = a["context"]
        if a.get("include_intel") is not None:
            out["include_intel"] = a["include_intel"]
        # basket/compare fallback shape
        out["stores"] = a.get("stores")
        return out
    if tool_name == "market_basket":
        return {"items": a.get("items") or [], "stores": a.get("stores"), "country": a.get("country")}
    if tool_name == "market_ask":
        return {"prompt": a.get("prompt") or a.get("query") or ""}
    if tool_name == "market_substitutes":
        return {
            "query": a.get("query") or a.get("product_query"),
            "country": a.get("country") or "PE",
            "store": a.get("store"),
            "limit": a.get("limit", 3),
        }
    if tool_name == "market_ticket":
        return {"url": a.get("url") or a.get("ticket_url"), "country": a.get("country")}
    if tool_name == "market_retailer_scorecard":
        return {"store": a.get("store"), "days": a.get("days", 30)}
    if tool_name == "market_price_history":
        # Verificado 2026-07-15/16 en vivo contra producción: el historial está atado a
        # producto+tienda, no solo al producto. Pasar solo product_id devuelve resultados
        # sin filtrar por tienda (ruidoso/engañoso), no un error -- así que se mantiene
        # explícito acá en vez de caer al passthrough genérico de abajo.
        return {k: v for k, v in {
            "product_id": a.get("product_id"),
            "store": a.get("store"),
            "limit": a.get("limit", 50),
        }.items() if v is not None}
    return a


def _http_call(
    method: str,
    path: str,
    args: dict[str, Any],
    *,
    timeout: float,
) -> tuple[int | None, Any, str | None, int]:
    """Low-level HTTP. Returns status, data, error, latency_ms."""
    started = datetime.now(timezone.utc)
    if httpx is None:
        return None, None, "httpx_not_installed", 0
    path, remaining = _format_path(path, args)
    url = f"{API_URL}{path}"
    try:
        with httpx.Client(timeout=timeout, headers=_session_headers()) as client:
            if method.upper() == "GET":
                r = client.get(url, params=remaining)
            elif method.upper() == "DELETE":
                r = client.delete(url, params=remaining)
            else:
                r = client.request(method.upper(), url, json=remaining)
        latency = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)
        try:
            data = r.json()
        except Exception:
            data = {"raw_text": (r.text or "")[:4000]}
        err = None if 200 <= r.status_code < 300 else f"http_{r.status_code}"
        return r.status_code, data, err, latency
    except Exception as exc:
        latency = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)
        return None, None, str(exc), latency


def _execute_discover(args: dict[str, Any], timeout: float) -> dict[str, Any]:
    """Compose /lines + /stores + /countries like market_mcp._discover_api.

    Verificado 2026-07-15/16 en vivo: GET /stores?country=PE SI filtra correctamente
    (9 tiendas PE, no las 26 de 10 paises) -- el bug de "country no filtra" que existe
    en la tool MCP market_discover esta aislado al wrapper de esa tool (agrupa por linea
    sin re-filtrar por pais), no al endpoint REST subyacente que se usa aca. No requiere
    fix en esta funcion.
    """
    started = datetime.now(timezone.utc)
    store_params = {}
    if args.get("country"):
        store_params["country"] = args["country"]
    if args.get("line"):
        store_params["line"] = args["line"]
    status_l, lines, err_l, _ = _http_call("GET", "/lines", {}, timeout=timeout)
    status_s, stores, err_s, _ = _http_call("GET", "/stores", store_params, timeout=timeout)
    status_c, countries, err_c, _ = _http_call("GET", "/countries", {}, timeout=timeout)
    latency = int((datetime.now(timezone.utc) - started).total_seconds() * 1000)
    ok = all(s and 200 <= s < 300 for s in (status_l, status_s, status_c))
    return {
        "tool": "market_discover",
        "ok": ok,
        "status_code": status_s or status_l,
        "latency_ms": latency,
        "args": args,
        "data": {"lines": lines, "stores": stores, "countries": countries} if ok else {
            "lines": lines, "stores": stores, "countries": countries,
            "errors": [e for e in (err_l, err_s, err_c) if e],
        },
        "error": None if ok else "discover_compose_partial_or_failed",
        "truncated": False,
        "confidence_notes": [],
    }


def execute_tool(tool_name: str, args: dict[str, Any], timeout: float = 60.0) -> dict[str, Any]:
    clean_args = _normalize_tool_args(tool_name, args)
    if tool_name == "market_discover":
        return _execute_discover(clean_args, timeout)

    spec = TOOL_HTTP.get(tool_name)
    if not spec:
        return {
            "tool": tool_name,
            "ok": False,
            "status_code": None,
            "latency_ms": 0,
            "args": clean_args,
            "data": None,
            "error": f"tool_not_wired:{tool_name}",
            "truncated": False,
            "confidence_notes": ["Map tool in TOOL_HTTP or call via MCP."],
        }

    method = spec["method"]
    path = spec["path"]
    status, data, err, latency = _http_call(method, path, clean_args, timeout=timeout)

    # Built-in fallback (e.g. optimize-purchase → basket/compare)
    if err and spec.get("fallback"):
        fb = spec["fallback"]
        fb_args = clean_args
        if tool_name == "market_optimize_purchase":
            fb_args = {
                "items": clean_args.get("items") or [],
                "stores": clean_args.get("stores"),
            }
            # basket/compare may not take country in body — stores filter is enough
        status2, data2, err2, latency2 = _http_call(
            fb["method"], fb["path"], fb_args, timeout=timeout
        )
        return {
            "tool": tool_name,
            "ok": err2 is None,
            "status_code": status2,
            "latency_ms": latency + latency2,
            "args": clean_args,
            "data": data2,
            "error": err2,
            "truncated": False,
            "confidence_notes": [
                f"primary {path} failed ({err}); used fallback {fb['path']}"
            ],
        }

    return {
        "tool": tool_name,
        "ok": err is None,
        "status_code": status,
        "latency_ms": latency,
        "args": clean_args,
        "data": data,
        "error": err,
        "truncated": False,
        "confidence_notes": [],
    }


def execute_plan_tools(plan: dict[str, Any]) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for step in plan.get("tools") or []:
        name = step["tool"]
        args = step.get("args") or {}
        res = execute_tool(name, args)
        results.append(res)
        if not res["ok"] and step.get("required") and step.get("on_error") == "abort":
            fb = step.get("fallback_tool")
            if fb:
                # Adapt args for search fallback from compare
                fb_args = dict(args)
                if fb == "market_search" and "query" not in fb_args and args.get("query"):
                    pass
                if fb == "market_search" and plan.get("intent", {}).get("entities", {}).get("product_query"):
                    fb_args.setdefault(
                        "query",
                        plan["intent"]["entities"]["product_query"],
                    )
                fb_res = execute_tool(fb, fb_args)
                results.append(fb_res)
                if not fb_res["ok"]:
                    break
            else:
                break
        if not res["ok"] and step.get("on_error") == "fallback" and step.get("fallback_tool"):
            fb_args = dict(args)
            if step["fallback_tool"] == "market_search":
                fb_args.setdefault("query", args.get("query") or plan.get("intent", {}).get("entities", {}).get("product_query"))
            results.append(execute_tool(step["fallback_tool"], fb_args))
    return results


# --- Enrich prompts ----------------------------------------------------------

def _read_optional(path: str | Path, limit: int = 12000) -> str:
    p = Path(path)
    if not p.is_file():
        return f"(missing file: {p})"
    text = p.read_text(encoding="utf-8", errors="replace")
    return text[:limit]


def prepare_enrichment_prompts(plan: dict[str, Any], tool_results: list[dict[str, Any]]) -> list[Path]:
    GENERATED.mkdir(parents=True, exist_ok=True)
    prompts_dir = GENERATED / "prompts"
    prompts_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    intent = plan.get("intent") or {}
    by_tool = {r["tool"]: r for r in tool_results}
    full_facts = extract_fact_index(tool_results)

    for agent in plan.get("agents") or []:
        aid = agent["id"]
        deps = agent.get("depends_on_tools") or []
        slice_data = {t: by_tool.get(t) for t in deps if t in by_tool}
        if not slice_data:
            slice_data = {r["tool"]: r for r in tool_results}
        scoped = [by_tool[t] for t in deps if t in by_tool] or tool_results
        fact_index = extract_fact_index(scoped) if deps else full_facts

        role_file = AGENCY_ROOT / agent["role_path"]
        context_file = Path(agent["context_path"])
        body = f"""# Enrichment task — {aid}

## Orchestrator meta
- plan_id: {plan.get("plan_id")}
- intent.primary: {intent.get("primary")}
- output_section: {agent.get("output_section")}
- orchestrator_version: {ORCH_VERSION}

## Rules (grounded)
1. Use ONLY facts in FactIndex + ToolResults below.
2. Do not invent prices, stock, delivery, canasta, IPC, or stores not listed.
3. Every number must appear in FactIndex.allowed_number_literals or raw ToolResults.
4. Cite tool names: (source: market_compare).
5. Output markdown for section `{agent.get("output_section")}`.
6. End with `warnings:` and `grounding_notes:`.

## Role (agency-agents)
{_read_optional(role_file)}

## CLI Market context
{_read_optional(context_file)}

## IntentEnvelope
```json
{json.dumps(intent, ensure_ascii=False, indent=2)}
```

## FactIndex
```json
{json.dumps(fact_index, ensure_ascii=False, indent=2)[:50000]}
```

## ToolResults (assigned)
```json
{json.dumps(slice_data, ensure_ascii=False, indent=2)[:100000]}
```
"""
        out = prompts_dir / f"prompt-{aid}.md"
        out.write_text(body, encoding="utf-8")
        written.append(out)
    return written


# --- LLM enrichment ----------------------------------------------------------

def _llm_config() -> dict[str, Any]:
    """Resolve provider/model/key from env.

    Supported providers:
      - openai (default if OPENAI_API_KEY)
      - anthropic
      - xai / grok (OpenAI-compatible)
      - ollama (local OpenAI-compatible)
      - none
    """
    provider = (os.getenv("ORCHESTRATOR_LLM_PROVIDER") or "").strip().lower()
    model = os.getenv("ORCHESTRATOR_LLM_MODEL", "").strip()
    key = (
        os.getenv("ORCHESTRATOR_LLM_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or os.getenv("ANTHROPIC_API_KEY")
        or os.getenv("XAI_API_KEY")
        or os.getenv("GROK_API_KEY")
        or ""
    )
    base = os.getenv("ORCHESTRATOR_LLM_BASE_URL", "").strip()

    if not provider:
        if os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
            provider = "anthropic"
        elif os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY"):
            provider = "xai"
        elif os.getenv("OPENAI_API_KEY") or os.getenv("ORCHESTRATOR_LLM_API_KEY"):
            provider = "openai"
        elif os.getenv("ORCHESTRATOR_LLM_BASE_URL"):
            provider = "ollama"
        else:
            provider = "none"

    if not model:
        model = {
            "openai": "gpt-4o-mini",
            "anthropic": "claude-3-5-haiku-latest",
            "xai": "grok-2-latest",
            "ollama": "llama3.2",
            "none": "",
        }.get(provider, "gpt-4o-mini")

    if not base:
        base = {
            "openai": "https://api.openai.com/v1",
            "xai": "https://api.x.ai/v1",
            "ollama": "http://127.0.0.1:11434/v1",
            "anthropic": "https://api.anthropic.com",
        }.get(provider, "https://api.openai.com/v1")

    return {
        "provider": provider,
        "model": model,
        "api_key": key,
        "base_url": base.rstrip("/"),
        "temperature": float(os.getenv("ORCHESTRATOR_LLM_TEMPERATURE", "0.2")),
        "max_tokens": int(os.getenv("ORCHESTRATOR_LLM_MAX_TOKENS", "1800")),
    }


def _truncate_json(obj: Any, max_chars: int = 14000) -> str:
    raw = json.dumps(obj, ensure_ascii=False, default=str)
    if len(raw) <= max_chars:
        return raw
    return raw[: max_chars - 20] + "\n…[truncated]…"


# Keys that usually carry citeable product/price/store facts
_FACT_NAME_KEYS = frozenset(
    {
        "name", "product", "product_name", "title", "query", "brand",
        "store", "store_key", "store_name", "retailer",
        "signal", "action", "pressure", "recommendation", "status",
        "country", "line", "currency", "tier",
    }
)
_FACT_NUM_KEYS = frozenset(
    {
        "price", "unit_price", "total", "qty", "quantity", "limit",
        "delta_pct", "avg_inflation_pct", "inflation_pct", "threshold_pct",
        "score", "confidence", "days", "count", "total_products",
        "first_price", "last_price", "coverage", "freshness",
    }
)


def _walk_facts(node: Any, path: str, out: dict[str, list[Any]], *, depth: int = 0) -> None:
    if depth > 8:
        return
    if isinstance(node, dict):
        for k, v in node.items():
            p = f"{path}.{k}" if path else str(k)
            kl = str(k).lower()
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                if kl in _FACT_NUM_KEYS or any(x in kl for x in ("price", "pct", "total", "score", "delta")):
                    out.setdefault("numbers", []).append({"path": p, "value": v})
            elif isinstance(v, str) and v.strip():
                if kl in _FACT_NAME_KEYS or kl.endswith("_name") or kl.endswith("_key"):
                    out.setdefault("labels", []).append({"path": p, "value": v[:200]})
                elif kl in ("product_id", "id", "barcode", "sku") and len(v) < 80:
                    out.setdefault("ids", []).append({"path": p, "value": v})
            _walk_facts(v, p, out, depth=depth + 1)
    elif isinstance(node, list):
        for i, item in enumerate(node[:40]):
            _walk_facts(item, f"{path}[{i}]", out, depth=depth + 1)


def extract_fact_index(tool_results: list[dict[str, Any]] | dict[str, Any]) -> dict[str, Any]:
    """Build an allowlist of citeable facts from ToolResults (anti-hallucination)."""
    if isinstance(tool_results, dict):
        # either {tool: result} or {"results": [...]}
        if "results" in tool_results and isinstance(tool_results["results"], list):
            items = tool_results["results"]
        else:
            items = [
                ({"tool": k, **v} if isinstance(v, dict) and "tool" not in v else v)
                for k, v in tool_results.items()
            ]
    else:
        items = tool_results

    by_tool: dict[str, Any] = {}
    all_numbers: list[Any] = []
    all_labels: list[Any] = []
    all_ids: list[Any] = []
    product_rows: list[dict[str, Any]] = []

    for r in items:
        if not isinstance(r, dict):
            continue
        tool = r.get("tool") or "unknown"
        if not r.get("ok", True) and r.get("data") is None:
            by_tool[tool] = {"ok": False, "error": r.get("error")}
            continue
        data = r.get("data")
        bucket: dict[str, list[Any]] = {"numbers": [], "labels": [], "ids": []}
        _walk_facts(data, "", bucket)
        # Dedup roughly
        for key in ("numbers", "labels", "ids"):
            seen: set[str] = set()
            uniq = []
            for item in bucket[key]:
                sig = f"{item['path']}={item['value']}"
                if sig in seen:
                    continue
                seen.add(sig)
                uniq.append(item)
            bucket[key] = uniq[:80]
        by_tool[tool] = {
            "ok": r.get("ok", True),
            "status_code": r.get("status_code"),
            "top_level_keys": list(data.keys()) if isinstance(data, dict) else type(data).__name__,
            "numbers": bucket["numbers"][:40],
            "labels": bucket["labels"][:40],
            "ids": bucket["ids"][:40],
        }
        all_numbers.extend(bucket["numbers"])
        all_labels.extend(bucket["labels"])
        all_ids.extend(bucket["ids"])

        # Compact product-like rows if present
        candidates = []
        if isinstance(data, dict):
            for k in ("results", "products", "items", "comparison", "matches"):
                if isinstance(data.get(k), list):
                    candidates = data[k]
                    break
                if isinstance(data.get(k), dict):
                    # basket comparison store → info
                    for sk, info in list(data[k].items())[:15]:
                        if isinstance(info, dict):
                            product_rows.append({
                                "tool": tool,
                                "store": info.get("store_name") or info.get("store") or sk,
                                "total": info.get("total"),
                                "currency": info.get("currency"),
                                "items": len(info.get("items") or []),
                            })
        for row in candidates[:20]:
            if not isinstance(row, dict):
                continue
            product_rows.append({
                "tool": tool,
                "name": row.get("name") or row.get("product") or row.get("title"),
                "price": row.get("price") or row.get("unit_price"),
                "store": row.get("store_name") or row.get("store") or row.get("store_key"),
                "brand": row.get("brand"),
                "product_id": row.get("product_id") or row.get("id"),
            })

    # Numeric allowlist for validators (string forms)
    number_values: set[str] = {
        str(n["value"]) for n in all_numbers if isinstance(n.get("value"), (int, float))
    }
    label_values = sorted({
        str(l["value"]).strip() for l in all_labels if str(l.get("value", "")).strip()
    })[:120]
    # Numbers embedded in product names (e.g. "120 g", "1L", "180g") are citeable
    for lab in label_values:
        for m in re.findall(r"\d+(?:[.,]\d+)?", lab):
            number_values.add(m)
            number_values.add(m.replace(",", "."))
    for row in product_rows:
        for field in ("name", "price", "total"):
            val = row.get(field)
            if val is None:
                continue
            if isinstance(val, (int, float)):
                number_values.add(str(val))
            else:
                for m in re.findall(r"\d+(?:[.,]\d+)?", str(val)):
                    number_values.add(m)
                    number_values.add(m.replace(",", "."))

    return {
        "tools": by_tool,
        "product_rows": product_rows[:30],
        "allowed_number_literals": sorted(number_values)[:150],
        "allowed_label_literals": label_values,
        "rules": [
            "Only cite prices/names/stores/signals present in tools.* or product_rows.",
            "If a figure is not in allowed_number_literals, do not invent it.",
            "If query intent mismatches product_rows names, say so explicitly.",
            "Never invent canasta/IPC/salario tables unless those keys exist in ToolResults.",
        ],
    }


def _numeric_literals_in_text(text: str) -> list[str]:
    # prices like 1.70, 12, 3.56, -3.56, 4.2
    return re.findall(r"(?<![A-Za-z_/])-?\d+(?:[.,]\d+)?%?(?![A-Za-z])", text or "")


def validate_enrichment_against_facts(markdown: str, fact_index: dict[str, Any]) -> list[str]:
    """Heuristic: flag numbers in prose that never appear in ToolResults fact index."""
    allowed = set(fact_index.get("allowed_number_literals") or [])
    # also allow integers as float forms
    expanded: set[str] = set()
    for a in allowed:
        expanded.add(a)
        expanded.add(a.replace(".", ","))
        try:
            f = float(a)
            expanded.add(str(f))
            if f == int(f):
                expanded.add(str(int(f)))
        except ValueError:
            pass
    # Always-ok structural numbers (counts of bullets, ranks 1-10, confidence 0-1 style may still flag)
    soft_ok = {str(i) for i in range(0, 31)}
    soft_ok.update({"100", "24", "7", "30", "60", "90"})

    suspects: list[str] = []
    for lit in _numeric_literals_in_text(markdown):
        norm = lit.rstrip("%").replace(",", ".")
        if lit in expanded or norm in expanded:
            continue
        if norm in soft_ok or lit in soft_ok:
            continue
        # percentage points / ranks often ok if small
        try:
            v = float(norm)
            if 0 <= v <= 20 and "." not in norm and v == int(v):
                continue
        except ValueError:
            pass
        suspects.append(lit)
    # unique preserve order
    seen: set[str] = set()
    out: list[str] = []
    for s in suspects:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out[:25]


def _llm_chat_openai_compat(
    *,
    base_url: str,
    api_key: str,
    model: str,
    system: str,
    user: str,
    temperature: float,
    max_tokens: int,
    timeout: float = 120.0,
) -> str:
    if httpx is None:
        raise RuntimeError("httpx_not_installed")
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    payload = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    }
    url = f"{base_url}/chat/completions"
    with httpx.Client(timeout=timeout, headers=headers) as client:
        r = client.post(url, json=payload)
    if r.status_code >= 400:
        raise RuntimeError(f"llm_http_{r.status_code}: {(r.text or '')[:500]}")
    data = r.json()
    return data["choices"][0]["message"]["content"]


def _llm_chat_anthropic(
    *,
    api_key: str,
    model: str,
    system: str,
    user: str,
    temperature: float,
    max_tokens: int,
    timeout: float = 120.0,
) -> str:
    if httpx is None:
        raise RuntimeError("httpx_not_installed")
    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "system": system,
        "messages": [{"role": "user", "content": user}],
    }
    with httpx.Client(timeout=timeout, headers=headers) as client:
        r = client.post("https://api.anthropic.com/v1/messages", json=payload)
    if r.status_code >= 400:
        raise RuntimeError(f"llm_http_{r.status_code}: {(r.text or '')[:500]}")
    data = r.json()
    parts = data.get("content") or []
    texts = [p.get("text", "") for p in parts if p.get("type") == "text"]
    return "\n".join(texts).strip()


def llm_complete(system: str, user: str, cfg: dict[str, Any] | None = None) -> str:
    cfg = cfg or _llm_config()
    provider = cfg["provider"]
    if provider == "none":
        raise RuntimeError(
            "No LLM configured. Set OPENAI_API_KEY or ORCHESTRATOR_LLM_PROVIDER=ollama"
        )
    if provider == "anthropic":
        return _llm_chat_anthropic(
            api_key=cfg["api_key"],
            model=cfg["model"],
            system=system,
            user=user,
            temperature=cfg["temperature"],
            max_tokens=cfg["max_tokens"],
        )
    # openai / xai / ollama
    return _llm_chat_openai_compat(
        base_url=cfg["base_url"],
        api_key=cfg["api_key"],
        model=cfg["model"],
        system=system,
        user=user,
        temperature=cfg["temperature"],
        max_tokens=cfg["max_tokens"],
    )


_GROUNDED_RULES = """
## Grounding (OBLIGATORIO — anti-alucinación)

1. SOLO podés usar hechos del bloque FactIndex y ToolResults del user message.
2. PROHIBIDO inventar: tablas de canasta, IPC, salario mínimo, stock, delivery, Nutri-Score, spreads, o tiendas que no estén en FactIndex.product_rows / labels.
3. Cada cifra (precio, %, total) debe aparecer en FactIndex.allowed_number_literals O en ToolResults JSON. Si no está, escribí "dato no presente en tools".
4. Cada nombre de producto/tienda citado debe estar en FactIndex.product_rows o allowed_label_literals.
5. Si el query del usuario no matchea bien los product_rows (ej. pidió "leche" y vinieron yogures), decilo explícitamente en warnings.
6. Formato de cita inline: `(source: market_compare)` o `(source: market_intel_brief)`.
7. No rellenes con conocimiento general del modelo sobre precios de Perú u otros países.
8. Preferí tablas cortas copiando SOLO filas de product_rows / campos reales del JSON.
9. Terminá SIEMPRE con:

```
warnings:
- ...
grounding_notes:
- facts_used: N
- unknowns: ...
```
"""


def _agent_system_prompt(agent: dict[str, Any]) -> str:
    role = _read_optional(AGENCY_ROOT / agent["role_path"], limit=6000)
    context = _read_optional(agent["context_path"], limit=3000)
    extra = ""
    if agent["id"] == "reality-checker":
        extra = """
## Rol especial Reality Checker
Recibís drafts de otros agentes. Tu trabajo es:
- Listar claims no soportados por FactIndex/ToolResults
- Marcar números inventados
- Confirmar o rechazar match query↔productos
- NO reescribas el análisis completo; emití hallazgos y severity (low/med/high)
"""
    return f"""Sos el sub-agente `{agent['id']}` del pipeline CLI Market Orchestrator.
Sección a producir: {agent.get('output_section')}
Respondé en español LATAM, markdown compacto.

{_GROUNDED_RULES}
{extra}

## Role card
{role}

## CLI Market context
{context}
"""


def _enricher_user_message(
    *,
    agent: dict[str, Any],
    intent: dict[str, Any],
    slice_data: dict[str, Any],
    fact_index: dict[str, Any],
    peer_drafts: dict[str, str] | None = None,
) -> str:
    parts = [
        f"## Intent\n```json\n{_truncate_json(intent, 3500)}\n```\n",
        f"## FactIndex (allowlist — SOLO citá de aquí + ToolResults)\n```json\n{_truncate_json(fact_index, 8000)}\n```\n",
        f"## ToolResults\n```json\n{_truncate_json(slice_data, 12000)}\n```\n",
    ]
    if peer_drafts and agent["id"] == "reality-checker":
        drafts_txt = "\n\n".join(
            f"### draft:{aid}\n{md[:4000]}" for aid, md in peer_drafts.items() if aid != "reality-checker"
        )
        parts.append(f"## Drafts de otros agentes (para auditar)\n{drafts_txt}\n")
        parts.append(
            "Auditar drafts vs FactIndex. Listá unsupported_claims, invented_numbers, query_mismatch.\n"
        )
    else:
        parts.append(
            f"Producí la sección `{agent.get('output_section')}`. "
            "Si falta un dato, decí que no está en tools — no inventes.\n"
        )
    return "\n".join(parts)


def run_enrichers(
    plan: dict[str, Any],
    tool_results: list[dict[str, Any]],
    *,
    use_llm: bool = True,
) -> dict[str, str]:
    """Run enrichers (LLM). Writes outputs to generated/orchestrator/outputs/."""
    outputs_dir = GENERATED / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)
    prepare_enrichment_prompts(plan, tool_results)

    by_tool = {r["tool"]: r for r in tool_results}
    intent = plan.get("intent") or {}
    fact_index = extract_fact_index(tool_results)
    (GENERATED / "last-fact-index.json").write_text(
        json.dumps(fact_index, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    cfg = _llm_config()
    # Lower temperature for grounded enrichment
    cfg = {**cfg, "temperature": min(float(cfg.get("temperature", 0.2)), 0.15)}
    results: dict[str, str] = {}

    # reality-checker last so it can audit peers
    agents = sorted(
        plan.get("agents") or [],
        key=lambda a: (
            a.get("parallel_group", 1),
            1 if a["id"] == "reality-checker" else 0,
            a["id"],
        ),
    )

    for agent in agents:
        aid = agent["id"]
        deps = agent.get("depends_on_tools") or []
        slice_data = {t: by_tool[t] for t in deps if t in by_tool}
        if not slice_data:
            slice_data = {r["tool"]: r for r in tool_results}

        # Fact index scoped to deps when possible
        scoped_results = [by_tool[t] for t in deps if t in by_tool] or tool_results
        scoped_facts = extract_fact_index(scoped_results)

        user_msg = _enricher_user_message(
            agent=agent,
            intent=intent,
            slice_data=slice_data,
            fact_index=scoped_facts,
            peer_drafts=results if aid == "reality-checker" else None,
        )
        out_path = outputs_dir / f"output-{aid}.md"
        if not use_llm or cfg["provider"] == "none":
            md = (
                f"_(enricher `{aid}` pendiente — sin LLM configurado)_\n\n"
                f"warnings:\n- llm_not_configured\n"
            )
            out_path.write_text(md, encoding="utf-8")
            results[aid] = md
            print(f"  [skip-llm] {aid}")
            continue
        try:
            system = _agent_system_prompt(agent)
            md = llm_complete(system, user_msg, cfg)
            suspects = validate_enrichment_against_facts(md, scoped_facts)
            if suspects and aid != "reality-checker":
                footer = (
                    "\n\n---\n**validator (auto)**\n"
                    f"- possible_ungrounded_numbers: {', '.join(suspects)}\n"
                    "- action: reality-checker / human must verify these literals\n"
                )
                md = md.rstrip() + footer
            elif suspects and aid == "reality-checker":
                # still attach for traceability
                md = md.rstrip() + f"\n\n<!-- validator_suspects: {suspects} -->\n"
            out_path.write_text(md, encoding="utf-8")
            results[aid] = md
            flag = f" suspects={suspects}" if suspects else ""
            print(f"  [llm:{cfg['provider']}/{cfg['model']}] {aid}  ({len(md)} chars){flag}")
        except Exception as exc:
            md = f"_(error en enricher `{aid}`: {exc})_\n\nwarnings:\n- enricher_failed\n"
            out_path.write_text(md, encoding="utf-8")
            results[aid] = md
            print(f"  [llm-error] {aid}: {exc}")
    return results


def run_synthesizer(
    plan: dict[str, Any],
    tool_results: list[dict[str, Any]],
    agent_outputs: dict[str, str],
    *,
    use_llm: bool = True,
) -> str:
    """Optional LLM pass to polish final markdown from assembled facts+enrichment."""
    cfg = _llm_config()
    cfg = {**cfg, "temperature": min(float(cfg.get("temperature", 0.2)), 0.1)}
    base = final_to_markdown(assemble_response(plan, tool_results, agent_outputs))
    if not use_llm or cfg["provider"] == "none":
        return base
    fact_index = extract_fact_index(tool_results)
    orch_ctx = _read_optional(CONTEXTS / "orchestrator-context.md", limit=5000)
    system = f"""{orch_ctx}

{_GROUNDED_RULES}

Sos la fase SYNTHESIZE. Compactá el borrador SIN añadir hechos nuevos.
Si un draft de agente inventó algo, preferí el reality-checker y FactIndex.
Si hay conflicto, quedate con ToolResults.
"""
    user = f"""Sintetizá la respuesta final para el usuario.
Estructura fija: Resumen, Hechos del moat, Análisis, Recomendación, Caveats, Siguientes pasos.
No inventes tablas ni cifras. Si el análisis de un agente no está grounded, omitilo o marcalo.

## FactIndex
```json
{_truncate_json(fact_index, 8000)}
```

## Borrador
{base[:18000]}
"""
    try:
        md = llm_complete(system, user, cfg)
        suspects = validate_enrichment_against_facts(md, fact_index)
        if suspects:
            md += (
                "\n\n---\n**validator (auto)**\n"
                f"- possible_ungrounded_numbers in final: {', '.join(suspects)}\n"
            )
        return md
    except Exception as exc:
        return base + f"\n\n_⚠️ synthesizer_failed: {exc}_\n"


# --- Assemble ----------------------------------------------------------------

def assemble_response(
    plan: dict[str, Any],
    tool_results: list[dict[str, Any]],
    agent_outputs: dict[str, str] | None = None,
) -> dict[str, Any]:
    agent_outputs = agent_outputs or {}
    intent = plan.get("intent") or {}
    primary = intent.get("primary")
    ok_tools = [r for r in tool_results if r.get("ok")]
    fail_tools = [r for r in tool_results if not r.get("ok")]

    summary: list[str] = [
        f"Intent clasificado: **{primary}** (confianza {intent.get('confidence', 0):.2f}).",
        f"Tools ejecutadas OK: {len(ok_tools)}/{len(tool_results)}.",
    ]
    if intent.get("risk_flags"):
        summary.append("Flags: " + ", ".join(intent["risk_flags"]))

    highlights: list[Any] = []
    for r in ok_tools:
        data = r.get("data")
        if isinstance(data, dict):
            # light highlight extraction
            for key in ("signal", "pressure", "action", "recommendation", "summary", "total", "best_store"):
                if key in data:
                    highlights.append({r["tool"]: {key: data[key]}})
                    break

    sections = []
    for agent in plan.get("agents") or []:
        aid = agent["id"]
        md = agent_outputs.get(aid) or agent_outputs.get(f"output-{aid}.md")
        if not md:
            # try file
            p = GENERATED / "outputs" / f"output-{aid}.md"
            if p.is_file():
                md = p.read_text(encoding="utf-8", errors="replace")
        sections.append(
            {
                "agent_id": aid,
                "title": agent.get("output_section"),
                "markdown": md or f"_(pendiente: ejecutar enricher `{aid}` con prompt generado)_",
            }
        )

    caveats = [
        "Los precios provienen del data moat de CLI Market; no reemplazan cotización contractual ni IPC oficial.",
    ]
    if any(f == "country_defaulted_PE" for f in intent.get("risk_flags") or []):
        caveats.append("Country defaulted a PE por no especificarse en el request.")
    for r in fail_tools:
        caveats.append(f"Tool `{r['tool']}` falló: {r.get('error')}.")
    # Surface auto-validator flags from enricher markdown
    for aid, md in (agent_outputs or {}).items():
        if "possible_ungrounded_numbers" in (md or ""):
            caveats.append(
                f"Validator: el enricher `{aid}` puede contener cifras no ancladas al FactIndex; revisar."
            )
        if aid == "reality-checker" and "unsupported_claims" in (md or "").lower():
            caveats.append("Reality-checker reportó claims no soportados — priorizar su sección.")

    # recommendation heuristic
    action = "monitor"
    rationale = "Revisar hechos del moat y secciones de análisis."
    if primary == "ambiguous":
        action = "clarify"
        rationale = "Intent ambiguo: se necesita una pregunta de clarificación antes de tools de compra."
    elif primary == "commerce_action" and "checkout_needs_confirm" in (intent.get("risk_flags") or []):
        action = "clarify"
        rationale = "Checkout requiere confirmación explícita."
    elif primary == "procurement_timing":
        for r in ok_tools:
            d = r.get("data") or {}
            if isinstance(d, dict) and d.get("signal"):
                sig = str(d["signal"]).lower()
                if "buy" in sig:
                    action = "buy_now"
                elif "wait" in sig:
                    action = "wait"
                else:
                    action = "monitor"
                rationale = f"Señal de procurement_signal/tool: {d.get('signal')}"
                break
    elif primary == "basket_optimize" and ok_tools:
        action = "split_stores"
        rationale = "Usar resultado de optimize_purchase (TCO / tiendas) en la sección de pricing y operations."
    elif primary == "product_search" and ok_tools:
        action = "buy_now"
        rationale = "Hay comparación disponible; elegir top pick del pricing-analyst."
    elif fail_tools and not ok_tools:
        action = "monitor"
        rationale = "Sin hechos útiles: reintentar tools o acotar country/line/query."

    next_actions: list[dict[str, Any]] = []
    if primary == "ambiguous":
        next_actions.append(
            {
                "type": "user",
                "label": "Aclarar: ¿comparar un producto, optimizar canasta, o ver inflación?",
                "payload": {},
            }
        )
    elif primary == "basket_optimize":
        next_actions.append({"type": "tool", "label": "Revisar carrito / add SKUs elegidos", "payload": {"tool": "market_add"}})
    elif primary == "product_help":
        next_actions.append({"type": "user", "label": "Registrar API key: market register", "payload": {}})

    final = {
        "response_id": f"resp_{uuid.uuid4().hex[:10]}",
        "plan_id": plan.get("plan_id"),
        "intent_primary": primary,
        "language": intent.get("language") or "es",
        "summary": summary[:5],
        "facts": {"tools_used": [r["tool"] for r in tool_results], "highlights": highlights},
        "enrichment": {"sections": sections},
        "recommendation": {
            "action": action,
            "rationale": rationale,
            "confidence": float(intent.get("confidence") or 0),
        },
        "caveats": caveats,
        "next_actions": next_actions,
        "raw": {
            "intent": intent,
            "plan": {k: plan[k] for k in plan if k != "intent"},
            "tool_results": tool_results,
            "agent_outputs_present": list(agent_outputs.keys()),
        },
    }
    return final


def final_to_markdown(final: dict[str, Any]) -> str:
    lines = ["# Respuesta orquestada — CLI Market", ""]
    lines.append("## Resumen")
    for b in final.get("summary") or []:
        lines.append(f"- {b}")
    lines.append("")
    lines.append("## Hechos del moat")
    lines.append(f"- Tools: {', '.join(final.get('facts', {}).get('tools_used') or [])}")
    for h in final.get("facts", {}).get("highlights") or []:
        lines.append(f"- `{json.dumps(h, ensure_ascii=False)[:200]}`")
    lines.append("")
    lines.append("## Análisis")
    for sec in final.get("enrichment", {}).get("sections") or []:
        lines.append(f"### {sec.get('title')} ({sec.get('agent_id')})")
        lines.append(sec.get("markdown") or "")
        lines.append("")
    rec = final.get("recommendation") or {}
    lines.append("## Recomendación")
    lines.append(f"- **Acción:** `{rec.get('action')}`")
    lines.append(f"- **Por qué:** {rec.get('rationale')}")
    lines.append("")
    lines.append("## Caveats")
    for c in final.get("caveats") or []:
        lines.append(f"- {c}")
    lines.append("")
    lines.append("## Siguientes pasos")
    for n in final.get("next_actions") or []:
        lines.append(f"- [{n.get('type')}] {n.get('label')}")
    lines.append("")
    lines.append(f"_orchestrator {ORCH_VERSION} · plan `{final.get('plan_id')}` · response `{final.get('response_id')}`_")
    return "\n".join(lines)


# --- I/O helpers -------------------------------------------------------------

def _save(name: str, obj: Any) -> Path:
    GENERATED.mkdir(parents=True, exist_ok=True)
    path = GENERATED / name
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_json(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_agent_outputs(outputs_dir: str | Path) -> dict[str, str]:
    d = Path(outputs_dir)
    out: dict[str, str] = {}
    if not d.is_dir():
        return out
    for p in d.glob("output-*.md"):
        # output-pricing-analyst.md → pricing-analyst
        aid = p.stem.replace("output-", "", 1)
        out[aid] = p.read_text(encoding="utf-8", errors="replace")
    return out


# --- CLI ---------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="CLI Market request orchestrator")
    parser.add_argument("request", nargs="?", help="Natural language request")
    parser.add_argument("--plan", action="store_true", help="Only understand+plan")
    parser.add_argument(
        "--run",
        action="store_true",
        help="Full pipeline: plan → tools → LLM enrichers → assemble",
    )
    parser.add_argument("--prepare-enrich", action="store_true", help="Write enrich prompts from plan+tools files")
    parser.add_argument("--enrich", action="store_true", help="Run LLM enrichers from saved plan+tools")
    parser.add_argument("--assemble", action="store_true", help="Assemble FinalResponse from files")
    parser.add_argument("--mode", choices=["fast", "standard", "deep"], default="standard")
    parser.add_argument("--llm", dest="llm", action="store_true", default=None, help="Force LLM enrichers on")
    parser.add_argument("--no-llm", dest="llm", action="store_false", help="Skip LLM (prompts only)")
    parser.add_argument("--synthesize", action="store_true", help="Extra LLM pass to polish final markdown")
    parser.add_argument("--plan-file", type=str, default=str(GENERATED / "last-plan.json"))
    parser.add_argument("--tools-file", type=str, default=str(GENERATED / "last-tools.json"))
    parser.add_argument("--outputs-dir", type=str, default=str(GENERATED / "outputs"))
    parser.add_argument("--out-dir", type=str, default=str(GENERATED))
    args = parser.parse_args(argv)

    # Default: LLM on when a provider/key is available
    use_llm = args.llm if args.llm is not None else (_llm_config()["provider"] != "none")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.prepare_enrich:
        plan = load_json(args.plan_file)
        tools = load_json(args.tools_file)
        if isinstance(tools, dict) and "results" in tools:
            tools = tools["results"]
        paths = prepare_enrichment_prompts(plan, tools)
        print(f"Wrote {len(paths)} prompts → {GENERATED / 'prompts'}")
        for p in paths:
            print(f"  - {p}")
        return 0

    if args.enrich:
        plan = load_json(args.plan_file)
        tools = load_json(args.tools_file)
        if isinstance(tools, dict) and "results" in tools:
            tools = tools["results"]
        print(f"Running enrichers (llm={use_llm})…")
        run_enrichers(plan, tools, use_llm=use_llm)
        return 0

    if args.assemble:
        plan = load_json(args.plan_file)
        tools = load_json(args.tools_file)
        if isinstance(tools, dict) and "results" in tools:
            tools = tools["results"]
        outputs = load_agent_outputs(args.outputs_dir)
        final = assemble_response(plan, tools, outputs)
        md = final_to_markdown(final)
        if args.synthesize and use_llm:
            md = run_synthesizer(plan, tools, outputs, use_llm=True)
            final["synthesized"] = True
        jp = out_dir / "last-response.json" if out_dir == GENERATED else GENERATED / "last-response.json"
        mp = GENERATED / "last-response.md"
        jp.write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")
        mp.write_text(md, encoding="utf-8")
        print(f"Assembled → {jp}")
        print(f"Markdown  → {mp}")
        print(md[:2000])
        return 0

    if not args.request and not (args.plan or args.run):
        parser.print_help()
        print("\nExamples:")
        print('  python ops/market_orchestrator.py --plan "optimiza leche, arroz en PE budget 200"')
        print('  python ops/market_orchestrator.py --run "inflación supermercados PE"')
        print('  python ops/market_orchestrator.py --run --synthesize "compara leche gloria PE"')
        cfg = _llm_config()
        print(f"\nLLM: provider={cfg['provider']} model={cfg['model']} key={'yes' if cfg['api_key'] else 'no'}")
        return 2

    raw = args.request or ""
    intent = classify_intent(raw)
    plan = build_plan(intent, mode=args.mode)
    plan_path = _save("last-plan.json", plan)
    if out_dir.resolve() != GENERATED.resolve():
        (out_dir / "last-plan.json").write_text(plan_path.read_text(encoding="utf-8"), encoding="utf-8")

    print(f"intent.primary = {intent.primary}  confidence={intent.confidence:.2f}")
    print(f"tools          = {[t['tool'] for t in plan['tools']]}")
    print(f"agents         = {[a['id'] for a in plan['agents']]}")
    print(f"plan           → {plan_path}")
    cfg = _llm_config()
    print(f"llm            = {cfg['provider']}/{cfg['model']}  enabled={use_llm}")

    if args.plan and not args.run:
        print(json.dumps({"intent": asdict(intent), "plan_id": plan["plan_id"], "tools": plan["tools"], "agents": plan["agents"]}, ensure_ascii=False, indent=2))
        return 0

    if not args.run:
        return 0

    # 1) Tools
    tool_results = execute_plan_tools(plan)
    tools_path = _save("last-tools.json", {"results": tool_results})
    print(f"tools results  → {tools_path}")
    for r in tool_results:
        flag = "OK" if r["ok"] else "FAIL"
        notes = ("; ".join(r.get("confidence_notes") or []))[:80]
        print(f"  [{flag}] {r['tool']}  {r.get('status_code')}  {r.get('error') or ''}  {notes}")

    # 2) Enrichers (LLM)
    print("enrichers…")
    agent_outputs = run_enrichers(plan, tool_results, use_llm=use_llm)

    # 3) Assemble (+ optional synthesizer)
    final = assemble_response(plan, tool_results, agent_outputs)
    md = final_to_markdown(final)
    if args.synthesize and use_llm:
        print("synthesizer…")
        md = run_synthesizer(plan, tool_results, agent_outputs, use_llm=True)
        final["synthesized"] = True

    jp = GENERATED / "last-response.json"
    mp = GENERATED / "last-response.md"
    jp.write_text(json.dumps(final, ensure_ascii=False, indent=2), encoding="utf-8")
    mp.write_text(md, encoding="utf-8")
    print(f"response       → {mp}")
    print("\n--- markdown preview ---\n")
    print(md[:3000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
