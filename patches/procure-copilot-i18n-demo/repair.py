#!/usr/bin/env python3
"""Fix syntax errors from a broken apply.py run on ProcureLanding.tsx.

From procure-copilot repo root:
  python patches/procure-copilot-i18n-demo/repair.py
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def repair_procure_landing(path: Path) -> bool:
    if not path.exists():
        print(f"skip: {path} not found")
        return False

    text = path.read_text(encoding="utf-8")
    original = text

    # Bad patch wrote: lang === \"en\"
    text = text.replace('lang === \\"en\\";', 'lang === "en";')
    text = text.replace('lang === \\"en\\"', 'lang === "en"')
    text = text.replace("lang === \\\"en\\\";", 'lang === "en";')

    # Undo risky string→literal swaps inside TS object literals
    text = re.sub(
        r"lead:\s*'\{copy\.hero\.title\.lead\}'",
        'lead: "Tus compras."',
        text,
    )
    text = re.sub(
        r"mid:\s*'\{copy\.hero\.title\.mid\}'",
        'mid: "Comparadas, verificadas,"',
        text,
    )
    text = re.sub(
        r"accent:\s*'\{copy\.hero\.title\.accent\}'",
        'accent: "aprobadas."',
        text,
    )

    if text != original:
        path.write_text(text, encoding="utf-8")
        print(f"repaired {path}")
        return True

    print(f"no changes needed in {path}")
    return False


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=Path, default=Path.cwd())
    args = parser.parse_args()
    target = args.target.resolve()
    repair_procure_landing(target / "components/ProcureLanding.tsx")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
