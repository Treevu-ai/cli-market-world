"""Tests HORECA Estación 90 — perfiles, plantillas y costo de menú."""

import json
import sys
from pathlib import Path

import pytest

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from routers.integrations.horeca_profiles import (
    seed_estacion90_profile,
    is_estacion90_profile,
    ESTACION90_BUSINESS_NAME,
)
from routers.integrations.horeca_templates import create_estacion90_templates, get_user_templates
from routers.integrations.horeca_menu_cost import (
    collect_ingredients_for_dishes,
    collect_menu_dishes,
    build_menu_cost_question,
)


@pytest.fixture
def horeca_db(monkeypatch, tmp_path):
    import market_core
    import market_core.market_core as mc

    data_dir = tmp_path / "market_data"
    data_dir.mkdir()
    db_file = data_dir / "market.db"

    monkeypatch.setenv("MARKET_DATA_DIR", str(data_dir))
    monkeypatch.setenv("DATABASE_URL", "")

    for mod in (mc, market_core):
        monkeypatch.setattr(mod, "DATA_DIR", data_dir, raising=False)
        monkeypatch.setattr(mod, "DB_FILE", db_file, raising=False)
        monkeypatch.setattr(mod, "USE_PG", False, raising=False)
        monkeypatch.setattr(mod, "_db_initialized", False, raising=False)

    from migrations.run_migration import run_horeca_migration

    run_horeca_migration()
    return market_core


def test_seed_estacion90_profile(horeca_db):
    sender = "whatsapp:+51911111111"
    profile = seed_estacion90_profile(sender)
    assert profile["business_name"] == ESTACION90_BUSINESS_NAME
    assert profile["business_type"] == "estacion90"
    assert is_estacion90_profile(profile)


def test_create_estacion90_templates(horeca_db):
    sender = "whatsapp:+51922222222"
    seed_estacion90_profile(sender)
    created = create_estacion90_templates(sender)
    assert created == 5
    templates = get_user_templates(sender)
    assert len(templates) == 5
    names = {t["template_name"] for t in templates}
    assert "Insumos semana cocina (Estación 90)" in names


def test_menu_ingredient_mapping():
    menu = json.loads(
        (root_dir / "hostinger" / "estacion90" / "api" / "menu.json").read_text(encoding="utf-8")
    )
    dishes = collect_menu_dishes(menu, category_id="menu_dia")
    assert any(d["id"] == "lomo_saltado" for d in dishes)
    ingredients = collect_ingredients_for_dishes(menu, ["lomo_saltado", "ceviche"])
    assert "lomo de res" in ingredients
    assert "limón" in ingredients
    question = build_menu_cost_question(ingredients[:3])
    assert "wong" in question.lower()
    assert "lomo de res" in question
