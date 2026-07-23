#!/usr/bin/env python3
"""
Consulta específica para golden records en fly.io
"""

import os

import requests
import json

token = os.environ["MARKET_API_TOKEN"]
api_url = "https://cli-market-api.fly.dev"

headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json"
}

print("="*70)
print("CLI MARKET - GOLDEN RECORDS ANALYSIS")
print("="*70)

# Primero, obtener info de API
try:
    print("\n📊 API Status:")
    resp = requests.get(f"{api_url}/", headers=headers, timeout=10)
    data = resp.json()
    print(f"   Stores: {data.get('stores', 'N/A')}")
    print(f"   Lines (Categorías): {data.get('lines', 'N/A')}")
    print(f"   Countries: {data.get('countries', 'N/A')}")
except Exception as e:
    print(f"   Error: {e}")

# Buscar con query simple para obtener muestra
categories = ["bebidas", "dairy", "lácteos", "alimentos", "proteínas", "frescos", "snacks"]

total_skus = 0
golden_records = 0

print(f"\n🔍 Buscando por categoría (timeout 30s por búsqueda):")

for cat in categories:
    try:
        resp = requests.post(
            f"{api_url}/products/search",
            headers=headers,
            json={"query": cat, "limit": 100, "country": "PE"},
            timeout=30
        )
        
        if resp.status_code == 200:
            data = resp.json()
            count = data.get('total', len(data.get('results', [])))
            results = data.get('results', [])
            
            # Contar golden records (si existe el campo)
            golden = sum(1 for r in results if r.get('golden_record') or r.get('is_golden') or r.get('canonical'))
            
            print(f"   {cat:15} → {count:4} SKUs (muestra: {len(results)}, golden: {golden})")
            total_skus += count
            golden_records += golden
            
    except requests.exceptions.Timeout:
        print(f"   {cat:15} → TIMEOUT (búsqueda lenta)")
    except Exception as e:
        print(f"   {cat:15} → Error: {str(e)[:40]}")

print(f"\n📈 TOTALES ACUMULADOS:")
print(f"   Total SKUs: ~{total_skus:,}")
print(f"   Golden Records: ~{golden_records:,}")
if total_skus > 0:
    print(f"   Cobertura: {(golden_records/total_skus*100):.1f}%")

# Hacer búsqueda de muestra para ver estructura
print(f"\n📋 ESTRUCTURA DE DATOS (muestra):")
try:
    resp = requests.post(
        f"{api_url}/products/search",
        headers=headers,
        json={"query": "coca cola", "limit": 1, "country": "PE"},
        timeout=30
    )
    if resp.status_code == 200:
        data = resp.json()
        if data.get('results'):
            print(json.dumps(data['results'][0], indent=2))
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "="*70)
print("NOTA: Los totales son aproximados (basados en muestras de búsqueda)")
print("="*70)
