#!/usr/bin/env python3
"""CLI Market — Price Pulse Multi-Agent Coordinator.

Prepares agent prompts from dashboard data, and assembles the final report.

Usage:
  python3 ops/price_pulse_agents.py --prepare   # Generate prompt files for 5 agents
  python3 ops/price_pulse_agents.py --assemble   # Assemble outputs into final report
  python3 ops/price_pulse_agents.py --run        # Prepare + (manual agent step) + assemble
  python3 ops/price_pulse_agents.py --report     # Print which files need attention

Architecture:
  /dashboard/data ──► slice per agent ──► prompt files ──► agent outputs ──► assembled PDF
"""

from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

# Paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

AGENTS_DIR = Path(__file__).resolve().parent.parent / "docs" / "agents" / "contexts"
PROMPTS_OUT = Path(__file__).resolve().parent / "generated" / "prompts"
OUTPUTS_DIR = Path(__file__).resolve().parent / "generated" / "outputs"
REPORTS_DIR = Path(__file__).resolve().parent / "generated" / "reports"

DASHBOARD_URL_PRODUCTION = "https://cli-market-production.up.railway.app/dashboard/data"
DASHBOARD_URL_LOCAL = "http://127.0.0.1:8765/dashboard/data"

# Agent definitions (from agency-agents repo)
AGENCY_AGENTS_BASE = Path.home() / "Proyectos" / "agency-agents" / "finance"

AGENTS: list[dict[str, Any]] = [
    {
        "id": "bookkeeper",
        "role_file": str(AGENCY_AGENTS_BASE / "finance-bookkeeper-controller.md"),
        "context_file": str(AGENTS_DIR / "bookkeeper-context.md"),
        "data_keys": ["kpis", "quality_funnel", "moat_summary", "collector", "store_health"],
        "section": "§5 Calidad del Dato + §6 Metodología y Audit Trail",
    },
    {
        "id": "financial-analyst",
        "role_file": str(AGENCY_AGENTS_BASE / "finance-financial-analyst.md"),
        "context_file": str(AGENTS_DIR / "financial-analyst-context.md"),
        "data_keys": ["inflation", "canasta_basica", "by_line_currency", "canasta_spreads", "top_risers", "top_fallers"],
        "section": "§1 Resumen Ejecutivo + §2 RPV + §3 Canasta Básica",
    },
    {
        "id": "fpa-analyst",
        "role_file": str(AGENCY_AGENTS_BASE / "finance-fpa-analyst.md"),
        "context_file": str(AGENTS_DIR / "fpa-analyst-context.md"),
        "data_keys": ["inflation", "canasta_basica", "inventory_daily", "moat_start", "by_country"],
        "section": "§7 Proyección 30/60/90d",
    },
    {
        "id": "investment-researcher",
        "role_file": str(AGENCY_AGENTS_BASE / "finance-investment-researcher.md"),
        "context_file": str(AGENTS_DIR / "investment-researcher-context.md"),
        "data_keys": ["by_country", "line_country_matrix", "marketing_spreads", "moat_summary", "by_line"],
        "section": "§4 Dispersión (contexto) + §8 Contexto Macro + Competitive Landscape",
    },
    {
        "id": "tax-strategist",
        "role_file": str(AGENCY_AGENTS_BASE / "finance-tax-strategist.md"),
        "context_file": str(AGENTS_DIR / "tax-strategist-context.md"),
        "data_keys": ["marketing_spreads", "by_country", "by_line_currency", "moat_summary"],
        "section": "§9 Transfer Pricing Brief",
    },
]

