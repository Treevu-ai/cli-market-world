"""
market_connectors/paypal_payments.py — PayPal REST API integration.

Handles PayPal checkout for subscriptions and one-time purchases.
Uses PayPal Orders API v2. Sandbox-ready.
"""

import os, base64, httpx, json

PAYPAL_CLIENT_ID = os.getenv("PAYPAL_CLIENT_ID", "")
PAYPAL_CLIENT_SECRET = os.getenv("PAYPAL_CLIENT_SECRET", "")
PAYPAL_SANDBOX = os.getenv("PAYPAL_SANDBOX", "true").lower() == "true"

PAYPAL_API = "https://api-m.sandbox.paypal.com" if PAYPAL_SANDBOX else "https://api-m.paypal.com"


async def _get_access_token() -> str:
    if not PAYPAL_CLIENT_ID or not PAYPAL_CLIENT_SECRET:
        raise ValueError("PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET not configured")
    auth = base64.b64encode(f"{PAYPAL_CLIENT_ID}:{PAYPAL_CLIENT_SECRET}".encode()).decode()
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{PAYPAL_API}/v1/oauth2/token",
            data={"grant_type": "client_credentials"},
            headers={"Authorization": f"Basic {auth}", "Content-Type": "application/x-www-form-urlencoded"},
        )
        if resp.status_code == 200:
            return resp.json()["access_token"]
        raise Exception(f"PayPal auth failed: {resp.text}")


async def create_order(amount: float, currency: str = "USD", reference: str = "",
                       return_url: str = "https://cli-market.dev?order=success",
                       cancel_url: str = "https://cli-market.dev?order=cancelled") -> dict:
    """Create a PayPal order and return the approval link."""
    token = await _get_access_token()
    body = {
        "intent": "CAPTURE",
        "purchase_units": [{
            "amount": {"currency_code": currency, "value": f"{amount:.2f}"},
            "reference_id": reference,
            "description": f"CLI Market — {reference}",
        }],
        "application_context": {
            "return_url": return_url, "cancel_url": cancel_url,
            "brand_name": "CLI Market", "shipping_preference": "NO_SHIPPING",
            "user_action": "PAY_NOW",
        },
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{PAYPAL_API}/v2/checkout/orders", json=body,
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        )
        if resp.status_code in (200, 201):
            data = resp.json()
            approve_link = next((l["href"] for l in data.get("links", []) if l["rel"] == "approve"), None)
            return {"order_id": data["id"], "status": data["status"], "approve_url": approve_link}
        return {"error": f"PayPal order failed: {resp.text}", "status": resp.status_code}
