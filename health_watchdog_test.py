# -*- coding: utf-8 -*-
"""One-shot dry run of health_watchdog.py's checks, without the sleep loop."""
from health_watchdog import check_freshness, heal_system


def main():
    status = check_freshness()
    if status == "stale":
        heal_system()
    elif status == "error":
        print("  ⚠ El sistema de monitoreo tiene un problema.")


if __name__ == "__main__":
    main()
