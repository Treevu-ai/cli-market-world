#!/usr/bin/env python3
"""E2E payment rails — CLI Market (billing + retail/logistics) and Procure Copilot.

Runs against deployed Fly.io (or MARKET_API_URL) and Procure Worker. Does not
complete real payments; validates endpoints, tier gates, and checkout payload shape
for PayPal, Mercado Pago, Yape and Plin.

Usage:
    python ops/payments_e2e.py
    MARKET_API_URL=https://... MARKET_API_TOKEN=... python ops/payments_e2e.py
    MARKET_PRO_API_KEY=sk-... python ops/payments_e2e.py  # retail logistics (Pro cart checkout)
    PROCURE_PUBLIC_URL=https://procure-copilot... python ops/payments_e2e.py

Exit 0 = all required checks passed.
"""

from __future__ import annotations

import json
import os
import sys
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

OPS = Path(__file__).resolve().parent
ROOT = OPS.parent
DEFAULT_API = "https://cli-market-api.fly.dev"
DEFAULT_PROCURE = "https://procurecopilot.com"
DEFAULT_LANDING = "https://cli-market.dev"
BILLING_METHODS = ("paypal", "mercadopago", "yape", "plin")
PROCURE_METHODS = BILLING_METHODS
PROCURE_HEADERS = {
    "Content-Type": "application/json",
    "x-plan": "pro",
    "x-user-id": "payments-e2e",
    "x-approver-id": "payments-e2e-approver",
}
RETAIL_METHODS = (
    ("yape", "POST", "/checkout/yape", None),
    ("plin", "POST", "/checkout/yape", None),
    ("paypal", "POST", "/checkout/paypal", None),
    ("mercadopago", "POST", "/checkout/mercadopago", None),
)
USER_TIERS_CHECKOUT = (
    ("free", False),
    ("starter", False),
    ("pro", True),
)


@dataclass
class Row:
    group: str
    name: str
    status: str  # PASS | FAIL | SKIP
    detail: str = ""
    latency_ms: float = 0.0


@dataclass
class Report:
    rows: list[Row] = field(default_factory=list)

    def add(self, group: str, name: str, status: str, detail: str = "", latency_ms: float = 0.0) -> None:
        self.rows.append(Row(group, name, status, detail, latency_ms))

    def failed(self) -> list[Row]:
        return [r for r in self.rows if r.status == "FAIL"]


def _load_admin_token() -> str:
    token = (os.getenv("MARKET_API_TOKEN") or "").strip()
    if token:
        return token
    rot = OPS / ".rotation-local.txt"
    if rot.exists():
        for line in rot.read_text(encoding="utf-8").splitlines():
            if line.startswith("MARKET_API_TOKEN="):
                return line.split("=", 1)[1].strip()
    return ""


def _load_pro_api_key() -> str:
    """Pro-tier sk- key for retail logistics checkout (same as Procure CLI_MARKET_API_KEY)."""
    for env_name in ("MARKET_PRO_API_KEY", "CLI_MARKET_API_KEY", "MARKET_USER_TOKEN"):
        key = (os.getenv(env_name) or "").strip()
        if key.startswith("sk-"):
            return key
    procure_env_candidates = (
        ROOT.parent / "procure-copilot" / ".env.local",
        ROOT.parent / "Projects" / "procure-copilot" / ".env.local",
    )
    procure_env = next((p for p in procure_env_candidates if p.exists()), None)
    if procure_env:
        for line in procure_env.read_text(encoding="utf-8").splitlines():
            if line.startswith("CLI_MARKET_API_KEY="):
                key = line.split("=", 1)[1].strip().strip("\"'")
                if key.startswith("sk-"):
                    return key
    return ""


_OPENAPI_CACHE: dict[str, set[str]] = {}


def _openapi_paths(base: str) -> set[str]:
    if base in _OPENAPI_CACHE:
        return _OPENAPI_CACHE[base]
    try:
        status, data, _ = http_json(base, "GET", "/openapi.json")
        if status == 200 and isinstance(data, dict):
            paths = set(data.get("paths") or {})
            _OPENAPI_CACHE[base] = paths
            return paths
    except RuntimeError:
        pass
    _OPENAPI_CACHE[base] = set()
    return set()


def _endpoint_available(base: str, path: str) -> bool:
    paths = _openapi_paths(base)
    return path in paths if paths else True


