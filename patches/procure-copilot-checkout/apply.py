#!/usr/bin/env python3
"""Procure Copilot — host SaaS subscribe checkout on /subscribe (Phase 2).

Copies billing UI from cli-market-world/landing and patches CTAs to on-site URLs.

From procure-copilot repo root:
  python ../cli-market-world/patches/procure-copilot-checkout/apply.py
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

# Relative to cli-market-world/landing
COPY_FROM_LANDING = [
    "components/BillingCheckoutModal.tsx",
    "components/BillingCheckoutTrigger.tsx",
    "components/ProcureSubscribeButton.tsx",
    "components/ProcurePricingPanel.tsx",
    "components/PaymentReturnBanner.tsx",
    "components/LegalConsentCheckbox.tsx",
    "components/WalletManualTransfer.tsx",
    "components/PayPalHostedButton.tsx",
    "hooks/useBodyScrollLock.ts",
    "lib/procurePlans.ts",
    "lib/api.ts",
    "lib/checkoutLocale.ts",
    "lib/safeCheckoutUrl.ts",
    "lib/billingCopy.ts",
    "lib/modalLayout.ts",
    "lib/funnel.ts",
    "lib/marketStats.ts",
    "lib/buildPlans.ts",
    "lib/LanguageContext.tsx",
]

# Patch-owned files (override landing copies)
COPY_FROM_PATCH = [
    "lib/procureCheckoutUrl.ts",
    "lib/procureCta.ts",
    "app/subscribe/page.tsx",
]

CLI_MARKET_SUBSCRIBE_RE = re.compile(
    r"https://cli-market\.dev(?:/build)?/?\?audience=procure&amp;plan=(?P<plan>starter|pro|builder)&amp;checkout=open#pricing"
    r"|https://cli-market\.dev(?:/build)?/?\?audience=procure&plan=(?P<plan2>starter|pro|builder)&checkout=open#pricing",
    re.IGNORECASE,
)


def _world_root(patch_dir: Path, explicit: Path | None) -> Path:
    if explicit:
        return explicit.resolve()
    return patch_dir.resolve().parents[2]


def copy_landing_files(landing: Path, target: Path) -> None:
    for rel in COPY_FROM_LANDING:
        src = landing / rel
        if not src.is_file():
            print(f"  WARN: missing landing file {rel}", file=sys.stderr)
            continue
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"  copied landing/{rel}")


def copy_patch_files(patch: Path, target: Path) -> None:
    for rel in COPY_FROM_PATCH:
        src = patch / rel
        if not src.is_file():
            print(f"  WARN: missing patch file {rel}", file=sys.stderr)
            continue
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"  copied patch/{rel}")


def patch_subscribe_hrefs(target: Path) -> list[str]:
    changed: list[str] = []
    for path in sorted(target.rglob("*")):
        if path.suffix not in {".ts", ".tsx", ".md", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8")
        if "cli-market.dev" not in text and "audience=procure" not in text:
            continue

        def repl(m: re.Match) -> str:
            plan = m.group("plan") or m.group("plan2")
            return f"/subscribe?plan={plan}&checkout=open"

        patched = CLI_MARKET_SUBSCRIBE_RE.sub(repl, text)
        patched = patched.replace(
            "https://cli-market.dev/?audience=procure#pricing",
            "/subscribe",
        )
        patched = patched.replace(
            "https://cli-market.dev/build?audience=procure#pricing",
            "/subscribe",
        )
        if patched != text:
            path.write_text(patched, encoding="utf-8")
            changed.append(path.relative_to(target).as_posix())
            print(f"  patched subscribe hrefs in {changed[-1]}")
    return changed


def patch_payment_return_banner(target: Path) -> None:
    path = target / "components/PaymentReturnBanner.tsx"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    original = text
    needle = 'const audience = params.get("audience") === "procure" ? "procure" : "build";'
    replacement = (
        'const audience =\n'
        '    params.get("audience") === "procure" ||\n'
        '    (typeof window !== "undefined" && window.location.pathname.startsWith("/subscribe"))\n'
        '      ? "procure"\n'
        '      : "build";'
    )
    if needle in text:
        text = text.replace(needle, replacement, 1)
    if text != original:
        path.write_text(text, encoding="utf-8")
        print("  patched PaymentReturnBanner (subscribe path = procure)")


def main() -> int:
    parser = argparse.ArgumentParser(description="Apply Procure /subscribe checkout patch")
    parser.add_argument("--target", type=Path, default=Path.cwd(), help="procure-copilot root")
    parser.add_argument("--patch", type=Path, default=Path(__file__).resolve().parent)
    parser.add_argument("--world", type=Path, default=None, help="cli-market-world root")
    args = parser.parse_args()

    target = args.target.resolve()
    patch = args.patch.resolve()
    world = _world_root(patch, args.world)
    landing = world / "landing"

    if not (target / "package.json").exists():
        print(f"error: not a Node project: {target}", file=sys.stderr)
        return 1
    if not landing.is_dir():
        print(f"error: landing not found: {landing}", file=sys.stderr)
        return 1

    print(f"Applying Procure checkout patch → {target}")
    print(f"  world: {world}")
    copy_landing_files(landing, target)
    copy_patch_files(patch, target)
    patch_payment_return_banner(target)
    patch_subscribe_hrefs(target)

    print("\nDone. Next:")
    print("  Set NEXT_PUBLIC_* env (see README.md)")
    print("  npm run build && npx opennextjs-cloudflare build && npx opennextjs-cloudflare deploy")
    print("  Update Railway PROCURE_*_URL vars (see README.md)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
