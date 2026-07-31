"""Tests básicos para funcionalidad HORECA."""

import pytest
import tempfile
from pathlib import Path

# Importar módulos HORECA
import sys
from pathlib import Path

root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from routers.integrations.horeca_profiles import (
    get_or_create_profile,
    update_profile_field,
    check_search_cooldown,
    check_daily_limit,
    calculate_savings,
    record_search_history,
    get_user_savings_summary
)


@pytest.fixture
def horeca_db(monkeypatch, tmp_path):
    """Setup test DB específico para HORECA."""
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
    
    # Ejecutar migración HORECA
    from migrations.run_migration import run_horeca_migration
    run_horeca_migration()
    
    return market_core


def test_profile_creation(horeca_db):
    """Test crear nuevo perfil HORECA."""
    profile = get_or_create_profile("whatsapp:+51900000000", "Test Restaurant", "restaurant")
    
    assert profile['business_name'] == "Test Restaurant"
    assert profile['business_type'] == "restaurant"
    assert profile['search_count'] == 0
    assert profile['total_savings'] == 0.0


def test_profile_update_field(horeca_db):
    """Test actualizar campo de perfil."""
    # Crear perfil primero
    get_or_create_profile("whatsapp:+51900000001", "Test Hotel", "pending")
    
    # Actualizar tipo de negocio
    success = update_profile_field("whatsapp:+51900000001", "business_type", "hotel")
    
    assert success == True
    
    # Verificar actualización
    profile = get_or_create_profile("whatsapp:+51900000001")
    assert profile['business_type'] == "hotel"


def test_cooldown_check(horeca_db):
    """Test cooldown de búsquedas."""
    from routers.integrations.horeca_profiles import HORECA_COOLDOWN_HOURS
    
    # Primera búsqueda debería pasar
    can_search = check_search_cooldown("whatsapp:+51900000002", "aceite vegetal")
    assert can_search == True
    
    # Simular búsqueda reciente
    record_search_history(
        "whatsapp:+51900000002", "aceite vegetal", "aceites",
        result_count=5, best_price=180.0, avg_price=200.0, savings=20.0
    )
    
    # Segunda búsqueda inmediata debería fallar
    can_search = check_search_cooldown("whatsapp:+51900000002", "aceite vegetal")
    assert can_search == False


def test_daily_limit_check(horeca_db):
    """Test límite diario de búsquedas."""
    from routers.integrations.horeca_profiles import HORECA_FREE_SEARCHES_DAILY, update_profile_search
    
    # Crear perfil con 4 búsquedas
    profile = get_or_create_profile("whatsapp:+51900000003", "Test Cafeteria", "cafeteria")
    
    # Simular 4 búsquedas
    for i in range(4):
        update_profile_search("whatsapp:+51900000003", f"producto_{i}", 10.0)
    
    # Verificar límite
    can_search, count = check_daily_limit("whatsapp:+51900000003")
    assert can_search == True  # 4 < 5 (límite default)
    assert count == 4
    
    # Agregar una más para alcanzar límite
    update_profile_search("whatsapp:+51900000003", "producto_5", 5.0)
    
    can_search, count = check_daily_limit("whatsapp:+51900000003")
    assert can_search == False  # 5 >= 5
    assert count == 5


def test_savings_calculation():
    """Test cálculo de ahorro."""
    answer = "Mejor opción: Wong - S/180.00\nMetro: S/200.00\nTottus: S/210.00"
    savings = calculate_savings("aceite", answer)
    
    assert savings > 0  # Debe haber ahorro
    # La lógica usa avg - min, donde avg = (180 + 200 + 210) / 3 = 196.67, min = 180
    # savings = 196.67 - 180 = 16.67
    assert abs(savings - 16.67) < 0.1  # Allow small floating point difference


def test_savings_summary(horeca_db):
    """Test resumen de ahorros."""
    from routers.integrations.horeca_profiles import update_profile_search
    
    # Crear perfil y agregar búsquedas con ahorro
    profile = get_or_create_profile("whatsapp:+51900000004", "Test Catering", "catering")
    
    # Simular búsquedas con ahorro
    record_search_history(
        "whatsapp:+51900000004", "aceite", "aceites",
        result_count=3, best_price=180.0, avg_price=200.0, savings=20.0
    )
    update_profile_search("whatsapp:+51900000004", "aceite", 20.0)
    
    record_search_history(
        "whatsapp:+51900000004", "detergente", "limpieza",
        result_count=2, best_price=50.0, avg_price=60.0, savings=10.0
    )
    update_profile_search("whatsapp:+51900000004", "detergente", 10.0)
    
    # Obtener resumen
    summary = get_user_savings_summary("whatsapp:+51900000004")
    
    assert summary['total_savings'] == 30.0
    assert summary['total_searches'] == 2
    assert len(summary['by_category']) == 2


def test_category_extraction():
    """Test extracción de categoría."""
    from routers.integrations.horeca_profiles import _extract_category
    
    assert _extract_category("aceite vegetal 20L") == "aceites"
    assert _extract_category("detergente industrial") == "limpieza"
    assert _extract_category("papel higiénico") == "papel"
    assert _extract_category("refresco coca cola") == "bebidas"
    assert _extract_category("producto random") == "general"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])