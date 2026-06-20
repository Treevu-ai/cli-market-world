#!/usr/bin/env python3
"""Add readme hero GIF/SVG to every Treevu-ai repo README."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEMO_GIF = ROOT / "landing" / "public" / "demo.gif"
# PyPI packages: relative assets/ paths 404 on pypi.org — use hosted demo GIF.
PYPI_HERO_URL = "https://cli-market.dev/demo.gif"
PYPI_PACKAGE_REPOS = frozenset({"cli-market-world", "cli-market-core", "procure-copilot"})
HERO_MARKERS = ("assets/readme-hero.", "assets/cli-market-demo.", "<!-- readme-hero -->", PYPI_HERO_URL)

REPO_CONFIG: dict[str, dict] = {
    "Treevu-ai": {
        "hero": "gif",
        "title": "RICARDO CUBA",
        "subtitle": "Founder @ CLI Market · Sinapsis Innovadora",
        "tagline": "Commerce infrastructure for AI agents · Perú",
    },
    "cli-market-world": {
        "hero": "gif",
        "title": "CLI MARKET",
        "subtitle": "Commerce infrastructure for AI agents",
        "tagline": "81 retailers · 41 verified · 8 countries · 22 MCP tools · 61k+ prices",
    },
    "cli-market-core": {
        "hero": "gif",
        "title": "CLI MARKET CORE",
        "subtitle": "Open SDK — search, compare, checkout & MCP",
        "tagline": "pip install cli-market-world · agentic commerce",
    },
    "cli-market-backend": {
        "hero": "svg",
        "title": "CLI MARKET BACKEND",
        "subtitle": "Collector · connectors · billing · dashboard",
        "tagline": "Private data moat · VTEX APIs · zero scraping",
    },
    "cli-market-index": {
        "hero": "svg",
        "title": "CLI MARKET INDEX",
        "subtitle": "Golden Records · entity resolution",
        "tagline": "Semantic moat · prod_* identity · 92% linkage",
    },
    "cli-market-content": {
        "hero": "svg",
        "title": "CLI MARKET CONTENT",
        "subtitle": "GTM · calendar · LinkedIn · 10 channels",
        "tagline": "Campaign ops · data-gates · price pulse",
    },
    "procure-copilot": {
        "hero": "gif",
        "title": "PROCURE COPILOT",
        "subtitle": "B2B procurement for LatAm enterprises",
        "tagline": "Powered by CLI Market API · 41 verified retailers · 8 countries",
    },
    "sinapsis-innovadora": {
        "hero": "svg",
        "title": "SINAPSIS INNOVADORA",
        "subtitle": "Agentic digital transformation studio",
        "tagline": "Design · strategy · innovation · Perú",
    },
    "treevu-ai-repo-landing": {
        "hero": "svg",
        "title": "TREEVU AI",
        "subtitle": "AI agent products & services",
        "tagline": "Official company landing",
    },
    "Agentic-Friendly": {
        "hero": "svg",
        "title": "AGENTIC FRIENDLY",
        "subtitle": "AI scoring & agentic lead qualification",
        "tagline": "Automate business processes with intelligent agents",
    },
    "invisible-hand": {
        "hero": "svg",
        "title": "INVISIBLE HAND",
        "subtitle": "Market automation engine",
        "tagline": "Connect · monitor · act on market signals",
    },
    "RWA_EUDR_PERU": {
        "hero": "svg",
        "title": "RWA EUDR PERU",
        "subtitle": "Real-world asset traceability",
        "tagline": "Agri-supply chains · EUDR compliance · Perú",
    },
    "factura-negociable-copilot": {
        "hero": "svg",
        "title": "FACTURA NEGOCIABLE",
        "subtitle": "Copiloto documental · Perú",
        "tagline": "Copilot Studio · Azure AI Search",
    },
    "mas-clientes": {
        "hero": "svg",
        "title": "MAS CLIENTES",
        "subtitle": "Compute platform for AI agents",
        "tagline": "Build and ship agents at scale",
    },
    "awesome-mcp-servers": {
        "hero": "svg",
        "title": "AWESOME MCP SERVERS",
        "subtitle": "Curated MCP server collection",
        "tagline": "Model Context Protocol ecosystem",
    },
    "diagnosticomype": {
        "hero": "svg",
        "title": "DIAGNOSTICO MYPE",
        "subtitle": "IA diagnostics for Peruvian SMBs",
        "tagline": "Landing · services · assessment",
    },
    "JARVIS": {
        "hero": "svg",
        "title": "JARVIS",
        "subtitle": "Connecting LLMs with the ML community",
        "tagline": "arxiv.org/pdf/2303.17580",
    },
    "open-design": {
        "hero": "svg",
        "title": "OPEN DESIGN",
        "subtitle": "Local-first design systems for agents",
        "tagline": "Prototypes · slides · export pipelines",
    },
    "agent-ready": {
        "hero": "svg",
        "title": "AGENT READY",
        "subtitle": "Agent-ready product patterns",
        "tagline": "Treevu-ai · agentic commerce",
    },
    "bnpl-caja-trujillo-prototipo": {
        "hero": "svg",
        "title": "BNPL CAJA TRUJILLO",
        "subtitle": "Buy now pay later prototype",
        "tagline": "Peru fintech · prototype",
    },
    "OpenMontage": {
        "hero": "svg",
        "title": "OPEN MONTAGE",
        "subtitle": "Video montage automation",
        "tagline": "Open tooling · media pipeline",
    },
    "ClawContentbot": {
        "hero": "svg",
        "title": "CLAW CONTENTBOT",
        "subtitle": "Content automation bot",
        "tagline": "Social · drafts · publishing",
    },
    "treevu-ai-repo": {
        "hero": "svg",
        "title": "TREEVU AI REPO",
        "subtitle": "Core company repository",
        "tagline": "Products · agents · experiments",
    },
    "agentic-business-os": {
        "hero": "svg",
        "title": "AGENTIC BUSINESS OS",
        "subtitle": "Operating system for agentic business",
        "tagline": "Workflows · automation · ops",
    },
    "carousel-generator": {
        "hero": "svg",
        "title": "CAROUSEL GENERATOR",
        "subtitle": "AI carousel maker for LinkedIn",
        "tagline": "Visual content · social · LATAM",
    },
    "microsoft-ml-repos": {
        "hero": "svg",
        "title": "MICROSOFT ML REPOS",
        "subtitle": "ML repository mirror & notes",
        "tagline": "Azure · research · reference",
    },
    "taller-mayo-2026": {
        "hero": "svg",
        "title": "TALLER MAYO 2026",
        "subtitle": "Workshop materials",
        "tagline": "Private · Treevu-ai",
    },
    "jarvis-cuba": {
        "hero": "svg",
        "title": "JARVIS CUBA",
        "subtitle": "JARVIS deployment · Cuba",
        "tagline": "Private deployment repository",
    },
    "codexskills": {
        "hero": "svg",
        "title": "CODEX SKILLS",
        "subtitle": "Private skills mirror sync",
        "tagline": "Agent tooling · internal",
    },
    "ari-bot-treevu": {
        "hero": "svg",
        "title": "ARI BOT",
        "subtitle": "Customer advisor bot",
        "tagline": "Treevu-ai · conversational AI",
    },
}


def _banner_svg(title: str, subtitle: str, tagline: str) -> str:
    t = title.replace("&", "&amp;").replace("<", "&lt;")
    s = subtitle.replace("&", "&amp;").replace("<", "&lt;")
    g = tagline.replace("&", "&amp;").replace("<", "&lt;")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 200" role="img" aria-label="{t}">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#080808"/>
      <stop offset="100%" stop-color="#0d1117"/>
    </linearGradient>
  </defs>
  <rect width="800" height="200" fill="url(#bg)"/>
  <rect x="1" y="1" width="798" height="198" fill="none" stroke="#1f2937" stroke-width="1"/>
  <text x="400" y="78" text-anchor="middle" font-family="ui-monospace,Consolas,monospace" font-size="28" font-weight="700" fill="#00d75f" letter-spacing="6">{t}</text>
  <text x="400" y="108" text-anchor="middle" font-family="ui-sans-serif,system-ui,sans-serif" font-size="14" fill="#9ca3af">{s}</text>
  <line x1="180" y1="128" x2="620" y2="128" stroke="#1f2937" stroke-width="1"/>
  <text x="400" y="152" text-anchor="middle" font-family="ui-monospace,Consolas,monospace" font-size="11" fill="#6b7280">{g}</text>
  <text x="400" y="178" text-anchor="middle" font-family="ui-monospace,Consolas,monospace" font-size="9" fill="#374151">Treevu-ai · github.com/Treevu-ai</text>
</svg>
"""


