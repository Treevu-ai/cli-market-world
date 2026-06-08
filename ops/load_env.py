"""Load SLACK_* and MARKET_* from repo .env files (best-effort, no extra deps)."""

from __future__ import annotations

import os
from pathlib import Path


def load_repo_env() -> None:
    root = Path(__file__).resolve().parent.parent
    for path in (root / ".env", root / "ops" / ".env", root / "ops" / ".rotation-local.txt"):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].strip()
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = value