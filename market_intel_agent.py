"""Conversational intelligence agent over the data moat.

A thin, server-side agent that answers natural-language questions about the
price-intelligence data by running a Claude tool-use loop. The model never sees
raw SQL — it can only call a fixed set of typed tools that wrap the existing
data functions (inflation, indicators, prices, dispersion, staple momentum).

Design notes:
  - No new dependency: calls the Anthropic Messages API directly over httpx.
  - Degrades gracefully: if ANTHROPIC_API_KEY is absent, ask_intel() raises a
    503-shaped error so the endpoint can report "agent unavailable".
  - Cost control: model is Haiku by default; the tool loop is capped.
  - The data is internal, so prompt-injection surface is low; even so, tools
    only expose aggregate read queries, never writes or arbitrary SQL.
"""

from __future__ import annotations

import json
import os

import httpx

from data_v1_service import query_dispersion, query_prices
from market_indicators import (
    compute_internal_inflation_avg,
    compute_staple_price_momentum,
    get_latest_values,
)

ANTHROPIC_API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_MODEL = os.getenv("INTEL_AGENT_MODEL", "claude-haiku-4-5")
MAX_TOOL_ITERATIONS = int(os.getenv("INTEL_AGENT_MAX_ITERS", "5"))
MAX_TOKENS = int(os.getenv("INTEL_AGENT_MAX_TOKENS", "1024"))


class AgentUnavailable(RuntimeError):
    """Raised when the agent cannot run (e.g. no API key configured)."""


SYSTEM_PROMPT = (
    "Sos el analista de datos de CLI Market, una plataforma de inteligencia de "
    "precios de retail en LatAm. Respondés preguntas sobre precios, inflación de "
    "góndola, indicadores y dispersión usando EXCLUSIVAMENTE las herramientas "
    "disponibles. Nunca inventes números: si una herramienta devuelve vacío o "
    "null, decilo claramente. Sé conciso y concreto, en español. Cuando cites "
    "inflación, aclará que es inflación observada online y no reemplaza el IPC "
    "oficial. Si la pregunta no se puede responder con los datos, explicá qué "
    "falta."
)

# ── Tool schemas (Anthropic format) ───────────────────────────────────────────

TOOLS = [
    {
        "name": "get_inflation",
        "description": (
            "Inflación promedio observada (delta % de precios) por país y línea "
            "sobre los últimos N días, calculada desde price_history."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "description": "ISO país, ej. PE, AR, CL. Opcional."},
                "line": {"type": "string", "description": "Línea, ej. supermercados, farmacias. Opcional."},
                "days": {"type": "integer", "description": "Ventana en días (default 30)."},
            },
        },
    },
    {
        "name": "get_staple_momentum",
        "description": "Cambio % promedio de precio de los productos de la canasta básica en los últimos N días.",
        "input_schema": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "description": "ISO país. Opcional."},
                "days": {"type": "integer", "description": "Ventana en días (default 7)."},
            },
        },
    },
    {
        "name": "get_indicators",
        "description": "Últimos valores de los indicadores del moat (promo_intensity, moat_freshness, store_coverage, etc.) por país/línea.",
        "input_schema": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "description": "ISO país. Opcional."},
                "line": {"type": "string", "description": "Línea. Opcional."},
                "limit": {"type": "integer", "description": "Máximo de indicadores (default 20)."},
            },
        },
    },
    {
        "name": "get_prices",
        "description": "Snapshots de precios filtrados por país, línea, moneda o tienda. Devuelve productos con precio y tienda.",
        "input_schema": {
            "type": "object",
            "properties": {
                "country": {"type": "string"},
                "line": {"type": "string"},
                "currency": {"type": "string"},
                "store": {"type": "string"},
                "limit": {"type": "integer", "description": "Máximo de filas (default 20)."},
            },
        },
    },
    {
        "name": "get_dispersion",
        "description": "Dispersión de precios (spread entre tiendas) por subcategoría, filtrable por línea y moneda.",
        "input_schema": {
            "type": "object",
            "properties": {
                "line": {"type": "string"},
                "currency": {"type": "string"},
                "limit": {"type": "integer", "description": "Máximo de grupos (default 20)."},
            },
        },
    },
]