def _hero_block(ext: str, alt: str, *, repo_name: str | None = None) -> str:
    if repo_name in PYPI_PACKAGE_REPOS and ext == "gif":
        src = PYPI_HERO_URL
    else:
        src = f"assets/readme-hero.{ext}"
    return (
        "<!-- readme-hero -->\n"
        "<div align=\"center\">\n\n"
        f"<img src=\"{src}\" alt=\"{alt}\" width=\"100%\" />\n\n"
        "</div>\n\n"
    )


def _has_hero(text: str) -> bool:
    return any(m in text for m in HERO_MARKERS)


def _inject_hero(readme: str, block: str) -> str:
    if _has_hero(readme):
        return readme
    # Keep YAML frontmatter / mcp-name line at top
    lines = readme.splitlines(keepends=True)
    insert_at = 0
    if lines and lines[0].startswith("mcp-name:"):
        insert_at = 1
        if len(lines) > 1 and lines[1].strip() == "":
            insert_at = 2
    return "".join(lines[:insert_at]) + block + "".join(lines[insert_at:])


def _run(cmd: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, check=False)


def _list_repos() -> list[str]:
    cp = _run(["gh", "repo", "list", "Treevu-ai", "--limit", "100", "--json", "name", "-q", ".[].name"])
    if cp.returncode != 0:
        raise SystemExit(cp.stderr or cp.stdout)
    return [ln.strip() for ln in cp.stdout.splitlines() if ln.strip()]