# IPC taxonomy (hardcoded fallback if import fails)
CANASTA_IPC_TABLE = """| Ítem canasta | División IPC | Subclase IPC | Ponderación INEI |
|-------------|-------------|-------------|------------------|
| leche | Alimentos y Bebidas No Alcohólicas | Leche, queso y huevos | 5.03% |
| arroz | Alimentos y Bebidas No Alcohólicas | Pan y cereales | 4.82% |
| aceite | Alimentos y Bebidas No Alcohólicas | Aceites y grasas | 3.41% |
| azucar | Alimentos y Bebidas No Alcohólicas | Azúcar, mermelada, chocolate | 2.78% |
| huevos | Alimentos y Bebidas No Alcohólicas | Leche, queso y huevos | 0.91% |
| pan | Alimentos y Bebidas No Alcohólicas | Pan y cereales | 3.52% |
| cafe | Alimentos y Bebidas No Alcohólicas | Café, té y cacao | 0.88% |
| pollo | Alimentos y Bebidas No Alcohólicas | Carne | 7.12% |
| queso | Alimentos y Bebidas No Alcohólicas | Leche, queso y huevos | 1.45% |
| jabon | Bienes y Servicios Diversos | Cuidado personal | 2.91% |"""


def fetch_data(local: bool = False) -> dict:
    errors: list[str] = []
    urls: list[tuple[str, str]] = []
    custom = os.getenv("DASHBOARD_DATA_URL", "")
    if custom:
        urls.append(("custom", custom))
    elif local:
        urls.append(("local", DASHBOARD_URL_LOCAL))
    else:
        urls.append(("production", DASHBOARD_URL_PRODUCTION))
        urls.append(("local", DASHBOARD_URL_LOCAL))
    for label, url in urls:
        try:
            r = httpx.get(url, timeout=30)
            if r.status_code == 200:
                if errors:
                    print(f"  ⚠️  {'; '.join(errors)} — using {label}")
                else:
                    print(f"  ✅ {label}")
                return r.json()
            errors.append(f"{label} returned {r.status_code}")
        except Exception as e:
            errors.append(f"{label} error: {e}")
    raise RuntimeError(f"Cannot fetch dashboard data. Errors: {'; '.join(errors)}")


def slice_data(data: dict, keys: list[str]) -> dict:
    """Extract only the fields an agent needs."""
    sliced: dict[str, Any] = {"generated_at": data.get("generated_at", "")}
    for k in keys:
        if k in data:
            sliced[k] = data[k]
    return sliced


def build_prompt(agent: dict, data_slice: dict, last_section: str = "") -> str:
    """Build a complete agent prompt: role + context + data + instruction."""
    parts: list[str] = []

    # 1. Role definition
    role_path = agent["role_file"]
    if os.path.exists(role_path):
        parts.append(open(role_path).read())
    else:
        parts.append(f"# {agent['id'].replace('-', ' ').title()}\n\n(Role file not found: {role_path})")

    # 2. CLI Market context
    ctx_path = agent["context_file"]
    if os.path.exists(ctx_path):
        parts.append("\n---\n")
        parts.append(open(ctx_path).read())
    else:
        parts.append(f"\n(Context file not found: {ctx_path})")

    # 3. Data slice
    parts.append("\n---\n")
    parts.append("## 📊 Datos del dashboard\n")
    parts.append("```json")
    parts.append(json.dumps(data_slice, indent=2, ensure_ascii=False))
    parts.append("```")

    # 4. Instruction
    parts.append("\n---\n")
    parts.append("## ✏️ Instrucción\n")
    parts.append(f"Producí tu sección del reporte Price Pulse CLI Market ({agent['section']}).")
    parts.append("Formato: markdown. Solo tu sección, no el reporte completo.")
    parts.append("Incluí tus conclusiones en el formato especificado en tu contexto.")

    if last_section:
        parts.append(f"\nLa sección anterior del reporte (Financial Analyst) ya produjo:\n{last_section[:500]}")

    return "\n".join(parts)


def prepare_prompts(data: dict) -> dict[str, str]:
    """Generate prompt files for all 5 agents. Returns path → agent_id map."""
    PROMPTS_OUT.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # Run bookkeeper and financial-analyst first (Fase 1)
    # For now, prepare all independently
    generated: dict[str, str] = {}
    for agent in AGENTS:
        sliced = slice_data(data, agent["data_keys"])
        prompt = build_prompt(agent, sliced)
        out_path = PROMPTS_OUT / f"prompt-{agent['id']}.md"
        out_path.write_text(prompt, encoding="utf-8")
        generated[str(out_path)] = agent["id"]
        print(f"  📝 {agent['id']}: {out_path} ({len(prompt)} chars)")

    # Also save the full data with hash for audit trail
    raw = json.dumps(data, indent=2, ensure_ascii=False)
    hash_path = PROMPTS_OUT / "dashboard-data.json"
    hash_path.write_text(raw, encoding="utf-8")
    sha = hashlib.sha256(raw.encode()).hexdigest()[:16]
    print(f"  🔐 Full dashboard saved: {hash_path} (SHA256: {sha})")

    return generated


