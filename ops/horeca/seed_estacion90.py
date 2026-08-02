#!/usr/bin/env python3
"""Seed del perfil HORECA Estación 90 + plantillas de procurement."""

import argparse
import sys
from pathlib import Path

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root))

from market_core import ensure_db_initialized
from migrations.run_migration import run_horeca_migration
from routers.integrations.horeca_profiles import seed_estacion90_profile
from routers.integrations.horeca_templates import create_estacion90_templates


def main() -> int:
    parser = argparse.ArgumentParser(description="Seed HORECA profile for Estación 90")
    parser.add_argument("whatsapp", help="Número WhatsApp, ej. whatsapp:+51999999999")
    args = parser.parse_args()

    ensure_db_initialized()
    run_horeca_migration()

    profile = seed_estacion90_profile(args.whatsapp)
    created = create_estacion90_templates(args.whatsapp)

    print(f"✓ Perfil: {profile['business_name']} ({profile['business_type']})")
    print(f"✓ Plantillas creadas: {created}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