def _default_config(name: str) -> dict:
    slug = name.replace("-", " ").upper()
    return {
        "hero": "svg",
        "title": slug[:40],
        "subtitle": name,
        "tagline": "Treevu-ai repository",
    }


def _apply_local(repo_path: Path, name: str, cfg: dict, *, dry_run: bool) -> str:
    readme = repo_path / "README.md"
    created = False
    if not readme.is_file():
        created = True
        if dry_run:
            return "would-create-readme"
        readme.write_text(f"# {name}\n\n", encoding="utf-8")

    assets = repo_path / "assets"
    ext = "gif" if cfg["hero"] == "gif" else "svg"
    alt = cfg["title"]

    if dry_run:
        if _has_hero(readme.read_text(encoding="utf-8")) if readme.is_file() else False:
            return "skip:has-hero"
        return f"would-update:{ext}" + ("+create" if created else "")

    assets.mkdir(exist_ok=True)
    if ext == "gif":
        if not DEMO_GIF.is_file():
            return "error:no-demo-gif"
        shutil.copy2(DEMO_GIF, assets / "readme-hero.gif")
    else:
        (assets / "readme-hero.svg").write_text(
            _banner_svg(cfg["title"], cfg["subtitle"], cfg["tagline"]),
            encoding="utf-8",
        )

    text = readme.read_text(encoding="utf-8")
    new_text = _inject_hero(text, _hero_block(ext, alt, repo_name=name))
    if new_text == text:
        return "skip:already-has-hero"
    readme.write_text(new_text, encoding="utf-8")
    suffix = "+created" if created else ""
    return f"updated:{ext}{suffix}"


def _clone_repo(name: str, dest: Path) -> bool:
    if (dest / ".git").is_dir():
        cp = _run(["git", "pull", "--ff-only"], cwd=dest)
        return cp.returncode == 0
    cp = _run(["gh", "repo", "clone", f"Treevu-ai/{name}", str(dest), "--", "--depth", "1"])
    return cp.returncode == 0


def _commit_push(repo_path: Path, name: str) -> str:
    _run(["git", "config", "user.email", "hello@cli-market.dev"], cwd=repo_path)
    _run(["git", "config", "user.name", "Ricardo Cuba"], cwd=repo_path)
    _run(["git", "add", "README.md", "assets"], cwd=repo_path)
    cp = _run(["git", "status", "--porcelain"], cwd=repo_path)
    if not cp.stdout.strip():
        return "skip:clean"
    _run(["git", "commit", "-m", "docs: add readme hero banner (GIF/SVG)"], cwd=repo_path)
    branch = _run(["git", "branch", "--show-current"], cwd=repo_path).stdout.strip() or "main"
    cp = _run(["git", "push", "origin", branch], cwd=repo_path)
    if cp.returncode != 0:
        return f"error:push:{cp.stderr.strip()[:120]}"
    return "pushed"


def main() -> int:
    dry_run = "--dry-run" in sys.argv
    push = "--push" in sys.argv
    only = [a for a in sys.argv[1:] if not a.startswith("--")]

    local_map = {
        "cli-market-world": ROOT,
        "cli-market-core": ROOT.parent / "cli-market-core",
        "cli-market-backend": ROOT.parent / "cli-market-backend",
        "cli-market-index": ROOT.parent / "cli-market-index",
        "cli-market-content": ROOT.parent / "cli-market-content",
        "Treevu-ai": ROOT.parent / "Treevu-ai",
    }

    repos = only or _list_repos()
    results: list[tuple[str, str]] = []

    with tempfile.TemporaryDirectory(prefix="readme-heroes-") as tmp:
        tmp_path = Path(tmp)
        for name in repos:
            cfg = REPO_CONFIG.get(name, _default_config(name))
            repo_path = local_map.get(name)
            cloned = False
            if repo_path is None or not repo_path.is_dir():
                repo_path = tmp_path / name
                if not _clone_repo(name, repo_path):
                    results.append((name, "error:clone"))
                    continue
                cloned = True
            elif not (repo_path / ".git").is_dir() and push:
                results.append((name, "error:no-git-local"))
                continue

            status = _apply_local(repo_path, name, cfg, dry_run=dry_run)
            if status.startswith("updated") and push and not dry_run:
                status = _commit_push(repo_path, name)
            results.append((name, status))
            if cloned and not dry_run and status == "skip:clean":
                pass

    width = max(len(n) for n, _ in results) if results else 10
    for name, status in sorted(results):
        print(f"{name:{width}}  {status}")
    updated = sum(1 for _, s in results if "updated" in s or "pushed" in s)
    print(f"\n{updated}/{len(results)} repos with hero assets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())