def assemble_report(data: dict) -> str:
    """Assemble agent outputs into final report."""
    now = datetime.now(timezone.utc)
    ds = now.strftime("%Y-%m-%d")
    week = f"{now.isocalendar().year}-W{now.isocalendar().week:02d}"

    k = data.get("kpis", {})
    moat = data.get("moat_summary", {})
    coll = data.get("collector", {})
    total = k.get("total_indexed", 0)
    snapshots = k.get("snapshots_24h", 0)
    coverage = k.get("coverage_7d_pct", 0)
    fresh_pct = k.get("fresh_24h_pct", 0)

    # Read agent outputs
    outputs: dict[str, str] = {}
    for agent in AGENTS:
        out_path = OUTPUTS_DIR / f"output-{agent['id']}.md"
        if out_path.exists():
            outputs[agent["id"]] = out_path.read_text(encoding="utf-8")
        else:
            outputs[agent["id"]] = f"*[{agent['id']}: output pendiente. Guardá la respuesta del agente en {out_path}]*"

    lines: list[str] = [
        "# CLI Market Price Pulse — Reporte Multi-Agente",
        f"**Semana {week} · {ds}**",
        "",
        "*Reporte generado con 5 agentes financieros especializados.*",
        "*CLI Market Intelligence — Piloto comercial · Confidencial*",
        "",
        "---",
        "",
        "## 1. Resumen Ejecutivo",
        f"- **{total:,}** precios indexados · **{snapshots:,}** refresh 24h",
        f"- **{coverage:.1f}%** cobertura 7d · **{fresh_pct:.1f}%** frescura",
        f"- Collector: **{coll.get('status', 'unknown')}** · Último snapshot: {moat.get('moat_age_hours', '—')}h",
        "",
        "---",
        "",
    ]

    # Fase 1: Financial Analyst output (§1-3)
    lines.append("## 📊 Análisis Financiero")
    lines.append("")
    if "financial-analyst" in outputs:
        lines.append(outputs["financial-analyst"])
    else:
        lines.append("*Pendiente — ejecutar Financial Analyst*")
    lines += ["", "---", ""]

    # Fase 1: Bookkeeper output (§5-6)
    lines.append("## 📒 Calidad del Dato y Metodología")
    lines.append("")
    if "bookkeeper" in outputs:
        lines.append(outputs["bookkeeper"])
    else:
        lines.append("*Pendiente — ejecutar Bookkeeper*")
    lines += ["", "---", ""]

    # Investment Researcher (§4, §8)
    lines.append("## 🔬 Contexto de Mercado")
    lines.append("")
    if "investment-researcher" in outputs:
        lines.append(outputs["investment-researcher"])
    else:
        lines.append("*Pendiente — ejecutar Investment Researcher*")
    lines += ["", "---", ""]

    # FP&A Analyst (§7)
    lines.append("## 📈 Proyecciones")
    lines.append("")
    if "fpa-analyst" in outputs:
        lines.append(outputs["fpa-analyst"])
    else:
        lines.append("*Pendiente — ejecutar FP&A Analyst*")
    lines += ["", "---", ""]

    # Tax Strategist (§9)
    lines.append("## 🏛️ Transfer Pricing Brief")
    lines.append("")
    if "tax-strategist" in outputs:
        lines.append(outputs["tax-strategist"])
    else:
        lines.append("*Pendiente — ejecutar Tax Strategist*")
    lines += ["", "---", ""]

    # IPC taxonomy appendix
    lines += [
        "## 📎 Apéndice: Trazabilidad IPC (INEI, base 2021=100)",
        "",
        CANASTA_IPC_TABLE,
        "",
        "*Ponderaciones referenciales. La canasta CLI Market cubre productos de consumo diario en retail formal urbano.*",
        "",
        "---",
        "",
        f"*Generado el {ds} · CLI Market Intelligence · hello@cli-market.dev*",
    ]

    return "\n".join(lines)


