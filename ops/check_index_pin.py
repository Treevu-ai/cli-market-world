#!/usr/bin/env python3
"""
check_index_pin.py — Verifica que TODAS las referencias al SHA de
cli-market-index (requirements.txt, workflows de este repo, y
requirements-private.txt de cli-market-backend si esta presente como
repo hermano) apunten al mismo commit.

Por que existe: el 2026-07-10 un CI break de horas se debio a que el
SHA de cli-market-index estaba clavado a mano en 6 lugares distintos
entre 2 repos (requirements.txt, requirements-private.txt de backend,
y 5 workflows de este repo) -- cuando se actualizo el pin en uno, los
otros 5 quedaron viejos silenciosamente. Mismo patron que
cli-market-content/scripts/check-claims.py resuelve para cifras de
producto: una fuente de verdad (requirements.txt), todo lo demas se
verifica contra ella en cada corrida, no se copia a mano.

Uso:
    python3 ops/check_index_pin.py

No modifica archivos -- solo reporta. Exit 1 si hay desalineacion.

Requiere: Python 3.8+, PyYAML (ya es dependencia de dev en este repo)
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:
    print("Este check requiere PyYAML: pip install pyyaml")
    sys.exit(2)

REPO = Path(__file__).resolve().parent.parent
SHA_RE = re.compile(r"[0-9a-f]{40}")


def canonical_sha() -> str:
    """Fuente de verdad: el pin en requirements.txt de este repo."""
    text = (REPO / "requirements.txt").read_text(encoding="utf-8")
    m = re.search(
        r"cli-market-index\[postgres\]\s*@\s*git\+https://github\.com/Treevu-ai/cli-market-index@([0-9a-f]{40})",
        text,
    )
    if not m:
        print("No se encontro un pin de cli-market-index con SHA completo (40 hex) en requirements.txt")
        print("(¿es un SHA corto? check_index_pin.py exige el formato completo, igual que ops/contract_parity.py)")
        sys.exit(2)
    return m.group(1)


def find_workflow_refs(canonical: str) -> list[tuple[str, str]]:
    """Recorre .github/workflows/*.yml buscando steps de checkout de
    cli-market-index y devuelve (archivo, sha_encontrado) para los que
    no coincidan con el canonico."""
    mismatches = []
    workflows_dir = REPO / ".github" / "workflows"
    if not workflows_dir.exists():
        return mismatches

    for path in sorted(workflows_dir.glob("*.yml")):
        try:
            doc = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as e:
            print(f"  ADVERTENCIA: {path.relative_to(REPO)} no parsea como YAML ({e}) — se salta")
            continue
        if not isinstance(doc, dict):
            continue
        jobs = doc.get("jobs", {})
        if not isinstance(jobs, dict):
            continue
        for job in jobs.values():
            if not isinstance(job, dict):
                continue
            for step in job.get("steps", []) or []:
                if not isinstance(step, dict):
                    continue
                with_block = step.get("with", {})
                if not isinstance(with_block, dict):
                    continue
                if with_block.get("repository") != "Treevu-ai/cli-market-index":
                    continue
                ref = str(with_block.get("ref", ""))
                if SHA_RE.fullmatch(ref) and ref != canonical:
                    mismatches.append((str(path.relative_to(REPO)), ref))
    return mismatches


def find_backend_mismatch(canonical: str) -> tuple[str, str] | None:
    """Si cli-market-backend existe como repo hermano (mismo padre),
    verifica su requirements-private.txt."""
    backend_req = REPO.parent / "cli-market-backend" / "requirements-private.txt"
    if not backend_req.exists():
        return None
    text = backend_req.read_text(encoding="utf-8")
    m = re.search(
        r"cli-market-index\[postgres\]\s*@\s*git\+https://github\.com/Treevu-ai/cli-market-index@([0-9a-f]{40})",
        text,
    )
    if not m:
        return None
    found = m.group(1)
    if found != canonical:
        return (str(backend_req), found)
    return None


def main() -> int:
    canonical = canonical_sha()
    print()
    print("CLI Market — Verificacion de pin cli-market-index")
    print()
    print(f"  Canonico (requirements.txt): {canonical}")
    print()

    problems = []

    for file, found in find_workflow_refs(canonical):
        problems.append(f"  {file}: ref = {found} (esperado {canonical})")

    backend_mismatch = find_backend_mismatch(canonical)
    if backend_mismatch:
        file, found = backend_mismatch
        problems.append(f"  {file}: {found} (esperado {canonical})")

    if not problems:
        print("  Todas las referencias coinciden. ✅")
        return 0

    print(f"  {len(problems)} desalineacion(es) encontradas:")
    print()
    for p in problems:
        print(p)
    print()
    print("  Fix: actualizar cada referencia al SHA canonico de arriba (o revertir")
    print("  requirements.txt si el pin viejo era el correcto).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
