"""Bulk-import/upsert contacts into HubSpot from a CSV file.

Uses the CRM v3 batch upsert endpoint (POST .../contacts/batch/upsert)
with idProperty=email — HubSpot matches existing contacts by email and
updates them instead of creating duplicates, so this is safe to re-run
on the same CSV (or an updated version of it) without piling up dupes.

Column names are auto-detected (case-insensitive, Spanish or English)
for the common fields; anything else in the CSV can be mapped to a
HubSpot property with --extra-prop.

Usage:
    # Preview what would be sent, without touching HubSpot
    python scripts/import_contacts.py contactos.csv --dry-run

    # Real import (needs HUBSPOT_ACCESS_TOKEN — a Private App token)
    export HUBSPOT_ACCESS_TOKEN=pat-na1-...
    python scripts/import_contacts.py contactos.csv

    # Map extra CSV columns to HubSpot properties
    python scripts/import_contacts.py contactos.csv \
        --extra-prop "Región=region" --extra-prop "Rubro=industry"

Required env var (not needed for --dry-run):
    HUBSPOT_ACCESS_TOKEN   Private App token (Settings > Integrations >
                           Private Apps in HubSpot), needs at least the
                           crm.objects.contacts.write scope.
"""

from __future__ import annotations

import argparse
import csv
import os
import sys
import time
from pathlib import Path
from typing import Any

import httpx

BASE_URL = "https://api.hubapi.com"
BATCH_SIZE = 100  # HubSpot's max per batch upsert call

# column header -> HubSpot property, first match wins (case-insensitive)
_COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "email": ("email", "correo", "correo electronico", "correo electrónico", "e-mail"),
    # "Contacto" (a single full-name column, common in association/directory
    # exports) has no HubSpot "full name" property to map to — HubSpot only
    # has firstname/lastname and derives the display name from those. Rather
    # than guess a first/last split on Peruvian double surnames, the whole
    # value goes into firstname unsplit; lastname stays empty.
    "firstname": ("firstname", "first name", "nombre", "nombres", "contacto"),
    "lastname": ("lastname", "last name", "apellido", "apellidos"),
    "phone": ("phone", "telefono", "teléfono", "celular", "whatsapp"),
    "company": (
        "company", "empresa", "compania", "compañía",
        "organizacion", "organización", "razon social", "razón social",
    ),
    "jobtitle": ("jobtitle", "job title", "cargo", "puesto"),
}


def _normalize(header: str) -> str:
    return header.strip().lower()


def _detect_columns(fieldnames: list[str]) -> dict[str, str]:
    """Map HubSpot property -> actual CSV column name for this file."""
    normalized = {_normalize(f): f for f in fieldnames}
    detected: dict[str, str] = {}
    for hs_prop, aliases in _COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in normalized:
                detected[hs_prop] = normalized[alias]
                break
    return detected


def _clean_value(raw: str | None) -> str:
    """Strip whitespace and literal wrapping quote chars.

    Some source exports double-escape quoted names (e.g. the Peruvian
    MYPE association registry), so csv.DictReader hands back values
    like '"ASOCIACION X"' with the quote characters still embedded —
    strip them so they don't end up in HubSpot property values.
    """
    return (raw or "").strip().strip('"').strip()


def _load_rows(csv_path: Path, extra_props: dict[str, str]) -> tuple[list[dict[str, Any]], list[str]]:
    """Returns (upsert inputs, skipped-row reasons)."""
    with csv_path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        if not reader.fieldnames:
            raise ValueError(f"{csv_path} no tiene encabezados / está vacío")
        columns = _detect_columns(reader.fieldnames)
        if "email" not in columns:
            raise ValueError(
                f"No encontré una columna de email en {csv_path}. "
                f"Encabezados vistos: {reader.fieldnames}"
            )

        inputs: list[dict[str, Any]] = []
        skipped: list[str] = []
        for i, row in enumerate(reader, start=2):  # 1 = header row
            email = _clean_value(row.get(columns["email"]))
            if not email or "@" not in email:
                skipped.append(f"fila {i}: sin email válido ({row!r})")
                continue

            properties: dict[str, str] = {"email": email}
            for hs_prop, col in columns.items():
                if hs_prop == "email":
                    continue
                val = _clean_value(row.get(col))
                if val:
                    properties[hs_prop] = val
            for csv_col, hs_prop in extra_props.items():
                val = _clean_value(row.get(csv_col))
                if val:
                    properties[hs_prop] = val

            inputs.append({"idProperty": "email", "id": email, "properties": properties})

        return inputs, skipped


