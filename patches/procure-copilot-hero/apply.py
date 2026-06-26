#!/usr/bin/env python3
"""Apply Procure hero terminal patch into procure-copilot checkout.

Fixes:
- demo.gif 920×520 (Procure flow, orange theme) replaces old 820×480 CLI Market gif
- Removes width:155% / margin-left:-27.5% crop hack
- Uses aspect-[920/520] + object-contain so full terminal is visible

Usage (from procure-copilot repo root):
  python3 ../cli-market-world/patches/procure-copilot-hero/apply.py
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

DEMO_BLOCK = re.compile(
    r'<div className="mt-10 w-full max-w-\[820px\] mx-auto text-left">[\s\S]*?'
    r'retailers verificados\s*</p>\s*</div>',
    re.MULTILINE,
)

INLINE_FIXES: list[tuple[str, str]] = [
    ('max-w-[820px]', 'max-w-[920px]'),
    ('width={820}', 'width={920}'),
    ('height={480}', 'height={520}'),
    (
        'style={{height:"272px"}}',
        'className="relative w-full aspect-[920/520] bg-[#0a0a0a]"',
    ),
    (
        'style={{height:272}}',
        'className="relative w-full aspect-[920/520] bg-[#0a0a0a]"',
    ),
    (
        'style={{width:"155%",marginLeft:"-27.5%",height:"auto",display:"block"}}',
        'className="w-full h-full object-contain object-top block"',
    ),
    (
        "style={{width:'155%',marginLeft:'-27.5%',height:'auto',display:'block'}}",
        'className="w-full h-full object-contain object-top block"',
    ),
    ('className="overflow-hidden" style={{height:"272px"}}', 'className="relative w-full aspect-[920/520] bg-[#0a0a0a]"'),
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
    if "MARKET_STATS.retailersVerified" in text:
        return "MARKET_STATS.retailersVerified"
    if "marketStats.retailersVerified" in text:
        return "marketStats.retailersVerified"
    if "RETAILERS_VERIFIED" in text:
        return "RETAILERS_VERIFIED"
    return "40"


def patch_procure_page(target: Path) -> None:
    path = target / "app/procure/page.tsx"
    if not path.exists():
        # Fallback: any file referencing demo.gif
        candidates = list(target.glob("app/**/*.tsx")) + list(target.glob("components/**/*.tsx"))
        for c in candidates:
            if "demo.gif" in c.read_text(encoding="utf-8"):
                path = c
                break
        else:
            print("  skip: no file with demo.gif found")
            return

    text = path.read_text(encoding="utf-8")
    if "ProcureHeroTerminal" in text and "155%" not in text and "272px" not in text:
        print(f"  {path.relative_to(target)} already patched")
        return

    retailers = _retailers_expr(text)
    component_usage = f"<ProcureHeroTerminal retailersVerified={{{retailers}}} />"

    if "ProcureHeroTerminal" not in text:
        if 'from "@/components/ProcureHeroTerminal"' not in text:
            if text.startswith("import "):
                first = text.find("\n", text.find("import "))
                text = (
                    text[: first + 1]
                    + 'import ProcureHeroTerminal from "@/components/ProcureHeroTerminal";\n'
                    + text[first + 1 :]
                )
            else:
                text = (
                    'import ProcureHeroTerminal from "@/components/ProcureHeroTerminal";\n'
                    + text
                )

    replaced = 0
    text, n = DEMO_BLOCK.subn(component_usage, text)
    replaced += n

    for old, new in INLINE_FIXES:
        if old in text:
            text = text.replace(old, new)
            replaced += 1

    if replaced == 0 and "ProcureHeroTerminal" not in text:
        print(f"  warn: could not auto-patch {path.name} — apply INLINE_FIXES manually")

    path.write_text(text, encoding="utf-8")
    print(f"  patched {path.relative_to(target)} ({replaced} replacements)")


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
    patch_procure_page(target)
    print("\nDone. Next:")
    print("  cd", target)
    print("  npm run build")
    print("  npx opennextjs-cloudflare build")
    print("  node scripts/copy-public-assets.mjs")
    print("  npx wrangler deploy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
