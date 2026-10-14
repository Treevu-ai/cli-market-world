"""Local-only guard: cli-market-api must stay stopped on Fly.

fly.toml's auto_start_machines=true (the live deployed config -- editing
the local file doesn't change it until the next `fly deploy`, see fly.toml
comment) means any stray request to cli-market-api.fly.dev silently
restarts its machines. Confirmed happening once already (2026-10-14).

Run on a schedule (Windows Task Scheduler) until either the Fly billing
block is resolved so `fly machine update --autostart=false` can be applied
directly, or a deploy picks up the fly.toml change. Idempotent and quiet
when there's nothing to do; logs only when it actually stops a machine.
"""

import json
import subprocess
import sys
from datetime import datetime, timezone

APP = "cli-market-api"
FLY = r"C:\Users\acuba\.fly\bin\fly.exe"


def main() -> int:
    result = subprocess.run(
        [FLY, "machine", "list", "-a", APP, "--json"],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        print(f"[{datetime.now(timezone.utc).isoformat()}] fly machine list failed: {result.stderr.strip()}")
        return 1

    machines = json.loads(result.stdout)
    running = [m for m in machines if m.get("state") not in ("stopped", "stopping")]
    if not running:
        return 0  # quiet — nothing to do

    for m in running:
        mid = m["id"]
        print(f"[{datetime.now(timezone.utc).isoformat()}] {APP}/{mid} was '{m.get('state')}' -- stopping it")
        stop = subprocess.run([FLY, "machine", "stop", mid, "-a", APP], capture_output=True, text=True)
        if stop.returncode != 0:
            print(f"  failed: {stop.stderr.strip()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
