"""
market_connectors/sunat_invoicing.py — SUNAT electronic invoice via PSE.

SUNAT direct is complex. Recommended: use a PSE (Facturalo, Efact, Digifact).
This connector builds UBL 2.1 + submits via PSE REST API.
"""

import os, httpx
from datetime import datetime, timezone

COMPANY = {"razon_social": "SINAPSIS INNOVADORA S.A.C.", "ruc": "20613045563",
           "direccion": "Lima, Perú", "web": "https://cli-market.dev"}

PSE_PROVIDER = os.getenv("SUNAT_PSE_PROVIDER", "facturalo")
PSE_API_KEY = os.getenv("SUNAT_PSE_API_KEY", "")
PSE_API_URL = os.getenv("SUNAT_PSE_API_URL", "")
SUNAT_MODE = os.getenv("SUNAT_MODE", "demo")


def build_invoice_ubl(order: dict, items: list[dict]) -> dict:
    subtotal = round(sum(i["price"] * i["quantity"] for i in items), 2)
    igv = round(subtotal * 0.18, 2)
    return {
        "tipo_documento": "01", "serie": "F001",
        "numero": order.get("order_id", "").replace("ORD-", ""),
        "fecha_emision": datetime.now(timezone.utc).isoformat(), "moneda": "PEN",
        "emisor": COMPANY,
        "cliente": {"nombre": order.get("username", "Cliente"), "tipo_documento": "0", "numero_documento": "-"},
        "items": [{"codigo": i.get("product_id",""), "descripcion": i.get("name",""),
                    "cantidad": i.get("quantity",1), "precio_unitario": i.get("price",0),
                    "subtotal": round(i.get("price",0)*i.get("quantity",1),2),
                    "unidad": "NIU",
                    "igv": round(i.get("price",0)*i.get("quantity",1)*0.18,2)} for i in items],
        "subtotal": subtotal, "igv": igv, "total": round(subtotal+igv,2),
    }


async def emit_invoice(order: dict, items: list[dict]) -> dict:
    if not PSE_API_KEY:
        return {"status": "demo", "message": f"SUNAT PSE no configurado ({PSE_PROVIDER}). Set SUNAT_PSE_API_KEY.",
                "invoice": build_invoice_ubl(order, items),
                "ruc": COMPANY["ruc"], "razon_social": COMPANY["razon_social"]}

    invoice = build_invoice_ubl(order, items)
    # Submit to PSE provider (Facturalo, Efact, or Digifact)
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.post(
            f"{PSE_API_URL}/v1/invoices", json=invoice,
            headers={"Authorization": f"Bearer {PSE_API_KEY}"},
        )
        if resp.status_code in (200, 201):
            data = resp.json()
            return {"status": "emitida", "invoice_id": data.get("id",""),
                    "serie_numero": f"{invoice['serie']}-{invoice['numero']}",
                    "cdr_status": data.get("cdr_status","accepted"),
                    "pdf_url": data.get("pdf_url",""), "ruc": COMPANY["ruc"]}
    return {"status": "demo", "invoice": invoice,
            "message": f"PSE {PSE_PROVIDER} responded {resp.status_code}. Modo {SUNAT_MODE}."}
