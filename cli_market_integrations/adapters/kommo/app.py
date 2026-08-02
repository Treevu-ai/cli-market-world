"""
Kommo CRM + CLI Market Middleware — FastAPI.

Diferencia de protocolo vs HubSpot/Zoho:
  - Webhook de Kommo llega como x-www-form-urlencoded, NO JSON.
  - Payload tiene estructura: leads[add][0][id], leads[update][0][id], etc.
  - FastAPI lee esto con Form() o parseando el body manual.
  - Los campos custom se escriben con field_id, no con nombres.

Endpoints:
  POST /webhook/kommo              Webhook Kommo (form-encoded)
  POST /api/enrich-lead/{id}       Enriquecimiento manual (libre + Pro)
  GET  /api/setup-fields           Crea custom fields en Kommo (idempotente)
  GET  /api/market-intelligence    Resumen libre
  GET  /api/market-intelligence/pro  Señales Pro
  GET  /health
  GET  /
"""
from __future__ import annotations

import asyncio
import logging
import os
from datetime import datetime, timezone
from typing import Any
from urllib.parse import parse_qs

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, HTTPException, Request, Response

load_dotenv()

from cli_market_integrations.shared.intel_client import CLIMarketIntelClient
from cli_market_integrations.adapters.kommo.kommo_client import KommoClient
from cli_market_integrations.adapters.kommo.enrichment import (
    build_lead_custom_fields,
    build_deal_custom_fields,
    LEAD_FIELD_DEFINITIONS,
)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Kommo CRM + CLI Market",
    version="0.1.0",
    description="Enrich Kommo leads and contacts with CLI Market price intelligence",
)

cli_market = CLIMarketIntelClient()
kommo = KommoClient()
WEBHOOK_SECRET = os.getenv("KOMMO_WEBHOOK_SECRET", "")


# ── Webhook auth ──────────────────────────────────────────────────────────────

def _check_auth(request: Request) -> None:
    if not WEBHOOK_SECRET:
        return
    sig = request.headers.get("X-Kommo-Webhook-Secret") or request.headers.get("X-Webhook-Secret") or ""
    if sig != WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")


# ── Webhook payload parsing ───────────────────────────────────────────────────

def _parse_kommo_webhook(body: bytes) -> dict[str, Any]:
    """
    Kommo envía el webhook como x-www-form-urlencoded.
    Extrae los IDs de leads/contacts afectados y la operación.

    Ejemplo de keys en el payload:
      leads[add][0][id]=111&leads[add][0][name]=Test
      leads[update][0][id]=222
      contacts[add][0][id]=333
    """
    parsed: dict[str, Any] = {"leads_add": [], "leads_update": [], "contacts_add": [], "contacts_update": []}
    try:
        qs = parse_qs(body.decode("utf-8", errors="replace"), keep_blank_values=True)
        for key, values in qs.items():
            val = values[0] if values else ""
            if "leads[add]" in key and key.endswith("[id]"):
                parsed["leads_add"].append(val)
            elif "leads[update]" in key and key.endswith("[id]"):
                parsed["leads_update"].append(val)
            elif "contacts[add]" in key and key.endswith("[id]"):
                parsed["contacts_add"].append(val)
            elif "contacts[update]" in key and key.endswith("[id]"):
                parsed["contacts_update"].append(val)
    except Exception as e:
        logger.error("Error parsing Kommo webhook body: %s", e)
    return parsed


# ── Core enrichment ───────────────────────────────────────────────────────────

async def enrich_lead(lead_id: str) -> dict[str, Any]:
    logger.info("Enriching Kommo lead %s", lead_id)
    lead_data, market_summary = await asyncio.gather(
        kommo.get_lead(lead_id, with_=["custom_fields_values"]),
        cli_market.get_market_summary(),
        return_exceptions=True,
    )
    if isinstance(lead_data, Exception): lead_data = {}
    if isinstance(market_summary, Exception): market_summary = {}

    custom_fields = build_lead_custom_fields(market_summary, lead_data)
    if not custom_fields:
        logger.warning("Lead %s: no custom field IDs configured — skipping update. Run /api/setup-fields first.", lead_id)
        return {"lead_id": lead_id, "status": "skipped_no_field_ids", "fields_count": 0}

    result = await kommo.update_lead(lead_id, {"custom_fields_values": custom_fields})
    logger.info("Lead %s enriched — %d custom fields written", lead_id, len(custom_fields))
    return {"lead_id": lead_id, "custom_fields_written": len(custom_fields), "kommo_result": result}


