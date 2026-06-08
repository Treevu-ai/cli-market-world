#!/usr/bin/env python3
"""Emit landing/lib/marketStats.ts and sync README, PyPI, server.json from market_stats.py."""

import json
import re
import shutil
import subprocess
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


def _pypi_description() -> str:
    counts = _mcp_counts()
    return (
        "mcp-name: io.github.Treevu-ai/cli-market-world - "
        "CLI Market: commerce API for AI agents. "
        f"{counts['default']} curated MCP tools ({counts['legacy']} legacy), "
        f"{s.INDICATORS_COUNT} indicators, "
        f"{s.RETAILERS_VERIFIED} verified retailers in {s.COUNTRIES} countries. MIT."
    )


def _server_description() -> str:
    counts = _mcp_counts()
    return _replace_mcp_count(s.server_json_description(), s.MCP_TOOLS, counts["default"])


def _readme_tagline_html() -> str:
    counts = _mcp_counts()
    return (
        f"<b>Commerce infrastructure for AI agents.</b><br>"
        f"{s.RETAILERS_DEFINED} retailers ({s.RETAILERS_VERIFIED} verified). "
        f"{s.COUNTRIES} countries. {s.PLATFORMS} platforms. "
        f"{counts['default']} curated MCP tools ({counts['legacy']} legacy). "
        f"{s.PAYMENTS_LABEL}.<br>"
        f"{s.PRICES_VERIFIED_LABEL} verified shelf prices, normalized per kg/L, "
        f"refreshed every {s.PRICES_REFRESH_HOURS} hours.<br>"
        f"One <code>pip install</code>. One API. Zero scraping."
    )


