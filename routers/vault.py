"""Payment vault endpoints — tokenized payment methods for recurring/one-click billing.

Endpoints:
  POST /billing/vault-setup           PayPal Vault: create setup token (buyer approval)
  POST /billing/vault-confirm         PayPal Vault: exchange setup token → payment token
  POST /billing/vault-charge          PayPal Vault: charge a vaulted payment method
  GET  /billing/vault-tokens          PayPal Vault: list saved payment tokens
  DELETE /billing/vault-tokens/{id}   PayPal Vault: delete a payment token
  POST /checkout/card-payment         MercadoPago: process card_token_id payment
  POST /checkout/save-card            MercadoPago: save card for future one-click
  GET  /checkout/saved-cards/{id}     MercadoPago: list saved cards for customer

All vault endpoints require authentication (Bearer token).
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Body, Header, HTTPException

from market_audit import record_audit
from market_vault import (
    bind_vault_customer,
    bind_vault_payment_token,
    vault_customer_bound_to_other,
    vault_customer_owned,
    vault_payment_token_owned,
)
from server_deps import require_api_key

logger = logging.getLogger(__name__)

router = APIRouter(tags=["vault"])


# ── PayPal Vault ─────────────────────────────────────────────────────────────


@router.post("/billing/vault-setup")
async def vault_setup(
    body: dict = Body(default={}),
    authorization: str | None = Header(None),
):
    """Create a PayPal Vault setup token — buyer approves to save payment method."""
    username = require_api_key(authorization)
    customer_id = (body.get("customer_id") or "").strip()
    if customer_id and vault_customer_bound_to_other(username, customer_id):
        raise HTTPException(status_code=403, detail="customer_id not owned by caller")

    from market_connectors.paypal_payments import create_vault_setup_token

    result = await create_vault_setup_token(
        customer_id=customer_id,
        return_url=body.get("return_url", "https://cli-market.dev?vault=success"),
        cancel_url=body.get("cancel_url", "https://cli-market.dev?vault=cancelled"),
    )
    if "error" in result:
        raise HTTPException(status_code=result.get("status", 502), detail=result["error"])
    if customer_id:
        bind_vault_customer(username, customer_id)
    record_audit("vault_setup", username=username, detail={"setup_token": result.get("setup_token_id")})
    return result


@router.post("/billing/vault-confirm")
async def vault_confirm(
    body: dict = Body(...),
    authorization: str | None = Header(None),
):
    """Exchange a setup token for a reusable payment token (after buyer approval)."""
    username = require_api_key(authorization)
    setup_token_id = (body.get("setup_token_id") or "").strip()
    if not setup_token_id:
        raise HTTPException(status_code=400, detail="setup_token_id required")

    from market_connectors.paypal_payments import create_vault_payment_token

    result = await create_vault_payment_token(setup_token_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status", 502), detail=result["error"])
    customer_id = (result.get("customer_id") or "").strip()
    if customer_id and vault_customer_bound_to_other(username, customer_id):
        raise HTTPException(status_code=403, detail="customer_id not owned by caller")
    payment_token_id = (result.get("payment_token_id") or "").strip()
    if payment_token_id:
        bind_vault_payment_token(username, customer_id, payment_token_id)
    if customer_id:
        bind_vault_customer(username, customer_id)
    record_audit(
        "vault_confirm",
        username=username,
        detail={"payment_token": result.get("payment_token_id"), "customer_id": result.get("customer_id")},
    )
    return result


@router.post("/billing/vault-charge")
async def vault_charge(
    body: dict = Body(...),
    authorization: str | None = Header(None),
):
    """Charge a vaulted payment method — no buyer redirect needed."""
    username = require_api_key(authorization)
    payment_token_id = (body.get("payment_token_id") or "").strip()
    amount = body.get("amount")
    if not payment_token_id:
        raise HTTPException(status_code=400, detail="payment_token_id required")
    if not amount or float(amount) <= 0:
        raise HTTPException(status_code=400, detail="amount must be > 0")
    if not vault_payment_token_owned(username, payment_token_id):
        raise HTTPException(status_code=403, detail="payment_token_id not owned by caller")

    from market_connectors.paypal_payments import charge_vault_payment_token

    result = await charge_vault_payment_token(
        payment_token_id,
        float(amount),
        currency=body.get("currency", "USD"),
        reference=body.get("reference", f"vault-{username}"),
    )
    if not result.get("ok"):
        raise HTTPException(status_code=result.get("status", 502), detail=result.get("error", "charge failed"))
    record_audit(
        "vault_charge",
        username=username,
        resource=result.get("order_id"),
        detail={"amount": amount, "payment_token_id": payment_token_id},
    )
    return result


@router.get("/billing/vault-tokens")
async def vault_tokens(
    customer_id: str = "",
    authorization: str | None = Header(None),
):
    """List saved PayPal payment tokens for a customer."""
    username = require_api_key(authorization)
    if not customer_id:
        raise HTTPException(status_code=400, detail="customer_id query param required")
    if not vault_customer_owned(username, customer_id):
        raise HTTPException(status_code=403, detail="customer_id not owned by caller")

    from market_connectors.paypal_payments import list_vault_payment_tokens

    result = await list_vault_payment_tokens(customer_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status", 502), detail=result["error"])
    return result


@router.delete("/billing/vault-tokens/{payment_token_id}")
async def vault_delete_token(
    payment_token_id: str,
    authorization: str | None = Header(None),
):
    """Delete a vaulted payment token."""
    username = require_api_key(authorization)
    if not vault_payment_token_owned(username, payment_token_id):
        raise HTTPException(status_code=403, detail="payment_token_id not owned by caller")
    from market_connectors.paypal_payments import delete_vault_payment_token

    result = await delete_vault_payment_token(payment_token_id)
    if not result.get("ok"):
        raise HTTPException(status_code=result.get("status", 502), detail=result.get("error", "delete failed"))
    record_audit("vault_delete", username=username, resource=payment_token_id)
    return result


# ── MercadoPago Card Tokenization ────────────────────────────────────────────


@router.post("/checkout/card-payment")
async def card_payment(
    body: dict = Body(...),
    authorization: str | None = Header(None),
):
    """Process a card payment using a MercadoPago card token (embedded checkout)."""
    username = require_api_key(authorization)
    card_token_id = (body.get("card_token_id") or body.get("token") or "").strip()
    amount = body.get("amount")
    if not card_token_id:
        raise HTTPException(status_code=400, detail="card_token_id required")
    if not amount or float(amount) <= 0:
        raise HTTPException(status_code=400, detail="amount must be > 0")

    from market_connectors.mercadopago_payments import create_card_payment

    result = await create_card_payment(
        card_token_id,
        float(amount),
        currency=body.get("currency", "PEN"),
        description=body.get("description", "CLI Market"),
        payer_email=body.get("email", ""),
        installments=int(body.get("installments", 1)),
        external_reference=body.get("reference", f"card-{username}"),
    )
    if "error" in result:
        raise HTTPException(status_code=result.get("status", 502), detail=result["error"])
    record_audit(
        "card_payment",
        username=username,
        resource=str(result.get("payment_id")),
        detail={"amount": amount, "last_four": result.get("card_last_four")},
    )
    return result


@router.post("/checkout/save-card")
async def save_card(
    body: dict = Body(...),
    authorization: str | None = Header(None),
):
    """Save a card to MercadoPago customer for future one-click payments."""
    username = require_api_key(authorization)
    card_token_id = (body.get("card_token_id") or body.get("token") or "").strip()
    customer_id = (body.get("customer_id") or "").strip()
    if not card_token_id:
        raise HTTPException(status_code=400, detail="card_token_id required")
    if not customer_id:
        raise HTTPException(status_code=400, detail="customer_id required")
    if vault_customer_bound_to_other(username, customer_id):
        raise HTTPException(status_code=403, detail="customer_id not owned by caller")

    from market_connectors.mercadopago_payments import save_card_for_customer

    result = await save_card_for_customer(card_token_id, customer_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status", 502), detail=result["error"])
    bind_vault_customer(username, customer_id)
    record_audit("save_card", username=username, detail={"customer_id": customer_id, "last_four": result.get("last_four")})
    return result


@router.get("/checkout/saved-cards/{customer_id}")
async def saved_cards(
    customer_id: str,
    authorization: str | None = Header(None),
):
    """List saved cards for a MercadoPago customer."""
    username = require_api_key(authorization)
    if not vault_customer_owned(username, customer_id):
        raise HTTPException(status_code=403, detail="customer_id not owned by caller")
    from market_connectors.mercadopago_payments import list_customer_cards

    result = await list_customer_cards(customer_id)
    if "error" in result:
        raise HTTPException(status_code=result.get("status", 502), detail=result["error"])
    return result
