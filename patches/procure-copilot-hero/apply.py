#!/usr/bin/env python3
"""Apply Procure hero redesign: remove demo.gif, add supermarket aisle background.

Usage (from procure-copilot repo root):
  python patches/procure-copilot-hero/apply.py

Or download install-hero.ps1 from GitHub and run it.
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

COPY_FILES = [
    "components/ProcureHeroBackground.tsx",
    "components/ProcureDemo.tsx",
    "public/hero-supermarket.webp",
]

REMOVE_PATHS = [
    "public/demo.gif",
    "components/ProcureHeroTerminal.tsx",
]

DEMO_GIF_REF = re.compile(r'["\']/demo\.gif["\']')
PRELOAD_DEMO = re.compile(r'<link rel="preload" as="image" href="/demo\.gif"\s*/>\s*')


def copy_tree(patch: Path, target: Path) -> None:
    for rel in COPY_FILES:
        src = patch / rel
        dst = target / rel
        if not src.exists():
            print(f"  warn: missing {rel}")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"  copied {rel}")


def remove_artifacts(target: Path) -> None:
    for rel in REMOVE_PATHS:
        path = target / rel
        if path.exists():
            path.unlink()
            print(f"  removed {rel}")


def _add_import(text: str, imp_line: str) -> str:
    if imp_line.strip() in text:
        return text
    if text.startswith('"use client"') or text.startswith("'use client'"):
        end = text.find("\n") + 1
        return text[:end] + "\n" + imp_line + text[end:]
    if text.startswith("import "):
        first = text.find("\n", text.find("import "))
        return text[: first + 1] + imp_line + text[first + 1 :]
    return imp_line + text


HERO_SECTION = re.compile(r'<section\s+id="hero"\s+className="([^"]*)"', re.DOTALL)


def _hero_section_classes(cls: str) -> str:
    if "relative" not in cls:
        cls = f"{cls} relative"
    if "overflow-hidden" not in cls:
        cls = f"{cls} overflow-hidden"
    return cls


def _mount_hero_background(text: str) -> str:
    if 'id="hero"' not in text:
        return text

    bg_import = 'import ProcureHeroBackground from "@/components/ProcureHeroBackground";\n'
    text = _add_import(text, bg_import)

    if "<ProcureHeroBackground" not in text:
        text = re.sub(
            r'(<section\s+id="hero"[^>]*>)',
            r"\1\n      <ProcureHeroBackground />",
            text,
            count=1,
        )

    def _fix_hero_classes(m: re.Match[str]) -> str:
        return f'<section id="hero" className="{_hero_section_classes(m.group(1))}"'

    text = HERO_SECTION.sub(_fix_hero_classes, text, count=1)

    def _fix_inner_z(m: re.Match[str]) -> str:
        cls = m.group(2)
        if "relative" not in cls:
            cls = f"{cls} relative"
        if "z-10" not in cls:
            cls = f"{cls} z-10"
        return f"{m.group(1)}{cls}{m.group(3)}"

    text = re.sub(
        r'(<ProcureHeroBackground\s*/>\s*<div\s+className=")([^"]*)(")',
        _fix_inner_z,
        text,
        count=1,
    )
    return text


def _strip_demo_ui(text: str) -> str:
    text = re.sub(
        r'<motion\.div[^>]*\bid="demo"[^>]*>[\s\S]*?</motion\.div>\s*',
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(
        r'<motion\.div[^>]*className="[^"]*lg:hidden[^"]*mt-10[^"]*"[^>]*>[\s\S]*?</motion\.div>\s*',
        "",
        text,
        flags=re.IGNORECASE,
    )
    text = re.sub(r"\s*<ProcureDemo\s*/>\s*", "\n", text)
    text = re.sub(r'import ProcureDemo from ["\']@/components/ProcureDemo["\'];\n', "", text)
    text = re.sub(r'import ProcureHeroTerminal from ["\']@/components/ProcureHeroTerminal["\'];\n', "", text)
    return text


def patch_hero_file(target: Path, rel: str, *, strip_demo: bool = False) -> None:
    path = target / rel
    if not path.exists():
        print(f"  skip: {rel} not found")
        return

    text = path.read_text(encoding="utf-8")
    original = text
    text = _mount_hero_background(text)
    if strip_demo:
        text = _strip_demo_ui(text)

    if 'id="hero"' in text and "<ProcureHeroBackground" not in text:
        print(f"  WARN: ProcureHeroBackground not mounted in {rel} — see TROUBLESHOOTING.md")

    if text != original:
        path.write_text(text, encoding="utf-8")
        print(f"  patched {rel}")


def patch_procure_page(target: Path) -> None:
    patch_hero_file(target, "app/procure/page.tsx", strip_demo=True)


def patch_procure_landing(target: Path) -> None:
    patch_hero_file(target, "components/ProcureLanding.tsx")


def patch_content_lib(target: Path) -> None:
    path = target / "lib/procure-content.ts"
    if not path.exists():
        return
    text = path.read_text(encoding="utf-8")
    new = DEMO_GIF_REF.sub('"/og.png"', text)
    if new != text:
        path.write_text(new, encoding="utf-8")
        print("  patched lib/procure-content.ts (og image)")


def scrub_demo_gif_refs(target: Path) -> None:
    roots = [target / "app", target / "components", target / "lib"]
    for root in roots:
        if not root.is_dir():
            continue
        for path in root.rglob("*"):
            if path.suffix not in {".tsx", ".ts", ".jsx", ".js", ".md"}:
                continue
            if path.name == "ProcureDemo.tsx":
                continue
            text = path.read_text(encoding="utf-8")
            if "/demo.gif" not in text:
                continue
            new = DEMO_GIF_REF.sub('"/og.png"', text)
            new = PRELOAD_DEMO.sub("", new)
            if new != text:
                path.write_text(new, encoding="utf-8")
                print(f"  scrubbed demo.gif in {path.relative_to(target)}")


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

    print(f"Applying hero background patch → {target}")
    copy_tree(patch, target)
    remove_artifacts(target)
    patch_procure_landing(target)
    patch_procure_page(target)
    patch_content_lib(target)
    scrub_demo_gif_refs(target)
    print("\nDone. Next:")
    print("  npm run build")
    print("  npx opennextjs-cloudflare build")
    print("  node scripts/copy-public-assets.mjs")
    print("  git add -A && git commit && git push origin main")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