def _readme_mcp_section() -> str:
    mcp_default = public_tool_count("default")
    tools = [t["name"] for t in list_tools("default")]
    tools_line = " ".join(f"`{name}`" for name in tools)
    return (
        f"## 🔧 {mcp_default} MCP tools (default profile) · {s.INDICATORS_COUNT} indicators\n\n"
        f"{tools_line}\n"
    )


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
  ogImageUrl: "/og.png",
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
        f'<p align="center">{_readme_tagline_html()}</p>',
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"🌍 \*\*\d+ retailers \(\d+ verificados activos\) · \d+ países · \d+ plataformas · \d+ herramientas MCP · \d+ indicadores\*\*",
        (
            f"🌍 **{s.RETAILERS_DEFINED} retailers ({s.RETAILERS_VERIFIED} verificados activos) · "
            f"{s.COUNTRIES} países · {s.PLATFORMS} plataformas · "
            f"{mcp_default} herramientas MCP ({mcp_legacy} legacy) · {s.INDICATORS_COUNT} indicadores**"
        ),
        text,
        count=1,
    )
    text = re.sub(
        r"🌍 \*\*\d+ retailers \(\d+ verified active\) · \d+ countries · \d+ platforms · \d+ MCP tools · \d+ indicators\*\*",
        (
            f"🌍 **{s.RETAILERS_DEFINED} retailers ({s.RETAILERS_VERIFIED} verified active) · "
            f"{s.COUNTRIES} countries · {s.PLATFORMS} platforms · "
            f"{mcp_default} curated MCP tools ({mcp_legacy} legacy) · {s.INDICATORS_COUNT} indicators**"
        ),
        text,
        count=1,
    )
    text = re.sub(
        r"cli-market-backend   Data ingestion — VTEX scrapers, FastAPI server, \d+ retailers, \d+k prices",
        f"cli-market-backend   Data ingestion — VTEX scrapers, FastAPI server, {s.RETAILERS_DEFINED} retailers, 45k prices",
        text,
        count=1,
    )
    text = re.sub(
        r"cli-market-core      Intelligence — indicators, stats, billing, connectors, \d+ MCP tools(?: \(default\))*",
        f"cli-market-core      Intelligence — indicators, stats, billing, connectors, {mcp_default} MCP tools (default)",
        text,
        count=1,
    )
    text = re.sub(
        r"## 🔧 \d+ MCP tools[^\n]*\n\n(?:`[^`]+` ?)+\n*",
        _readme_mcp_section() + "\n",
        text,
        count=1,
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
        r"\d+ retailers \(\d+ verified active\)",
        f"{s.RETAILERS_DEFINED} retailers ({s.RETAILERS_VERIFIED} verified active)",
        text,
    )
    text = re.sub(
        r"\d+ retailers \(\d+ verificados activos\)",
        f"{s.RETAILERS_DEFINED} retailers ({s.RETAILERS_VERIFIED} verificados activos)",
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
    desc = _pypi_description().replace('"', '\\"')
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
    desc = _server_description()
    for rel in ("server.json", "landing/public/server.json"):
        path = ROOT / rel
        data = json.loads(path.read_text(encoding="utf-8"))
        data["description"] = desc
        data["version"] = s.PACKAGE_VERSION
        if data.get("packages"):
            pkg = data["packages"][0]
            pkg["version"] = s.PACKAGE_VERSION
            env_vars = list(pkg.get("environmentVariables") or [])
            by_name = {e["name"]: e for e in env_vars}
            by_name["MCP_TOOL_PROFILE"] = {
                "name": "MCP_TOOL_PROFILE",
                "description": "MCP tool profile: default (curated) or legacy (all tools)",
                "default": "default",
            }
            pkg["environmentVariables"] = list(by_name.values())
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
    data["env"] = {
        "MARKET_API_URL": "https://cli-market-production.up.railway.app",
        "MCP_TOOL_PROFILE": "default",
    }
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Synced {path}")
    root = ROOT / "mcp.json"
    root.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Synced {root}")


def _og_price_compact() -> str:
    m = re.match(r"([\d,]+)", s.PRICES_VERIFIED_LABEL)
    if m:
        n = int(m.group(1).replace(",", ""))
        if n >= 1000:
            return f"{n // 1000}K+"
    return s.PRICES_VERIFIED_LABEL.replace(",", "")


def _og_stats_line_es() -> str:
    mcp = public_tool_count("default")
    return (
        f"{s.RETAILERS_DEFINED} retailers · {_og_price_compact()} precios · "
        f"{mcp} MCP · {s.COUNTRIES} países LatAm"
    )


def _og_stats_line_en() -> str:
    mcp = public_tool_count("default")
    return (
        f"{s.RETAILERS_DEFINED} retailers · {_og_price_compact()} prices · "
        f"{mcp} MCP · {s.COUNTRIES} countries"
    )


def _og_svg_content() -> str:
    stats = _og_stats_line_es()
    pip = s.PIP_INSTALL_CMD
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a0a0b"/>
      <stop offset="100%" stop-color="#131314"/>
    </linearGradient>
    <radialGradient id="glow" cx="50%" cy="40%" r="45%">
      <stop offset="0%" stop-color="#3afecf" stop-opacity="0.12"/>
      <stop offset="100%" stop-color="#3afecf" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="border" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#3afecf" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#ffffff" stop-opacity="0.08"/>
    </linearGradient>
  </defs>
  <rect width="1200" height="630" fill="url(#bg)"/>
  <rect width="1200" height="630" fill="url(#glow)"/>
  <rect x="40" y="40" width="1120" height="550" rx="8" fill="none" stroke="url(#border)" stroke-width="1.5"/>
  <rect x="40" y="40" width="1120" height="4" rx="2" fill="#47475d"/>
  <circle cx="68" cy="62" r="5" fill="#ffffff" fill-opacity="0.15"/>
  <circle cx="88" cy="62" r="5" fill="#ffffff" fill-opacity="0.15"/>
  <circle cx="108" cy="62" r="5" fill="#ffffff" fill-opacity="0.15"/>
  <text x="600" y="72" text-anchor="middle" font-family="ui-monospace, monospace" font-size="11" fill="#b9cac2" fill-opacity="0.5">market_agent_sh // og_preview</text>
  <text x="600" y="268" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="64" font-weight="700" fill="#ffffff" letter-spacing="-2">CLI Market</text>
  <text x="600" y="318" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="26" fill="#3afecf" font-style="italic">La capa programable del retail físico</text>
  <text x="600" y="368" text-anchor="middle" font-family="ui-monospace, monospace" font-size="22" fill="#b9cac2">{stats}</text>
  <rect x="320" y="400" width="560" height="56" rx="4" fill="#3afecf" fill-opacity="0.12" stroke="#3afecf" stroke-opacity="0.35"/>
  <text x="600" y="436" text-anchor="middle" font-family="ui-monospace, monospace" font-size="18" font-weight="700" fill="#3afecf" letter-spacing="2">{pip}</text>
  <text x="600" y="510" text-anchor="middle" font-family="ui-monospace, monospace" font-size="16" fill="#84948d">cli-market.dev · MIT · Network Engine Active</text>
  <circle cx="440" cy="508" r="4" fill="#3afecf"/>
</svg>
"""


def _og_preview_svg_content() -> str:
    stats = _og_stats_line_en()
    pip = s.PIP_INSTALL_CMD
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 200">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0a0a0b"/>
      <stop offset="100%" stop-color="#131314"/>
    </linearGradient>
  </defs>
  <rect width="800" height="200" fill="url(#bg)"/>
  <rect x="1" y="1" width="798" height="198" fill="none" stroke="#3afecf" stroke-opacity="0.2"/>
  <rect x="0" y="0" width="800" height="3" fill="#47475d"/>
  <text x="400" y="68" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="34" font-weight="700" fill="#ffffff" letter-spacing="-1">CLI Market</text>
  <text x="400" y="96" text-anchor="middle" font-family="ui-sans-serif, system-ui, sans-serif" font-size="13" fill="#3afecf">commerce infrastructure for AI agents</text>
  <text x="400" y="126" text-anchor="middle" font-family="ui-monospace, monospace" font-size="11" fill="#b9cac2">{stats}</text>
  <text x="400" y="154" text-anchor="middle" font-family="ui-monospace, monospace" font-size="10" fill="#84948d">{pip} · cli-market.dev · MIT</text>
  <line x1="180" y1="168" x2="620" y2="168" stroke="#3b4a44" stroke-width="0.5"/>
  <text x="400" y="186" text-anchor="middle" font-family="ui-monospace, monospace" font-size="8" fill="#84948d" letter-spacing="1">MIT · MCP NATIVE · LATAM RETAIL · VERIFIED PRICES</text>
</svg>
"""


def sync_og_svg() -> None:
    path = ROOT / "landing" / "public" / "og.svg"
    path.write_text(_og_svg_content(), encoding="utf-8")
    print(f"Synced {path}")


def sync_og_preview_svg() -> None:
    path = ROOT / "landing" / "public" / "og-preview.svg"
    path.write_text(_og_preview_svg_content(), encoding="utf-8")
    print(f"Synced {path}")


def sync_og_png() -> None:
    """Rasterize OG SVGs to PNG — social crawlers (LinkedIn, Slack) do not use SVG."""
    node = shutil.which("node") or shutil.which("node.exe")
    if not node:
        print("WARN: node not found — og.png not regenerated", file=sys.stderr)
        return
    landing = ROOT / "landing"
    rasterizer = landing / "scripts" / "rasterize_og.mjs"
    pairs = [
        (landing / "public" / "og.svg", landing / "public" / "og.png"),
        (landing / "public" / "og-preview.svg", landing / "public" / "og-preview.png"),
    ]
    for svg_path, png_path in pairs:
        result = subprocess.run(
            [node, str(rasterizer), str(svg_path.relative_to(landing)), str(png_path.relative_to(landing))],
            cwd=landing,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"WARN: could not rasterize {svg_path.name}: {result.stderr.strip()}", file=sys.stderr)
            continue
        print(f"Synced {png_path}")


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


def sync_glama_json() -> None:
    counts = _mcp_counts()
    path = ROOT / "glama.json"
    tools = [t["name"] for t in list_tools("default")]
    data = {
        "license": s.LICENSE,
        "description": (
            f"Commerce infrastructure for AI agents — {counts['default']} curated MCP tools "
            f"({counts['legacy']} legacy) to search, compare, and purchase across "
            f"{s.RETAILERS_VERIFIED} verified retailers in {s.COUNTRIES} countries. "
            f"{s.PRICES_VERIFIED_LABEL} real shelf prices refreshed every {s.PRICES_REFRESH_HOURS} hours. "
            "Free tier available."
        ),
        "categories": ["ecommerce", "retail", "commerce", "data", "prices"],
        "tools": tools,
    }
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Synced {path}")


def main() -> None:
    write_market_stats_ts()
    sync_readme()
    sync_pyproject()
    sync_server_json()
    sync_mcp_json()
    sync_glama_json()
    sync_og_svg()
    sync_og_preview_svg()
    sync_og_png()
    sync_llms_txt()


if __name__ == "__main__":
    main()