# ── Tool dispatch ─────────────────────────────────────────────────────────────

def _dispatch(name: str, args: dict, db) -> dict:
    """Execute a single tool against the live data. Returns a JSON-serializable dict."""
    if name == "get_inflation":
        val = compute_internal_inflation_avg(
            db, args.get("country"), args.get("line"), int(args.get("days", 30) or 30)
        )
        return {
            "avg_inflation_pct": val,
            "country": args.get("country"),
            "line": args.get("line"),
            "days": int(args.get("days", 30) or 30),
            "note": "Inflación observada online; no reemplaza IPC oficial.",
        }
    if name == "get_staple_momentum":
        val = compute_staple_price_momentum(
            db, args.get("country"), int(args.get("days", 7) or 7)
        )
        return {
            "staple_momentum_pct": val,
            "country": args.get("country"),
            "days": int(args.get("days", 7) or 7),
        }
    if name == "get_indicators":
        values = get_latest_values(
            db,
            country=args.get("country"),
            line=args.get("line"),
            limit=int(args.get("limit", 20) or 20),
        )
        return {"count": len(values), "indicators": values}
    if name == "get_prices":
        return query_prices(
            db,
            clean=True,
            country=args.get("country"),
            line=args.get("line"),
            currency=args.get("currency"),
            store=args.get("store"),
            limit=int(args.get("limit", 20) or 20),
        )
    if name == "get_dispersion":
        return query_dispersion(
            db,
            clean=True,
            line=args.get("line"),
            currency=args.get("currency"),
            limit=int(args.get("limit", 20) or 20),
        )
    return {"error": f"unknown tool: {name}"}


# ── Orchestration ─────────────────────────────────────────────────────────────

def ask_intel(question: str, db, *, model: str | None = None) -> dict:
    """Run the tool-use loop and return {answer, tools_used, iterations}.

    Raises AgentUnavailable when ANTHROPIC_API_KEY is not configured.
    """
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise AgentUnavailable("ANTHROPIC_API_KEY not configured")

    model = model or DEFAULT_MODEL
    headers = {
        "x-api-key": api_key,
        "anthropic-version": ANTHROPIC_VERSION,
        "content-type": "application/json",
    }
    messages: list[dict] = [{"role": "user", "content": question}]
    tools_used: list[str] = []

    with httpx.Client(timeout=60.0) as client:
        for _ in range(MAX_TOOL_ITERATIONS):
            payload = {
                "model": model,
                "max_tokens": MAX_TOKENS,
                "system": SYSTEM_PROMPT,
                "tools": TOOLS,
                "messages": messages,
            }
            resp = client.post(ANTHROPIC_API_URL, headers=headers, json=payload)
            if resp.status_code != 200:
                raise AgentUnavailable(f"LLM error {resp.status_code}: {resp.text[:200]}")
            data = resp.json()

            if data.get("stop_reason") == "tool_use":
                messages.append({"role": "assistant", "content": data["content"]})
                tool_results = []
                for block in data["content"]:
                    if block.get("type") == "tool_use":
                        tools_used.append(block["name"])
                        try:
                            result = _dispatch(block["name"], block.get("input", {}), db)
                        except Exception as e:  # tool failure → report to model, don't crash
                            result = {"error": str(e)}
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block["id"],
                            "content": json.dumps(result, ensure_ascii=False, default=str),
                        })
                messages.append({"role": "user", "content": tool_results})
                continue

            # Final assistant turn — extract text
            answer = "".join(
                b.get("text", "") for b in data.get("content", []) if b.get("type") == "text"
            )
            return {
                "answer": answer.strip(),
                "tools_used": tools_used,
                "model": model,
            }

    return {
        "answer": "No pude resolver la consulta dentro del límite de pasos. Probá reformularla.",
        "tools_used": tools_used,
        "model": model,
        "truncated": True,
    }
