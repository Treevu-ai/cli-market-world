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
    "lib/procureEnStrings.ts",
    "lib/procureI18n.ts",
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
# Source pattern: const n = "hello@cli-market.dev"; function d(e) { return `mailto:${n}?subject=...`; }
MAILTO_VAR_FN = re.compile(
    r"(?:const|let|var)\s+(?P<var>\w+)\s*=\s*[\"']hello@cli-market\.dev[\"']\s*;?\s*"
    r"function\s+(?P<fn>\w+)\s*\(\s*(?P<arg>\w+)\s*\)\s*\{[^{}]*`mailto:\$\{(?P=var)\}\?subject=\$\{encodeURIComponent\((?P=arg)\)\}`[^{}]*\}",
    re.MULTILINE | re.DOTALL,
)
MAILTO_TEMPLATE = re.compile(
    r"`mailto:\$\{\w+\}\?subject=\$\{encodeURIComponent\(\w+\)\}`",
)
MAILTO_URL = re.compile(
    r'mailto:hello@cli-market\.dev\?[^"\'`\s\)>]*',
    re.IGNORECASE,
)
CONTACT_PROCURE = "https://cli-market.dev/contact?topic=procure#contact-procure"

CTA_GLOB_DIRS = ("app", "lib", "components")


def _patch_mailto_text(text: str, *, add_cta_import: bool = True) -> str:
    if add_cta_import:
        cta_import = (
            'import { procureBookDemoHref, procureTryDemoHref, procureSalesHref } from "@/lib/procureCta";\n'
        )
        text = _add_import(text, cta_import)

    m = MAILTO_VAR_FN.search(text)
    if m:
        fn = m.group("fn")
        text = MAILTO_VAR_FN.sub(
            "function mailtoHref(_subject: string) { return procureBookDemoHref(); }",
            text,
            count=1,
        )
        text = re.sub(rf"\b{re.escape(fn)}\s*\([^)]*\)", "procureBookDemoHref()", text)

    text = MAILTO_FN.sub(
        "function mailtoHref(_subject: string) { return procureBookDemoHref(); }",
        text,
    )
    text = MAILTO_ARROW.sub(
        "const mailtoHref = (_subject: string) => procureBookDemoHref();",
        text,
    )
    text = MAILTO_INLINE.sub("", text)
    text = MAILTO_TEMPLATE.sub("procureBookDemoHref()", text)
    text = MAILTO_URL.sub(CONTACT_PROCURE, text)
    text = re.sub(r"\bmailtoHref\s*\([^)]*\)", "procureBookDemoHref()", text)
    text = re.sub(r'\bl\s*\(\s*"[^"]+"\s*\)', "procureBookDemoHref()", text)
    text = re.sub(r'\bd\s*\(\s*"[^"]+"\s*\)', "procureBookDemoHref()", text)
    text = re.sub(
        r'`mailto:hello@cli-market\.dev\?subject=\$\{encodeURIComponent\([^)]+\)\}`',
        "procureBookDemoHref()",
        text,
        flags=re.IGNORECASE,
    )

    for old, new in [
        ('l("Demo Procure Copilot 15 min")', "procureBookDemoHref()"),
        ('l("Piloto Procure Copilot")', "procureBookDemoHref()"),
        ('l("Enterprise Procure Copilot")', 'procureSalesHref("Enterprise Procure Copilot")'),
        ('d("Demo Procure Copilot 15 min")', "procureBookDemoHref()"),
        ('d("Piloto Procure Copilot")', "procureBookDemoHref()"),
        ('d("Enterprise Procure Copilot")', 'procureSalesHref("Enterprise Procure Copilot")'),
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
    print("  OK: no demo mailto (?subject=) in lib/ or components/")
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
    """Add LangToggle + wire EN copy via useProcureContent."""
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


def _procure_content_exports(target: Path) -> list[str]:
    path = target / "lib/procure-content.ts"
    if not path.exists():
        return []
    return re.findall(r"^export const (\w+)", path.read_text(encoding="utf-8"), re.MULTILINE)


def generate_use_procure_content(target: Path) -> None:
    exports = _procure_content_exports(target)
    if not exports:
        print("  skip: no export const in lib/procure-content.ts")
        return

    path = target / "lib/useProcureContent.ts"
    if path.exists() and "useProcureContent" in path.read_text(encoding="utf-8"):
        print("  skip: lib/useProcureContent.ts already present")
        return

    imports = ", ".join(exports)
    pack = ", ".join(exports)
    body = f'''\"use client\";

import {{ useMemo }} from "react";
import {{ useLang }} from "@/lib/LanguageContext";
import {{ localizeProcureData }} from "@/lib/procureI18n";
import {{ {imports} }} from "@/lib/procure-content";

const RAW = {{ {pack} }} as const;

export function useProcureContent() {{
  const {{ lang }} = useLang();
  return useMemo(() => localizeProcureData(RAW, lang), [lang]);
}}
'''
    path.write_text(body, encoding="utf-8")
    print("  wrote lib/useProcureContent.ts (i18n hook)")


def patch_procure_i18n_imports(target: Path) -> None:
    exports = _procure_content_exports(target)
    if not exports:
        return

    candidates = [
        target / "components/ProcureLanding.tsx",
        target / "app/procure/page.tsx",
    ]
    import_re = re.compile(
        r'import\s+\{([^}]+)\}\s+from\s+["\']@/lib/procure-content["\'];?\n'
    )

    for path in candidates:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if not import_re.search(text):
            continue
        original = text

        text = import_re.sub(
            'import { useProcureContent } from "@/lib/useProcureContent";\n',
            text,
            count=1,
        )

        if "useProcureContent()" not in text:
            text = re.sub(
                r"(export default function \w+\(\)\s*\{)",
                r"\1\n  const procureContent = useProcureContent();",
                text,
                count=1,
            )

        for name in sorted(exports, key=len, reverse=True):
            text = re.sub(rf"(?<!\.)\b{re.escape(name)}\b", f"procureContent.{name}", text)

        text = text.replace("procureContent.procureContent.", "procureContent.")
        if text != original:
            path.write_text(text, encoding="utf-8")
            rel = path.relative_to(target).as_posix()
            print(f"  patched {rel} (useProcureContent i18n)")


def patch_procure_i18n_inline(target: Path) -> None:
    """Fallback when content lives inline (no procure-content import)."""
    for rel in ("components/ProcureLanding.tsx", "app/procure/page.tsx"):
        path = target / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        if "Tus compras" not in text or "useProcureLocalized" in text:
            continue
        if "from \"@/lib/procure-content\"" in text or "from '@/lib/procure-content'" in text:
            continue

        original = text
        text = _add_import(text, 'import { useLang } from "@/lib/LanguageContext";\n')
        text = _add_import(text, 'import { getProcureCopy } from "@/lib/procureLocale";\n')
        text = _add_import(text, 'import { useProcureLocalized } from "@/lib/procureI18n";\n')

        text = re.sub(
            r"(export default function \w+\(\)\s*\{)",
            r"\1\n  const { lang } = useLang();\n  const copy = getProcureCopy(lang);",
            text,
            count=1,
        )
        text = re.sub(
            r'title:\s*\{\s*lead:\s*"Tus compras\."\s*,\s*mid:\s*"Comparadas, verificadas,"\s*,\s*accent:\s*"aprobadas\."\s*\}',
            "title: copy.hero.title",
            text,
        )
        const_match = re.search(r"^const\s+(\w+)\s*=\s*\{", text, re.MULTILINE)
        if const_match:
            var = const_match.group(1)
            if f"useProcureLocalized({var}" not in text:
                text = re.sub(
                    rf"(export default function \w+\(\)\s*\{{)",
                    rf"\1\n  const {var} = useProcureLocalized({var}Raw);",
                    text,
                    count=1,
                )
                text = text.replace(f"const {var} =", f"const {var}Raw =", 1)

        if text != original:
            path.write_text(text, encoding="utf-8")
            print(f"  patched {rel} (inline i18n)")



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
    generate_use_procure_content(target)
    patch_procure_i18n_imports(target)
    patch_procure_i18n_inline(target)
    _verify_no_demo_mailto(target)
    print("\nDone. Next:")
    print("  npm run build")
    print("  npx opennextjs-cloudflare build")
    print("  node scripts/copy-public-assets.mjs")
    print("  npx opennextjs-cloudflare deploy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
