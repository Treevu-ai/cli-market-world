#!/usr/bin/env python3
"""Apply Procure hero terminal patch into procure-copilot checkout.

Fixes:
- demo.gif 920×520 (Procure flow, orange theme)
- Removes width:155% / margin-left:-27.5% crop hack (any spacing in JSX)
- Replaces inline demo block with ProcureHeroTerminal (GIF-only, no double chrome)

Usage (from procure-copilot repo root):
  python3 ../cli-market-world/patches/procure-copilot-hero/apply.py
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

# Inline demo block (footer may use {stats.retailersVerified} before "retailers verificados")
DEMO_BLOCK = re.compile(
    r'<div className="mt-10 w-full max-w-\[820px\] mx-auto text-left">[\s\S]*?'
    r"retailers verificados[\s\S]*?</p>\s*</div>",
    re.MULTILINE,
)

# Loose patterns — procure-copilot formats JSX with spaces inside {{ }}
CROP_HEIGHT = re.compile(
    r'className="overflow-hidden"\s+style=\{\{\s*height:\s*["\']?272px?["\']?\s*\}\}',
)
CROP_STYLE = re.compile(
    r'style=\{\{\s*width:\s*["\']155%["\']\s*,\s*marginLeft:\s*["\']-27\.5%["\']\s*,'
    r'\s*height:\s*["\']auto["\']\s*,\s*display:\s*["\']block["\']\s*\}\}',
)
IMG_DIMS = re.compile(r'\bwidth=\{?820\}?\s+height=\{?480\}?')

INLINE_REPLACEMENTS: list[tuple[re.Pattern[str], str]] = [
    (CROP_HEIGHT, 'className="relative w-full bg-[#0a0a0a]"'),
    (
        CROP_STYLE,
        'className="w-full h-auto block"',
    ),
    (IMG_DIMS, f"width={920} height={520}"),
    (re.compile(r"max-w-\[820px\]"), "max-w-full"),
]


def copy_tree(patch: Path, target: Path) -> None:
    for rel in [
        "components/ProcureHeroTerminal.tsx",
        "public/demo.gif",
    ]:
        src = patch / rel
        dst = target / rel
        if not src.exists():
            print(f"  warn: missing patch file {rel}")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"  copied {rel}")


def _retailers_expr(text: str) -> str:
    for expr in (
        "MARKET_STATS.retailersVerified",
        "marketStats.retailersVerified",
        "stats.retailersVerified",
        "n.g.retailersVerified",
    ):
        if expr in text:
            return expr
    if "RETAILERS_VERIFIED" in text:
        return "RETAILERS_VERIFIED"
    if re.search(r'from\s+["\']@/lib/market-stats["\']', text):
        return "stats.retailersVerified"
    return "40"


def _tsx_files(target: Path) -> list[Path]:
    roots = [target / "app", target / "components"]
    files: list[Path] = []
    for root in roots:
        if root.is_dir():
            files.extend(root.rglob("*.tsx"))
    return sorted(set(files))


def _add_import(text: str) -> str:
    imp = 'import ProcureHeroTerminal from "@/components/ProcureHeroTerminal";\n'
    if imp.strip() in text or "ProcureHeroTerminal" not in text:
        return text
    if text.startswith('"use client"') or text.startswith("'use client'"):
        end = text.find("\n") + 1
        return text[:end] + "\n" + imp + text[end:]
    if text.startswith("import "):
        first = text.find("\n", text.find("import "))
        return text[: first + 1] + imp + text[first + 1 :]
    return imp + text


def patch_file(path: Path, retailers: str) -> int:
    text = path.read_text(encoding="utf-8")
    if "demo.gif" not in text and "155%" not in text and "272px" not in text:
        return 0

    original = text
    replaced = 0
    retailers_local = _retailers_expr(text)

    component_usage = f"<ProcureHeroTerminal retailersVerified={{{retailers_local}}} />"
    text, n = DEMO_BLOCK.subn(component_usage, text)
    replaced += n

    for pattern, repl in INLINE_REPLACEMENTS:
        text, n = pattern.subn(repl, text)
        replaced += n

    # Legacy exact strings (no spaces)
    for old, new in [
        ('style={{height:"272px"}}', 'className="relative w-full bg-[#0a0a0a]"'),
        (
            'style={{width:"155%",marginLeft:"-27.5%",height:"auto",display:"block"}}',
            'className="w-full h-auto block"',
        ),
        ("width={820}", "width={920}"),
        ("height={480}", "height={520}"),
    ]:
        if old in text:
            text = text.replace(old, new)
            replaced += 1

    if text != original:
        if "ProcureHeroTerminal" in text:
            text = _add_import(text)
        path.write_text(text, encoding="utf-8")
        print(f"  patched {path.name} ({replaced} changes)")
    return replaced


def patch_procure_repo(target: Path) -> None:
    files = _tsx_files(target)
    demo_files = [f for f in files if "demo.gif" in f.read_text(encoding="utf-8")]
    if not demo_files:
        print("  warn: no .tsx with demo.gif under app/ or components/")
        return

    retailers = "40"
    for f in demo_files:
        retailers = _retailers_expr(f.read_text(encoding="utf-8"))

    total = 0
    for f in demo_files:
        total += patch_file(f, retailers)

    # Also patch any file that still has the crop hack (inline helper in page.tsx)
    for f in files:
        raw = f.read_text(encoding="utf-8")
        if "155%" in raw or "272px" in raw or 'marginLeft:"-27.5%' in raw:
            total += patch_file(f, retailers)

    if total == 0:
        print("  warn: no changes applied — check demo markup manually")


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

    print(f"Applying hero patch → {target}")
    copy_tree(patch, target)
    patch_procure_repo(target)
    print("\nDone. Rebuild and deploy:")
    print("  npm run build")
    print("  npx opennextjs-cloudflare build")
    print("  node scripts/copy-public-assets.mjs")
    print("  npx wrangler deploy")
    print("\nVerify HTML has NO '155%' and NO '272px' in /procure source.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
