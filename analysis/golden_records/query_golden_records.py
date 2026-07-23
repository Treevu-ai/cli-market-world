#!/usr/bin/env python3
"""
Script para consultar golden records en CLI Market
"""

import psycopg2
from os import environ

db_url = "postgresql://postgres:[REVOKED — old Railway password, project deleted]@zephyr.proxy.rlwy.net:47133/railway"

try:
    print("Conectando a BD CLI Market...")
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()
    
    # Query para contar SKUs con golden_record
    print("\nConsultando tabla products...")
    cursor.execute("""
        SELECT 
            COUNT(*) as total_skus,
            COUNT(CASE WHEN golden_record IS NOT NULL THEN 1 END) as golden_records,
            COUNT(CASE WHEN golden_record IS NULL THEN 1 END) as sin_golden_record
        FROM products;
    """)
    
    result = cursor.fetchone()
    total, golden, sin_golden = result
    
    print("\n" + "="*60)
    print("GOLDEN RECORDS EN CLI MARKET")
    print("="*60)
    print(f"Total SKUs: {total:,}")
    print(f"Golden Records: {golden:,}")
    print(f"Sin Golden Record: {sin_golden:,}")
    if total > 0:
        print(f"Cobertura: {(golden/total*100):.1f}%")
    print("="*60)
    
    # Query adicional: por categoría
    print("\nPor Categoría:")
    cursor.execute("""
        SELECT 
            category,
            COUNT(*) as total,
            COUNT(CASE WHEN golden_record IS NOT NULL THEN 1 END) as golden,
            ROUND(100.0 * COUNT(CASE WHEN golden_record IS NOT NULL THEN 1 END) / COUNT(*), 1) as cobertura_pct
        FROM products
        GROUP BY category
        ORDER BY total DESC
        LIMIT 20;
    """)
    
    for row in cursor.fetchall():
        cat, tot, gold, cob = row
        print(f"  {cat}: {tot:,} SKUs ({gold:,} golden = {cob}%)")
    
    cursor.close()
    conn.close()
    print("\n✓ Consulta completada")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
