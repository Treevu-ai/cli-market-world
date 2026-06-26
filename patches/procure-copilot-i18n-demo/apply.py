#!/usr/bin/env python3
"""Procure Copilot — fix demo CTAs (no mailto) + EN/ES toggle.

From procure-copilot repo root:
  python patches/procure-copilot-i18n-demo/apply.py
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

COPY_FILES = [
    "lib/procureCta.ts",
    "lib/i18n.ts",
    "lib/LanguageContext.tsx",
    "lib/procureLocale.ts",
    "components/LangToggle.tsx",
]

MAILTO_FN = re.compile(
    r"function\s+mailtoHref\s*\([^)]*\)\s*\{[\s\S]*?\n\}",
    re.MULTILINE,
)
MAILTO_ARROW = re.compile(
    r"(?:const|let|var)\s+mailtoHref\s*=\s*\([^)]*\)\s*=>[^;]+;",
    re.MULTILINE,
)
MAILTO_INLINE = re.compile(
    r'let\s+i\s*=\s*"hello@cli-market\.dev"\s*;?\s*'
    r"function\s+l\s*\(\s*e\s*\)\s*\{[^}]+\}",
    re.MULTILINE,
)
MAILTO_URL = re.compile(
    r'mailto:hello@cli-market\.dev(?:\?[^"\'`\s\)>]*)?',
    re.IGNORECASE,
)
CONTACT_PROCURE = "https://cli-market.dev/contact?topic=procure#contact-procure"

CTA_GLOB_DIRS = ("lib", "components")


def _patch_mailto_text(text: str, *, add_cta_import: bool = True) -> str:
    if add_cta_import:
        cta_import = (
            'import { procureBookDemoHref, procureTryDemoHref, procureSalesHref } from "@/lib/procureCta";\n'
        )
        text = _add_import(text, cta_import)

    text = MAILTO_FN.sub(
        "function mailtoHref(_subject: string) { return procureBookDemoHref(); }",
        text,
    )
    text = MAILTO_ARROW.sub(
        "const mailtoHref = (_subject: string) => procureBookDemoHref();",
        text,
    )
    text = MAILTO_INLINE.sub("", text)
    text = MAILTO_URL.sub(CONTACT_PROCURE, text)
    text = re.sub(r"\bmailtoHref\s*\([^)]*\)", "procureBookDemoHref()", text)
    text = re.sub(r'\bl\s*\(\s*"[^"]+"\s*\)', "procureBookDemoHref()", text)
    text = re.sub(
        r'`mailto:hello@cli-market\.dev\?subject=\$\{encodeURIComponent\([^)]+\)\}`',
        "procureBookDemoHref()",
        text,
        flags=re.IGNORECASE,
    )

    for old, new in [
        ('href:"/dashboard"', "href:procureTryDemoHref()"),
        ('href: "/dashboard"', "href: procureTryDemoHref()"),
        ('ctaHref:"/dashboard"', "ctaHref:procureTryDemoHref()"),
        ('ctaHref: "/dashboard"', "ctaHref: procureTryDemoHref()"),
        ('href:"/dashboard?welcome=1"', "href:procureTryDemoHref()"),
        ('href: "/dashboard?welcome=1"', "href: procureTryDemoHref()"),
    ]:
        text = text.replace(old, new)

    return text


def _patch_cta_files(target: Path) -> list[str]:
    changed: list[str] = []
    for dirname in CTA_GLOB_DIRS:
        root = target / dirname
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if path.suffix not in {".ts", ".tsx"}:
                continue
            if path.name == "procureCta.ts":
                continue
            text = path.read_text(encoding="utf-8")
            if "hello@cli-market.dev" not in text and "/dashboard" not in text:
                continue
            patched = _patch_mailto_text(text)
            if patched != text:
                path.write_text(patched, encoding="utf-8")
                rel = path.relative_to(target).as_posix()
                changed.append(rel)
                print(f"  patched {rel} (demo CTAs)")
    return changed


def _verify_no_demo_mailto(target: Path) -> bool:
    bad: list[str] = []
    for dirname in CTA_GLOB_DIRS:
        root = target / dirname
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if path.suffix not in {".ts", ".tsx"}:
                continue
            if "mailto:hello@cli-market.dev?" in path.read_text(encoding="utf-8"):
                bad.append(path.relative_to(target).as_posix())
    if bad:
        print("  WARN: mailto still present in:", ", ".join(bad), file=sys.stderr)
        return False
    print("  OK: no mailto:hello@cli-market.dev in lib/ or components/")
    return True


def copy_tree(patch: Path, target: Path) -> None:
    for rel in COPY_FILES:
        src = patch / rel
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"  copied {rel}")


def _add_import(text: str, line: str) -> str:
    if line.strip() in text:
        return text
    if text.startswith('"use client"') or text.startswith("'use client'"):
        end = text.find("\n") + 1
        return text[:end] + "\n" + line + text[end:]
    m = re.search(r"^import .+;\n", text, re.MULTILINE)
    if m:
        return text[: m.end()] + line + text[m.end() :]
    return line + text


def patch_procure_content(target: Path) -> None:
    path = target / "lib/procure-content.ts"
    if not path.exists():
        print("  skip: lib/procure-content.ts not found")
        return

    text = path.read_text(encoding="utf-8")
    patched = _patch_mailto_text(text)
    if patched != text:
        path.write_text(patched, encoding="utf-8")
        print("  patched lib/procure-content.ts (demo CTAs)")


def patch_layout(target: Path) -> None:
    path = target / "app/layout.tsx"
    if not path.exists():
        print("  skip: app/layout.tsx not found")
        return

    text = path.read_text(encoding="utf-8")
    original = text

    text = _add_import(text, 'import { LanguageProvider } from "@/lib/LanguageContext";\n')

    if "<LanguageProvider>" not in text and "{children}" in text:
        text = text.replace("{children}", "<LanguageProvider>{children}</LanguageProvider>", 1)

    if text != original:
        path.write_text(text, encoding="utf-8")
        print("  patched app/layout.tsx (LanguageProvider)")


def repair_procure_landing(target: Path) -> None:
    """Fix syntax from an older broken apply.py (escaped quotes on isEN line)."""
    path = target / "components/ProcureLanding.tsx"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    original = text
    text = text.replace('lang === \\"en\\";', 'lang === "en";')
    text = text.replace('lang === \\"en\\"', 'lang === "en"')
    if text != original:
        path.write_text(text, encoding="utf-8")
        print("  repaired components/ProcureLanding.tsx (escaped quotes)")


def patch_procure_landing(target: Path) -> None:
    """Add LangToggle only — demo CTAs are patched in lib/procure-content.ts."""
    path = target / "components/ProcureLanding.tsx"
    if not path.exists():
        print("  skip: components/ProcureLanding.tsx not found")
        return

    repair_procure_landing(target)

    text = path.read_text(encoding="utf-8")
    original = text

    text = _add_import(text, 'import LangToggle from "@/components/LangToggle";\n')

    if "<LangToggle" not in text:
        text = re.sub(
            r"(return\s*\(\s*)",
            r'\1<LangToggle className="fixed top-4 right-4 z-50" />\n      ',
            text,
            count=1,
        )

    if text != original:
        path.write_text(text, encoding="utf-8")
        print("  patched components/ProcureLanding.tsx (LangToggle)")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--patch", type=Path, default=Path(__file__).resolve().parent)
    args = parser.parse_args()
    target = args.target.resolve()
    patch = args.patch.resolve()

    if not (target / "package.json").exists():
        print(f"error: not a Node project: {target}", file=sys.stderr)
        return 1

    print(f"Applying Procure i18n + demo patch → {target}")
    copy_tree(patch, target)
    repair_procure_landing(target)
    patch_procure_content(target)
    _patch_cta_files(target)
    patch_layout(target)
    patch_procure_landing(target)
    _verify_no_demo_mailto(target)
    print("\nDone. Next:")
    print("  npm run build")
    print("  npx opennextjs-cloudflare build")
    print("  node scripts/copy-public-assets.mjs")
    print("  npx opennextjs-cloudflare deploy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
