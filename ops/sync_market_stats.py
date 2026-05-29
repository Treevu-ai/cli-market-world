#!/usr/bin/env python3
"""Emit landing/lib/marketStats.ts and sync README, PyPI, server.json from market_stats.py."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import market_stats as s

OUT_TS = ROOT / "landing" / "lib" / "marketStats.ts"


def write_market_stats_ts() -> None:
    ts = f"""// AUTO-GENERATED — do not edit. Run: python3 ops/sync_market_stats.py

export const MARKET_STATS = {{
  retailersDefined: {s.RETAILERS_DEFINED},
  retailersVerified: {s.RETAILERS_VERIFIED},
  platforms: {s.PLATFORMS},
  platformVtex: {s.PLATFORM_VTEX},
  platformShopify: {s.PLATFORM_SHOPIFY},
  platformMagento: {s.PLATFORM_MAGENTO},
  countries: {s.COUNTRIES},
  countryCodes: {list(s.COUNTRY_CODES)!r},
  mcpTools: {s.MCP_TOOLS},
  pricesVerifiedLabel: "{s.PRICES_VERIFIED_LABEL}",
  pricesRefreshHours: {s.PRICES_REFRESH_HOURS},
  packageVersion: "{s.PACKAGE_VERSION}",
  license: "{s.LICENSE}",
  paymentsLabel: "{s.PAYMENTS_LABEL}",
  businessLines: {s.BUSINESS_LINES},
  retailersPhraseEn: "{s.RETAILERS_PHRASE_EN}",
  retailersPhraseEs: "{s.RETAILERS_PHRASE_ES}",
  platformsPhraseEn: "{s.PLATFORMS_PHRASE_EN}",
  platformsPhraseEs: "{s.PLATFORMS_PHRASE_ES}",
  headerEn: {json.dumps(s.header_en())},
  headerEs: {json.dumps(s.header_es())},
  shopifyBrands: {json.dumps(list(s.SHOPIFY_BRANDS))},
  seoDescription: {json.dumps(s.seo_description())},
  serverDescription: {json.dumps(s.server_json_description())},
}} as const;
"""
    OUT_TS.write_text(ts, encoding="utf-8")
    print(f"Wrote {OUT_TS}")


def sync_readme() -> None:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r'<img src="https://img\.shields\.io/badge/retailers-\d+-brightgreen" alt="[^"]*">',
        f'<img src="https://img.shields.io/badge/retailers-{s.RETAILERS_DEFINED}-brightgreen" alt="{s.RETAILERS_DEFINED} retailers">',
        text,
    )
    text = re.sub(
        r'<img src="https://img\.shields\.io/badge/platforms-\d+-blue" alt="[^"]*">',
        f'<img src="https://img.shields.io/badge/platforms-{s.PLATFORMS}-blue" alt="{s.PLATFORMS} platforms">',
        text,
    )
    text = re.sub(
        r"<p align=\"center\"><b>Commerce infrastructure for AI agents\.</b><br>.*?</p>",
        f'<p align="center">{s.readme_tagline_html()}</p>',
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = text.replace(
        "One API call across 30 verified retailers.",
        f"One API call across {s.RETAILERS_DEFINED} retailers ({s.RETAILERS_VERIFIED} verified).",
    )
    text = text.replace(
        "any product across 30 verified retailers in 8 countries",
        f"any product across {s.RETAILERS_VERIFIED} verified retailers in {s.COUNTRIES} countries",
    )
    path.write_text(text, encoding="utf-8")
    print(f"Synced {path}")


def sync_pyproject() -> None:
    path = ROOT / "pyproject.toml"
    text = path.read_text(encoding="utf-8")
    desc = s.pypi_summary().replace('"', '\\"')
    text = re.sub(
        r'^description = ".*"$',
        f'description = "{desc}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
    path.write_text(text, encoding="utf-8")
    print(f"Synced {path}")


def sync_server_json() -> None:
    desc = s.server_json_description()
    for rel in ("server.json", "landing/public/server.json"):
        path = ROOT / rel
        data = json.loads(path.read_text(encoding="utf-8"))
        data["description"] = desc
        data["version"] = s.PACKAGE_VERSION
        if data.get("packages"):
            data["packages"][0]["version"] = s.PACKAGE_VERSION
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"Synced {path}")


def main() -> None:
    write_market_stats_ts()
    sync_readme()
    sync_pyproject()
    sync_server_json()


if __name__ == "__main__":
    main()
