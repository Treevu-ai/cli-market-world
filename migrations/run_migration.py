"""Script para ejecutar migraciones HORECA en SQLite."""

import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from market_core import get_db

def run_horeca_migration():
    """Ejecuta la migración del schema HORECA."""
    
    # Leer el archivo SQL
    migration_file = root_dir / "migrations" / "add_horeca_schema.sql"
    
    if not migration_file.exists():
        print(f"❌ Error: Migration file not found: {migration_file}")
        return False
    
    with open(migration_file, 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    # Ejecutar cada statement SQL
    db = get_db()
    try:
        # Dividir el script en statements individuales
        statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
        
        for statement in statements:
            if statement:
                print(f"Executing: {statement[:50]}...")
                db.execute(statement)
        
        db.commit()
        print("✅ HORECA migration completed successfully!")
        
        # Verificar tablas creadas
        tables = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'horeca_%'"
        ).fetchall()
        
        print(f"📊 Created {len(tables)} HORECA tables:")
        for table in tables:
            print(f"  - {table['name']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error running migration: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    success = run_horeca_migration()
    sys.exit(0 if success else 1)