def report_status() -> None:
    """Print which prompt/output files exist and which are missing."""
    print("Price Pulse Agent Status:\n")
    for agent in AGENTS:
        prompt = PROMPTS_OUT / f"prompt-{agent['id']}.md"
        output = OUTPUTS_DIR / f"output-{agent['id']}.md"
        p_ok = "✅" if prompt.exists() else "❌"
        o_ok = "✅" if output.exists() else "❌"
        print(f"  {agent['id']}: prompt {p_ok}  output {o_ok}")
    print(f"\nPrompts dir:  {PROMPTS_OUT}")
    print(f"Outputs dir:  {OUTPUTS_DIR}")
    print("\nWorkflow:  1) --prepare  2) run agents manually  3) --assemble")


def submit_job(*, country: str = "PE", callback_url: str = "", local: bool = False) -> dict:
    """Enqueue Price Pulse via POST /v1/intel/price-pulse (Pro tier)."""
    base = os.getenv("MARKET_API_URL", "").rstrip("/") or (
        "http://127.0.0.1:8765" if local else "https://cli-market-production.up.railway.app"
    )
    token = os.getenv("MARKET_API_TOKEN") or os.getenv("CLI_MARKET_TOKEN", "")
    if not token:
        raise RuntimeError("Set MARKET_API_TOKEN or CLI_MARKET_TOKEN for --submit")
    url = f"{base}/v1/intel/price-pulse"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    body = {"country": country.upper()[:2], "callback_url": callback_url}
    r = httpx.post(url, json=body, headers=headers, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"submit failed {r.status_code}: {r.text[:300]}")
    return r.json()


def main() -> None:
    import argparse
    parser = argparse.ArgumentParser(description="Price Pulse Multi-Agent Coordinator")
    parser.add_argument("--prepare", action="store_true", help="Generate prompt files")
    parser.add_argument("--assemble", action="store_true", help="Assemble outputs into final report")
    parser.add_argument("--run", action="store_true", help="Prepare + assemble")
    parser.add_argument("--report", action="store_true", help="Show file status")
    parser.add_argument("--submit", action="store_true", help="Enqueue async job via API")
    parser.add_argument("--country", default="PE", help="Country for --submit (ISO 2-letter)")
    parser.add_argument("--callback-url", default="", help="Webhook URL when job completes")
    parser.add_argument("--local", action="store_true", help="Use localhost")
    args = parser.parse_args()

    if args.report:
        report_status()
        return

    if args.submit:
        try:
            result = submit_job(
                country=args.country,
                callback_url=args.callback_url,
                local=args.local,
            )
        except RuntimeError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        print(f"✅ Job queued: {result.get('job_id')} status={result.get('status')}")
        print(f"   Poll: GET /v1/intel/price-pulse/{result.get('job_id')}")
        return

    if not any([args.prepare, args.assemble, args.run]):
        parser.print_help()
        return

    print("Fetching dashboard data...")
    try:
        data = fetch_data(local=args.local)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    if args.prepare or args.run:
        print("\nGenerating prompts...")
        prepare_prompts(data)
        print(f"\n✅ Prompts ready in {PROMPTS_OUT}")
        print("Next: open each prompt file in your LLM tool and save the output.")
        print(f"      Output files go in {OUTPUTS_DIR}/output-<agent>.md")

    if args.assemble or args.run:
        print("\nAssembling report...")
        report = assemble_report(data)
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        ds = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        path = REPORTS_DIR / f"price-pulse-agents-{ds}.md"
        path.write_text(report, encoding="utf-8")
        print(f"✅ Report written: {path}")
        print(f"   Lines: {len(report.splitlines())}")
        print(f"   Convert to PDF: pandoc {path} -o {path.with_suffix('.pdf')} --pdf-engine=xelatex")


if __name__ == "__main__":
    main()
