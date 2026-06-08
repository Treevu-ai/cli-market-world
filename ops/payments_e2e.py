#!/usr/bin/env python3
"""E2E payment flows — all billing + retail channels and tier gates.

Runs against deployed Railway (or MARKET_API_URL). Does not complete real payments;
validates endpoints, config, tier gates, and checkout payload shape.

Usage:
    python ops/payments_e2e.py
    MARKET_API_URL=https://... MARKET_API_TOKEN=... python ops/payments_e2e.py

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
DEFAULT_API = "https://cli-market-production.up.railway.app"
BILLING_METHODS = ("paypal", "mercadopago", "yape", "plin")
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


def http_json(
    base: str,
    method: str,
    path: str,
    *,
    body: dict | None = None,
    token: str = "",
    timeout: float = 45.0,
) -> tuple[int, dict | list | str, float]:
    url = base.rstrip("/") + path
    headers = {"User-Agent": "CLI-Market-Payments-E2E/1.0", "Accept": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
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
            if not data.get("qr_url"):
                rep.add("billing", f"pro-checkout/{method}", "FAIL", "no qr_url", ms)
                continue
            if data.get("amount_pen") is None:
                rep.add("billing", f"pro-checkout/{method}", "FAIL", "no amount_pen", ms)
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

    for tier, should_checkout in USER_TIERS_CHECKOUT:
        if admin:
            if not set_tier(base, admin, user, tier):
                rep.add("tier", f"set-tier/{tier}", "FAIL", "admin set-tier failed")
                continue
            rep.add("tier", f"set-tier/{tier}", "PASS", tier)
        elif tier != "free":
            rep.add("tier", f"retail/{tier}", "SKIP", "MARKET_API_TOKEN missing for set-tier")
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
                    if ch_name in ("yape", "plin") and data.get("qr_url"):
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
    for group in ("config", "billing", "tier", "legacy"):
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
    admin = _load_admin_token()
    run_id = uuid.uuid4().hex[:10]
    rep = Report()

    print(f"API: {base}")
    print(f"run_id: {run_id}")
    if admin:
        print("admin: MARKET_API_TOKEN loaded")
    else:
        print("admin: not set — tier tests limited to free-only gates")

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
    run_billing_channels(base, rep, run_id)
    run_tier_gates(base, rep, admin)
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