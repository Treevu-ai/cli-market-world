#!/usr/bin/env python3
"""CLI Market — Growth & Brand Multi-Agent Coordinator.

Connects the 6 design/marketing/sales personas from agency-agents (previously
defined in docs/agents/contexts/ but never wired to anything) to real CLI
Market signals: live site copy, public adoption metrics (PyPI, GitHub), and
live data-gate numbers — so none of them have to guess or invent claims.

Unlike price_pulse_agents.py (which slices one shared financial dashboard into
sections of a single report), each agent here produces its own standalone
deliverable, because the personas are heterogeneous (brand guidelines vs. UX
research vs. a sales demo brief aren't sections of the same document).

Usage:
  python3 ops/growth_pulse_agents.py --prepare   # Generate prompt files for 6 agents
  python3 ops/growth_pulse_agents.py --assemble  # Copy agent outputs to their docs/ destination
  python3 ops/growth_pulse_agents.py --run       # Prepare + (manual agent step) + assemble
  python3 ops/growth_pulse_agents.py --report    # Print which files need attention

Architecture:
  live signals (site HTML / PyPI / GitHub / health-stats) ──► per-agent data ──►
  prompt files ──► agent outputs (manual LLM step) ──► docs/<agent-output>.md
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

import httpx

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

AGENTS_DIR = PROJECT_ROOT / "docs" / "agents" / "contexts"
PROMPTS_OUT = Path(__file__).resolve().parent / "generated" / "prompts"
OUTPUTS_DIR = Path(__file__).resolve().parent / "generated" / "outputs"
DOCS_DIR = PROJECT_ROOT / "docs"

AGENCY_AGENTS_BASE = Path.home() / "Proyectos" / "agency-agents"
DESIGN_BASE = AGENCY_AGENTS_BASE / "design"
MARKETING_BASE = AGENCY_AGENTS_BASE / "marketing"
SALES_BASE = AGENCY_AGENTS_BASE / "sales"

LANDING_URL = "https://cli-market.dev/"
HEALTH_STATS_URL = "https://cli-market-api.fly.dev/health/stats"
GH_REPO = "Treevu-ai/cli-market-world"
PYPI_PACKAGE = "cli-market-world"

# Agent definitions — the 6 personas that existed only as unused context files.
AGENTS: list[dict[str, Any]] = [
    {
        "id": "brand-guardian",
        "role_file": str(DESIGN_BASE / "design-brand-guardian.md"),
        "context_file": str(AGENTS_DIR / "brand-guardian-context.md"),
        "data_source": "site_snapshot",
        "output_doc": str(DOCS_DIR / "brand-guidelines.md"),
        "instruction": "Producí/actualizá las brand guidelines de CLI Market (logo, color, tipografía, voz, uso correcto/incorrecto) y un touchpoint audit contra la copy real incluida abajo.",
    },
    {
        "id": "ui-designer",
        "role_file": str(DESIGN_BASE / "design-ui-designer.md"),
        "context_file": str(AGENTS_DIR / "ui-designer-context.md"),
        "data_source": "site_snapshot",
        "output_doc": str(DOCS_DIR / "ui-component-library.md"),
        "instruction": "Especificá la librería de componentes (estados, accesibilidad WCAG AA) para las superficies reales listadas en tu contexto, usando la copy/estructura actual del sitio incluida abajo como punto de partida.",
    },
    {
        "id": "ux-architect",
        "role_file": str(DESIGN_BASE / "design-ux-architect.md"),
        "context_file": str(AGENTS_DIR / "ux-architect-context.md"),
        "data_source": "site_snapshot",
        "output_doc": str(DOCS_DIR / "design-system.md"),
        "instruction": "Producí el design system document + component library spec + layout framework descritos en tu contexto, evaluando la estructura real del sitio incluida abajo.",
    },
    {
        "id": "ux-researcher",
        "role_file": str(DESIGN_BASE / "design-ux-researcher.md"),
        "context_file": str(AGENTS_DIR / "ux-researcher-context.md"),
        "data_source": "public_signals",
        "output_doc": str(DOCS_DIR / "ux-research.md"),
        "instruction": "Analizá el funnel (landing → pip install → market login → primera búsqueda → recurrente → Pro) usando las señales públicas reales de abajo (PyPI, GitHub) y evaluación heurística. Marcá toda suposición cualitativa como [HIPÓTESIS].",
    },
    {
        "id": "content-creator",
        "role_file": str(MARKETING_BASE / "marketing-content-creator.md"),
        "context_file": str(AGENTS_DIR / "content-creator-context.md"),
        "data_source": "live_claims",
        "output_doc": str(OUTPUTS_DIR / "content-ideas.md"),
        "instruction": "Generá 5 ideas de contenido (LinkedIn/DEV.to/Twitter) citando SOLO las cifras reales de abajo. Si falta un dato, marcalo [ACTUALIZAR] — no inventes números.",
    },
    {
        "id": "sales-engineer",
        "role_file": str(SALES_BASE / "sales-engineer.md"),
        "context_file": str(AGENTS_DIR / "sales-engineer-context.md"),
        "data_source": "live_claims",
        "output_doc": str(DOCS_DIR / "sales-demo-brief.md"),
        "instruction": "Preparate un brief pre-demo: confirmá si el moat está sano (ver datos abajo) y por lo tanto si podés demostrar el flujo de compra, o si tenés que mostrar el data-gate como diferenciador y reprogramar.",
    },
]

# Data-gate freshness threshold — mirrors the "coverage >= 80%" gate used
# elsewhere (content-creator's `make gate`, sales-engineer's `make gate-remote`).
MOAT_STALE_COVERAGE_PCT = 80.0
MOAT_STALE_AGE_HOURS = 6.0


def _strip_html(html: str, max_chars: int = 4000) -> str:
    """Crude HTML→text: drop script/style, strip tags, collapse whitespace."""
    html = re.sub(r"<(script|style)[^>]*>.*?</\1>", "", html, flags=re.S | re.I)
    text = re.sub(r"<[^>]+>", " ", html)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]


def fetch_site_snapshot() -> dict:
    r = httpx.get(LANDING_URL, timeout=20, follow_redirects=True)
    r.raise_for_status()
    return {
        "url": LANDING_URL,
        "status_code": r.status_code,
        "visible_text": _strip_html(r.text),
    }


def fetch_public_signals() -> dict:
    signals: dict[str, Any] = {}
    try:
        r = httpx.get(f"https://pypistats.org/api/packages/{PYPI_PACKAGE}/recent", timeout=15)
        r.raise_for_status()
        signals["pypi_downloads"] = r.json().get("data", {})
    except Exception as e:
        signals["pypi_downloads"] = {"error": str(e)}

    try:
        out = subprocess.run(
            ["gh", "api", f"repos/{GH_REPO}",
             "--jq", "{stars: .stargazers_count, watchers: .subscribers_count, open_issues: .open_issues_count}"],
            capture_output=True, text=True, timeout=20, check=True,
        )
        signals["github"] = json.loads(out.stdout)
    except Exception as e:
        signals["github"] = {"error": str(e)}

    return signals


def fetch_live_claims() -> dict:
    r = httpx.get(HEALTH_STATS_URL, timeout=15)
    r.raise_for_status()
    stats = r.json()
    coverage = stats.get("coverage_7d_pct", 0)
    moat_age = stats.get("moat_age_hours", 999)
    stats["moat_stale"] = coverage < MOAT_STALE_COVERAGE_PCT or moat_age > MOAT_STALE_AGE_HOURS
    return stats


DATA_FETCHERS = {
    "site_snapshot": fetch_site_snapshot,
    "public_signals": fetch_public_signals,
    "live_claims": fetch_live_claims,
}

_data_cache: dict[str, dict] = {}


def fetch_for(agent: dict) -> dict:
    source = agent["data_source"]
    if source not in _data_cache:
        print(f"  🌐 fetching {source}...")
        _data_cache[source] = DATA_FETCHERS[source]()
    return _data_cache[source]


def build_prompt(agent: dict, data: dict) -> str:
    parts: list[str] = []

    role_path = agent["role_file"]
    if os.path.exists(role_path):
        parts.append(open(role_path, encoding="utf-8").read())
    else:
        parts.append(
            f"# {agent['id'].replace('-', ' ').title()}\n\n"
            f"(Role file not found: {role_path} — ¿está clonado ~/Proyectos/agency-agents?)"
        )

    ctx_path = agent["context_file"]
    if os.path.exists(ctx_path):
        parts.append("\n---\n")
        parts.append(open(ctx_path, encoding="utf-8").read())
    else:
        parts.append(f"\n(Context file not found: {ctx_path})")

    parts.append("\n---\n")
    parts.append(f"## 📊 Datos reales ({agent['data_source']})\n")
    parts.append("```json")
    parts.append(json.dumps(data, indent=2, ensure_ascii=False))
    parts.append("```")

    parts.append("\n---\n")
    parts.append("## ✏️ Instrucción\n")
    parts.append(agent["instruction"])
    parts.append("Formato: markdown. No inventes cifras — todo claim debe salir de los datos de arriba.")

    return "\n".join(parts)


def prepare_prompts() -> None:
    PROMPTS_OUT.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    for agent in AGENTS:
        data = fetch_for(agent)
        prompt = build_prompt(agent, data)
        out_path = PROMPTS_OUT / f"prompt-{agent['id']}.md"
        out_path.write_text(prompt, encoding="utf-8")
        print(f"  📝 {agent['id']}: {out_path} ({len(prompt)} chars)")


def assemble_outputs() -> None:
    """Copy each agent's saved output to its real docs/ destination."""
    for agent in AGENTS:
        out_path = OUTPUTS_DIR / f"output-{agent['id']}.md"
        dest = Path(agent["output_doc"])
        if not out_path.exists():
            print(f"  ⏳ {agent['id']}: sin output todavía ({out_path})")
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(out_path.read_text(encoding="utf-8"), encoding="utf-8")
        print(f"  ✅ {agent['id']}: → {dest}")


