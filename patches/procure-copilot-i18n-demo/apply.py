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
    r"function\s+mailtoHref\s*\([^)]*\)\s*\{[^}]*\}",
    re.MULTILINE,
)
MAILTO_INLINE = re.compile(
    r'let\s+i\s*=\s*"hello@cli-market\.dev"\s*;?\s*'
    r"function\s+l\s*\(\s*e\s*\)\s*\{[^}]+\}",
    re.MULTILINE,
)


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
    original = text

    cta_import = (
        'import { procureBookDemoHref, procureTryDemoHref, procureSalesHref } from "@/lib/procureCta";\n'
    )
    text = _add_import(text, cta_import)

    text = MAILTO_FN.sub(
        "function mailtoHref(_subject: string) { return procureBookDemoHref(); }",
        text,
    )
    text = MAILTO_INLINE.sub("", text)

    for old, new in [
        ('l("Demo Procure Copilot 15 min")', "procureBookDemoHref()"),
        ('l("Piloto Procure Copilot")', "procureBookDemoHref()"),
        ('l("Enterprise Procure Copilot")', 'procureSalesHref("Enterprise Procure Copilot")'),
        ('href:"/dashboard"', "href:procureTryDemoHref()"),
        ('href: "/dashboard"', "href: procureTryDemoHref()"),
        ('ctaHref:"/dashboard"', "ctaHref:procureTryDemoHref()"),
        ('ctaHref: "/dashboard"', "ctaHref: procureTryDemoHref()"),
        ("mailto:hello@cli-market.dev?subject=Demo%20Procure%20Copilot%2015%20min", "https://cli-market.dev/contact?topic=procure#contact-procure"),
    ]:
        text = text.replace(old, new)

    if text != original:
        path.write_text(text, encoding="utf-8")
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


def patch_procure_landing(target: Path) -> None:
    path = target / "components/ProcureLanding.tsx"
    if not path.exists():
        print("  skip: components/ProcureLanding.tsx not found")
        return

    text = path.read_text(encoding="utf-8")
    original = text

    text = _add_import(text, 'import { useLang } from "@/lib/LanguageContext";\n')
    text = _add_import(text, 'import LangToggle from "@/components/LangToggle";\n')
    text = _add_import(text, 'import { getProcureCopy } from "@/lib/procureLocale";\n')

    if "getProcureCopy" not in text or "const copy = getProcureCopy" not in text:
        text = re.sub(
            r"(export default function ProcureLanding\(\)\s*\{)",
            r"\1\n  const { lang } = useLang();\n  const copy = getProcureCopy(lang);\n  const isEN = lang === \"en\";",
            text,
            count=1,
        )

    # Hero block — wire bilingual copy + fixed CTAs
    text = text.replace(
        "Tus compras.",
        '{copy.hero.title.lead}',
    )
    text = text.replace(
        "Comparadas, verificadas,",
        '{copy.hero.title.mid}',
    )
    text = text.replace(
        "aprobadas.",
        '{copy.hero.title.accent}',
    )
    text = text.replace('label:"Probar demo"', "label:copy.tryDemoLabel")
    text = text.replace('label: "Probar demo"', "label: copy.tryDemoLabel")
    text = text.replace('"Agendar demo 15 min"', "{copy.bookDemoLabel}")

    # Lang toggle in header (once)
    if "<LangToggle" not in text and 'id="hero"' in text:
        text = text.replace(
            '<section id="hero"',
            '<LangToggle className="fixed top-4 right-4 z-50" />\n      <section id="hero"',
            1,
        )

    if text != original:
        path.write_text(text, encoding="utf-8")
        print("  patched components/ProcureLanding.tsx (i18n + LangToggle)")
    else:
        print("  WARN: ProcureLanding.tsx — apply manual i18n (see README.md)")


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
    patch_procure_content(target)
    patch_layout(target)
    patch_procure_landing(target)
    print("\nDone. Next:")
    print("  npm run build")
    print("  npx opennextjs-cloudflare build")
    print("  node scripts/copy-public-assets.mjs")
    print("  npx opennextjs-cloudflare deploy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
