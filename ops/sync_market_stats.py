#!/usr/bin/env python3
"""Emit landing/lib/marketStats.ts and sync README, PyPI, server.json from market_stats.py."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE_ROOT = ROOT.parent / "cli-market-core"
for p in (ROOT, CORE_ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from market_core import market_stats as s
from market_core.market_mcp_registry import (
    TOOLS,
    get_tool_meta,
    list_tools,
    public_tool_count,
    tool_in_profile,
)

OUT_TS = ROOT / "landing" / "lib" / "marketStats.ts"

_BUNDLE_PREFIXES = ("[Shop] ", "[Intel] ", "[Account] ", "[Advanced] ", "[Admin] ")
_CANONICAL_HIGHLIGHTS = frozenset({"market_discover", "market_intel_brief", "market_price_alerts"})
_PUBLIC_BUNDLES = ("shop", "intel", "account")


def _strip_bundle_prefix(description: str) -> str:
    for prefix in _BUNDLE_PREFIXES:
        if description.startswith(prefix):
            return description[len(prefix) :]
    return description


def _mcp_counts() -> dict[str, int]:
    return {
        "default": public_tool_count("default"),
        "legacy": public_tool_count("legacy"),
        "full": public_tool_count("full"),
    }


def _bundle_tools_for_landing(profile: str = "default") -> dict[str, list[dict[str, str | bool]]]:
    bundles: dict[str, list[dict[str, str | bool]]] = {b: [] for b in _PUBLIC_BUNDLES}
    for tool in TOOLS:
        name = tool["name"]
        meta = get_tool_meta(name)
        if not meta or meta["bundle"] not in bundles or not tool_in_profile(name, profile):
            continue
        bundles[meta["bundle"]].append(
            {
                "id": name,
                "description": _strip_bundle_prefix(tool["description"]),
                "canonical": name in _CANONICAL_HIGHLIGHTS,
            }
        )
    for items in bundles.values():
        items.sort(key=lambda t: (not t["canonical"], t["id"]))
    return bundles


def _replace_mcp_count(text: str, old: int, new: int, *, es: bool = False) -> str:
    replacements = [
        (f"{old} MCP tools", f"{new} MCP tools"),
        (f"{old} herramientas MCP", f"{new} herramientas MCP"),
        (f"{old} curated MCP tools", f"{new} curated MCP tools"),
    ]
    if es:
        replacements = [
            (f"{old} herramientas MCP", f"{new} herramientas MCP"),
            (f"{old} MCP tools", f"{new} MCP tools"),
        ]
    out = text
    for old_phrase, new_phrase in replacements:
        out = out.replace(old_phrase, new_phrase)
    return out


def write_market_stats_ts() -> None:
    counts = _mcp_counts()
    bundles = _bundle_tools_for_landing("default")
    header_en = _replace_mcp_count(s.header_en(), s.MCP_TOOLS, counts["default"])
    header_es = _replace_mcp_count(s.header_es(), s.MCP_TOOLS, counts["default"], es=True)
    seo = _replace_mcp_count(s.seo_description(), s.MCP_TOOLS, counts["default"])
    server_desc = _replace_mcp_count(s.server_json_description(), s.MCP_TOOLS, counts["default"])
    ts = f"""// AUTO-GENERATED — do not edit. Run: python3 ops/sync_market_stats.py