def report_status() -> None:
    print("Growth Pulse Agent Status:\n")
    for agent in AGENTS:
        prompt = PROMPTS_OUT / f"prompt-{agent['id']}.md"
        output = OUTPUTS_DIR / f"output-{agent['id']}.md"
        dest = Path(agent["output_doc"])
        p_ok = "✅" if prompt.exists() else "❌"
        o_ok = "✅" if output.exists() else "❌"
        d_ok = "✅" if dest.exists() else "❌"
        print(f"  {agent['id']}: prompt {p_ok}  output {o_ok}  destino {d_ok}  ({dest})")
    print(f"\nPrompts dir:  {PROMPTS_OUT}")
    print(f"Outputs dir:  {OUTPUTS_DIR}")
    print("\nWorkflow:  1) --prepare  2) run agents manually, save a output-<id>.md  3) --assemble")


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Growth & Brand Multi-Agent Coordinator")
    parser.add_argument("--prepare", action="store_true", help="Generate prompt files")
    parser.add_argument("--assemble", action="store_true", help="Copy outputs to their docs/ destination")
    parser.add_argument("--run", action="store_true", help="Prepare + assemble")
    parser.add_argument("--report", action="store_true", help="Show file status")
    args = parser.parse_args()

    if args.report:
        report_status()
        return

    if not any([args.prepare, args.assemble, args.run]):
        parser.print_help()
        return

    if args.prepare or args.run:
        print("Generating prompts (fetching live signals)...")
        prepare_prompts()
        print(f"\n✅ Prompts ready in {PROMPTS_OUT}")
        print("Next: open each prompt file in your LLM tool and save the output.")
        print(f"      Output files go in {OUTPUTS_DIR}/output-<agent>.md")

    if args.assemble or args.run:
        print("\nAssembling outputs...")
        assemble_outputs()


if __name__ == "__main__":
    main()
