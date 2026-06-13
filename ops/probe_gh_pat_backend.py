#!/usr/bin/env python3
"""Probe whether GH_PAT can read Treevu-ai/cli-market-backend (CI contract parity gate)."""

from __future__ import annotations

import os
import sys
import urllib.error
import urllib.request

REPO_API = "https://api.github.com/repos/Treevu-ai/cli-market-backend"


def gh_pat_can_read_backend(token: str | None = None) -> bool:
    token = (token or os.environ.get("GH_PAT") or "").strip()
    if not token:
        return False
    req = urllib.request.Request(
        REPO_API,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "cli-market-world-probe",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.status == 200
    except urllib.error.HTTPError as exc:
        return exc.code == 200
    except OSError:
        return False


def main() -> int:
    token = (os.environ.get("GH_PAT") or "").strip()
    ok = gh_pat_can_read_backend(token)

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as fh:
            fh.write(f"ok={'true' if ok else 'false'}\n")

    if ok:
        print("GH_PAT can read cli-market-backend — contract parity required")
    elif token:
        print(
            "::warning::GH_PAT cannot read Treevu-ai/cli-market-backend — "
            "contract parity skipped (add Contents: Read on backend repo)"
        )
    else:
        print("::warning::GH_PAT not set — contract parity skipped")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
