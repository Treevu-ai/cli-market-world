#!/usr/bin/env python3
"""Apply SEO/GEO patch from cli-market-world into procure-copilot checkout.

Usage (from procure-copilot repo root):
  python3 ../cli-market-world/patches/procure-copilot-seo/apply.py

Or with explicit paths:
  python3 apply.py --target /path/to/procure-copilot --patch /path/to/patch
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def copy_tree(patch: Path, target: Path) -> None:
    for rel in [
        "lib/site.ts",
        "lib/seo.ts",
        "app/dashboard/layout.tsx",
        "public/llms.txt",
        "public/og.svg",
        "public/og.png",
        "scripts/rasterize_og.mjs",
        "scripts/copy-public-assets.mjs",
        "next-sitemap.config.js",
    ]:
        src = patch / rel
        dst = target / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        print(f"  copied {rel}")


def patch_layout(target: Path) -> None:
    path = target / "app/layout.tsx"
    if not path.exists():
        print(f"  skip layout: {path} not found")
        return
    text = path.read_text(encoding="utf-8")
    if "from \"@/lib/seo\"" in text or "from '@/lib/seo'" in text:
        print("  layout.tsx already patched")
        return

    # Remove inline metadata export block (Next Metadata type)
    text = re.sub(
        r"export const metadata(?:: Metadata)?\s*=\s*\{[\s\S]*?\n\};\n",
        "",
        text,
        count=1,
    )
    text = text.replace(
        "procure-copilot.contacto-8e4.workers.dev",
        "procurecopilot.com",
    )

    seo_import = 'import { organizationJsonLd, rootMetadata } from "@/lib/seo";\n'
    if "import type { Metadata }" in text:
        text = text.replace(
            "import type { Metadata } from \"next\";\n",
            "import type { Metadata } from \"next\";\n" + seo_import,
        )
    else:
        text = seo_import + text

    if "export const metadata" not in text:
        text = text.replace(
            seo_import,
            seo_import + "export const metadata: Metadata = rootMetadata;\n\n",
            1,
        )

    json_ld = (
        '<script\n'
        "          type=\"application/ld+json\"\n"
        "          dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationJsonLd) }}\n"
        "        />"
    )
    if "organizationJsonLd" not in text:
        if "<head>" in text:
            text = text.replace("<head>", "<head>\n        " + json_ld, 1)
        elif "<body" in text:
            text = text.replace("<body", "<head>" + json_ld + "</head>\n      <body", 1)

    path.write_text(text, encoding="utf-8")
    print("  patched app/layout.tsx")


def patch_procure_page(target: Path) -> None:
    path = target / "app/procure/page.tsx"
    if not path.exists():
        print(f"  skip procure page: {path} not found")
        return
    text = path.read_text(encoding="utf-8")
    if "procurePageMetadata" in text:
        print("  app/procure/page.tsx already patched")
        return

    if "export const metadata" in text:
        text = re.sub(
            r"export const metadata(?:: Metadata)?\s*=\s*\{[\s\S]*?\n\};\n",
            "",
            text,
            count=1,
        )

    if "from \"@/lib/seo\"" not in text:
        if text.startswith("import "):
            first = text.find("\n", text.find("import "))
            text = (
                text[: first + 1]
                + 'import { procurePageMetadata } from "@/lib/seo";\n'
                + text[first + 1 :]
            )
        else:
            text = 'import { procurePageMetadata } from "@/lib/seo";\n' + text

    if "export const metadata" not in text:
        lines = text.split("\n")
        insert_at = 0
        for i, line in enumerate(lines):
            if line.startswith("import "):
                insert_at = i + 1
        lines.insert(insert_at, "export const metadata = procurePageMetadata;")
        text = "\n".join(lines)

    text = text.replace(
        "procure-copilot.contacto-8e4.workers.dev",
        "procurecopilot.com",
    )
    path.write_text(text, encoding="utf-8")
    print("  patched app/procure/page.tsx")


def patch_package_json(target: Path) -> None:
    path = target / "package.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    scripts = data.setdefault("scripts", {})
    if "next-sitemap" not in scripts.get("build", ""):
        build = scripts.get("build", "next build")
        scripts["build"] = f"{build} && next-sitemap"
    scripts.setdefault(
        "og:png",
        "node scripts/rasterize_og.mjs public/og.svg public/og.png",
    )
    dev = data.setdefault("devDependencies", {})
    dev.setdefault("next-sitemap", "^4.2.3")
    dev.setdefault("@resvg/resvg-js", "^2.6.2")
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print("  patched package.json")


def generate_og_png(target: Path) -> None:
    svg = target / "public/og.svg"
    png = target / "public/og.png"
    script = target / "scripts/rasterize_og.mjs"
    if png.exists():
        print("  og.png exists")
        return
    try:
        subprocess.run(
            ["npm", "install", "@resvg/resvg-js", "--no-save"],
            cwd=target,
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["node", str(script), str(svg), str(png)],
            cwd=target,
            check=True,
        )
        print("  generated public/og.png")
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"  warn: could not generate og.png ({exc}). Run: npm run og:png")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--target",
        type=Path,
        default=Path.cwd(),
        help="procure-copilot repo root",
    )
    parser.add_argument(
        "--patch",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="patch directory",
    )
    args = parser.parse_args()
    target = args.target.resolve()
    patch = args.patch.resolve()

    if not (target / "package.json").exists():
        print(f"error: not a Node project: {target}", file=sys.stderr)
        return 1

    print(f"Applying SEO patch → {target}")
    copy_tree(patch, target)
    patch_layout(target)
    patch_procure_page(target)
    patch_package_json(target)
    generate_og_png(target)
    print("\nDone. Next:")
    print("  cd", target)
    print("  npm install")
    print("  npm run og:png   # if og.png missing")
    print("  npm run build")
    print("  npx wrangler deploy")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
