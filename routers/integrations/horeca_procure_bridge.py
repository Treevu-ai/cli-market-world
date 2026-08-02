"""Puente HORECA WhatsApp → Procure Copilot (aprobación + trazabilidad)."""

from __future__ import annotations

import os
from typing import Any

import httpx

PROCURE_COPILOT_URL = os.getenv(
    "PROCURE_COPILOT_URL",
    "https://procure-copilot.contacto-8e4.workers.dev",
).rstrip("/")
PROCURE_E2E_SECRET = os.getenv("PROCURE_E2E_SECRET", "").strip()
PROCURE_ESTACION90_ORG = os.getenv("PROCURE_ESTACION90_ORG", "estacion90")
PROCURE_ESTACION90_PLAN = os.getenv("PROCURE_ESTACION90_PLAN", "pro")
PROCURE_ESTACION90_APPROVER = os.getenv(
    "PROCURE_ESTACION90_APPROVER",
    os.getenv("HORECA_ESTACION90_APPROVER", "gerente-estacion90"),
)


def procure_enabled() -> bool:
    return bool(PROCURE_COPILOT_URL and PROCURE_E2E_SECRET)


def _procure_headers(sender: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "x-e2e-secret": PROCURE_E2E_SECRET,
        "x-plan": PROCURE_ESTACION90_PLAN,
        "x-user-id": f"wa-{sender.replace('whatsapp:', '')}",
        "x-organization-id": PROCURE_ESTACION90_ORG,
        "x-approver-id": PROCURE_ESTACION90_APPROVER,
    }


async def run_menu_procurement(
    sender: str,
    *,
    menu_category_id: str = "menu_dia",
    preset_id: str | None = None,
) -> dict[str, Any]:
    """Ejecuta procurement en Procure Copilot (D1 + aprobación si aplica)."""
    if not procure_enabled():
        return {"ok": False, "error": "Procure Copilot no configurado (PROCURE_COPILOT_URL / PROCURE_E2E_SECRET)"}

    body: dict[str, Any] = {
        "country": "PE",
        "preferredRetailers": ["wong", "metro", "plazavea"],
        "approvalThreshold": 150,
        "xUserId": f"wa-{sender.replace('whatsapp:', '')}",
    }
    if preset_id:
        body["presetId"] = preset_id
    else:
        body["menuCategoryId"] = menu_category_id

    async with httpx.AsyncClient(timeout=90.0) as client:
        resp = await client.post(
            f"{PROCURE_COPILOT_URL}/api/procurement/menu-run",
            json=body,
            headers=_procure_headers(sender),
        )
        try:
            payload = resp.json()
        except ValueError:
            return {"ok": False, "error": f"Procure respondió {resp.status_code}"}

    if resp.status_code != 200 or not payload.get("success"):
        return {
            "ok": False,
            "error": payload.get("error", f"Procure error {resp.status_code}"),
        }

    data = payload.get("data") or {}
    return {"ok": True, "data": data}


def format_procure_whatsapp(result: dict[str, Any]) -> str:
    if not result.get("ok"):
        return f"❌ Cotización Procure: {result.get('error', 'error')}"

    data = result["data"]
    best = data.get("bestOption") or {}
    status = data.get("status", "")
    savings = float(data.get("totalSavings") or 0)
    retailer = best.get("retailer", "—")
    total = float(best.get("tcoTotal") or best.get("total") or 0)
    currency = best.get("currency", "PEN")

    lines = [
        "📋 *Cotización Procure — Estación 90*",
        f"Mejor opción: *{retailer}* — {currency} {total:.2f}",
    ]
    if savings > 0:
        lines.append(f"Ahorro vs otras tiendas: {currency} {savings:.2f}")

    if data.get("menuSummary"):
        lines.append(f"\n🍽️ *Menú del día:*\n{data['menuSummary']}")

    if status == "pending_approval":
        lines.append(
            "\n⏳ *Pendiente de aprobación* del gerente. "
            "Revisá en Procure Copilot o respondé `aprobar compra` cuando esté listo."
        )
    elif status == "checkout_ready":
        lines.append("\n✅ Aprobado — listo para checkout en Procure Copilot.")

    dashboard = os.getenv("PROCURE_COPILOT_DASHBOARD_URL", f"{PROCURE_COPILOT_URL}/dashboard?org=estacion90")
    lines.append(f"\n🔗 Dashboard: {dashboard}")
    return "\n".join(lines)