export const MARKET_STATS = {{
  retailersDefined: {s.RETAILERS_DEFINED},
  retailersVerified: {s.RETAILERS_VERIFIED},
  platforms: {s.PLATFORMS},
  platformVtex: {s.PLATFORM_VTEX},
  platformShopify: {s.PLATFORM_SHOPIFY},
  platformMagento: {s.PLATFORM_MAGENTO},
  platformWooCommerce: {s.PLATFORM_WOOCOMMERCE},
  woocommerceStores: {json.dumps(list(s.WOOCOMMERCE_STORES))},
  countries: {s.COUNTRIES},
  countryCodes: {list(s.COUNTRY_CODES)!r},
  mcpTools: {counts["default"]},
  mcpToolsLegacy: {counts["legacy"]},
  mcpToolsFull: {counts["full"]},
  mcpDefaultProfile: "default",
  mcpBundles: {json.dumps(bundles, ensure_ascii=False)},
  indicatorsCount: {s.INDICATORS_COUNT},
  enrichmentSourcesLabel: "{s.ENRICHMENT_SOURCES_LABEL}",
  pricesVerifiedLabel: "{s.PRICES_VERIFIED_LABEL}",
  pricesRefreshHours: {s.PRICES_REFRESH_HOURS},
  pypiPackageName: "{s.PYPI_PACKAGE_NAME}",
  pypiUrl: "{s.PYPI_URL}",
  pepyProjectUrl: "{s.PEPY_PROJECT_URL}",
  pepyBadgeUrl: "{s.PEPY_BADGE_URL}",
  pipInstallCmd: "{s.PIP_INSTALL_CMD}",
  packageVersion: "{s.PACKAGE_VERSION}",
  license: "{s.LICENSE}",
  paymentsLabel: "{s.PAYMENTS_LABEL}",
  businessLines: {s.BUSINESS_LINES},
  retailersPhraseEn: "{s.RETAILERS_PHRASE_EN}",
  retailersPhraseEs: "{s.RETAILERS_PHRASE_ES}",
  platformsPhraseEn: "{s.PLATFORMS_PHRASE_EN}",
  platformsPhraseEs: "{s.PLATFORMS_PHRASE_ES}",
  headerEn: {json.dumps(header_en)},
  headerEs: {json.dumps(header_es)},
  shopifyBrands: {json.dumps(list(s.SHOPIFY_BRANDS))},
  seoDescription: {json.dumps(seo)},
  serverDescription: {json.dumps(server_desc)},
}} as const;
"""
    OUT_TS.write_text(ts, encoding="utf-8")
    print(f"Wrote {OUT_TS}")


def sync_readme() -> None:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r"\[!\[PyPI Downloads\]\([^)]+\)\]\([^)]+\)",
        f"[![PyPI Downloads]({s.PEPY_BADGE_URL})]({s.PEPY_PROJECT_URL})",
        text,
        count=1,
    )
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
    mcp_default = public_tool_count("default")
    mcp_legacy = public_tool_count("legacy")
    text = re.sub(
        r'<img src="https://img\.shields\.io/badge/MCP%20tools-\d+-00d75f" alt="[^"]*">',
        f'<img src="https://img.shields.io/badge/MCP%20tools-{mcp_default}-00d75f" alt="{mcp_default} curated MCP tools ({mcp_legacy} legacy)">',
        text,
    )
    text = re.sub(
        r"## \d+ MCP tools",
        f"## {mcp_default} MCP tools (default profile)",
        text,
        count=1,
    )
    text = re.sub(
        r"<p align=\"center\"><b>Commerce infrastructure for AI agents\.</b><br>.*?</p>",
        f'<p align="center">{s.readme_tagline_html()}</p>',
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"├── market_mcp\.py            → MCP server \(\d+ tools\)",
        f"├── market_mcp.py            → MCP server ({mcp_default} default / {mcp_legacy} legacy)",
        text,
        count=1,
    )
    text = text.replace(
        "One API call across 30 verified retailers.",
        f"One API call across {s.RETAILERS_DEFINED} retailers ({s.RETAILERS_VERIFIED} verified).",
    )
    text = text.replace(
        "any product across 30 verified retailers in 8 countries",
        f"any product across {s.RETAILERS_VERIFIED} verified retailers in {s.COUNTRIES} countries",
    )
    # Spanish: verified prices label (catches both "39 000+" and "39,000+")
    text = re.sub(
        r"\*\*Más de [\d,. ]+\+? precios de góndola verificados\*\*",
        f"**Más de {s.PRICES_VERIFIED_LABEL} precios de góndola verificados**",
        text,
    )
    text = re.sub(
        r"\*\*[\d,]+\+ verified shelf prices\*\*",
        f"**{s.PRICES_VERIFIED_LABEL} verified shelf prices**",
        text,
    )
    # Spanish: retailers + countries in body text (bold and plain)
    text = re.sub(
        r"\d+ retailers \(\d+ verificados\)",
        f"{s.RETAILERS_DEFINED} retailers ({s.RETAILERS_VERIFIED} verificados)",
        text,
    )
    text = re.sub(
        r"\d+ retailers, \d+ verified active(?! en)",
        f"{s.RETAILERS_DEFINED} retailers, {s.RETAILERS_VERIFIED} verified active",
        text,
    )
    text = re.sub(
        r"\d+ retailers \(\d+ verified\)",
        f"{s.RETAILERS_DEFINED} retailers ({s.RETAILERS_VERIFIED} verified)",
        text,
    )
    text = re.sub(
        r"\d+ verified active\b",
        f"{s.RETAILERS_VERIFIED} verified active",
        text,
    )
    # Countries count (both bold and plain)
    text = re.sub(
        r"\b\d+ países\b",
        f"{s.COUNTRIES} países",
        text,
    )
    text = re.sub(
        r"\b\d+ countries\b",
        f"{s.COUNTRIES} countries",
        text,
    )
    # Indicators count
    text = re.sub(
        r"· \d+ indicadores\b",
        f"· {s.INDICATORS_COUNT} indicadores",
        text,
    )
    text = re.sub(
        r"· \d+ indicators\b",
        f"· {s.INDICATORS_COUNT} indicators",
        text,
    )
    path.write_text(text, encoding="utf-8")
    print(f"Synced {path}")


def sync_pyproject() -> None:
    path = ROOT / "pyproject.toml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r'^version = ".*"$',
        f'version = "{s.PACKAGE_VERSION}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
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


def _mcp_bundle_manifest(profile: str = "default") -> dict[str, list[str]]:
    bundles: dict[str, list[str]] = {b: [] for b in _PUBLIC_BUNDLES}
    for tool in TOOLS:
        name = tool["name"]
        meta = get_tool_meta(name)
        if not meta or meta["bundle"] not in bundles or not tool_in_profile(name, profile):
            continue
        bundles[meta["bundle"]].append(name)
    return bundles


def sync_mcp_json() -> None:
    counts = _mcp_counts()
    default_tools = [t["name"] for t in list_tools("default")]
    legacy_tools = [t["name"] for t in list_tools("legacy")]
    bundle_manifest = _mcp_bundle_manifest("default")
    path = ROOT / "landing" / "public" / "mcp.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["description"] = (
        f"Commerce infrastructure for AI agents — {counts['default']} curated MCP tools "
        f"({counts['legacy']} legacy) to search, compare, and purchase across "
        f"{s.RETAILERS_VERIFIED} retailers in {s.COUNTRIES} countries. "
        f"{s.PRICES_VERIFIED_LABEL} real prices, {s.INDICATORS_COUNT} market indicators, "
        f"refreshed every {s.PRICES_REFRESH_HOURS} hours. MIT."
    )
    data["default_profile"] = "default"
    data["profiles"] = {
        "default": {"tool_count": counts["default"], "description": "Curated Shop + Intel + Account bundles"},
        "full": {"tool_count": counts["full"], "description": "Default plus advanced tools and legacy aliases"},
        "legacy": {"tool_count": counts["legacy"], "description": "All registered tools (backward compatible)"},
    }
    data["bundles"] = {
        key: {
            "label": key.capitalize(),
            "tools": names,
            "canonical": [n for n in names if n in _CANONICAL_HIGHLIGHTS],
        }
        for key, names in bundle_manifest.items()
    }
    data["tools"] = default_tools
    data["tools_legacy"] = legacy_tools
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Synced {path}")
    root = ROOT / "mcp.json"
    root.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Synced {root}")


def sync_og_svg() -> None:
    path = ROOT / "landing" / "public" / "og.svg"
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r"\d+ MCP tools \| pip install",
        f"{public_tool_count('default')} MCP tools | pip install",
        text,
        count=1,
    )
    text = text.replace("pip install cli-market", s.PIP_INSTALL_CMD)
    path.write_text(text, encoding="utf-8")
    print(f"Synced {path}")


def sync_og_preview_svg() -> None:
    path = ROOT / "landing" / "public" / "og-preview.svg"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"\d+ MCP", f"{public_tool_count('default')} MCP", text, count=1)
    text = text.replace("pip install cli-market", s.PIP_INSTALL_CMD)
    path.write_text(text, encoding="utf-8")
    print(f"Synced {path}")


def _llms_bundle_section() -> str:
    counts = _mcp_counts()
    bundle_manifest = _mcp_bundle_manifest("default")
    lines = [
        f"## MCP tool bundles (default profile: {counts['default']} curated tools)",
        "",
        "Set `MCP_TOOL_PROFILE=default` (recommended) or `legacy` "
        f"({counts['legacy']} tools, includes deprecated aliases).",
        "",
    ]
    for key in _PUBLIC_BUNDLES:
        names = bundle_manifest[key]
        canonical = [n for n in names if n in _CANONICAL_HIGHLIGHTS]
        lines.append(f"### {key.capitalize()} ({len(names)} tools)")
        if canonical:
            lines.append(f"Canonical: {', '.join(canonical)}")
        lines.append(", ".join(names))
        lines.append("")
    lines.extend(
        [
            "## Recommended flows by ICP",
            "",
            "### Builder / AI agent",
            "1. `market_discover` → `market_search` → `market_compare` → `market_basket`",
            "2. `market_login` → `market_add` → `market_cart` → `market_checkout` (Pro tier)",
            "",
            "### Research / fintech",
            "1. `market_intel_brief` → `market_inflation` → `market_scores`",
            "2. `market_export` for CSV/JSON pulls; `market_trending` for category momentum",
            "",
            "### Authenticated user",
            "1. `market_whoami` → `market_preferences` → `market_price_alerts`",
            "2. `market_favorites` + `market_subscription` for account management",
            "",
        ]
    )
    return "\n".join(lines)


def sync_llms_txt() -> None:
    counts = _mcp_counts()
    for rel in ("landing/public/llms.txt",):
        path = ROOT / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        text = text.replace("pip install cli-market", s.PIP_INSTALL_CMD)
        text = text.replace("pip install cli-market-world-world-world", s.PIP_INSTALL_CMD)
        text = text.replace("https://pypi.org/project/cli-market/", s.PYPI_URL)
        text = re.sub(
            r"- \d+ MCP tools \(.*?\)",
            f"- {counts['default']} curated MCP tools (Shop · Intel · Account; {counts['legacy']} legacy)",
            text,
            count=1,
        )
        text = re.sub(
            r"- \*\*Predictable Tools\*\*: \d+ MCP tools with standardized primitives\.",
            f"- **Predictable Tools**: {counts['default']} curated MCP tools in Shop/Intel/Account bundles.",
            text,
            count=1,
        )
        path.write_text(text, encoding="utf-8")
        print(f"Synced {path}")

    full_path = ROOT / "landing/public/llms-full.txt"
    if full_path.exists():
        text = full_path.read_text(encoding="utf-8")
        text = text.replace("pip install cli-market", s.PIP_INSTALL_CMD)
        text = text.replace("pip install cli-market-world-world-world", s.PIP_INSTALL_CMD)
        text = text.replace("https://pypi.org/project/cli-market/", s.PYPI_URL)
        text = re.sub(
            r"## \d+ MCP tools\n\n.*?(?=\n## Countries:)",
            _llms_bundle_section() + "\n",
            text,
            count=1,
            flags=re.DOTALL,
        )
        full_path.write_text(text, encoding="utf-8")
        print(f"Synced {full_path}")


def main() -> None:
    write_market_stats_ts()
    sync_readme()
    sync_pyproject()
    sync_server_json()
    sync_mcp_json()
    sync_og_svg()
    sync_og_preview_svg()
    sync_llms_txt()


if __name__ == "__main__":
    main()