async def enrich_lead_pro(lead_id: str) -> dict[str, Any]:
    """Enrichment con señales Pro (procurement + price_risk)."""
    procurement, price_risk = await asyncio.gather(
        cli_market.get_procurement_signal(),
        cli_market.get_price_risk(),
        return_exceptions=True,
    )
    if isinstance(procurement, Exception): procurement = {"error": str(procurement)}
    if isinstance(price_risk, Exception): price_risk = {"error": str(price_risk)}

    custom_fields = build_deal_custom_fields(procurement, price_risk)
    if not custom_fields:
        return {"lead_id": lead_id, "status": "skipped_no_field_ids", "fields_count": 0}

    result = await kommo.update_lead(lead_id, {"custom_fields_values": custom_fields})
    return {"lead_id": lead_id, "pro_fields_written": len(custom_fields), "kommo_result": result}


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {"service": "Kommo CRM + CLI Market", "version": "0.1.0", "status": "running", "timestamp": datetime.now(timezone.utc).isoformat()}


@app.get("/health")
async def health():
    cli_ok, kommo_ok = await asyncio.gather(cli_market.health_check(), kommo.health_check())
    return {"status": "healthy" if (cli_ok and kommo_ok) else "degraded", "cli_market_api": cli_ok, "kommo_api": kommo_ok, "timestamp": datetime.now(timezone.utc).isoformat()}


@app.post("/webhook/kommo")
async def kommo_webhook(background_tasks: BackgroundTasks, request: Request):
    """
    Kommo envía webhooks como x-www-form-urlencoded, no JSON.
    Respondemos 200 inmediatamente y procesamos en background.
    """
    _check_auth(request)
    body = await request.body()
    parsed = _parse_kommo_webhook(body)

    scheduled = []
    for lead_id in set(parsed["leads_add"] + parsed["leads_update"]):
        if lead_id:
            background_tasks.add_task(enrich_lead, lead_id)
            background_tasks.add_task(enrich_lead_pro, lead_id)
            scheduled.append({"type": "lead_enrichment", "lead_id": lead_id})

    # Kommo espera 200 vacío o con body mínimo
    return Response(
        content=f'{{"status":"accepted","scheduled":{len(scheduled)}}}',
        media_type="application/json",
        status_code=200,
    )


@app.post("/api/enrich-lead/{lead_id}")
async def manual_enrich_lead(lead_id: str, pro: bool = False):
    """
    Enriquecimiento manual.
    ?pro=true para incluir señales Pro (procurement_signal + price_risk).
    """
    base = await enrich_lead(lead_id)
    if pro:
        pro_result = await enrich_lead_pro(lead_id)
        return {"status": "enriched", **base, "pro": pro_result}
    return {"status": "enriched", **base}


@app.get("/api/setup-fields")
async def setup_fields():
    """
    Crea los custom fields de CLI Market en Kommo (idempotente).
    Retorna los field_ids creados — copiar a env vars KOMMO_FIELD_*.
    Ejecutar UNA SOLA VEZ al configurar la integración.
    """
    results = []
    for defn in LEAD_FIELD_DEFINITIONS:
        env_var = defn["env"]
        existing_id = os.getenv(env_var)
        if existing_id:
            results.append({"name": defn["name"], "status": "already_configured", "field_id": existing_id, "env_var": env_var})
            continue
        resp = await kommo.create_lead_custom_field(defn["name"], defn["type"])
        created = resp.get("_embedded", {}).get("custom_fields", [{}])[0] if not resp.get("error") else {}
        fid = created.get("id")
        results.append({
            "name": defn["name"],
            "status": "created" if fid else "error",
            "field_id": fid,
            "env_var": env_var,
            "note": f"Set {env_var}={fid} in your .env" if fid else resp.get("error"),
        })
    return {"status": "setup_complete", "fields": results}


@app.get("/api/market-intelligence")
async def market_intelligence(country: str = "PE"):
    summary, macro = await asyncio.gather(
        cli_market.get_market_summary(country=country),
        cli_market.get_macro(country=country),
    )
    return {"country": country, "timestamp": datetime.now(timezone.utc).isoformat(), **summary, "macro": macro}


@app.get("/api/market-intelligence/pro")
async def market_intelligence_pro(country: str = "PE"):
    procurement, price_risk = await asyncio.gather(
        cli_market.get_procurement_signal(country=country),
        cli_market.get_price_risk(country=country),
    )
    return {"country": country, "timestamp": datetime.now(timezone.utc).isoformat(), "procurement_signal": procurement, "price_risk": price_risk}
