"""
cli-market-integrate — entry point for all CRM adapters.

Usage:
  cli-market-integrate simla   [--host HOST] [--port PORT] [--reload]
  cli-market-integrate hubspot [--host HOST] [--port PORT] [--reload]
  cli-market-integrate zoho    [--host HOST] [--port PORT] [--reload]
  cli-market-integrate --list
"""
from __future__ import annotations

import argparse
import os
import sys


ADAPTERS = {
    "simla":   ("cli_market_integrations.adapters.simla.app:app",   8000),
    "hubspot": ("cli_market_integrations.adapters.hubspot.app:app", 8001),
    "zoho":    ("cli_market_integrations.adapters.zoho.app:app",    8002),
    "kommo":   ("cli_market_integrations.adapters.kommo.app:app",   8003),
}


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="cli-market-integrate",
        description="Start a CLI Market CRM integration adapter",
    )
    parser.add_argument(
        "adapter",
        nargs="?",
        choices=list(ADAPTERS.keys()),
        help="CRM adapter to run (simla | hubspot | zoho | kommo)",
    )
    parser.add_argument("--host", default=os.getenv("SERVER_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=None)
    parser.add_argument("--reload", action="store_true", help="Enable hot-reload (dev only)")
    parser.add_argument("--list", action="store_true", help="List available adapters")

    args = parser.parse_args()

    if args.list or not args.adapter:
        print("Available adapters:")
        for name, (app_path, default_port) in ADAPTERS.items():
            print(f"  {name:<10} default port {default_port}  →  {app_path}")
        sys.exit(0)

    app_path, default_port = ADAPTERS[args.adapter]
    port = args.port or int(os.getenv("SERVER_PORT", str(default_port)))

    try:
        import uvicorn
    except ImportError:
        print("uvicorn not installed. Run: pip install 'cli-market-integrations[serve]'")
        sys.exit(1)

    print(f"Starting {args.adapter} adapter on {args.host}:{port}")
    uvicorn.run(app_path, host=args.host, port=port, reload=args.reload)


if __name__ == "__main__":
    main()
