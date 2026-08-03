"""Map imported HubSpot contacts (Asociaciones MYPE) to their oficio file.

Cross-references three sources, all in cli-market-content:
  1. "Listado Asociaciones Inscritas - LIMPIO.csv" — RUC, Razon social, email
  2. oficios_sinapsis_cli_market/README.md — per-association index with the
     .md filename for each pre-written oficio (outreach letter)
  3. import_contacts.py's own row-selection logic (valid email only) — so
     this only lists the 105 associations actually sitting in HubSpot now,
     not all 147 in the registry.

Output: one CSV row per HubSpot contact with which oficio file to send.

Usage:
    python scripts/map_oficios_to_contacts.py \
        "/path/to/cli-market-content/commercial/Asociaciones MYPE"
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from import_contacts import _load_rows  # noqa: E402

_README_LINE = re.compile(r"^- \[(\d+)\] (.+?) \| (.+?) \| (.+?) \| (\S+\.md)$")


def _normalize_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().upper()).strip('"')


def _parse_readme_index(readme_path: Path) -> dict[str, dict[str, str]]:
    """Razon social (normalized) -> {numero, contacto, region, archivo}."""
    index: dict[str, dict[str, str]] = {}
    for line in readme_path.read_text(encoding="utf-8").splitlines():
        m = _README_LINE.match(line)
        if not m:
            continue
        numero, razon_social, contacto, region, archivo = m.groups()
        index[_normalize_name(razon_social)] = {
            "numero": numero,
            "contacto": contacto,
            "region": region,
            "archivo": archivo,
        }
    return index


def build_mapping(asociaciones_dir: Path) -> tuple[list[dict[str, str]], list[str]]:
    csv_path = asociaciones_dir / "Listado Asociaciones Inscritas - LIMPIO.csv"
    readme_path = asociaciones_dir / "oficios_sinapsis_cli_market" / "README.md"
    if not csv_path.is_file():
        raise FileNotFoundError(csv_path)
    if not readme_path.is_file():
        raise FileNotFoundError(readme_path)

    # Reuse import_contacts' own email-validity filter so this mapping only
    # covers the same 105 rows that actually made it into HubSpot.
    upsert_inputs, _ = _load_rows(csv_path, extra_props={})
    imported_emails = {row["properties"]["email"].lower() for row in upsert_inputs}

    oficio_index = _parse_readme_index(readme_path)

    rows: list[dict[str, str]] = []
    unmatched: list[str] = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as fh:
        for row in csv.DictReader(fh):
            email = (row.get("Correo") or "").strip()
            if not email or email.lower() not in imported_emails:
                continue
            razon_social = (row.get("Razon social") or "").strip().strip('"')
            oficio = oficio_index.get(_normalize_name(razon_social))
            if oficio is None:
                unmatched.append(razon_social)
                continue
            rows.append(
                {
                    "RUC": (row.get("RUC") or "").strip(),
                    "Razon Social": razon_social,
                    "Contacto": (row.get("Contacto") or "").strip(),
                    "Email (HubSpot)": email,
                    "Telefono": (row.get("Teléfono") or "").strip(),
                    "Region": oficio["region"],
                    "Oficio": oficio["archivo"],
                }
            )
    return rows, unmatched


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("asociaciones_dir", type=Path, help='Ruta a "commercial/Asociaciones MYPE"')
    parser.add_argument("--out", type=Path, default=Path("oficios_por_contacto.csv"))
    args = parser.parse_args(argv)

    try:
        rows, unmatched = build_mapping(args.asociaciones_dir)
    except FileNotFoundError as exc:
        print(f"No encontré {exc}", file=sys.stderr)
        return 1

    with args.out.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(
            fh, fieldnames=["RUC", "Razon Social", "Contacto", "Email (HubSpot)", "Telefono", "Region", "Oficio"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"{len(rows)} contactos mapeados a su oficio -> {args.out}")
    if unmatched:
        print(f"{len(unmatched)} sin oficio correspondiente en el README:", file=sys.stderr)
        for name in unmatched:
            print(f"  {name}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