def http_json(
    base: str,
    method: str,
    path: str,
    *,
    body: dict | None = None,
    token: str = "",
    extra_headers: dict[str, str] | None = None,
    timeout: float = 90.0,
) -> tuple[int, dict | list | str, float]:
    url = base.rstrip("/") + path
    headers = {"User-Agent": "CLI-Market-Payments-E2E/1.0", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if extra_headers:
        headers.update(extra_headers)
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = Request(url, data=data, headers=headers, method=method.upper())
    t0 = time.perf_counter()
    try:
        with urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            latency = (time.perf_counter() - t0) * 1000
            try:
                return resp.status, json.loads(raw), latency
            except json.JSONDecodeError:
                return resp.status, raw, latency
    except HTTPError as exc:
        latency = (time.perf_counter() - t0) * 1000
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            return exc.code, json.loads(raw), latency
        except json.JSONDecodeError:
            return exc.code, raw, latency
    except URLError as exc:
        raise RuntimeError(f"{method} {path}: {exc}") from exc


def register_user(base: str) -> tuple[str, str]:
    status, data, _ = http_json(base, "POST", "/auth/register", body={})
    if status != 200 or not isinstance(data, dict):
        raise RuntimeError(f"register failed: {status} {data}")
    key = data.get("api_key") or ""
    user = data.get("username") or ""
    if not key or not user:
        raise RuntimeError(f"register missing fields: {data}")
    return user, key


def search_first_product(base: str, token: str) -> dict | None:
    status, data, _ = http_json(
        base,
        "POST",
        "/products/search",
        token=token,
        body={"query": "leche", "country": "PE", "limit": 3},
    )
    if status != 200 or not isinstance(data, dict):
        return None
    items = data.get("results") or data.get("products") or []
    if not items:
        return None
    p = items[0]
    return {
        "product_id": str(p.get("product_id") or p.get("id") or "1"),
        "name": p.get("name") or "leche",
        "price": float(p.get("price") or 5.0),
        "store": p.get("store") or p.get("store_key") or "wong",
        "url": p.get("url") or "",
    }


def add_cart_item(base: str, token: str, product: dict) -> bool:
    status, data, _ = http_json(
        base,
        "POST",
        "/cart/add",
        token=token,
        body={**product, "quantity": 1},
    )
    return status == 200 and isinstance(data, dict)


def set_tier(base: str, admin: str, username: str, tier: str) -> bool:
    status, data, _ = http_json(
        base,
        "POST",
        "/v1/admin/set-tier",
        token=admin,
        body={"username": username, "tier": tier},
    )
    return status == 200 and isinstance(data, dict)


def run_config_probes(base: str, rep: Report) -> None:
    probes = (
        ("paypal-status", "/paypal-status", ["configured"]),
        ("mercadopago-status", "/mercadopago-status", ["configured"]),
        ("checkout-rates", "/checkout/rates", ["base", "rates"]),
        ("mp-webhook", "/checkout/mercadopago-webhook", []),
    )
    for name, path, keys in probes:
        try:
            status, data, ms = http_json(base, "GET", path)
        except RuntimeError as exc:
            rep.add("config", name, "FAIL", str(exc))
            continue
        if name == "mp-webhook" and status in (200, 401):
            rep.add("config", name, "PASS", f"status={status}", ms)
            continue
        if status not in (200, 400, 401, 405):
            rep.add("config", name, "FAIL", f"status={status}", ms)
            continue
        if keys and isinstance(data, dict):
            missing = [k for k in keys if k not in data]
            if missing:
                rep.add("config", name, "FAIL", f"missing {missing}", ms)
                continue
        rep.add("config", name, "PASS", f"status={status}", ms)


def run_billing_channels(base: str, rep: Report, run_id: str) -> None:
    if not _endpoint_available(base, "/billing/pro-checkout"):
        for method in BILLING_METHODS:
            rep.add("billing", f"pro-checkout/{method}", "SKIP", "endpoint not deployed")
        return

    for method in BILLING_METHODS:
        email = f"e2e+{method}+{run_id}@cli-market.dev"
        try:
            status, data, ms = http_json(
                base,
                "POST",
                "/billing/pro-checkout",
                body={
                    "email": email,
                    "username": f"e2e-{method}-{run_id[:8]}",
                    "lang": "es",
                    "payment_method": method,
                },
            )
        except RuntimeError as exc:
            rep.add("billing", f"pro-checkout/{method}", "FAIL", str(exc))
            continue

        if status not in (200, 501, 502):
            rep.add("billing", f"pro-checkout/{method}", "FAIL", f"status={status} {data}", ms)
            continue

        if not isinstance(data, dict) or not data.get("ok"):
            rep.add("billing", f"pro-checkout/{method}", "FAIL", f"ok=false {data}", ms)
            continue

        rid = data.get("request_id") or ""
        if not str(rid).startswith("PRO-"):
            rep.add("billing", f"pro-checkout/{method}", "FAIL", f"bad request_id {rid}", ms)
            continue

        if method == "paypal":
            url = data.get("approve_url") or data.get("payment_link") or ""
            if not str(url).startswith("http"):
                rep.add("billing", f"pro-checkout/{method}", "FAIL", "no approve_url", ms)
                continue
        elif method in ("yape", "plin"):
            manual = data.get("payment_mode") == "manual_transfer" or data.get("manual_steps")
            mp_url = data.get("checkout_url") or data.get("approve_url") or ""
            if manual:
                if data.get("amount_pen") is None:
                    rep.add("billing", f"pro-checkout/{method}", "FAIL", "no amount_pen", ms)
                    continue
            elif str(mp_url).startswith("http"):
                pass  # routed to Mercado Pago checkout (default in prod)
            else:
                rep.add("billing", f"pro-checkout/{method}", "FAIL", "no manual_transfer or checkout_url", ms)
                continue
        elif method == "mercadopago":
            url = data.get("checkout_url") or data.get("approve_url") or ""
            if not str(url).startswith("http"):
                rep.add("billing", f"pro-checkout/{method}", "FAIL", "no checkout_url", ms)
                continue

        auto = data.get("auto_activate")
        note = "auto" if auto else "manual"
        rep.add("billing", f"pro-checkout/{method}", "PASS", f"{rid} ({note})", ms)


def run_tier_gates(base: str, rep: Report, admin: str) -> tuple[str, str]:
    user, token = register_user(base)
    product = search_first_product(base, token)
    if not product:
        rep.add("tier", "setup/cart", "FAIL", "no search product for cart")
        return user, token
    if not add_cart_item(base, token, product):
        rep.add("tier", "setup/cart", "FAIL", "cart/add failed")
        return user, token
    rep.add("tier", "setup/user", "PASS", user)

    set_tier_live = _endpoint_available(base, "/v1/admin/set-tier")
    if admin and not set_tier_live:
        rep.add("tier", "set-tier", "SKIP", "/v1/admin/set-tier not deployed")

    for tier, should_checkout in USER_TIERS_CHECKOUT:
        if should_checkout and not set_tier_live:
            rep.add("tier", f"retail/{tier}", "SKIP", "set-tier not deployed — use retail group")
            continue
        if admin and set_tier_live:
            if not set_tier(base, admin, user, tier):
                rep.add("tier", f"set-tier/{tier}", "FAIL", "admin set-tier failed")
                continue
            rep.add("tier", f"set-tier/{tier}", "PASS", tier)
        elif tier != "free":
            reason = "set-tier not deployed" if admin else "MARKET_API_TOKEN missing for set-tier"
            rep.add("tier", f"retail/{tier}", "SKIP", reason)
            continue

        for ch_name, method, path, _ in RETAIL_METHODS:
            if should_checkout and product and not add_cart_item(base, token, product):
                rep.add("tier", f"{tier}/{ch_name}", "FAIL", "cart/add before checkout failed")
                continue
            try:
                status, data, ms = http_json(base, method, path, token=token)
            except RuntimeError as exc:
                rep.add("tier", f"{tier}/{ch_name}", "FAIL", str(exc))
                continue

            if should_checkout:
                if status == 200 and isinstance(data, dict):
                    if ch_name in ("yape", "plin") and (
                        data.get("payment_mode") == "manual_transfer" or data.get("manual_steps")
                    ):
                        rep.add("tier", f"{tier}/{ch_name}", "PASS", data.get("order_id", ""), ms)
                    elif ch_name == "mercadopago" and data.get("checkout_url"):
                        rep.add("tier", f"{tier}/{ch_name}", "PASS", data.get("order_id", ""), ms)
                    elif ch_name == "paypal" and data.get("approve_url"):
                        rep.add("tier", f"{tier}/{ch_name}", "PASS", data.get("order_id", ""), ms)
                    elif status == 501:
                        rep.add("tier", f"{tier}/{ch_name}", "SKIP", "gateway not configured", ms)
                    else:
                        rep.add("tier", f"{tier}/{ch_name}", "FAIL", f"status={status} {data}", ms)
                elif status in (501, 502):
                    rep.add("tier", f"{tier}/{ch_name}", "SKIP", f"gateway {status}", ms)
                else:
                    rep.add("tier", f"{tier}/{ch_name}", "FAIL", f"expected 200 got {status}", ms)
            else:
                if status == 403:
                    rep.add("tier", f"{tier}/{ch_name}", "PASS", "403 as expected", ms)
                else:
                    rep.add("tier", f"{tier}/{ch_name}", "FAIL", f"expected 403 got {status}", ms)

        if not admin:
            break

    if admin:
        set_tier(base, admin, user, "free")

    return user, token


def _checkout_payload_ok(method: str, data: dict) -> tuple[bool, str]:
    """Validate retail or procure checkout JSON shape."""
    if method in ("yape", "plin"):
        if data.get("payment_mode") == "manual_transfer" or data.get("manual_steps"):
            return True, str(data.get("order_id") or data.get("request_id") or "")
        return False, "missing manual_transfer"
    if method == "mercadopago":
        url = data.get("checkout_url") or data.get("preference_id")
        if url and str(url).startswith("http"):
            return True, str(data.get("order_id") or "")
        return False, "missing checkout_url"
    if method == "paypal":
        url = data.get("approve_url") or data.get("approval_url") or data.get("checkout_url")
        if url and str(url).startswith("http"):
            return True, str(data.get("order_id") or data.get("paypal_order_id") or "")
        return False, "missing approve_url"
    return False, f"unknown method {method}"


def _procure_checkout_payload_ok(method: str, payload: dict) -> tuple[bool, str]:
    if not isinstance(payload, dict):
        return False, "non-dict response"
    if not payload.get("success"):
        err = str(payload.get("error") or "")
        if "Pro" in err or "tier" in err.lower():
            return False, f"gate: {err}"
        return False, err or "success=false"
    checkout = payload.get("checkout")
    if not isinstance(checkout, dict):
        inner = payload.get("data")
        if isinstance(inner, dict):
            checkout = inner.get("checkout")
    if not isinstance(checkout, dict):
        return False, "missing checkout"
    url = checkout.get("checkoutUrl") or checkout.get("qrUrl")
    if method in ("yape", "plin"):
        if checkout.get("qrUrl") or (url and str(url).startswith("http")):
            return True, str(checkout.get("orderId") or "")
        return False, "missing qrUrl/checkoutUrl"
    if method == "mercadopago":
        if url and str(url).startswith("http"):
            return True, str(checkout.get("orderId") or "")
        return False, "missing checkoutUrl"
    if method == "paypal":
        if url and str(url).startswith("http"):
            return True, str(checkout.get("orderId") or checkout.get("paypalOrderId") or "")
        return False, "missing checkoutUrl"
    return False, f"unknown method {method}"


def _procure_run_and_approve(procure_base: str) -> tuple[dict | None, str]:
    status, run, _ = http_json(
        procure_base,
        "POST",
        "/api/procurement/run",
        body={
            "items": [{"product": "arroz", "quantity": 2}],
            "country": "PE",
            "approvalThreshold": 1,
        },
        extra_headers=PROCURE_HEADERS,
    )
    if status != 200 or not isinstance(run, dict) or not run.get("success"):
        return None, f"run {status} {run}"
    proc = run.get("data") or {}
    if not isinstance(proc, dict) or not proc.get("id"):
        return None, "run missing procurement id"

    if proc.get("status") == "pending_approval":
        approval = proc.get("approval") or {}
        aid = approval.get("id")
        if not aid:
            return None, "pending_approval without approval.id"
        status, appr, _ = http_json(
            procure_base,
            "POST",
            "/api/procurement/approve",
            body={
                "approvalId": aid,
                "response": "approved",
                "responderId": "payments-e2e-approver",
            },
            extra_headers=PROCURE_HEADERS,
        )
        if status != 200 or not isinstance(appr, dict) or not appr.get("success"):
            return None, f"approve {status} {appr}"
        proc = (appr.get("data") or {}).get("procurement") or proc

    if proc.get("status") not in ("checkout_ready", "approved"):
        return None, f"status={proc.get('status')}"

    return proc, ""


def run_procure_channels(procure_base: str, rep: Report) -> None:
    """Procure Copilot: run → approve → checkout per payment rail."""
    try:
        status, data, ms = http_json(procure_base, "GET", "/procure")
    except RuntimeError as exc:
        rep.add("procure", "health", "FAIL", str(exc))
        return
    if status != 200:
        rep.add("procure", "health", "FAIL", f"status={status}", ms)
        return
    rep.add("procure", "health", "PASS", "landing ok", ms)

    for method in PROCURE_METHODS:
        proc, err = _procure_run_and_approve(procure_base)
        if not proc:
            err_l = err.lower()
            if "429" in err and (
                "plan_limit_quota" in err_l or "procurement limit" in err_l
            ):
                rep.add("procure", f"checkout/{method}", "SKIP", err)
            else:
                rep.add("procure", f"checkout/{method}", "FAIL", err)
            continue

        try:
            status, payload, ms = http_json(
                procure_base,
                "POST",
                "/api/procurement/checkout",
                body={"procurementId": proc["id"], "payment": method},
                extra_headers=PROCURE_HEADERS,
            )
        except RuntimeError as exc:
            rep.add("procure", f"checkout/{method}", "FAIL", str(exc))
            continue

        if status in (501, 502):
            rep.add("procure", f"checkout/{method}", "SKIP", f"gateway {status}", ms)
            continue

        if isinstance(payload, dict):
            err_text = str(payload.get("error") or "")
            err_code = str(payload.get("code") or "")
            if status in (403, 429) and (
                err_code in ("PLAN_LIMIT_CHECKOUT", "PLAN_LIMIT_QUOTA")
                or ("Pro" in err_text and ("CLI Market" in err_text or "Procure Pro" in err_text))
                or "procurement limit" in err_text.lower()
            ):
                rep.add("procure", f"checkout/{method}", "SKIP", err_text or err_code, ms)
                continue

        if status != 200 or not isinstance(payload, dict):
            rep.add("procure", f"checkout/{method}", "FAIL", f"status={status} {payload}", ms)
            continue

        err_text = str(payload.get("error") or "")
        if method == "paypal" and ("PayPal" in err_text or status == 501):
            rep.add("procure", f"checkout/{method}", "SKIP", err_text or "paypal unavailable", ms)
            continue
        if method == "mercadopago" and ("Mercado" in err_text or status == 501):
            rep.add("procure", f"checkout/{method}", "SKIP", err_text or "mp unavailable", ms)
            continue

        ok, detail = _procure_checkout_payload_ok(method, payload)
        if ok:
            rep.add("procure", f"checkout/{method}", "PASS", detail, ms)
        else:
            rep.add("procure", f"checkout/{method}", "FAIL", detail, ms)


def run_retail_logistics_channels(base: str, rep: Report, admin: str) -> None:
    """Retail cart checkout (logistics rail) — Pro tier, all four gateways."""
    pro_key = _load_pro_api_key()
    set_tier_live = _endpoint_available(base, "/v1/admin/set-tier")

    if pro_key:
        token = pro_key
        status, acc, _ = http_json(base, "GET", "/auth/account", token=token)
        if status != 200 or not isinstance(acc, dict) or acc.get("tier") != "pro":
            for method in BILLING_METHODS:
                rep.add("retail", f"checkout/{method}", "FAIL", "MARKET_PRO_API_KEY not pro tier")
            return
        user = str(acc.get("username") or "pro-user")
        rep.add("retail", "setup", "PASS", f"user={user} tier=pro (api key)")
    elif admin and set_tier_live:
        user, token = register_user(base)
        product = search_first_product(base, token)
        if not product or not add_cart_item(base, token, product):
            for method in BILLING_METHODS:
                rep.add("retail", f"checkout/{method}", "FAIL", "cart setup failed")
            return
        if not set_tier(base, admin, user, "pro"):
            for method in BILLING_METHODS:
                rep.add("retail", f"checkout/{method}", "FAIL", "set-tier pro failed")
            return
        rep.add("retail", "setup", "PASS", f"user={user} tier=pro")
    else:
        for method in BILLING_METHODS:
            rep.add(
                "retail",
                f"checkout/{method}",
                "SKIP",
                "set MARKET_PRO_API_KEY or deploy /v1/admin/set-tier",
            )
        return

    product = search_first_product(base, token)
    if not product:
        for method in BILLING_METHODS:
            rep.add("retail", f"checkout/{method}", "FAIL", "no search product")
        return

    for ch_name, method, path, _ in RETAIL_METHODS:
        if not add_cart_item(base, token, product):
            rep.add("retail", f"checkout/{ch_name}", "FAIL", "cart/add failed")
            continue
        try:
            status, data, ms = http_json(base, method, path, token=token)
        except RuntimeError as exc:
            rep.add("retail", f"checkout/{ch_name}", "FAIL", str(exc))
            continue

        if status in (501, 502):
            rep.add("retail", f"checkout/{ch_name}", "SKIP", f"gateway {status}", ms)
            continue
        if status != 200 or not isinstance(data, dict):
            rep.add("retail", f"checkout/{ch_name}", "FAIL", f"status={status} {data}", ms)
            continue

        ok, detail = _checkout_payload_ok(ch_name, data)
        if ok:
            rep.add("retail", f"checkout/{ch_name}", "PASS", detail, ms)
        else:
            rep.add("retail", f"checkout/{ch_name}", "FAIL", detail, ms)

    if admin and set_tier_live and not pro_key:
        set_tier(base, admin, user, "free")


def run_procure_billing(base: str, rep: Report, run_id: str) -> None:
    """Procure subscription rail on Fly.io (landing #procure tab)."""
    if not _endpoint_available(base, "/billing/procure-subscribe"):
        rep.add("billing", "procure-subscribe", "SKIP", "endpoint not deployed")
        return
    try:
        status, data, ms = http_json(
            base,
            "POST",
            "/billing/procure-subscribe",
            body={
                "email": f"e2e+procure+{run_id}@cli-market.dev",
                "tier": "procure_pro",
                "payment_method": "paypal",
                "lang": "es",
            },
        )
    except RuntimeError as exc:
        rep.add("billing", "procure-subscribe", "FAIL", str(exc))
        return
    if status in (501, 502):
        rep.add("billing", "procure-subscribe", "SKIP", f"PayPal unavailable ({status})", ms)
        return
    if status != 200 or not isinstance(data, dict):
        rep.add("billing", "procure-subscribe", "FAIL", f"status={status} {data}", ms)
        return
    tier = data.get("tier") or data.get("plan")
    if tier == "procure_pro" or data.get("checkout_url") or data.get("approve_url") or data.get("ok"):
        rep.add("billing", "procure-subscribe", "PASS", f"tier={tier or 'procure_pro'}", ms)
    else:
        rep.add("billing", "procure-subscribe", "FAIL", str(data), ms)


def run_landing_pricing_smoke(landing: str, rep: Report) -> None:
    """Landing #pricing — Build · Procure · Listed tabs (post-unification)."""
    try:
        status, body, ms = http_json(landing, "GET", "/")
    except RuntimeError as exc:
        rep.add("landing", "home", "FAIL", str(exc))
        return
    if status != 200 or not isinstance(body, str):
        rep.add("landing", "home", "FAIL", f"status={status}", ms)
        return
    rep.add("landing", "home", "PASS", "200", ms)
    markers = (
        ("tab-build", "Build"),
        ("tab-procure", "Procure"),
        ("tab-listed", "Listed"),
        ("anchor-pricing", 'id="pricing"'),
        ("anchor-procure", 'id="procure"'),
        ("anchor-listed", 'id="listed"'),
        ("pro-checkout", 'id="pro-checkout"'),
        ("cta-pro-modal", "Elegir Pro"),
        ("cta-procure-modal", "Suscribir con PayPal"),
        ("section-glow", "landing-section-glow"),
        ("hero-terminal", "hero-terminal"),
    )
    for name, needle in markers:
        if needle in body:
            rep.add("landing", name, "PASS", needle)
        else:
            rep.add("landing", name, "FAIL", f"missing {needle}")

    # Pricing cards should expose CTA only — email fields live in checkout modal (client)
    pricing_slice = body[body.find('id="pricing"'): body.find('id="faq"')] if 'id="pricing"' in body else ""
    email_inputs = pricing_slice.count('type="email"')
    if email_inputs > 2:
        rep.add("landing", "pricing-no-inline-email", "FAIL", f"email inputs={email_inputs}")
    else:
        rep.add("landing", "pricing-no-inline-email", "PASS", "cards lean")

    try:
        status, _, ms = http_json(DEFAULT_PROCURE, "GET", "/procure")
    except RuntimeError as exc:
        rep.add("landing", "procure-redirect", "FAIL", str(exc))
        return
    if status == 200:
        rep.add("landing", "procure-redirect", "PASS", "followed to landing", ms)
    else:
        rep.add("landing", "procure-redirect", "FAIL", f"status={status}", ms)


def run_p0a_idempotency(base: str, rep: Report, admin: str) -> None:
    """P0-A: Idempotency-Key, confirmation_mode, webhook dedup (live API)."""
    pro_key = _load_pro_api_key()
    set_tier_live = _endpoint_available(base, "/v1/admin/set-tier")
    token = pro_key
    if not token and admin and set_tier_live:
        user, token = register_user(base)
        product = search_first_product(base, token)
        if not product or not add_cart_item(base, token, product):
            rep.add("p0a", "setup", "SKIP", "cart setup failed")
            return
        if not set_tier(base, admin, user, "pro"):
            rep.add("p0a", "setup", "SKIP", "set-tier pro failed")
            return
    elif not token:
        rep.add("p0a", "idempotency", "SKIP", "needs MARKET_PRO_API_KEY or admin set-tier")
        rep.add("p0a", "confirmation_mode", "SKIP", "needs pro checkout access")
        return

    product = search_first_product(base, token)
    if not product:
        rep.add("p0a", "setup", "FAIL", "no search product")
        return

    idem = f"e2e-idem-{uuid.uuid4().hex[:12]}"
    if not add_cart_item(base, token, product):
        rep.add("p0a", "idempotency", "FAIL", "cart/add failed")
        return
    try:
        s1, d1, ms1 = http_json(
            base,
            "POST",
            "/checkout/yape",
            token=token,
            extra_headers={"Idempotency-Key": idem},
        )
        if not add_cart_item(base, token, product):
            rep.add("p0a", "idempotency", "FAIL", "cart/add replay failed")
            return
        s2, d2, ms2 = http_json(
            base,
            "POST",
            "/checkout/yape",
            token=token,
            extra_headers={"Idempotency-Key": idem},
        )
    except RuntimeError as exc:
        rep.add("p0a", "idempotency", "FAIL", str(exc))
        return

    if s1 == 200 and s2 == 200 and isinstance(d1, dict) and isinstance(d2, dict):
        if d1.get("order_id") and d1.get("order_id") == d2.get("order_id"):
            rep.add("p0a", "idempotency", "PASS", d1["order_id"], ms1 + ms2)
        else:
            rep.add("p0a", "idempotency", "FAIL", f"orders differ {d1} vs {d2}")
    elif s1 in (501, 502):
        rep.add("p0a", "idempotency", "SKIP", f"gateway {s1}")
    else:
        rep.add("p0a", "idempotency", "FAIL", f"status {s1}/{s2}")

    if s1 == 200 and isinstance(d1, dict):
        mode = d1.get("confirmation_mode") or ("manual" if d1.get("auto_activate") is False else "")
        scope = (d1.get("capabilities") or {}).get("checkout_scope")
        if mode == "manual" or scope == "cli_market_internal":
            rep.add("p0a", "confirmation_mode", "PASS", f"mode={mode} scope={scope}", ms1)
        else:
            rep.add("p0a", "confirmation_mode", "FAIL", str(d1))

    try:
        status, cap, ms = http_json(base, "GET", "/v1/capabilities")
        if status == 200 and isinstance(cap, dict) and cap.get("checkout", {}).get("scope") == "cli_market_internal":
            rep.add("p0a", "capabilities", "PASS", "cli_market_internal", ms)
        elif status == 404:
            rep.add("p0a", "capabilities", "SKIP", "not deployed yet")
        else:
            rep.add("p0a", "capabilities", "FAIL", f"status={status} {cap}", ms)
    except RuntimeError as exc:
        rep.add("p0a", "capabilities", "FAIL", str(exc))


def run_legacy_endpoints(base: str, rep: Report, run_id: str) -> None:
    """Backward-compat billing paths still wired in CLI/landing."""
    cases = (
        ("request-pro", "/billing/request-pro", {"email": f"e2e+req+{run_id}@cli-market.dev", "lang": "es"}),
        ("paypal-subscribe", "/billing/paypal-subscribe", {
            "email": f"e2e+pp+{run_id}@cli-market.dev",
            "lang": "es",
        }),
    )
    for name, path, body in cases:
        try:
            status, data, ms = http_json(base, "POST", path, body=body)
        except RuntimeError as exc:
            rep.add("legacy", name, "FAIL", str(exc))
            continue
        if status in (200, 501, 502) and isinstance(data, dict) and data.get("ok"):
            rep.add("legacy", name, "PASS", f"status={status}", ms)
        elif status in (501, 502):
            rep.add("legacy", name, "SKIP", f"PayPal unavailable ({status})", ms)
        else:
            rep.add("legacy", name, "FAIL", f"status={status} {data}", ms)


def print_report(rep: Report) -> None:
    groups: dict[str, list[Row]] = {}
    for row in rep.rows:
        groups.setdefault(row.group, []).append(row)

    print("\n=== Payments E2E Report ===\n")
    for group in ("config", "p0a", "billing", "tier", "retail", "procure", "landing", "legacy"):
        rows = groups.get(group, [])
        if not rows:
            continue
        print(f"-- {group} --")
        for r in rows:
            lat = f" {r.latency_ms:.0f}ms" if r.latency_ms else ""
            extra = f" — {r.detail}" if r.detail else ""
            print(f"  [{r.status:4}] {r.name}{lat}{extra}")
        print()

    passed = sum(1 for r in rep.rows if r.status == "PASS")
    failed = sum(1 for r in rep.rows if r.status == "FAIL")
    skipped = sum(1 for r in rep.rows if r.status == "SKIP")
    print(f"TOTAL  PASS {passed}  FAIL {failed}  SKIP {skipped}")


def main() -> int:
    base = os.getenv("MARKET_API_URL", DEFAULT_API).rstrip("/")
    procure_base = os.getenv("PROCURE_PUBLIC_URL", DEFAULT_PROCURE).rstrip("/")
    landing = os.getenv("LANDING_URL", DEFAULT_LANDING).rstrip("/")
    admin = _load_admin_token()
    run_id = uuid.uuid4().hex[:10]
    rep = Report()

    print(f"API: {base}")
    print(f"Procure: {procure_base}")
    print(f"Landing: {landing}")
    print(f"run_id: {run_id}")
    pro_key = _load_pro_api_key()
    if admin:
        print("admin: MARKET_API_TOKEN loaded")
    else:
        print("admin: not set — tier tests limited to free-only gates")
    if pro_key:
        print("retail: MARKET_PRO_API_KEY loaded")
    else:
        print("retail: no pro api key — logistics checkout needs MARKET_PRO_API_KEY or set-tier")

    try:
        status, data, ms = http_json(base, "GET", "/")
        if status == 200 and isinstance(data, dict) and data.get("status") == "running":
            rep.add("config", "health", "PASS", "running", ms)
        else:
            rep.add("config", "health", "FAIL", f"{status} {data}", ms)
            print_report(rep)
            return 1
    except RuntimeError as exc:
        rep.add("config", "health", "FAIL", str(exc))
        print_report(rep)
        return 1

    run_config_probes(base, rep)
    run_p0a_idempotency(base, rep, admin)
    run_billing_channels(base, rep, run_id)
    run_procure_billing(base, rep, run_id)
    run_tier_gates(base, rep, admin)
    run_retail_logistics_channels(base, rep, admin)
    run_procure_channels(procure_base, rep)
    run_landing_pricing_smoke(landing, rep)
    run_legacy_endpoints(base, rep, run_id)

    print_report(rep)
    fails = rep.failed()
    if fails:
        print("\nFailures:")
        for f in fails:
            print(f"  - [{f.group}] {f.name}: {f.detail}")
        return 1
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(ROOT))
    raise SystemExit(main())