def _chunks(items: list[Any], size: int) -> list[list[Any]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def upsert_batch(token: str, batch: list[dict[str, Any]], *, timeout: float = 30.0) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    with httpx.Client(timeout=timeout) as client:
        r = client.post(
            f"{BASE_URL}/crm/v3/objects/contacts/batch/upsert",
            headers=headers,
            json={"inputs": batch},
        )
        if r.status_code >= 400:
            return {"error": True, "status_code": r.status_code, "body": r.json()}
        return {"error": False, "body": r.json()}


# HubSpot's own import wizard (Contacts > Import) auto-matches columns by
# these exact header names — no API/token needed at all, works on Free.
_HUBSPOT_IMPORT_HEADERS: dict[str, str] = {
    "email": "Email",
    "firstname": "First Name",
    "lastname": "Last Name",
    "phone": "Phone Number",
    "company": "Company Name",
    "jobtitle": "Job Title",
}


def export_for_hubspot_import(inputs: list[dict[str, Any]], out_path: Path) -> None:
    """Write a CSV shaped for HubSpot's UI-based import (Contacts > Import).

    Bypasses the API entirely, so it works even when the account has no
    Private App / write-scoped token available (e.g. gated behind a paid
    plan on Free CRM).
    """
    hs_props_present: list[str] = []
    for row in inputs:
        for prop in row["properties"]:
            if prop not in hs_props_present:
                hs_props_present.append(prop)

    headers = [_HUBSPOT_IMPORT_HEADERS.get(p, p) for p in hs_props_present]
    with out_path.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(headers)
        for row in inputs:
            writer.writerow([row["properties"].get(p, "") for p in hs_props_present])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("csv_path", type=Path)
    parser.add_argument("--dry-run", action="store_true", help="Mostrar qué se enviaría, sin llamar a HubSpot")
    parser.add_argument(
        "--export-csv",
        type=Path,
        metavar="OUT_PATH",
        help=(
            "No llamar a la API — escribir un CSV listo para subir a mano en "
            "Contacts > Import de HubSpot (funciona en el plan free, sin token)."
        ),
    )
    parser.add_argument(
        "--extra-prop",
        action="append",
        default=[],
        metavar="CSV_COLUMN=hubspot_property",
        help="Mapear una columna extra del CSV a una propiedad de HubSpot. Repetible.",
    )
    args = parser.parse_args(argv)

    if not args.csv_path.is_file():
        print(f"No existe {args.csv_path}", file=sys.stderr)
        return 1

    extra_props: dict[str, str] = {}
    for spec in args.extra_prop:
        if "=" not in spec:
            print(f"--extra-prop inválido (esperaba CSV_COLUMN=hubspot_property): {spec}", file=sys.stderr)
            return 1
        csv_col, hs_prop = spec.split("=", 1)
        extra_props[csv_col] = hs_prop

    try:
        inputs, skipped = _load_rows(args.csv_path, extra_props)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(f"{len(inputs)} contactos con email válido, {len(skipped)} filas omitidas.")
    for reason in skipped[:10]:
        print(f"  omitida: {reason}")
    if len(skipped) > 10:
        print(f"  ... y {len(skipped) - 10} más")

    if not inputs:
        return 0

    if args.export_csv:
        export_for_hubspot_import(inputs, args.export_csv)
        print(f"\nEscrito {args.export_csv} — subilo en HubSpot: Contacts > Import > File from computer.")
        return 0

    if args.dry_run:
        print("\n[dry-run] primeros 3 contactos que se subirían:")
        for row in inputs[:3]:
            print(f"  {row['properties']}")
        print(f"\n[dry-run] se harían {len(_chunks(inputs, BATCH_SIZE))} llamadas batch de hasta {BATCH_SIZE} contactos.")
        return 0

    token = os.environ["HUBSPOT_ACCESS_TOKEN"]
    created = updated = errored = 0
    for batch_num, batch in enumerate(_chunks(inputs, BATCH_SIZE), start=1):
        result = upsert_batch(token, batch)
        if result["error"]:
            errored += len(batch)
            print(f"batch {batch_num}: ERROR {result['status_code']} — {result['body']}", file=sys.stderr)
            continue
        for record in result["body"].get("results", []):
            if record.get("new"):
                created += 1
            else:
                updated += 1
        print(f"batch {batch_num}/{len(_chunks(inputs, BATCH_SIZE))}: ok ({len(batch)} contactos)")
        if batch_num < len(_chunks(inputs, BATCH_SIZE)):
            time.sleep(0.2)  # stay well under HubSpot's rate limit

    print(f"\nListo: {created} creados, {updated} actualizados, {errored} con error.")
    return 1 if errored else 0


if __name__ == "__main__":
    raise SystemExit(main())
