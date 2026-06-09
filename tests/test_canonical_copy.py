"""CI guard: deprecated pip package name must not appear in repo copy."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from ops.check_canonical_copy import find_stale_copy


def test_no_stale_pip_install_copy():
    hits = find_stale_copy(REPO_ROOT)
    if hits:
        lines = [f"  {rel}:{line_no} [{label}] {snippet}" for rel, line_no, label, snippet in hits]
        raise AssertionError(
            "Stale GTM copy found (use pip install cli-market-world):\n" + "\n".join(lines)
        )